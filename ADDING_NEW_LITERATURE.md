# Adding New Literature to the RAG System

This guide explains how to add new PDF papers to your ASP Literature RAG knowledge base.

---

## Quick Start

### 1. Add PDF Files
Place new PDF files in the main pdfs directory:
```bash
cp new_paper.pdf /home/david/projects/asp_ai_agent/asp_literature/pdfs/
```

### 2. Run the Indexer
```bash
cd /home/david/projects/asp_ai_agent
python3 index_new_pdfs.py
```

### 3. Restart the Server
```bash
bash /tmp/restart_server.sh
```

---

## How It Works

### Directory Structure
```
asp_literature/
└── pdfs/
    ├── transferred/        # Already-indexed PDFs (don't re-process)
    └── new_paper.pdf      # New PDFs to index
```

### Workflow

1. **Add PDFs**: Place new PDFs in `asp_literature/pdfs/`

2. **Smart Indexing**: The `index_new_pdfs.py` script will:
   - Check which papers are already in the collection
   - Only process NEW PDFs (not in transferred/)
   - Extract text and metadata
   - Generate embeddings
   - Add to ChromaDB collection

3. **Auto-Transfer**: After successful indexing:
   - PDFs are moved to `pdfs/transferred/`
   - This prevents re-indexing the same papers

4. **Server Restart**: Restart Flask to load the updated collection

---

## Example Session

```bash
# Add 3 new papers
cp paper1.pdf paper2.pdf paper3.pdf asp_literature/pdfs/

# Index them
python3 index_new_pdfs.py

# Output:
# ======================================================================
# ASP Literature RAG - Incremental PDF Indexer
# ======================================================================
#
# Initializing RAG system...
# Current collection size: 1997 chunks
#
# 📊 Found 25 already-indexed papers in collection
#
# 📚 Found 3 NEW PDFs to index:
#    - paper1.pdf
#    - paper2.pdf
#    - paper3.pdf
#
#    [1/3] Processing: paper1.pdf
#        Extracting metadata...
#        ✓ Method: embedded_metadata
#        ✓ Title: Antimicrobial Stewardship in Critical Care...
#        Created 89 chunks
# ... (continues for paper2 and paper3)
#
# 🔄 Computing embeddings for 267 chunks...
# 💾 Storing in ChromaDB...
# ✅ Indexing complete! 267 chunks indexed
#
# 📁 Moving 3 indexed PDFs to asp_literature/pdfs/transferred/...
#    ✓ Moved: paper1.pdf
#    ✓ Moved: paper2.pdf
#    ✓ Moved: paper3.pdf
#
# ✅ Complete! Indexed 3 new PDFs
#    Total chunks in collection: 2264
# ======================================================================
# ✅ SUCCESS: Indexed 3 new PDF(s)
#    New collection size: 2264 chunks
#    Indexed PDFs moved to: asp_literature/pdfs/transferred/
# ======================================================================
#
# ⚠️  REMINDER: Restart the Flask server to use the updated collection
#    bash /tmp/restart_server.sh

# Restart server
bash /tmp/restart_server.sh
```

---

## Manual Operations

### Check Current Collection Size
```python
from asp_rag_module import ASPLiteratureRAG
rag = ASPLiteratureRAG()
print(f"Collection has {rag.collection.count()} chunks")
```

### List Indexed Papers
```python
from asp_rag_module import ASPLiteratureRAG
rag = ASPLiteratureRAG()

results = rag.collection.get(limit=1000, include=['metadatas'])
titles = set(meta.get('title', 'Unknown') for meta in results['metadatas'])
print(f"Total papers: {len(titles)}")
for title in sorted(titles):
    print(f"  - {title}")
```

### Test Search Quality
```python
from asp_rag_module import ASPLiteratureRAG
rag = ASPLiteratureRAG()

results = rag.search("antibiotic stewardship ICU", n_results=5)
for i, result in enumerate(results, 1):
    print(f"{i}. {result['title']} (similarity: {result['similarity']})")
```

---

## Troubleshooting

### "No new PDFs to index"
- Check that PDFs are in `asp_literature/pdfs/` (not in `transferred/`)
- Verify PDFs aren't already indexed by checking the collection

### Indexing Errors
- Ensure PDFs are valid and readable
- Check PDF is text-based (not scanned images)
- Large PDFs may take longer to process

### Server Doesn't See New Papers
- Did you restart the server? Run: `bash /tmp/restart_server.sh`
- Check server logs: `tail -50 /tmp/server_new.log | grep "ASP Literature RAG loaded"`

### Force Re-Index Everything
If you need to completely rebuild the index:
```python
from asp_rag_module import ASPLiteratureRAG
rag = ASPLiteratureRAG()
rag.index_pdfs(force_reindex=True)
```

---

## Best Practices

1. **Organize by Topic**: Consider using subdirectories in `transferred/`:
   ```
   transferred/
   ├── clinical_guidelines/
   ├── stewardship_education/
   └── resistance_epidemiology/
   ```

2. **Descriptive Filenames**: Use meaningful names:
   - ✅ `gerber-2009-rheumatic-fever-prevention.pdf`
   - ❌ `paper1.pdf`

3. **Batch Processing**: Add multiple PDFs at once for efficiency

4. **Test Queries**: After adding papers, test search with relevant queries

5. **Monitor Collection Size**: Track growth over time
   - Initial: 22 papers, 1792 chunks
   - After update: 28 papers, 1997 chunks

---

## Technical Details

### Metadata Extraction
The indexer extracts:
- Title (from PDF metadata or text parsing)
- Authors (first author highlighted)
- Journal, Volume, Pages
- Publication year
- DOI and PMID (if available)

### Chunking Strategy
- Chunk size: 512 tokens
- Overlap: 50 tokens
- Preserves context across chunk boundaries

### Embedding Model
- Model: `pritamdeka/S-PubMedBert-MS-MARCO`
- Optimized for biomedical literature
- Embedding dimension: 768

### Vector Database
- ChromaDB with persistent storage
- Cosine similarity search
- Indexed by paper_id and chunk_index

---

## Future Enhancements

Potential improvements:
- Automatic PDF download from PubMed
- Duplicate detection by DOI/PMID
- Quality scoring for papers
- Topic-based collections
- Version tracking for updated papers

---

Last Updated: 2025-11-18
