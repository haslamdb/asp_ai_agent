#!/usr/bin/env python3
"""
Unified AI Server for ASP AI Agent
Integrates:
- Ollama (local models)
- Citation Assistant with PubMedBERT
- Google Gemini API
- Anthropic Claude API
"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from functools import lru_cache
import hashlib
import asyncio
import concurrent.futures
import threading
import time

app = Flask(__name__)
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*', 'file://*', 'https://haslamdb.github.io'])

# Configuration
OLLAMA_API = "http://localhost:11434"
CITATION_API = "http://localhost:9998"  # Secure citation assistant
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Claude API endpoint
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
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
    
    # Check API keys
    services['gemini'] = {
        'status': 'configured' if GEMINI_API_KEY else 'not_configured'
    }
    services['claude'] = {
        'status': 'configured' if ANTHROPIC_API_KEY else 'not_configured'
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
                    'name': f"Ollama: {model['name']}",
                    'provider': 'ollama',
                    'type': 'llm',
                    'local': True,
                    'description': f"Local model - {model.get('details', {}).get('parameter_size', 'Unknown size')}"
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
            'description': 'RAG with PubMedBERT embeddings for medical literature'
        })
    
    # Add Claude models if configured
    if ANTHROPIC_API_KEY:
        models.extend([
            {
                'id': 'claude:3-opus',
                'name': 'Claude 4.1 Opus',
                'provider': 'anthropic',
                'type': 'llm',
                'local': False,
                'description': 'Most capable Claude model for complex tasks'
            },
            {
                'id': 'claude:3-sonnet',
                'name': 'Claude 4.5 Sonnet',
                'provider': 'anthropic',
                'type': 'llm',
                'local': False,
                'description': 'Balanced performance and cost'
            },
            {
                'id': 'claude:3-haiku',
                'name': 'Claude 4.5 Haiku',
                'provider': 'anthropic',
                'type': 'llm',
                'local': False,
                'description': 'Fast and efficient for simple tasks'
            }
        ])
    
    # Add Gemini if configured
    if GEMINI_API_KEY:
        models.extend([
            {
                'id': 'gemini:2.5-flash',
                'name': 'Gemini 2.5 Flash',
                'provider': 'google',
                'type': 'llm',
                'local': False,
                'description': 'Latest Gemini model with multimodal capabilities'
            },
            {
                'id': 'gemini:2.5-pro',
                'name': 'Gemini 2.5 Pro',
                'provider': 'google',
                'type': 'llm',
                'local': False,
                'description': 'Advanced reasoning with large context window'
            }
        ])
    
    return jsonify({'models': models, 'count': len(models)})

@app.route('/claude', methods=['POST'])
def claude_endpoint():
    """Direct Claude endpoint for frontend compatibility"""
    data = request.json
    system_prompt = data.get('system', '')
    messages = data.get('messages', [])
    max_tokens = data.get('max_tokens', 4000)
    
    if not messages:
        return jsonify({'error': 'Messages are required'}), 400
    
    try:
        # Use Claude 3.5 Sonnet as default
        result = claude_chat('3-sonnet', messages, system_prompt)
        
        if result[1] == 200:
            response_data = result[0].get_json()
            # Transform to match expected frontend format
            return jsonify({
                'text': response_data.get('response', ''),
                'model': response_data.get('model', ''),
                'usage': response_data.get('usage', {})
            })
        else:
            return result
    except Exception as e:
        return jsonify({'error': f'Claude endpoint error: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Unified chat endpoint for all models"""
    data = request.json
    model_id = data.get('model', 'ollama:gemma2:27b')
    messages = data.get('messages', [])
    query = data.get('query', '')
    system_prompt = data.get('system', '')
    temperature = data.get('temperature', 0.7)
    
    # Extract the last user message if messages are provided
    if messages and not query:
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                query = msg.get('content', '')
                break
    
    provider, model_name = model_id.split(':', 1)
    
    try:
        if provider == 'ollama':
            return ollama_chat(model_name, messages or [{'role': 'user', 'content': query}], system_prompt)
        elif provider == 'pubmedbert':
            return citation_search(query)
        elif provider == 'claude':
            return claude_chat(model_name, messages or [{'role': 'user', 'content': query}], system_prompt, temperature)
        elif provider == 'gemini':
            return gemini_chat(model_name, messages or [{'role': 'user', 'content': query}], system_prompt)
        else:
            return jsonify({'error': f'Unknown provider: {provider}'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'model': model_id}), 500

def ollama_chat(model: str, messages: List[Dict], system_prompt: str = '') -> tuple:
    """Handle Ollama model chat"""
    try:
        # Add system prompt if provided
        if system_prompt and (not messages or messages[0].get('role') != 'system'):
            messages.insert(0, {'role': 'system', 'content': system_prompt})
        
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
                'provider': 'ollama',
                'local': True
            })
        else:
            return jsonify({'error': f'Ollama error: {response.text}'}), response.status_code
    except requests.Timeout:
        return jsonify({'error': 'Request timeout - model may be loading'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def claude_chat(model: str, messages: List[Dict], system_prompt: str = '', temperature: float = 0.7) -> tuple:
    """Handle Claude API chat"""
    if not ANTHROPIC_API_KEY:
        return jsonify({'error': 'Claude API key not configured'}), 400
    
    try:
        # Map model names to Claude model IDs
        model_map = {
            '3-opus': 'claude-opus-4-1',  # Claude 4.1 Opus
            '4.1-opus': 'claude-opus-4-1',
            '3-sonnet': 'claude-sonnet-4-5',
            '3-haiku': 'claude-haiku-4-5',
            '3.5-sonnet': 'claude-sonnet-4-5',
            '4.5-sonnet': 'claude-sonnet-4-5',
            '4.5-haiku': 'claude-haiku-4-5'
        }
        
        claude_model = model_map.get(model, 'claude-sonnet-4-5')
        
        # Prepare messages for Claude API
        claude_messages = []
        for msg in messages:
            if msg['role'] != 'system':  # Claude handles system prompts differently
                claude_messages.append({
                    'role': 'user' if msg['role'] == 'user' else 'assistant',
                    'content': msg['content']
                })
        
        # Prepare the request
        request_data = {
            'model': claude_model,
            'messages': claude_messages,
            'max_tokens': 4096,
            'temperature': temperature
        }
        
        # Add system prompt if provided
        if system_prompt or (messages and messages[0].get('role') == 'system'):
            request_data['system'] = system_prompt or messages[0]['content']
        
        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'response': result['content'][0]['text'],
                'model': f'claude:{model}',
                'provider': 'anthropic',
                'local': False,
                'usage': result.get('usage', {})
            })
        else:
            error_detail = response.json() if response.text else {'error': response.text}
            return jsonify({'error': f'Claude API error: {error_detail}'}), response.status_code
    except Exception as e:
        return jsonify({'error': f'Claude error: {str(e)}'}), 500

def citation_search(query: str) -> tuple:
    """Handle Citation Assistant search with PubMedBERT"""
    try:
        # Search for relevant papers
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
            citations = []
            for i, paper in enumerate(papers, 1):
                response += f"{i}. **{paper.get('title', 'Unknown Title')}**\n"
                response += f"   Authors: {paper.get('authors', 'Unknown Authors')}\n"
                response += f"   Year: {paper.get('year', 'Unknown')}\n"
                response += f"   Relevance: {paper.get('score', 0):.2f}\n"
                if paper.get('context'):
                    response += f"   Context: {paper['context'][:200]}...\n"
                response += "\n"
                
                citations.append({
                    'title': paper.get('title', ''),
                    'authors': paper.get('authors', ''),
                    'year': paper.get('year', ''),
                    'score': paper.get('score', 0)
                })
        else:
            response = "No relevant citations found in the PubMedBERT database."
            citations = []
        
        return jsonify({
            'response': response,
            'model': 'pubmedbert:citation',
            'provider': 'citation_assistant',
            'local': True,
            'citations': citations
        })
    except Exception as e:
        return jsonify({'error': f'Citation assistant error: {str(e)}'}), 500

def gemini_chat(model: str, messages: List[Dict], system_prompt: str = '') -> tuple:
    """Handle Gemini API chat"""
    if not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API key not configured'}), 400
    
    try:
        # Map model names
        model_map = {
            '2.0-flash': 'gemini-2.5-flash',
            '2.5-flash': 'gemini-2.5-flash',
            '1.5-pro': 'gemini-2.5-pro',
            '2.5-pro': 'gemini-2.5-pro'
        }
        
        gemini_model = model_map.get(model, 'gemini-2.5-flash')
        
        # Convert messages to Gemini format
        contents = []
        
        # Add system instruction if provided
        system_instruction = None
        if system_prompt or (messages and messages[0].get('role') == 'system'):
            system_instruction = {'parts': [{'text': system_prompt or messages[0]['content']}]}
            if messages and messages[0].get('role') == 'system':
                messages = messages[1:]  # Remove system message from list
        
        for msg in messages:
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append({
                'role': role,
                'parts': [{'text': msg['content']}]
            })
        
        request_data = {'contents': contents}
        if system_instruction:
            request_data['systemInstruction'] = system_instruction
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={GEMINI_API_KEY}",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract sources if available
            sources = []
            grounding = result.get('candidates', [{}])[0].get('groundingMetadata')
            if grounding and grounding.get('groundingAttributions'):
                for attr in grounding['groundingAttributions']:
                    if attr.get('web'):
                        sources.append({
                            'title': attr['web'].get('title', ''),
                            'uri': attr['web'].get('uri', '')
                        })
            
            return jsonify({
                'response': text,
                'model': f'gemini:{model}',
                'provider': 'google',
                'local': False,
                'sources': sources
            })
        else:
            return jsonify({'error': f'Gemini error: {response.text}'}), response.status_code
    except Exception as e:
        return jsonify({'error': f'Gemini error: {str(e)}'}), 500

@app.route('/api/asp-feedback', methods=['POST'])
def asp_feedback():
    """
    Special endpoint for ASP-specific feedback using the best available model
    """
    data = request.json
    module = data.get('module', 'general')
    user_input = data.get('input', '')
    preferred_model = data.get('model')
    
    # Build specialized prompts based on module
    if module == 'business_case':
        system_prompt = """You are a senior hospital administrator (CFO/CMO) reviewing an ASP business case.
        Focus on ROI calculations, stakeholder engagement strategies, and measurable outcomes.
        Be skeptical but constructive. Ground feedback in real-world ASP literature."""
    elif module == 'prescriber_psychology':
        system_prompt = """You are an expert in behavioral science and prescriber psychology for ASP.
        Analyze cognitive biases (commission bias, omission bias, availability heuristic).
        Suggest evidence-based communication strategies like academic detailing and motivational interviewing."""
    else:
        system_prompt = """You are an ASP expert providing feedback on antimicrobial stewardship.
        Focus on evidence-based practices and implementation strategies."""
    
    # Try to enhance with citations
    citations = []
    if check_services().get('citation_assistant', {}).get('status') == 'online':
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
    
    # Build enhanced input
    enhanced_input = user_input
    if citations:
        enhanced_input += "\n\nRelevant literature to consider:\n"
        for cite in citations:
            enhanced_input += f"- {cite.get('title', '')} ({cite.get('year', '')}): {cite.get('context', '')[:100]}...\n"
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': enhanced_input}
    ]
    
    # Try preferred model first, then fall back to best available
    if preferred_model:
        result = chat_with_model(preferred_model, messages)
        if result[1] == 200:
            response_data = result[0].get_json()
            response_data['citations'] = citations
            return jsonify(response_data)
    
    # Try models in order of preference for medical tasks
    model_preference = [
        'claude:3-sonnet',  # Best for medical reasoning
        'gemini:2.5-flash',  # Good with search integration
        'ollama:gemma2:27b',  # Local fallback
    ]
    
    for model_id in model_preference:
        provider = model_id.split(':')[0]
        if provider == 'claude' and not ANTHROPIC_API_KEY:
            continue
        if provider == 'gemini' and not GEMINI_API_KEY:
            continue
        if provider == 'ollama' and check_services().get('ollama', {}).get('status') != 'online':
            continue
        
        result = chat_with_model(model_id, messages)
        if result[1] == 200:
            response_data = result[0].get_json()
            response_data['citations'] = citations
            return jsonify(response_data)
    
    return jsonify({'error': 'No AI models available', 'citations': citations}), 503

@lru_cache(maxsize=100)
def get_cached_citations(query_hash: str) -> Optional[List[Dict]]:
    """Cache citation searches for common queries"""
    try:
        if check_services().get('citation_assistant', {}).get('status') == 'online':
            search_resp = requests.post(
                f"{CITATION_API}/api/search",
                json={'query': query_hash, 'max_results': 5},
                timeout=15
            )
            if search_resp.status_code == 200:
                return search_resp.json().get('results', [])
    except:
        pass
    return []

def calculate_relevance_score(citations: List[Dict]) -> float:
    """Calculate average relevance score for citations"""
    if not citations:
        return 0.0
    scores = []
    for cite in citations:
        # Estimate relevance based on available metadata
        score = 0.5  # base score
        if cite.get('year', 0) > 2020:
            score += 0.2  # recent publication
        if len(cite.get('context', '')) > 100:
            score += 0.3  # substantial context
        scores.append(score)
    return sum(scores) / len(scores) if scores else 0.0

@app.route('/api/hybrid-asp', methods=['POST'])
def hybrid_asp_agent():
    """
    Hybrid agent for ASP education:
    1. Cloud model interprets user intent
    2. Local model (citation_assistant + Gemma2) generates factual content
    3. Cloud model formats educational response
    """
    data = request.json
    user_query = data.get('query', '')
    cloud_model = data.get('cloud_model', 'claude:4.5-sonnet')
    
    if not user_query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Step 1: Use cloud model to interpret and structure the query
    interpretation_prompt = """You are an ASP education assistant. Analyze this learner's question and:
    1. Identify the core medical/antimicrobial concept being asked about
    2. Extract any specific pathogens, antibiotics, or conditions mentioned
    3. Determine what type of information would be most educational (mechanism, spectrum, resistance patterns, etc.)
    4. Reformulate as a clear, focused query for medical literature search
    
    Output ONLY the reformulated query, nothing else."""
    
    interpretation_messages = [
        {'role': 'system', 'content': interpretation_prompt},
        {'role': 'user', 'content': user_query}
    ]
    
    # Get structured query from cloud model
    cloud_response = chat_with_model(cloud_model, interpretation_messages)
    if cloud_response[1] != 200:
        # Fallback to original query if interpretation fails
        structured_query = user_query
    else:
        structured_query = cloud_response[0].get_json().get('response', user_query)
    
    # Step 2: Get factual content with parallel processing
    start_time = time.time()
    factual_content = ""
    citations = []
    
    # Create hash for caching
    query_hash = hashlib.md5(structured_query.encode()).hexdigest()
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        # Submit citation search task
        if check_services().get('citation_assistant', {}).get('status') == 'online':
            def fetch_citations():
                try:
                    # Try cache first
                    cached = get_cached_citations.cache_info()
                    search_resp = requests.post(
                        f"{CITATION_API}/api/search",
                        json={'query': structured_query, 'max_results': 5},
                        timeout=15
                    )
                    if search_resp.status_code == 200:
                        return search_resp.json().get('results', [])
                except Exception as e:
                    print(f"Citation error: {str(e)}")
                return []
            
            citation_future = executor.submit(fetch_citations)
            futures.append(('citations', citation_future))
        
        # Submit local model generation task
        if check_services().get('ollama', {}).get('status') == 'online':
            def generate_local_content(cit_future):
                try:
                    # Wait for citations to build context
                    cits = cit_future.result(timeout=10) if cit_future else []
                    if cits:
                        citation_context = "\n".join([
                            f"- {cite.get('title', '')} ({cite.get('year', '')}): {cite.get('context', '')}"
                            for cite in cits[:3]
                        ])
                        
                        local_prompt = f"""Based on the following peer-reviewed literature, provide a factual, evidence-based response about {structured_query}:
                        
                        {citation_context}
                        
                        Focus on: mechanisms of action, spectrum of activity, resistance patterns, clinical pearls, and stewardship considerations.
                        Be precise and cite specific findings from the literature provided."""
                        
                        local_messages = [{'role': 'user', 'content': local_prompt}]
                        local_response = ollama_chat('gemma2:27b', local_messages)
                        if local_response[1] == 200:
                            return local_response[0].get_json().get('response', '')
                except Exception as e:
                    print(f"Local generation error: {str(e)}")
                return ""
            
            local_future = executor.submit(generate_local_content, 
                                         citation_future if 'citation_future' in locals() else None)
            futures.append(('local', local_future))
        
        # Collect results
        for name, future in futures:
            try:
                if name == 'citations':
                    citations = future.result(timeout=15)
                elif name == 'local':
                    factual_content = future.result(timeout=30)
            except Exception as e:
                print(f"Error collecting {name}: {str(e)}")
    
    processing_time = time.time() - start_time
    
    # Step 3: Use cloud model to format educational response
    formatting_prompt = """You are an expert medical educator specializing in antimicrobial stewardship.
    Format the following factual content into an educational response that:
    1. Starts with key learning points
    2. Explains concepts progressively (basic to advanced)
    3. Includes clinical pearls and practical tips
    4. Highlights common misconceptions or pitfalls
    5. Ends with a brief summary and self-check questions
    
    Make it engaging and appropriate for ID fellows."""
    
    final_content = f"Original question: {user_query}\n\n"
    if factual_content:
        final_content += f"Evidence-based content:\n{factual_content}\n\n"
    if citations:
        final_content += "Key references:\n"
        for cite in citations[:3]:
            final_content += f"- {cite.get('title', '')} ({cite.get('year', '')})\n"
    
    formatting_messages = [
        {'role': 'system', 'content': formatting_prompt},
        {'role': 'user', 'content': final_content}
    ]
    
    # Get formatted response from cloud model
    final_response = chat_with_model(cloud_model, formatting_messages)
    if final_response[1] != 200:
        # Return raw content if formatting fails
        return jsonify({
            'response': factual_content or "Unable to generate response",
            'citations': citations,
            'model': 'hybrid',
            'error': 'Formatting failed'
        }), 207
    
    response_data = final_response[0].get_json()
    response_data['citations'] = citations
    response_data['model'] = f'hybrid:{cloud_model}+gemma2'
    response_data['structured_query'] = structured_query
    
    # Add quality metrics
    response_data['quality_metrics'] = {
        'num_citations': len(citations),
        'avg_relevance': calculate_relevance_score(citations),
        'used_local_model': bool(factual_content),
        'processing_time_seconds': round(processing_time, 2),
        'cache_info': {
            'hits': get_cached_citations.cache_info().hits if hasattr(get_cached_citations, 'cache_info') else 0,
            'misses': get_cached_citations.cache_info().misses if hasattr(get_cached_citations, 'cache_info') else 0,
        },
        'services_used': {
            'cloud_interpretation': True,
            'citation_assistant': len(citations) > 0,
            'local_gemma2': bool(factual_content),
            'cloud_formatting': final_response[1] == 200
        }
    }
    
    return jsonify(response_data)

@app.route('/api/hybrid-asp-stream', methods=['POST'])
def hybrid_asp_stream():
    """
    Streaming version of the hybrid ASP agent
    Returns Server-Sent Events (SSE) with progress updates
    """
    data = request.json
    user_query = data.get('query', '')
    cloud_model = data.get('cloud_model', 'claude:4.5-sonnet')
    
    def generate():
        # Stage 1: Interpreting query
        yield f"data: {json.dumps({'stage': 1, 'status': 'interpreting', 'message': 'Analyzing your question...'})}\n\n"
        
        interpretation_prompt = """You are an ASP education assistant. Analyze this learner's question and:
        1. Identify the core medical/antimicrobial concept being asked about
        2. Extract any specific pathogens, antibiotics, or conditions mentioned
        3. Determine what type of information would be most educational
        4. Reformulate as a clear, focused query for medical literature search
        
        Output ONLY the reformulated query, nothing else."""
        
        interpretation_messages = [
            {'role': 'system', 'content': interpretation_prompt},
            {'role': 'user', 'content': user_query}
        ]
        
        cloud_response = chat_with_model(cloud_model, interpretation_messages)
        structured_query = user_query
        if cloud_response[1] == 200:
            structured_query = cloud_response[0].get_json().get('response', user_query)
            yield f"data: {json.dumps({'stage': 1, 'status': 'complete', 'structured_query': structured_query})}\n\n"
        
        # Stage 2: Fetching citations and generating local content
        yield f"data: {json.dumps({'stage': 2, 'status': 'searching', 'message': 'Searching medical literature...'})}\n\n"
        
        citations = []
        factual_content = ""
        
        # Parallel processing with status updates
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            
            if check_services().get('citation_assistant', {}).get('status') == 'online':
                def fetch_citations():
                    try:
                        search_resp = requests.post(
                            f"{CITATION_API}/api/search",
                            json={'query': structured_query, 'max_results': 5},
                            timeout=15
                        )
                        if search_resp.status_code == 200:
                            return search_resp.json().get('results', [])
                    except Exception as e:
                        print(f"Citation error: {str(e)}")
                    return []
                
                citation_future = executor.submit(fetch_citations)
                futures.append(('citations', citation_future))
            
            # Wait and report results
            for name, future in futures:
                try:
                    if name == 'citations':
                        citations = future.result(timeout=15)
                        if citations:
                            yield f"data: {json.dumps({'stage': 2, 'status': 'found_citations', 'count': len(citations)})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'stage': 2, 'status': 'error', 'message': str(e)})}\n\n"
        
        # Stage 3: Generating local content
        if citations and check_services().get('ollama', {}).get('status') == 'online':
            yield f"data: {json.dumps({'stage': 3, 'status': 'generating', 'message': 'Generating evidence-based content...'})}\n\n"
            
            citation_context = "\n".join([
                f"- {cite.get('title', '')} ({cite.get('year', '')}): {cite.get('context', '')}"
                for cite in citations[:3]
            ])
            
            local_prompt = f"""Based on the following peer-reviewed literature, provide a factual response about {structured_query}:
            
            {citation_context}
            
            Focus on mechanisms, spectrum, resistance, and clinical pearls."""
            
            local_messages = [{'role': 'user', 'content': local_prompt}]
            local_response = ollama_chat('gemma2:27b', local_messages)
            if local_response[1] == 200:
                factual_content = local_response[0].get_json().get('response', '')
                yield f"data: {json.dumps({'stage': 3, 'status': 'complete', 'has_content': bool(factual_content)})}\n\n"
        
        # Stage 4: Formatting response
        yield f"data: {json.dumps({'stage': 4, 'status': 'formatting', 'message': 'Creating educational response...'})}\n\n"
        
        formatting_prompt = """Format this into an educational response with key points, progressive explanation, and clinical pearls."""
        
        final_content = f"Question: {user_query}\n\n"
        if factual_content:
            final_content += f"Evidence: {factual_content}\n\n"
        if citations:
            final_content += "References:\n"
            for cite in citations[:3]:
                final_content += f"- {cite.get('title', '')} ({cite.get('year', '')})\n"
        
        formatting_messages = [
            {'role': 'system', 'content': formatting_prompt},
            {'role': 'user', 'content': final_content}
        ]
        
        final_response = chat_with_model(cloud_model, formatting_messages)
        if final_response[1] == 200:
            response_text = final_response[0].get_json().get('response', '')
            
            # Send final response with metrics
            quality_metrics = {
                'num_citations': len(citations),
                'avg_relevance': calculate_relevance_score(citations),
                'used_local_model': bool(factual_content),
                'services_used': {
                    'citation_assistant': len(citations) > 0,
                    'local_gemma2': bool(factual_content),
                }
            }
            
            yield f"data: {json.dumps({'stage': 4, 'status': 'complete', 'response': response_text, 'citations': citations, 'metrics': quality_metrics})}\n\n"
        
        yield f"data: {json.dumps({'stage': 5, 'status': 'done'})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def chat_with_model(model_id: str, messages: List[Dict]) -> tuple:
    """Helper to chat with a specific model"""
    provider, model_name = model_id.split(':', 1)
    
    if provider == 'ollama':
        return ollama_chat(model_name, messages)
    elif provider == 'claude':
        return claude_chat(model_name, messages)
    elif provider == 'gemini':
        return gemini_chat(model_name, messages)
    elif provider == 'pubmedbert':
        query = messages[-1]['content'] if messages else ''
        return citation_search(query)
    
    return jsonify({'error': f'Unknown model: {model_id}'}), 400

if __name__ == '__main__':
    print("=" * 60)
    print("Unified AI Server for ASP AI Agent")
    print("=" * 60)
    
    print("\nChecking services...")
    services = check_services()
    
    print("\nAvailable Services:")
    print(f"  Ollama: {services.get('ollama', {}).get('status', 'offline')}")
    if services.get('ollama', {}).get('models'):
        for model in services['ollama']['models']:
            print(f"    - {model}")
    
    print(f"  Citation Assistant: {services.get('citation_assistant', {}).get('status', 'offline')}")
    print(f"  Google Gemini: {services.get('gemini', {}).get('status', 'not_configured')}")
    print(f"  Anthropic Claude: {services.get('claude', {}).get('status', 'not_configured')}")
    
    print("\n" + "=" * 60)
    print("Server running on http://localhost:5000")
    print("=" * 60)
    
    print("\nEndpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /api/models      - List available models")
    print("  POST /api/chat        - Chat with any model")
    print("  POST /api/asp-feedback - ASP-specific feedback")
    
    print("\nTo use Claude or Gemini, set environment variables:")
    print("  export ANTHROPIC_API_KEY='your-key-here'")
    print("  export GEMINI_API_KEY='your-key-here'")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)