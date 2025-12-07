# literature_extractor.py
"""
Local LLM extraction layer for PubMed literature
Uses Qwen/Gemma to extract structured information from abstracts and full text
"""

import requests
import json
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os

class RelevanceLevel(Enum):
    HIGH = "high"           # Directly answers the query
    MEDIUM = "medium"       # Related, provides useful context
    LOW = "low"             # Tangentially related
    NOT_RELEVANT = "not_relevant"  # False positive from search


@dataclass
class ExtractedEvidence:
    """Structured extraction from a single article"""
    pmid: str
    title: str
    
    # Relevance assessment
    relevance: RelevanceLevel = RelevanceLevel.MEDIUM
    relevance_reasoning: str = ""
    
    # Key extracted information
    study_type: str = ""  # RCT, cohort, case series, review, guideline, etc.
    population: str = ""  # Patient population studied
    intervention: str = ""  # What was done/studied
    comparator: str = ""  # Control/comparison group
    outcomes: List[str] = field(default_factory=list)  # Key outcomes/findings
    
    # Clinical relevance
    key_findings: List[str] = field(default_factory=list)  # 2-3 most important points
    limitations: List[str] = field(default_factory=list)
    clinical_implications: str = ""
    
    # For ASP-specific extractions
    antibiotics_mentioned: List[str] = field(default_factory=list)
    pathogens_mentioned: List[str] = field(default_factory=list)
    resistance_patterns: str = ""
    stewardship_implications: str = ""
    
    # Metadata
    year: Optional[int] = None
    journal: str = ""
    extraction_confidence: float = 0.0  # 0-1, how confident the extractor is
    
    def to_context(self) -> str:
        """Format for LLM context window - much more compact than raw text"""
        parts = [f"[PMID {self.pmid}] {self.title}"]
        parts.append(f"Relevance: {self.relevance.value} | Study Type: {self.study_type}")
        
        if self.population:
            parts.append(f"Population: {self.population}")
        if self.intervention:
            parts.append(f"Intervention: {self.intervention}")
        
        if self.key_findings:
            parts.append("Key Findings:")
            for finding in self.key_findings[:3]:
                parts.append(f"  • {finding}")
        
        if self.clinical_implications:
            parts.append(f"Clinical Implications: {self.clinical_implications}")
        
        if self.stewardship_implications:
            parts.append(f"Stewardship Relevance: {self.stewardship_implications}")
        
        if self.limitations:
            parts.append(f"Limitations: {'; '.join(self.limitations[:2])}")
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)
        d['relevance'] = self.relevance.value
        return d


class LiteratureExtractor:
    """
    Uses local LLM to extract structured information from medical literature
    """
    
    EXTRACTION_PROMPT = """You are a medical literature analyst specializing in antimicrobial stewardship.
    
Analyze the following article and extract structured information. Be precise and evidence-based.

QUERY CONTEXT: {query}

ARTICLE TO ANALYZE:
Title: {title}
PMID: {pmid}
Year: {year}
Journal: {journal}

Content:
{content}

---

Extract the following information. If information is not available, use "Not specified".

Respond in this exact JSON format:
```json
{{
    "relevance": "high|medium|low|not_relevant",
    "relevance_reasoning": "Brief explanation of why this article is/isn't relevant to the query",
    
    "study_type": "RCT|cohort|case-control|case series|systematic review|meta-analysis|narrative review|guideline|other",
    "population": "Description of patient population (age, setting, condition)",
    "intervention": "What was studied or done",
    "comparator": "Control or comparison group if applicable",
    
    "outcomes": [
        "Primary outcome with result",
        "Secondary outcomes if notable"
    ],
    
    "key_findings": [
        "Most important finding 1",
        "Most important finding 2",
        "Most important finding 3"
    ],
    
    "limitations": [
        "Key limitation 1",
        "Key limitation 2"
    ],
    
    "clinical_implications": "What this means for clinical practice",
    
    "antibiotics_mentioned": ["list", "of", "antibiotics"],
    "pathogens_mentioned": ["list", "of", "pathogens"],
    "resistance_patterns": "Any resistance data mentioned",
    "stewardship_implications": "Relevance to antimicrobial stewardship programs",
    
    "extraction_confidence": 0.85
}}
```

Focus on extracting actionable, clinically relevant information. Be concise but complete."""

    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 model: str = "qwen2.5:72b-instruct-q4_K_M",
                 cache_db: str = "extraction_cache.db",
                 timeout: int = 60):
        """
        Args:
            ollama_url: URL for Ollama API
            model: Local model to use for extraction
            cache_db: SQLite database for caching extractions
            timeout: Request timeout in seconds
        """
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = timeout
        self.cache_db = cache_db
        
        # Initialize cache database
        self._init_cache()
    
    def _init_cache(self):
        """Initialize SQLite cache for extractions"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_cache (
                cache_key TEXT PRIMARY KEY,
                pmid TEXT,
                query_hash TEXT,
                extraction_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pmid ON extraction_cache(pmid)
        """)
        conn.commit()
        conn.close()
    
    def _get_cache_key(self, pmid: str, query: str, content_hash: str) -> str:
        """Generate cache key from pmid, query, and content"""
        combined = f"{pmid}:{query}:{content_hash}:{self.model}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[ExtractedEvidence]:
        """Retrieve cached extraction if available"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT extraction_json FROM extraction_cache WHERE cache_key = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                data = json.loads(row[0])
                data['relevance'] = RelevanceLevel(data['relevance'])
                return ExtractedEvidence(**data)
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        return None
    
    def _save_cache(self, cache_key: str, pmid: str, query: str, 
                    extraction: ExtractedEvidence):
        """Save extraction to cache"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO extraction_cache 
                (cache_key, pmid, query_hash, extraction_json, model)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cache_key,
                pmid,
                hashlib.md5(query.encode()).hexdigest(),
                json.dumps(extraction.to_dict()),
                self.model
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def extract_single(self, 
                       pmid: str,
                       title: str,
                       content: str,
                       query: str,
                       year: Optional[int] = None,
                       journal: str = "",
                       use_cache: bool = True) -> ExtractedEvidence:
        """
        Extract structured information from a single article
        
        Args:
            pmid: PubMed ID
            title: Article title
            content: Abstract or full text
            query: The user's original query (for relevance assessment)
            year: Publication year
            journal: Journal name
            use_cache: Whether to use cached extractions
        
        Returns:
            ExtractedEvidence with structured information
        """
        content_hash = hashlib.md5(content[:1000].encode()).hexdigest()
        cache_key = self._get_cache_key(pmid, query, content_hash)
        
        # Check cache first
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        # Truncate content if too long (keep first and last parts)
        max_content_length = 6000
        if len(content) > max_content_length:
            half = max_content_length // 2
            content = content[:half] + "\n\n[...content truncated...]\n\n" + content[-half:]
        
        # Build the prompt
        prompt = self.EXTRACTION_PROMPT.format(
            query=query,
            title=title,
            pmid=pmid,
            year=year or "Unknown",
            journal=journal or "Unknown",
            content=content
        )
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent extraction
                        "num_predict": 2000
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result_text = response.json().get("response", "")
                extraction = self._parse_extraction(result_text, pmid, title, year, journal)
                
                # Cache the result
                if use_cache:
                    self._save_cache(cache_key, pmid, query, extraction)
                
                return extraction
            else:
                print(f"Ollama error for PMID {pmid}: {response.status_code}")
                
        except requests.Timeout:
            print(f"Timeout extracting PMID {pmid}")
        except Exception as e:
            print(f"Extraction error for PMID {pmid}: {e}")
        
        # Return minimal extraction on failure
        return ExtractedEvidence(
            pmid=pmid,
            title=title,
            relevance=RelevanceLevel.MEDIUM,
            relevance_reasoning="Extraction failed - using raw content",
            year=year,
            journal=journal,
            extraction_confidence=0.0
        )
    
    def _parse_extraction(self, 
                          response_text: str,
                          pmid: str,
                          title: str,
                          year: Optional[int],
                          journal: str) -> ExtractedEvidence:
        """Parse LLM response into ExtractedEvidence"""
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # Map relevance string to enum
                relevance_str = data.get('relevance', 'medium').lower()
                relevance_map = {
                    'high': RelevanceLevel.HIGH,
                    'medium': RelevanceLevel.MEDIUM,
                    'low': RelevanceLevel.LOW,
                    'not_relevant': RelevanceLevel.NOT_RELEVANT
                }
                relevance = relevance_map.get(relevance_str, RelevanceLevel.MEDIUM)
                
                return ExtractedEvidence(
                    pmid=pmid,
                    title=title,
                    relevance=relevance,
                    relevance_reasoning=data.get('relevance_reasoning', ''),
                    study_type=data.get('study_type', ''),
                    population=data.get('population', ''),
                    intervention=data.get('intervention', ''),
                    comparator=data.get('comparator', ''),
                    outcomes=data.get('outcomes', []),
                    key_findings=data.get('key_findings', []),
                    limitations=data.get('limitations', []),
                    clinical_implications=data.get('clinical_implications', ''),
                    antibiotics_mentioned=data.get('antibiotics_mentioned', []),
                    pathogens_mentioned=data.get('pathogens_mentioned', []),
                    resistance_patterns=data.get('resistance_patterns', ''),
                    stewardship_implications=data.get('stewardship_implications', ''),
                    year=year,
                    journal=journal,
                    extraction_confidence=data.get('extraction_confidence', 0.7)
                )
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error for PMID {pmid}: {e}")
        except Exception as e:
            print(f"Parse error for PMID {pmid}: {e}")
        
        # Fallback
        return ExtractedEvidence(
            pmid=pmid,
            title=title,
            year=year,
            journal=journal,
            extraction_confidence=0.3
        )
    
    def extract_batch(self,
                      documents: List[Dict],
                      query: str,
                      max_workers: int = 3,
                      use_cache: bool = True) -> List[ExtractedEvidence]:
        """
        Extract from multiple documents in parallel
        
        Args:
            documents: List of dicts with pmid, title, content, year, journal
            query: User's query for relevance assessment
            max_workers: Number of parallel extraction threads
            use_cache: Whether to use cached extractions
        
        Returns:
            List of ExtractedEvidence objects
        """
        extractions = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for doc in documents:
                future = executor.submit(
                    self.extract_single,
                    pmid=doc.get('pmid', ''),
                    title=doc.get('title', ''),
                    content=doc.get('content', doc.get('abstract', '')),
                    query=query,
                    year=doc.get('year'),
                    journal=doc.get('journal', ''),
                    use_cache=use_cache
                )
                futures[future] = doc.get('pmid', '')
            
            for future in as_completed(futures):
                pmid = futures[future]
                try:
                    extraction = future.result()
                    extractions.append(extraction)
                except Exception as e:
                    print(f"Extraction failed for PMID {pmid}: {e}")
        
        # Sort by relevance
        relevance_order = {
            RelevanceLevel.HIGH: 0,
            RelevanceLevel.MEDIUM: 1,
            RelevanceLevel.LOW: 2,
            RelevanceLevel.NOT_RELEVANT: 3
        }
        extractions.sort(key=lambda x: (relevance_order[x.relevance], -x.extraction_confidence))
        
        return extractions
    
    def format_extractions_for_llm(self,
                                    extractions: List[ExtractedEvidence],
                                    max_length: int = 6000,
                                    include_low_relevance: bool = False) -> str:
        """
        Format extracted evidence for final LLM context
        
        Args:
            extractions: List of ExtractedEvidence objects
            max_length: Maximum total context length
            include_low_relevance: Whether to include low/not_relevant articles
        
        Returns:
            Formatted context string for LLM
        """
        # Filter by relevance
        if not include_low_relevance:
            extractions = [e for e in extractions 
                          if e.relevance in [RelevanceLevel.HIGH, RelevanceLevel.MEDIUM]]
        
        if not extractions:
            return "No relevant literature found for this query."
        
        parts = [
            "=== EXTRACTED EVIDENCE ===",
            f"Found {len(extractions)} relevant sources:\n"
        ]
        
        # High relevance first
        high_relevance = [e for e in extractions if e.relevance == RelevanceLevel.HIGH]
        medium_relevance = [e for e in extractions if e.relevance == RelevanceLevel.MEDIUM]
        
        current_length = sum(len(p) for p in parts)
        
        for i, extraction in enumerate(high_relevance + medium_relevance, 1):
            entry = f"\n--- Source {i} ({extraction.relevance.value} relevance) ---\n"
            entry += extraction.to_context()
            
            if current_length + len(entry) > max_length:
                parts.append(f"\n[{len(extractions) - i + 1} additional sources truncated]")
                break
            
            parts.append(entry)
            current_length += len(entry)
        
        parts.append("\n=== END EVIDENCE ===")
        
        return "\n".join(parts)


class EnhancedPubMedRAG:
    """
    Enhanced RAG system with local LLM extraction layer
    
    Pipeline:
    1. Local RAG search (fast, pre-indexed)
    2. PubMed search if needed (current literature)
    3. PMC full text fetch (deep content)
    4. Local LLM extraction (structured, compressed)
    5. Final LLM response (with clean context)
    """
    
    def __init__(self,
                 pubmed_rag,  # Your PubMedRAGSystem instance
                 extractor: Optional[LiteratureExtractor] = None,
                 ollama_url: str = "http://localhost:11434",
                 extraction_model: str = "qwen2.5:72b-instruct-q4_K_M"):
        """
        Args:
            pubmed_rag: PubMedRAGSystem instance for retrieval
            extractor: Optional LiteratureExtractor (created if not provided)
            ollama_url: Ollama API URL
            extraction_model: Model to use for extraction
        """
        self.pubmed_rag = pubmed_rag
        self.extractor = extractor or LiteratureExtractor(
            ollama_url=ollama_url,
            model=extraction_model
        )
    
    def retrieve_and_extract(self,
                             query: str,
                             max_results: int = 5,
                             fetch_full_text: bool = True,
                             force_pubmed: bool = False,
                             extract: bool = True) -> Dict[str, Any]:
        """
        Full retrieval + extraction pipeline
        
        Args:
            query: User's query
            max_results: Maximum documents to retrieve
            fetch_full_text: Whether to fetch PMC full text
            force_pubmed: Skip local RAG
            extract: Whether to run local LLM extraction
        
        Returns:
            Dict with extractions, raw_documents, metadata, and formatted_context
        """
        start_time = time.time()
        
        # Step 1-3: Retrieve documents
        documents, retrieval_metadata = self.pubmed_rag.retrieve(
            query=query,
            max_results=max_results,
            fetch_full_text=fetch_full_text,
            force_pubmed=force_pubmed
        )
        
        retrieval_time = time.time() - start_time
        
        result = {
            "raw_documents": documents,
            "retrieval_metadata": retrieval_metadata,
            "timing": {"retrieval_seconds": round(retrieval_time, 2)}
        }
        
        if not documents:
            result["extractions"] = []
            result["formatted_context"] = "No relevant literature found."
            return result
        
        # Step 4: Extract with local LLM
        if extract:
            extraction_start = time.time()
            
            # Prepare documents for extraction
            docs_for_extraction = []
            for doc in documents:
                docs_for_extraction.append({
                    'pmid': doc.pmid,
                    'title': doc.title,
                    'content': doc.full_text or doc.abstract,
                    'year': doc.year,
                    'journal': doc.journal
                })
            
            extractions = self.extractor.extract_batch(
                documents=docs_for_extraction,
                query=query,
                max_workers=3
            )
            
            extraction_time = time.time() - extraction_start
            
            result["extractions"] = extractions
            result["timing"]["extraction_seconds"] = round(extraction_time, 2)
            result["formatted_context"] = self.extractor.format_extractions_for_llm(
                extractions, 
                max_length=6000
            )
            
            # Summary stats
            result["summary"] = {
                "total_retrieved": len(documents),
                "high_relevance": len([e for e in extractions if e.relevance == RelevanceLevel.HIGH]),
                "medium_relevance": len([e for e in extractions if e.relevance == RelevanceLevel.MEDIUM]),
                "low_relevance": len([e for e in extractions if e.relevance == RelevanceLevel.LOW]),
                "not_relevant": len([e for e in extractions if e.relevance == RelevanceLevel.NOT_RELEVANT]),
                "sources_used": retrieval_metadata.get("sources_used", [])
            }
        else:
            # No extraction - use raw formatting
            result["extractions"] = []
            result["formatted_context"] = self.pubmed_rag.format_context_for_llm(documents)
        
        result["timing"]["total_seconds"] = round(time.time() - start_time, 2)
        
        return result