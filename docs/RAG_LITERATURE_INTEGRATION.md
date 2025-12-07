# RAG Literature Integration - ASP AI Agent

## Overview

The ASP AI Agent has been enhanced with a sophisticated hierarchical literature retrieval system that integrates local RAG, PubMed search, and PMC full-text retrieval. This provides evidence-based responses backed by current medical literature across all interaction points.

## Architecture

### Hierarchical Retrieval System

The system implements a three-tier retrieval strategy:

1. **Local RAG (Tier 1)**
   - Primary source: Pre-indexed ASP literature
   - 10,832+ indexed chunks from curated PDFs
   - Fastest retrieval with sub-second response
   - Uses BGE embeddings for semantic search

2. **PubMed Search (Tier 2)**
   - Fallback for current literature
   - Real-time search via NCBI E-utilities API
   - Configurable with NCBI API key for higher rate limits
   - Returns abstracts and metadata

3. **PMC Full Text (Tier 3)**
   - Attempts to fetch complete articles
   - Available for open-access publications
   - Provides deeper context when needed

## Components

### Core Modules

#### `pubmed_rag_tools.py`
- **Class**: `PubMedRAGSystem`
- **Purpose**: Orchestrates hierarchical retrieval
- **Key Features**:
  - Automatic fallback between tiers
  - Deduplication by PMID
  - Similarity threshold filtering
  - Source tracking for transparency

#### `literature_extractor.py`
- **Class**: `LiteratureExtractor`
- **Purpose**: Structured extraction from literature using local LLMs
- **Model**: Qwen 2.5 72B (configurable)
- **Key Features**:
  - Extracts study type, population, interventions
  - Identifies key findings and limitations
  - Caches extractions in SQLite
  - Relevance scoring (HIGH/MEDIUM/LOW)

#### `EnhancedPubMedRAG`
- Combines retrieval with extraction
- Pipeline: Search → Retrieve → Extract → Synthesize
- Optimized for medical Q&A

## API Endpoints

### Literature Search Endpoints

#### `/api/literature/search`
- **Method**: POST
- **Purpose**: Basic hierarchical literature search
- **Parameters**:
  ```json
  {
    "query": "search query",
    "max_results": 5,
    "force_pubmed": false,
    "fetch_full_text": false
  }
  ```
- **Returns**: Documents with metadata and sources

#### `/api/literature/extract`
- **Method**: POST
- **Purpose**: Search + AI extraction
- **Parameters**:
  ```json
  {
    "query": "search query",
    "max_results": 5,
    "extract_top_n": 3
  }
  ```
- **Returns**: Structured extractions with key findings

### Enhanced Chat Endpoints

#### `/api/chat/with-literature`
- **Method**: POST
- **Purpose**: Chat with automatic literature retrieval
- **Parameters**:
  ```json
  {
    "query": "user question",
    "model": "claude:4.5-opus",
    "max_literature": 5
  }
  ```
- **Features**:
  - Automatically retrieves relevant papers
  - Includes sources in response
  - Falls back gracefully if services unavailable

#### `/api/chat/evidence-based`
- **Method**: POST
- **Purpose**: Full extraction pipeline for comprehensive responses
- **Parameters**:
  ```json
  {
    "query": "clinical question",
    "model": "claude:4.5-opus",
    "max_literature": 5,
    "extract_top_n": 3
  }
  ```
- **Pipeline**: Search → Extract → Synthesize

#### `/api/chat/agentic`
- **Method**: POST
- **Purpose**: LLM-orchestrated literature search (experimental)
- **Features**:
  - LLM decides when to search
  - Tool-calling paradigm
  - Currently optimized for Claude models

## Web Interface Integration

### Pages Updated

#### 1. `local_models.html`
- **Behavior**: Maintains dual response mode
  - Standard LLM response
  - Expert RAG-enhanced response
- **Default Model**: Claude Opus 4.5
- **Use Case**: Comparing RAG vs non-RAG responses

#### 2. `asp_ai_agent.html`
- **Behavior**: RAG-enhanced by default
- **Endpoint**: `/api/chat/with-literature`
- **Features**:
  - Automatic literature retrieval
  - Source citations displayed
  - Up to 5 papers per query
- **Default Model**: Claude Opus 4.5

#### 3. `agent_models.html`
- **Behavior**: RAG-enhanced by default
- **Endpoint**: `/api/chat/with-literature`
- **Features**:
  - Multi-model support with RAG
  - Source tracking
  - Evidence-based responses
- **Default Model**: Claude Opus 4.5

#### 4. `cicu_module.html`
- **Behavior**: Enhanced CICU feedback with RAG
- **Endpoint**: `/api/modules/cicu/feedback`
- **Features**:
  - Hierarchical literature search
  - Full-text retrieval when available
  - Rubric-based evaluation with evidence
- **Default Model**: Claude Opus 4.5

## Configuration

### Environment Variables

```bash
# NCBI API Key (optional but recommended)
NCBI_API_KEY=your_api_key_here

# Literature Extraction Model
EXTRACTION_MODEL=qwen2.5:72b-instruct-q4_K_M

# Default Chat Model
DEFAULT_MODEL=claude:4.5-opus
```

### Rate Limits

- `/api/literature/search`: 30 requests/minute
- `/api/literature/extract`: 10 requests/minute
- `/api/chat/with-literature`: 15 requests/minute
- `/api/chat/evidence-based`: 10 requests/minute
- `/api/chat/agentic`: 20 requests/minute

## Model Support

### Preferred Models (Tool-capable)
- **Claude Opus 4.5** (default) - Best quality
- **Claude Sonnet 4.5** - Balanced speed/quality
- **Gemini 3 Pro** - Google's latest
- **GPT-5.1** - OpenAI's newest

### Local Models (Via Ollama)
- **Qwen 2.5 72B** - Extraction specialist
- **Llama 3.1 70B** - General purpose
- **OpenBioLLM 70B** - Medical domain
- **Gemma 2 27B** - Fast inference

## Security Features

### CSRF Protection
- All endpoints require CSRF tokens
- Session-based authentication
- Secure token generation

### Input Validation
- Prompt injection protection
- Input sanitization
- Length limits enforced

### Rate Limiting
- Per-endpoint limits
- IP-based tracking
- Graceful degradation

## Graceful Degradation

The system handles service unavailability elegantly:

1. **No Local RAG** → Skip to PubMed
2. **No PubMed Access** → Use local RAG only
3. **No Extraction Model** → Return raw search results
4. **No Cloud LLM** → Fall back to local Ollama
5. **No Literature** → Standard LLM response

## Testing

### Test Script
Use `test_literature_api.py` to verify:
- Literature search functionality
- Extraction pipeline
- Chat with literature
- Source citation

### Manual Testing
```bash
# Basic search
curl -X POST http://localhost:8080/api/literature/search \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: [token]" \
  -d '{"query": "vancomycin dosing"}'

# Chat with literature
curl -X POST http://localhost:8080/api/chat/with-literature \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: [token]" \
  -d '{"query": "What is the evidence for beta-lactam infusions?", "model": "claude:4.5-opus"}'
```

## Benefits

### Clinical Decision Support
- Evidence-based recommendations
- Current literature integration
- Transparent source citations
- Confidence scoring

### Educational Value
- Learn from primary sources
- Understand evidence quality
- Track citation trails
- Compare conflicting evidence

### Quality Assurance
- Reproducible responses
- Auditable sources
- Version tracking
- Continuous improvement

## Future Enhancements

### Planned Features
1. **Extraction Improvements**
   - Multi-model extraction consensus
   - Custom extraction templates
   - Domain-specific extractors

2. **Retrieval Enhancements**
   - Hybrid search (dense + sparse)
   - Re-ranking models
   - Query expansion
   - Citation graph analysis

3. **Interface Updates**
   - Interactive source explorer
   - Evidence strength visualization
   - Contradiction detection
   - Real-time updates

4. **Integration Expansion**
   - Additional literature databases
   - Clinical guidelines integration
   - Drug interaction databases
   - Local hospital protocols

## Troubleshooting

### Common Issues

1. **No PubMed Results**
   - Check NCBI API key configuration
   - Verify network connectivity
   - Check rate limits

2. **Slow Extraction**
   - Ensure Ollama is running
   - Check model availability
   - Monitor GPU usage

3. **Missing Sources**
   - Verify PubMed RAG initialization
   - Check local RAG index
   - Review similarity thresholds

### Debug Mode
Set environment variable for verbose logging:
```bash
export RAG_DEBUG=true
```

## Performance Metrics

### Typical Response Times
- Local RAG only: < 1 second
- PubMed search: 2-5 seconds
- Full extraction: 15-30 seconds
- Complete pipeline: 20-40 seconds

### Resource Usage
- RAM: 8-16GB (model dependent)
- Storage: ~5GB for embeddings
- Network: Minimal (API calls only)
- GPU: Recommended for extraction

## Compliance & Ethics

### Data Privacy
- No patient data in literature
- Secure API communications
- Local processing when possible
- HIPAA-compliant deployment ready

### Citation Ethics
- Always cite sources
- Respect copyright
- Link to originals
- Acknowledge limitations

## Support & Maintenance

### Monitoring
- Check `/health` endpoint
- Review extraction cache
- Monitor API quotas
- Track error logs

### Updates
- Regular literature reindexing
- Model updates as available
- API compatibility checks
- Security patches

## Conclusion

The RAG Literature Integration transforms the ASP AI Agent into a powerful evidence-based clinical decision support tool. By combining local expertise with global medical knowledge, it provides trustworthy, transparent, and current recommendations for antimicrobial stewardship.

---

*Last Updated: December 2024*
*Version: 2.0.0*
*Status: Production Ready*