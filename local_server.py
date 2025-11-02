#!/usr/bin/env python3
"""
Local AI Server for ASP AI Agent
Integrates Ollama models and Citation Assistant with PubMedBERT
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from typing import Dict, Any, List

app = Flask(__name__)
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*', 'file://*'])

# Configuration
OLLAMA_API = "http://localhost:11434"
CITATION_API = "http://localhost:9998"  # Secure citation assistant
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': check_services()
    })

def check_services():
    """Check which services are available"""
    services = {}
    
    # Check Ollama
    try:
        resp = requests.get(f"{OLLAMA_API}/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            services['ollama'] = {
                'status': 'online',
                'models': [m['name'] for m in models]
            }
        else:
            services['ollama'] = {'status': 'offline'}
    except:
        services['ollama'] = {'status': 'offline'}
    
    # Check Citation Assistant
    try:
        resp = requests.get(f"{CITATION_API}/api/stats", timeout=2)
        if resp.status_code == 200:
            services['citation_assistant'] = {
                'status': 'online',
                'stats': resp.json()
            }
        else:
            services['citation_assistant'] = {'status': 'offline'}
    except:
        services['citation_assistant'] = {'status': 'offline'}
    
    # Check if Gemini API key is configured
    services['gemini'] = {
        'status': 'configured' if GEMINI_API_KEY else 'not_configured'
    }
    
    return services

@app.route('/api/models', methods=['GET'])
def list_models():
    """List all available models"""
    models = []
    
    # Add Ollama models
    try:
        resp = requests.get(f"{OLLAMA_API}/api/tags", timeout=2)
        if resp.status_code == 200:
            ollama_models = resp.json().get('models', [])
            for model in ollama_models:
                models.append({
                    'id': f"ollama:{model['name']}",
                    'name': model['name'],
                    'provider': 'ollama',
                    'type': 'llm',
                    'local': True
                })
    except:
        pass
    
    # Add Citation Assistant
    services = check_services()
    if services.get('citation_assistant', {}).get('status') == 'online':
        models.append({
            'id': 'pubmedbert:citation',
            'name': 'PubMedBERT Citation Assistant',
            'provider': 'citation_assistant',
            'type': 'rag',
            'local': True,
            'description': 'Retrieval-augmented generation using PubMedBERT embeddings'
        })
    
    # Add Gemini if configured
    if GEMINI_API_KEY:
        models.append({
            'id': 'gemini:2.0-flash',
            'name': 'Gemini 2.0 Flash',
            'provider': 'google',
            'type': 'llm',
            'local': False
        })
    
    return jsonify({'models': models})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Unified chat endpoint for all models"""
    data = request.json
    model_id = data.get('model', 'ollama:gemma2:27b')
    messages = data.get('messages', [])
    query = data.get('query', '')
    
    # Extract the last user message if messages are provided
    if messages and not query:
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                query = msg.get('content', '')
                break
    
    provider, model_name = model_id.split(':', 1)
    
    try:
        if provider == 'ollama':
            return ollama_chat(model_name, messages or [{'role': 'user', 'content': query}])
        elif provider == 'pubmedbert':
            return citation_search(query)
        elif provider == 'gemini':
            return gemini_chat(messages or [{'role': 'user', 'content': query}])
        else:
            return jsonify({'error': f'Unknown provider: {provider}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def ollama_chat(model: str, messages: List[Dict]) -> tuple:
    """Handle Ollama model chat"""
    try:
        response = requests.post(
            f"{OLLAMA_API}/api/chat",
            json={
                'model': model,
                'messages': messages,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'response': result.get('message', {}).get('content', ''),
                'model': f'ollama:{model}',
                'provider': 'ollama'
            })
        else:
            return jsonify({'error': f'Ollama error: {response.text}'}), response.status_code
    except requests.Timeout:
        return jsonify({'error': 'Request timeout - model may be loading'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def citation_search(query: str) -> tuple:
    """Handle Citation Assistant search with PubMedBERT"""
    try:
        # First, search for relevant papers
        search_resp = requests.post(
            f"{CITATION_API}/api/search",
            json={
                'query': query,
                'max_results': 5
            },
            timeout=30
        )
        
        if search_resp.status_code != 200:
            return jsonify({'error': 'Citation search failed'}), 500
        
        papers = search_resp.json().get('results', [])
        
        # Format response with citations
        if papers:
            response = f"Based on PubMedBERT semantic search, here are relevant citations:\n\n"
            for i, paper in enumerate(papers, 1):
                response += f"{i}. **{paper.get('title', 'Unknown Title')}**\n"
                response += f"   Authors: {paper.get('authors', 'Unknown Authors')}\n"
                response += f"   Year: {paper.get('year', 'Unknown')}\n"
                response += f"   Relevance: {paper.get('score', 0):.2f}\n"
                if paper.get('context'):
                    response += f"   Context: {paper['context'][:200]}...\n"
                response += "\n"
            
            # Try to get a summary if available
            summary_resp = requests.post(
                f"{CITATION_API}/api/summarize",
                json={'query': query},
                timeout=30
            )
            if summary_resp.status_code == 200:
                summary = summary_resp.json().get('summary', '')
                if summary:
                    response += f"\n**Summary:** {summary}"
        else:
            response = "No relevant citations found in the PubMedBERT database."
        
        return jsonify({
            'response': response,
            'model': 'pubmedbert:citation',
            'provider': 'citation_assistant',
            'papers': papers
        })
    except Exception as e:
        return jsonify({'error': f'Citation assistant error: {str(e)}'}), 500

def gemini_chat(messages: List[Dict]) -> tuple:
    """Handle Gemini API chat"""
    if not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API key not configured'}), 400
    
    try:
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append({
                'role': role,
                'parts': [{'text': msg['content']}]
            })
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
            json={'contents': contents},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({
                'response': text,
                'model': 'gemini:2.0-flash',
                'provider': 'google'
            })
        else:
            return jsonify({'error': f'Gemini error: {response.text}'}), response.status_code
    except Exception as e:
        return jsonify({'error': f'Gemini error: {str(e)}'}), 500

@app.route('/api/asp-feedback', methods=['POST'])
def asp_feedback():
    """
    Special endpoint for ASP-specific feedback using the best available model
    with medical/clinical knowledge
    """
    data = request.json
    module = data.get('module', 'general')
    user_input = data.get('input', '')
    
    # Build a specialized prompt based on the module
    if module == 'business_case':
        system_prompt = """You are a senior hospital administrator reviewing an ASP business case.
        Focus on ROI, stakeholder engagement, and measurable outcomes."""
    elif module == 'prescriber_psychology':
        system_prompt = """You are an expert in behavioral science and prescriber psychology.
        Analyze cognitive biases and suggest evidence-based communication strategies."""
    else:
        system_prompt = """You are an ASP expert providing feedback on antimicrobial stewardship."""
    
    # First try to get relevant citations from PubMedBERT
    citations = []
    try:
        search_resp = requests.post(
            f"{CITATION_API}/api/search",
            json={'query': user_input[:500], 'max_results': 3},
            timeout=10
        )
        if search_resp.status_code == 200:
            citations = search_resp.json().get('results', [])
    except:
        pass
    
    # Build enhanced prompt with citations
    enhanced_input = user_input
    if citations:
        enhanced_input += "\n\nRelevant literature:\n"
        for cite in citations:
            enhanced_input += f"- {cite.get('title', '')} ({cite.get('year', '')})\n"
    
    # Use the best available LLM
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': enhanced_input}
    ]
    
    # Try Ollama first (local), then Gemini (if configured)
    services = check_services()
    
    if services.get('ollama', {}).get('status') == 'online':
        result = ollama_chat('gemma2:27b', messages)
        if result[1] == 200:
            response_data = result[0].get_json()
            response_data['citations'] = citations
            return jsonify(response_data)
    
    if GEMINI_API_KEY:
        result = gemini_chat(messages)
        if result[1] == 200:
            response_data = result[0].get_json()
            response_data['citations'] = citations
            return jsonify(response_data)
    
    return jsonify({'error': 'No AI models available'}), 503

if __name__ == '__main__':
    print("Starting Local AI Server...")
    print(f"Checking services...")
    services = check_services()
    print(f"Available services: {json.dumps(services, indent=2)}")
    
    print("\nServer running on http://localhost:5000")
    print("Endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/models - List available models")
    print("  POST /api/chat - Chat with any model")
    print("  POST /api/asp-feedback - ASP-specific feedback")
    
    app.run(host='0.0.0.0', port=5000, debug=True)