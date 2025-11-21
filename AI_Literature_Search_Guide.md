# AI-Assisted Literature Search and Download

## Overview

This document describes the AI-powered literature mining system for Antimicrobial Stewardship Program (ASP) research. The system uses gemma2:27b (a 27 billion parameter language model) running locally via Ollama to intelligently filter and score research papers based on their relevance to ASP education and training.

## System Architecture

### Components

1. **PubMed Search** - Queries PubMed database for ASP-related papers
2. **AI Filtering** - Uses gemma2:27b to score papers on educational relevance (0-10 scale)
3. **PDF Discovery** - Finds open access PDFs via PubMed Central and Unpaywall
4. **Automated Download** - Downloads available PDFs with error handling and retry logic

### Hardware

- **GPU**: NVIDIA RTX A6000 (48GB VRAM, CUDA device 1)
- **Alternative**: NVIDIA RTX A5000 (24GB VRAM, CUDA device 0)
- **Model Size**: gemma2:27b (14.6 GB)
- **Performance**: ~300 papers/minute after warmup (0.2s per paper)

## Installation

### Prerequisites

```bash
# Install Python dependencies
pip install pymed requests pandas tqdm

# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull gemma2:27b model
ollama pull gemma2:27b
```

### Verify Setup

Before running the literature miner, test your configuration:

```bash
python test_gemma_setup.py
```

This will verify:
- ✓ Ollama server is running
- ✓ gemma2:27b model is installed
- ✓ GPU is available and detected
- ✓ Model can score papers correctly

## Usage

### Full Pipeline (Recommended)

Run all steps in one command using a screen session (safe for SSH):

```bash
screen -S asp_mining -d -m bash -c "python asp_literature_miner.py --step all --years 5 --max-results 500 --model gemma2:27b --score-threshold 7.0 --query-type training; echo 'Complete! Press enter'; read"
```

**Parameters:**
- `--step all` - Run all 4 steps: search, filter, find PDFs, download
- `--years 5` - Search papers from last 5 years
- `--max-results 500` - Maximum papers to retrieve from PubMed
- `--model gemma2:27b` - LLM model for scoring
- `--score-threshold 7.0` - Minimum relevance score (0-10 scale)
- `--query-type training` - Focus on education/training papers

### Monitoring Progress

```bash
# List screen sessions
screen -list

# View current output (non-intrusive)
screen -S asp_mining -X hardcopy /tmp/asp.txt && tail -30 /tmp/asp.txt

# Attach to session (watch live)
screen -r asp_mining
# Press Ctrl+A then D to detach

# Kill session if needed
screen -S asp_mining -X quit
```

### Individual Steps

If you prefer to run steps separately:

```bash
# Step 1: Search PubMed
python asp_literature_miner.py --step search --years 5 --max-results 500 --query-type training

# Step 2: AI Filter with gemma2:27b
python asp_literature_miner.py --step filter --model gemma2:27b --score-threshold 7.0

# Step 3: Find open access PDFs
python asp_literature_miner.py --step find

# Step 4: Download PDFs
python asp_literature_miner.py --step download
```

## Output Files

All outputs are saved to `asp_literature/`:

```
asp_literature/
├── asp_papers_raw_5yr.csv          # All papers from PubMed search
├── asp_papers_raw_5yr.json         # JSON format
├── asp_papers_filtered.csv         # AI-filtered papers with scores
├── asp_papers_filtered.json        # JSON format (sorted by score)
├── pdf_locations.csv               # PDF URLs found
├── pdf_locations.json              # JSON format
├── filter_checkpoint.json          # Progress checkpoint (temp)
└── pdfs/
    ├── <pmid>.pdf                  # Downloaded papers
    └── download_failures.csv       # Failed downloads log
```

## AI Scoring Criteria

gemma2:27b scores papers on relevance to ASP education/training (0-10):

| Score | Description |
|-------|-------------|
| **10** | Core ASP education (curriculum design, teaching methods, training programs) |
| **8-9** | Strong training focus (competency assessment, educational interventions) |
| **6-7** | Mixed clinical/educational (implementation with training component) |
| **4-5** | Minimal education (brief mention of training in QI project) |
| **1-3** | Tangential (general ASP topics, no educational focus) |
| **0** | Not relevant |

**Default threshold**: 7.0 (keeps papers with strong educational focus)

## Query Types

### Training Query (Recommended for Education Research)
Focuses on educational aspects:
- "antimicrobial stewardship" + "education"
- "curriculum" + "training"
- "medical education" + "fellowship"
- "prescriber education" + "competency"

### Broad Query
Includes more general ASP research:
- "antimicrobial stewardship" + "intervention"
- "quality improvement" + "implementation"
- "behavior change" + "prescriber"

## Advanced Features

### Progress Checkpointing
- Automatically saves progress every 10 papers
- Resume interrupted filtering from checkpoint
- Checkpoint file: `asp_literature/filter_checkpoint.json`

### Error Handling
- Automatic retry (2 attempts) for failed API requests
- Timeout handling (60s per paper)
- Logs slow requests (>10s)
- Failed downloads tracked in `download_failures.csv`

### Performance Monitoring
After completion, the script reports:
- Average inference time per paper
- Min/max processing times
- Total papers filtered
- Average relevance score
- Download success rate

## Example Output

```
============================================================
STEP 2: FILTERING WITH AI (gemma2:27b)
============================================================

→ Starting AI filtering for 100 papers...
→ Mode: Scoring (0-10)
→ Threshold: 7.0

✓ Ollama server is running
✓ Model 'gemma2:27b' is available
→ GPU(s) detected:
  0, NVIDIA RTX A5000, 24564 MiB
  1, NVIDIA RTX A6000, 49140 MiB
→ Ollama will automatically use available GPU(s)

Filtering Papers: 100%|████████| 100/100 [00:30<00:00, 3.33it/s]

✓ AI filtering complete. Kept 23 relevant papers.
→ Average relevance score: 8.2/10
→ Performance: avg=0.3s, min=0.2s, max=1.1s per paper
```

## Troubleshooting

### Ollama Not Running
```bash
# Error: Could not connect to Ollama
# Solution:
ollama serve
```

### Model Not Found
```bash
# Error: Model 'gemma2:27b' not found
# Solution:
ollama pull gemma2:27b
```

### Out of Memory
If GPU memory is insufficient:
```bash
# Use smaller model
python asp_literature_miner.py --model gemma2:9b --step filter
```

### Slow Inference
- First inference: ~3-4s (model loading)
- Subsequent: ~0.2s (cached in GPU)
- If consistently slow (>10s), check GPU availability

### Resume Interrupted Session
If filtering was interrupted, simply re-run the same command:
```bash
python asp_literature_miner.py --step filter --model gemma2:27b --score-threshold 7.0
```
The checkpoint will be automatically loaded and processing will continue.

## Tips for Best Results

1. **Start Small**: Test with `--max-results 20` before large batches
2. **Use Screen**: Always run in screen/tmux for SSH sessions
3. **Adjust Threshold**: Lower threshold (6.0) for more papers, higher (8.0) for only highly relevant
4. **Query Type**: Use `training` for education research, `broad` for general ASP
5. **Monitor GPU**: Check `nvidia-smi` to ensure GPU is being used
6. **Review Scores**: Check filtered papers to calibrate threshold

## Performance Expectations

### With RTX A6000 (GPU)
- Search: ~1 minute for 500 papers
- Filtering: ~2-3 minutes for 100 papers
- PDF Finding: ~30 seconds for 50 papers
- Download: ~2 minutes for 20 PDFs

### Full Pipeline (500 papers)
- Total time: ~15-20 minutes
- Expected filtered: 50-100 papers (depending on threshold)
- Expected PDFs: 10-30 (varies by open access availability)

## Citation

If you use this tool in your research, please cite:

```
ASP AI Agent Literature Mining Tool
Cincinnati Children's Hospital Medical Center
Powered by gemma2:27b via Ollama
```

## Support

For issues or questions:
1. Run `python test_gemma_setup.py` to diagnose setup problems
2. Check screen session output for error messages
3. Review `download_failures.csv` for PDF download issues
4. Examine `filter_checkpoint.json` if filtering was interrupted

## Future Enhancements

Planned features:
- Multi-GPU support for parallel processing
- Custom scoring criteria via config file
- Integration with reference managers (Zotero, Mendeley)
- PDF text extraction and analysis
- Citation network analysis

---

**Last Updated**: November 2, 2025
**Version**: 1.0
**Model**: gemma2:27b (14.6 GB)
**Hardware**: NVIDIA RTX A6000 (48GB VRAM)
