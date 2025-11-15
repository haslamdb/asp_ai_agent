# Expert Knowledge Embeddings

This directory contains ChromaDB vector embeddings for the Expert Knowledge RAG system.

## Purpose

The Expert Knowledge RAG complements the literature-based RAG by indexing:

1. **Expert Corrections** - When experts review and correct AI-generated feedback
2. **Exemplar Responses** - Gold standard answers at different mastery levels
3. **Teaching Patterns** - Common pedagogical approaches used by expert educators
4. **Rubric Examples** - Concrete examples of how rubric criteria are applied

## Structure

Once populated, this directory will contain ChromaDB collections:

```
expert_embeddings/
├── chroma.sqlite3              # ChromaDB metadata database
├── expert_corrections/         # Expert feedback corrections collection
├── exemplar_responses/         # Gold standard responses collection
└── teaching_patterns/          # Common teaching pattern collection
```

## Data Sources

Expert knowledge is collected through:
- Expert panel review of AI feedback (Phase 1)
- Fellow pilot study with expert evaluation (Phase 2)
- Continuous in-app feedback collection (Phase 4)

## Implementation

The Expert Knowledge RAG is implemented in `expert_knowledge_rag.py` (planned) and uses:
- **Embedding Model**: pritamdeka/S-PubMedBert-MS-MARCO (same as literature RAG)
- **Vector Database**: ChromaDB (persistent client)
- **Dimensionality**: 768 (PubMedBERT)

## Usage

Expert knowledge is retrieved contextually during feedback generation to:
- Show AI how experts have corrected similar feedback in the past
- Reference teaching patterns relevant to the current scenario
- Compare user responses to exemplar responses at different mastery levels

## Status

🚧 **Planned** - Will be populated during Phase 2 (Pilot Study) and Phase 3 (Iterative Improvement)

Target: 50+ expert corrections indexed by end of Phase 3

## Related Documentation

- [Expert Knowledge RAG System Guide](../../docs/Setting%20Up%20the%20Expert%20Knowledge%20RAG%20System.docx)
- [Feedback Collection Protocol](../../docs/Structured%20Approach%20for%20Collecting%20Feedback.docx)
- [Fine Tuning Strategy](../../docs/Fine%20Tuning%20the%20Model.docx)
