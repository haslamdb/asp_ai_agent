# In unified_server.py

from pubmed_rag_tools import PubMedRAGSystem, PUBMED_RAG_TOOLS

# Initialize the hierarchical RAG system
pubmed_rag = PubMedRAGSystem(
    local_rag=asp_rag,  # Your existing ASPLiteratureRAG
    similarity_threshold=0.55,
    min_local_results=3,
    ncbi_api_key=os.environ.get('NCBI_API_KEY')  # Optional but recommended
)

@app.route('/api/literature/search', methods=['POST'])
@limiter.limit("30 per minute")
def literature_search():
    """Hierarchical literature search endpoint"""
    data = request.json or {}
    query = data.get('query', '')
    max_results = data.get('max_results', 5)
    fetch_full_text = data.get('fetch_full_text', False)
    force_pubmed = data.get('force_pubmed', False)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    documents, metadata = pubmed_rag.retrieve(
        query=query,
        max_results=max_results,
        fetch_full_text=fetch_full_text,
        force_pubmed=force_pubmed
    )
    
    return jsonify({
        'success': True,
        'documents': [
            {
                'pmid': doc.pmid,
                'title': doc.title,
                'abstract': doc.abstract[:500] + '...' if len(doc.abstract) > 500 else doc.abstract,
                'has_full_text': doc.full_text is not None,
                'source': doc.source.value,
                'similarity': doc.similarity_score,
                'year': doc.year,
                'authors': doc.authors,
                'journal': doc.journal
            }
            for doc in documents
        ],
        'metadata': metadata
    })


@app.route('/api/chat/with-literature', methods=['POST'])
@limiter.limit("15 per minute")
def chat_with_literature():
    """
    Chat endpoint that automatically retrieves relevant literature
    and includes it in context for the LLM
    """
    data = request.json or {}
    query = data.get('query', '')
    model = data.get('model', 'claude:4.5-sonnet')
    auto_search = data.get('auto_search', True)
    fetch_full_text = data.get('fetch_full_text', False)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    literature_context = ""
    sources_used = []
    documents = []
    
    if auto_search:
        # Retrieve relevant literature
        documents, metadata = pubmed_rag.retrieve(
            query=query,
            max_results=5,
            fetch_full_text=fetch_full_text
        )
        sources_used = metadata.get('sources_used', [])
        
        if documents:
            literature_context = pubmed_rag.format_context_for_llm(documents)
    
    # Build the prompt with literature context
    system_prompt = """You are an expert antimicrobial stewardship educator.
    
When literature is provided, you MUST:
1. Ground your response in the evidence provided
2. Cite sources by PMID when making specific claims
3. Distinguish between what the literature says vs. your interpretation
4. Note if the literature is insufficient to fully answer the question

If no relevant literature is found, acknowledge this and provide your best guidance
while noting the limitation."""

    user_message = query
    if literature_context:
        user_message = f"""{literature_context}

Based on the above literature, please answer:

{query}"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message}
    ]
    
    # Call the LLM
    result = chat_with_model(model, messages)
    
    if isinstance(result, tuple) and result[1] != 200:
        return result
    
    response_data = result[0].get_json() if hasattr(result[0], 'get_json') else result[0]
    
    # Enhance response with literature metadata
    response_data['literature'] = {
        'sources_used': sources_used,
        'documents': [
            {
                'pmid': doc.pmid,
                'title': doc.title,
                'source': doc.source.value,
                'year': doc.year
            }
            for doc in documents
        ],
        'count': len(documents)
    }
    
    return jsonify(response_data)