#!/usr/bin/env python3
"""
Test script to verify PubMed path selection
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_rag_type(rag_type, query):
    """Test a specific RAG type configuration"""
    print(f"\n{'='*60}")
    print(f"Testing RAG type: {rag_type}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    # Get CSRF token
    session = requests.Session()
    csrf_resp = session.get(f"{BASE_URL}/api/csrf-token")
    
    if csrf_resp.status_code != 200:
        print("Failed to get CSRF token")
        return
    
    csrf_token = csrf_resp.json().get('csrf_token')
    
    # Prepare request
    headers = {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrf_token
    }
    
    payload = {
        "input": query,
        "module_id": "asp_module",
        "scenario_id": "general_query",
        "level": "intermediate",
        "rag_type": rag_type,
        "mode": "qa",
        "conversation_history": []
    }
    
    print(f"Sending request with rag_type: {rag_type}")
    
    # Send request
    response = session.post(
        f"{BASE_URL}/api/feedback/enhanced",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Look for debug messages in the response
        response_text = result.get('response', '')
        
        if '[DEBUG: Using Enhanced Feedback Generator path - NOT PubMed fallback]' in response_text:
            print("✓ CONFIRMED: Using Enhanced Feedback Generator")
        elif '[DEBUG: Using PubMed fallback path' in response_text:
            print("✓ CONFIRMED: Using PubMed fallback path")
            # Extract the debug info
            import re
            debug_match = re.search(r'\[DEBUG: Using PubMed fallback path\. rag_type=(\w+), force_pubmed=(\w+)\]', response_text)
            if debug_match:
                print(f"  - rag_type={debug_match.group(1)}")
                print(f"  - force_pubmed={debug_match.group(2)}")
        else:
            print("⚠️ No debug message found in response")
            print("First 500 chars of response:")
            print(response_text[:500])
        
        # Check metadata
        metadata = result.get('metadata', {})
        print(f"\nMetadata received:")
        print(f"  - use_literature: {metadata.get('use_literature')}")
        print(f"  - use_expert: {metadata.get('use_expert')}")
        print(f"  - force_pubmed: {metadata.get('force_pubmed')}")
        
        # Check sources
        sources = result.get('sources', [])
        if isinstance(sources, list):
            print(f"\nSources found: {len(sources)}")
            for i, source in enumerate(sources[:2], 1):
                print(f"  {i}. PMID: {source.get('pmid', 'N/A')} - {source.get('title', 'No title')[:50]}...")
        else:
            print(f"\nSources type: {type(sources)}, value: {sources}")
    else:
        print(f"Request failed with status {response.status_code}")
        print(f"Error: {response.text[:500]}")
    
    time.sleep(2)  # Rate limiting

def main():
    # Test query about pediatric osteomyelitis
    query = "What studies support short IV therapy for pediatric osteomyelitis?"
    
    # Test different RAG types
    test_cases = [
        ('both', 'Should use Enhanced Feedback Generator'),
        ('pubmed', 'Should use PubMed fallback'),
        ('both_pubmed', 'Should use PubMed fallback'),
        ('literature', 'Should use Enhanced Feedback Generator'),
    ]
    
    for rag_type, expected in test_cases:
        print(f"\nExpected behavior: {expected}")
        test_rag_type(rag_type, query)

if __name__ == "__main__":
    main()