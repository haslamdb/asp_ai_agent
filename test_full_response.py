#!/usr/bin/env python3
"""Test to see full PubMed response"""

import requests
import json

BASE_URL = "http://localhost:8080"

# Get CSRF token
session = requests.Session()
csrf_resp = session.get(f"{BASE_URL}/api/csrf-token")
csrf_token = csrf_resp.json().get('csrf_token')

# Prepare request
headers = {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrf_token
}

payload = {
    "input": "What studies support short IV therapy for pediatric osteomyelitis?",
    "module_id": "asp_module",
    "scenario_id": "general_query",
    "level": "intermediate",
    "rag_type": "pubmed",
    "mode": "qa",
    "conversation_history": []
}

# Send request
response = session.post(
    f"{BASE_URL}/api/feedback/enhanced",
    headers=headers,
    json=payload,
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    print("="*70)
    print("FULL RESPONSE:")
    print("="*70)
    print(result.get('response', 'No response'))
    print("\n" + "="*70)
    print(f"Sources found: {len(result.get('sources', []))}")
    for source in result.get('sources', []):
        print(f"  - PMID: {source.get('pmid')} - {source.get('title')}")
else:
    print(f"Error: {response.status_code}")