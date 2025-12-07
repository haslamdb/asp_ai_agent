
#!/usr/bin/env python3
"""Test enhanced feedback endpoint with PubMed"""

import requests
import json

def test_enhanced_pubmed():
    session = requests.Session()
    
    # Get CSRF token
    token_response = session.get("http://localhost:8080/api/csrf-token")
    csrf_token = token_response.json().get('csrf_token')
    print(f"Got CSRF token: {csrf_token[:20]}...")
    
    # Test query
    query = "PMID:34350458"
    
    # Test with different rag_types
    for rag_type in ['pubmed', 'both_pubmed']:
        print(f"\n{'='*60}")
        print(f"Testing with rag_type: {rag_type}")
        print('='*60)
        
        payload = {
            "input": query,
            "module_id": "general",
            "scenario_id": "general",
            "level": "intermediate",
            "rag_type": rag_type,
            "mode": "qa"
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        response = session.post(
            "http://localhost:8080/api/feedback/enhanced",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print the full response to see what we're getting
            print(f"Full response keys: {list(data.keys())}")
            
            # Check the response field
            if 'response' in data:
                response_text = data['response'][:500]
                print(f"Response preview: {response_text}...")
                if '34350458' in str(data['response']) or 'IDSA' in str(data['response']):
                    print("✓ Found PMID/IDSA mention in response!")
                else:
                    print("✗ No PMID 34350458 or IDSA mention in response")
            
            # Check for feedback
            if 'feedback' in data:
                feedback = data['feedback'][:500]
                
                # Check if PMID is mentioned
                if '34350458' in feedback or 'IDSA' in feedback or 'guideline' in feedback.lower():
                    print("✓ Found relevant content in feedback!")
                    print(f"Feedback preview: {feedback}...")
                else:
                    print("✗ No relevant content found")
                    print(f"Feedback: {feedback}...")
            
            # Check metadata
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"Metadata: {json.dumps(metadata, indent=2)}")
            
            # Check sources
            if 'sources' in data and data['sources']:
                print(f"✓ Sources found: {len(data['sources'])}")
                for source in data['sources'][:2]:
                    print(f"  - PMID {source.get('pmid')}: {source.get('title')[:80]}...")
            else:
                print("✗ No sources in response")
                
            # Check enhanced_prompt to see if literature was included
            if 'enhanced_prompt' in data:
                prompt = data['enhanced_prompt']
                if 'No literature context available' in prompt:
                    print("✗ ERROR: No literature context in prompt!")
                elif 'PMID' in prompt:
                    print("✓ Literature context included in prompt")
                    # Extract the literature section
                    lit_start = prompt.find('Relevant Medical Literature')
                    if lit_start > 0:
                        lit_section = prompt[lit_start:lit_start+500]
                        print(f"Literature section: {lit_section}...")
        else:
            print(f"Error: {response.text[:500]}")

if __name__ == "__main__":
    test_enhanced_pubmed()