# ASP AI Agent

AI-powered adaptive educational platform for antimicrobial stewardship fellowship training with support for multiple AI models including Claude, Gemini, and local Ollama models. The system leverages literature-based recommendations through Retrieval-Augmented Generation (RAG) to provide evidence-backed guidance grounded in current ASP research and guidelines.

## 🎯 Project Overview

The ASP AI Agent is a comprehensive educational system designed to train the next generation of antimicrobial stewardship leaders. It features adaptive learning modules, real-time feedback, and evidence-based clinical scenarios addressing critical gaps in ASP education.

### Key Features
- **Hybrid RAG System** - Combines literature mining (PubMed) with expert knowledge retrieval for evidence-backed, pedagogically-sound guidance
- **Adaptive Learning System** - Personalized difficulty adjustment based on performance
- **Multi-Turn Conversations** - Context-aware coaching with up to 50 turns of dialogue
- **Rubric-Based Assessment** - Standardized evaluation across 4 competency domains
- **Continuous Improvement Loop** - Expert validation and user feedback systematically enhance AI performance
- **Equity Analytics** - Real-time monitoring for educational disparities
- **Clinical Modules** - Real-world scenarios from CICU, NICU, and other settings

## 🚀 Quick Start

### Installation (30 seconds)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/haslamdb/asp_ai_agent.git
   cd asp_ai_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set API keys** (choose one or more):
   ```bash
   export ANTHROPIC_API_KEY='your-claude-key-here'
   export GEMINI_API_KEY='your-gemini-key-here'
   # Optional: Install Ollama for local models
   ```

4. **Start the server**:
   ```bash
   ./start_local.sh  # Or: python unified_server.py
   ```

5. **Open interface**: Visit `http://localhost:5001` or 'http://192.168.1.163:8080/cicu_module.html'

## 📂 Project Structure

```
asp_ai_agent/
├── docs/                           # Documentation
│   ├── SETUP.md                   # Detailed setup instructions
│   ├── IMPLEMENTATION_COMPLETE.md # Implementation status
│   ├── CICU_Module_Documentation.md # CICU module details
│   └── ASP_Agent_*.md            # System documentation
│
├── modules/                        # Educational modules
│   ├── cicu_prolonged_antibiotics_module.py
│   ├── module_integration.py
│   └── cicu_module_export.json
│
├── tests/                          # Test suites
│   ├── test_integration.py        # System integration tests
│   └── test_gemma_setup.py       # Model testing
│
├── core_components/                # Core system files
│   ├── unified_server.py          # Main server with all endpoints
│   ├── session_manager.py         # User session management
│   ├── conversation_manager.py    # Multi-turn dialogue handler
│   ├── adaptive_engine.py         # Adaptive learning engine
│   ├── rubric_scorer.py          # Assessment system
│   └── equity_analytics.py       # Disparity monitoring
│
├── interfaces/                     # User interfaces
│   ├── agent_models.html          # Training module interface
│   ├── asp_ai_agent.html         # Chat consultation interface
│   └── index.html                 # Landing page
│
├── api/                           # API endpoints
│   ├── gemini.js                 # Vercel Edge Function
│   └── claude.js                 # Vercel Edge Function
│
├── asp_literature/                # Literature & expert knowledge
│   ├── asp_literature_miner.py   # PubMed mining tool
│   ├── pdfs/                      # Downloaded research papers
│   └── expert_embeddings/         # Expert knowledge ChromaDB (planned)
│
├── data/                          # Data storage
│   ├── asp_sessions.db           # SQLite session database
│   └── next_steps_and_implementation.txt
│
└── config/                        # Configuration
    ├── requirements.txt           # Python dependencies
    ├── vercel.json               # Vercel deployment
    └── start_local.sh            # Local startup script
```

## 🎓 Educational Modules

### Currently Available

#### CICU Prolonged Antibiotics Module
Addresses overuse of meropenem and vancomycin in cardiac ICU settings.
- **Scenarios**: 4 progressive difficulty levels
- **Focus**: Data analysis → Intervention design → Implementation → Sustainability
- **Metrics**: Process, outcome, and balancing measures
- **Documentation**: [CICU Module Guide](./docs/CICU_Module_Documentation.md)

### Coming Soon
- NICU Antibiotic Stewardship
- Surgical Prophylaxis Optimization
- Outpatient Oral Antibiotic Selection
- Others!

## 🔧 Core Components

### Session Management (`session_manager.py`)
- SQLite persistence for user progress
- Demographics and learning history tracking
- Module completion status

### Adaptive Learning Engine (`adaptive_engine.py`)
- Bloom's taxonomy mastery levels
- Performance-based difficulty adjustment
- Personalized learning paths
- Time-to-mastery predictions

### Conversation Manager (`conversation_manager.py`)
- State machine for dialogue flow
- Intent analysis and scaffolding
- Progressive hint system
- Context retention (50 turns)

### Rubric Scorer (`rubric_scorer.py`)
- Standardized assessment criteria
- 5-level scoring (Not Evident → Exemplary)
- Competency-based evaluation
- Progress tracking over time

### Equity Analytics (`equity_analytics.py`)
- Demographic performance analysis
- Disparity detection and severity scoring
- Actionable recommendations
- Dashboard data generation

## 🔄 Continuous Improvement & Feedback Enhancement

The ASP AI Agent implements a comprehensive **4-phase feedback loop** that systematically improves system performance through expert validation and user feedback.

### Hybrid RAG Architecture

The system uses two complementary knowledge sources:

1. **Literature RAG** - Evidence from ASP research papers
   - Indexed PubMed articles on antimicrobial stewardship
   - Semantic search using PubMedBERT embeddings
   - Citation tracking and evidence grading

2. **Expert Knowledge RAG** - Pedagogical expertise from educators
   - Expert corrections of AI feedback
   - Exemplar responses at different mastery levels
   - Teaching patterns and common learner misconceptions
   - Rubric application examples with expert reasoning

### Feedback Enhancement Strategy

#### **Phase 1: Expert Content Validation** (Weeks 1-4)
**Goal**: Ensure clinical accuracy and pedagogical soundness

- **Expert Panel Review** - 2-3 ASP faculty validate scenarios, rubrics, and AI feedback samples
- **Gold Standard Creation** - Experts create exemplar responses at each mastery level
- **Rubric Calibration** - Inter-rater reliability testing (target: κ > 0.70)

**Deliverables**:
- Expert validation scores (target: >4.0/5.0)
- Gold standard response library
- Refined assessment rubrics

#### **Phase 2: Small-Scale Pilot** (Weeks 5-8)
**Goal**: Understand learner interactions and identify improvement areas

- **Pilot Cohort** - 4-6 ID fellows complete modules with comprehensive instrumentation
- **Data Collection**:
  - Engagement metrics (time per scenario, hint usage, drop-off points)
  - Learning outcomes (pre/post knowledge gain, score progression)
  - User satisfaction (feedback helpfulness ratings, qualitative interviews)
- **Expert Review** - Content experts evaluate 20-30 AI-generated feedback samples

**Success Metrics**:
- Completion rate: >75%
- Feedback helpfulness: >80% "helpful" ratings
- Pre/post knowledge gain: >20% improvement
- Expert agreement with AI scoring: <10% discrepancy

#### **Phase 3: Iterative Improvement** (Weeks 9-12)
**Goal**: Data-driven refinement of content and AI performance

**Analysis Activities**:
- Identify drop-off points and revise problematic scenarios
- Correlate hint effectiveness with score improvements
- Analyze AI vs. expert scoring discrepancies
- Extract common learner misconceptions

**AI Enhancement Approaches**:

1. **Prompt Engineering** (Primary - 90% of effort)
   - Incorporate expert correction patterns into system prompts
   - Add concrete examples of desired feedback style
   - Specify expert-validated rubric criteria
   - Include statistical patterns from expert reviews

2. **Expert Knowledge RAG** (Secondary)
   - Index expert corrections for contextual retrieval
   - Build searchable database of teaching patterns
   - Link exemplar responses to similar scenarios
   - Enable AI to reference relevant expert guidance

3. **Output Validation** (Quality Assurance)
   - Verify required sections in feedback
   - Check citation accuracy (PubMed ID validation)
   - Ensure specific references to user responses
   - Validate actionable next steps

**Deliverables**:
- Refined system prompts incorporating expert patterns
- Expert knowledge database with 50+ indexed corrections
- Updated module content addressing common misconceptions
- Validation pipeline for AI output quality

#### **Phase 4: Continuous Improvement Loop** (Ongoing)
**Goal**: Systematic enhancement as the system scales

**In-App Feedback Collection**:
```javascript
// Feedback widget on every AI response
- 👍/👎 helpfulness rating
- Optional detailed comments
- Automatic flagging of low-rated responses for expert review
```

**Regular Review Cycles**:
- **Monthly**: Review flagged unhelpful responses (10-20 samples)
- **Quarterly**: Expert panel review session (50 random samples)
- **Biannually**: Update literature database with new publications

**A/B Testing Framework**:
- Test competing pedagogical approaches (e.g., hint timing, rubric visibility)
- Measure impact on learning outcomes and satisfaction
- Deploy winning variants systematically

**Key Success Metrics**:
| Metric | Target | Current |
|--------|--------|---------|
| Expert validation score | >4.0/5.0 | Baseline in progress |
| Feedback helpfulness | >80% | Pilot phase |
| Expert-AI scoring agreement | <10% discrepancy | Pilot phase |
| Module completion rate | >75% | Pilot phase |
| Pre/post knowledge gain | >20% | Pilot phase |
| User satisfaction | >4.0/5.0 | Pilot phase |

### Implementation Details

**Database Schema** for feedback collection:
```sql
-- User feedback on AI responses
CREATE TABLE user_feedback (
    feedback_id UUID PRIMARY KEY,
    user_id UUID,
    response_id UUID,
    helpful BOOLEAN,
    comments TEXT,
    timestamp TIMESTAMP
);

-- Expert corrections
CREATE TABLE expert_corrections (
    correction_id UUID PRIMARY KEY,
    response_id UUID,
    expert_id UUID,
    original_ai_feedback TEXT,
    corrected_feedback TEXT,
    expert_reasoning TEXT,
    accuracy_rating INT,  -- 1-5
    helpfulness_rating INT,  -- 1-5
    timestamp TIMESTAMP
);

-- Exemplar responses
CREATE TABLE expert_exemplars (
    exemplar_id UUID PRIMARY KEY,
    module_id TEXT,
    scenario_id TEXT,
    mastery_level TEXT,  -- 'emerging', 'proficient', 'exemplary'
    response_text TEXT,
    expert_commentary TEXT,
    competency_scores JSONB,
    timestamp TIMESTAMP
);
```

**For detailed implementation guides, see**:
- [Setting Up the Expert Knowledge RAG System](./docs/Setting%20Up%20the%20Expert%20Knowledge%20RAG%20System.docx)
- [Fine Tuning the Model](./docs/Fine%20Tuning%20the%20Model.docx)
- [Structured Approach for Collecting Feedback](./docs/Structured%20Approach%20for%20Collecting%20Feedback.docx)

## 🚀 API Endpoints

### Core Educational Endpoints
- `POST /api/asp-feedback` - Main ASP feedback with full context
- `POST /api/session/create` - Create persistent user session
- `GET /api/session/current` - Get current session with progress
- `POST /api/conversation/process` - Process multi-turn dialogue
- `GET /api/adaptive/assessment` - Get difficulty recommendations
- `POST /api/rubric/evaluate` - Evaluate with standardized rubrics
- `GET /api/equity/dashboard` - Equity analytics dashboard

### Module-Specific Endpoints
- `POST /api/modules/cicu/interact` - CICU module interaction
- `GET /api/modules/cicu/tracker` - Implementation metrics
- `POST /api/modules/cicu/countermeasure` - Get barrier solutions

## 🤖 AI Model Support

| Model | Best For | Features | Availability |
|-------|----------|----------|--------------|
| **Claude 3.5 Sonnet** | Complex medical reasoning | Best accuracy, nuanced feedback | API key required |
| **Gemini 2.5 Flash** | Fast responses, search | Web search, quick iterations | Free tier available |
| **Gemma2:27b** | Local deployment | Privacy, no API costs | Via Ollama |
| **Llama3.1:70b** | Large local model | High quality, offline | Via Ollama |

## 📊 Testing

Run the comprehensive test suite:

```bash
# Run all integration tests
python tests/test_integration.py

# Test model setup
python tests/test_gemma_setup.py

# Test specific module
python modules/cicu_prolonged_antibiotics_module.py
```

## 📖 Documentation

### System Documentation
- **[Setup Guide](./docs/SETUP.md)** - Complete installation instructions
- **[Implementation Status](./docs/IMPLEMENTATION_COMPLETE.md)** - Current feature status
- **[Executive Summary](./docs/ASP_Agent_Executive_Summary.md)** - Project overview
- **[Visual Workflows](./docs/ASP_Agent_Visual_Workflows.md)** - System architecture
- **[Module Guide](./docs/CICU_Module_Documentation.md)** - CICU module details

### Feedback Enhancement Guides
- **[Expert Knowledge RAG System](./docs/Setting%20Up%20the%20Expert%20Knowledge%20RAG%20System.docx)** - Database schema and implementation for expert knowledge indexing and retrieval
- **[Fine Tuning Strategy](./docs/Fine%20Tuning%20the%20Model.docx)** - Comprehensive guide to prompt engineering, RAG enhancement, and LLM fine-tuning approaches
- **[Feedback Collection Protocol](./docs/Structured%20Approach%20for%20Collecting%20Feedback.docx)** - 4-phase implementation plan with expert review templates and pilot study design

## 🔐 Security & Privacy

- API keys stored as environment variables
- Server-side proxy for credential protection
- SQLite database with user anonymization
- CORS configured for authorized origins
- No PHI/PII in educational scenarios

## 🚀 Deployment

### Local Development
```bash
./start_local.sh  # Starts on port 5001 with auto-reload
```

### Production (Vercel)
```bash
vercel --prod  # Deploy to production
```

See [Setup Guide](./docs/SETUP.md) for detailed deployment instructions.

## 📈 Roadmap

### Core Platform ✅ (Complete)
- Session management with SQLite persistence
- Multi-turn conversation engine (50 turns)
- Adaptive difficulty system
- Rubric-based scoring (4 competencies)
- Equity analytics dashboard
- Literature RAG with PubMedBERT embeddings
- CICU module (4 difficulty levels)

### Expert Content Validation 🚧 (Current - Weeks 1-4)
- Recruit expert panel (2-3 ASP faculty + 1 medical educator)
- Expert review of CICU module scenarios and rubrics
- Collection of gold standard exemplar responses
- Inter-rater reliability testing (target: κ > 0.70)
- Initial AI feedback quality baseline

### Small-Scale Pilot 📅 (Weeks 5-8)
- Recruit 4-6 ID fellows for pilot study
- Comprehensive instrumentation and logging
- Pre/post knowledge assessment
- Semi-structured qualitative interviews
- Expert review of 20-30 AI feedback samples
- Identify drop-off points and usability issues

### Iterative Improvement 🔧 (Weeks 9-12)
- Analyze pilot data (engagement, learning outcomes, satisfaction)
- Implement prompt engineering refinements
- Build Expert Knowledge RAG database (50+ corrections)
- Develop output validation pipeline
- Update module content addressing misconceptions
- A/B testing framework implementation

### Continuous Enhancement Loop 🔄 (Ongoing)
- Deploy in-app feedback collection (👍/👎 ratings)
- Monthly review of flagged responses (10-20 samples)
- Quarterly expert panel reviews (50 random samples)
- Biannual literature database updates
- Systematic A/B testing of pedagogical approaches

### Scale & Research 🎯 (Months 6-12)
- Expand to 2-3 additional fellowship programs
- Develop NICU and surgical prophylaxis modules
- Publish pilot study results
- Optimize performance and infrastructure
- Prepare for national deployment

### National Deployment 🚀 (Year 2+)
- Deploy to 65 pediatric ID fellowship programs
- Integration with national ASP certification
- Multi-institutional research collaboration
- Continuous module expansion
- Long-term outcomes tracking

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Update documentation
5. Submit a pull request

## 📄 License

This project is proprietary and confidential. All rights reserved.

## 🆘 Support

- **Technical Issues**: dbhaslam@gmail.com
- **Module Feedback**: aspfeedback@cchmc.org
- **Setup Help**: See [Setup Guide](./docs/SETUP.md)

---

