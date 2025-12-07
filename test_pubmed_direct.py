#!/usr/bin/env python3
"""Test PubMed search directly"""

from pubmed_rag_tools import PubMedRAGSystem

# Initialize the RAG system
rag = PubMedRAGSystem()

# Test searches
queries = [
    "PMID:34350458",
    "IDSA guidelines osteomyelitis children",
    "treatment pediatric osteomyelitis"
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"Searching for: {query}")
    print('='*60)
    
    # Use force_pubmed=True to ensure we search PubMed
    documents, metadata = rag.retrieve(
        query=query,
        max_results=3,
        force_pubmed=True
    )
    
    print(f"Metadata: {metadata}")
    print(f"Found {len(documents)} documents")
    
    for doc in documents[:2]:
        print(f"\nPMID: {doc.pmid}")
        print(f"Title: {doc.title[:100]}...")
        print(f"Source: {doc.source.value}")