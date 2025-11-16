# Expert RAG System Setup Guide

This guide helps you set up and use the Expert Knowledge RAG system for improving AI feedback quality in the ASP AI Agent.

## 📋 Overview

The Expert RAG system implements the **layered improvement strategy** recommended in the documentation:

1. **Prompt Engineering** (90% of effort) ← Primary strategy
2. **RAG Enhancement** - Retrieve expert corrections and exemplars
3. **Output Validation** - Ensure quality (future)
4. **LLM Fine-Tuning** - Only if needed (much later)

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Enhanced Feedback Generator           │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────────┐
│Literature│  │Expert        │
│RAG       │  │Knowledge RAG │
│(Existing)│  │(New)         │
└──────────┘  └──────┬───────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
    ┌────────┐              ┌─────────┐
    │SQLite  │              │ChromaDB │
    │Database│              │Vectors  │
    └────────┘              └─────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/david/projects/asp_ai_agent
pip install -r requirements.txt
```

### 2. Test the System

```bash
# Test Expert Knowledge RAG
python expert_knowledge_rag.py

# Test Enhanced Feedback Generator
python enhanced_feedback_generator.py
```

### 3. Add Your First Expert Knowledge

#### Option A: Create a Sample CSV Template

```bash
python add_expert_knowledge.py template-csv
# This creates: expert_corrections_template.csv
```

Edit the CSV file and then import:

```bash
python add_expert_knowledge.py corrections expert_corrections_template.csv
```

#### Option B: Create a Sample JSON Template

```bash
python add_expert_knowledge.py template-json
# This creates: expert_exemplars_template.json
```

Edit the JSON file and then import:

```bash
python add_expert_knowledge.py exemplars expert_exemplars_template.json
```

## 📁 Files Created

```
asp_ai_agent/
├── expert_knowledge_rag.py          # Core Expert RAG system
├── enhanced_feedback_generator.py   # Hybrid RAG feedback generator
├── add_expert_knowledge.py          # Utility for importing data
├── asp_expert_knowledge.db          # SQLite database (created on first run)
├── asp_literature/
│   └── expert_embeddings/           # ChromaDB vector store (created on first run)
└── requirements.txt                 # Updated with new dependencies
```

## 🎯 Usage Examples

### Example 1: Adding Expert Corrections from CSV

Create a CSV file with expert reviews:

```csv
Timestamp,Expert Name,Module ID,Scenario ID,Difficulty Level,Competency Area,User Response,AI Feedback,Expert Correction,Expert Reasoning,What AI Missed,What AI Did Well
2025-01-16 10:30,Dr. Martinez,cicu_prolonged_antibiotics,cicu_beginner_data_analysis,beginner,data_analysis,We should track DOT,Good approach,Provide the formula: DOT/1000 PD = (total days / patient days) × 1000,Need concrete formulas,Requiring specific formula,Acknowledged direction
```

Import:

```bash
python add_expert_knowledge.py corrections my_expert_reviews.csv
```

### Example 2: Adding Exemplar Responses from JSON

Create a JSON file with exemplar responses:

```json
[
  {
    "module_id": "cicu_prolonged_antibiotics",
    "scenario_id": "cicu_beginner_data_analysis",
    "difficulty_level": "beginner",
    "mastery_level": "exemplary",
    "response_text": "To analyze CICU antibiotic use, I would calculate DOT/1000 patient-days...",
    "expert_commentary": "This demonstrates exemplary data analysis with specific formulas...",
    "what_makes_it_good": ["Provided actual formula", "Calculated numbers"],
    "what_would_improve": ["Could add visualization"],
    "competency_scores": {
      "data_analysis": 5,
      "clinical_decision_making": 4
    },
    "expert_name": "Dr. Martinez"
  }
]
```

Import:

```bash
python add_expert_knowledge.py exemplars my_exemplars.json
```

### Example 3: Generating Enhanced Feedback

```python
from enhanced_feedback_generator import EnhancedFeedbackGenerator

# Initialize
generator = EnhancedFeedbackGenerator()

# Generate feedback
result = generator.generate_feedback(
    module_id='cicu_prolonged_antibiotics',
    scenario_id='cicu_beginner_data_analysis',
    user_response='I would calculate DOT and compare to benchmarks...',
    difficulty_level='beginner',
    use_expert_knowledge=True,
    use_literature=True
)

# Access results
print(f"Expert corrections used: {result['sources']['expert_corrections_used']}")
print(f"Exemplars shown: {result['sources']['exemplars_shown']}")
print(f"Literature citations: {result['sources']['literature_citations']}")
print(f"\nEnhanced prompt:\n{result['enhanced_prompt']}")
```

## 📊 Database Schema

### Expert Corrections Table

```sql
CREATE TABLE expert_corrections (
    correction_id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    difficulty_level TEXT NOT NULL,
    competency_area TEXT NOT NULL,
    user_response TEXT NOT NULL,
    ai_feedback_original TEXT NOT NULL,
    expert_correction TEXT NOT NULL,
    expert_reasoning TEXT,
    expert_name TEXT,
    what_ai_missed TEXT,  -- JSON array
    what_ai_did_well TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Expert Exemplars Table

```sql
CREATE TABLE expert_exemplars (
    exemplar_id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    difficulty_level TEXT NOT NULL,
    mastery_level TEXT NOT NULL,  -- 'emerging', 'developing', 'proficient', 'exemplary'
    response_text TEXT NOT NULL,
    expert_commentary TEXT,
    what_makes_it_good TEXT,  -- JSON array
    what_would_improve TEXT,  -- JSON array
    competency_scores TEXT,  -- JSON object
    expert_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Integration with unified_server.py

To integrate with your existing Flask server, add this endpoint:

```python
from enhanced_feedback_generator import EnhancedFeedbackGenerator

# Initialize (do this once at server startup)
feedback_generator = EnhancedFeedbackGenerator()

@app.route('/api/asp-feedback-enhanced', methods=['POST'])
def generate_enhanced_feedback():
    """Enhanced feedback endpoint using expert knowledge RAG"""
    data = request.json

    try:
        result = feedback_generator.generate_feedback(
            module_id=data.get('module_id', 'cicu_prolonged_antibiotics'),
            scenario_id=data.get('scenario_id', 'cicu_beginner'),
            user_response=data['input'],
            difficulty_level=data.get('level', 'beginner'),
            use_expert_knowledge=True,
            use_literature=True
        )

        return jsonify({
            'success': True,
            'response': result['feedback'],
            'enhanced_prompt': result['enhanced_prompt'],
            'sources': result['sources'],
            'metadata': result['metadata']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## 📈 Recommended Workflow

### Phase 1: Expert Content Validation (Weeks 1-4)

1. **Recruit 2-3 expert reviewers**
   - ASP faculty with different perspectives
   - Medical educators
   - Behavioral scientists

2. **Collect initial expert corrections**
   - Have experts review 20-30 AI-generated feedback samples
   - Use the CSV template for easy collection
   - Import using `add_expert_knowledge.py`

3. **Create gold standard exemplars**
   - Have experts write 2-3 exemplar responses per mastery level
   - Use the JSON template
   - Import into system

### Phase 2: Iterative Improvement (Weeks 5-8)

1. **Test enhanced feedback**
   - Generate feedback with expert knowledge enabled
   - Compare to baseline (without expert knowledge)
   - Measure improvement

2. **Add more expert knowledge**
   - Continue collecting corrections from expert reviews
   - Add more exemplar responses
   - Build up the knowledge base to 50+ entries

3. **Monitor quality metrics**
   - Expert agreement scores
   - Feedback helpfulness ratings
   - Citation accuracy

### Phase 3: Scale (Weeks 9+)

1. **Deploy to pilot users**
   - 4-6 fellows test the system
   - Collect in-app feedback
   - Flag unhelpful responses for expert review

2. **Continuous improvement**
   - Monthly review of flagged responses
   - Add new corrections to knowledge base
   - Refine prompts based on patterns

## 🔍 Monitoring and Debugging

### Check System Statistics

```python
from expert_knowledge_rag import ExpertKnowledgeRAG

rag = ExpertKnowledgeRAG()
stats = rag.get_statistics()
print(f"Corrections: {stats['corrections_count']}")
print(f"Exemplars: {stats['exemplars_count']}")
```

### View Database Contents

```bash
sqlite3 asp_expert_knowledge.db

# List all corrections
SELECT correction_id, expert_name, scenario_id, competency_area
FROM expert_corrections;

# List all exemplars
SELECT exemplar_id, mastery_level, scenario_id
FROM expert_exemplars;
```

### Test Retrieval

```python
from expert_knowledge_rag import ExpertKnowledgeRAG

rag = ExpertKnowledgeRAG()

# Test correction retrieval
corrections = rag.retrieve_corrections(
    scenario_id='cicu_beginner_data_analysis',
    user_response='I would calculate DOT',
    competency_area='data_analysis',
    n_results=3
)

for corr in corrections:
    print(f"Expert: {corr['expert_name']}")
    print(f"What AI missed: {corr['what_ai_missed']}")
    print(f"Correction: {corr['expert_correction'][:100]}...\n")
```

## 🚨 Troubleshooting

### Issue: "No module named 'sentence_transformers'"

```bash
pip install sentence-transformers chromadb
```

### Issue: "Collection is empty" when retrieving

You need to add expert knowledge first:

```bash
python add_expert_knowledge.py template-csv
# Edit the generated CSV file
python add_expert_knowledge.py corrections expert_corrections_template.csv
```

### Issue: Embedding model download is slow

The PubMedBERT model (~1GB) downloads on first use. This is normal and only happens once.

## 📚 Next Steps

1. **Collect your first batch of expert corrections** (20-30 samples)
2. **Create exemplar responses** for key scenarios (2-3 per mastery level)
3. **Test the enhanced feedback generator** with real user responses
4. **Integrate with unified_server.py** using the endpoint example above
5. **Monitor and iterate** - add more corrections as you collect them

## 🔗 Related Documentation

- `docs/Setting Up the Expert Knowledge RAG System.docx` - Detailed PostgreSQL version
- `docs/Fine Tuning the Model.docx` - Fine-tuning strategy (later phase)
- `docs/Structured Approach for Collecting Feedback.docx` - Comprehensive feedback collection plan
- `README.md` - Main project documentation

## 💡 Tips for Success

1. **Start small** - Begin with 10-20 expert corrections to validate the approach
2. **Focus on prompt engineering** - This gives 90% of the benefit before fine-tuning
3. **Use consistent formats** - Follow the CSV/JSON templates exactly
4. **Validate regularly** - Compare enhanced vs. baseline feedback quality
5. **Iterate based on data** - Track which expert corrections have most impact

## 🤝 Contributing Expert Knowledge

If you're an expert contributing corrections or exemplars:

1. Use the CSV template for corrections: `python add_expert_knowledge.py template-csv`
2. Focus on what the AI *missed* or *should have emphasized*
3. Provide specific, actionable feedback in your corrections
4. Include your reasoning to help improve the system
5. Create exemplars that demonstrate different mastery levels

## 📧 Support

For questions or issues:
- Open a GitHub issue
- Email: aspfeedback@cchmc.org or dbhaslam@gmail.com
