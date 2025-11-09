#!/usr/bin/env python3
"""
ASP Literature RAG System
Independent RAG module for antimicrobial stewardship literature
Uses PubMedBERT embeddings and ChromaDB for vector search
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
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
        embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO",
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
        # Set default paths
        project_root = Path(__file__).parent
        self.pdf_dir = Path(pdf_dir) if pdf_dir else project_root / "asp_literature" / "pdfs"
        self.embeddings_dir = Path(embeddings_dir) if embeddings_dir else project_root / "asp_literature" / "embeddings"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = collection_name

        # Ensure directories exist
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔬 Initializing ASP Literature RAG System")
        print(f"   PDF directory: {self.pdf_dir}")
        print(f"   Embeddings directory: {self.embeddings_dir}")

        # Initialize embedding model
        print(f"   Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print(f"   ✓ Model loaded (embedding dim: {self.embedding_model.get_sentence_embedding_dimension()})")

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.embeddings_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            doc_count = self.collection.count()
            print(f"   ✓ Loaded existing collection with {doc_count} chunks")
        except:
            print(f"   Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Antimicrobial Stewardship Research Literature"}
            )
            print(f"   ✓ Collection created (empty)")

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

    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Chunk text into overlapping segments
        Simple sentence-based chunking
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap

        # Split into sentences (simple regex)
        sentences = re.split(r'[.!?]\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Estimate tokens (rough: ~1.3 chars per token for English)
            sentence_tokens = len(sentence) // 1.3

            if current_length + sentence_tokens > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))

                # Start new chunk with overlap (keep last few sentences)
                overlap_sentences = int(len(current_chunk) * (overlap / chunk_size))
                current_chunk = current_chunk[-overlap_sentences:] if overlap_sentences > 0 else []
                current_length = sum(len(s) // 1.3 for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_tokens

        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def index_pdfs(self, force_reindex: bool = False):
        """
        Index all PDFs in the pdf_dir

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

        print(f"\n📚 Indexing {len(pdf_files)} PDF files...")

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

            # Chunk text
            chunks = self.chunk_text(text)
            print(f"       Created {len(chunks)} chunks")

            # Prepare for insertion
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{pdf_path.stem}_chunk_{chunk_idx}"
                all_chunks.append(chunk)
                all_metadata.append({
                    "filename": pdf_path.name,
                    "pmid": pdf_path.stem,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks)
                })
                all_ids.append(chunk_id)

        if not all_chunks:
            print("   No chunks to index!")
            return

        print(f"\n🔄 Computing embeddings for {len(all_chunks)} chunks...")
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32
        )

        print(f"💾 Storing in ChromaDB...")
        self.collection.add(
            documents=all_chunks,
            embeddings=embeddings.tolist(),
            metadatas=all_metadata,
            ids=all_ids
        )

        print(f"✅ Indexing complete! {len(all_chunks)} chunks indexed")

    def search(
        self,
        query: str,
        n_results: int = 5,
        min_similarity: float = 0.3
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
        query_embedding = self.embedding_model.encode(query)

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

            formatted_results.append({
                'text': results['documents'][0][i],
                'filename': results['metadatas'][0][i]['filename'],
                'pmid': results['metadatas'][0][i]['pmid'],
                'similarity': round(similarity, 3)
            })

        # Return top n_results
        return formatted_results[:n_results]

    def get_context_for_query(
        self,
        query: str,
        max_results: int = 3,
        max_length: int = 1500
    ) -> str:
        """
        Get formatted context string for RAG augmentation

        Args:
            query: Search query
            max_results: Maximum number of paper excerpts
            max_length: Maximum total character length

        Returns:
            Formatted string with relevant excerpts and citations
        """
        results = self.search(query, n_results=max_results)

        if not results:
            return ""

        context_parts = []
        total_length = 0

        for result in results:
            excerpt = result['text'][:500]  # Limit each excerpt
            citation = f"[PMID {result['pmid']}]"

            part = f"{citation} {excerpt}"

            if total_length + len(part) > max_length:
                break

            context_parts.append(part)
            total_length += len(part)

        if not context_parts:
            return ""

        return "\n\n".join(context_parts)


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
