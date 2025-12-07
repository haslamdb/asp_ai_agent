def ollama_chat_with_tools(model: str, messages: List[Dict], 
                           tools: List[Dict] = None) -> tuple:
    payload = {
        'model': model,
        'messages': messages,
        'stream': False
    }
    if tools:
        payload['tools'] = tools
    
    response = requests.post(f"{OLLAMA_API}/api/chat", json=payload)
    result = response.json()
    
    # Check if model wants to call a tool
    if result.get('message', {}).get('tool_calls'):
        # Execute tools, append results, call again
        ...