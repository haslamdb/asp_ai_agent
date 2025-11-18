# PDF Indexing Guide - ASP Literature RAG

**Last Updated:** 2025-11-18

---

## Official Indexing Script

**Use:** `index_new_pdfs_llm.py`

This is the **ONLY** script you should use for adding new PDFs to the RAG system.

### Key Features:
- ✅ **Incremental:** Only indexes NEW PDFs (does not re-index existing papers)
- ✅ **LLM-Enhanced:** Uses Gemini 2.0 Flash for clean metadata extraction
- ✅ **Quality Checks:** Rejects garbage titles (page headers, URLs) and triggers LLM fallback
- ✅ **Preserves Data:** Adds to existing collection, does NOT overwrite

---

## Workflow

### Step 1: Add New PDFs
```bash
# Place new PDF files in the main directory
cp new_paper1.pdf new_paper2.pdf /home/david/projects/asp_ai_agent/asp_literature/pdfs/
```

### Step 2: Run Indexing Script
```bash
cd /home/david/projects/asp_ai_agent
python3 index_new_pdfs_llm.py
```

**What it does:**
- Checks which papers are already indexed (skips them)
- Extracts metadata using 3-tier approach:
  1. PDF embedded metadata (fast)
  2. Text parsing from first pages (reliable)
  3. **LLM extraction** (when titles contain garbage like "www.", "◆", DOI links)
- Generates embeddings
- **Adds** to existing ChromaDB collection

### Step 3: Move Indexed PDFs
```bash
cd /home/david/projects/asp_ai_agent/asp_literature/pdfs
mv *.pdf transferred/
```

This prevents re-indexing the same papers next time.

### Step 4: Restart Server
```bash
bash /tmp/restart_server.sh
```

Server loads the updated collection with new papers.

---

## Example Session

```bash
# Add 2 new papers
$ cp rheumatic_fever_2024.pdf strep_treatment_2023.pdf asp_literature/pdfs/

# Run indexing
$ python3 index_new_pdfs_llm.py

✓ GEMINI_API_KEY loaded

Incrementally indexing new PDFs with LLM-enhanced metadata extraction...

Current collection: 1086 chunks

Checking for already-indexed papers...
✓ Found 14 already-indexed papers

📚 Found 2 NEW PDFs to index:
   - rheumatic_fever_2024.pdf
   - strep_treatment_2023.pdf

Indexing new PDFs with LLM metadata extraction...
======================================================================
   [1/2] Processing: rheumatic_fever_2024.pdf
       Extracting metadata...
   ✓ LLM extracted metadata: Acute Rheumatic Fever: Updated Diagnostic Criteria...
       ✓ Method: llm
       ✓ Title: Acute Rheumatic Fever: Updated Diagnostic Criteria...
       Created 89 chunks
   [2/2] Processing: strep_treatment_2023.pdf
       Extracting metadata...
       ✓ Method: embedded_metadata
       ✓ Title: Group A Streptococcal Infections: Treatment Guidelines...
       Created 67 chunks

🔄 Computing embeddings for 156 chunks...
💾 Adding to existing collection...
======================================================================

✓ Indexing complete! Added 156 chunks
Final collection size: 1242 chunks

# Move to transferred
$ cd asp_literature/pdfs
$ mv *.pdf transferred/

# Restart server
$ bash /tmp/restart_server.sh
Server running with PID: 1234567
```

---

## Metadata Extracted

For each paper, the script extracts:

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Clean paper title | "Poststreptococcal Reactive Arthritis: Diagnostic Challenges" |
| `first_author` | Last name of first author | "Chun" |
| `authors` | List of all authors | ["Chun TH", "Smith JK"] |
| `year` | Publication year | 2019 |
| `journal` | Journal name | "Perm J" |
| `doi` | Digital Object Identifier | "10.7812/TPP/18.304" |
| `pmid` | PubMed ID | "30352948" |
| `volume` | Journal volume | "23" |
| `pages` | Page range | "18-304" |

---

## Quality Checks

The script automatically detects and rejects low-quality titles that contain:

- URLs: `www.`, `http`, `.com`, `.org`
- DOI links: `doi.org`
- Page markers: `◆`, `•`, `Volume`, `Number`
- Copyright text: `©`, `All rights reserved`
- Headers: `For personal use only`

When detected, it **automatically triggers LLM extraction** for clean metadata.

---

## Archived Scripts

Old indexing scripts (DO NOT USE):
- `archived/index_new_pdfs.py` - Old version without LLM
- `archived/reindex_asp_literature.py` - Old reindexing script

These are kept for reference only.

---

## Troubleshooting

### "No new PDFs to index"
- Check PDFs are in `asp_literature/pdfs/` (not `transferred/`)
- Verify filenames don't match already-indexed papers

### GPU Out of Memory
- Stop Ollama models: `ollama stop llama3.1:70b`
- Or the script will use available GPU memory

### "GEMINI_API_KEY not set"
- Make sure `GEMINI_API_KEY` is in `.env` file
- LLM fallback won't work without it (will use text parsing only)

### Poor Metadata Quality
- Check if LLM extraction was triggered (look for "✓ LLM extracted metadata")
- If not, the title might have passed quality checks
- You can manually re-index specific papers

---

## Current Collection Status

**Location:** `literature_embeddings/` (ChromaDB)
**Current Size:** 1086 chunks (14 papers)
**Embedding Model:** pritamdeka/S-PubMedBert-MS-MARCO (768 dim)

**Papers with LLM-extracted metadata:**
- 18.304.pdf → "Poststreptococcal Reactive Arthritis: Diagnostic Challenges" (Chun, 2019)
- p517.pdf → "Poststreptococcal Illness: Recognition and Management" (Maness, 2018)
- diagnostic_stewardship_of_endotracheal_aspirate.20.pdf
- precision_medicine_and_patient_outcomes_in.423.pdf

---

## Best Practices

1. **Add papers in batches** - More efficient than one-by-one
2. **Descriptive filenames** - Helps with organization (not critical for indexing)
3. **Move to transferred immediately** - Prevents accidental re-indexing
4. **Test search quality** - After adding papers, test with relevant queries
5. **Monitor collection size** - Track growth over time

---

## Technical Details

### Chunking Strategy
- **Chunk size:** 512 tokens
- **Overlap:** 50 tokens
- Preserves context across chunk boundaries

### Embedding Model
- **Model:** S-PubMedBert-MS-MARCO
- **Optimized for:** Biomedical literature
- **Dimension:** 768
- **Device:** GPU (falls back to CPU if unavailable)

### LLM for Metadata
- **Model:** Gemini 2.0 Flash Exp
- **Provider:** Google Generative AI
- **Purpose:** Extract clean bibliographic data from messy PDFs
- **Fallback:** Only triggered when embedded/parsed metadata is low quality

---

Last Updated: 2025-11-18
