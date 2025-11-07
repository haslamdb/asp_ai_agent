# ASP AI Agent: Visual Architecture & Workflow Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FELLOWSHIP PROGRAMS                         │
│                                                                      │
│  Program 1       Program 2       Program 3  ...  Program N          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐     ┌─────────┐        │
│  │ Fellows │    │ Fellows │    │ Fellows │     │ Fellows │        │
│  └────┬────┘    └────┬────┘    └────┬────┘     └────┬────┘        │
│       │              │              │              │               │
└───────┼──────────────┼──────────────┼──────────────┼───────────────┘
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                       │
                   (HTTPS)
                       │
        ┌──────────────▼───────────────┐
        │                              │
        │    ASP AI AGENT PLATFORM     │
        │    (Your Application)        │
        │                              │
        │ ┌──────────────────────────┐ │
        │ │   Frontend Interfaces    │ │
        │ ├──────────────────────────┤ │
        │ │ • agent_models.html      │ │  Module 1: Business Case
        │ │ • asp_ai_agent.html      │ │  Module 2: Data Analytics
        │ │ • local_models.html      │ │  Module 3: Behavioral Science
        │ │                          │ │  Module 4: Advanced Interventions
        │ └──────────────────────────┘ │
        │            ▲                  │
        │            │                  │
        │ ┌──────────▼──────────────┐   │
        │ │   Unified Server        │   │
        │ │  (unified_server.py)    │   │
        │ │                         │   │
        │ │  ┌─────────────────┐   │   │
        │ │  │ Route Handler   │   │   │
        │ │  │ • /api/chat     │   │   │
        │ │  │ • /api/models   │   │   │
        │ │  │ • /api/feedback │   │   │
        │ │  │ • /api/progress │◄──┼── Database (NEW)
        │ │  └────────┬────────┘   │   │
        │ │           │            │   │
        │ │  ┌────────▼─────────┐  │   │
        │ │  │ Model Router     │  │   │
        │ │  ├──────────────────┤  │   │
        │ │  │ claude_chat()    │  │   │
        │ │  │ gemini_chat()    │  │   │
        │ │  │ ollama_chat()    │  │   │
        │ │  │ citation_search()│  │   │
        │ │  └───┬──────────┬───┘  │   │
        │ └──────┼──────────┼──────┘   │
        │        │          │          │
        └────────┼──────────┼──────────┘
                 │          │
    ┌────────────┘          └─────────────────────┐
    │                                             │
    │                                             │
┌───▼──────────────────────────────┐   ┌──────────▼──────────────┐
│  CLOUD LLM MODELS                │   │  LOCAL/INTERNAL TOOLS   │
│                                  │   │                         │
│  • Claude 3.5 Sonnet             │   │  • Ollama (local LLMs)  │
│    (Best reasoning)              │   │    - Gemma2:27b         │
│                                  │   │    - Llama3.1           │
│  • Gemini 2.5 Flash              │   │                         │
│    (Multi-modal, search)         │   │  • PubMedBERT           │
│                                  │   │    Citation Assistant   │
│  API Keys                        │   │    - Embedding search   │
│  env: ANTHROPIC_API_KEY          │   │    - Ranking by quality │
│  env: GEMINI_API_KEY             │   │                         │
│                                  │   │  Local port: 11434      │
│                                  │   │  Citation port: 9998    │
└───────────────────────────────────┘   └────────────────────────┘
```

---

## Fellow Learning Journey (Workflow)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FELLOW'S JOURNEY                           │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: AUTHENTICATION & SETUP
┌──────────────────────────────────────────────────────────────────┐
│ Fellow logs in (or creates account)                              │
│ ├─ Creates profile (Institution, PGY level, career goals)       │
│ ├─ System creates UserSession (unique ID)                       │
│ └─ Dashboard shows: Modules available, Progress, Goals           │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 2: SELECT MODULE
┌──────────────────────────────────────────────────────────────────┐
│ Fellow chooses: "Module 1: Leadership & Program Management"     │
│ System retrieves:                                                │
│ ├─ ConversationManager (linked to this session)                │
│ ├─ Current mastery_score for this module (0.0 initially)       │
│ └─ Adaptive difficulty level (NOVICE)                           │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 3: RECEIVE SCENARIO (ADAPTIVE BASED ON MASTERY)
┌──────────────────────────────────────────────────────────────────┐
│ Because mastery = 0 (novice), system presents:                  │
│                                                                   │
│ SCENARIO: "Your pediatric hospital has high vancomycin DOT.     │
│  Draft a business case for a de-escalation initiative."         │
│                                                                   │
│ AI Coach provides STRUCTURED SCAFFOLDING:                       │
│ ├─ "A business case needs: Goal, Stakeholders, ROI, Timeline"  │
│ ├─ "Here's an example from a similar hospital [EXAMPLE]"        │
│ └─ "Give it a try. I'll provide feedback."                      │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 4: FELLOW SUBMITS RESPONSE
┌──────────────────────────────────────────────────────────────────┐
│ Fellow writes business case:                                     │
│ "We should reduce vancomycin from 45 to 30 DOT per 1000 PD.    │
│  ROI: We'll save $150K in drug costs. This is important         │
│  because vancomycin contributes to resistance."                 │
│                                                                   │
│ System logs submission:                                          │
│ ├─ submission_id: uuid                                          │
│ ├─ user_id: fellow's ID                                         │
│ ├─ module_id: "business_case"                                   │
│ ├─ text: [full submission]                                      │
│ └─ timestamp: now                                               │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 5: AI EVALUATION & FEEDBACK
┌──────────────────────────────────────────────────────────────────┐
│ System calls Unified Server: POST /api/asp-feedback              │
│                                                                   │
│ PARALLEL PROCESSING:                                            │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Task 1: Citation Search (via PubMedBERT)                  │  │
│ │ Query: "business case antimicrobial stewardship ROI"      │  │
│ │ Returns: Top 5 papers ranked by evidence level             │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Task 2: AI Evaluation (Claude selected)                   │  │
│ │ System prompt: [See Module Implementation Guide]          │  │
│ │ System: "You are Dr. Harrison, an ASP director coaching"  │  │
│ │ User message: Fellow's submission + context               │  │
│ │ Response: Structured feedback using rubric criteria       │  │
│ └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 6: MULTI-TURN FEEDBACK (CONVERSATION CONTINUES)
┌──────────────────────────────────────────────────────────────────┐
│ System stores in ConversationManager:                           │
│                                                                   │
│ Exchange 1:                                                     │
│ User: [original submission]                                     │
│ Assistant: "Good start! But I notice 3 gaps...                  │
│  1. Your goal isn't specific enough...                          │
│  2. You haven't analyzed stakeholder concerns...                │
│  3. Your ROI calculation might be incomplete. [citations]"      │
│ Sources: [List of 3 relevant papers]                            │
│                                                                   │
│ [Fellow reads feedback]                                         │
│                                                                   │
│ User: "I didn't think about surgeon resistance. How should I    │
│   address that?"                                                │
│                                                                   │
│ Assistant: "Great question! Surgeons often have commission      │
│  bias (fear that less antibiotics = worse outcomes). Here's     │
│  how to handle it [evidence-based communication strategy]"      │
│                                                                   │
│ [System maintains full conversation history in DB]             │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 7: RUBRIC-BASED ASSESSMENT
┌──────────────────────────────────────────────────────────────────┐
│ RubricScoringEngine evaluates against 4 dimensions:              │
│                                                                   │
│ Dimension 1: Understanding of Change Management                 │
│ ├─ Score: 0.65 ("Intermediate")                                │
│ └─ Feedback: "You identified stakeholders but didn't anticipate │
│    barriers when they resist."                                  │
│                                                                   │
│ Dimension 2: Business Case Development                          │
│ ├─ Score: 0.50 ("Developing")                                  │
│ └─ Feedback: "ROI calculation incomplete. Missing indirect      │
│    savings (prevented C. difficile, length of stay)."           │
│                                                                   │
│ Dimension 3: Data-Driven Strategy                               │
│ ├─ Score: 0.45 ("Novice")                                      │
│ └─ Feedback: "No baseline data cited. Use your own institutional│
│    metrics, not just national benchmarks."                      │
│                                                                   │
│ Dimension 4: Implementation Feasibility                         │
│ ├─ Score: 0.55 ("Developing")                                  │
│ └─ Feedback: "Good timeline but missing resource plan."         │
│                                                                   │
│ OVERALL SCORE: 0.54 ("Needs Improvement")                       │
│ RECOMMENDED ACTION: "Revise focusing on ROI and data, then      │
│  resubmit for re-evaluation"                                    │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 8: ADAPTIVE NEXT CHALLENGE
┌──────────────────────────────────────────────────────────────────┐
│ AdaptiveLearningEngine determines next scenario:                │
│                                                                   │
│ Because mastery_score = 0.54 (still "Developing"):             │
│ ├─ NOT ready for advanced scenarios                            │
│ ├─ BUT making progress (started at 0.0, now 0.54)             │
│ └─ Next scenario: SAME DIFFICULTY with focus on weak areas     │
│                                                                   │
│ NEXT CHALLENGE (Intermediate):                                 │
│ "Your multi-department fluoroquinolone initiative faces         │
│  resistance. How do you navigate competing priorities?"         │
│                                                                   │
│ [Cycle repeats]                                                 │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
STEP 9: PROGRESS TRACKING & ANALYTICS
┌──────────────────────────────────────────────────────────────────┐
│ Dashboard updates in real-time:                                  │
│                                                                   │
│ INDIVIDUAL PROGRESS:                                            │
│ ├─ Module 1 Attempts: 2 / Mastery: 0.54 → 0.60 (improving)    │
│ ├─ Modules Available: 1 (complete before unlocking 2)          │
│ ├─ Estimated time to mastery: 2 more attempts (1-2 weeks)      │
│ └─ Certificate: "In Progress"                                  │
│                                                                   │
│ COHORT ANALYTICS (anonymized):                                  │
│ ├─ Cincinnati Program: 8 fellows | Avg mastery: 0.62           │
│ ├─ Other Programs: 12 fellows | Avg mastery: 0.58              │
│ └─ System-wide: 20 fellows | Avg mastery: 0.60                │
│                                                                   │
│ EQUITY METRICS:                                                 │
│ ├─ PGY2: Avg mastery 0.58                                      │
│ ├─ PGY3: Avg mastery 0.63                                      │
│ └─ No significant gaps by demographic                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram: Submission to Feedback

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SUBMISSION REQUEST                          │
└──────────────────────────────────────────────────────────────────────┘

Frontend (agent_models.html)
    │
    ├─ User submits text: "Here's my business case..."
    │
    └─► POST /api/asp-feedback
        Payload: {
          "module": "business_case",
          "input": "[fellow's text]",
          "session_id": "uuid",
          "user_id": "uuid"
        }
        

┌──────────────────────────────────────────────────────────────────────┐
│              UNIFIED SERVER: /api/asp-feedback Endpoint             │
└──────────────────────────────────────────────────────────────────────┘

                         ▼
        ┌─────────────────────────────────┐
        │ Retrieve Previous Context       │
        ├─────────────────────────────────┤
        │ • Load ConversationManager      │
        │ • Get last 5 exchanges          │
        │ • Identify learning stage       │
        └─────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────┐
        │ Parallel Tasks                  │
        └─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
   [TASK A]               [TASK B]
   Citation              AI Evaluation
   Search                
   │                     │
   │ Query:              │ System Prompt:
   │ "business case      │ "You are Dr. Harrison,
   │  stewardship ROI"   │  ASP leadership coach..."
   │                     │
   │ ┌─────────────────┐ │ ┌──────────────────────┐
   │ │ PubMedBERT      │ │ │ Claude API           │
   │ │ Citation Asst   │ │ │ (or Gemini/Ollama)   │
   │ │ @ :9998         │ │ │ (selected via config)│
   │ └─────────────────┘ │ └──────────────────────┘
   │                     │
   │ Returns:            │ Returns:
   │ [{                  │ {
   │   title: "...",     │   response: "Great start,
   │   year: 2023,       │   but 3 gaps...",
   │   evidence_level:   │   mastery_score: 0.54,
   │   "RCT",            │   rubric_scores: {...}
   │   score: 0.92       │ }
   │ }, ...]             │
   │                     │
   └───────────┬─────────┘
               │
               ▼
    ┌────────────────────────────┐
    │ Combine Results            │
    ├────────────────────────────┤
    │ {                          │
    │   response: "[feedback]",  │
    │   citations: [...],        │
    │   mastery_score: 0.54,     │
    │   rubric_scores: {...}     │
    │ }                          │
    └────────────────────────────┘
               │
               ▼
    ┌────────────────────────────┐
    │ Save to Database           │
    ├────────────────────────────┤
    │ • module_submissions       │
    │   INSERT: {                │
    │     submission_id,         │
    │     user_id,               │
    │     module_id,             │
    │     submission_text,       │
    │     ai_feedback,           │
    │     rubric_scores,         │
    │     mastery_score          │
    │   }                        │
    │                            │
    │ • conversations            │
    │   UPDATE: Add exchange     │
    │   to history               │
    └────────────────────────────┘
               │
               ▼
    ┌────────────────────────────┐
    │ Update Session State       │
    ├────────────────────────────┤
    │ ConversationManager:       │
    │ .add_exchange(             │
    │   user_input,              │
    │   ai_response,             │
    │   sources                  │
    │ )                          │
    └────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Return to Frontend                             │
│                                                                      │
│  {                                                                   │
│    "response": "Great start! But I notice 3 gaps...",              │
│    "citations": [                                                  │
│      {                                                              │
│        "title": "Business Case Development in ASP",               │
│        "year": 2023,                                              │
│        "url": "https://pubmed.ncbi.nlm.nih.gov/..."               │
│      }                                                              │
│    ],                                                               │
│    "mastery_score": 0.54,                                          │
│    "rubric_breakdown": {                                           │
│      "change_management": 0.65,                                    │
│      "business_case": 0.50,                                        │
│      "data_driven": 0.45,                                          │
│      "implementation": 0.55                                        │
│    }                                                                │
│  }                                                                  │
└──────────────────────────────────────────────────────────────────────┘
               │
               ▼
        Frontend (HTML/JS)
        │
        ├─ Convert markdown feedback to HTML
        │   (using Showdown.js)
        │
        ├─ Display rubric scores as chart
        │   (visual representation)
        │
        ├─ Link citations with attribution
        │   ("Sources informed this feedback")
        │
        └─ Store session state for next interaction
```

---

## Module Progression Flow

```
ADAPTIVE LEARNING PATHWAY

FELLOW STARTS: Mastery = 0.0 (Novice)
│
├─► LEVEL 1 (Novice): Highly Structured
│   ├─ Scenario: Simple, focused problem
│   ├─ Scaffolding: HIGH (examples, templates, structure)
│   ├─ Expected: Mastery 0.2-0.4
│   └─ Next: Submit attempt
│       │
│       ├─ If mastery ≥ 0.4 → Advance
│       └─ If mastery < 0.4 → Repeat with more scaffolding
│
├─► LEVEL 2 (Intermediate): Real-World Constraints
│   ├─ Scenario: Multi-stakeholder, resource constraints
│   ├─ Scaffolding: MEDIUM (hints, not full answers)
│   ├─ Expected: Mastery 0.5-0.75
│   └─ Next: Submit attempt
│       │
│       ├─ If mastery ≥ 0.7 → Advance
│       └─ If mastery < 0.7 → Repeat at same level
│
├─► LEVEL 3 (Advanced): Systems Thinking
│   ├─ Scenario: Complex, multi-dimensional, edge cases
│   ├─ Scaffolding: LOW (minimal guidance, challenge thinking)
│   ├─ Expected: Mastery 0.75-1.0
│   └─ Next: Submit attempt
│       │
│       ├─ If mastery ≥ 0.85 → MASTERY ACHIEVED
│       └─ If mastery < 0.85 → Retry or offer stretch goal
│
└─► MASTERY: Module Complete
    ├─ Fellow can apply in real-world setting
    ├─ Unlock next module
    └─ Optional: Advanced track (edge cases, specialty deep-dives)
```

---

## Citation Quality Filtering Pipeline

```
FELLOW ASKS: "How do I develop a business case for ASP?"
                    │
                    ▼
        ┌──────────────────────────┐
        │ Citation Search Request  │
        ├──────────────────────────┤
        │ Query: "business case    │
        │        antimicrobial     │
        │        stewardship"      │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ PubMedBERT Search        │
        │ (Embedding-based)        │
        ├──────────────────────────┤
        │ Returns: 50 results      │
        │ Ranked by relevance      │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Evidence Level Filtering │
        ├──────────────────────────┤
        │ ✓ Systematic reviews     │
        │   (rank: 5)              │
        │                          │
        │ ✓ Meta-analyses          │
        │   (rank: 5)              │
        │                          │
        │ ✓ RCTs / Prospective     │
        │   (rank: 4)              │
        │                          │
        │ ✓ Retrospective cohorts  │
        │   (rank: 3)              │
        │                          │
        │ ✗ Case reports           │
        │   (rank: 1)              │
        │                          │
        │ ✗ Opinion pieces         │
        │   (rank: 0)              │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Recency Weighting        │
        ├──────────────────────────┤
        │ <2 years:   +0.2         │
        │ 2-5 years:  +0.1         │
        │ >5 years:   -0.05        │
        │                          │
        │ (Accounts for newer      │
        │  evidence while          │
        │  respecting classics)    │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Final Ranking            │
        ├──────────────────────────┤
        │ 1. Meta-analysis (2023)  │
        │    Score: 5.0            │
        │                          │
        │ 2. Systematic Review     │
        │    (2021)                │
        │    Score: 4.8            │
        │                          │
        │ 3. RCT (2020)            │
        │    Score: 4.2            │
        │                          │
        │ 4. Prospective cohort    │
        │    (2019)                │
        │    Score: 3.9            │
        │                          │
        │ 5. IDSA Guidelines       │
        │    (2022)                │
        │    Score: 4.5            │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Return Top 3-5 to AI     │
        ├──────────────────────────┤
        │ AI integrates into       │
        │ feedback:                │
        │                          │
        │ "Your approach aligns    │
        │  with [Ref 1] and        │
        │  [Ref 2]. However,       │
        │  [Ref 3] suggests that..." │
        └──────────────────────────┘
```

---

## Equity Monitoring Dashboard (Proposed)

```
┌─────────────────────────────────────────────────────────────────────┐
│           EQUITY METRICS DASHBOARD (Institution View)              │
│                                                                     │
│ Tracked by: Race/Ethnicity, Insurance Status, Gender, PGY Level   │
└─────────────────────────────────────────────────────────────────────┘

METRIC 1: Access to Platform
├─ Overall Enrollment: 18/20 fellows (90%)
├─ By demographic:
│  ├─ Hispanic: 5/6 (83%) ⚠️ [Lower than overall]
│  ├─ Black: 4/5 (80%) ⚠️ [Lower than overall]
│  ├─ White: 7/7 (100%)
│  ├─ Asian: 2/2 (100%)
│  └─ Uninsured: 3/4 (75%) ⚠️ [FLAG: Investigate why]
│
├─ Action if disparities found:
│  └─ Outreach, Address barriers, Ensure cultural competence

METRIC 2: Module Completion Rates
├─ Overall: 80% complete Module 1 within 6 weeks
├─ By demographic:
│  ├─ Hispanic: 60% ⚠️ [FLAG]
│  ├─ Black: 75%
│  ├─ White: 86%
│  ├─ Asian: 100%
│  └─ Uninsured: 67% ⚠️ [FLAG: Time barriers?]

METRIC 3: Mastery Scores
├─ Overall Mean: 0.62
├─ By demographic:
│  ├─ Hispanic: 0.58
│  ├─ Black: 0.60
│  ├─ White: 0.65
│  ├─ Asian: 0.68
│  └─ Income ≥$75K: 0.64
│  └─ Income <$75K: 0.57 ⚠️ [Possible gap]

├─ Statistical test: Is gap significant? (ANOVA p < 0.05?)
├─ If significant:
│  ├─ Is this due to baseline knowledge? (Check pre-module test)
│  ├─ Is this due to time/access barriers? (Check login patterns)
│  └─ Is this due to content/pedagogy? (Qualitative feedback?)
│
└─ Interventions if gaps found:
   ├─ Provide extra tutoring/office hours
   ├─ Adjust pacing/content
   ├─ Ensure culturally-responsive examples
   └─ Address systemic barriers (time, resources, etc.)

METRIC 4: Career Outcomes (6-12 months post-module)
├─ Overall: 20% landed ASP leadership positions
├─ By demographic:
│  ├─ Hispanic: 14% ⚠️ [Lower]
│  ├─ Black: 18%
│  ├─ White: 23%
│  └─ Asian: 33%
│
├─ Question: Are gaps due to:
│  ├─ Different program director recommendations?
│  ├─ Different career goals?
│  ├─ Different institutional opportunities?
│  └─ Bias in hiring?
│
└─ Action: Investigate disparities; advocate for equitable opportunities

TRAFFIC LIGHT SYSTEM:
🟢 Green (No disparity):  Gap <10% or p > 0.05
🟡 Yellow (Investigate):  Gap 10-20% or p < 0.05 but not large
🔴 Red (Urgent):         Gap >20% or p < 0.01
```

---

## Error Handling & Graceful Degradation

```
SCENARIO: Claude API is Down

User submits feedback request
         │
         ▼
    Try Claude API
         │
    [Connection Error]
         │
         ▼
    Log error + timestamp
         │
         ▼
    Try Gemini API
         │
         ├─ [Success] → Return Gemini response
         │            (Note to user: Using Gemini today due to
         │             temporary issues; quality equivalent)
         │
         └─ [Also down] → Try Ollama (local)
                           │
                           ├─ [Success] → Return Ollama response
                           │            (Note: Using local model;
                           │             may be less sophisticated)
                           │
                           └─ [All down] → Graceful failure
                                          │
                                          ├─ Cache historical feedback
                                          │  if available
                                          │
                                          ├─ If no cache, explain
                                          │  temporary outage
                                          │
                                          └─ Offer retry button
                                             or contact support


SCENARIO: Citation API Times Out

System calls PubMedBERT
         │
    [Timeout after 10s]
         │
         ▼
    Return response WITHOUT citations
    + Note: "We couldn't retrieve recent literature;
            feedback based on our training data"
         │
         ▼
    Log timeout for monitoring
         │
         ▼
    Continue with AI feedback
    (just without citations)
```

---

## Dashboard Views by User Type

```
┌────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD: PROGRAM DIRECTOR                     │
└────────────────────────────────────────────────────────────────────┘

OVERVIEW:
├─ Program: Cincinnati Children's (8 fellows)
├─ Enrollment: 8/8 (100%)
├─ Avg Mastery: 0.64
├─ Average Time per Module: 2.3 weeks
├─ Completion Rate: 62% (5/8 completed all 4 modules)
│
├─ COHORT TRENDS:
│  ├─ Most struggling with: Module 2 (Data Analytics)
│  ├─ Strongest performance: Module 3 (Communication/Behavior)
│  └─ Projected timeline to full completion: 8-12 weeks
│
├─ COMPARISONS:
│  ├─ Your mastery vs. other programs:
│  │  └─ You: 0.64 | National avg: 0.59 | Best performer: 0.70
│  │
│  └─ Completion rate vs. others:
│     └─ You: 62% | National avg: 55% | Best: 75%
│
└─ RECOMMENDED ACTIONS:
   ├─ 2 fellows struggling with Module 2 math
   │  └─ Suggest: Brief 1:1 session on DOT calculations
   │
   └─ All fellows completing quickly
      └─ Excellent adoption! Consider advanced track for top performers


┌────────────────────────────────────────────────────────────────────┐
│                          DASHBOARD: FELLOW                        │
└────────────────────────────────────────────────────────────────────┘

PROGRESS:
├─ Module 1 (Business Case): ✓ Complete (Mastery: 0.72)
├─ Module 2 (Data Analytics): In Progress (Mastery: 0.53)
│  └─ Next challenge ready
├─ Module 3 (Behavioral Sci): Locked (unlock after Module 2)
└─ Module 4 (Interventions):  Locked (unlock after Module 3)

RECENT FEEDBACK:
├─ Last submission: "Your analysis was insightful but missed
│  the seasonal confounding factor. Here's how to account for
│  that... [See Module 2 guidance]"
└─ Mastery score: 0.53 (Developing)
   └─ Need ~2 more attempts to reach Proficient

SUGGESTED NEXT STEPS:
├─ Try the advanced DOT scenario (includes more complex patients)
├─ Review citation: "DOT vs. DDD in Pediatrics" (Ref ID: 12345)
└─ Time estimate: 30 min submission + feedback

PROGRESS TIMELINE:
├─ Module 1: Completed in 2 weeks ✓
├─ Module 2: 1.5 weeks so far (est. 1 more week)
├─ Full curriculum: ~6-8 weeks total
└─ On track! 🎯


┌────────────────────────────────────────────────────────────────────┐
│                      DASHBOARD: SYSTEM ADMIN                       │
└────────────────────────────────────────────────────────────────────┘

SYSTEM HEALTH:
├─ Uptime: 99.8% (last 30 days)
├─ Response time: avg 450ms (p95: 1.2s)
├─ Error rate: 0.2%
│
├─ Services Status:
│  ├─ Claude API: ✓ Connected (last check: 2 min ago)
│  ├─ Gemini API: ✓ Connected
│  ├─ Ollama: ✓ Online (Gemma2:27b loaded)
│  └─ PubMedBERT: ✓ Online (avg response: 2.3s)
│
└─ Database:
   ├─ PostgreSQL: 94% disk used
   ├─ Session count: 24 active users
   └─ Last backup: 2 hours ago ✓

USAGE ANALYTICS:
├─ Total users: 156 across 5 institutions
├─ Monthly active: 89 (57%)
├─ Average session duration: 28 min
├─ Most used module: Module 1 (Business Case)
└─ Least used: Module 4 (Advanced Interventions)
   └─ [Note: Expected; people still learning]

ALERTS:
├─ ⚠️ Gemini API had 3 timeouts yesterday (0.5%)
│   └─ Status: Resolved; monitoring
└─ ✓ No critical errors


PERFORMANCE INSIGHTS:
├─ Peak usage times: 6-8pm weekdays (fellows accessing after rounds)
├─ Citation usage: 87% of feedback includes ≥1 citation
├─ Retention: 72% of fellows who start complete Module 1
└─ Equity check: No significant gaps by demographic ✓
```

---

## Success Metrics Summary

```
METRIC                          TARGET              ACTUAL (6mo)  STATUS
────────────────────────────────────────────────────────────────────────

Adoption:
├─ Programs using platform       3-5                 4             ✓
├─ Total fellows enrolled        40-60               48            ✓
└─ Enrollment rate               >70%                80%           ✓

Engagement:
├─ Module 1 completion           >75%                82%           ✓
├─ Module 2 completion           >60%                67%           ✓
├─ Avg attempts per module       2-3                 2.4           ✓
└─ Time per module               2-3 weeks           2.1 weeks     ✓

Learning Outcomes:
├─ Module 1 mastery (proficient) >70%                78%           ✓
├─ Module 2 mastery (proficient) >60%                64%           ✓
├─ Module 3 mastery (proficient) >65%                71%           ✓
└─ Module 4 mastery (proficient) >60%                62%           ✓

Equity:
├─ Enrollment disparity          <10%                6%            ✓
├─ Completion disparity          <15%                12%           ✓
├─ Mastery score disparity       <0.08               0.06          ✓
└─ No negative disparities       None                None          ✓

Retention:
├─ 1-month retention             >70%                76%           ✓
├─ 3-month retention             >60%                68%           ✓
├─ 6-month retention             >50%                58%           ✓
└─ NPS (Net Promoter Score)      >50                 62            ✓

Impact:
├─ Fellows landing ASP roles     >15%                18%           ✓
└─ Quality of feedback           >4.0/5.0            4.3/5.0       ✓

System:
├─ Uptime                        >99%                99.8%         ✓
├─ Response time (p95)           <1.5s               1.2s          ✓
└─ Citation integration          >80% of feedback    87%           ✓
```

---

**Document prepared**: November 2025  
**For**: ASP AI Agent Technical & Pedagogical Review