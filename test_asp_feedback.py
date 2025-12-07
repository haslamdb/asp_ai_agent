#!/usr/bin/env python3
"""Test the updated ASP feedback endpoint with PubMed integration"""

import requests
import json

def test_asp_feedback():
    # Create a proper session to maintain cookies
    session = requests.Session()
    
    # First, establish a session by getting the CSRF token
    # This will set the session cookie
    token_url = "http://localhost:8080/api/csrf-token"
    token_response = session.get(token_url)
    
    if token_response.status_code != 200:
        print(f"Failed to get CSRF token: {token_response.status_code}")
        return
    
    csrf_token = token_response.json().get('csrf_token')
    print(f"Got CSRF token: {csrf_token[:20]}...")
    print(f"Session cookies: {session.cookies.get_dict()}")
    
    # Test the ASP feedback endpoint
    url = "http://localhost:8080/api/asp-feedback"
    
    test_queries = [
        "What are the IDSA guidelines for treatment of osteomyelitis in children?",
        "PMID:34350458",
        "Treatment of osteomyelitis in children"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing query: {query}")
        print('='*60)
        
        payload = {
            "input": query,
            "module": "general",
            "model": "qwen2.5:72b"  # Use the correct model name format
        }
        
        # Use the CSRF token in headers
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if PubMed info is included
            if 'pubmed_info' in data:
                print(f"✓ PubMed info found!")
                pubmed_info = data['pubmed_info']
                print(f"  - Sources used: {pubmed_info.get('sources_used', [])}")
                print(f"  - PubMed results: {pubmed_info.get('pubmed_results', 0)}")
                print(f"  - Local results: {pubmed_info.get('local_results', 0)}")
            else:
                print("✗ No PubMed info in response")
            
            # Check the actual response
            if 'response' in data:
                response_text = data['response'][:500]  # First 500 chars
                
                # Check if PMIDs are mentioned in the response
                if 'PMID' in response_text:
                    print("✓ PMIDs found in response text")
                else:
                    print("✗ No PMIDs mentioned in response")
                
                print(f"\nResponse preview: {response_text}...")
            
            # Check citations
            if 'citations' in data and data['citations']:
                print(f"\n✓ Citations found: {len(data['citations'])} citations")
            else:
                print("\n✗ No citations in response")
                
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:500])

if __name__ == "__main__":
    test_asp_feedback()