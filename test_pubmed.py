#!/usr/bin/env python3
"""Test PubMed RAG functionality directly"""

from pubmed_rag_tools import PubMedRAGSystem

def test_pubmed_search():
    print("Testing PubMed search functionality...")
    
    # Initialize the RAG system
    rag = PubMedRAGSystem()
    
    # Test query
    query = "PMID:34350458"
    print(f"\nSearching for: {query}")
    
    # Perform search
    results = rag.retrieve(query, max_results=5)
    
    print(f"\nType of results: {type(results)}")
    print(f"Results: {results}")
    
    # Check if it's returning a tuple (docs, context)
    if isinstance(results, tuple):
        docs, context = results
        print(f"\nFound {len(docs)} documents")
        for i, doc in enumerate(docs, 1):
            print(f"\n--- Result {i} ---")
            print(f"PMID: {doc.pmid}")
            print(f"Title: {doc.title}")
            print(f"Source: {doc.source.value}")
            print(f"Score: {doc.similarity_score:.3f}")
            print(f"Abstract: {doc.abstract[:200]}..." if len(doc.abstract) > 200 else f"Abstract: {doc.abstract}")
    else:
        print(f"\nFound {len(results)} results")
        for i, doc in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            if isinstance(doc, list):
                print(f"Got a list: {doc}")
            else:
                print(f"PMID: {doc.pmid}")
                print(f"Title: {doc.title}")
                print(f"Source: {doc.source.value}")
                print(f"Score: {doc.similarity_score:.3f}")
                print(f"Abstract: {doc.abstract[:200]}..." if len(doc.abstract) > 200 else f"Abstract: {doc.abstract}")

if __name__ == "__main__":
    test_pubmed_search()