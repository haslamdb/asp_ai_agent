#!/usr/bin/env python3

# Test RAG type logic
rag_types = ['none', 'literature', 'expert', 'both', 'pubmed', 'both_pubmed']

for rag_type in rag_types:
    use_literature = rag_type in ['literature', 'both', 'pubmed', 'both_pubmed']
    use_expert_knowledge = rag_type in ['expert', 'both', 'both_pubmed']
    force_pubmed = rag_type in ['pubmed', 'both_pubmed']
    
    # Assuming enhanced_feedback_gen exists (is not None)
    enhanced_feedback_gen = True
    would_use_enhanced = enhanced_feedback_gen and not force_pubmed
    
    print(f"\nrag_type: {rag_type}")
    print(f"  force_pubmed: {force_pubmed}")
    print(f"  would_use_enhanced_feedback_gen: {would_use_enhanced}")
    print(f"  would_use_pubmed_fallback: {not would_use_enhanced}")
