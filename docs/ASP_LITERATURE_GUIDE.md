# Adding Literature to ASP RAG System - Quick Guide

## Overview

The enhanced RAG system now extracts bibliographic metadata from PDFs automatically and generates AMA-style citations, regardless of PDF filename.

## Adding PDFs

### Method 1: Add PDF with Any Filename

```bash
# Copy PDF to literature directory
cp ~/Downloads/your_study.pdf /home/david/projects/asp_ai_agent/asp_literature/pdfs/

# Re-index (extracts metadata automatically)
cd /home/david/projects/asp_ai_agent
python3 << 'EOF'
from asp_rag_module import ASPLiteratureRAG
rag = ASPLiteratureRAG()
rag.index_pdfs(force_reindex=True)
EOF
```

### Method 2: Add PMID-Named PDF (Backward Compatible)

```bash
# Name PDF by PMID (8 digits)
cp ~/Downloads/study.pdf /home/david/projects/asp_ai_agent/asp_literature/pdfs/12345678.pdf

# Re-index (automatically uses PMID as paper_id)
python3 -c "from asp_rag_module import ASPLiteratureRAG; rag = ASPLiteratureRAG(); rag.index_pdfs(force_reindex=True)"
```

## Metadata Extraction Process

The system uses a **three-tier approach**:

1. **Embedded PDF Metadata** (fast) - extracts title, author, date from PDF properties
2. **First-Page Text Parsing** (more reliable) - parses journal article format for metadata
3. **LLM Extraction** (fallback, most accurate) - uses Gemini to extract structured data

**Extraction happens automatically** during indexing - no manual configuration needed!

## What Metadata is Extracted

- **Title**: Paper title
- **Authors**: Full author list
- **First Author**: For inline citations
- **Year**: Publication year
- **Journal**: Journal name
- **Volume/Pages**: Citation details
- **DOI**: Digital Object Identifier
- **PMID**: PubMed ID (if available in PDF or filename)

## Citation Output Format

### Before (PMID-only)
```
[PMID 12345678] This study showed that antimicrobial stewardship...
```

### After (AMA-style with rich metadata)
```
According to Smith et al. (2023), This study showed that antimicrobial 
stewardship interventions reduced inappropriate vancomycin use by 34% 
in ICU settings [1]

References:
[1] Smith JK, Johnson AM, Brown RL. Impact of ASP interventions on ICU 
    antibiotic use. JAMA. 2023;329(15):1234-1245. doi:10.1001/jama.2023.12345
```

## Testing Your Addition

```python
from asp_rag_module import ASPLiteratureRAG

rag = ASPLiteratureRAG()

# Search your newly added paper
results = rag.search("your search terms", n_results=5)

# Check metadata was extracted
for result in results:
    print(f"Title: {result['title']}")
    print(f"Authors: {result['authors']}")
    print(f"Year: {result['year']}")
    print(f"Extraction method: {result.get('extraction_method', 'unknown')}")

# Get formatted context
context = rag.get_context_for_query("your query", max_results=3)
print(context)  # Will show AMA citations
```

## Troubleshooting

### No metadata extracted
- **Cause**: PDF might be scanned image (no extractable text)
- **Solution**: Use OCR tool or ensure PDF has text layer

### Wrong title extracted
- **Cause**: PDF first page has unusual format
- **Solution**: System will attempt LLM fallback automatically (if GEMINI_API_KEY is set)

### PMID not detected
- **Cause**: PMID not in PDF text or filename
- **Solution**: Either rename to PMID.pdf or manually add to metadata (future feature)

## Current Status

- **25 PDFs indexed** with rich metadata
- **1,792 chunks** with bibliographic information
- **Extraction methods used**: Embedded metadata (48%), Text parsing (52%), LLM (0%)
- **All existing PMID-based PDFs** work without changes (backward compatible)

## Configuration

### Enable/Disable LLM Fallback

```python
from asp_rag_module import ASPLiteratureRAG

# With LLM fallback (default)
rag = ASPLiteratureRAG()

# Without LLM fallback (faster, lower accuracy)
rag.metadata_extractor.use_llm_fallback = False
rag.index_pdfs(force_reindex=True)
```

### Requires
- `GEMINI_API_KEY` environment variable for LLM fallback
- PDF must have text layer (not scanned images)

---

**Last Updated**: November 18, 2025  
**System Version**: v2.0 with metadata extraction
