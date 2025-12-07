# pubmed_rag_tools.py
"""
Hierarchical PubMed RAG System
Combines local ChromaDB + live PubMed search + PMC full text
"""

import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET

class RetrievalSource(Enum):
    LOCAL_RAG = "local_rag"
    PUBMED_SEARCH = "pubmed_search"
    PMC_FULL_TEXT = "pmc_full_text"

@dataclass
class RetrievedDocument:
    """Unified document representation from any source"""
    pmid: str
    title: str
    abstract: str
    full_text: Optional[str] = None
    source: RetrievalSource = RetrievalSource.LOCAL_RAG
    similarity_score: float = 0.0
    year: Optional[int] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    
    def to_context(self, max_length: int = 2000) -> str:
        """Format for LLM context window"""
        content = self.full_text or self.abstract
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return f"""[PMID: {self.pmid}] {self.title}
Authors: {self.authors or 'N/A'} | {self.journal or 'N/A'} ({self.year or 'N/A'})
Source: {self.source.value} | Relevance: {self.similarity_score:.2f}

{content}
"""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'pmid': self.pmid,
            'title': self.title,
            'abstract': self.abstract,
            'full_text': self.full_text,
            'source': self.source.value,
            'similarity_score': self.similarity_score,
            'year': self.year,
            'authors': self.authors,
            'journal': self.journal
        }


class PubMedRAGSystem:
    """
    Hierarchical retrieval system:
    1. Check local RAG first (fast, pre-indexed)
    2. Fall back to PubMed search if needed
    3. Optionally fetch full text from PMC
    """
    
    # PubMed E-utilities base URLs
    PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    PMC_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    def __init__(self, local_rag=None, similarity_threshold: float = 0.6,
                 min_local_results: int = 3, ncbi_api_key: str = None):
        """
        Args:
            local_rag: Your existing ASPLiteratureRAG instance
            similarity_threshold: Minimum similarity to consider local results sufficient
            min_local_results: Minimum number of good local results before searching PubMed
            ncbi_api_key: Optional NCBI API key for higher rate limits
        """
        self.local_rag = local_rag
        self.similarity_threshold = similarity_threshold
        self.min_local_results = min_local_results
        self.api_key = ncbi_api_key
        
    def retrieve(self, query: str, max_results: int = 5,
                 force_pubmed: bool = False,
                 fetch_full_text: bool = False) -> Tuple[List[RetrievedDocument], Dict]:
        """
        Main retrieval method with tiered strategy
        
        Returns:
            Tuple of (documents, metadata about retrieval process)
        """
        metadata = {
            "query": query,
            "sources_used": [],
            "local_results": 0,
            "pubmed_results": 0,
            "full_text_fetched": 0
        }
        
        all_docs = []
        
        # Step 1: Try local RAG first
        if self.local_rag and not force_pubmed:
            local_docs = self._search_local_rag(query, max_results)
            metadata["local_results"] = len(local_docs)
            
            # Filter by similarity threshold
            good_local = [d for d in local_docs if d.similarity_score >= self.similarity_threshold]
            all_docs.extend(good_local)
            
            if good_local:
                metadata["sources_used"].append("local_rag")
            
            # If we have enough good local results, we might be done
            if len(good_local) >= self.min_local_results:
                # But still check if query seems to need current literature
                if not self._needs_current_literature(query):
                    return all_docs[:max_results], metadata
        
        # Step 2: Search PubMed for additional/current results
        pubmed_docs = self._search_pubmed(query, max_results)
        metadata["pubmed_results"] = len(pubmed_docs)
        
        if pubmed_docs:
            metadata["sources_used"].append("pubmed_search")
            
            # Deduplicate by PMID
            existing_pmids = {d.pmid for d in all_docs}
            new_docs = [d for d in pubmed_docs if d.pmid not in existing_pmids]
            all_docs.extend(new_docs)
        
        # Step 3: Optionally fetch full text for top results
        if fetch_full_text and all_docs:
            # Try to get full text for top 3 most relevant
            top_docs = sorted(all_docs, key=lambda x: x.similarity_score, reverse=True)[:3]
            for doc in top_docs:
                full_text = self._fetch_pmc_full_text(doc.pmid)
                if full_text:
                    doc.full_text = full_text
                    doc.source = RetrievalSource.PMC_FULL_TEXT
                    metadata["full_text_fetched"] += 1
            
            if metadata["full_text_fetched"] > 0:
                metadata["sources_used"].append("pmc_full_text")
        
        # Sort by relevance and return
        all_docs.sort(key=lambda x: x.similarity_score, reverse=True)
        return all_docs[:max_results], metadata
    
    def _search_local_rag(self, query: str, max_results: int) -> List[RetrievedDocument]:
        """Search the local ChromaDB RAG"""
        if not self.local_rag:
            return []
        
        try:
            results = self.local_rag.search(query, n_results=max_results, min_similarity=0.3)
            
            docs = []
            for r in results:
                docs.append(RetrievedDocument(
                    pmid=r.get('pmid', 'unknown'),
                    title=r.get('title', ''),
                    abstract=r.get('text', ''),
                    source=RetrievalSource.LOCAL_RAG,
                    similarity_score=r.get('similarity', 0.0),
                    year=r.get('year'),
                    authors=r.get('authors'),
                    journal=r.get('journal')
                ))
            return docs
        except Exception as e:
            print(f"Local RAG search error: {e}")
            return []
    
    def _search_pubmed(self, query: str, max_results: int) -> List[RetrievedDocument]:
        """Search PubMed via E-utilities"""
        try:
            # Step 1: Search for PMIDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            if self.api_key:
                search_params["api_key"] = self.api_key
            
            search_resp = requests.get(self.PUBMED_SEARCH_URL, params=search_params, timeout=10)
            search_data = search_resp.json()
            
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []
            
            # Step 2: Fetch article details
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "rettype": "abstract",
                "retmode": "xml"
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key
            
            fetch_resp = requests.get(self.PUBMED_FETCH_URL, params=fetch_params, timeout=15)
            
            # Parse XML response
            docs = self._parse_pubmed_xml(fetch_resp.text)
            
            # Assign relevance scores based on position (PubMed returns by relevance)
            for i, doc in enumerate(docs):
                doc.similarity_score = 1.0 - (i * 0.1)  # Simple decay
            
            return docs
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[RetrievedDocument]:
        """Parse PubMed XML response into documents"""
        docs = []
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else "unknown"
                
                title_elem = article.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else ""
                
                # Get abstract
                abstract_parts = []
                for abstract_text in article.findall(".//AbstractText"):
                    label = abstract_text.get("Label", "")
                    text = abstract_text.text or ""
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                abstract = " ".join(abstract_parts)
                
                # Get year
                year_elem = article.find(".//PubDate/Year")
                year = int(year_elem.text) if year_elem is not None else None
                
                # Get authors
                authors = []
                for author in article.findall(".//Author"):
                    lastname = author.find("LastName")
                    initials = author.find("Initials")
                    if lastname is not None:
                        name = lastname.text
                        if initials is not None:
                            name += f" {initials.text}"
                        authors.append(name)
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += " et al."
                
                # Get journal
                journal_elem = article.find(".//Journal/Title")
                journal = journal_elem.text if journal_elem is not None else None
                
                docs.append(RetrievedDocument(
                    pmid=pmid,
                    title=title,
                    abstract=abstract,
                    source=RetrievalSource.PUBMED_SEARCH,
                    year=year,
                    authors=author_str,
                    journal=journal
                ))
                
        except ET.ParseError as e:
            print(f"XML parse error: {e}")
        
        return docs
    
    def _fetch_pmc_full_text(self, pmid: str) -> Optional[str]:
        """Attempt to fetch full text from PMC"""
        try:
            # First, convert PMID to PMCID
            convert_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
            convert_params = {
                "ids": pmid,
                "format": "json"
            }
            
            convert_resp = requests.get(convert_url, params=convert_params, timeout=5)
            convert_data = convert_resp.json()
            
            records = convert_data.get("records", [])
            if not records or "pmcid" not in records[0]:
                return None  # No PMC version available
            
            pmcid = records[0]["pmcid"]
            
            # Fetch full text from PMC
            pmc_params = {
                "db": "pmc",
                "id": pmcid,
                "rettype": "full",
                "retmode": "text"
            }
            if self.api_key:
                pmc_params["api_key"] = self.api_key
            
            pmc_resp = requests.get(self.PMC_FETCH_URL, params=pmc_params, timeout=15)
            
            if pmc_resp.status_code == 200 and len(pmc_resp.text) > 500:
                # Clean up the text (remove excessive whitespace)
                text = " ".join(pmc_resp.text.split())
                return text[:15000]  # Limit to ~15k chars
            
            return None
            
        except Exception as e:
            print(f"PMC fetch error for PMID {pmid}: {e}")
            return None
    
    def _needs_current_literature(self, query: str) -> bool:
        """Heuristic to detect if query needs recent/current literature"""
        current_indicators = [
            "recent", "latest", "current", "2024", "2025", "new",
            "emerging", "novel", "update", "guideline"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in current_indicators)
    
    def format_context_for_llm(self, documents: List[RetrievedDocument],
                                max_total_length: int = 8000) -> str:
        """Format retrieved documents for LLM context window"""
        if not documents:
            return "No relevant literature found."
        
        context_parts = [
            "=== RETRIEVED LITERATURE ===\n",
            f"Found {len(documents)} relevant sources:\n"
        ]
        
        total_length = sum(len(p) for p in context_parts)
        per_doc_limit = (max_total_length - total_length) // len(documents)
        
        for i, doc in enumerate(documents, 1):
            doc_context = f"\n--- Source {i} ---\n"
            doc_context += doc.to_context(max_length=per_doc_limit)
            context_parts.append(doc_context)
        
        context_parts.append("\n=== END LITERATURE ===\n")
        
        return "".join(context_parts)


# Tool definitions for LLM function calling
PUBMED_RAG_TOOLS = [
    {
        "name": "search_literature",
        "description": """Search for antimicrobial stewardship literature. 
        First checks local indexed database, then searches PubMed if needed.
        Use this when you need evidence to support your response.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query - be specific about pathogens, antibiotics, or clinical scenarios"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default 5)",
                    "default": 5
                },
                "fetch_full_text": {
                    "type": "boolean",
                    "description": "Whether to fetch full text from PMC for top results",
                    "default": False
                },
                "force_pubmed": {
                    "type": "boolean",
                    "description": "Skip local RAG and search PubMed directly",
                    "default": False
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_article_details",
        "description": "Get detailed information about a specific article by PMID",
        "input_schema": {
            "type": "object",
            "properties": {
                "pmid": {
                    "type": "string",
                    "description": "PubMed ID of the article"
                },
                "include_full_text": {
                    "type": "boolean",
                    "description": "Attempt to fetch full text from PMC",
                    "default": True
                }
            },
            "required": ["pmid"]
        }
    }
]