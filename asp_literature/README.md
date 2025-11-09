# ASP Literature Knowledge Base

## Overview

This directory contains the curated literature for the ASP AI Agent's RAG (Retrieval-Augmented Generation) system.

## Structure

```
asp_literature/
├── pdfs/              # Source research papers (PDFs)
├── embeddings/        # Vector store (ChromaDB)
└── README.md          # This file
```

## Current Status

- **Papers**: 20 ASP research papers
- **Chunks**: 1,277 text segments indexed
- **Embeddings**: PubMedBERT (768-dim biomedical)

## Adding New Papers

### Step 1: Add PDF to pdfs/ directory

```bash
# Copy new paper(s) to pdfs directory
cp /path/to/new_paper.pdf asp_literature/pdfs/
```

### Step 2: Reindex

```bash
# From project root
python3 reindex_asp_literature.py
```

This will:
1. Scan all PDFs in `pdfs/` directory
2. Extract text and create chunks
3. Generate PubMedBERT embeddings
4. Store in ChromaDB vector store

## How It's Used

When users submit responses in the CICU module:

1. **Query Generation**: System extracts key concepts from the response
2. **Semantic Search**: Searches indexed literature using PubMedBERT
3. **Context Retrieval**: Retrieves 3-5 most relevant excerpts with PMIDs
4. **LLM Generation**: Gemini uses both retrieved literature AND its general knowledge
5. **Evidence-Based Feedback**: Response includes specific PMID citations

## File Naming Convention

PDFs should be named by PMID for traceability:
- `12345678.pdf` = PMID 12345678
- `39284176.pdf` = PMID 39284176

## Maintenance

### Check Index Status

```bash
python3 -c "from asp_rag_module import ASPLiteratureRAG; rag = ASPLiteratureRAG(); print(f'Chunks: {rag.collection.count()}')"
```

### Force Complete Reindex

```bash
python3 reindex_asp_literature.py
```

### Test Search

```bash
python3 asp_rag_module.py
```

## Storage

- **PDFs**: ~15MB (20 papers)
- **Embeddings**: ~50MB (ChromaDB + metadata)
- **Total**: ~65MB

Scales linearly with paper count.

## Notes

- ChromaDB is persistent (survives restarts)
- Embeddings are computed once, cached in `embeddings/`
- Adding papers is incremental (doesn't re-index existing)
- For best results, use full-text research papers (not abstracts)
