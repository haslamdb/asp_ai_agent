# ASP Literature RAG System

## Overview

The ASP (Antimicrobial Stewardship Program) Literature RAG (Retrieval-Augmented Generation) system provides **evidence-based feedback** by combining:

1. **Local Knowledge Base**: Curated ASP research papers stored as PDFs and indexed with PubMedBERT embeddings
2. **LLM Intelligence**: Gemini/Claude providing pedagogical expertise and broader ASP knowledge

## Architecture

```
User Response
     ↓
[1] Extract key concepts (DOT, interventions, behavioral change, etc.)
     ↓
[2] RAG System: Search indexed literature using PubMedBERT
     ↓
[3] Retrieve 3-5 most relevant paper excerpts with PMID citations
     ↓
[4] Build prompt with: Scenario + User Response + Literature Context + Rubrics
     ↓
[5] Gemini 2.0 Flash: Generate feedback using BOTH literature AND its own knowledge
     ↓
Formatted feedback with evidence-based citations
```

## Key Features

- **Independent**: Self-contained RAG system, not dependent on citation_assistant server
- **Hybrid Knowledge**: Combines curated evidence (RAG) with LLM general knowledge
- **Evidence-Based**: References specific PMIDs when providing guidance
- **Expandable**: Easy to add more PDFs and re-index

## File Structure

```
asp_ai_agent/
├── asp_rag_module.py                # RAG module (search, indexing)
├── reindex_asp_literature.py        # Script to reindex all PDFs
├── unified_server.py                # Server with RAG integration
├── asp_literature/
│   ├── pdfs/                        # Source PDFs (20 papers currently)
│   │   ├── 38734660.pdf
│   │   ├── 39284176.pdf
│   │   └── ...
│   └── embeddings/                  # ChromaDB vector store
│       └── chroma.sqlite3           # 1277 chunks indexed
└── ASP_RAG_SYSTEM.md (this file)
```

## Current Status

- **Papers Indexed**: 20 ASP research papers
- **Total Chunks**: 1,277 text segments
- **Embedding Model**: PubMedBERT (pritamdeka/S-PubMedBert-MS-MARCO, 768-dim)
- **Vector Store**: ChromaDB (persistent, local)
- **LLM**: Gemini 2.0 Flash (fast, accurate)

## How It Works

### 1. When User Submits Response

The system automatically:
1. Extracts key ASP concepts from the scenario/response
2. Searches the literature with multiple queries:
   - "antimicrobial stewardship [level]"
   - "reducing broad-spectrum antibiotic use"
   - "days of therapy DOT measurement"
   - "behavioral change interventions antimicrobial"
   - "implementation science stewardship"

### 2. RAG Retrieval

- Searches 1,277 indexed chunks using semantic similarity (PubMedBERT)
- Returns top 3-5 most relevant excerpts (min similarity: 0.4)
- Deduplicates by PMID to ensure diverse sources
- Includes PMID citations for traceability

### 3. LLM Generation

Gemini receives:
- The scenario and user's response
- Relevant literature excerpts with PMIDs
- Evaluation rubrics for 4 competency domains
- Instruction to use BOTH literature AND its own knowledge

### 4. Output

Feedback includes:
- Scores across 4 domains (Data Analysis, Behavioral Intervention, Implementation Science, Clinical Decision Making)
- Specific, actionable guidance
- **Evidence-based citations** (e.g., "As shown in PMID 39284176...")
- Strengths and areas for improvement

## Adding More Literature

### Option 1: Quick Add (Incremental)

```bash
# 1. Add PDF files to asp_literature/pdfs/
cp new_paper.pdf asp_literature/pdfs/

# 2. Run the indexing test (will add new papers)
python3 asp_rag_module.py
```

### Option 2: Complete Re-index (Recommended)

```bash
# Re-index all PDFs from scratch
python3 reindex_asp_literature.py
```

### Option 3: Programmatic

```python
from asp_rag_module import ASPLiteratureRAG

rag = ASPLiteratureRAG()
rag.index_pdfs(force_reindex=True)  # Re-index everything
```

## Testing the RAG System

### Test 1: Direct RAG Search

```bash
python3 asp_rag_module.py
```

This runs the test suite which:
- Initializes the RAG system
- Indexes PDFs (if not already done)
- Performs test searches
- Displays relevant excerpts

### Test 2: Web Interface

```bash
# Start server (RAG auto-loads)
python3 unified_server.py

# Navigate to CICU module
# http://localhost:8080/cicu_module.html

# Submit a response and check feedback for PMID citations
```

### Test 3: API Request

```bash
curl -X POST http://localhost:8080/api/modules/cicu/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "input": "I would calculate DOT per 1000 patient days and implement behavioral interventions",
    "level": "beginner"
  }' | python3 -m json.tool
```

Check the response for:
- `"success": true`
- PMID citations in the feedback text
- Server logs showing "Retrieved X relevant papers for context"

## Technical Details

### Embedding Model

- **Model**: `pritamdeka/S-PubMedBert-MS-MARCO`
- **Dimensions**: 768
- **Optimized for**: Biomedical literature search
- **Speed**: ~10 chunks/second on CPU

### Chunking Strategy

- **Method**: Sentence-aware chunking
- **Chunk Size**: 512 tokens (~650 characters)
- **Overlap**: 50 tokens (maintains context across chunks)
- **Preserves**: Sentence boundaries (no mid-sentence cuts)

### Search Parameters

- **Similarity Metric**: Cosine similarity (via ChromaDB)
- **Minimum Threshold**: 0.4 (filters low-relevance results)
- **Results per Query**: 2 (deduped to 5 total across all queries)
- **Multiple Queries**: 5 different search angles for comprehensive retrieval

## Performance

- **Index Loading**: ~3 seconds (PubMedBERT model + ChromaDB)
- **Search Latency**: <100ms for 5 queries across 1,277 chunks
- **Total Feedback Time**: ~3-5 seconds (search + Gemini generation)
- **Disk Space**: ~15MB for 20 PDFs + 50MB for embeddings

## Future Enhancements

### Planned Features

1. **Automatic PDF Downloads**: Integration with PubMed API to fetch papers by PMID
2. **Metadata Enrichment**: Extract authors, dates, study types from PDFs
3. **Citation Formatting**: Properly formatted citations (not just PMIDs)
4. **Advanced Filtering**: Filter by publication date, study type, or topic
5. **Hybrid Search**: Combine semantic search with keyword (BM25) search
6. **User Feedback Loop**: Learn from which citations were most helpful

### Scaling

- **Current**: 20 papers, 1,277 chunks (~50MB)
- **Target**: 200+ papers, 15,000+ chunks (~500MB)
- **Performance**: ChromaDB scales to millions of vectors without degradation

## Troubleshooting

### RAG Not Loading

**Symptom**: Server starts but shows "⚠ Warning: Could not initialize ASP RAG"

**Solutions**:
1. Check that `asp_literature/embeddings/` exists
2. Run `python3 asp_literature_rag.py` to create index
3. Verify PubMedBERT model downloaded: `~/.cache/torch/sentence_transformers/`

### No Citations in Feedback

**Symptom**: Feedback works but doesn't reference PMIDs

**Solutions**:
1. Check server logs for "Retrieved X relevant papers"
2. If "Retrieved 0 relevant papers", try lowering `min_similarity` in unified_server.py:401
3. Verify PDFs indexed: check `asp_rag.collection.count()` in Python

### Slow Performance

**Symptom**: Feedback takes >10 seconds

**Solutions**:
1. RAG search is fast (<100ms) - slowness likely from Gemini API
2. Check network connectivity
3. Consider using local Ollama model as fallback

## Integration Points

### unified_server.py

**Lines 45**: Import RAG module
**Lines 64-68**: Initialize RAG system
**Lines 386-424**: RAG search in feedback endpoint
**Lines 439-447**: Add literature context to prompt

### cicu_module.html

No changes required - RAG works transparently behind the API

## Benefits of This Approach

1. **Evidence-Based**: Grounds feedback in actual research, not just LLM knowledge
2. **Traceable**: PMID citations allow users to verify sources
3. **Updatable**: Add new papers without retraining LLM
4. **Independent**: Not dependent on external services
5. **Fast**: PubMedBERT optimized for biomedical text
6. **Hybrid**: Best of both worlds (curated literature + LLM intelligence)

## Example Feedback (with RAG)

**Without RAG**:
> "Your DOT calculation approach is good. Consider implementing behavioral interventions to change prescribing habits."

**With RAG**:
> "Your DOT calculation approach is good. Consider implementing behavioral interventions to change prescribing habits. As shown in PMID 39284176, audit-and-feedback combined with academic detailing reduced inappropriate vancomycin use by 34% in ICU settings. Additionally, PMID 40775754 demonstrated that involving clinical champions from the cardiology team significantly improved adoption rates."

---

**Last Updated**: November 9, 2025
**System Version**: v1.0
**Papers Indexed**: 20
**Chunks**: 1,277
