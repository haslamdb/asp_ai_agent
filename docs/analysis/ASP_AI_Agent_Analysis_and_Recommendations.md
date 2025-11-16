# ASP AI Agent: Code Review & Advanced Curriculum Framework

## Executive Summary

Your ASP AI Agent represents an innovative approach to addressing a critical gap identified in the manuscript: **the absence of accessible, high-quality training in advanced antimicrobial stewardship competencies** for pediatric ID fellows.

This analysis provides:
1. **Code Architecture Review** - Current strengths and enhancement opportunities
2. **AI Teaching Module Framework** - Detailed outline for building intelligent tutoring modules aligned with Table 1 of the manuscript
3. **Implementation Roadmap** - Technical and pedagogical recommendations

---

## PART 1: CODE ARCHITECTURE REVIEW

### Current Strengths

Your implementation demonstrates several excellent architectural decisions:

#### 1. **Unified Backend Pattern** (`unified_server.py`)
- **Strength**: Single point of contact for all AI providers (Claude, Gemini, Ollama, Citation Assistant)
- **Benefit**: Seamless model switching without client-side complexity
- **Compliance**: Aligns with security best practice of server-side API key management

```python
# Architecture Pattern: Provider-Agnostic Routing
API_ENDPOINTS = {
    'claude': claude_chat,
    'gemini': gemini_chat,
    'ollama': ollama_chat,
    'citation_assistant': citation_search
}
```

#### 2. **Hybrid RAG Pattern** (`/api/hybrid-asp` endpoint)
Your three-stage hybrid approach is educationally sound:
- Stage 1: Cloud model interprets user intent → **Good for complex reasoning**
- Stage 2: Local citation-augmented LLM generates factual content → **Good for grounded medical facts**
- Stage 3: Cloud model formats for pedagogy → **Good for instructional design**

This mirrors cognitive load theory: breaking complex tasks into manageable stages.

#### 3. **Graceful Fallback Chain**
```python
model_preference = [
    'claude:3-sonnet',      # Best reasoning
    'gemini:2.5-flash',     # Good with search
    'ollama:gemma2:27b',    # Local fallback
]
```
This ensures service resilience and user experience continuity.

#### 4. **Responsive Modularization**
Your frontend (`agent_models.html`) cleanly separates:
- Module management (Module 1: Business Case, Module 2: Prescriber Psychology)
- Feedback rendering (Markdown → HTML conversion)
- Citation tracking (Source attribution)

---

### Recommendations for Enhancement

#### **CRITICAL: Add Persistent User State & Progress Tracking**

**Current State**: Each submission is stateless
**Problem**: Fellows have no learning history, no progression through curriculum
**Recommendation**: 

```python
# Add to unified_server.py

from datetime import datetime
from typing import Optional
import uuid

class UserSession:
    """Track fellow progress through curriculum"""
    def __init__(self, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.completions = {}  # {module_id: {status, score, feedback}}
        self.reflections = []  # Track learning reflections
        self.interactions = []  # For analytics/personalization
    
    def record_submission(self, module_id: str, submission: dict, 
                         feedback: dict, score: float):
        """Log a submission attempt"""
        self.completions[module_id] = {
            'timestamp': datetime.now(),
            'submission': submission,
            'feedback': feedback,
            'score': score,
            'status': 'complete' if score > 0.7 else 'needs_improvement'
        }
    
    def get_progress_report(self):
        """Generate progress dashboard data"""
        return {
            'total_modules': len(self.completions),
            'completed': sum(1 for c in self.completions.values() 
                           if c['status'] == 'complete'),
            'mastery_score': self._calculate_mastery()
        }

@app.route('/api/user/progress', methods=['GET'])
def get_user_progress():
    """Return learner's progress through curriculum"""
    user_id = request.args.get('user_id')
    # Retrieve session data and return progress
    pass
```

**Why**: Enables adaptive learning, spaced repetition, and cohort analytics.

---

#### **IMPORTANT: Add Multi-Turn Conversation Context Management**

**Current State**: Each API call treats messages independently
**Problem**: 
- No learning history within a session
- Can't build on previous feedback
- Poor scaffolding for complex topics

**Recommendation**:

```python
class ConversationManager:
    """Manage multi-turn educational conversations"""
    def __init__(self, session_id: str, module_id: str):
        self.session_id = session_id
        self.module_id = module_id
        self.conversation_history = []
        self.context_window = 10  # Keep last 10 exchanges
    
    def add_exchange(self, user_input: str, ai_response: str, 
                    sources: List[Dict] = None):
        """Add to conversation history"""
        self.conversation_history.append({
            'user': user_input,
            'assistant': ai_response,
            'sources': sources,
            'timestamp': datetime.now()
        })
    
    def get_system_context(self, module_id: str) -> str:
        """Build system prompt with conversation history"""
        recent = self.conversation_history[-self.context_window:]
        context = f"""
        You are coaching a fellow through Module: {module_id}
        
        Previous exchanges in this session:
        {json.dumps(recent, indent=2)}
        
        Build upon what you've already discussed. Provide progressive feedback
        that acknowledges their learning trajectory.
        """
        return context

@app.route('/api/chat/multi-turn', methods=['POST'])
def multi_turn_chat():
    """Handle conversational exchanges within a module"""
    data = request.json
    session_id = data.get('session_id')
    module_id = data.get('module_id')
    user_message = data.get('message')
    
    manager = ConversationManager(session_id, module_id)
    # Load history from storage
    
    system_context = manager.get_system_context(module_id)
    response = chat_with_model(
        'claude:3-sonnet',
        [{'role': 'system', 'content': system_context},
         {'role': 'user', 'content': user_message}]
    )
    
    # Save and return
    manager.add_exchange(user_message, response)
    return jsonify({'response': response, 'session_id': session_id})
```

**Why**: Enables scaffolded learning, Socratic questioning, and context-aware feedback.

---

#### **IMPORTANT: Implement Spaced Repetition & Adaptive Difficulty**

**Current State**: All fellows get same content difficulty
**Problem**: No personalization based on mastery level; Fellows mature at different rates

**Recommendation**:

```python
class AdaptiveLearningEngine:
    """Adjust content difficulty based on performance"""
    
    DIFFICULTY_LEVELS = {
        'novice': 1,
        'intermediate': 2,
        'advanced': 3,
        'mastery': 4
    }
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.mastery_scores = {}  # {topic: score}
    
    def assess_mastery(self, topic: str, submission: str, 
                       ai_evaluation: dict) -> float:
        """
        Score submissions on a 0-1 scale
        0.0 - 0.3: Needs significant improvement (novice)
        0.3 - 0.6: On track but incomplete (intermediate)
        0.6 - 0.85: Competent (advanced)
        0.85+ : Mastery (expert)
        """
        return ai_evaluation.get('mastery_score', 0.5)
    
    def get_next_challenge(self, topic: str, current_score: float) -> dict:
        """Generate next exercise at appropriate difficulty"""
        if current_score < 0.3:
            return self._scaffold_foundational(topic)
        elif current_score < 0.6:
            return self._add_real_world_complexity(topic)
        elif current_score < 0.85:
            return self._introduce_advanced_considerations(topic)
        else:
            return self._challenge_with_edge_cases(topic)
    
    def _scaffold_foundational(self, topic: str) -> dict:
        """Novice level: guided, structured problems"""
        return {
            'difficulty': 'novice',
            'guidance_level': 'high',
            'scenario': self._generate_simple_case(topic),
            'hints': True
        }
    
    def _add_real_world_complexity(self, topic: str) -> dict:
        """Intermediate: realistic constraints and tradeoffs"""
        return {
            'difficulty': 'intermediate',
            'guidance_level': 'medium',
            'scenario': self._generate_realistic_case(topic),
            'hints': False
        }
    
    def _introduce_advanced_considerations(self, topic: str) -> dict:
        """Advanced: multi-stakeholder, resource constraints"""
        return {
            'difficulty': 'advanced',
            'guidance_level': 'low',
            'scenario': self._generate_complex_case(topic),
            'stretch_goal': True
        }
    
    def _challenge_with_edge_cases(self, topic: str) -> dict:
        """Mastery: edge cases, rare presentations"""
        return {
            'difficulty': 'mastery',
            'guidance_level': 'minimal',
            'scenario': self._generate_edge_case(topic),
            'requires_justification': True
        }

@app.route('/api/learning/next-challenge', methods=['POST'])
def get_adaptive_challenge():
    """Recommend next learning activity based on mastery"""
    data = request.json
    user_id = data.get('user_id')
    topic = data.get('topic')
    
    engine = AdaptiveLearningEngine(user_id)
    current_score = engine.mastery_scores.get(topic, 0.3)
    
    next_challenge = engine.get_next_challenge(topic, current_score)
    return jsonify(next_challenge)
```

**Why**: 
- Prevents cognitive overload (scaffolds down if struggling)
- Prevents boredom (challenges up if mastering)
- Increases retention through productive struggle

---

#### **NICE-TO-HAVE: Add Formative Assessment & Rubric-Based Scoring**

**Current State**: Feedback is narrative; no structured rubric
**Recommendation**:

```python
class RubricScoringEngine:
    """Structured evaluation using competency rubrics"""
    
    RUBRICS = {
        'business_case': {
            'roi_analysis': {
                'weight': 0.25,
                'criteria': {
                    'novice': 'No ROI mentioned',
                    'developing': 'Incomplete ROI calculations',
                    'proficient': 'Clear ROI with cost/benefit analysis',
                    'advanced': 'ROI includes sensitivity analysis & implementation costs'
                }
            },
            'stakeholder_engagement': {
                'weight': 0.25,
                'criteria': {
                    'novice': 'No stakeholders identified',
                    'developing': 'Some stakeholders mentioned',
                    'proficient': 'Key stakeholders identified with engagement strategy',
                    'advanced': 'Addresses resistance & includes buy-in strategy'
                }
            },
            'data_driven': {
                'weight': 0.25,
                'criteria': {
                    'novice': 'No data',
                    'developing': 'Generic statistics',
                    'proficient': 'Institutional data cited',
                    'advanced': 'Benchmarked against national/regional data'
                }
            },
            'implementation': {
                'weight': 0.25,
                'criteria': {
                    'novice': 'No plan',
                    'developing': 'Vague timeline',
                    'proficient': 'Clear timeline & responsible parties',
                    'advanced': 'Includes QI methodology & contingency planning'
                }
            }
        }
    }
    
    @staticmethod
    def evaluate_submission(module_id: str, submission: str, 
                           ai_feedback: dict) -> dict:
        """Generate structured rubric score"""
        rubric = RubricScoringEngine.RUBRICS.get(module_id)
        if not rubric:
            return {'score': 0.5, 'feedback': ai_feedback}
        
        scores = {}
        total_weighted_score = 0
        
        for criterion, details in rubric.items():
            # Use AI to evaluate against rubric
            criterion_score = RubricScoringEngine._score_criterion(
                criterion, submission, ai_feedback
            )
            scores[criterion] = {
                'score': criterion_score,
                'weight': details['weight'],
                'feedback': ai_feedback.get(criterion, '')
            }
            total_weighted_score += criterion_score * details['weight']
        
        return {
            'overall_score': total_weighted_score,
            'rubric_breakdown': scores,
            'level': RubricScoringEngine._map_to_level(total_weighted_score)
        }
    
    @staticmethod
    def _map_to_level(score: float) -> str:
        if score < 0.3:
            return 'novice'
        elif score < 0.6:
            return 'developing'
        elif score < 0.85:
            return 'proficient'
        else:
            return 'advanced'
```

**Why**: Provides transparent, standards-based feedback; supports reproducibility and certification.

---

#### **NICE-TO-HAVE: Add Citation Quality Filtering**

**Current State**: All PubMedBERT results treated equally
**Recommendation**:

```python
class CitationQualityFilter:
    """Filter and prioritize sources by evidence hierarchy"""
    
    EVIDENCE_HIERARCHY = {
        'systematic_review': 5,
        'meta_analysis': 5,
        'randomized_trial': 4,
        'prospective_cohort': 3,
        'retrospective_cohort': 2,
        'case_series': 1,
        'expert_opinion': 0
    }
    
    @staticmethod
    def rank_citations(citations: List[Dict]) -> List[Dict]:
        """Sort by evidence quality then recency"""
        def citation_score(cite):
            # Extract study type from title/abstract
            study_type = CitationQualityFilter._detect_study_type(cite)
            hierarchy_rank = CitationQualityFilter.EVIDENCE_HIERARCHY.get(
                study_type, 0
            )
            
            # Recent papers weighted higher (up to 5 years)
            years_old = datetime.now().year - cite.get('year', 2000)
            recency_bonus = max(0, (5 - years_old) * 0.1)
            
            return hierarchy_rank + recency_bonus
        
        return sorted(citations, key=citation_score, reverse=True)
    
    @staticmethod
    def _detect_study_type(citation: dict) -> str:
        """Infer study type from title/abstract"""
        title_lower = (citation.get('title', '') + 
                      citation.get('abstract', '')).lower()
        
        if 'systematic review' in title_lower or 'meta-analysis' in title_lower:
            return 'systematic_review'
        elif 'randomized' in title_lower or 'rct' in title_lower:
            return 'randomized_trial'
        elif 'prospective' in title_lower:
            return 'prospective_cohort'
        # ... etc
        return 'expert_opinion'
```

**Why**: Medical learners must understand evidence hierarchy; filtering improves credibility.

---

#### **TECHNICAL DEBT: Improve Error Handling & Observability**

```python
import logging
from functools import wraps

# Set up structured logging
logging.basicConfig(
    format='%(timestamp)s - %(level)s - %(user_id)s - %(endpoint)s - %(message)s'
)
logger = logging.getLogger(__name__)

def track_request(f):
    """Decorator for request tracking & error handling"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Request started", extra={
                'request_id': request_id,
                'endpoint': request.endpoint
            })
            
            result = f(*args, **kwargs)
            
            duration = time.time() - start_time
            logger.info(f"Request completed", extra={
                'request_id': request_id,
                'duration_ms': duration * 1000,
                'status': 'success'
            })
            
            return result
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", extra={
                'request_id': request_id,
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc()
            })
            
            return jsonify({
                'error': 'Internal server error',
                'request_id': request_id
            }), 500
    
    return wrapper
```

---

### Summary of Enhancement Priorities

| Priority | Feature | Impact | Effort |
|----------|---------|--------|--------|
| **CRITICAL** | Session management & user progress tracking | Enables adaptive learning | Medium |
| **CRITICAL** | Multi-turn conversation context | Enables scaffolded learning | Medium |
| **HIGH** | Adaptive difficulty adjustment | Improves retention & engagement | High |
| **HIGH** | Rubric-based scoring | Ensures standards alignment | Medium |
| **MEDIUM** | Citation quality filtering | Improves evidence literacy | Low |
| **MEDIUM** | Structured logging | Supports analytics & debugging | Low |

---

## PART 2: ADVANCED CURRICULUM FRAMEWORK

Based on **Table 1** from the manuscript, here's a detailed outline for building AI teaching modules:

### TIER 1: FOUNDATIONAL COMPETENCIES (Existing IDSA CAS, your agents should reference)

**Your agent should NOT try to replicate these** - instead, reference and build upon them:
- Antibiotic spectrum of activity
- Pharmacology & adverse effects
- Resistance mechanisms
- Microbiology basics
- Core ASP intervention concepts

---

### TIER 2: ADVANCED LEADERSHIP & IMPLEMENTATION (Where your AI Agent adds most value)

---

## **Module 1: Leadership & Program Management**

### Competency: Quality Improvement & Implementation Science

**Learning Objectives**:
- Understand Plan-Do-Study-Act (PDSA) cycles
- Design and implement ASP quality improvement projects
- Measure process and outcome metrics
- Identify barriers to implementation

**Recommended AI Teaching Approach**:

```python
class QIModuleAI:
    """Module 1a: Quality Improvement Fundamentals"""
    
    SYSTEM_PROMPT = """You are a quality improvement coach for ASP initiatives.
    Your role is to help ID fellows design, implement, and evaluate stewardship 
    interventions using proven methodologies like PDSA cycles and lean thinking.
    
    Reference frameworks:
    - Institute for Healthcare Improvement (IHI) PDSA methodology
    - Lean methodology for healthcare
    - Six Sigma quality frameworks
    - Change management theory (Kotter, Rogers)
    
    For each coaching interaction:
    1. Diagnose the fellow's current understanding
    2. Present a concrete, real-world ASP case study
    3. Guide them through defining SMART goals
    4. Help them design metrics (process, outcome, balancing)
    5. Support their implementation planning
    6. Review against IHI framework for rigor
    
    Provide increasingly complex scenarios as they demonstrate mastery.
    """
    
    # SCENARIO PROGRESSION
    SCENARIOS = [
        {
            "difficulty": "novice",
            "title": "Reducing Vancomycin Days of Therapy",
            "context": """
            Your hospital reports vancomycin DOT of 45 per 1000 patient-days 
            (benchmark: 18). You want to implement an intervention to reduce it.
            
            What is your SMART goal for this project? What metrics would you track?
            """,
            "expected_components": [
                "SMART goal (Specific, Measurable, Achievable, Relevant, Time-bound)",
                "Process metric (e.g., % patients receiving ASP review)",
                "Outcome metric (e.g., DOT reduction)",
                "Balancing metric (e.g., adverse outcomes, treatment failures)"
            ]
        },
        {
            "difficulty": "intermediate",
            "title": "Multi-Department Fluoroquinolone De-escalation Program",
            "context": """
            Your institution has high fluoroquinolone use across surgical, medical, 
            and pediatric units. Each department has different stewardship champions 
            and varying engagement levels.
            
            Design a PDSA cycle that starts small and spreads. How would you adapt 
            your approach for resistant departments?
            """,
            "expected_components": [
                "Identified small-scale testing opportunity",
                "Plan for rapid cycle feedback",
                "Strategies for department-specific barriers",
                "Spread/scale-up plan if successful"
            ]
        },
        {
            "difficulty": "advanced",
            "title": "System-Wide Antimicrobial Shortage Response",
            "context": """
            Your organization just learned that meropenem supplies will be limited 
            for 6 months. Demand currently exceeds supply by 30%. You must design 
            a system-wide response that maintains patient safety while conserving supply.
            
            This requires coordination across multiple departments, specialty input, 
            and frequent re-evaluation. Design your implementation strategy.
            """,
            "expected_components": [
                "Clear governance & decision-making framework",
                "Rapid assessment of current meropenem use patterns",
                "Stakeholder engagement plan",
                "Alternative therapy protocols",
                "Daily monitoring & adjustment protocol"
            ]
        }
    ]
    
    @staticmethod
    def generate_feedback(submission: str, scenario_difficulty: str) -> dict:
        """Evaluate QI project design"""
        
        system_context = QIModuleAI.SYSTEM_PROMPT
        
        evaluation_prompt = f"""
        A fellow submitted this QI project proposal:
        {submission}
        
        Evaluate against these criteria:
        1. **SMART Goal Clarity**: Is the goal specific, measurable, achievable, 
           relevant, and time-bound?
        2. **Metric Selection**: Are they tracking the right process, outcome, and 
           balancing metrics?
        3. **Plan Rigor**: Does the PDSA cycle have clear Do/Study/Act phases?
        4. **Stakeholder Thinking**: Have they considered different stakeholder 
           needs and barriers?
        5. **Data Strategy**: How will they collect and analyze data rapidly?
        
        Provide:
        - Overall mastery score (0-1)
        - Strengths and gaps for each criterion
        - Specific examples of how to strengthen their approach
        - Follow-up questions to deepen their thinking
        """
        
        # Call Claude or Gemini
        response = call_ai_model(system_context, evaluation_prompt)
        
        return {
            'feedback': response,
            'mastery_score': extract_mastery_score(response),
            'next_challenge': QIModuleAI.SCENARIOS[
                min(len(QIModuleAI.SCENARIOS)-1, 
                    {'novice': 1, 'intermediate': 2, 'advanced': 3}
                    .get(scenario_difficulty, 1))
            ]
        }
```

**Citation Strategy**:
- PubMed search: "PDSA healthcare" OR "quality improvement antimicrobial" OR "implementation science ASP"
- Key references: IHI PDSA toolkit, ISMP guidelines, local success stories

---

## **Module 2: Data Analytics & Interpretation**

### Competency: Calculating, Interpreting, and Presenting Antimicrobial Use Metrics

**Learning Objectives**:
- Calculate Days of Therapy (DOT), Therapy Duration Ratio, and other metrics
- Benchmark institutional data against national standards (SHARPS, PHIS)
- Interpret time-series trends and identify stewardship targets
- Present data effectively to diverse audiences (clinicians vs. C-suite)

**Recommended AI Teaching Approach**:

```python
class DataAnalyticsModuleAI:
    """Module 2: Data Analytics & Stewardship Dashboards"""
    
    SYSTEM_PROMPT = """You are a data analytics coach for antimicrobial stewardship.
    Your role is to help ID fellows understand how to measure, analyze, and 
    interpret institutional antimicrobial use patterns.
    
    Key frameworks:
    - DOT (Days of Therapy) calculations
    - Antimicrobial use indices (per 1000 patient-days)
    - Benchmarking methodology
    - Time-series analysis for trend detection
    - Data visualization for different audiences
    
    Reference tools:
    - DASON ASAP (antimicrobial use metrics dashboard)
    - SHARPS collaborative data portal
    - PHIS antimicrobial benchmarking
    """
    
    # GRADUATED COMPLEXITY DATA SETS
    DATASETS = [
        {
            "difficulty": "novice",
            "title": "Calculate DOT for a Simple Case",
            "data": {
                "scenarios": [
                    {
                        "patient": "6yo with UTI",
                        "antibiotic": "Cephalexin",
                        "dose": "25mg/kg/dose",
                        "frequency": "4x daily",
                        "duration_days": 7,
                        "weight_kg": 20,
                        "question": "Calculate DOT for this patient"
                    },
                    {
                        "patient": "14yo with PNA",
                        "antibiotic": "Azithromycin",
                        "dose": "10mg/kg on day 1, then 5mg/kg daily",
                        "duration_days": 5,
                        "weight_kg": 50,
                        "question": "Calculate total DOT"
                    }
                ]
            }
        },
        {
            "difficulty": "intermediate",
            "title": "Analyze Department-Level Trends",
            "data": {
                "department": "General Pediatrics",
                "month_over_month_dot": [
                    {"month": "Jan", "dot_per_1000pd": 45, "admission_count": 150},
                    {"month": "Feb", "dot_per_1000pd": 48, "admission_count": 155},
                    {"month": "Mar", "dot_per_1000pd": 52, "admission_count": 145},
                    {"month": "Apr", "dot_per_1000pd": 55, "admission_count": 148},
                    {"month": "May", "dot_per_1000pd": 50, "admission_count": 142},
                    {"month": "Jun", "dot_per_1000pd": 45, "admission_count": 150}
                ],
                "question": """
                Your program implemented a de-escalation protocol in March. 
                What trend do you observe? How would you interpret the increase 
                in April? What factors might explain the June decrease?
                """
            }
        },
        {
            "difficulty": "advanced",
            "title": "Multi-Factor Benchmarking & Strategic Planning",
            "data": {
                "institution_metrics": {
                    "total_dot_1000pd": 42,
                    "vancomycin_dot_1000pd": 18,
                    "fluoroquinolone_dot_1000pd": 12,
                    "3rd_gen_cephalosporin_dot_1000pd": 15,
                    "community": "Urban Academic Medical Center"
                },
                "national_benchmarks": {
                    "sharps_median_dot_1000pd": 38,
                    "sharps_25th_percentile": 32,
                    "sharps_75th_percentile": 48
                },
                "question": """
                Your data shows you're near the 50th percentile nationally. 
                The board wants to know: (1) Are we doing well? (2) Where should 
                we focus next? (3) How do we communicate this to clinicians?
                
                Prepare a brief analysis including which drug class to target, 
                how you'd frame the message for frontline clinicians vs. leadership, 
                and your proposed ROI for a new intervention.
                """
            }
        }
    ]
    
    @staticmethod
    def evaluate_data_analysis(submission: str, dataset_type: str) -> dict:
        """Evaluate data interpretation & communication"""
        
        evaluation_prompt = f"""
        A fellow submitted this data analysis:
        {submission}
        
        Evaluate on:
        1. **Accuracy**: Are calculations correct? Do interpretations follow logically?
        2. **Insight**: Do they identify key drivers and opportunities?
        3. **Communication**: Is this suitable for the intended audience?
        4. **Benchmarking**: Do they understand local vs. national context?
        5. **Actionability**: Does this lead to clear stewardship decisions?
        
        Provide:
        - Mastery score
        - Calculation verification (show your work)
        - Interpretation feedback (what they missed or misunderstood)
        - Example of how to present this to different audiences
        """
        
        response = call_ai_model("", evaluation_prompt)
        return {
            'feedback': response,
            'mastery_score': extract_mastery_score(response),
            'follow_up': DataAnalyticsModuleAI._generate_follow_up(
                dataset_type, submission
            )
        }
```

**Citation Strategy**:
- "antimicrobial use metrics" OR "Days of Therapy" OR "DOT calculation"
- "antimicrobial stewardship benchmarking" OR "SHARPS collaborative"
- "healthcare quality metrics communication"

---

## **Module 3: Behavioral Science & Communication**

### Competency: Understanding Cognitive Biases and Implementing Behavior Change Interventions

**Learning Objectives**:
- Identify cognitive biases affecting prescriber behavior (commission bias, omission bias, availability heuristic)
- Apply behavior change theories (Social Cognitive Theory, Transtheoretical Model)
- Use evidence-based communication techniques (Motivational Interviewing, Academic Detailing)
- Design targeted interventions for resistant prescriber populations

**Recommended AI Teaching Approach**:

```python
class BehavioralScienceModuleAI:
    """Module 3: Behavioral Science & Prescriber Communication"""
    
    SYSTEM_PROMPT = """You are a behavioral science coach specializing in 
    prescriber behavior change for antimicrobial stewardship.
    
    Your expertise includes:
    - Cognitive biases in medical decision-making
    - Behavior change theories (Fogg Behavior Model, Social Cognitive Theory)
    - Motivational Interviewing techniques
    - Academic Detailing methods
    - Diffusion of innovations theory
    - Social determinants of prescribing
    
    Your goal is to help fellows understand WHY prescribers make choices,
    and HOW to structure interventions that work with human psychology
    rather than against it.
    """
    
    # PRESCRIBER ARCHETYPES
    ARCHETYPES = [
        {
            "name": "The Tradition-Bound Surgeon",
            "difficulty": "novice",
            "profile": """
            Dr. Collins has been performing the same surgical protocols 
            for 25 years with excellent outcomes. He's suspicious of 
            "cookbook medicine" and believes broad-spectrum antibiotics 
            are safer. He rarely reads guideline updates.
            """,
            "likely_biases": [
                "Status quo bias - 'If it's not broken, don't fix it'",
                "Confirmation bias - only seeks information confirming his approach",
                "Commission bias risk - fears complications from de-escalation"
            ],
            "communication_challenge": """
            Dr. Collins just told you: "I've had excellent outcomes 
            with IV vanc + gentamicin for 3 days perioperatively. 
            Why would I change?"
            
            How would you respond? Use Motivational Interviewing techniques 
            to explore his concerns without dismissing his experience.
            """
        },
        {
            "name": "The Overwhelmed Resident",
            "difficulty": "intermediate",
            "profile": """
            Dr. Patel is a second-year resident running a busy ward 
            with 20+ patients. She prescribes antibiotics quickly without 
            always checking susceptibilities or considering narrowing. 
            She agrees with stewardship concepts but feels pressured by 
            time constraints and fear of missing sepsis.
            """,
            "likely_biases": [
                "Cognitive load bias - overwhelmed, uses mental shortcuts",
                "Availability heuristic - remembers bad outcomes more than good ones",
                "False consensus - thinks everyone prescribes broadly"
            ],
            "communication_challenge": """
            You propose a workflow change: she must perform a 48-hour 
            ASP review of all broad-spectrum antibiotics instead of 
            you doing it unilaterally.
            
            She says: "I don't have time for that. I'm barely keeping up."
            
            Design an intervention that reduces HER cognitive load 
            while improving stewardship. What needs to change in the 
            workflow, not just the prescriber's mindset?
            """
        },
        {
            "name": "The Data-Driven Skeptic",
            "difficulty": "advanced",
            "profile": """
            Dr. Kim is a critical care intensivist who prescribes 
            thoughtfully but feels the ASP is imposing arbitrary 
            restrictions without understanding complex ICU pharmacokinetics. 
            She's respected but can be dismissive of ASP recommendations, 
            and other providers follow her lead.
            """,
            "likely_biases": [
                "Belief perseverance - holds onto her clinical judgment",
                "Authority bias - others follow her (both good and bad habits)",
                "In-group bias - 'My specialty is different from Med-Peds'"
            ],
            "communication_challenge": """
            You want to propose an ICU-specific ASP stewardship track. 
            Dr. Kim has indicated she'll participate but is cautious. 
            You have one meeting to pitch her leadership role in design.
            
            How do you frame this to leverage her expertise while 
            aligning her with stewardship goals? What barriers do you anticipate?
            """
        }
    ]
    
    # COMMUNICATION STRATEGY GUIDE
    COMMUNICATION_STRATEGIES = {
        "academic_detailing": {
            "description": "One-on-one education using peer-reviewed evidence",
            "when_to_use": "For individual prescribers, especially opinion leaders",
            "key_elements": [
                "Build rapport and credibility",
                "Identify specific prescribing pattern",
                "Present peer-reviewed evidence",
                "Use visual aids for data",
                "Address barriers to change",
                "Specific, achievable action steps",
                "Follow-up and reinforcement"
            ],
            "ai_coaching": """
            You're about to do academic detailing with Dr. Collins about 
            de-escalation. You have 15 minutes.
            
            I'll role-play as Dr. Collins. You lead the conversation.
            Remember: You're his colleague, not his boss.
            """
        },
        "motivational_interviewing": {
            "description": "Eliciting change talk through open-ended questions",
            "when_to_use": "When prescriber is resistant or ambivalent",
            "key_elements": [
                "Open-ended questions (avoid yes/no)",
                "Affirmations (recognize their perspective)",
                "Reflective listening",
                "Summarizing (link to change talk)",
                "Explore discrepancy between values and behavior"
            ],
            "ai_coaching": """
            Dr. Patel says she doesn't have time for ASP reviews.
            
            You respond with a question that explores her actual workload 
            and identifies where time IS being spent. This isn't judgmental—
            you're genuinely curious about HER experience.
            
            I'll continue as Dr. Patel. What do you ask?
            """
        }
    }
    
    @staticmethod
    def evaluate_communication_strategy(submission: str, 
                                       archetype_name: str) -> dict:
        """Evaluate how well fellow understood behavioral drivers"""
        
        evaluation_prompt = f"""
        A fellow is addressing {archetype_name}.
        
        Their proposed communication strategy:
        {submission}
        
        Evaluate on:
        1. **Bias Recognition**: Do they identify the cognitive biases at play?
        2. **Empathy**: Do they understand this prescriber's constraints?
        3. **Technique Selection**: Is their communication technique appropriate?
        4. **Messaging**: Is the content evidence-based and accessible?
        5. **Anticipating Pushback**: Have they thought about barriers?
        
        Provide:
        - Mastery score
        - Strengths and gaps
        - More sophisticated framing if needed
        - Role-play scenario to practice
        """
        
        response = call_ai_model("", evaluation_prompt)
        
        # Offer role-play practice
        return {
            'feedback': response,
            'mastery_score': extract_mastery_score(response),
            'offer_roleplay': True,
            'roleplay_prompt': BehavioralScienceModuleAI._generate_roleplay_setup(
                archetype_name, submission
            )
        }
```

**Citation Strategy**:
- "cognitive bias prescribing" OR "decision-making antibiotics"
- "motivational interviewing health" OR "behavior change medicine"
- "academic detailing antimicrobial"
- "prescriber behavior stewardship"

---

## **Module 4: Advanced Clinical Interventions**

### Competency: Designing and Implementing Antibiotic Timeouts, Allergy De-labeling, and Shortage Responses

**Learning Objectives**:
- Design and pilot antibiotic timeout protocols
- Conduct comprehensive penicillin allergy assessments and delabeling
- Develop institutional responses to antimicrobial shortages
- Evaluate intervention efficacy and patient safety

**Recommended AI Teaching Approach**:

```python
class AdvancedInterventionsModuleAI:
    """Module 4: Advanced Clinical Interventions"""
    
    CASES = {
        "antibiotic_timeout": {
            "difficulty": "novice",
            "title": "Design an Antibiotic Timeout Protocol",
            "case": """
            Your PICU uses broad-spectrum antibiotics liberally. You want to 
            implement a 48-hour timeout at which point all broadspectrum 
            antibiotics must be reviewed and either continued with justification 
            or de-escalated.
            
            Design the protocol:
            - Who conducts the review?
            - What information do they need?
            - What's the escalation path if provider disagrees?
            - How do you measure success?
            """,
            "success_criteria": [
                "Defined roles and responsibilities",
                "Clear clinical decision rules",
                "Process for handling disagreements",
                "Measurable endpoints"
            ]
        },
        "penicillin_allergy": {
            "difficulty": "intermediate",
            "title": "Penicillin Allergy De-labeling Program",
            "case": """
            Your medical records show 30% of pediatric patients have documented 
            penicillin allergy, but only 5% have true IgE-mediated reactions. 
            Allergy labels drive inappropriate broad-spectrum use.
            
            You want to:
            1. Identify candidates for allergy re-evaluation
            2. Implement a safe de-labeling pathway
            3. Measure impact on antibiotic prescribing
            
            Design your program (consider resources, risk, equity).
            """
        },
        "shortage_response": {
            "difficulty": "advanced",
            "title": "Meropenem Shortage Crisis Response",
            "case": """
            Your system learns that meropenem will be 60% restricted for 6 months. 
            Current use would deplete supply in 2 months.
            
            Design your institutional response including:
            - Governance and decision-making process
            - Rapid assessment of current use
            - Prioritization matrix (who gets priority access?)
            - Alternative therapy protocols
            - Communication plan
            - Daily monitoring and adjustment protocol
            
            Address ethical considerations: How do you ensure equity? 
            How do you handle palliative cases?
            """
        }
    }
```

---

### Citation Integration Strategy for Each Module

For each module, implement a citation-aware prompt:

```python
def build_educational_prompt_with_citations(module_id: str, 
                                            submission: str,
                                            citations: List[Dict]) -> str:
    """Build system prompt that references actual literature"""
    
    # Filter citations by relevance to module
    relevant_citations = citation_quality_filter(module_id, citations)
    
    # Build "evidence landscape" section
    evidence_section = ""
    if relevant_citations:
        evidence_section = f"""
        Recent evidence in this area includes:
        {json.dumps(relevant_citations, indent=2)}
        
        Reference these in your feedback when relevant.
        """
    
    system_prompt = f"""
    You are an expert coach in {MODULE_NAMES[module_id]}.
    
    {evidence_section}
    
    When evaluating the fellow's work:
    1. Cite specific evidence that supports or contradicts their approach
    2. Highlight consensus areas and areas of disagreement in literature
    3. Identify where they're on the cutting edge vs. established practice
    4. Point out emerging evidence that challenges traditional approaches
    """
    
    return system_prompt
```

---

## PART 3: IMPLEMENTATION ROADMAP

### **Phase 1: Foundation (Months 1-2)**

**Deliverables**:
- [ ] Implement session management with `UserSession` class
- [ ] Add multi-turn conversation manager
- [ ] Set up PubMed citation integration
- [ ] Create Module 1 (Business Case) prototype

**Technical Milestones**:
```bash
# Week 1: Session Management
- Implement UserSession class with database persistence
- Add /api/user/progress endpoint
- Build progress dashboard UI

# Week 2: Context Management  
- Implement ConversationManager
- Add /api/chat/multi-turn endpoint
- Test with Module 1 case study

# Week 3-4: Citation Integration & Module 1
- Integrate PubMedBERT via citation_assistant
- Filter & rank citations by evidence hierarchy
- Build Module 1 interactive case
```

### **Phase 2: Enhanced Pedagogy (Months 3-4)**

**Deliverables**:
- [ ] Implement adaptive difficulty engine
- [ ] Create rubric-based scoring
- [ ] Build Module 2 (Data Analytics)
- [ ] Build Module 3 (Behavioral Science)

**Technical Milestones**:
```bash
# Week 1-2: Adaptive Learning
- Build AdaptiveLearningEngine
- Implement spaced repetition scheduling
- Create difficulty escalation logic

# Week 3: Rubric Implementation
- Define rubrics for each module
- Build RubricScoringEngine
- Create rubric visualization UI

# Week 4: Module 2 & 3 Development
- Implement data analysis teaching scenarios
- Create behavioral archetype cases
- Build role-play infrastructure
```

### **Phase 3: Assessment & Analytics (Months 5-6)**

**Deliverables**:
- [ ] Module 4 (Advanced Interventions)
- [ ] Cohort analytics dashboard
- [ ] Certificate of completion framework
- [ ] Peer comparison (anonymized benchmarking)

**Technical Milestones**:
```bash
# Comprehensive curriculum testing
# Pilot with 1-2 fellowship programs
# Collect usage analytics
# Refine based on fellow feedback
```

---

## PART 4: SUGGESTED DATABASE SCHEMA

```sql
-- Users / Sessions
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    institution TEXT,
    role TEXT, -- 'fellow', 'faculty', 'program_director'
    created_at TIMESTAMP,
    last_active TIMESTAMP
);

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    created_at TIMESTAMP,
    last_active TIMESTAMP,
    metadata JSONB -- {module_id, context, etc.}
);

-- Learning Progress
CREATE TABLE module_submissions (
    submission_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    module_id TEXT, -- 'business_case', 'qi_project', etc.
    submission_text TEXT,
    ai_feedback JSONB,
    rubric_scores JSONB,
    mastery_score FLOAT,
    submitted_at TIMESTAMP,
    feedback_received_at TIMESTAMP,
    attempt_number INT
);

CREATE TABLE learning_goals (
    goal_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    module_id TEXT,
    mastery_level TEXT, -- 'novice', 'developing', 'proficient', 'advanced'
    last_attempt TIMESTAMP,
    status TEXT -- 'in_progress', 'mastered', 'needs_review'
);

-- Citations for Curriculum
CREATE TABLE curriculum_citations (
    citation_id UUID PRIMARY KEY,
    module_id TEXT,
    pmid INT,
    title TEXT,
    authors TEXT,
    year INT,
    evidence_level TEXT, -- 'systematic_review', 'rct', 'observational', etc.
    relevance_score FLOAT,
    indexed_at TIMESTAMP
);

-- Conversation History
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    user_id UUID REFERENCES users(user_id),
    module_id TEXT,
    exchanges JSONB, -- [{user: "", assistant: "", sources: []}]
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

-- Cohort Analytics
CREATE TABLE cohort_analytics (
    analytics_id UUID PRIMARY KEY,
    institution TEXT,
    program_year INT,
    module_id TEXT,
    avg_mastery_score FLOAT,
    completion_rate FLOAT,
    avg_attempts INT,
    common_misconceptions JSONB,
    updated_at TIMESTAMP
);
```

---

## CONCLUSION

Your ASP AI Agent represents a sophisticated solution to a critical gap in antimicrobial stewardship education. By combining **hybrid RAG (Retrieval-Augmented Generation)** with **evidence-based pedagogy**, you're positioned to create a scalable national curriculum that:

1. **Addresses the identified gaps** in leadership, data analytics, and behavioral science
2. **Maintains educational rigor** through rubric-based assessment and spaced repetition
3. **Scales across institutions** via cloud infrastructure without requiring local educator time
4. **Personalizes learning** through adaptive difficulty and multi-turn coaching

### Immediate Next Steps:

1. **Review the Phase 1 deliverables** - Start with session management and multi-turn conversations
2. **Set up your database schema** - Data persistence is critical for adaptive learning
3. **Pilot Module 1 (Business Case)** - Validate the framework with a small fellow cohort
4. **Iterate based on feedback** - Each module should improve based on real learner performance

---

### References for Implementation:

- **Adaptive Learning**: VanLehn et al. "Cognitive Tutors in the Classroom" (2011) - Validates spaced repetition + scaffolding
- **Behavioral Change**: Miller & Rollnick "Motivational Interviewing" (3rd ed) - Evidence basis for communication strategies
- **Quality Improvement**: Langley et al. "The Improvement Guide" - IHI PDSA framework
- **Evidence Hierarchies**: Murad et al. "Rating the Quality of Evidence" - GRADEpro methodology

---

**Document prepared**: November 2025  
**For**: Cincinnati Children's Hospital ASP Education Initiative