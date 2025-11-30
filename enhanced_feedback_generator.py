#!/usr/bin/env python3
"""
Enhanced Feedback Generator with Hybrid RAG
Combines literature RAG (research papers) and expert knowledge RAG (corrections/exemplars)
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

# Import both RAG systems
from asp_rag_module import ASPLiteratureRAG
from expert_knowledge_rag import ExpertKnowledgeRAG


class EnhancedFeedbackGenerator:
    """
    Generates feedback using both literature RAG and expert knowledge RAG
    Implements the layered approach recommended in documentation:
    1. Prompt Engineering (90% of effort) - primary strategy
    2. RAG Enhancement - retrieve relevant expert and literature context
    3. Output Validation - ensure quality and completeness
    """

    def __init__(self):
        """Initialize both RAG systems"""
        print("🚀 Initializing Enhanced Feedback Generator")

        # Initialize Literature RAG (existing)
        try:
            self.literature_rag = ASPLiteratureRAG()
            print("✓ Literature RAG loaded")
        except Exception as e:
            print(f"⚠ Warning: Could not load Literature RAG: {e}")
            self.literature_rag = None

        # Initialize Expert Knowledge RAG (new)
        try:
            self.expert_rag = ExpertKnowledgeRAG()
            print("✓ Expert Knowledge RAG loaded")
        except Exception as e:
            print(f"⚠ Warning: Could not load Expert Knowledge RAG: {e}")
            self.expert_rag = None

        print("✅ Enhanced Feedback Generator ready\n")

    def generate_feedback(
        self,
        module_id: str,
        scenario_id: str,
        user_response: str,
        difficulty_level: str,
        competency_areas: List[str] = None,
        use_expert_knowledge: bool = True,
        use_literature: bool = True,
        mode: str = "evaluation"
    ) -> Dict:
        """
        Generate comprehensive feedback using all available knowledge sources

        Args:
            module_id: e.g., 'cicu_prolonged_antibiotics'
            scenario_id: e.g., 'cicu_beginner_data_analysis'
            user_response: Fellow's response text (evaluation mode) or question (qa mode)
            difficulty_level: 'beginner', 'intermediate', 'advanced', 'expert'
            competency_areas: List of competencies to evaluate
            use_expert_knowledge: Whether to retrieve expert corrections/exemplars
            use_literature: Whether to retrieve relevant research papers
            mode: 'evaluation' (assess student response) or 'qa' (answer question directly)

        Returns:
            Dict with feedback, sources, and metadata
        """
        if not competency_areas:
            competency_areas = [
                'data_analysis',
                'behavioral_intervention',
                'implementation_science',
                'clinical_decision_making'
            ]

        print(f"📝 Generating feedback for: {scenario_id} ({difficulty_level})")

        # ====================================================================
        # STEP 1: Retrieve relevant expert knowledge
        # ====================================================================
        expert_corrections = []
        expert_exemplars = []

        if use_expert_knowledge and self.expert_rag:
            print("→ Retrieving expert knowledge...")

            # Get relevant expert corrections (similar scenarios where experts corrected AI)
            for competency in competency_areas:
                corrections = self.expert_rag.retrieve_corrections(
                    scenario_id=scenario_id,
                    user_response=user_response,
                    competency_area=competency,
                    difficulty_level=difficulty_level,
                    n_results=2  # Top 2 per competency
                )
                expert_corrections.extend(corrections)

            # Get exemplar responses for target mastery level
            target_mastery = self._map_difficulty_to_mastery(difficulty_level)
            expert_exemplars = self.expert_rag.retrieve_exemplars(
                scenario_id=scenario_id,
                mastery_level=target_mastery,
                n_results=2
            )

            print(f"  ✓ Found {len(expert_corrections)} relevant corrections")
            print(f"  ✓ Found {len(expert_exemplars)} exemplar responses")

        # ====================================================================
        # STEP 2: Retrieve relevant literature
        # ====================================================================
        literature_results = []

        if use_literature and self.literature_rag:
            print("→ Retrieving relevant literature...")

            # Use the actual user question/response as the primary search query
            # This is much more effective than generic module-based queries
            primary_query = user_response[:500]  # Limit length for embedding

            try:
                # Primary search using user's actual question
                # INCREASED: n_results to 50 - we're only using ~4% of context window
                results = self.literature_rag.search(primary_query, n_results=50, min_similarity=0.35)
                literature_results.extend(results)
            except Exception as e:
                print(f"  Warning: Primary search failed: {e}")

            # If we didn't find enough results, try module-based fallback queries
            if len(literature_results) < 3:
                literature_queries = self._generate_literature_queries(
                    module_id, difficulty_level
                )
                for query in literature_queries[:1]:  # Just one fallback query
                    try:
                        results = self.literature_rag.search(query, n_results=10, min_similarity=0.35)
                        literature_results.extend(results)
                    except:
                        pass

            # Deduplicate by PMID (but only if PMID exists)
            seen_pmids = set()
            seen_filenames = set()
            unique_results = []
            for result in literature_results:
                pmid = result.get('pmid', '')
                filename = result.get('filename', '')

                # Use PMID if available, otherwise use filename
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    unique_results.append(result)
                elif not pmid and filename not in seen_filenames:
                    seen_filenames.add(filename)
                    unique_results.append(result)
            literature_results = unique_results[:40]  # Keep top 40 (using ~15% of context window)

            print(f"  ✓ Found {len(literature_results)} relevant papers")

        # ====================================================================
        # STEP 3: Build enhanced prompt with all context
        # ====================================================================
        enhanced_prompt = self._build_enhanced_prompt(
            scenario_id=scenario_id,
            user_response=user_response,
            difficulty_level=difficulty_level,
            competency_areas=competency_areas,
            expert_corrections=expert_corrections,
            expert_exemplars=expert_exemplars,
            literature_results=literature_results,
            mode=mode
        )

        # ====================================================================
        # STEP 4: Generate feedback with LLM (placeholder)
        # ====================================================================
        # NOTE: This would call your actual LLM (Claude, Gemini, etc.)
        # For now, returning the enhanced prompt for testing
        feedback_text = f"[This is where LLM feedback would be generated using the enhanced prompt]\n\nPrompt preview:\n{enhanced_prompt[:500]}..."

        # ====================================================================
        # STEP 5: Return with sources and metadata
        # ====================================================================
        return {
            'feedback': feedback_text,
            'enhanced_prompt': enhanced_prompt,  # For testing/debugging
            'sources': {
                'expert_corrections_used': len(expert_corrections),
                'exemplars_shown': len(expert_exemplars),
                'literature_citations': len(literature_results)
            },
            'expert_corrections': expert_corrections,
            'expert_exemplars': expert_exemplars,
            'literature_sources': literature_results,  # Renamed for consistency
            'metadata': {
                'module_id': module_id,
                'scenario_id': scenario_id,
                'difficulty_level': difficulty_level,
                'timestamp': datetime.now().isoformat()
            }
        }

    def _build_enhanced_prompt(
        self,
        scenario_id: str,
        user_response: str,
        difficulty_level: str,
        competency_areas: List[str],
        expert_corrections: List[Dict],
        expert_exemplars: List[Dict],
        literature_results: List[Dict],
        mode: str = "evaluation"
    ) -> str:
        """
        Build comprehensive prompt with all retrieved knowledge

        Implements the refined prompt engineering strategy:
        - Specific persona and expertise cues
        - Concrete examples from expert corrections
        - Teaching patterns from experts
        - Evidence from literature
        """

        # Switch between QA mode and evaluation mode
        if mode == "qa":
            return self._build_qa_prompt(
                user_response=user_response,
                expert_corrections=expert_corrections,
                expert_exemplars=expert_exemplars,
                literature_results=literature_results
            )

        # Otherwise, use evaluation mode (original behavior)
        prompt = f"""You are an expert antimicrobial stewardship educator providing evidence-based
feedback on trainee responses. Your role is to evaluate responses rigorously using
published literature and established clinical guidelines. Avoid first-person anecdotes
or references to personal practice - focus on what the evidence shows.

# SCENARIO CONTEXT
Scenario ID: {scenario_id}
Difficulty Level: {difficulty_level}
Competency Areas: {', '.join(competency_areas)}

# FELLOW'S RESPONSE TO EVALUATE
{user_response}

---

# EXPERT KNOWLEDGE TO GUIDE YOUR EVALUATION
"""

        # Add expert corrections section
        if expert_corrections:
            prompt += f"""
## How Experts Have Corrected Similar Responses

You have access to {len(expert_corrections)} expert corrections of AI feedback
on similar responses. Here's what experts emphasized:

"""
            for i, corr in enumerate(expert_corrections[:3], 1):  # Top 3
                prompt += f"""
### Expert Correction {i}
**Scenario**: {corr['scenario_id']}
**What AI missed**: {', '.join(corr['what_ai_missed'])}
**Expert's feedback**: {corr['expert_correction'][:300]}...
**Reasoning**: {corr.get('expert_reasoning', 'N/A')}

"""

        # Add exemplars section
        if expert_exemplars:
            prompt += f"""
## What Exemplary Responses Look Like

Here are {len(expert_exemplars)} example(s) of high-quality responses:

"""
            for i, ex in enumerate(expert_exemplars, 1):
                prompt += f"""
### Exemplar {i} (Mastery: {ex['mastery_level']})
**Response excerpt**: {ex['response_text'][:400]}...
**What makes it good**: {', '.join(ex.get('what_makes_it_good', []))}
**Expert commentary**: {ex.get('expert_commentary', 'N/A')[:200]}

"""

        # Add literature section
        if literature_results:
            prompt += f"""
## Relevant Literature

Recent ASP research relevant to this scenario:

"""
            for i, paper in enumerate(literature_results, 1):
                prompt += f"""
### Paper {i}
**Source**: {paper.get('filename', 'N/A')}
**PMID**: {paper.get('pmid', 'N/A')}
**Excerpt**: {paper.get('text', 'N/A')[:200]}...

"""

        # Add evaluation instructions
        prompt += """
---

# YOUR TASK

Evaluate the fellow's response using your expertise, informed by the expert
knowledge and literature above. Specifically:

1. **Learn from expert corrections**: Pay attention to what experts emphasized
   that AI missed. Don't make the same mistakes.

2. **Compare to exemplars**: How does this response compare to exemplary responses?
   What's missing or could be stronger?

3. **Reference literature**: When relevant, cite specific findings from the
   ASP literature to support your feedback.

4. **Be specific and actionable**: Provide concrete next steps, not vague suggestions.
   Use Socratic questions to promote deeper thinking.

5. **Start with strengths**: Acknowledge what they did well before areas for improvement.

# OUTPUT FORMAT

Structure your feedback as follows:

## Strengths
[2-3 specific things they did well]

## Data Analysis
[Score: X/5]
[Specific feedback with examples from their response]

## Behavioral Intervention
[Score: X/5]
[Specific feedback with examples from their response]

## Implementation Science
[Score: X/5]
[Specific feedback with examples from their response]

## Clinical Decision Making
[Score: X/5]
[Specific feedback with examples from their response]

## Questions to Deepen Your Thinking
[2-3 Socratic questions]

## Next Steps
[2-3 concrete, actionable recommendations]

## Overall Assessment
[Brief summary and encouragement]

Provide your evaluation now.
"""

        return prompt

    def _build_qa_prompt(
        self,
        user_response: str,
        expert_corrections: List[Dict],
        expert_exemplars: List[Dict],
        literature_results: List[Dict]
    ) -> str:
        """
        Build prompt for Q&A mode - directly answer clinical questions with RAG enhancement

        Args:
            user_response: The clinical question to answer
            expert_corrections: Retrieved expert knowledge
            expert_exemplars: Retrieved exemplar responses
            literature_results: Retrieved literature citations

        Returns:
            Prompt string for Q&A mode
        """

        prompt = f"""You are an expert antimicrobial stewardship consultant providing evidence-based
clinical guidance. Your responses should be formal, objective, and grounded in published
literature and clinical guidelines. Do NOT use first-person statements like "in my experience,"
"at my institution," or "in my practice." Instead, cite what the literature shows and what
guidelines recommend.

# CLINICAL QUESTION
{user_response}

---

# KNOWLEDGE BASE TO INFORM YOUR ANSWER
"""

        # Add expert knowledge section
        if expert_corrections or expert_exemplars:
            prompt += """
## Expert Knowledge

"""
            if expert_corrections:
                prompt += f"Based on {len(expert_corrections)} expert correction(s) from similar cases:\n\n"
                for i, corr in enumerate(expert_corrections[:2], 1):
                    prompt += f"""**Expert Insight {i}:**
- Context: {corr.get('scenario_id', 'N/A')}
- Key points: {', '.join(corr.get('what_ai_missed', [])[:3])}
- Expert guidance: {corr.get('expert_correction', '')[:250]}...

"""

            if expert_exemplars:
                prompt += f"\nExemplary clinical approaches ({len(expert_exemplars)} example(s)):\n\n"
                for i, ex in enumerate(expert_exemplars[:2], 1):
                    prompt += f"""**Exemplar {i}:**
- {ex.get('response_text', '')[:200]}...
- What makes this approach strong: {', '.join(ex.get('what_makes_it_good', [])[:2])}

"""

        # Add literature section
        if literature_results:
            prompt += f"""
## Relevant Clinical Literature

Recent antimicrobial stewardship research ({len(literature_results)} citation(s)):

"""
            for i, paper in enumerate(literature_results, 1):
                pmid = paper.get('pmid', '')
                paper_id = paper.get('paper_id', f"doc_{i}") # Use paper_id or generated ID if no PMID
                
                prompt += f"""**Source [{i}]:**
**PMID/ID:** {pmid if pmid else paper_id}
**Title:** {paper.get('title', 'Unknown title')}
**Excerpt:**
{paper.get('text', 'N/A')[:350]}...

"""
        else:
            # NO LITERATURE CASE - Be explicit
            prompt += """
## Relevant Clinical Literature

**⚠️ NO SPECIFIC LITERATURE WAS PROVIDED FOR THIS QUESTION.**

The indexed literature database does not contain papers directly addressing this specific clinical question.

**YOU MUST NOT CREATE ANY CITATIONS OR REFERENCES.**
**DO NOT include a "References" section in your response.**
**State clearly that this answer is based on general clinical principles, not the indexed literature.**
"""
        
        # Add task instructions
        prompt += """
---

# YOUR TASK

Provide a direct, evidence-based answer to the clinical question above.

## Content Requirements:
1. **Answer the question directly** - Start with a clear, actionable answer
2. **Provide comprehensive detail** - Write 800-1000 words with thorough clinical context
3. **Reference the evidence** - Cite the expert knowledge and literature provided above using [1], [2], etc. CORRESPONDING to the Source numbers above.
4. **BE TRANSPARENT about evidence limitations** - If no specific literature was provided above, or if the provided literature doesn't directly address the question, include a disclaimer.
5. **Provide detailed clinical context** - When applicable, include:
   - Pathophysiology or mechanism
   - Diagnostic considerations
   - Treatment rationale and options
   - Key clinical decision points
   - Risk factors and complications
6. **Note limitations** - Mention any important caveats or situations where the answer might differ
7. **Be practical** - Focus on actionable clinical guidance with specific recommendations

## ⚠️ CRITICAL RULE - Academic Honesty (READ CAREFULLY):

**YOU ARE ABSOLUTELY FORBIDDEN FROM FABRICATING OR INVENTING CITATIONS.**

RULES YOU MUST FOLLOW:
1. **ONLY cite literature from the "Relevant Clinical Literature" section above**
2. **IF that section says "NO SPECIFIC LITERATURE WAS PROVIDED"**, then you MUST NOT create a references section.
3. **IF the provided literature exists**, you MUST use the exact "PMID/ID" strings provided.
4. **NEVER EVER** create references with fake author names, journals, or PMIDs.

**IF YOU VIOLATE THIS RULE, THE ENTIRE RESPONSE WILL BE CONSIDERED ACADEMICALLY DISHONEST.**

## Formatting Requirements:
Use clean, professional markdown formatting:

- Start with a **clear direct answer** (use bold for emphasis on key recommendation)
- Use **bullet points** for lists of considerations, alternatives, or key points
- Use **numbered lists** for sequential steps or hierarchical information
- Add **section headings** (##) for major topic changes if needed

### References Section Formatting (CRITICAL):
- **REQUIRED**: Create a "## **References**" section at the end (note the bold asterisks)
- **DO NOT** use bullet points for the references. They **MUST** be a numbered list.
- Format as a numbered list with each reference on a new line
- Add TWO blank lines before the References section
- **USE THE "PMID/ID" information provided in the literature section above.**
- Copy the complete PMID/ID from "PMID/ID:" - do NOT truncate or modify it.
- Each reference MUST start with its number followed by a period: "1. ", "2. ", "3. "
- Reference numbers must match in-text citations (e.g., [1], [2])
- DO NOT include "Source: filename.pdf" or partial URLs
- ONLY list the PMID/ID as the reference.

**CORRECT Reference Format:**
```
## **References**

1. PMID: 12345678
2. PMID: 87654321
3. doc_3
```

**INCORRECT formats (DO NOT USE):**
❌ "References" (not bold)
❌ "Source: p517.pdf" (filename instead of citation)
❌ Incomplete citations with authors, titles, journals.
❌ URLs or partial journal website addresses

- Use **bold** for important clinical terms or recommendations
- Keep paragraphs concise and scannable

**Example structure for a comprehensive response (800-2000 words):**
```
**Direct Answer:** [Clear, actionable answer to the question]

**Clinical Context:**

[3-4 paragraphs providing detailed background, pathophysiology, and clinical significance. Be comprehensive.]

**Evidence and Recommendations:**

[3-4 paragraphs discussing the evidence base in depth, citing the literature provided. Include specific recommendations with citations [1], [2]. Analyze the evidence strength.]

**Key Clinical Considerations:** (when applicable)

- **Diagnostic Workup:** [Detailed explanation]
- **Treatment Approach:** [Specific treatment recommendations]
- **Monitoring:** [What to watch for]
- **Risk Factors:** [Who is at higher risk]
- **Complications:** [What complications to watch for]

**Patient-Specific Factors:** (when applicable)

[Discuss how patient characteristics (age, comorbidities, etc.) might change management]

**Alternative Approaches:** (when applicable)

[When applicable, discuss alternative management strategies]


## **References** (Always include this section)

1. [PMID/ID from Source 1]
2. [PMID/ID from Source 2]
```"""

        return prompt

    def _generate_literature_queries(self, module_id: str, difficulty_level: str) -> List[str]:
        """Generate literature search queries based on module and difficulty"""
        base_queries = {
            'cicu_prolonged_antibiotics': [
                'antimicrobial stewardship cardiac ICU',
                'antibiotic de-escalation pediatric cardiac surgery',
                'broad-spectrum antibiotic reduction CICU'
            ]
        }

        # Get module-specific queries or use defaults
        queries = base_queries.get(module_id, [
            f'antimicrobial stewardship {difficulty_level}',
            'antibiotic stewardship interventions',
            'behavior change antimicrobial prescribing'
        ])

        return queries

    def _map_difficulty_to_mastery(self, difficulty: str) -> str:
        """Map difficulty level to expected mastery level"""
        mapping = {
            'beginner': 'developing',
            'intermediate': 'proficient',
            'advanced': 'proficient',
            'expert': 'exemplary'
        }
        return mapping.get(difficulty, 'developing')


def test_enhanced_feedback():
    """Test the enhanced feedback generator"""
    print("=" * 80)
    print("Enhanced Feedback Generator - Test")
    print("=" * 80 + "\n")

    # Initialize
    generator = EnhancedFeedbackGenerator()

    # Test scenario
    test_response = """
    I would start by calculating the DOT (days of therapy) for the CICU to understand
    our baseline antibiotic use. Then I'd compare it to national benchmarks to see
    if we're using too many antibiotics. If we are, I'd work with the team to reduce use.
    """

    print("\nTest: Generating feedback for beginner data analysis scenario\n")
    print("=" * 80)

    result = generator.generate_feedback(
        module_id='cicu_prolonged_antibiotics',
        scenario_id='cicu_beginner_data_analysis',
        user_response=test_response,
        difficulty_level='beginner',
        use_expert_knowledge=True,
        use_literature=True
    )

    print(f"\n✅ Feedback generated successfully!")
    print(f"\nSources used:")
    print(f" - Expert corrections: {result['sources']['expert_corrections_used']}")
    print(f" - Exemplar responses: {result['sources']['exemplars_shown']}")
    print(f" - Literature citations: {result['sources']['literature_citations']}")

    print(f"\n📄 Enhanced prompt preview:")
    print("=" * 80)
    print(result['enhanced_prompt'][:1000])
    print("\n... (truncated)")
    print("=" * 80)


if __name__ == "__main__":
    test_enhanced_feedback()
