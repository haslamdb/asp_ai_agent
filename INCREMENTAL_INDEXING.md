# Incremental Literature Indexing Guide

## Overview

The `reindex_from_endnote.py` script now supports **incremental indexing** - it preserves existing embeddings and only indexes new papers you add to your EndNote library.

## Quick Start

### Add New Literature (Recommended)

When you add new PDFs to your EndNote library, simply run:

```bash
python reindex_from_endnote.py
```

This will:
- ✅ **Preserve** all existing embeddings
- ✅ **Only index** new PDFs not yet in the collection
- ✅ **Skip** duplicates (by filename and PMID)
- ✅ Save time and compute resources

### Full Reindex (When Needed)

If you need to rebuild the entire index from scratch (e.g., after changing chunk size):

```bash
python reindex_from_endnote.py --full
```

This will:
- ⚠️ **Delete** existing collection
- 🔄 Re-index all PDFs from scratch
- ⏱️ Takes longer (processes all papers)

## How It Works

### Incremental Mode (Default)

1. **Checks existing collection** for already-indexed papers
2. **Scans EndNote library** for all PDFs
3. **Compares** to find new papers
4. **Indexes only new papers** and adds them to existing collection
5. **Preserves** all existing embeddings

### Detection Logic

Papers are considered "already indexed" if:
- **Filename** matches an existing entry, OR
- **PMID** matches an existing entry

This prevents duplicates even if you rename files.

## Workflow Examples

### Example 1: Adding 10 New Papers

```bash
# You add 10 new papers to EndNote library
# Current collection: 150 papers, 45,000 chunks

python reindex_from_endnote.py

# Output:
# 📊 Incremental indexing mode - preserving existing embeddings
#    Current collection size: 45000 chunks
# 🔍 Checking already-indexed papers...
#    Found 150 already-indexed files
#    Found 148 unique PMIDs already indexed
# 🔍 Scanning PDFs in asp_literature/asp_library.Data/PDF...
#    Found 160 PDF files total
# 📊 Summary:
#    Total PDFs found: 160
#    Already indexed (skipped): 150
#    New PDFs to index: 10
# 🔄 Computing embeddings for 300 chunks...
# ✅ Indexing complete!
#    📊 New chunks added: 300
#    📚 Total collection size: 45300 chunks
#    💾 Existing embeddings preserved
```

### Example 2: No New Papers

```bash
python reindex_from_endnote.py

# Output:
# ✅ No new chunks to index - everything is already indexed!
#    Total collection size: 45300 chunks
```

### Example 3: Full Reindex

```bash
python reindex_from_endnote.py --full

# Output:
# 🧹 Full reindex mode - clearing existing RAG collection...
#    ✓ Deleted old collection
#    ✓ Created fresh collection
# [processes all 160 papers...]
# ✅ Indexing complete!
#    📚 Total collection size: 48000 chunks
```

## Performance Comparison

| Scenario | Papers | Mode | Time | Computation |
|----------|--------|------|------|-------------|
| Initial index | 150 | Full | ~30 min | 45,000 embeddings |
| Add 10 papers | 10 | Incremental | ~2 min | 300 embeddings |
| Add 10 papers | 160 | Full (old way) | ~32 min | 48,000 embeddings |

**Result: 15x faster for small additions!**

## When to Use Each Mode

### Use Incremental (Default) When:
- ✅ Adding new papers to your library
- ✅ Updating metadata in EndNote
- ✅ Regular maintenance
- ✅ You want to save time

### Use Full Reindex (--full) When:
- 🔧 Changing chunk size or overlap settings
- 🔧 Changing embedding model
- 🔧 Major library reorganization
- 🐛 Fixing corrupted collection
- 🧹 Clean slate needed

## Verifying Results

After indexing, restart the unified server:

```bash
# Stop current server
pkill -f unified_server.py

# Start fresh
nohup python unified_server.py > unified_server.log 2>&1 &

# Check health
curl http://localhost:8080/health
```

You should see the updated collection size in the response.

## Troubleshooting

### "Everything is already indexed" but I added papers

**Check:**
1. Are the PDFs in the correct directory? (`asp_literature/asp_library.Data/PDF/`)
2. Does EndNote have metadata for these PDFs? (Check `sdb.eni` and `pdb.eni`)
3. Are the filenames unique? (Not duplicates of existing papers)

**Solution:** Check the EndNote metadata:
```python
from reindex_from_endnote import get_endnote_metadata
meta = get_endnote_metadata()
print(f"Papers in EndNote: {len(meta)}")
print("Sample:", list(meta.keys())[:5])
```

### Collection seems corrupted

**Solution:** Do a full reindex:
```bash
python reindex_from_endnote.py --full
```

### New papers not showing up in searches

**Cause:** Server needs restart to reload collection

**Solution:**
```bash
pkill -f unified_server.py
nohup python unified_server.py > unified_server.log 2>&1 &
```

## Technical Details

### Chunk Settings

Current settings (optimized for context):
- **Chunk size:** 600 tokens (increased from 512)
- **Overlap:** 100 tokens (increased from 50)

These settings provide better context for RAG retrieval.

### Collection Structure

Each chunk has metadata:
- `filename`: PDF filename
- `paper_id`: Unique identifier (PMID or generated)
- `title`, `first_author`, `year`, `journal`
- `doi`, `pmid`, `volume`, `pages`
- `authors_json`: Full author list
- `chunk_index`, `total_chunks`: Position info
- `extraction_method`: "endnote_db"

### Storage Location

- **ChromaDB:** `chroma_db/` directory (auto-created)
- **Collection name:** `asp_literature`
- **Embeddings:** PubMedBERT (768-dimensional)

## Best Practices

1. **Use incremental by default** - faster and preserves work
2. **Full reindex** only when necessary
3. **Restart server** after indexing to apply changes
4. **Verify** collection size matches expectations
5. **Keep EndNote** metadata up-to-date (PMID, authors, titles)

## See Also

- [PDF_INDEXING_GUIDE.md](PDF_INDEXING_GUIDE.md) - Original indexing documentation
- [ADDING_NEW_LITERATURE.md](ADDING_NEW_LITERATURE.md) - How to add papers to EndNote
