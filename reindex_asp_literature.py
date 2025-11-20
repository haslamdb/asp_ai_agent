#!/usr/bin/env python3
"""
Reindex ASP Literature
Convenience script to reindex all PDFs in asp_literature/pdfs/
"""

from asp_rag_module import ASPLiteratureRAG

def main():
    """Reindex all ASP literature PDFs"""
    print("=" * 80)
    print("Reindexing ASP Literature")
    print("=" * 80)

    # Initialize RAG system
    rag = ASPLiteratureRAG()

    # Force reindex of all PDFs
    rag.index_pdfs(force_reindex=True)

    print("\n" + "=" * 80)
    print("✅ Reindexing Complete!")
    print(f"   Total chunks indexed: {rag.collection.count()}")
    print("=" * 80)

if __name__ == "__main__":
    main()
