#!/usr/bin/env python3
"""
OFFICIAL PDF INDEXING SCRIPT - ASP Literature RAG

Incrementally indexes NEW PDFs with LLM-enhanced metadata extraction.
This script ADDS to the existing collection, does NOT overwrite it.

WORKFLOW:
1. Place new PDF files in: asp_literature/pdfs/
2. Run this script: python3 index_new_pdfs_llm.py
3. Move indexed PDFs to transferred: mv asp_literature/pdfs/*.pdf asp_literature/pdfs/transferred/
4. Restart server: bash /tmp/restart_server.sh

FEATURES:
- ✅ INCREMENTAL: Only indexes NEW PDFs (skips already-indexed papers)
- Three-tier metadata extraction (embedded → text parsing → LLM fallback)
- Quality check for titles (rejects garbage/headers, triggers LLM)
- Gemini 2.0 Flash LLM for clean citation extraction
- Extracts: title, authors, year, journal, DOI, PMID
"""

from asp_rag_module import ASPLiteratureRAG
from dotenv import load_dotenv
import os

# Load environment variables (including GEMINI_API_KEY)
load_dotenv()

# Verify API key is loaded
if not os.environ.get('GEMINI_API_KEY'):
    print("❌ ERROR: GEMINI_API_KEY not found in environment")
    print("   Make sure it's set in .env file")
    exit(1)

print("✓ GEMINI_API_KEY loaded")
print("\nReindexing all PDFs with LLM-enhanced metadata extraction...")
print("This will use Gemini to extract clean titles, authors, and citations.\n")

# Initialize RAG
rag = ASPLiteratureRAG()

print(f"Current collection: {rag.collection.count()} chunks\n")

# Get list of already-indexed papers
print("Checking for already-indexed papers...")
existing_filenames = set()
try:
    results = rag.collection.get(limit=10000, include=['metadatas'])
    for meta in results['metadatas']:
        if 'filename' in meta:
            existing_filenames.add(meta['filename'])
    print(f"✓ Found {len(existing_filenames)} already-indexed papers\n")
except Exception as e:
    print(f"  Warning: Could not check existing papers: {e}\n")

# Find NEW PDFs to index
from pathlib import Path
pdf_dir = Path('asp_literature/pdfs')
all_pdfs = list(pdf_dir.glob('*.pdf'))
new_pdfs = [p for p in all_pdfs if p.name not in existing_filenames]

if not new_pdfs:
    print("✓ No new PDFs to index")
    print(f"  Collection remains at: {rag.collection.count()} chunks")
    exit(0)

print(f"📚 Found {len(new_pdfs)} NEW PDFs to index:")
for pdf in new_pdfs:
    print(f"   - {pdf.name}")
print()

# Index ONLY new PDFs
print("Indexing new PDFs with LLM metadata extraction...")
print("=" * 70)

import pypdf
from sentence_transformers import SentenceTransformer
import json

all_chunks = []
all_metadata = []
all_ids = []

for idx, pdf_path in enumerate(new_pdfs, 1):
    print(f"   [{idx}/{len(new_pdfs)}] Processing: {pdf_path.name}")

    try:
        # Extract text
        text = rag.extract_text_from_pdf(pdf_path)
        if not text.strip():
            print(f"       Warning: No text extracted, skipping")
            continue

        # Extract metadata with LLM
        print(f"       Extracting metadata...")
        paper_metadata = rag.metadata_extractor.extract_metadata(pdf_path, text)
        print(f"       ✓ Method: {paper_metadata.get('extraction_method', 'unknown')}")
        if paper_metadata.get('title'):
            print(f"       ✓ Title: {paper_metadata['title'][:60]}...")

        # Generate paper ID
        paper_id = rag._generate_paper_id(pdf_path, paper_metadata)

        # Chunk text
        chunks = rag.chunk_text(text)
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

    except Exception as e:
        print(f"       ✗ Error processing {pdf_path.name}: {e}")
        continue

if not all_chunks:
    print("\n   No chunks to index!")
    exit(0)

# Compute embeddings and ADD to existing collection
print(f"\n🔄 Computing embeddings for {len(all_chunks)} chunks...")
embeddings = rag.embedding_model.encode(
    all_chunks,
    show_progress_bar=True,
    batch_size=32
)

print(f"💾 Adding to existing collection...")
rag.collection.add(
    documents=all_chunks,
    embeddings=embeddings.tolist(),
    metadatas=all_metadata,
    ids=all_ids
)

print("=" * 70)
print(f"\n✓ Indexing complete! Added {len(all_chunks)} chunks")
print(f"Final collection size: {rag.collection.count()} chunks")
print("\nNow restart the server:")
print("  bash /tmp/restart_server.sh")
