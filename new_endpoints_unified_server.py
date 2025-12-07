# In unified_server.py

from literature_extractor import LiteratureExtractor, EnhancedPubMedRAG, RelevanceLevel

# Initialize the enhanced system
print("Initializing Literature Extractor...")
try:
    default_extraction_model = os.environ.get('EXTRACTION_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
    literature_extractor = LiteratureExtractor(
        ollama_url=OLLAMA_API,
        model=default_extraction_model,
        cache_db='data/extraction_cache.db'
    )
    
    enhanced_rag = EnhancedPubMedRAG(
        pubmed_rag=pubmed_rag,
        extractor=literature_extractor
    )
    print(f"✓ Literature Extractor initialized with {default_extraction_model}")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Literature Extractor: {e}")
    literature_extractor = None
    enhanced_rag = None


@app.route('/api/literature/extract', methods=['POST'])
@limiter.limit("10 per minute")  # Extraction is expensive
def extract_literature():
    """
    Enhanced literature search with local LLM extraction
    
    Returns structured, compressed evidence instead of raw text
    """
    data = request.json or {}
    query = data.get('query', '')
    max_results = data.get('max_results', 5)
    fetch_full_text = data.get('fetch_full_text', True)
    force_pubmed = data.get('force_pubmed', False)
    skip_extraction = data.get('skip_extraction', False)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    if not enhanced_rag:
        return jsonify({'error': 'Enhanced RAG system not available'}), 503
    
    try:
        result = enhanced_rag.retrieve_and_extract(
            query=query,
            max_results=max_results,
            fetch_full_text=fetch_full_text,
            force_pubmed=force_pubmed,
            extract=not skip_extraction
        )
        
        # Serialize extractions
        extractions_json = []
        for ext in result.get('extractions', []):
            extractions_json.append(ext.to_dict())
        
        # Serialize raw documents
        raw_docs_json = []
        for doc in result.get('raw_documents', []):
            raw_docs_json.append({
                'pmid': doc.pmid,
                'title': doc.title,
                'abstract': doc.abstract[:500] + '...' if len(doc.abstract) > 500 else doc.abstract,
                'has_full_text': doc.full_text is not None,
                'source': doc.source.value,
                'year': doc.year
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'extractions': extractions_json,
            'raw_documents': raw_docs_json,
            'formatted_context': result.get('formatted_context', ''),
            'summary': result.get('summary', {}),
            'timing': result.get('timing', {}),
            'retrieval_metadata': result.get('retrieval_metadata', {})
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500


@app.route('/api/chat/evidence-based', methods=['POST'])
@limiter.limit("10 per minute")
def evidence_based_chat():
    """
    Chat endpoint with full extraction pipeline:
    1. Retrieve literature (local RAG + PubMed)
    2. Extract structured evidence (local LLM)
    3. Generate response (cloud LLM with extracted context)
    """
    data = request.json or {}
    query = data.get('query', '')
    model = data.get('model', 'claude:4.5-sonnet')
    max_sources = data.get('max_sources', 5)
    fetch_full_text = data.get('fetch_full_text', True)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    if not enhanced_rag:
        # Fallback to basic chat
        return chat_with_literature()
    
    try:
        # Step 1-2: Retrieve and extract
        extraction_result = enhanced_rag.retrieve_and_extract(
            query=query,
            max_results=max_sources,
            fetch_full_text=fetch_full_text,
            extract=True
        )
        
        formatted_context = extraction_result.get('formatted_context', '')
        extractions = extraction_result.get('extractions', [])
        summary = extraction_result.get('summary', {})
        
        # Step 3: Build prompt for final LLM
        system_prompt = """You are an expert antimicrobial stewardship educator.

You have been provided with structured evidence extracted from peer-reviewed literature.
Each source has been assessed for relevance and key findings have been extracted.

When responding:
1. Prioritize HIGH relevance sources
2. Cite PMIDs when making specific claims
3. Synthesize findings across multiple sources when applicable
4. Note the strength of evidence (study types, sample sizes)
5. Acknowledge limitations and gaps in the evidence
6. Provide actionable clinical recommendations based on the evidence

If the evidence is insufficient, say so clearly and provide your best guidance."""

        user_message = f"""Based on the following extracted evidence, please answer my question.

{formatted_context}

---

QUESTION: {query}

Please provide an evidence-based response with citations."""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        # Call the cloud LLM
        llm_result = chat_with_model(model, messages)
        
        if isinstance(llm_result, tuple) and llm_result[1] != 200:
            return llm_result
        
        response_data = llm_result[0].get_json() if hasattr(llm_result[0], 'get_json') else llm_result[0]
        
        # Enhance response with extraction metadata
        response_data['evidence'] = {
            'sources_used': summary.get('sources_used', []),
            'high_relevance_count': summary.get('high_relevance', 0),
            'total_sources': summary.get('total_retrieved', 0),
            'extractions': [
                {
                    'pmid': e.pmid,
                    'title': e.title,
                    'relevance': e.relevance.value,
                    'study_type': e.study_type,
                    'key_findings': e.key_findings[:2],  # Top 2 findings
                    'year': e.year
                }
                for e in extractions
                if e.relevance in [RelevanceLevel.HIGH, RelevanceLevel.MEDIUM]
            ]
        }
        
        response_data['timing'] = extraction_result.get('timing', {})
        response_data['pipeline'] = 'enhanced_extraction'
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Evidence-based chat failed: {str(e)}'}), 500


@app.route('/api/modules/cicu/feedback-enhanced', methods=['POST'])
@limiter.limit("10 per minute")
def cicu_feedback_with_extraction():
    """
    Enhanced CICU feedback using extracted literature evidence
    """
    data = request.json or {}
    user_input = data.get('input', '')
    level = data.get('level', 'beginner')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # Get scenario context
    level_map = {
        'beginner': CICUDifficultyLevel.BEGINNER,
        'intermediate': CICUDifficultyLevel.INTERMEDIATE,
        'advanced': CICUDifficultyLevel.ADVANCED,
        'expert': CICUDifficultyLevel.EXPERT
    }
    difficulty_level = level_map.get(level, CICUDifficultyLevel.BEGINNER)
    scenario = cicu_module.get_scenario(difficulty_level)
    
    # Build search queries based on scenario and user input
    search_queries = [
        "antimicrobial stewardship implementation barriers",
        "reducing broad-spectrum antibiotic use pediatric",
        "behavior change prescriber antibiotic"
    ]
    
    # Add query based on user input keywords
    if "data" in user_input.lower() or "metric" in user_input.lower():
        search_queries.append("antimicrobial stewardship metrics DOT measurement")
    if "resist" in user_input.lower() or "barrier" in user_input.lower():
        search_queries.append("antimicrobial stewardship barriers physician resistance")
    
    # Retrieve and extract evidence
    all_extractions = []
    if enhanced_rag:
        try:
            for query in search_queries[:3]:  # Limit to 3 queries
                result = enhanced_rag.retrieve_and_extract(
                    query=query,
                    max_results=2,
                    fetch_full_text=False,  # Abstracts usually sufficient
                    extract=True
                )
                all_extractions.extend(result.get('extractions', []))
            
            # Deduplicate by PMID
            seen_pmids = set()
            unique_extractions = []
            for ext in all_extractions:
                if ext.pmid not in seen_pmids:
                    seen_pmids.add(ext.pmid)
                    unique_extractions.append(ext)
            
            # Take top 5 by relevance
            unique_extractions.sort(
                key=lambda x: (
                    0 if x.relevance == RelevanceLevel.HIGH else 
                    1 if x.relevance == RelevanceLevel.MEDIUM else 2,
                    -x.extraction_confidence
                )
            )
            all_extractions = unique_extractions[:5]
            
        except Exception as e:
            print(f"Extraction error in CICU feedback: {e}")
            all_extractions = []
    
    # Format evidence context
    evidence_context = ""
    if all_extractions:
        evidence_context = literature_extractor.format_extractions_for_llm(
            all_extractions,
            max_length=3000
        )
    
    # Build evaluation prompt with extracted evidence
    evaluation_prompt = f"""You are an expert antimicrobial stewardship educator evaluating a fellow's response.

**SCENARIO:**
{scenario['description']}

**KEY TASKS:**
{chr(10).join(f"- {task}" for task in scenario['key_tasks'])}

**LEARNER'S RESPONSE:**
{user_input}

**EXTRACTED EVIDENCE FROM LITERATURE:**
{evidence_context if evidence_context else "No specific literature retrieved for this evaluation."}

**EVALUATION INSTRUCTIONS:**
1. Evaluate across 4 domains: Data Analysis, Behavioral Intervention, Implementation Science, Clinical Decision Making
2. Reference the extracted literature when providing feedback
3. Cite PMIDs when connecting feedback to specific evidence
4. Be constructive and specific

Provide scores (1-5) for each domain, strengths, areas for improvement, and next steps."""

    # Use the existing LLM chain
    response_data = None
    model_used = None
    
    # Try Claude first, then Gemini, then Ollama
    for model_id in ['claude:4.5-haiku', 'gemini:2.5-flash', f'ollama:{os.environ.get("OLLAMA_MODEL", "qwen2.5:72b-instruct-q4_K_M")}']:
        try:
            result = chat_with_model(model_id, [{'role': 'user', 'content': evaluation_prompt}])
            if isinstance(result, tuple) and result[1] == 200:
                response_data = result[0].get_json()
                model_used = model_id
                break
        except:
            continue
    
    if response_data:
        response_data['evidence_used'] = [
            {
                'pmid': e.pmid,
                'title': e.title,
                'relevance': e.relevance.value,
                'key_findings': e.key_findings[:2]
            }
            for e in all_extractions
            if e.relevance in [RelevanceLevel.HIGH, RelevanceLevel.MEDIUM]
        ]
        response_data['model'] = model_used
        return jsonify(response_data)
    
    return jsonify({'error': 'All models failed'}), 503