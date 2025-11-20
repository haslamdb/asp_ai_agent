
#!/usr/bin/env python3
"""
Re-index ASP Literature using EndNote Metadata
Extracts high-quality metadata (PMID, Title, Author, Year) from EndNote database
and links it to the corresponding PDFs for indexing.
"""

import os
import sys
import sqlite3
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.getcwd())

from asp_rag_module import ASPLiteratureRAG

# Paths
SDB_PATH = 'asp_literature/asp_library.Data/sdb/sdb.eni'
PDB_PATH = 'asp_literature/asp_library.Data/sdb/pdb.eni'
PDF_BASE_DIR = Path('asp_literature/asp_library.Data/PDF')

def get_endnote_metadata() -> Dict[str, Dict]:
    """
    Extract metadata from EndNote databases and map to PDF paths
    Returns: Dict mapping {pdf_filename: metadata_dict}
    """
    if not os.path.exists(SDB_PATH) or not os.path.exists(PDB_PATH):
        print(f"Error: EndNote databases not found at {SDB_PATH} or {PDB_PATH}")
        return {}

    print("📊 Reading EndNote metadata...")
    
    # Connect to databases
    conn_sdb = sqlite3.connect(SDB_PATH)
    cursor_sdb = conn_sdb.cursor()
    
    conn_pdb = sqlite3.connect(PDB_PATH)
    cursor_pdb = conn_pdb.cursor()
    
    # Get all PDFs and their ref_ids
    cursor_pdb.execute("SELECT refs_id, subkey FROM pdf_index")
    pdf_records = cursor_pdb.fetchall()
    
    metadata_map = {}
    
    print(f"   Found {len(pdf_records)} PDF records in index")
    
    for ref_id, subkey in pdf_records:
        if not subkey:
            continue
            
        # Clean subkey to get relative path (remove junk if any)
        try:
            if isinstance(subkey, bytes):
                subkey_str = subkey.decode('utf-8', errors='ignore')
            else:
                subkey_str = str(subkey)
            
            # Extract the path part (usually starts with digits/)
            rel_path = subkey_str.strip().split('\x00')[0] 
            
            # Get metadata for this ref_id
            cursor_sdb.execute(
                "SELECT title, author, year, accession_number, electronic_resource_number, secondary_title, volume, pages FROM refs WHERE id=?", 
                (ref_id,)
            )
            ref_data = cursor_sdb.fetchone()
            
            if ref_data:
                title, author, year, pmid, doi, journal, volume, pages = ref_data
                
                # Clean up data
                meta = {
                    'title': title.strip() if title else None,
                    'first_author': author.strip().split('\r')[0].split('\n')[0] if author else None,
                    'authors': [a.strip() for a in author.split('\r')] if author else [],
                    'year': int(year.strip()) if year and year.strip().isdigit() else None,
                    'pmid': pmid.strip() if pmid else None,
                    'doi': doi.strip() if doi else None,
                    'journal': journal.strip() if journal else None,
                    'volume': volume.strip() if volume else None,
                    'pages': pages.strip() if pages else None,
                    'rel_path': rel_path,
                    'filename': os.path.basename(rel_path)
                }
                
                # Map by filename
                metadata_map[meta['filename']] = meta
                
        except Exception as e:
            print(f"   Warning parsing record {ref_id}: {e}")

    conn_sdb.close()
    conn_pdb.close()
    
    print(f"   Mapped metadata for {len(metadata_map)} PDFs")
    return metadata_map

def reindex_with_endnote(incremental: bool = True):
    """
    Re-index using EndNote metadata

    Args:
        incremental: If True (default), preserve existing embeddings and only add new papers.
                    If False, delete everything and reindex from scratch.
    """

    # 1. Get EndNote metadata
    endnote_meta = get_endnote_metadata()
    if not endnote_meta:
        return

    # 2. Initialize RAG
    rag = ASPLiteratureRAG()

    if incremental:
        print("\n📊 Incremental indexing mode - preserving existing embeddings")
        print(f"   Current collection size: {rag.collection.count()} chunks")
    else:
        # FULL REINDEX: Clear existing collection
        print("\n🧹 Full reindex mode - clearing existing RAG collection...")
        try:
            rag.client.delete_collection(rag.collection_name)
            print("   ✓ Deleted old collection")
        except:
            pass

        # Re-create collection
        rag.collection = rag.client.create_collection(
            name=rag.collection_name,
            metadata={"description": "Antimicrobial Stewardship Research Literature",
                     "hnsw:space": "cosine"}
        )
        print("   ✓ Created fresh collection")
    
    # 3. Get existing indexed files (for incremental mode)
    existing_filenames = set()
    existing_pmids = set()

    if incremental:
        print("\n🔍 Checking already-indexed papers...")
        try:
            offset = 0
            batch_size = 10000
            while True:
                results = rag.collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=['metadatas']
                )
                if not results['metadatas']:
                    break

                for meta in results['metadatas']:
                    if 'filename' in meta:
                        existing_filenames.add(meta['filename'])
                    if 'pmid' in meta and meta['pmid']:
                        existing_pmids.add(meta['pmid'])

                offset += batch_size
                if len(results['metadatas']) < batch_size:
                    break

            print(f"   Found {len(existing_filenames)} already-indexed files")
            print(f"   Found {len(existing_pmids)} unique PMIDs already indexed")
        except Exception as e:
            print(f"   Warning: Could not retrieve existing data: {e}")

    # 4. Find PDFs to index
    if not PDF_BASE_DIR.exists():
        print(f"Error: PDF directory not found at {PDF_BASE_DIR}")
        return

    print(f"\n🔍 Scanning PDFs in {PDF_BASE_DIR}...")
    found_pdfs = list(PDF_BASE_DIR.rglob("*.pdf"))
    print(f"   Found {len(found_pdfs)} PDF files total")

    # 5. Process and Index
    print("\n📚 Indexing with EndNote metadata...")

    all_chunks = []
    all_metadata = []
    all_ids = []
    seen_pmids = set(existing_pmids)  # Start with already-indexed PMIDs
    
    # INCREASED CONTEXT: Larger chunks, larger overlap
    CHUNK_SIZE = 600  # Increased from 512
    OVERLAP = 100     # Increased from 50
    
    print(f"   Chunking settings: Size={CHUNK_SIZE}, Overlap={OVERLAP}")

    indexed_count = 0
    skipped_count = 0

    for idx, pdf_path in enumerate(found_pdfs, 1):
        filename = pdf_path.name

        # Look up metadata
        meta = endnote_meta.get(filename)

        if not meta:
            print(f"   [{idx}/{len(found_pdfs)}] ⚠️ No EndNote metadata for: {filename} (Skipping)")
            skipped_count += 1
            continue

        pmid = meta.get('pmid')

        # Skip if already indexed (incremental mode)
        if incremental:
            if filename in existing_filenames:
                if idx % 50 == 0:  # Only print every 50th to avoid spam
                    print(f"   [{idx}/{len(found_pdfs)}] ⏭️  Skipping already-indexed: {filename}")
                skipped_count += 1
                continue
            if pmid and pmid in seen_pmids:
                print(f"   [{idx}/{len(found_pdfs)}] ⏭️  Skipping duplicate PMID: {pmid} ({filename})")
                skipped_count += 1
                continue
        else:
            # Full reindex mode: still check for duplicates within current batch
            if pmid and pmid in seen_pmids:
                print(f"   [{idx}/{len(found_pdfs)}] ⏭️  Skipping duplicate PMID: {pmid} ({filename})")
                skipped_count += 1
                continue

        if pmid:
            seen_pmids.add(pmid)
            
        print(f"   [{idx}/{len(found_pdfs)}] Processing: {filename}")
        print(f"       Title: {meta.get('title')[:50]}...")
        print(f"       PMID: {meta.get('pmid', 'N/A')}")
        
        try:
            # Extract text
            text = rag.extract_text_from_pdf(pdf_path)
            if not text.strip():
                print(f"       Warning: No text extracted")
                continue
                
            # Generate ID
            if meta.get('pmid'):
                paper_id = f"pmid_{meta['pmid']}"
            else:
                paper_id = rag._generate_paper_id(pdf_path, meta)
            
            # Chunk text with new parameters
            chunks = rag.chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
            print(f"       Created {len(chunks)} chunks")
            
            # Create chunk objects
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{paper_id}_chunk_{chunk_idx}"
                all_chunks.append(chunk)
                
                chunk_metadata = {
                    "filename": filename,
                    "paper_id": paper_id,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "title": meta.get('title') or '',
                    "first_author": meta.get('first_author') or '',
                    "year": str(meta.get('year')) if meta.get('year') else '',
                    "journal": meta.get('journal') or '',
                    "doi": meta.get('doi') or '',
                    "pmid": meta.get('pmid') or '',
                    "authors_json": json.dumps(meta.get('authors', [])),
                    "volume": meta.get('volume') or '',
                    "pages": meta.get('pages') or '',
                    "extraction_method": "endnote_db"
                }
                
                all_metadata.append(chunk_metadata)
                all_ids.append(chunk_id)

            indexed_count += 1

        except Exception as e:
            print(f"       ✗ Error: {e}")
            skipped_count += 1

    # Summary before indexing
    print(f"\n📊 Summary:")
    print(f"   Total PDFs found: {len(found_pdfs)}")
    print(f"   Already indexed (skipped): {skipped_count}")
    print(f"   New PDFs to index: {indexed_count}")

    if not all_chunks:
        print("\n✅ No new chunks to index - everything is already indexed!")
        print(f"   Total collection size: {rag.collection.count()} chunks")
        return

    # 5. Update ChromaDB
    print(f"\n🔄 Storing {len(all_chunks)} chunks in ChromaDB...")
    
    batch_size = 100
    total_batches = (len(all_chunks) + batch_size - 1) // batch_size
    
    for i in range(0, len(all_chunks), batch_size):
        end_idx = min(i + batch_size, len(all_chunks))
        print(f"   Batch {i//batch_size + 1}/{total_batches}...", end='\r')
        
        batch_chunks = all_chunks[i:end_idx]
        batch_meta = all_metadata[i:end_idx]
        batch_ids = all_ids[i:end_idx]
        
        embeddings = rag.embedding_model.encode(batch_chunks)
        
        rag.collection.add(
            documents=batch_chunks,
            embeddings=embeddings.tolist(),
            metadatas=batch_meta,
            ids=batch_ids
        )
        
    print(f"\n✅ Indexing complete!")
    if incremental:
        print(f"   📊 New chunks added: {len(all_chunks)}")
        print(f"   📚 Total collection size: {rag.collection.count()} chunks")
        print(f"   💾 Existing embeddings preserved")
    else:
        print(f"   📚 Total collection size: {rag.collection.count()} chunks")
    print("   🔄 Restart the server to apply changes.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index ASP literature from EndNote")
    parser.add_argument(
        '--full',
        action='store_true',
        help='Force full reindex (deletes existing collection). Default is incremental.'
    )
    args = parser.parse_args()

    reindex_with_endnote(incremental=not args.full)
