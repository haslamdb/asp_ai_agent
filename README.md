# ASP AI Agent

AI-powered adaptive educational platform for antimicrobial stewardship fellowship training with support for multiple AI models including Claude, Gemini, and local Ollama models. The system leverages literature-based recommendations through Retrieval-Augmented Generation (RAG) to provide evidence-backed guidance grounded in current ASP research and guidelines.

## 🎯 Project Overview

The ASP AI Agent is a comprehensive educational system designed to train the next generation of antimicrobial stewardship leaders. It features adaptive learning modules, real-time feedback, and evidence-based clinical scenarios addressing critical gaps in ASP education.

### Key Features
- **Literature-Based Recommendations** - Mines PubMed and retrieves relevant ASP research to provide RAG driven, evidence-backed guidance
- **Adaptive Learning System** - Personalized difficulty adjustment based on performance
- **Multi-Turn Conversations** - Context-aware coaching with up to 50 turns of dialogue
- **Rubric-Based Assessment** - Standardized evaluation across 4 competency domains
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
├── asp_literature/                # Literature mining
│   ├── asp_literature_miner.py   # PubMed mining tool
│   └── pdfs/                      # Downloaded papers
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

- **[Setup Guide](./docs/SETUP.md)** - Complete installation instructions
- **[Implementation Status](./docs/IMPLEMENTATION_COMPLETE.md)** - Current feature status
- **[Executive Summary](./docs/ASP_Agent_Executive_Summary.md)** - Project overview
- **[Visual Workflows](./docs/ASP_Agent_Visual_Workflows.md)** - System architecture
- **[Module Guide](./docs/CICU_Module_Documentation.md)** - CICU module details

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

### Phase 1 ✅ (Complete)
- Session management
- Multi-turn conversations
- Adaptive difficulty
- Rubric scoring
- Equity tracking

### Phase 2 🚧 (Current - 8 weeks)
- Module content creation
- Frontend dashboard development
- Integration testing
- Pilot preparation

### Phase 3 📅 (Planned - 12 weeks)
- Pilot with 2-3 fellowship programs
- Feedback collection and iteration
- Performance optimization
- Scale preparation

### Phase 4 🎯 (Future)
- Deploy to 65 pediatric ID programs
- Continuous improvement
- Research publications
- National ASP certification integration

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

- **Technical Issues**: Open a GitHub issue
- **Module Feedback**: aspfeedback@cchmc.org or dbhaslam@gmail.com
- **Setup Help**: See [Setup Guide](./docs/SETUP.md)

---

