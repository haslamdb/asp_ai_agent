# Sample AI Feedback Scenarios for Expert Review

Use these samples to test your Google Form and get your first expert corrections.

---

## Sample 1: Beginner Data Analysis

### Context
- **Module**: cicu_prolonged_antibiotics
- **Scenario**: cicu_beginner_data_analysis
- **Difficulty**: beginner
- **Competency**: data_analysis

### Scenario Description
You're a new ASP fellow reviewing antibiotic use in the cardiac ICU. You notice that meropenem and vancomycin are frequently used for prolonged durations. The CICU director has asked you to analyze the data and present findings.

### Fellow's Response
```
I would start by calculating the DOT (days of therapy) for the CICU to understand
our baseline antibiotic use. Then I'd compare it to national benchmarks to see
if we're using too many antibiotics. If we are, I'd work with the team to reduce use.
```

### AI-Generated Feedback
```
Good approach! You've identified the key metric (DOT) and the importance of
benchmarking. Calculating DOT and comparing to national standards is the right
first step for antimicrobial stewardship data analysis.

Your plan to "work with the team" shows awareness of the collaborative nature
of ASP interventions.

To strengthen this response:
- Consider which specific benchmark you'd use (NHSN, SHARPS, or institution-specific)
- Think about how you'd present the data to make it compelling
- What timeframe would you analyze?

Overall, this is a solid foundational approach. Score: 3/5
```

### What an Expert Might Say

**Expert Correction Example:**
```
You're on the right track identifying DOT as the key metric, but let's make this
concrete. When you say "calculate DOT," show me you know the formula:

DOT per 1000 patient-days = (Total antibiotic days / Total patient days) × 1000

Now apply it: If the CICU had 450 meropenem days and 1000 total patient days
last quarter, what's your DOT/1000 PD? That's 450 DOT/1000 PD.

Which benchmark would you use? For a cardiac ICU, I'd recommend NHSN PICU data
since there's no cardiac-specific benchmark. Their 50th percentile is ~380 DOT/1000 PD.
So you're 70 days above benchmark—that's your gap to present.

The phrase "work with the team" is too vague. Who specifically? The CICU medical
director? Nurse manager? Fellows? Each needs different data. What format? Email?
Dashboard? Run chart? Be specific about your dissemination plan.

Try rewriting with actual numbers and named stakeholders.
```

**What AI Missed:**
- Requiring the actual DOT formula
- Pushing for calculated numbers, not just concepts
- Asking which specific benchmark source
- Challenging "work with the team" as too vague
- Requesting concrete dissemination plan

**What AI Did Well:**
- Acknowledged correct general direction
- Positive, encouraging tone
- Mentioned benchmarking importance

---

## Sample 2: Intermediate Behavioral Intervention

### Context
- **Module**: cicu_prolonged_antibiotics
- **Scenario**: cicu_intermediate_intervention
- **Difficulty**: intermediate
- **Competency**: behavioral_intervention

### Scenario Description
Your data shows CICU antibiotic use is 40% above benchmark. You need to design an intervention to change prescribing behavior. What's your approach?

### Fellow's Response
```
I would create an educational intervention for the CICU prescribers. I'd present
the data showing we're above benchmark and provide guidelines on appropriate
antibiotic duration. I'd also offer to consult on complex cases to help them
feel supported in de-escalating antibiotics.
```

### AI-Generated Feedback
```
Excellent - you've identified education as a key component! Presenting data and
providing guidelines are evidence-based approaches to changing prescriber behavior.

Your offer to consult shows good clinical judgment and addresses the common barrier
of uncertainty about de-escalation.

To enhance this intervention:
- Consider how you'd deliver the education (didactic? Case-based? At the point of care?)
- Think about sustainability - what happens after the initial education?
- How would you measure success?

This demonstrates good understanding of behavioral interventions. Score: 4/5
```

### What an Expert Might Say

**Expert Correction Example:**
```
Stop right there. Education alone achieves only 15-20% behavior change in antimicrobial
stewardship (Davey et al., 2017, Cochrane Review). If this is your only intervention,
you'll likely fail.

Which behavior change framework are you using? COM-B? Social Cognitive Theory?
The Theory of Planned Behavior? You need a theory-driven approach.

Let's break this down using COM-B:
- **Capability**: Yes, education helps, but make it case-based, not didactic.
  Can you embed teaching into their workflow?
- **Opportunity**: Who are the CICU opinion leaders? Which attending is most
  respected? You need them as champions. Also, what's the EHR workflow? Can you
  add decision support at the point of prescribing?
- **Motivation**: Prescribers are driven by commission bias - "better safe than sorry."
  How will you address their fear of stopping antibiotics? Audit and feedback with
  peer comparison is more effective than education. Show them "Dr. Smith stopped
  antibiotics at 48 hours in 60% of cases with no adverse events."

Your "consult offer" is good but won't scale. What happens when you're not there?
You need to build systems, not create dependency.

Rewrite your intervention using COM-B and tell me specific tactics for each domain.
```

**What AI Missed:**
- Citing evidence that education alone is insufficient (~15% effectiveness)
- Requiring a behavior change framework (COM-B, etc.)
- Addressing cognitive biases (commission bias)
- Questioning scalability of consult-based approach
- Pushing for peer comparison/audit-feedback
- Asking about opinion leaders and champions
- Challenging the assumption that education = behavior change

**What AI Did Well:**
- Nothing significant - the AI was too permissive and didn't challenge the weak intervention

---

## Sample 3: Advanced Implementation Science

### Context
- **Module**: cicu_prolonged_antibiotics
- **Scenario**: cicu_advanced_implementation
- **Difficulty**: advanced
- **Competency**: implementation_science

### Scenario Description
You've designed an intervention (guideline + audit-feedback) to reduce prolonged
meropenem use. How will you implement and spread this across the CICU?

### Fellow's Response
```
I would pilot the intervention in the CICU for 3 months, collect data on
de-escalation rates and clinical outcomes, then present results to leadership.
If successful, I'd implement hospital-wide. I'd track DOT monthly and share
results with the team.
```

### AI-Generated Feedback
```
Great! You've outlined a logical implementation sequence with a pilot phase
followed by spread. Collecting both process measures (de-escalation rates) and
outcome measures (clinical outcomes) shows sophisticated understanding.

Monthly tracking and result-sharing demonstrates commitment to continuous monitoring.

Consider adding:
- What would make you decide if the pilot was "successful"?
- How would you adapt the intervention for other ICUs (surgical ICU, medical ICU)?
- What sustainability plan would ensure this continues after you rotate off?

Strong implementation approach overall. Score: 4/5
```

### What an Expert Might Say

**Expert Correction Example:**
```
You're missing the entire implementation science framework. "Pilot for 3 months
then implement hospital-wide" is not a plan—it's a recipe for failure.

Use PDSA cycles or the CFIR framework. Here's what's missing:

**Timeline specificity**:
- What happens in Week 1-2? (Baseline data collection? Stakeholder meetings?)
- Week 3-4? (Pilot in ONE pod, not whole CICU)
- Week 5-8? (Refinement based on barriers encountered)
- Week 9-12? (Spread to other pods with local adaptation)

**Sustainability plan**:
- Who owns this after you rotate?
- How do you embed it in fellow onboarding?
- What triggers re-measurement (annual? When new attendings join?)

**Balancing measures**:
You mentioned clinical outcomes, but which? I want to see:
- Process: De-escalation rate (target: 60% within 48h)
- Outcome: Late-onset sepsis (should NOT increase)
- Balancing: ICU length of stay, mortality (should not worsen)
- Leading indicator: Guideline adherence (% following the protocol)

**Spread strategy**:
"Hospital-wide" is too vague. Each ICU has different culture, patient population,
and prescribing patterns. How would you adapt?
- SICU: Different organisms, surgical prophylaxis mindset
- MICU: Multi-organ failure, longer appropriate durations
- PICU: Different dosing, different organisms

You need a dissemination plan with champions in EACH unit, not one-size-fits-all.

**Context assessment (CFIR)**:
- What are the barriers in YOUR CICU? (Nurse pushback? Attending resistance?
  EHR limitations?)
- How would you assess readiness to change?
- Which implementation strategies match your identified barriers?

Rewrite with a phased timeline, specific metrics for success/failure, and a
context-sensitive spread plan.
```

**What AI Missed:**
- Requiring specific implementation science framework (PDSA, CFIR)
- Demanding week-by-week timeline, not just "3 months"
- Challenging "hospital-wide" as too simplistic
- Requiring balancing measures, not just outcomes
- Asking about sustainability and ownership
- Pushing for barrier assessment and local adaptation
- Questioning how "success" is defined quantitatively
- Addressing cultural differences between ICU types

**What AI Did Well:**
- Acknowledged process vs. outcome measures distinction
- Mentioned sustainability (but didn't push hard enough)

---

## How to Use These Samples

### For Testing Your Google Form:
1. Copy Sample 1 into your Google Form as a test submission
2. Fill in your own expert correction
3. Verify the form captures all fields correctly
4. Export to CSV and test the import script

### For Your First Expert Reviews:
1. Send your expert reviewers the link to your Google Form
2. Include these scenarios in an email or Word doc
3. Ask them to review 1-2 scenarios (not all 3 - that's too much)
4. They copy the Fellow's Response and AI Feedback into the form
5. They write their expert correction

### Sample Email to Experts:

```
Subject: Quick Expert Review - 10 minutes (ASP AI Feedback)

Hi Dr. [Name],

Could you spend 10 minutes reviewing AI-generated feedback for my ASP teaching tool?

Please review Sample 1 below:
[Paste Sample 1 content here]

Then complete this quick form with your expert correction:
[Your Google Form Link]

What to do:
1. Read the scenario, fellow's response, and AI feedback above
2. Click the form link
3. Fill in the context fields (already filled below if you copy-paste):
   - Module: cicu_prolonged_antibiotics
   - Scenario: cicu_beginner_data_analysis
   - Difficulty: beginner
   - Competency: data_analysis
4. Paste the fellow's response and AI feedback
5. Write what YOU would say instead
6. Note what the AI missed

That's it! Takes ~10 minutes.

Thanks so much!
[Your name]
```

---

## Expected Timeline

### Week 1: Setup
- Create Google Form
- Test with these samples
- Send to 2-3 expert reviewers

### Week 2: Collect
- Experts complete 1-2 reviews each
- Goal: 5-10 initial corrections

### Week 3: Import & Test
- Export CSV from Google Sheets
- Import: `python add_expert_knowledge.py corrections file.csv`
- Test enhanced feedback generation
- Compare to baseline

### Week 4: Iterate
- Collect 10 more corrections
- Import and re-test
- Measure improvement in feedback quality

---

## Success Metrics

After importing your first batch of expert corrections, measure:

✅ **Retrieval accuracy**: Do similar scenarios retrieve relevant corrections?
```python
from expert_knowledge_rag import ExpertKnowledgeRAG
rag = ExpertKnowledgeRAG()
corrections = rag.retrieve_corrections(
    scenario_id='cicu_beginner_data_analysis',
    user_response='I would calculate DOT',
    n_results=3
)
# Should retrieve Sample 1's correction
```

✅ **Prompt enhancement**: Does the enhanced prompt include expert patterns?
```python
from enhanced_feedback_generator import EnhancedFeedbackGenerator
gen = EnhancedFeedbackGenerator()
result = gen.generate_feedback(
    module_id='cicu_prolonged_antibiotics',
    scenario_id='cicu_beginner_data_analysis',
    user_response='I would calculate DOT and compare to benchmarks',
    difficulty_level='beginner'
)
print(result['sources'])  # Should show corrections_used > 0
```

✅ **Quality improvement**: Expert review of new AI feedback with enhanced prompts
- Baseline: 3.2/5 average expert rating
- Target after 20 corrections: 4.0/5 average expert rating

---

**Ready to start?**

1. Create your Google Form using `GOOGLE_FORM_EXPERT_REVIEW_GUIDE.md`
2. Send Sample 1 or 2 to your first expert reviewer
3. Import their corrections and test!
