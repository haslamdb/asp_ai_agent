# Retrieval-Augmented Generation (RAG) Explained

## A Guide to How We Enhance AI Responses with Domain-Specific Literature

---

## Table of Contents

1. [What is RAG?](#what-is-rag)
2. [Why RAG Matters](#why-rag-matters)
3. [How Our RAG System Works](#how-our-rag-system-works)
   - [Phase 1: Indexing (One-Time Setup)](#phase-1-indexing-one-time-setup)
   - [Phase 2: Query Processing (Every Question)](#phase-2-query-processing-every-question)
4. [The Key Insight: Why RAG Beats Memory Alone](#the-key-insight-why-rag-beats-memory-alone)
5. [Technical Details of Our Implementation](#technical-details-of-our-implementation)
6. [Limitations and Considerations](#limitations-and-considerations)
7. [Summary](#summary)

---

## What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that enhances AI language model responses by providing relevant source documents at query time. Instead of relying solely on what the AI "remembers" from training, we give it specific, relevant excerpts from our curated literature database to reference when answering questions.

Think of it as the difference between:
- **Asking an expert to answer from memory** (what they vaguely recall from years of reading)
- **Asking an expert to answer with their notes open** (referencing specific sources as they respond)

---

## Why RAG Matters

Large Language Models (LLMs) like Claude, GPT, or Gemini are trained on vast amounts of text, but they have significant limitations:

| Limitation | Problem | How RAG Helps |
|------------|---------|---------------|
| **Knowledge cutoff** | Training data has a fixed date; newer publications aren't included | RAG injects current literature at query time |
| **Fuzzy memory** | Training compresses information into statistical patterns, losing precision | RAG provides exact text to reference |
| **No citations** | LLMs can't cite specific sources from training | RAG enables citation of specific PMIDs and sources |
| **Hallucination risk** | LLMs may confidently state incorrect information | RAG grounds responses in provided evidence |
| **Domain gaps** | Specialized literature may be underrepresented in training | RAG supplements with domain-specific content |

---

## How Our RAG System Works

Our system operates in two phases: **Indexing** (done once per document) and **Query Processing** (done for each question).

### Phase 1: Indexing (One-Time Setup)

When we add new literature to our database, each document goes through a pipeline:

```
PDF Document
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: TEXT EXTRACTION                                    │
│                                                             │
│  PyPDF extracts raw text from the PDF                       │
│  • Captures paragraphs, headings, and body text             │
│  • Tables and figures may not extract cleanly               │
│  • Result: Plain text version of the document               │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: CHUNKING                                           │
│                                                             │
│  Long documents are split into smaller pieces               │
│  • Each chunk: ~300 words (600 tokens)                      │
│  • Chunks overlap by ~100 tokens                            │
│  • Overlap prevents losing context at boundaries            │
│  • A 20-page paper becomes ~30-50 chunks                    │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: EMBEDDING GENERATION                               │
│                                                             │
│  Each chunk is converted to a numerical vector              │
│  • We use the BAAI/bge-large-en embedding model             │
│  • Each chunk becomes 1,024 numbers (a "vector")            │
│  • These numbers capture semantic meaning                   │
│  • Similar concepts → similar vectors                       │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: STORAGE                                            │
│                                                             │
│  ChromaDB stores three things for each chunk:               │
│  • The original text                                        │
│  • The 1,024-dimensional embedding vector                   │
│  • Metadata (PMID, title, authors, journal, year)           │
└─────────────────────────────────────────────────────────────┘
```

#### What is an Embedding?

An embedding converts text into a list of numbers that captures its meaning. Similar concepts end up with similar numbers:

```
"Ventilator-associated pneumonia diagnostic criteria"
    → [0.023, -0.087, 0.142, ..., 0.056]  (1,024 numbers)

"VAP diagnosis guidelines"
    → [0.025, -0.082, 0.138, ..., 0.061]  (very similar!)

"Pizza recipes"
    → [-0.156, 0.234, -0.012, ..., 0.189]  (very different)
```

This allows us to find semantically related content even when exact keywords don't match.

---

### Phase 2: Query Processing (Every Question)

When a user asks a question, the system retrieves relevant literature and injects it into the prompt:

```
User's Question: "What are the diagnostic criteria for VAP?"
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: EMBED THE QUERY                                    │
│                                                             │
│  The question is converted to a vector using the same       │
│  embedding model used during indexing                       │
│                                                             │
│  "What are the diagnostic criteria for VAP?"                │
│      → [0.019, -0.091, 0.145, ..., 0.052]                   │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: VECTOR SIMILARITY SEARCH                           │
│                                                             │
│  ChromaDB compares the query vector against all stored      │
│  chunk vectors (10,779 in our database)                     │
│                                                             │
│  Uses cosine similarity: How much do vectors point          │
│  in the same direction?                                     │
│                                                             │
│  Returns the top 10-20 most similar chunks                  │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: BUILD AUGMENTED PROMPT                             │
│                                                             │
│  The retrieved chunks are inserted into the prompt:         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ You are an expert antimicrobial stewardship           │  │
│  │ consultant providing evidence-based guidance...       │  │
│  │                                                       │  │
│  │ **RELEVANT RESEARCH EVIDENCE:**                       │  │
│  │                                                       │  │
│  │ [1] PMID 18426596: "VAP requires new or progressive   │  │
│  │ radiographic infiltrate plus at least two of three    │  │
│  │ clinical features: fever >38°C, leukocytosis..."      │  │
│  │                                                       │  │
│  │ [2] PMID 32306086: "The diagnosis of VAP in           │  │
│  │ critically ill patients remains challenging..."       │  │
│  │                                                       │  │
│  │ **USER'S QUESTION:**                                  │  │
│  │ What are the diagnostic criteria for VAP?             │  │
│  │                                                       │  │
│  │ Cite sources using PMID numbers when referencing      │  │
│  │ the evidence above.                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: SEND TO LLM                                        │
│                                                             │
│  The augmented prompt is sent to the language model         │
│  (Claude, Gemini, or a local model like Llama)              │
│                                                             │
│  The LLM generates a response that:                         │
│  • References the provided evidence                         │
│  • Cites specific PMIDs                                     │
│  • Is grounded in the retrieved literature                  │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
Evidence-Based Response with Citations
```

---

## The Key Insight: Why RAG Beats Memory Alone

This is the most important concept to understand:

**Training data is stored as compressed statistical patterns across billions of parameters—it's not like a database where the LLM can "look up" a paper.**

### The Difference in Practice

**What the LLM "remembers" from training (fuzzy, compressed):**
```
"VAP... something about 48 hours... ventilator... infiltrate...
 fever... maybe leukocytosis?... was it NHSN or IDSA guidelines?..."
```

**What RAG provides (exact, verifiable):**
```
"VAP: A pneumonia where the patient is on mechanical ventilation
 for > 2 consecutive calendar days on the date of event, with day
 of ventilator placement being Day 1, AND the ventilator was in
 place on the date of event or the day before."

 — NHSN Guidelines, January 2025
```

### An Expert Analogy

| Scenario | Quality of Response |
|----------|---------------------|
| **Expert answering from memory** | "I remember reading something about VAP criteria... I think it was around 48 hours on a vent, some clinical signs..." (vague, may contain errors) |
| **Expert with notes in hand** | "Let me reference the exact criteria—according to the NHSN 2025 guidelines, VAP requires >2 calendar days of mechanical ventilation plus these specific clinical criteria..." (precise, verifiable) |

The expert "knows" the content either way, but having source material in front of them produces a better, more accurate response.

### Why RAG Responses Are Better

Even when the LLM was trained on the same literature, RAG improves responses because:

| Factor | Without RAG | With RAG |
|--------|-------------|----------|
| **Precision** | Approximate, may misremember numbers | Exact wording and statistics |
| **Citations** | "Studies show..." (no specifics) | "According to Smith et al. (PMID 12345678)..." |
| **Confidence** | Hedges with "generally," "approximately" | Can make definitive statements |
| **Accuracy** | May conflate studies or invent details | Constrained to provided evidence |
| **Currency** | Limited to training cutoff date | Can include papers published yesterday |

---

## Technical Details of Our Implementation

### Our Current System Statistics

| Component | Specification |
|-----------|---------------|
| **Indexed papers** | 328 unique publications |
| **Total chunks** | 10,779 |
| **Average chunk size** | ~300 words (~2,100 characters) |
| **Embedding model** | BAAI/bge-large-en |
| **Embedding dimensions** | 1,024 |
| **Vector database** | ChromaDB |
| **Storage size** | ~250 MB |

### The Embedding Model

We use **BAAI/bge-large-en** (Beijing Academy of AI, General Embedding), which:
- Produces 1,024-dimensional vectors
- Is optimized for English text retrieval
- Captures semantic meaning, not just keywords
- Normalizes vectors for cosine similarity search

### Chunk Configuration

```
Chunk size:    600 tokens (~300 words)
Overlap:       100 tokens
```

The overlap ensures that if an important concept spans a chunk boundary, it appears in both chunks and won't be missed.

### Search Parameters

```
Results retrieved:     12-20 chunks per query
Minimum similarity:    0.35 (35% match threshold)
Deduplication:         By PMID to avoid repeating the same paper
```

---

## Limitations and Considerations

### 1. Garbage In, Garbage Out
If PDF text extraction produces garbled output (common with tables, figures, or complex layouts), the embeddings will be noisy and retrieval quality suffers.

### 2. Semantic ≠ Authoritative
A review paper discussing VAP may rank higher than official CDC guidelines because it contains more prose about "diagnostic criteria." The embedding model doesn't know which source is more authoritative.

### 3. Context Window Limits
LLMs have a maximum input size. We can only inject ~12 chunks before hitting limits, so important papers may be excluded if they don't rank in the top results.

### 4. No Understanding of Document Structure
Embeddings don't understand that "Table 2" contains the actual diagnostic criteria. They just see text, which may include table headers, footnotes, and formatting artifacts.

### 5. Retrieval Depends on Query Formulation
Searching for "PMID 39945582" won't find the paper semantically—the embedding model doesn't know that string of numbers refers to a specific paper. (We've added special handling for PMID lookups to address this.)

---

## Summary

**RAG (Retrieval-Augmented Generation)** enhances AI responses by:

1. **Indexing** domain-specific literature as searchable embeddings
2. **Retrieving** relevant excerpts when a question is asked
3. **Injecting** those excerpts into the prompt sent to the LLM
4. **Grounding** the response in specific, citable evidence

The result is responses that are:
- More **precise** (exact text, not fuzzy memories)
- More **current** (not limited by training cutoff)
- More **verifiable** (includes citations)
- More **accurate** (reduced hallucination)
- More **domain-specific** (tailored to your literature collection)

RAG doesn't replace the LLM's knowledge—it supplements it with a focused, curated knowledge base that the LLM can reference directly, like an expert answering questions with their library open in front of them.

---

## Appendix: The Complete RAG Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INDEXING PHASE (One-Time)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   PDF Library                                                           │
│       │                                                                 │
│       ▼                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────┐ │
│   │ Extract │ -> │  Chunk  │ -> │  Embed  │ -> │   Store in ChromaDB │ │
│   │  Text   │    │  Text   │    │ (1024d) │    │   (text + vectors)  │ │
│   └─────────┘    └─────────┘    └─────────┘    └─────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        QUERY PHASE (Every Question)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   User Question                                                         │
│       │                                                                 │
│       ├──────────────────────────────────┐                              │
│       ▼                                  │                              │
│   ┌─────────┐    ┌─────────────────┐     │                              │
│   │  Embed  │ -> │ Search ChromaDB │     │                              │
│   │  Query  │    │ (similarity)    │     │                              │
│   └─────────┘    └────────┬────────┘     │                              │
│                           │              │                              │
│                           ▼              │                              │
│                  ┌─────────────────┐     │                              │
│                  │ Top 12 Relevant │     │                              │
│                  │     Chunks      │     │                              │
│                  └────────┬────────┘     │                              │
│                           │              │                              │
│                           ▼              ▼                              │
│                  ┌─────────────────────────────┐                        │
│                  │    BUILD AUGMENTED PROMPT   │                        │
│                  │  ┌───────────────────────┐  │                        │
│                  │  │ Instructions          │  │                        │
│                  │  │ + Retrieved Chunks    │  │                        │
│                  │  │ + User Question       │  │                        │
│                  │  └───────────────────────┘  │                        │
│                  └──────────────┬──────────────┘                        │
│                                 │                                       │
│                                 ▼                                       │
│                  ┌─────────────────────────────┐                        │
│                  │     SEND TO LLM (Claude,    │                        │
│                  │     Gemini, or Local)       │                        │
│                  └──────────────┬──────────────┘                        │
│                                 │                                       │
│                                 ▼                                       │
│                  ┌─────────────────────────────┐                        │
│                  │  Evidence-Based Response    │                        │
│                  │     with Citations          │                        │
│                  └─────────────────────────────┘                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*Document created: November 2025*
*ASP AI Agent - Antimicrobial Stewardship Training System*
