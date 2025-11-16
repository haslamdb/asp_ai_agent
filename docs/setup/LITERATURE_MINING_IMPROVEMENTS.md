# Literature Mining System Improvements

## Summary of Changes (November 9, 2025)

### 1. Fixed Critical PMC API Bug ✅

**Problem**: The `find_pmc_pdf()` function in `asp_literature_miner.py` line 579 was treating the PMC API response as a dictionary when it returns a list.

**Fix**: 
```python
# Before (BROKEN):
if pmid in records:
    pmcid = records[pmid].get('pmcid')

# After (FIXED):
records = data.get('records', [])
if records and len(records) > 0:
    record = records[0]
    pmcid = record.get('pmcid')
```

**Impact**: PMC PDF finder now works correctly! Previously returned 0 PMC PDFs, now finding many.

### 2. Created Manual Download Helper Tool ✅

**New Script**: `manual_download_helper.py`

Generates 6 export formats for papers that can't be auto-downloaded:

1. **manual_download_links.txt** - Direct PubMed/DOI links
2. **manual_download_endnote.xml** - EndNote/Zotero import
3. **manual_download.bib** - BibTeX format
4. **librarian_request.csv** - Formatted for librarian requests
5. **failed_pmids.txt** - Simple PMID list
6. **manual_download_report.txt** - Summary with top journals

**Usage**:
```bash
python3 manual_download_helper.py
```

### 3. Results: 92% Improvement in PDF Discovery ✅

**Before Fix**:
- URLs found: 38/106 (35.8%)
- PMC PDFs: 0 ❌
- Unpaywall only: 38

**After Fix**:
- URLs found: 73/106 (68.9%) ✅
- PMC + Unpaywall combined
- **92% improvement!**

### Current Status

**Papers in System**:
- Total from PubMed search: 500 papers (5 years)
- After AI filtering: 107 papers
- Open access URLs found: 73 papers (69%)
- Successfully downloaded PDFs: 20 papers (19%)

**Remaining Challenge**:
- 86 papers need institutional access or manual download
- Many URLs return HTML instead of PDF (publisher blocks automated downloads)
- Solution: Use manual download helper files + librarian request

### Files Modified

1. **asp_literature_miner.py** - Fixed PMC API bug (line 577-584)
2. **manual_download_helper.py** - NEW script for manual retrieval
3. **asp_literature/pdf_locations.json** - Updated with 73 URLs (was 38)
4. **asp_literature/pdf_locations.csv** - Updated
5. **asp_literature/manual_download_*.*** - 6 export files regenerated

### Next Steps

1. **Send to Librarian**: 
   ```
   asp_literature/librarian_request.csv
   ```
   Contains 86 papers with full metadata for institutional access request

2. **Check Institutional Subscriptions** for top journals:
   - JAC-antimicrobial resistance (7 papers)
   - Antibiotics (Basel) (7 papers)
   - Journal of veterinary medical education (5 papers)
   - The Journal of hospital infection (4 papers)

3. **Manual Download** using:
   - `manual_download_links.txt` for direct browser access
   - `manual_download_endnote.xml` to import into reference manager

### Technical Details

**PMC ID Converter API**:
- Endpoint: `https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/`
- Returns: List of records with PMCIDs
- Now correctly extracts PMCID from first record

**PDF Sources Checked**:
1. PubMed Central (PMC) - Open access repository
2. Unpaywall API - Aggregates open access from multiple sources

**Download Blockers**:
- HTTP 403 errors (publisher blocks)
- HTML instead of PDF (login pages)
- Paywalled content

### Commits

1. `9283021` - Fix PMC API bug and add manual download helper
2. `b16488d` - Update PDF locations with improved results (92% improvement)

---

**Improvement Summary**: Fixed critical bug, created manual download tools, and nearly doubled PDF discovery rate from 36% to 69%.
