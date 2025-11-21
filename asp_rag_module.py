#!/usr/bin/env python3
"""
ASP Literature RAG System
Independent RAG module for antimicrobial stewardship literature
Uses PubMedBERT embeddings and ChromaDB for vector search
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

# PDF processing
try:
    import pypdf
except ImportError:
    try:
        import PyPDF2 as pypdf
    except ImportError:
        pypdf = None

# Embeddings and vector store
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import torch


class PDFMetadataExtractor:
    """
    Extract bibliographic metadata from PDFs using three-tier approach:
    1. PDF embedded metadata (fast)
    2. First-page text parsing (reliable)
    3. LLM extraction (fallback, most accurate)
    """
    
    def __init__(self, use_llm_fallback: bool = True):
        """
        Initialize metadata extractor
        
        Args:
            use_llm_fallback: Use LLM for extraction when other methods fail
        """
        self.use_llm_fallback = use_llm_fallback
        
        # Common patterns for metadata extraction
        self.year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        self.doi_pattern = re.compile(r'10\.\d{4,}/[^\s]+')
        self.pmid_pattern = re.compile(r'PMID[:\s]*(\d{8})', re.IGNORECASE)
    
    def extract_metadata(self, pdf_path: Path, text: str = None) -> Dict:
        """
        Extract metadata using three-tier approach
        
        Args:
            pdf_path: Path to PDF file
            text: Already extracted text (optional, to avoid re-extraction)
        
        Returns:
            Dict with: title, authors, year, journal, doi, pmid, etc.
        """
        metadata = {
            'filename': pdf_path.name,
            'title': None,
            'authors': [],
            'first_author': None,
            'year': None,
            'journal': None,
            'volume': None,
            'pages': None,
            'doi': None,
            'pmid': None,
            'extraction_method': None
        }
        
        # Tier 1: PDF embedded metadata
        embedded_meta = self._extract_from_pdf_metadata(pdf_path)
        metadata.update({k: v for k, v in embedded_meta.items() if v})

        # Check if we have minimum required fields AND quality title
        if metadata['title'] and metadata['year'] and self._is_quality_title(metadata['title']):
            metadata['extraction_method'] = 'embedded_metadata'
            return metadata

        # Tier 2: First-page text parsing
        if text is None:
            text = self._extract_text_from_pdf(pdf_path)

        parsed_meta = self._extract_from_first_page(text)
        metadata.update({k: v for k, v in parsed_meta.items() if v and not metadata[k]})

        # Check if we have minimum required fields AND quality title
        if metadata['title'] and metadata['year'] and self._is_quality_title(metadata['title']):
            metadata['extraction_method'] = 'text_parsing'
            return metadata

        # Tier 3: LLM extraction (ALWAYS use for poor quality titles)
        if self.use_llm_fallback:
            if text is None:
                text = self._extract_text_from_pdf(pdf_path)
            llm_meta = self._extract_with_llm(text[:4000])  # First ~2 pages
            # LLM takes precedence over garbage titles
            metadata.update({k: v for k, v in llm_meta.items() if v})
            if metadata['title']:
                metadata['extraction_method'] = 'llm'
        
        # Fallback: use filename as title if nothing else worked
        if not metadata['title']:
            metadata['title'] = pdf_path.stem.replace('_', ' ').title()
            metadata['extraction_method'] = 'filename'
        
        return metadata
    
    def _is_quality_title(self, title: str) -> bool:
        """
        Check if extracted title looks like a real paper title (not garbage/headers)

        Returns False if title contains common indicators of bad extraction:
        - URLs or DOIs
        - Page numbers
        - Journal website headers
        - Copyright notices
        - "www." or "http"
        """
        if not title or len(title) < 10:
            return False

        title_lower = title.lower()

        # Bad indicators
        bad_patterns = [
            'www.', 'http', '.com', '.org', '.edu',
            'doi.org', '◆', '•',
            'volume', 'number', 'page',
            'copyright ©', 'all rights reserved',
            'for personal use only',
            'no other uses without permission',
            'this is an open access article'
        ]

        for pattern in bad_patterns:
            if pattern in title_lower:
                return False

        # Good indicator: title should have some lowercase letters (not all caps header)
        has_mixed_case = any(c.islower() for c in title) and any(c.isupper() for c in title)

        return has_mixed_case or len(title.split()) > 5

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF first 2 pages for metadata"""
        if not pypdf:
            return ""
        
        text_parts = []
        try:
            with open(pdf_path, 'rb') as file:
                if hasattr(pypdf, 'PdfReader'):
                    pdf_reader = pypdf.PdfReader(file)
                    pages_to_read = min(2, len(pdf_reader.pages))
                    for i in range(pages_to_read):
                        text_parts.append(pdf_reader.pages[i].extract_text())
                else:
                    pdf_reader = pypdf.PdfFileReader(file)
                    pages_to_read = min(2, pdf_reader.numPages)
                    for i in range(pages_to_read):
                        text_parts.append(pdf_reader.getPage(i).extractText())
        except Exception as e:
            print(f"   Warning: Could not extract text from {pdf_path.name}: {e}")
        
        return '\n'.join(text_parts)
    
    def _extract_from_pdf_metadata(self, pdf_path: Path) -> Dict:
        """Tier 1: Extract from embedded PDF metadata"""
        metadata = {}
        
        if not pypdf:
            return metadata
        
        try:
            with open(pdf_path, 'rb') as file:
                if hasattr(pypdf, 'PdfReader'):
                    pdf_reader = pypdf.PdfReader(file)
                    info = pdf_reader.metadata
                else:
                    pdf_reader = pypdf.PdfFileReader(file)
                    info = pdf_reader.getDocumentInfo()
                
                if info:
                    # Extract title
                    if hasattr(info, 'title') and info.title:
                        metadata['title'] = str(info.title).strip()
                    elif '/Title' in info:
                        metadata['title'] = str(info['/Title']).strip()
                    
                    # Extract author
                    if hasattr(info, 'author') and info.author:
                        author_str = str(info.author).strip()
                        metadata['authors'] = [author_str]
                        metadata['first_author'] = author_str
                    elif '/Author' in info:
                        author_str = str(info['/Author']).strip()
                        metadata['authors'] = [author_str]
                        metadata['first_author'] = author_str
                    
                    # Try to extract year from creation date
                    date_field = None
                    if hasattr(info, 'creation_date'):
                        date_field = info.creation_date
                    elif '/CreationDate' in info:
                        date_field = info['/CreationDate']
                    
                    if date_field:
                        year_match = self.year_pattern.search(str(date_field))
                        if year_match:
                            metadata['year'] = int(year_match.group())
        
        except Exception as e:
            print(f"   Warning: Could not read PDF metadata from {pdf_path.name}: {e}")
        
        return metadata
    
    def _extract_from_first_page(self, text: str) -> Dict:
        """Tier 2: Parse first page text for metadata"""
        metadata = {}
        
        if not text:
            return metadata
        
        lines = text.split('\n')
        first_500_chars = text[:500]
        
        # Extract DOI
        doi_match = self.doi_pattern.search(text)
        if doi_match:
            metadata['doi'] = doi_match.group()
        
        # Extract PMID
        pmid_match = self.pmid_pattern.search(text)
        if pmid_match:
            metadata['pmid'] = pmid_match.group(1)
        
        # Extract year (look for 4-digit year in first 500 chars)
        year_matches = self.year_pattern.findall(first_500_chars)
        if year_matches:
            # Most recent year is likely publication year
            metadata['year'] = int(max(year_matches))
        
        # Extract title (heuristic: first substantial line, often in larger font)
        # Usually within first 10 lines
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if len(line) > 20 and len(line) < 300 and not line.startswith('http'):
                # Avoid lines that look like URLs, page numbers, etc.
                if not re.match(r'^[\d\s\-/]+$', line):  # Not just numbers/dates
                    metadata['title'] = line
                    break
        
        # Try to identify journal name (common patterns)
        journal_patterns = [
            r'(Journal of [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'([A-Z][a-z]+ Medicine)',
            r'(Clinical [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'(The [A-Z][a-z]+ Journal)',
            r'(JAMA|BMJ|Lancet|Nature|Science)(?:\s|$)',
        ]
        
        for pattern in journal_patterns:
            match = re.search(pattern, first_500_chars)
            if match:
                metadata['journal'] = match.group(1)
                break
        
        return metadata
    
    def _extract_with_llm(self, text: str) -> Dict:
        """Tier 3: Use LLM for structured extraction"""
        metadata = {}
        
        try:
            # Only import google.generativeai if we need it
            import google.generativeai as genai
            
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                print("   Warning: GEMINI_API_KEY not set, skipping LLM metadata extraction")
                return metadata
            
            genai.configure(api_key=api_key)
            # Use latest Gemini model for metadata extraction
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""Extract bibliographic metadata from this academic paper text. Return ONLY a JSON object with these fields:
{{
    "title": "full paper title",
    "authors": ["Author1", "Author2"],
    "first_author": "Last name of first author",
    "year": 2023,
    "journal": "journal name",
    "volume": "volume number",
    "pages": "page range",
    "doi": "DOI if available",
    "pmid": "PMID if available"
}}

If a field is not found, use null. Return ONLY the JSON, no other text.

Paper text:
{text}"""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (might be wrapped in markdown code blocks)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            # Parse JSON
            llm_data = json.loads(response_text)
            
            # Clean and validate
            if llm_data.get('title'):
                metadata['title'] = llm_data['title']
            if llm_data.get('authors') and isinstance(llm_data['authors'], list):
                metadata['authors'] = llm_data['authors']
            if llm_data.get('first_author'):
                metadata['first_author'] = llm_data['first_author']
            if llm_data.get('year'):
                try:
                    metadata['year'] = int(llm_data['year'])
                except:
                    pass
            if llm_data.get('journal'):
                metadata['journal'] = llm_data['journal']
            if llm_data.get('volume'):
                metadata['volume'] = str(llm_data['volume'])
            if llm_data.get('pages'):
                metadata['pages'] = llm_data['pages']
            if llm_data.get('doi'):
                metadata['doi'] = llm_data['doi']
            if llm_data.get('pmid'):
                metadata['pmid'] = str(llm_data['pmid'])
            
            print(f"   ✓ LLM extracted metadata: {metadata.get('title', 'Unknown')[:50]}...")
            
        except ImportError:
            print("   Warning: google-generativeai not installed, skipping LLM extraction")
        except Exception as e:
            print(f"   Warning: LLM metadata extraction failed: {e}")
        
        return metadata


class CitationFormatter:
    """
    Format citations in various academic styles
    """
    
    def format_ama(self, metadata: Dict) -> str:
        """
        Format citation in AMA (American Medical Association) style
        
        Example: Smith JK, Johnson AM, Brown RL. Impact of ASP interventions 
                 on ICU antibiotic use. JAMA. 2023;329(15):1234-1245. 
                 doi:10.1001/jama.2023.12345
        """
        parts = []
        
        # Authors (last name + initials)
        if metadata.get('authors'):
            author_list = metadata['authors'][:6]  # AMA uses max 6 authors
            formatted_authors = []
            for author in author_list:
                # Handle different author formats
                if ',' in author:
                    # Already in "Last, First" format
                    formatted_authors.append(author.replace(', ', ' '))
                else:
                    formatted_authors.append(author)
            
            if len(metadata['authors']) > 6:
                authors_str = ', '.join(formatted_authors) + ', et al'
            else:
                authors_str = ', '.join(formatted_authors)
            parts.append(authors_str + '.')
        
        # Title
        if metadata.get('title'):
            parts.append(metadata['title'].rstrip('.') + '.')
        
        # Journal with volume/pages
        if metadata.get('journal'):
            journal_part = metadata['journal']
            if metadata.get('year'):
                journal_part += f" {metadata['year']}"
            if metadata.get('volume'):
                journal_part += f";{metadata['volume']}"
                if metadata.get('pages'):
                    journal_part += f":{metadata['pages']}"
            journal_part += '.'
            parts.append(journal_part)
        elif metadata.get('year'):
            # Year alone if no journal
            parts.append(f"{metadata['year']}.")
        
        # DOI
        if metadata.get('doi'):
            parts.append(f"doi:{metadata['doi']}")
        
        # PMID as fallback
        if metadata.get('pmid') and not metadata.get('doi'):
            parts.append(f"PMID: {metadata['pmid']}")
        
        return ' '.join(parts)
    
    def format_inline(self, metadata: Dict) -> str:
        """
        Format inline citation: Author et al. (Year)
        or: Author (Year) if single author
        """
        if not metadata.get('first_author') and not metadata.get('authors'):
            return metadata.get('title', 'Unknown')[:30] + '...'
        
        # Get first author last name
        first_author = metadata.get('first_author')
        if not first_author and metadata.get('authors'):
            first_author = metadata['authors'][0]
        
        # Extract last name
        if ',' in first_author:
            last_name = first_author.split(',')[0]
        elif ' ' in first_author:
            last_name = first_author.split()[-1]
        else:
            last_name = first_author
        
        # Format based on author count
        num_authors = len(metadata.get('authors', []))
        if num_authors > 2:
            author_str = f"{last_name} et al."
        elif num_authors == 2:
            author_str = f"{last_name} and {metadata['authors'][1].split(',')[0] if ',' in metadata['authors'][1] else metadata['authors'][1]}"
        else:
            author_str = last_name
        
        # Add year
        year = metadata.get('year', 'n.d.')
        return f"{author_str} ({year})"


class ASPLiteratureRAG:
    """
    Retrieval-Augmented Generation system for ASP literature

    Provides semantic search over antimicrobial stewardship research papers
    using PubMedBERT embeddings and ChromaDB vector store.
    """

    def __init__(
        self,
        pdf_dir: str = None,
        embeddings_dir: str = None,
        embedding_model: str = "BAAI/bge-large-en",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        collection_name: str = "asp_literature"
    ):
        """
        Initialize ASP Literature RAG system

        Args:
            pdf_dir: Directory containing PDF files (default: asp_literature/pdfs/)
            embeddings_dir: Directory for vector store (default: asp_literature/embeddings/)
            embedding_model: Sentence transformer model (default: PubMedBERT)
            chunk_size: Text chunk size in tokens (default: 512)
            chunk_overlap: Overlap between chunks in tokens (default: 50)
            collection_name: ChromaDB collection name
        """
        # Set default paths (use persistent storage in production for embeddings)
        project_root = Path(__file__).parent
        data_dir = Path('/var/app/current/data') if Path('/var/app/current/data').exists() else project_root

        # PDFs stay in the application directory (read-only literature)
        self.pdf_dir = Path(pdf_dir) if pdf_dir else project_root / "asp_literature" / "pdfs"
        # Embeddings go to persistent storage (generated at runtime)
        self.embeddings_dir = Path(embeddings_dir) if embeddings_dir else data_dir / "literature_embeddings"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = collection_name
        self.text_splitter = self._build_text_splitter()

        # Ensure directories exist
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔬 Initializing ASP Literature RAG System")
        print(f"   PDF directory: {self.pdf_dir}")
        print(f"   Embeddings directory: {self.embeddings_dir}")

        # Initialize embedding model
        print(f"   Loading embedding model: {embedding_model}")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        trust_remote = "BAAI" in embedding_model or "bge" in embedding_model.lower()
        self.embedding_model = SentenceTransformer(
            embedding_model,
            device=device,
            trust_remote_code=trust_remote
        )
        # Recommended for BGE models
        if hasattr(self.embedding_model, "max_seq_length"):
            self.embedding_model.max_seq_length = max(self.embedding_model.max_seq_length, self.chunk_size)
        print(f"   ✓ Model loaded (embedding dim: {self.embedding_model.get_sentence_embedding_dimension()})")

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.embeddings_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection with cosine similarity
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            doc_count = self.collection.count()
            print(f"   ✓ Loaded existing collection with {doc_count} chunks")
        except:
            print(f"   Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Antimicrobial Stewardship Research Literature",
                         "hnsw:space": "cosine"}  # Use cosine similarity
            )
            print(f"   ✓ Collection created (empty)")
        
        # Initialize metadata extractor and citation formatter
        self.metadata_extractor = PDFMetadataExtractor(use_llm_fallback=True)
        self.citation_formatter = CitationFormatter()
        print(f"   ✓ Metadata extraction enabled (with LLM fallback)")

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        if not pypdf:
            raise ImportError("pypdf or PyPDF2 required for PDF processing. Install with: pip install pypdf")

        text = []
        try:
            with open(pdf_path, 'rb') as file:
                if hasattr(pypdf, 'PdfReader'):
                    # pypdf (newer)
                    pdf_reader = pypdf.PdfReader(file)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                else:
                    # PyPDF2 (older)
                    pdf_reader = pypdf.PdfFileReader(file)
                    for page_num in range(pdf_reader.numPages):
                        page = pdf_reader.getPage(page_num)
                        text.append(page.extractText())
        except Exception as e:
            print(f"   Warning: Error reading {pdf_path.name}: {e}")
            return ""

        return '\n'.join(text)

    def _build_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Create a token-aware text splitter that respects tables/bullets.
        Falls back to character-based splitting if tiktoken encoder is unavailable.
        """
        try:
            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                model_name="gpt-3.5-turbo",
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            print(f"   ✓ Using tiktoken-based splitter (chunk={self.chunk_size}, overlap={self.chunk_overlap})")
            return splitter
        except Exception as exc:
            print(f"   ⚠ Warning: Token splitter unavailable ({exc}); using character-based fallback")
            return RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len
            )

    def chunk_text(self, text: str) -> List[str]:
        """Chunk text using the configured splitter"""
        if not self.text_splitter:
            self.text_splitter = self._build_text_splitter()
        return self.text_splitter.split_text(text)

    def index_pdfs(self, force_reindex: bool = False):
        """
        Index all PDFs in the pdf_dir with metadata extraction

        Args:
            force_reindex: If True, re-index even if already indexed
        """
        # Check if already indexed
        if not force_reindex and self.collection.count() > 0:
            print(f"   Collection already has {self.collection.count()} chunks")
            print(f"   Use force_reindex=True to re-index")
            return

        if not self.pdf_dir.exists():
            print(f"   Warning: PDF directory not found: {self.pdf_dir}")
            return

        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"   Warning: No PDF files found in {self.pdf_dir}")
            return

        print(f"\n📚 Indexing {len(pdf_files)} PDF files with metadata extraction...")

        all_chunks = []
        all_metadata = []
        all_ids = []

        for idx, pdf_path in enumerate(pdf_files, 1):
            print(f"   [{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")

            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text.strip():
                print(f"       Warning: No text extracted")
                continue

            # Extract metadata
            print(f"       Extracting metadata...")
            paper_metadata = self.metadata_extractor.extract_metadata(pdf_path, text)
            print(f"       ✓ Method: {paper_metadata.get('extraction_method', 'unknown')}")
            if paper_metadata.get('title'):
                print(f"       ✓ Title: {paper_metadata['title'][:60]}...")
            
            # Generate unique paper ID
            paper_id = self._generate_paper_id(pdf_path, paper_metadata)

            # Chunk text
            chunks = self.chunk_text(text)
            print(f"       Created {len(chunks)} chunks")

            # Prepare for insertion with rich metadata
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{paper_id}_chunk_{chunk_idx}"
                all_chunks.append(chunk)
                
                # Build metadata dict (ChromaDB requires all values to be simple types and not None)
                chunk_metadata = {
                    "filename": pdf_path.name,
                    "paper_id": paper_id,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    
                    # Bibliographic metadata (only include if not None/empty)
                    "title": paper_metadata.get('title') or '',
                    "first_author": paper_metadata.get('first_author') or '',
                    "year": str(paper_metadata.get('year')) if paper_metadata.get('year') else '',
                    "journal": paper_metadata.get('journal') or '',
                    "doi": paper_metadata.get('doi') or '',
                    "pmid": paper_metadata.get('pmid') or '',
                    
                    # Store authors as JSON string (ChromaDB doesn't support lists in metadata)
                    "authors_json": json.dumps(paper_metadata.get('authors', [])),
                    "volume": paper_metadata.get('volume') or '',
                    "pages": paper_metadata.get('pages') or '',
                    "extraction_method": paper_metadata.get('extraction_method') or ''
                }
                
                all_metadata.append(chunk_metadata)
                all_ids.append(chunk_id)

        if not all_chunks:
            print("   No chunks to index!")
            return

        print(f"\n🔄 Computing embeddings for {len(all_chunks)} chunks...")
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True
        )

        print(f"💾 Storing in ChromaDB...")
        self.collection.add(
            documents=all_chunks,
            embeddings=embeddings.tolist(),
            metadatas=all_metadata,
            ids=all_ids
        )

        print(f"✅ Indexing complete! {len(all_chunks)} chunks indexed")

    def index_new_pdfs_and_transfer(self, transferred_subdir: str = "transferred") -> int:
        """
        Index only NEW PDFs and move them to a transferred subdirectory after indexing.
        This prevents re-indexing the same PDFs multiple times.

        Args:
            transferred_subdir: Name of subdirectory to move processed PDFs

        Returns:
            Number of new PDFs indexed
        """
        import shutil

        # Create transferred directory if it doesn't exist
        transferred_dir = self.pdf_dir / transferred_subdir
        transferred_dir.mkdir(exist_ok=True)

        # Get existing paper IDs from collection
        existing_ids = set()
        try:
            results = self.collection.get(limit=10000, include=['metadatas'])
            for meta in results['metadatas']:
                if 'paper_id' in meta:
                    existing_ids.add(meta['paper_id'])
        except:
            pass

        print(f"📊 Found {len(existing_ids)} already-indexed papers in collection")

        # Find new PDFs (not yet indexed)
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        new_pdfs = []

        for pdf_path in pdf_files:
            # Generate paper ID to check if already indexed
            text_sample = self.extract_text_from_pdf(pdf_path)[:2000]  # Just sample for ID
            metadata_sample = {'title': '', 'pmid': ''}  # Will be extracted properly later
            paper_id = self._generate_paper_id(pdf_path, metadata_sample)

            if paper_id not in existing_ids:
                new_pdfs.append(pdf_path)

        if not new_pdfs:
            print("✓ No new PDFs to index")
            return 0

        print(f"\n📚 Found {len(new_pdfs)} NEW PDFs to index:")
        for pdf in new_pdfs:
            print(f"   - {pdf.name}")

        # Index new PDFs
        all_chunks = []
        all_metadata = []
        all_ids = []
        processed_pdfs = []

        for idx, pdf_path in enumerate(new_pdfs, 1):
            print(f"\n   [{idx}/{len(new_pdfs)}] Processing: {pdf_path.name}")

            try:
                # Extract text
                text = self.extract_text_from_pdf(pdf_path)
                if not text.strip():
                    print(f"       Warning: No text extracted, skipping")
                    continue

                # Extract metadata
                print(f"       Extracting metadata...")
                paper_metadata = self.metadata_extractor.extract_metadata(pdf_path, text)
                print(f"       ✓ Method: {paper_metadata.get('extraction_method', 'unknown')}")
                if paper_metadata.get('title'):
                    print(f"       ✓ Title: {paper_metadata['title'][:60]}...")

                # Generate unique paper ID
                paper_id = self._generate_paper_id(pdf_path, paper_metadata)

                # Chunk text
                chunks = self.chunk_text(text)
                print(f"       Created {len(chunks)} chunks")

                # Prepare for insertion
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{paper_id}_chunk_{chunk_idx}"
                    all_chunks.append(chunk)

                    chunk_metadata = {
                        "filename": pdf_path.name,
                        "paper_id": paper_id,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                        "title": paper_metadata.get('title') or '',
                        "first_author": paper_metadata.get('first_author') or '',
                        "year": str(paper_metadata.get('year')) if paper_metadata.get('year') else '',
                        "journal": paper_metadata.get('journal') or '',
                        "doi": paper_metadata.get('doi') or '',
                        "pmid": paper_metadata.get('pmid') or '',
                        "authors_json": json.dumps(paper_metadata.get('authors', [])),
                        "volume": paper_metadata.get('volume') or '',
                        "pages": paper_metadata.get('pages') or '',
                        "extraction_method": paper_metadata.get('extraction_method') or ''
                    }

                    all_metadata.append(chunk_metadata)
                    all_ids.append(chunk_id)

                processed_pdfs.append(pdf_path)

            except Exception as e:
                print(f"       ✗ Error processing {pdf_path.name}: {e}")
                continue

        if not all_chunks:
            print("\n   No chunks to index!")
            return 0

        # Compute embeddings and store
        print(f"\n🔄 Computing embeddings for {len(all_chunks)} chunks...")
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True
        )

        print(f"💾 Storing in ChromaDB...")
        self.collection.add(
            documents=all_chunks,
            embeddings=embeddings.tolist(),
            metadatas=all_metadata,
            ids=all_ids
        )

        print(f"✅ Indexing complete! {len(all_chunks)} chunks indexed")

        # Move processed PDFs to transferred directory
        print(f"\n📁 Moving {len(processed_pdfs)} indexed PDFs to {transferred_dir}...")
        for pdf_path in processed_pdfs:
            try:
                dest = transferred_dir / pdf_path.name
                shutil.move(str(pdf_path), str(dest))
                print(f"   ✓ Moved: {pdf_path.name}")
            except Exception as e:
                print(f"   ✗ Error moving {pdf_path.name}: {e}")

        print(f"\n✅ Complete! Indexed {len(processed_pdfs)} new PDFs")
        print(f"   Total chunks in collection: {self.collection.count()}")

        return len(processed_pdfs)

    def _generate_paper_id(self, pdf_path: Path, metadata: Dict) -> str:
        """
        Generate unique paper ID (backward compatible with PMID-based naming)

        Args:
            pdf_path: Path to PDF file
            metadata: Extracted metadata

        Returns:
            Unique paper ID string
        """
        # Try PMID from filename (backward compatibility)
        if pdf_path.stem.isdigit() and len(pdf_path.stem) == 8:
            return f"pmid_{pdf_path.stem}"

        # Try PMID from metadata
        if metadata.get('pmid'):
            return f"pmid_{metadata['pmid']}"

        # Generate semantic ID from metadata
        author = metadata.get('first_author', 'unknown')
        if author and author != 'unknown':
            author = author.split(',')[0].lower()  # Get last name
            author = re.sub(r'[^a-z]', '', author)  # Remove non-letters
        else:
            author = 'unknown'

        year = metadata.get('year')
        if year is None or year == '':
            year = 'nodate'

        # Extract keyword from title
        title = metadata.get('title', '')
        if title:
            # Get first meaningful word from title (skip common words)
            title_words = [w.lower() for w in re.findall(r'\b[a-z]{4,}\b', title.lower())]
            skip_words = {'study', 'analysis', 'review', 'impact', 'effect', 'outcomes', 'antimicrobial', 'antibiotic'}
            keyword = next((w for w in title_words if w not in skip_words), title_words[0] if title_words else 'paper')
        else:
            # Use filename as keyword when no title exists (ensures uniqueness)
            keyword = pdf_path.stem[:20].lower()

        # If we still have completely generic metadata, append filename hash to ensure uniqueness
        if author == 'unknown' and year == 'nodate' and keyword == 'paper':
            # Use sanitized filename to ensure uniqueness
            filename_id = re.sub(r'[^a-z0-9]', '', pdf_path.stem.lower())[:30]
            return f"unknown_{filename_id}"

        return f"{author}_{year}_{keyword}"

    def search(
        self,
        query: str,
        n_results: int = 5,
        min_similarity: float = 0.2
    ) -> List[Dict]:
        """
        Search for relevant literature excerpts

        Args:
            query: Search query
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of dicts with keys: text, filename, pmid, similarity
        """
        if self.collection.count() == 0:
            print("   Warning: Collection is empty. Run index_pdfs() first.")
            return []

        # Encode query
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results * 2  # Fetch more to filter by similarity
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            similarity = 1 - results['distances'][0][i]  # Convert distance to similarity


            if similarity < min_similarity:
                continue

            # Reconstruct full metadata from chunk metadata
            meta = results['metadatas'][0][i]
            full_metadata = {
                'text': results['documents'][0][i],
                'filename': meta['filename'],
                'paper_id': meta.get('paper_id', meta.get('pmid', '')),
                'similarity': round(similarity, 3),
                
                # Bibliographic metadata for citations
                'title': meta.get('title', ''),
                'first_author': meta.get('first_author', ''),
                'year': int(meta['year']) if meta.get('year') and meta['year'].isdigit() else None,
                'journal': meta.get('journal', ''),
                'doi': meta.get('doi', ''),
                'pmid': meta.get('pmid', ''),
                'authors': json.loads(meta.get('authors_json', '[]')),
                'volume': meta.get('volume', ''),
                'pages': meta.get('pages', '')
            }
            
            formatted_results.append(full_metadata)

        # Return top n_results
        return formatted_results[:n_results]

    def get_context_for_query(
        self,
        query: str,
        max_results: int = 3,
        max_length: int = 1500
    ) -> str:
        """
        Get formatted context string for RAG augmentation with AMA-style citations

        Args:
            query: Search query
            max_results: Maximum number of paper excerpts
            max_length: Maximum total character length

        Returns:
            Formatted string with relevant excerpts and AMA-style citations
        """
        results = self.search(query, n_results=max_results * 2)  # Get extras for deduplication

        if not results:
            return ""

        # Deduplicate by paper_id to ensure diverse sources
        seen_papers = set()
        unique_results = []
        for result in results:
            paper_id = result.get('paper_id', result.get('pmid', ''))
            if paper_id not in seen_papers:
                seen_papers.add(paper_id)
                unique_results.append(result)
                if len(unique_results) >= max_results:
                    break

        if not unique_results:
            return ""

        context_parts = []
        references = []
        total_length = 0

        for ref_num, result in enumerate(unique_results, 1):
            # Limit excerpt length
            excerpt = result['text'][:500]
            
            # Create inline citation
            inline_cite = self.citation_formatter.format_inline(result)
            
            # Format: "As shown by Author et al. (Year), [excerpt text]. [ref_num]"
            part = f"According to {inline_cite}, {excerpt} [{ref_num}]"

            if total_length + len(part) > max_length:
                break

            context_parts.append(part)
            
            # Build full AMA reference
            full_citation = self.citation_formatter.format_ama(result)
            references.append(f"[{ref_num}] {full_citation}")
            
            total_length += len(part)

        if not context_parts:
            return ""

        # Combine excerpts and references
        context = "\n\n".join(context_parts)
        if references:
            context += "\n\nReferences:\n" + "\n".join(references)
        
        return context



def main():
    """Test/demo the RAG system"""
    print("=" * 80)
    print("ASP Literature RAG System - Test")
    print("=" * 80)

    # Initialize
    rag = ASPLiteratureRAG()

    # Index PDFs (if needed)
    rag.index_pdfs()

    # Test search
    print("\n" + "=" * 80)
    print("Test Search: 'antimicrobial stewardship interventions'")
    print("=" * 80)

    results = rag.search("antimicrobial stewardship interventions", n_results=3)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['filename']} (similarity: {result['similarity']})")
        print(f"   {result['text'][:200]}...")

    # Test context generation
    print("\n" + "=" * 80)
    print("Test Context Generation")
    print("=" * 80)
    context = rag.get_context_for_query("reducing broad-spectrum antibiotic use")
    print(context[:500] + "...")


if __name__ == "__main__":
    main()
