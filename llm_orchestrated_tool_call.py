@app.route('/api/chat/agentic', methods=['POST'])
@limiter.limit("10 per minute")
def agentic_chat():
    """
    Agentic chat where LLM decides when to search literature
    Uses tool calling for Claude/GPT-4
    """
    data = request.json or {}
    query = data.get('query', '')
    model = data.get('model', 'claude:4.5-sonnet')
    max_iterations = data.get('max_iterations', 3)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    system_prompt = """You are an expert antimicrobial stewardship educator with access to literature search tools.

When answering questions:
1. First consider if you need evidence to support your response
2. Use the search_literature tool to find relevant papers
3. If initial results are insufficient, search again with refined queries
4. Always cite PMIDs when making evidence-based claims

Available tools:
- search_literature: Search local database + PubMed for relevant papers
- get_article_details: Get full details/text for a specific PMID"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': query}
    ]
    
    all_literature = []
    
    # Agentic loop
    for iteration in range(max_iterations):
        # Call LLM with tools
        if model.startswith('claude:'):
            response = claude_chat_with_tools(
                model.split(':')[1], 
                messages, 
                PUBMED_RAG_TOOLS
            )
        else:
            # Fallback to non-tool version
            response = chat_with_model(model, messages)
            break
        
        result = response[0].get_json() if hasattr(response[0], 'get_json') else response[0]
        
        # Check if LLM wants to use a tool
        if 'tool_use' in result:
            tool_call = result['tool_use']
            tool_name = tool_call['name']
            tool_input = tool_call['input']
            
            # Execute the tool
            if tool_name == 'search_literature':
                docs, metadata = pubmed_rag.retrieve(**tool_input)
                tool_result = pubmed_rag.format_context_for_llm(docs)
                all_literature.extend(docs)
            elif tool_name == 'get_article_details':
                docs, _ = pubmed_rag.retrieve(
                    query=f"PMID:{tool_input['pmid']}", 
                    max_results=1,
                    fetch_full_text=tool_input.get('include_full_text', True)
                )
                tool_result = docs[0].to_context() if docs else "Article not found"
                all_literature.extend(docs)
            
            # Add tool result to conversation
            messages.append({'role': 'assistant', 'content': '', 'tool_use': tool_call})
            messages.append({'role': 'user', 'content': f'Tool result:\n{tool_result}'})
        else:
            # LLM gave final response
            break
    
    # Get final response
    final_response = result.get('response', result.get('content', ''))
    
    return jsonify({
        'response': final_response,
        'model': model,
        'iterations': iteration + 1,
        'literature': {
            'count': len(all_literature),
            'documents': [
                {'pmid': d.pmid, 'title': d.title, 'source': d.source.value}
                for d in all_literature
            ]
        }
    })


def claude_chat_with_tools(model: str, messages: List[Dict], tools: List[Dict]) -> tuple:
    """Claude chat with tool calling support"""
    if not ANTHROPIC_API_KEY:
        return jsonify({'error': 'Claude API key not configured'}), 400
    
    model_map = {
        '4.5-opus': 'claude-opus-4-5',
        '4.5-sonnet': 'claude-sonnet-4-5',
        '4.5-haiku': 'claude-haiku-4-5'
    }
    claude_model = model_map.get(model, 'claude-sonnet-4-5')
    
    # Separate system prompt
    system_prompt = ""
    claude_messages = []
    for msg in messages:
        if msg['role'] == 'system':
            system_prompt = msg['content']
        else:
            claude_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
    
    request_data = {
        'model': claude_model,
        'messages': claude_messages,
        'max_tokens': 4096,
        'tools': tools
    }
    if system_prompt:
        request_data['system'] = system_prompt
    
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
        
        # Check for tool use
        for block in result.get('content', []):
            if block.get('type') == 'tool_use':
                return jsonify({
                    'tool_use': {
                        'id': block['id'],
                        'name': block['name'],
                        'input': block['input']
                    }
                }), 200
        
        # Regular text response
        text_content = ''.join(
            block['text'] for block in result['content'] 
            if block.get('type') == 'text'
        )
        return jsonify({'response': text_content, 'model': f'claude:{model}'}), 200
    
    return jsonify({'error': f'Claude error: {response.text}'}), response.status_code