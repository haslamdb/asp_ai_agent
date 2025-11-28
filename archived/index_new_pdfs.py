#!/usr/bin/env python3
"""
Script to index new PDFs and move them to the transferred directory.
This prevents re-indexing the same PDFs multiple times.

Usage:
    python3 index_new_pdfs.py

Place new PDF files in: asp_literature/pdfs/
After indexing, they will be moved to: asp_literature/pdfs/transferred/
"""

from asp_rag_module import ASPLiteratureRAG

def main():
    print("=" * 70)
    print("ASP Literature RAG - Incremental PDF Indexer")
    print("=" * 70)
    print()

    # Initialize RAG
    print("Initializing RAG system...")
    rag = ASPLiteratureRAG()
    print(f"Current collection size: {rag.collection.count()} chunks\n")

    # Index new PDFs and transfer them
    num_indexed = rag.index_new_pdfs_and_transfer(transferred_subdir="transferred")

    print()
    print("=" * 70)
    if num_indexed > 0:
        print(f"✅ SUCCESS: Indexed {num_indexed} new PDF(s)")
        print(f"   New collection size: {rag.collection.count()} chunks")
        print(f"   Indexed PDFs moved to: asp_literature/pdfs/transferred/")
    else:
        print("✅ No new PDFs to index")
        print(f"   Collection remains at: {rag.collection.count()} chunks")
    print("=" * 70)

    # Restart reminder
    if num_indexed > 0:
        print()
        print("⚠️  REMINDER: Restart the Flask server to use the updated collection")
        print("   bash /tmp/restart_server.sh")

if __name__ == "__main__":
    main()
