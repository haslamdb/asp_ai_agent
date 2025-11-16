#!/usr/bin/env python3
"""
Unified AI Server for ASP AI Agent
Integrates:
- Ollama (local models)
- Citation Assistant with PubMedBERT
- Google Gemini API
- Anthropic Claude API
"""

from flask import Flask, request, jsonify, Response, stream_with_context, session, send_file, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import authentication models and routes
from auth_models import db, User, UserSession as AuthUserSession, UserProgress as AuthUserProgress
from auth_routes import auth_bp

# Import session management
from session_manager import (
    SessionManager, UserSession, ConversationTurn,
    ModuleProgress, ModuleStatus, DifficultyLevel
)

# Import new modules
from conversation_manager import ConversationManager, ConversationState
from adaptive_engine import AdaptiveLearningEngine, MasteryLevel
from rubric_scorer import RubricScorer, CriterionLevel
from equity_analytics import EquityAnalytics

# Import CICU module
from modules.cicu_prolonged_antibiotics_module import CICUAntibioticsModule, DifficultyLevel as CICUDifficultyLevel

# Import ASP Literature RAG
from asp_rag_module import ASPLiteratureRAG

# Import Expert Knowledge RAG and Enhanced Feedback Generator
from expert_knowledge_rag import ExpertKnowledgeRAG
from enhanced_feedback_generator import EnhancedFeedbackGenerator

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'asp-ai-agent-secret-key-change-in-production')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///asp_ai_agent.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register authentication blueprint
app.register_blueprint(auth_bp)

CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*', 'file://*', 'https://haslamdb.github.io'], supports_credentials=True)

# Initialize all managers
session_mgr = SessionManager()
conversation_mgr = ConversationManager()
adaptive_engine = AdaptiveLearningEngine()
rubric_scorer = RubricScorer()
equity_analytics = EquityAnalytics()

# Initialize CICU module
cicu_module = CICUAntibioticsModule()

# Initialize ASP Literature RAG system
print("Initializing ASP Literature RAG system...")
try:
    asp_rag = ASPLiteratureRAG()
    print(f"✓ ASP Literature RAG loaded with {asp_rag.collection.count()} chunks")
except Exception as e:
    print(f"⚠ Warning: Could not initialize ASP RAG: {e}")
    asp_rag = None

# Initialize Expert Knowledge RAG and Enhanced Feedback Generator
print("Initializing Expert Knowledge RAG system...")
try:
    expert_rag = ExpertKnowledgeRAG()
    enhanced_feedback_gen = EnhancedFeedbackGenerator()
    print(f"✓ Expert Knowledge RAG loaded")
    print(f"  - Expert corrections: {expert_rag.corrections_collection.count()}")
    print(f"  - Expert exemplars: {expert_rag.exemplars_collection.count()}")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Expert RAG: {e}")
    expert_rag = None
    enhanced_feedback_gen = None

# Configuration - load from environment with defaults
OLLAMA_API_PORT = os.environ.get('OLLAMA_API_PORT', '11434')
CITATION_API_PORT = os.environ.get('CITATION_API_PORT', '9998')
OLLAMA_API = f"http://localhost:{OLLAMA_API_PORT}"
CITATION_API = f"http://localhost:{CITATION_API_PORT}"
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Claude API endpoint
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS)"""
    try:
        return send_file(filename)
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': check_services()
    })

# Old logout routes removed - now handled by auth_bp

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new user session"""
    data = request.json or {}
    user_session = session_mgr.create_session(
        email=data.get('email'),
        name=data.get('name'),
        institution=data.get('institution'),
        fellowship_year=data.get('fellowship_year')
    )
    
    # Store in Flask session
    session['user_id'] = user_session.user_id
    
    return jsonify({
        'user_id': user_session.user_id,
        'created_at': user_session.created_at.isoformat(),
        'current_difficulty': user_session.current_difficulty.value
    })

@app.route('/api/session/current', methods=['GET'])
def get_current_session():
    """Get current session info"""
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({'error': 'No active session'}), 401
    
    user_session = session_mgr.get_session(user_id)
    if not user_session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(user_session.get_progress_summary())

@app.route('/api/user/progress', methods=['GET'])
def get_user_progress():
    """Get detailed user progress"""
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({'error': 'No active session'}), 401
    
    user_session = session_mgr.get_session(user_id)
    if not user_session:
        return jsonify({'error': 'Session not found'}), 404
    
    progress_data = user_session.get_progress_summary()
    
    # Add detailed module progress
    progress_data['modules'] = {}
    for module_id, progress in user_session.module_progress.items():
        progress_data['modules'][module_id] = {
            'status': progress.status.value,
            'attempts': progress.attempts,
            'best_score': progress.best_score,
            'mastery_level': progress.mastery_level,
            'last_attempt': progress.last_attempt.isoformat() if progress.last_attempt else None
        }
    
    # Add recent conversation context
    progress_data['recent_conversations'] = [
        {
            'timestamp': turn.timestamp.isoformat(),
            'module_id': turn.module_id,
            'user_message': turn.user_message[:100] + '...' if len(turn.user_message) > 100 else turn.user_message
        }
        for turn in user_session.get_context_window(5)
    ]
    
    return jsonify(progress_data)

@app.route('/api/conversation/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history for current user"""
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({'error': 'No active session'}), 401
    
    limit = request.args.get('limit', 10, type=int)
    history = session_mgr.get_conversation_history(user_id, limit)
    
    return jsonify({
        'user_id': user_id,
        'conversations': [
            {
                'turn_id': turn.turn_id,
                'timestamp': turn.timestamp.isoformat(),
                'module_id': turn.module_id,
                'user_message': turn.user_message,
                'ai_response': turn.ai_response,
                'citations': turn.citations,
                'metrics': turn.metrics
            }
            for turn in history
        ]
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get system-wide analytics (admin endpoint)"""
    # In production, add authentication here
    analytics = session_mgr.get_analytics()
    return jsonify(analytics)

@app.route('/api/adaptive/assessment', methods=['POST'])
def adaptive_assessment():
    """Get adaptive difficulty assessment for user"""
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({'error': 'No active session'}), 401
    
    user_session = session_mgr.get_session(user_id)
    if not user_session:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.json or {}
    module_id = data.get('module_id')
    
    # Get mastery assessment
    mastery_level = adaptive_engine.assess_mastery_level(user_session, module_id) if module_id else None
    
    # Get personalized learning path
    learning_path = adaptive_engine.generate_personalized_path(user_session)
    
    # Get performance report
    performance_report = adaptive_engine.generate_performance_report(user_session)
    
    return jsonify({
        'current_mastery': mastery_level.name if mastery_level else None,
        'current_difficulty': user_session.current_difficulty.value,
        'learning_path': learning_path,
        'performance_report': performance_report
    })

@app.route('/api/rubric/evaluate', methods=['POST'])
def evaluate_with_rubric():
    """Evaluate a response using rubric scoring"""
    data = request.json or {}
    response = data.get('response', '')
    rubric_id = data.get('rubric_id')
    context = data.get('context', {})
    
    if not response or not rubric_id:
        return jsonify({'error': 'Response and rubric_id required'}), 400
    
    try:
        evaluation = rubric_scorer.evaluate_response(response, rubric_id, context)
        
        return jsonify({
            'rubric_id': evaluation.rubric_id,
            'total_score': evaluation.total_score,
            'percentage': evaluation.percentage,
            'overall_level': evaluation.overall_level.name,
            'strengths': evaluation.strengths,
            'areas_for_improvement': evaluation.areas_for_improvement,
            'specific_feedback': evaluation.specific_feedback,
            'next_steps': evaluation.next_steps,
            'criterion_scores': [
                {
                    'criterion': score.criterion.name,
                    'level': score.level.name,
                    'score': score.score,
                    'feedback': score.feedback
                }
                for score in evaluation.criterion_scores
            ]
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/equity/report', methods=['GET'])
def equity_report():
    """Get equity analytics report"""
    # In production, add authentication here
    days = request.args.get('days', 30, type=int)
    format_type = request.args.get('format', 'json')
    
    report = equity_analytics.analyze_equity(days)
    
    if format_type == 'summary':
        return equity_analytics.export_equity_report(report, 'summary'), 200, {'Content-Type': 'text/plain'}
    else:
        return jsonify(json.loads(equity_analytics.export_equity_report(report, 'json')))

@app.route('/api/equity/dashboard', methods=['GET'])
def equity_dashboard():
    """Get equity dashboard data"""
    # In production, add authentication here
    dashboard_data = equity_analytics.generate_dashboard_data()
    return jsonify(dashboard_data)

@app.route('/api/modules/cicu/scenario', methods=['GET'])
def get_cicu_scenario():
    """Get CICU module scenario for specified difficulty level"""
    level_str = request.args.get('level', 'beginner').lower()

    # Map string to DifficultyLevel enum
    level_map = {
        'beginner': CICUDifficultyLevel.BEGINNER,
        'intermediate': CICUDifficultyLevel.INTERMEDIATE,
        'advanced': CICUDifficultyLevel.ADVANCED,
        'expert': CICUDifficultyLevel.EXPERT
    }

    difficulty_level = level_map.get(level_str, CICUDifficultyLevel.BEGINNER)
    scenario = cicu_module.get_scenario(difficulty_level)

    return jsonify(scenario)

@app.route('/api/modules/cicu/hint', methods=['GET'])
def get_cicu_hint():
    """Get hint for CICU module"""
    level_str = request.args.get('level', 'beginner').lower()
    hint_number = request.args.get('hint_number', 0, type=int)

    # Map string to DifficultyLevel enum
    level_map = {
        'beginner': CICUDifficultyLevel.BEGINNER,
        'intermediate': CICUDifficultyLevel.INTERMEDIATE,
        'advanced': CICUDifficultyLevel.ADVANCED,
        'expert': CICUDifficultyLevel.EXPERT
    }

    difficulty_level = level_map.get(level_str, CICUDifficultyLevel.BEGINNER)
    hint = cicu_module.get_hint(difficulty_level, hint_number)

    if hint:
        return jsonify({'hint': hint, 'hint_number': hint_number})
    else:
        return jsonify({'error': 'No more hints available'}), 404

@app.route('/api/modules/cicu/evaluate', methods=['POST'])
def evaluate_cicu_response():
    """Evaluate user response for CICU module"""
    data = request.json or {}
    response_text = data.get('response', '')
    level_str = data.get('level', 'beginner').lower()

    # Map string to DifficultyLevel enum
    level_map = {
        'beginner': CICUDifficultyLevel.BEGINNER,
        'intermediate': CICUDifficultyLevel.INTERMEDIATE,
        'advanced': CICUDifficultyLevel.ADVANCED,
        'expert': CICUDifficultyLevel.EXPERT
    }

    difficulty_level = level_map.get(level_str, CICUDifficultyLevel.BEGINNER)
    evaluation = cicu_module.evaluate_response(response_text, difficulty_level)

    return jsonify(evaluation)

@app.route('/api/modules/cicu/metrics', methods=['GET'])
def get_cicu_metrics():
    """Get implementation metrics tracker for CICU module"""
    metrics = cicu_module.generate_implementation_tracker()
    return jsonify(metrics)

@app.route('/api/modules/cicu/countermeasures', methods=['GET'])
def get_cicu_countermeasures():
    """Get countermeasure strategies for barriers"""
    barrier_type = request.args.get('barrier_type', 'provider_resistance')
    countermeasures = cicu_module.generate_countermeasure_template(barrier_type)
    return jsonify(countermeasures)

@app.route('/api/modules/cicu/feedback', methods=['POST'])
def cicu_ai_feedback():
    """AI-powered CICU feedback using LLM with rubric-based evaluation"""
    data = request.json or {}
    user_input = data.get('input', '')
    level = data.get('level', 'beginner')
    preferred_model = data.get('model', 'gemma2:27b')  # Default to faster model

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    # Get the scenario and rubrics for this level
    level_map = {
        'beginner': CICUDifficultyLevel.BEGINNER,
        'intermediate': CICUDifficultyLevel.INTERMEDIATE,
        'advanced': CICUDifficultyLevel.ADVANCED,
        'expert': CICUDifficultyLevel.EXPERT
    }
    difficulty_level = level_map.get(level, CICUDifficultyLevel.BEGINNER)
    scenario = cicu_module.get_scenario(difficulty_level)

    # Retrieve relevant literature using RAG
    literature_context = ""
    if asp_rag:
        try:
            # Extract key concepts for literature search
            search_queries = [
                f"antimicrobial stewardship {level}",
                "reducing broad-spectrum antibiotic use",
                "days of therapy DOT measurement",
                "behavioral change interventions antimicrobial",
                "implementation science stewardship"
            ]

            all_results = []
            for query in search_queries:
                results = asp_rag.search(query, n_results=2, min_similarity=0.4)
                all_results.extend(results)

            # Deduplicate by PMID and take top 5
            seen_pmids = set()
            unique_results = []
            for result in all_results:
                if result['pmid'] not in seen_pmids:
                    seen_pmids.add(result['pmid'])
                    unique_results.append(result)
                    if len(unique_results) >= 5:
                        break

            if unique_results:
                literature_parts = []
                for i, result in enumerate(unique_results, 1):
                    excerpt = result['text'][:400]  # Limit excerpt length
                    literature_parts.append(f"[{i}] PMID {result['pmid']}: {excerpt}")

                literature_context = "\n\n".join(literature_parts)
                print(f"   Retrieved {len(unique_results)} relevant papers for context")
        except Exception as e:
            print(f"   Warning: RAG search failed: {e}")
            literature_context = ""

    # Build comprehensive evaluation prompt with literature context
    evaluation_prompt = f"""You are an expert antimicrobial stewardship educator evaluating a fellow's response to a training scenario.

**SCENARIO:**
{scenario['description']}

**KEY TASKS:**
{chr(10).join(f"- {task}" for task in scenario['key_tasks'])}

**LEARNER'S RESPONSE:**
{user_input}"""

    # Add literature context if available
    if literature_context:
        evaluation_prompt += f"""

**RELEVANT RESEARCH EVIDENCE:**
The following are excerpts from recent antimicrobial stewardship literature that may be relevant to this scenario. Reference these when appropriate in your feedback to provide evidence-based guidance:

{literature_context}

When referencing these sources, cite them using the PMID numbers provided."""

    evaluation_prompt += """

**YOUR EVALUATION TASK:**
Evaluate this response across 4 competency domains using the rubrics below. For each domain, assign a score (1-5) and provide specific, actionable feedback. When relevant, reference the research evidence provided above to support your feedback.

**RUBRIC DOMAINS:**

1. **Data Analysis** (1-5):
   - 5 (Exemplary): Calculates DOT correctly, uses multiple benchmarks, identifies patterns, creates compelling visualizations
   - 4 (Proficient): Accurate DOT calculation, uses benchmarks, recognizes gaps, good data presentation
   - 3 (Developing): Basic DOT calculation, some comparison, identifies obvious issues
   - 2 (Emerging): Calculation errors, minimal benchmarking, poor pattern recognition
   - 1 (Not Evident): No meaningful metrics or analysis

2. **Behavioral Intervention** (1-5):
   - 5 (Exemplary): Identifies cognitive biases, uses behavior change frameworks, creates psychological safety, designs nudges
   - 4 (Proficient): Identifies biases, applies behavior change principles, addresses hierarchy/fear, uses champions
   - 3 (Developing): Recognizes barriers, focuses on education, basic communication planning
   - 2 (Emerging): Minimal behavioral insight, relies on mandates, no psychological factors
   - 1 (Not Evident): Ignores human factors, policy-only approach, no stakeholder engagement

3. **Implementation Science** (1-5):
   - 5 (Exemplary): Uses implementation framework (PDSA/RE-AIM), plans sustainability, includes metrics, addresses adaptation
   - 4 (Proficient): Structured approach, pilot testing, success metrics, considers sustainability
   - 3 (Developing): Basic implementation plan, limited testing, few metrics
   - 2 (Emerging): Vague approach, no pilot, unclear metrics
   - 1 (Not Evident): No implementation plan or metrics

4. **Clinical Decision Making** (1-5):
   - 5 (Exemplary): Evidence-based guidelines, balances safety/stewardship, context-specific protocols
   - 4 (Proficient): Uses guidelines appropriately, considers safety, addresses clinical concerns
   - 3 (Developing): Basic guideline awareness, some safety consideration
   - 2 (Emerging): Limited clinical reasoning, generic approaches
   - 1 (Not Evident): No clinical evidence or safety consideration

**OUTPUT FORMAT:**
Provide your evaluation in this structure:

## Evaluation Summary

**Overall Score:** [Average of 4 domains]/5.0

### Domain Scores:
- Data Analysis: [score]/5 - [Performance level]
- Behavioral Intervention: [score]/5 - [Performance level]
- Implementation Science: [score]/5 - [Performance level]
- Clinical Decision Making: [score]/5 - [Performance level]

### Strengths:
- [Specific strength 1]
- [Specific strength 2]
- [Specific strength 3]

### Areas for Improvement:
- [Specific improvement area 1 with actionable advice]
- [Specific improvement area 2 with actionable advice]
- [Specific improvement area 3 with actionable advice]

### Specific Feedback:
[Detailed constructive feedback addressing both what was done well and what needs improvement. Be specific, reference examples from their response, and provide concrete suggestions.]

### Next Steps:
1. [Actionable next step]
2. [Actionable next step]
3. [Actionable next step]

IMPORTANT GUIDANCE:
- Be constructive and supportive while maintaining high standards
- If they suggest inappropriate stakeholder engagement (e.g., blaming, confrontation), address this firmly but constructively
- Highlight what they did well before addressing gaps
- Provide specific, actionable guidance for improvement
- Reference evidence-based practices and frameworks where appropriate"""

    # Try to get AI feedback with fallback chain
    response_data = None
    model_used = None
    errors = []

    try:
        # Try Gemini first (most reliable for now)
        if GEMINI_API_KEY:
            try:
                print(f"Trying Gemini for CICU feedback...")
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                # Try newest models first
                model_name = 'gemini-2.0-flash-exp'
                model = genai.GenerativeModel(model_name)
                result = model.generate_content(evaluation_prompt)
                response_data = result.text
                model_used = model_name
                print(f"Gemini succeeded! Response length: {len(response_data)}")
            except Exception as e:
                error_msg = f"Gemini failed: {e}"
                print(error_msg)
                errors.append(error_msg)

        # Try Ollama if Gemini didn't work and it was requested
        if not response_data and (preferred_model.startswith('ollama:') or not ':' in preferred_model):
            try:
                model_name = preferred_model.replace('ollama:', '') if preferred_model.startswith('ollama:') else preferred_model
                print(f"Trying Ollama model: {model_name}...")

                ollama_response = requests.post(
                    f"{OLLAMA_API}/api/chat",
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": evaluation_prompt}],
                        "stream": False
                    },
                    timeout=45  # Generous timeout for evaluation
                )

                if ollama_response.status_code == 200:
                    result = ollama_response.json()
                    response_data = result.get('message', {}).get('content', '')
                    model_used = f"ollama:{model_name}"
                    print(f"Ollama succeeded! Response length: {len(response_data)}")
                else:
                    error_msg = f"Ollama returned status {ollama_response.status_code}"
                    print(error_msg)
                    errors.append(error_msg)
            except Exception as e:
                error_msg = f"Ollama failed: {e}"
                print(error_msg)
                errors.append(error_msg)

        # Final fallback to Claude if available
        if not response_data and ANTHROPIC_API_KEY:
            try:
                print(f"Trying Claude...")
                from anthropic import Anthropic
                client = Anthropic(api_key=ANTHROPIC_API_KEY)
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": evaluation_prompt}]
                )
                response_data = message.content[0].text
                model_used = "claude-3-5-sonnet"
                print(f"Claude succeeded! Response length: {len(response_data)}")
            except Exception as e:
                error_msg = f"Claude failed: {e}"
                print(error_msg)
                errors.append(error_msg)

        if response_data:
            return jsonify({
                'response': response_data,
                'model': model_used,
                'success': True
            })
        else:
            error_summary = '; '.join(errors) if errors else 'No models attempted'
            print(f"All models failed: {error_summary}")
            return jsonify({'error': f'All AI models failed: {error_summary}'}), 500

    except Exception as e:
        print(f"Error in AI feedback: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'AI evaluation failed: {str(e)}'}), 500

@app.route('/api/feedback/enhanced', methods=['POST'])
def enhanced_feedback():
    """
    Enhanced AI feedback using Expert Knowledge RAG

    Combines literature RAG + expert corrections + exemplar responses
    for higher quality, expert-validated feedback
    """
    if not enhanced_feedback_gen:
        return jsonify({
            'error': 'Enhanced feedback system not available',
            'fallback': True
        }), 503

    data = request.json or {}
    user_input = data.get('input', '')
    module_id = data.get('module_id', 'cicu_prolonged_antibiotics')
    scenario_id = data.get('scenario_id', 'cicu_beginner_data_analysis')
    level = data.get('level', 'beginner')

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    try:
        # Use Enhanced Feedback Generator
        print(f"Generating enhanced feedback for: {scenario_id} ({level})")

        result = enhanced_feedback_gen.generate_feedback(
            module_id=module_id,
            scenario_id=scenario_id,
            user_response=user_input,
            difficulty_level=level,
            use_expert_knowledge=True,
            use_literature=True
        )

        # The enhanced_prompt includes expert corrections and exemplars
        # Now we need to send it to an LLM to generate the actual feedback

        # Try LLMs in order: Claude -> Gemini -> Ollama
        response_data = None
        model_used = None
        errors = []

        # Try Claude first (best quality)
        if ANTHROPIC_API_KEY:
            try:
                print("Trying Claude for enhanced feedback...")
                from anthropic import Anthropic
                client = Anthropic(api_key=ANTHROPIC_API_KEY)
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=3000,
                    messages=[{"role": "user", "content": result['enhanced_prompt']}]
                )
                response_data = message.content[0].text
                model_used = "claude-3.5-sonnet"
                print(f"Claude succeeded with enhanced feedback!")
            except Exception as e:
                errors.append(f"Claude failed: {e}")
                print(errors[-1])

        # Fallback to Gemini if Claude failed
        if not response_data and GEMINI_API_KEY:
            try:
                print("Trying Gemini for enhanced feedback...")
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(result['enhanced_prompt'])
                response_data = response.text
                model_used = "gemini-1.5-flash"
                print(f"Gemini succeeded with enhanced feedback!")
            except Exception as e:
                errors.append(f"Gemini failed: {e}")
                print(errors[-1])

        # Fallback to local Ollama if both failed
        if not response_data:
            try:
                print("Trying Ollama for enhanced feedback...")
                default_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
                response = requests.post(
                    f"{OLLAMA_API}/api/generate",
                    json={
                        'model': default_model,
                        'prompt': result['enhanced_prompt'],
                        'stream': False
                    },
                    timeout=120
                )
                if response.status_code == 200:
                    response_data = response.json().get('response', '')
                    model_used = f"ollama:{default_model}"
                    print(f"Ollama succeeded with enhanced feedback!")
                else:
                    errors.append(f"Ollama failed: {response.text}")
            except Exception as e:
                errors.append(f"Ollama failed: {e}")
                print(errors[-1])

        if response_data:
            return jsonify({
                'success': True,
                'response': response_data,
                'model': model_used,
                'enhanced': True,
                'sources': result['sources'],
                'metadata': result['metadata']
            })
        else:
            error_summary = '; '.join(errors) if errors else 'No models attempted'
            return jsonify({
                'error': f'All AI models failed: {error_summary}',
                'success': False
            }), 500

    except Exception as e:
        print(f"Error in enhanced feedback: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Enhanced feedback failed: {str(e)}',
            'success': False
        }), 500

@app.route('/api/conversation/process', methods=['POST'])
def process_conversation():
    """Process conversation turn with context awareness"""
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({'error': 'No active session'}), 401
    
    user_session = session_mgr.get_session(user_id)
    if not user_session:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.json or {}
    user_message = data.get('message', '')
    module_id = data.get('module_id')
    
    # Process through conversation manager
    conversation_result = conversation_mgr.process_turn(
        user_session, user_message, module_id
    )
    
    # Get appropriate scenario if needed
    if conversation_result['context'].state == ConversationState.SCENARIO_INTRODUCTION:
        scenario = conversation_mgr.get_scenario_for_user(user_session, module_id)
        if scenario:
            # Adapt scenario complexity
            adapted_scenario = adaptive_engine.adapt_scenario_complexity(scenario, user_session)
            conversation_result['scenario'] = adapted_scenario
    
    return jsonify(conversation_result)

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

        # Check if result is a tuple (error case) or Response (success case)
        if isinstance(result, tuple):
            return result  # Error response
        else:
            # Success - transform response to match expected frontend format
            response_data = result.get_json()
            return jsonify({
                'text': response_data.get('response', ''),
                'model': response_data.get('model', ''),
                'usage': response_data.get('usage', {})
            })
    except Exception as e:
        return jsonify({'error': f'Claude endpoint error: {str(e)}'}), 500

@app.route('/gemini', methods=['POST'])
@app.route('/', methods=['POST'])
def gemini_endpoint():
    """Direct Gemini endpoint for frontend compatibility (also handles root /)"""
    data = request.json
    system_prompt = data.get('systemInstruction', {}).get('parts', [{}])[0].get('text', '')
    contents = data.get('contents', [])

    if not contents:
        return jsonify({'error': 'Contents are required'}), 400

    # Convert Gemini format to standard messages format
    messages = []
    for content in contents:
        parts = content.get('parts', [])
        text = parts[0].get('text', '') if parts else ''
        messages.append({
            'role': 'user' if content.get('role', 'user') == 'user' else 'assistant',
            'content': text
        })

    try:
        # Use Gemini 2.0 Flash as default
        result = gemini_chat('gemini-2.0-flash-exp', messages, system_prompt)

        # Check if result is a tuple (error case) or Response (success case)
        if isinstance(result, tuple):
            return result  # Error response
        else:
            # Success - transform response to match expected frontend format
            response_data = result.get_json()
            return jsonify({
                'candidates': [{
                    'content': {
                        'parts': [{
                            'text': response_data.get('response', '')
                        }]
                    }
                }],
                'model': response_data.get('model', ''),
                'usage': response_data.get('usage', {})
            })
    except Exception as e:
        return jsonify({'error': f'Gemini endpoint error: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Unified chat endpoint for all models"""
    data = request.json
    default_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
    model_id = data.get('model', f'ollama:{default_model}')
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
    Now with session management and multi-turn context
    """
    data = request.json
    module = data.get('module', 'general')
    user_input = data.get('input', '')
    preferred_model = data.get('model')
    
    # Get or create user session
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    user_session = None
    if user_id:
        user_session = session_mgr.get_session(user_id)
    
    if not user_session:
        # Create anonymous session
        user_session = session_mgr.create_session()
        session['user_id'] = user_session.user_id
        user_id = user_session.user_id
    
    # Adapt difficulty based on user's current level
    difficulty_prompts = {
        DifficultyLevel.BEGINNER: "Provide foundational concepts with clear explanations. Use simple examples.",
        DifficultyLevel.INTERMEDIATE: "Build on basic knowledge. Include some nuance and complexity.",
        DifficultyLevel.ADVANCED: "Assume strong foundation. Focus on edge cases and advanced strategies.",
        DifficultyLevel.EXPERT: "Engage at expert level. Include cutting-edge research and controversial topics."
    }
    
    difficulty_modifier = difficulty_prompts.get(user_session.current_difficulty, "")
    
    # Build specialized prompts based on module
    if module == 'business_case':
        system_prompt = f"""You are a senior hospital administrator (CFO/CMO) reviewing an ASP business case.
        Focus on ROI calculations, stakeholder engagement strategies, and measurable outcomes.
        Be skeptical but constructive. Ground feedback in real-world ASP literature.
        {difficulty_modifier}"""
    elif module == 'prescriber_psychology':
        system_prompt = f"""You are an expert in behavioral science and prescriber psychology for ASP.
        Analyze cognitive biases (commission bias, omission bias, availability heuristic).
        Suggest evidence-based communication strategies like academic detailing and motivational interviewing.
        {difficulty_modifier}"""
    else:
        system_prompt = f"""You are an ASP expert providing feedback on antimicrobial stewardship.
        Focus on evidence-based practices and implementation strategies.
        {difficulty_modifier}"""
    
    # Add conversation context
    context_prompt = ""
    recent_turns = user_session.get_context_window(3)
    if recent_turns:
        context_prompt = "\n\nPrevious conversation context:\n"
        for turn in recent_turns:
            context_prompt += f"User: {turn.user_message[:200]}...\n"
            context_prompt += f"Assistant: {turn.ai_response[:200]}...\n\n"
    
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
    
    # Build enhanced input with context
    enhanced_input = user_input
    if context_prompt:
        enhanced_input = context_prompt + "\nCurrent question: " + user_input
    if citations:
        enhanced_input += "\n\nRelevant literature to consider:\n"
        for cite in citations:
            enhanced_input += f"- {cite.get('title', '')} ({cite.get('year', '')}): {cite.get('context', '')[:100]}...\n"
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': enhanced_input}
    ]

    response_data = None
    model_used = None

    # Try preferred model first, then fall back to best available
    if preferred_model:
        result = chat_with_model(preferred_model, messages)
        if isinstance(result, tuple) and len(result) == 2:
            response_obj, status_code = result
            if status_code == 200:
                response_data = response_obj.get_json()
                response_data['citations'] = citations
                model_used = preferred_model

    # Try models in order of preference for medical tasks if no response yet
    if not response_data:
        default_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
        model_preference = [
            'claude:3-sonnet',  # Best for medical reasoning
            'gemini:2.5-flash',  # Good with search integration
            f'ollama:{default_model}',  # Local fallback
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
            if isinstance(result, tuple) and len(result) == 2:
                response_obj, status_code = result
                if status_code == 200:
                    response_data = response_obj.get_json()
                    response_data['citations'] = citations
                    model_used = model_id
                    break
    
    if response_data:
        # Process conversation context
        conversation_context = conversation_mgr.process_turn(user_session, user_input, module)
        
        # Get coaching prompt if in active coaching mode
        if conversation_context['response_strategy']['type'] == 'coaching':
            coaching_prompt = conversation_mgr.generate_coaching_prompt(
                conversation_context['context'],
                conversation_context['response_strategy']
            )
            # Note: coaching prompt applied to earlier message construction
        
        # Save conversation turn
        turn = ConversationTurn(
            user_message=user_input,
            ai_response=response_data.get('response', ''),
            module_id=module,
            context_used={
                'difficulty': user_session.current_difficulty.value,
                'conversation_state': conversation_context['context'].state.value,
                'scaffolding_level': conversation_context['scaffolding_level']
            },
            citations=citations,
            metrics={'model': model_used}
        )
        user_session.add_turn(turn)
        session_mgr.save_conversation_turn(user_id, turn)
        
        # Evaluate response with rubric if appropriate
        rubric_evaluation = None
        score = 0.5  # Default score
        
        if module in ['leadership', 'analytics', 'behavioral', 'clinical']:
            # Map module to appropriate rubric
            rubric_map = {
                'leadership': 'leadership_business_case',
                'analytics': 'analytics_dot_calculation',
                'behavioral': 'behavioral_bias_identification',
                'clinical': 'clinical_protocol_development'
            }
            rubric_id = rubric_map.get(module)
            
            if rubric_id:
                try:
                    evaluation = rubric_scorer.evaluate_response(
                        response_data.get('response', ''),
                        rubric_id,
                        {'user_input': user_input, 'citations': citations}
                    )
                    rubric_evaluation = {
                        'score': evaluation.percentage,
                        'level': evaluation.overall_level.name,
                        'strengths': evaluation.strengths[:2],
                        'improvements': evaluation.areas_for_improvement[:2],
                        'feedback': evaluation.specific_feedback
                    }
                    score = evaluation.percentage / 100  # Convert to 0-1 scale
                except:
                    # Fallback to simple scoring
                    if len(response_data.get('response', '')) > 500:
                        score += 0.2
                    if citations:
                        score += 0.3
        else:
            # Simple scoring for non-module responses
            if len(response_data.get('response', '')) > 500:
                score += 0.2
            if citations:
                score += 0.3
        
        # Update module progress with score
        user_session.update_module_progress(module, score, response_data)
        
        # Adaptive difficulty adjustment
        recent_performance = {
            'accuracy': score,
            'response_time': 30,  # Placeholder - would track actual time
            'hints_used': len(conversation_context.get('hints_available', [])),
            'attempts': conversation_context['context'].attempts_on_current
        }
        new_difficulty, difficulty_reasoning = adaptive_engine.calculate_difficulty_adjustment(
            user_session, recent_performance
        )
        if new_difficulty != user_session.current_difficulty:
            user_session.current_difficulty = new_difficulty
        
        session_mgr.update_session(user_session)
        
        # Add comprehensive session info to response
        response_data['session_info'] = {
            'user_id': user_id,
            'difficulty': user_session.current_difficulty.value,
            'module_attempts': user_session.module_progress.get(module, ModuleProgress(module)).attempts if module in user_session.module_progress else 0,
            'conversation_state': conversation_context['context'].state.value,
            'scaffolding_level': conversation_context['scaffolding_level'],
            'next_steps': conversation_context['next_steps']
        }
        
        # Add rubric evaluation if available
        if rubric_evaluation:
            response_data['evaluation'] = rubric_evaluation
        
        # Add adaptive learning insights
        mastery_level = adaptive_engine.assess_mastery_level(user_session, module)
        response_data['learning_insights'] = {
            'current_mastery': mastery_level.name,
            'difficulty_adjustment': difficulty_reasoning if new_difficulty != user_session.current_difficulty else None,
            'personalized_path': adaptive_engine.generate_personalized_path(user_session)[:1]  # Top recommendation
        }
        
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

                        default_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
                        local_messages = [{'role': 'user', 'content': local_prompt}]
                        local_response = ollama_chat(default_model, local_messages)
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

            default_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
            local_messages = [{'role': 'user', 'content': local_prompt}]
            local_response = ollama_chat(default_model, local_messages)
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

    # Create database tables on first run
    with app.app_context():
        db.create_all()
        print("\n✓ Database initialized")

        # Check if admin user exists, create if not
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("  Creating default admin user...")
            admin = User(
                email='admin@asp-ai-agent.com',
                full_name='Admin User',
                is_admin=True,
                is_active=True,
                email_verified=True
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print(f"  ✓ Admin user created: admin@asp-ai-agent.com / admin123")
            print(f"    WARNING: Change this password immediately!")

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
    print("Server running on http://localhost:8080")
    print("=" * 60)

    print("\nAuthentication Endpoints:")
    print("  GET  /login           - User login page")
    print("  GET  /signup          - User registration page")
    print("  GET  /dashboard       - User dashboard (requires login)")
    print("  GET  /logout          - User logout")

    print("\nAPI Endpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /api/models      - List available models")
    print("  POST /api/chat        - Chat with any model")
    print("  POST /api/asp-feedback - ASP-specific feedback")
    print("  POST /api/feedback/enhanced - Enhanced feedback with Expert RAG")
    print("  GET  /api/modules/cicu/scenario - CICU scenarios")
    print("  GET  /api/modules/cicu/hint     - CICU hints")
    print("  POST /api/modules/cicu/evaluate - CICU evaluation")

    print("\nTo use Claude or Gemini, set environment variables:")
    print("  export ANTHROPIC_API_KEY='your-key-here'")
    print("  export GEMINI_API_KEY='your-key-here'")
    print()

    # Production settings for AWS Elastic Beanstalk
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(host='0.0.0.0', port=port, debug=debug)