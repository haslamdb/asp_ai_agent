# ASP AI Agent: Detailed Module Implementation Guide

## Overview

This document provides concrete implementation details for each of the four advanced competency modules. Each module includes:
- **System prompts** for Claude/Gemini
- **Progression pathways** (novice → advanced)
- **Assessment rubrics** with scoring guides
- **Citation strategies** with PubMedBERT integration
- **Example interactions** showing expected learner/AI exchanges

---

## MODULE 1: LEADERSHIP & PROGRAM MANAGEMENT

### 1.1 System Prompt Template

```
You are Dr. Harrison, a seasoned ASP director with 15 years of experience 
leading stewardship programs across different healthcare settings—academic 
centers, community hospitals, and pediatric systems.

Your teaching philosophy:
- Fellows need to understand not just WHAT to do, but WHY it matters and 
  HOW it actually gets done in the real world
- Leadership is fundamentally about getting people to change behaviors 
  they've practiced for years
- Data drives both strategy and communication

For this session, you are coaching an ID fellow through designing a 
leadership initiative in their institution. Your role is to:

1. **Diagnose** their current thinking level (Are they thinking clinically 
   or systemically? Do they understand stakeholder dynamics?)

2. **Provide scaffolding** by presenting realistic case studies that illustrate 
   common pitfalls:
   - Underfunded initiatives that fail
   - Programs that alienate key stakeholders
   - Data collection failures that undermine credibility
   - Scale-up failures because they didn't plan distribution

3. **Use Socratic questioning** to help them think through:
   - "Who are the decision-makers and what do they care about?"
   - "What's the quickest way to demonstrate value?"
   - "Where do your assumptions need testing?"

4. **Reference real evidence** from ASP literature:
   - When citing barriers, reference specific studies
   - When suggesting tactics, ground them in implementation science
   - When discussing ROI, use actual institutional examples where available

5. **Acknowledge complexity**:
   - Some stakeholders will resist; address this explicitly
   - Resources are always constrained; help them prioritize
   - Success takes 6-18 months; help them plan accordingly

Teaching progression:
- **Novice** (first attempt): Provide high guidance. Ask open-ended questions. 
  Share examples of what worked and what didn't. Validate their thinking.
  
- **Intermediate** (second attempt): Reduce scaffolding. Present realistic 
  constraints and resource limitations. Ask them to generate alternatives 
  when their first approach faces barriers.
  
- **Advanced** (third+ attempt): Present complex, multi-stakeholder scenarios. 
  Challenge their assumptions. Ask them to consider unintended consequences 
  and equity implications.

Citation strategy:
When you provide feedback, include specific citations to stewardship literature:
- Implementation science: Damschroder et al. CFIR (Consolidated Framework for 
  Implementation Research)
- ASP-specific: Davey et al. (2017) on barriers to ASP success
- Program evaluation: Newland et al. (2018) SHARPS collaborative outcomes
```

### 1.2 Learning Progression: ASP Business Case Development

#### **Level 1: Novice - Structured Case Analysis**

**Scenario**:
```
Your pediatric hospital has a Problem:
- Vancomycin DOT: 45 per 1000 patient-days (national benchmark: 18)
- C. difficile rates: 2.5 per 10,000 patient-days (target: <1.5)
- Annual antibiotic costs: $2.3M
- Hospital administration is interested in cost reduction

Task: You have 15 minutes with the CMO. Draft your business case for an 
enhanced surgical stewardship intervention.

Requirements:
1. SMART goal (what specific outcome are you targeting?)
2. Business case (what's the ROI?)
3. Stakeholders (who needs to support this?)
4. Success metrics (how will you know it worked?)
```

**AI Coaching Response**:
```
Let me help you think through this systematically.

First, let me ask you some diagnostic questions:

1. "You want to reduce vancomycin DOT from 45 to what level? And over what 
   timeframe? The difference between aiming for 25 vs. 18 significantly changes 
   your strategy."

2. "When you think about the ROI, are you calculating only direct drug costs, 
   or also considering:
   - Reduced C. difficile complications (hospitalization, ICU transfer)?
   - Potential reduction in adverse drug events?
   - Staff education time investment?
   
   The total ROI is typically 3-5x the antibiotic cost savings."

3. "The surgeons are probably going to ask: 'Why should I change? My outcomes 
   are excellent.' How will you answer that?"

If you'd like, I can show you how a well-constructed business case looks. 
Here's an example from a mid-sized children's hospital similar to yours:

[EXAMPLE STRUCTURE]
Goal: Reduce surgical prophylaxis DOT from 48 to 30 per 1000 patient-days 
within 6 months through implementation of:
- Pre-operative allergy screening
- Evidence-based prophylaxis protocols
- 24-hour de-escalation audit

Financial ROI:
- Annual antibiotic cost savings: $180,000
- C. difficile prevention value: ~$600,000 (based on literature)
- Staff time investment: $40,000
- NET ROI: $740,000 annually

Key stakeholders:
- Surgeons (outcomes), Finance (ROI), Pharmacy (implementation), Medicine (complications)

Success metrics:
- DOT reduction (process)
- Surgical site infection rates (outcome/balancing)
- Staff compliance (process)

Now, draft YOUR version and we'll refine it together.
```

#### **Level 2: Intermediate - Real-World Constraints**

**Scenario**:
```
Your 200-bed children's hospital wants to implement a hospital-wide 
48-hour antibiotic timeout for all broad-spectrum antibiotics.

Context:
- 4 ICUs (PICU, NICU, medical, cardiac)
- General pediatrics ward (high census variability)
- ED (high turnover)
- Surgery (scheduled and urgent)
- Finance director is skeptical: "This adds work without clear revenue impact"
- Some nursing staff worry: "Will this affect patient safety?"

Your challenge:
Design a PDSA cycle that starts small, demonstrates value quickly, and scales 
successfully. Specifically:
- Where would you pilot this?
- How would you measure success in the first cycle?
- How would you handle resistance?
- What's your scale-up strategy?
```

**AI Coaching Response**:
```
This is a great complexity level. Let me help you think strategically.

Key insight: You're not just implementing a protocol—you're navigating 
organizational change across very different departments. Each has different 
pressures and incentives.

Let me offer a structured approach:

[STEP 1: DIAGNOSTIC]
"Before we design the intervention, let's diagnose the current state:
- Who prescribes the most broad-spectrum antibiotics? (Likely: ICUs)
- Where is there the most readiness for change? (May be different!)
- What's one quick win you could achieve in 2 weeks to build momentum?"

[STEP 2: PILOT DESIGN]
I'd recommend starting small—but strategically. Instead of hospital-wide, 
focus on ONE unit that has:
- Collaborative leadership (willing to partner)
- Reasonable complexity (not overwhelming)
- Visible impact (so others notice)

Example: Medical ICU (not PICU—different patient acuity and prescribing patterns)

Your 2-week PDSA cycle might be:
PLAN: Define 48-hour review protocol, train 2 clinical pharmacists, prepare 
talking points for resistant prescribers

DO: Implement for one week, collect daily data on:
- Number of reviews completed
- Time per review (burden estimate)
- Number of de-escalations (safety outcome)
- Prescriber feedback

STUDY: Analyze data. What worked? What was burdensome? 
Interview one resistant prescriber.

ACT: Refine protocol based on learning. Plan next cycle.

[STEP 3: ANTICIPATED BARRIERS]
"Your skeptical finance director will ask: 'What's the ROI?'
Your answer: 'Week 1, we de-escalated 6 patients from vancomycin to 
cephalosporins. That's $18/day × 30 = $540/month in just this unit. 
Plus, we have one fewer C. difficile case (value: ~$50,000).'
This is the data to build institutional support."

[STEP 4: SCALE-UP]
Once the medical ICU cycle is successful, you'll have:
- Real data to convince skeptics
- Protocol refined through iteration
- One unit of champions to influence peers
- Evidence that it's doable

Then scale to next unit, etc.

What unit would you actually start with in YOUR hospital? 
And what would "success" look like in week 1?
```

#### **Level 3: Advanced - Systems Thinking & Unintended Consequences**

**Scenario**:
```
You're now the ASP director at a 500-bed health system with 4 hospitals 
(pediatric, adult acute, women's/maternal, specialty psychiatric).

New mandate: Reduce system-wide CDI rates from 2.0 to 0.8 per 10,000 
patient-days within 18 months.

Complexity factors:
- Different IT systems across hospitals (not fully integrated)
- Separate labs for pediatrics vs. adult medicine
- Different pharmacy leadership at each site
- Psychiatric hospital has unique prescribing patterns (antibiotics 
  for residents with chronic infections)
- Board is expecting significant cost savings AND quality improvement

Challenge:
Design a system-wide improvement strategy that:
1. Aligns incentives across independent hospital units
2. Addresses inequitable impacts (psychiatric hospital already under-resourced)
3. Manages competing priorities (cost vs. quality)
4. Plans for failure modes and contingencies
5. Communicates progress to diverse stakeholders

This is NOT just about executing a protocol. This is about navigating 
organizational politics, resource constraints, and unintended consequences.
```

**AI Coaching Response**:
```
This is where stewardship leadership gets really sophisticated. You're not 
just managing a clinical intervention—you're orchestrating organizational change 
across a complex system with competing incentives.

Let me frame this using implementation science:

[PROBLEM ANALYSIS - CFIR Framework]
Your context includes:
- OUTER SETTING: Board mandate (external pressure), cost constraints (resource limitation), existing competition between hospitals
- INNER SETTING: Different IT/labs (compatibility issue), different leadership (fidelity risk)
- INTERVENTION: CDI reduction (relatively straightforward technically)
- INDIVIDUALS: Varies by site; some champions, some skeptics
- IMPLEMENTATION PROCESS: You need to coordinate across silos

[STRATEGY - Your Differentiated Approach]
Instead of "one size fits all," I'd recommend:

1. **Pediatric hospital**: Lead with data/quality (CDI in kids is particularly 
   devastating; parents very concerned). Emphasize patient safety.

2. **Adult acute**: Lead with economics. CDI = long stays = costs. 
   Calculate: "For every 1% reduction in CDI, we save $X and improve HCAHPS scores."

3. **Women's/maternal**: Lead with safety (maternal-fetal transmission concerns 
   are real). Connect to patient satisfaction.

4. **Psychiatric**: This is where you need to be MOST thoughtful.
   - Already under-resourced ✓
   - Patients may have chronic infections that could be over-treated ✓
   - Staff may feel blamed (incorrectly) for higher rates ✓
   
   Your approach: Extra support, not extra scrutiny. Provide clinical pharmacist 
   hours for complex cases. Show investment in THEIR success, not judgment.

[RISK MITIGATION]
Unintended consequences to anticipate:

a) **Undermining other antibiotic initiatives**
   If you over-focus on CDI risk, you might inadvertently increase other 
   resistant organisms. Solution: Monitor for increasing ESBL rates, etc. 
   Include balancing metrics.

b) **Widening inequities**
   If psychiatric hospital can't meet targets due to resource constraints, 
   they'll feel blamed and disengage. Solution: Adjust targets by baseline 
   complexity. Provide more support to struggling sites.

c) **Suppressing reporting**
   If sites are judged harshly on CDI rates, they might not report cases. 
   Solution: Separate "improvement incentives" from "accountability measures."

d) **Workflow disruption**
   New protocols might slow urgent prescribing. Solution: Build in exceptions 
   and escalation paths for ICU/sepsis cases.

[COORDINATION STRUCTURE]
I'd establish:
- Steering committee (CMOs from each site, your director, CNO, CFO)
  - Meets monthly
  - Makes system-wide resource decisions
  - Resolves competing priorities
  
- Implementation leads at each hospital (usually pharmacy)
  - Customize approach to local context
  - Report monthly to steering committee
  - Support each other (learning collaborative model)
  
- Data team (shared, system-wide)
  - Standardize CDI definitions and reporting
  - Provide monthly dashboards to each site
  - Identify emerging problems early

[COMMUNICATION STRATEGY]
Month 1-2: Transparency and engagement
- Share CDI benchmarking data (how you compare nationally)
- Acknowledge that psychiatric hospital will need EXTRA support (not judgment)
- Present improvement model: "We're ALL learning together"

Month 3-6: Quick wins
- Publicize early successes (even partial)
- Celebrate one unit's improvement (but frame as "learning, not shaming")
- Share specific tactics that worked: "This pediatric unit did X..."

Month 6-12: Sustain and spread
- Monthly dashboards showing progress
- Peer learning sessions (units learning from each other)
- Continue celebrating incremental progress, not just endpoints

Month 12-18: Sustainability planning
- What will keep improvement going after project ends?
- How do we embed this in normal workflows?
- What's the new "normal" staffing/infrastructure needed?

[HONEST CONVERSATION]
"This 18-month timeline is ambitious, especially across 4 hospitals. 
Be prepared for:
- Month 3-4: Initial enthusiasm, some quick wins, emerging barriers
- Month 6: Plateau and frustration ("Why aren't we seeing bigger gains?")
- Month 9: Decision point (Do we double down? Adjust strategy?)
- Month 12-18: Slow incremental progress

Your job is not to guarantee success, but to:
1. Make it POSSIBLE
2. Learn quickly when things aren't working
3. Adjust based on data
4. Celebrate progress, not perfection
5. Sustain commitment despite setbacks

What's your biggest concern about this system-wide approach?
And what's ONE thing you'd do differently from what I've outlined?"
```

### 1.3 Assessment Rubric: Leadership & Program Management

```
DIMENSION 1: UNDERSTANDING OF CHANGE MANAGEMENT (25% weight)

Novice (0-0.3):
□ Shows little understanding of organizational dynamics
□ Treats change as simple (if we just tell people the protocol, they'll follow)
□ Ignores stakeholder concerns or views them as obstacles

Developing (0.3-0.6):
□ Identifies some key stakeholders
□ Recognizes that change is hard but offers only surface solutions
□ May oversimplify barriers or miss systemic issues
Example: "We'll just show them the data"

Proficient (0.6-0.85):
□ Identifies diverse stakeholders and their different incentives
□ Designs specific engagement strategies tailored to different groups
□ Anticipates 2-3 major barriers and plans responses
□ References change management literature (Kotter, Rogers, etc.)
Example: "For surgeons, I'll lead with outcomes data. For finance, 
I'll emphasize ROI. For nursing, I'll address workflow burden."

Advanced (0.85+):
□ Demonstrates sophisticated understanding of organizational complexity
□ Addresses equity considerations (How does this affect under-resourced units?)
□ Plans for unintended consequences and system interactions
□ Tailors approach based on organizational context, not one-size-fits-all
□ Includes contingency planning for resistance or failure

---

DIMENSION 2: BUSINESS CASE DEVELOPMENT (25% weight)

Novice (0-0.3):
□ ROI calculation missing or severely incomplete
□ Only considers direct drug costs (incomplete financial picture)
□ Goals vague and not time-bound

Developing (0.3-0.6):
□ ROI calculation attempted but may have errors
□ Includes direct costs and one secondary benefit (e.g., C. difficile)
□ Goals SMART-ish but execution plan vague

Proficient (0.6-0.85):
□ Accurate ROI calculation including:
  - Direct antibiotic cost savings
  - Indirect savings (reduced CDI, reduced length of stay)
  - Implementation costs (training, pharmacist time)
□ ROI clearly stated: "For every $1 invested, we return $3-5"
□ SMART goals with clear timeline and responsible parties
□ Addresses multiple audiences (Finance, Medicine, Quality)

Advanced (0.85+):
□ Comprehensive financial analysis including:
  - Sensitivity analysis (What if adoption is only 50%?)
  - Break-even analysis (When do we see positive ROI?)
  - Comparison to alternative investments
□ Connects to institutional strategic priorities
□ Addresses equity (How does ROI differ by patient population?)
□ Plans for sustainability ("How do we fund this long-term?")

---

DIMENSION 3: DATA-DRIVEN STRATEGY (25% weight)

Novice (0-0.3):
□ Lacks specific metrics or measurement plan
□ No reference to institutional baseline data
□ Doesn't distinguish between process and outcome metrics

Developing (0.3-0.6):
□ Identifies some relevant metrics
□ May confuse process and outcome metrics
□ Doesn't specify data collection/analysis methods
Example: "We'll measure antibiotic use reduction"

Proficient (0.6-0.85):
□ Clear process metrics (e.g., % of broad-spectrum prescriptions reviewed)
□ Clear outcome metrics (e.g., DOT reduction, CDI rates)
□ Balancing metrics to avoid unintended harms
□ Specific data source and collection methods identified
□ Benchmarking plan (comparing to national standards)

Advanced (0.85+):
□ Sophisticated analytics plan:
  - Statistical methods described (time-series analysis, risk adjustment)
  - Power/sample size considered
  - Stratified analysis by unit/department (heterogeneity)
□ Plan for data visualization for different audiences
□ Integration with institutional data infrastructure
□ Plans for continuous monitoring and rapid feedback loops

---

DIMENSION 4: IMPLEMENTATION FEASIBILITY (25% weight)

Novice (0-0.3):
□ Implementation plan vague or missing
□ Doesn't address resource constraints
□ No timeline or milestones

Developing (0.3-0.6):
□ Basic implementation steps outlined
□ Some awareness of resource needs but not specific
□ Timeline present but may be unrealistic

Proficient (0.6-0.85):
□ Realistic implementation timeline with milestones
□ Resources specified (FTE, equipment, budget)
□ Workflow integration planned
□ Contingency for likely barriers
□ Clear accountability (who does what?)

Advanced (0.85+):
□ Phased approach with decision points
□ Pilot design with specific success criteria
□ Scale-up strategy if pilot successful
□ Plans for sustaining change (hardest part!)
□ Engagement strategy for champions and skeptics
□ Risk mitigation for equity/access concerns

---

OVERALL MASTERY SCORE CALCULATION:
(Avg of 4 dimensions)
0-0.3 = Needs significant improvement (offer one-on-one coaching)
0.3-0.6 = Developing competency (second attempt recommended)
0.6-0.85 = Proficient (can apply in real work settings)
0.85-1.0 = Advanced (ready for complex system-wide initiatives)
```

### 1.4 Citation Integration Example

```python
# Module 1 Citation Integration

LEADERSHIP_CITATIONS = {
    "change_management_theory": [
        {
            "pmid": 27899754,
            "title": "Implementing Antimicrobial Stewardship Programs in Healthcare Systems",
            "authors": "Davey et al.",
            "year": 2017,
            "evidence_level": "systematic_review",
            "relevance": 0.95,
            "key_finding": "Successful ASP implementation requires clear governance, 
            adequate resources, and engagement of prescribing leaders"
        },
        {
            "pmid": 20838122,
            "title": "Using the Consolidated Framework for Implementation Research 
            to advance implementation of antimicrobial stewardship programs",
            "authors": "Damschroder et al.",
            "year": 2010,
            "evidence_level": "conceptual_framework",
            "relevance": 0.90,
            "key_finding": "Addresses organizational context, implementation process, 
            and individual factors that influence success"
        }
    ],
    "roi_and_economics": [
        {
            "pmid": 29546174,
            "title": "The business case for antimicrobial stewardship programs",
            "authors": "IDSA/SHEA",
            "year": 2018,
            "evidence_level": "expert_consensus",
            "relevance": 0.95,
            "key_finding": "ASP ROI typically 2-5x; includes both direct savings and 
            prevented complications"
        }
    ],
    "stakeholder_engagement": [
        {
            "pmid": 27899754,
            "title": "Barriers and facilitators to stewardship engagement",
            "authors": "Davey et al.",
            "year": 2017,
            "evidence_level": "systematic_review",
            "relevance": 0.88,
            "key_finding": "Physician engagement is critical; must address specialty-specific 
            concerns (surgeons want outcome data, intensivists want flexibility)"
        }
    ]
}

def add_citations_to_business_case_feedback(submission: str, 
                                           feedback: str) -> str:
    """Enhance feedback with specific citations"""
    
    # Get relevant citations
    relevant = LEADERSHIP_CITATIONS["roi_and_economics"]
    
    enhanced_feedback = f"""
    {feedback}
    
    ---
    SUPPORTING EVIDENCE:
    
    Your approach to ROI calculation is grounded in the IDSA/SHEA framework 
    (Ref: IDSA Antimicrobial Stewardship Economics Task Force, 2018; PMID: 29546174).
    
    Key insight from this framework: Most institutions see 2-5x ROI when calculating:
    - Direct drug cost savings
    - Prevented adverse events (C. difficile, nephrotoxicity)
    - Reduced length of stay
    
    You mentioned $180,000 in direct savings. This is reasonable. But if you 
    factor in prevented C. difficile costs (~$40,000-50,000 per case), the 
    total ROI approaches $500,000+.
    
    RECOMMENDATION: Strengthen your business case by citing this framework 
    and showing the full economic impact, not just drug costs.
    """
    
    return enhanced_feedback
```

---

## MODULE 2: DATA ANALYTICS & INTERPRETATION

### 2.1 System Prompt

```
You are Dr. Sarah Chen, a biostatistician and ASP leader who specializes 
in translating complex antimicrobial use data into actionable intelligence.

Your teaching philosophy:
- Data is power, but only if correctly interpreted and communicated
- The same metric can tell different stories to different audiences
- Most healthcare providers are NOT trained in data analysis; 
  your job is to make data accessible without oversimplifying
- Dashboards and visualizations matter more than statistical sophistication

For this session, you are teaching fellows to:

1. **Calculate fundamental metrics correctly**:
   - Days of Therapy (DOT) and how it differs from DDDs
   - DOT per 1000 patient-days (why this is better than absolute counts)
   - How to handle patients on multiple antibiotics simultaneously
   - Appropriate denominators (admission-level vs. patient-day-level vs. 
     facility-level)

2. **Interpret trends without over-interpreting**:
   - Statistical significance vs. clinical significance
   - Seasonal variations and confounding factors
   - Lag time between intervention and measurement

3. **Benchmark appropriately**:
   - How to find comparison data (SHARPS, PHIS, your literature)
   - Percentile interpretation (you're at 50th, 75th, 25th—what does this mean?)
   - When benchmarking is helpful vs. potentially harmful (gaming metrics)

4. **Visualize for audiences**:
   - What would make sense to frontline clinicians?
   - What would convince the CFO?
   - What would communicate to quality/safety committee?

5. **Close the loop**:
   - From data → insight → intervention → measurement → communication → action
   - Where do stewardship efforts typically fail in this loop?

Teaching progression:
- **Novice**: Focus on calculation accuracy. Use simple datasets. 
  Emphasize conceptual understanding (Why DOT, not raw counts?).
  
- **Intermediate**: Multi-variable datasets. Trend interpretation. 
  Introduce real-world confounders.
  
- **Advanced**: System-level analytics. Benchmarking strategy. 
  Sophisticated communication for diverse audiences.
```

### 2.2 Data Analysis Scenarios with Progressive Complexity

#### **Scenario 1: Basic DOT Calculation (Novice)**

```
Your pediatric ward had 150 admissions last month.
Calculate DOT for the following patients:

Patient A: 6-year-old with UTI
- Cephalexin 25 mg/kg/dose, QID
- Weight: 20 kg
- Days of therapy: 7 days
- DOT = ?

Patient B: 10-year-old with pneumonia
- Azithromycin 10 mg/kg on day 1, then 5 mg/kg daily
- Weight: 30 kg
- Days: 5 (given as Z-pack variant)
- DOT = ?

Patient C: 14-year-old with serious infection
- Meropenem 20 mg/kg/dose, TID AND
- Vancomycin 15 mg/kg/dose, TID
- Weight: 50 kg
- Days: 10
- DOT = ? (answer: one DOT per drug, not combined)

BONUS: If your ward had 1,500 patient-days total, what is your 
vancomycin DOT per 1000 patient-days for these three cases alone?
```

**AI Coaching Response**:

```
Good! Let's work through these carefully. The key concept is:
DOT = 1 day of therapy per antibiotic, regardless of dose or frequency

Patient A:
Cephalexin for 7 days = 7 DOT
(The dose/frequency doesn't matter for DOT calculation—just the drug 
and duration)

Patient B:
Azithromycin for 5 days = 5 DOT
(Even though it's a Z-pack with a 5-day course)

Patient C:
Meropenem for 10 days = 10 DOT
Vancomycin for 10 days = 10 DOT
TOTAL = 20 DOT (NOT 10—these are separate drugs)

Why is this different from DDD (Defined Daily Dose)?
DDD is a WHO standard dose for an adult. It's different than how we 
actually dose pediatric patients. DOT is more useful for stewardship 
because it reflects actual prescribing, not standardized doses.

Your ward calculation:
- Total antibiotics this month from these 3 patients: 20 DOT
- Total patient-days: 1,500
- These 3 patients' vancomycin DOT: 10
- Vancomycin DOT per 1000 patient-days = (10/1,500) × 1,000 = 6.7

IMPORTANT: This is just for 3 patients. To get your actual vancomycin 
DOT per 1000 patient-days for the whole ward, you'd sum ALL vancomycin 
DOTs that month.

Does this make sense? Ready to try the next level (interpreting trends)?
```

---

#### **Scenario 2: Trend Interpretation & Seasonality (Intermediate)**

```
Your pediatric ward has been tracking total antibiotic DOT per 1000 
patient-days for the past 12 months:

Month    DOT/1000pd    Admissions    Events That Month
Jan      38            145           
Feb      40            148           
Mar      42            150           
Apr      45            142           Cold/flu season
May      43            145           Implemented new culture protocol
Jun      42            140           Implemented antibiotic timeout
Jul      40            138           
Aug      39            135           Summer (fewer admissions)
Sep      42            140           RSV/pneumonia season starts
Oct      44            150           
Nov      45            155           Full RSV/pneumonia season
Dec      43            148           Holiday staffing changes

Your ASP started its intervention in June (antibiotic timeout).

QUESTIONS:
1. What's the trend pre-intervention (Jan-May)?
2. Did the intervention work? How would you know?
3. What confounding factors might be at play?
4. How would you communicate this to the hospital board?
```

**AI Coaching Response**:

```
Excellent question—this is where many stewardship folks mess up the 
interpretation. Let me walk through it:

1. PRE-INTERVENTION TREND (Jan-May):
   Gradual increase from 38 → 45
   BUT: Admissions stayed ~145 (fairly stable)
   Interpretation: Increasing antibiotic intensity, not just higher census
   Likely reason: Cold/flu season (April peak)
   
   Question for you: Would you expect seasonal variation in DOT? 
   (Yes! More infections in winter → more antibiotics)

2. DID THE INTERVENTION WORK?
   This is tricky. Let's look:
   
   June: 42 (down from 45 in May)
   July: 40 (down further)
   August: 39 (continues down)
   
   BUT ALSO: Admissions down (142 → 135 → 138)
   
   Your instinct: "Yes! The timeout worked!"
   Reality: Admissions decreased, which might explain some DOT reduction
   
   Better approach:
   - Calculate DOT PER ADMISSION (not just per 1000 patient-days)
   
   May: 45 DOT per 1000 PD ÷ (145/1000) = ~6.5 DOT per admission
   June: 42 ÷ (140/1000) = 6.0 DOT per admission
   July: 40 ÷ (138/1000) = 5.8 DOT per admission
   
   This metric (DOT per admission) controls for census changes.
   Now the trend is clearer: ~5% reduction month 1, ~7% total through July
   
3. CONFOUNDING FACTORS:
   - Seasonality: Sept-Nov are high RSV months; DOT goes back UP
   - June data: You coincidentally had lower admissions
   - June-Aug: Summer = fewer admissions anyway
   - December: Holiday staffing might affect data quality
   
   You cannot claim "intervention saved 6 DOT" without controlling for 
   these factors.

4. HOW TO COMMUNICATE TO BOARD:
   
   NOT THIS: "Our intervention reduced antibiotic use by 6 points!"
   (Misleading—seasonality is a factor)
   
   THIS: "After implementing antibiotic timeout in June, we've sustained 
   lower DOT despite seasonal increases. Pre-June, we would have expected 
   September DOT of 48-50 (based on 3-year historical pattern). Instead, 
   we saw 42. This suggests our intervention prevented an additional 
   6-8 DOT increase, worth approximately $60,000 in prevented costs 
   and complications."
   
   Better: "We implemented a new antibiotic review process and will track 
   outcomes for 6 months (through spring) to properly evaluate effectiveness 
   accounting for seasonal variations."

KEY LESSON: Be honest about confounding. If you oversell the data, 
clinicians will lose trust. If you show thoughtful analysis, they'll 
believe you for future initiatives.

Does this help clarify the difference between "Did we see a change?" 
and "Did our intervention cause the change?"
```

---

#### **Scenario 3: System-Level Analytics & Benchmarking (Advanced)**

```
You're the new ASP director at a 400-bed health system with:
- Pediatric hospital (150 beds): DOT 42 per 1000 patient-days
- Adult acute hospital (180 beds): DOT 68 per 1000 patient-days
- Women's/maternal (70 beds): DOT 35 per 1000 patient-days

National benchmarks (from SHARPS collaborative):
- Pediatric (75th percentile): 45, (median): 38, (25th percentile): 32
- Adult (75th percentile): 72, (median): 58, (25th percentile): 48
- OB/GYN (75th percentile): 40, (median): 28, (25th percentile): 22

ANALYSIS QUESTIONS:

1. Interpret the system-wide performance:
   - Where are you strongest? Weakest?
   - Where should strategic focus be?
   - What does benchmarking tell you about improvement opportunity?

2. Drill down on pharmacy:
   - Top 5 antibiotics by DOT at each facility
   - Drug-class specific analysis (is this driven by vancomycin? Floroquinolones?)
   - How do you identify the "right" target?

3. Equity considerations:
   - Your pediatric hospital serves low-income, uninsured population
   - Adult hospital: insured, private practice-affiliated
   - Does this affect appropriateness of benchmarking?

4. Intervention design:
   - Based on this data alone, what would you recommend?
   - Where do you have greatest improvement potential?
   - How do you communicate different strategies for different units?

5. ROI argument to CFO:
   - If you reduced system DOT by 15%, what's the financial impact?
   - Should the "savings" be returned to departments or reinvested in ASP?
```

**AI Coaching Response**:

```
This is excellent strategic thinking. You're moving from "How do we 
reduce DOT?" to "Where is the highest-value opportunity in our system, 
and how do we address equity concerns?"

Let me structure my response:

[1. SYSTEM PERFORMANCE ANALYSIS]

Pediatric hospital:
- Your DOT (42) is ABOVE the median (38)
- You're between 50th-75th percentile (not in bottom quartile, not best)
- Improvement potential: Get from 42 → 38 (to meet median)

Adult hospital:
- Your DOT (68) is BELOW the median (58)
- You're doing worse than 75% of benchmarks
- Improvement potential: Get from 68 → 58 (significant gap)
- This is your biggest opportunity

OB/GYN:
- Your DOT (35) is just above the 25th percentile (22)
- You're well below median (28)
- Most room for improvement numerically
- BUT: Is this appropriate? Need to drill down.

STRATEGIC FOCUS: Adult hospital (biggest gap from best practice) 
+ OB/GYN (surprisingly high for this patient population)

[2. DRUG-CLASS DRILLING]

You need to ask:
- Is adult hospital's high DOT driven by appropriate ICU empiric therapy?
  OR by unnecessary broad-spectrum use in general medicine?
  
- For OB: Is this prophylaxis (shouldn't be high) or treatment 
  of actual infections?
  
This requires getting individual hospital data (which your EHR should have).

EXAMPLE ANALYSIS:
"Adult hospital's high DOT is 60% vancomycin (32/1000 PD) and 30% 
fluoroquinolones (20/1000 PD). Vancomycin is appropriate for ICU empiric 
therapy, but we have 400 vancomycin DOTs in non-ICU areas. That's our 
target."

[3. EQUITY CONSIDERATIONS]

You're right to think about this. Your pediatric hospital:
- Serves low-income, uninsured kids
- May have higher infection rates (social determinants)
- May have different organism distribution
- Comparing directly to SHARPS (which may include more affluent centers) 
  might not be fair

What you should do:
- Get SHARPS data stratified by patient acuity (PICU vs. general)
- Look at similar hospitals (safety-net pediatric centers)
- If your pediatric hospital has higher acuity, a DOT of 42 might be 
  appropriate
- Compare adult and OB to appropriate cohorts (teaching vs. community hospitals?)

This prevents you from imposing inappropriate targets based on misleading benchmarks.

[4. INTERVENTION DESIGN]

Given this analysis:

Priority 1 (Highest Impact): Adult Hospital
- Target: Get 400 excess vancomycin DOT under control
- Approach: Audit-feedback for non-ICU vancomycin prescribing
- Expected gain: 10-15 DOT reduction → Save $100-150K

Priority 2 (Surprising High): OB/GYN
- Question first: Is this actually inappropriate? (Get data)
- If so: Review prophylaxis protocols
- Expected gain: 5-8 DOT reduction

Priority 3 (Lower ROI but achievable): Pediatric
- Target: Fluoroquinolone use in older kids (not indicated for many conditions)
- Approach: Education + default order changes
- Expected gain: 3-5 DOT reduction

Different communication for each:
- Adult hospital: "We're above benchmarks. Let's get competitive."
- OB/GYN: "This seems high for prophylaxis-dominant use. Let's investigate."
- Pediatric: "You're near best practice. Let's sustain and target specific drugs."

[5. FINANCIAL ARGUMENT TO CFO]

System-wide opportunity:
- Current total system DOT: ~55 per 1000 PD (weighted across beds)
- Benchmark for this system mix: ~48 per 1000 PD
- Gap: 7 DOT per 1000 PD

Financial impact:
- Average antibiotic cost: ~$50/day (varies by drug)
- System patient-days/year: ~146,000 (rough estimate)
- Current system DOT per year: 8,030 DOTs
- Target: 7,008 DOTs
- Difference: 1,022 DOTs not given
- Direct drug cost savings: $51,100/year
- Prevented complications (C. difficile, resistance): ~$200-300K
- TOTAL first-year ROI: ~$250-350K on investment of ~$150K (ASP staffing)

Your pitch: "If we reduce system DOT from 55 to 48 within 18 months, 
we save $250K while improving patient safety. This ROI pays for an 
FTE ASP director and all associated costs."

Does this analysis feel complete?
```

### 2.3 Data Analytics Assessment Rubric

```
DIMENSION 1: CALCULATION ACCURACY (20% weight)

Novice (0-0.3):
□ Calculation errors (wrong formula, math mistakes)
□ Confusion between DOT and DDD
□ Doesn't account for multi-drug combinations
□ Denominator errors (patient-days vs. admissions vs. facilities)

Developing (0.3-0.6):
□ Mostly correct calculations with minor errors
□ Understands DOT vs. DDD but may not explain well
□ Handles single-drug cases well, struggles with multi-drug
□ Correct denominator choice but may not justify it

Proficient (0.6-0.85):
□ Accurate calculations across simple and complex scenarios
□ Clear explanation of why DOT is preferred for stewardship
□ Correctly handles multi-drug patients
□ Appropriate denominator with clear rationale

Advanced (0.85+):
□ Flawless calculations including edge cases
□ Discusses limitations of different metrics and when each is appropriate
□ Adapts metric to specific question (e.g., DOT per admission vs. per 1000 PD)
□ Considers data quality issues (missing data, coding errors)

---

DIMENSION 2: TREND INTERPRETATION (25% weight)

Novice (0-0.3):
□ Mistakes correlation for causation
□ Ignores confounding variables
□ No discussion of statistical vs. clinical significance
□ Misses seasonal patterns

Developing (0.3-0.6):
□ Recognizes some confounding (admits it exists)
□ Acknowledges seasonality but doesn't account for it
□ May over-interpret small changes

Proficient (0.6-0.85):
□ Identifies major confounders (census, seasonality, interventions timing)
□ Distinguishes between "change observed" and "intervention caused change"
□ Uses appropriate control (DOT per admission, historical comparison)
□ Acknowledges limitations of analysis

Advanced (0.85+):
□ Sophisticated trend analysis:
  - Time-series methods (controlling for seasonal patterns)
  - Risk adjustment for patient complexity
  - Sensitivity analyses (What if this confounder is stronger?)
□ Appropriate statistical testing (if warranted)
□ Honest about what data can and cannot claim

---

DIMENSION 3: BENCHMARKING STRATEGY (25% weight)

Novice (0-0.3):
□ No reference to benchmarks
□ If benchmarks used, no understanding of percentile or context
□ Inappropriate comparisons (comparing pediatric to adult, etc.)

Developing (0.3-0.6):
□ Aware of benchmark sources (SHARPS, PHIS)
□ Attempts comparison but may be inappropriate
□ Doesn't account for institutional differences

Proficient (0.6-0.85):
□ Uses appropriate benchmark cohorts
□ Understands percentile interpretation
□ Accounts for institutional differences (teaching vs. community, 
   patient acuity, etc.)
□ Identifies specific improvement targets based on benchmarking

Advanced (0.85+):
□ Critical evaluation of benchmarks:
  - Are these the right comparisons for YOUR hospital?
  - What are the limitations of benchmark data?
□ Uses benchmarks to identify specific opportunities, not just "reduce DOT"
□ Considers unintended consequences of chasing metrics
□ Incorporates equity considerations (Should low-income patients be 
   held to same benchmarks?)

---

DIMENSION 4: COMMUNICATION & VISUALIZATION (25% weight)

Novice (0-0.3):
□ Data presented without clear message
□ No consideration of audience
□ Visualizations unclear or misleading

Developing (0.3-0.6):
□ Clearer message but may use inappropriate visualizations
□ Some audience consideration but not tailored
□ Visualizations present but could be improved

Proficient (0.6-0.85):
□ Clear, specific message appropriate to data
□ Different visualization choices for different audiences:
  - Frontline clinicians: Simple bar charts, drug-specific trends
  - Leadership: ROI, benchmarking vs. competitors
  - Quality committee: Balancing metrics, adverse outcomes
□ Correct interpretation provided, not raw numbers
□ Acknowledges limitations in communication

Advanced (0.85+):
□ Sophisticated communication strategy:
  - Visual hierarchy guides viewer to key insights
  - Honest about uncertainty (confidence intervals, data quality issues)
  - Avoids misleading choices (axis manipulation, cherry-picked timeframes)
  - Anticipates questions and addresses them preemptively
□ Different narratives for different audiences:
  - CFO: "Here's the ROI"
  - Medical staff: "Here's what this means for your patients"
  - Board: "Here's our competitive position"

---

OVERALL SCORE = Average of 4 dimensions
```

---

## MODULE 3: BEHAVIORAL SCIENCE & COMMUNICATION

### 3.1 System Prompt

```
You are Dr. Marcus Johnson, a behavioral economist and ASP leader with 
10 years of experience changing prescriber behavior.

Teaching philosophy:
- Prescriber behavior is not irrational; it's rational given their constraints
- Most interventions fail because they don't understand the incentives
- Behavior change is harder than knowledge change
- The best interventions work WITH psychology, not against it

Your role:
1. Help fellows understand the COGNITIVE BIASES at play:
   - Commission bias: "It's better to treat than not treat"
   - Omission bias: "If I don't give an antibiotic and patient gets worse, 
     it's my fault; if I give an antibiotic and patient gets worse anyway, 
     it's the disease"
   - Availability heuristic: "I remember the bad outcome from de-escalation; 
     I don't remember the 100 successes"
   - Status quo bias: "I've always done it this way and it works"
   - Anchoring: First antibiotic prescribed sticks (hard to de-escalate later)

2. Teach BEHAVIOR CHANGE FRAMEWORKS:
   - Fogg Behavior Model: B = M (motivation) × A (ability) × P (prompt)
   - Social Cognitive Theory: Self-efficacy, outcome expectations, environmental factors
   - Transtheoretical Model: Stages of change (precontemplation → contemplation → 
     preparation → action → maintenance)
   - Diffusion of Innovations: How do new practices spread?

3. Coach EVIDENCE-BASED COMMUNICATION:
   - Motivational Interviewing: Explore ambivalence, not lecture
   - Academic Detailing: One-on-one peer education
   - Social norms: "Your peers are doing X"
   - Loss framing: "If you don't change, you'll miss these patients"
   - Gain framing: "If you change, you'll improve these outcomes"

4. Help them DESIGN INTERVENTIONS that work:
   - For every prescriber personality type
   - In real-world constraints
   - With sustainable change

Teaching progression:
- **Novice**: Learn the common biases. Practice identifying them in cases.
  Start with one communication technique.
  
- **Intermediate**: Combine biases with communication strategies. 
  Design interventions for specific prescriber archetypes.
  
- **Advanced**: Multi-layer interventions addressing systemic factors. 
  Anticipate how interventions might fail. Plan for equity.
```

### 3.2 Prescriber Psychology Scenarios

#### **Scenario 1: The Tradition-Bound Surgeon (Novice)**

```
Dr. Richard Collins, 25-year veteran orthopedic surgeon, has been doing 
the same antibiotic protocol for 20 years:
- IV vancomycin + gentamicin preoperatively
- Continued for 3 days postoperatively
- Excellent outcomes (low infection rate, no mortality)
- Rarely reads literature
- Dismissive of "cookbook medicine"

Your challenge: You want to implement guidelines supporting 24-hour 
prophylaxis (1 day, not 3 days). Research shows this is equally effective, 
costs less, and reduces resistance.

Dr. Collins tells you: "I'm not interested in experimenting on my patients. 
My outcomes are excellent. Why change?"

QUESTIONS:
1. What cognitive biases are at play in Dr. Collins' thinking?
2. How would you respond to this comment?
3. What communication technique would be most effective?
4. What barrier (obstacle) do you anticipate?
```

**AI Coaching Response**:

```
Excellent case. This is really common and quite challenging. Let me break 
it down:

[1. COGNITIVE BIASES AT PLAY]

Status quo bias: "If it's not broken, don't fix it"
- His current protocol works (low infection rate)
- Switching means risk, even if evidence supports it
- His brain says: "Changing = risk; staying = safe"

Confirmation bias: "I only seek information that confirms my approach"
- He "rarely reads literature" 
- If he does read, he probably dismisses studies that contradict him
- He probably DOES remember the rare bad outcome from early de-escalation 
  in his career (availability heuristic)

Commission bias: "Giving an antibiotic is safer than not giving it"
- His bias: 3 days is "safer" than 1 day
- Even though data says they're equivalent
- He's probably not thinking: "Evidence shows we can safely stop now"

Outcome bias: "My outcomes are good, therefore my method is optimal"
- This logic is flawed (he might have good outcomes despite the protocol, 
  not because of it)
- But it's a powerful driver of his behavior

[2. HOW TO RESPOND]

NOT THIS: "The guidelines say 1 day is sufficient. You should follow them."
(He'll dismiss guidelines as cookbook medicine)

NOT THIS: "You're prescribing too many antibiotics."
(Defensive, attacks his competence)

THIS: "Dr. Collins, your outcomes are genuinely excellent. I want to 
understand your thinking. You're using 3 days postoperatively—walk me 
through your reasoning. What would concern you about stopping at 24 hours?"

Why this works:
- Affirms his competence (genuine compliment)
- Shows curiosity, not judgment
- Uses Motivational Interviewing: open-ended question
- Gives him a chance to voice his concerns (which you need to address)

He might say: "I worry about infections. If someone gets infected and I 
only gave them one day, I'd feel responsible."

YOUR RESPONSE: "That's a legitimate concern. Let's look at the data 
specifically for orthopedic surgery. Here's a study of 5,000 orthopedic 
patients where 24-hour prophylaxis had identical infection rates to 
3-day prophylaxis. Also, look at your own data—how many surgical site 
infections have you had in the past 3 years? Let's see if we can find 
any that are attributable to prophylaxis duration."

This is academic detailing: peer-to-peer, data-driven, addressing his 
specific concern.

[3. MOST EFFECTIVE COMMUNICATION TECHNIQUE]

For Dr. Collins: ACADEMIC DETAILING + careful framing

Why:
- He responds to data (when delivered by peer, not administrator)
- He needs his expertise validated first ("Your outcomes are excellent")
- He needs reassurance of safety before willing to change
- He needs to feel he's making the decision, not being dictated to

Timeline: This might take 3-4 conversations over 2-3 months
- Month 1: Initial conversation (understand his reasoning)
- Month 2: Share data (research + his own outcomes)
- Month 3: Pilot with "willing" patients (maybe 10% of his cases)
- Month 4: Evaluate outcomes (almost certainly equivalent/better)
- Month 5-6: Gradual adoption

[4. ANTICIPATED BARRIERS]

The biggest barrier is PSYCHOLOGICAL, not logical:
- If he changes his protocol and even ONE patient gets an infection, 
  he'll blame himself ("I didn't protect them adequately")
- This is called "commission bias" (doing something feels riskier than 
  doing nothing, even when data says otherwise)
- No amount of data will fully overcome this fear

How you address it:
- Start with his willing patients (maybe one colleague who trusts you)
- Make sure outcomes are tracked carefully
- Share successes with him (neutral tone, not triumphalist)
- If there IS a complication, be honest: "Post-op day 4 infection; 
  this can happen regardless of prophylaxis duration"

Your realistic goal: 60-70% adoption in year 1. Some surgeons 
will hold out longer. That's okay—you're changing culture, not 
winning an argument.

Does this help frame how to work with a "stuck" prescriber?
```

---

#### **Scenario 2: Designing an Intervention for Multiple Prescriber Types (Intermediate)**

```
Your ED has a problem:
- Broad-spectrum antibiotics (cefepime, meropenem) used frequently for 
  presumed sepsis, but only 40% of blood cultures actually positive
- Antibiotics started empirically but NOT de-escalated when cultures 
  show sensitivities

Prescriber breakdown:
- 5 senior attendings (15+ years): Traditionalists, skeptical of ASP
- 12 junior attendings (2-5 years): More engaged, willing to learn
- 8 residents: Busy, under-supervised, use whatever is "safest"
- 3 APP (midlevel providers): High trust in ASP input

Your goal: Improve de-escalation rates from 20% to 60% within 6 months

Challenge: Design interventions that work for EACH group, not a 
one-size-fits-all approach.
```

**AI Coaching Response**:

```
This is excellent strategic thinking. Most failed ASP initiatives use 
one intervention for everyone. You're recognizing that different people 
need different approaches.

Let me use the Fogg Behavior Model: B = M (motivation) × A (ability) × P (prompt)

For behavior to change: Motivation AND Ability AND Prompt must ALL be present.

[PRESCRIBER ANALYSIS]

Senior Attendings (5 people):
- Motivation: LOW (Confident in their practice, skeptical of ASP)
- Ability: HIGH (Experience, authority to change own practice)
- Prompt: NOT ENOUGH (Email reminders go unread)

Intervention:
- Build credibility FIRST. Ask one of them to co-lead an audit.
- Give them data on their OWN practice (Feedback):
  "You're at 15% de-escalation; your peers are at 30%"
- Once they see their data, offer ONE specific recommendation per month
  (Not overwhelming; not lecturing)
- Let them make changes at their pace
- Timeframe: 3-6 months to see shift

Juniors (12 people):
- Motivation: MEDIUM (Interested in improvement; worried about guideline compliance)
- Ability: MEDIUM (Less experience than seniors; may second-guess themselves)
- Prompt: NEEDED (Reminders would help, but need supportive tone)

Intervention:
- Monthly small-group discussions (Peer learning)
- Case-based: "When should we de-escalate?" (Not lecturing; discussing)
- Empower with decision aids (E.g., flowchart: "If culture negative, 
  consider de-escalation")
- Offer 1:1 consultation: "Can I offer you another perspective on 
  this case?"

Residents (8 people):
- Motivation: LOW (Already anxious, fear bad outcomes, influenced by seniors)
- Ability: MEDIUM (Less experienced; may not know how to de-escalate safely)
- Prompt: CRITICAL (Need support to override senior's choice)

Intervention:
- Your highest-touch group
- Create a "24-hour culture default" order:
  "If culture negative after 24 hours, consider: ________"
  (Requires provider to actively choose TO CONTINUE broad-spectrum)
- This flips the default (easier cognitively to do nothing)
- Training: 30-min session on "safe de-escalation" with case examples
- Empower APPs (who already trust ASP) to prompt residents
  ("What does your culture show?")

APPs (3 people):
- Motivation: HIGH (Trust ASP, want to improve)
- Ability: HIGH (Clinical expertise; authority)
- Prompt: JUST DO IT

Intervention:
- Make APPs "Champions" or "ASP liaisons"
- Give them authority to ask about cultures at 24 hours
- Teach them the key messaging: "No growth so far... should we think 
  about narrowing?"
- This is actually EASIER than attending conversations because they're 
  already aligned

[INTEGRATED STRATEGY]

Month 1: Infrastructure setup
- ED dashboard showing prescriber de-escalation rates (anonymous, by provider type)
- Decision aid on charts/EHR prompts
- Culture default orders

Month 2: Senior attendings
- 1:1 meetings with 5 attendings (show their data, invite collaboration)
- "Help us understand why de-escalation might be challenging?"

Month 3-4: Small group learning (juniors) + APP empowerment
- Bi-weekly case-based discussions
- APPs start asking about cultures at 24 hours
- Track who's responding positively

Month 5-6: Reinforce residents + celebrate wins
- Recognition: "This week, Dr. X de-escalated 5 patients safely"
- Monthly report: System performance (showing group progress, not individual)

[COMMUNICATION STRATEGY]

Senior attendings: "We need your leadership and expertise to make this work"
Juniors: "Let's learn together; here are tools to help"
Residents: "We're here to support you; you're not alone"
APPs: "You're the frontline; help us close the loop"

[REALISTIC TIMELINE]

- Month 1-2: Little change (building foundation)
- Month 3: First signs (maybe one senior shifts; residents more receptive)
- Month 4-5: Noticeable improvement (15-20% → 35-40% de-escalation)
- Month 6: Approaching goal (40-50% de-escalation)
- Month 9-12: Sustained (55-65%)

The key is: DIFFERENT interventions for different people. 
One conversation won't work for everyone.

Which group are you most concerned about? Let's dig deeper into 
that specific strategy.
```

---

#### **Scenario 3: Complex Multi-Factor Behavior Change Intervention (Advanced)**

```
You're implementing a major stewardship intervention:
"Antibiotic Timeout with Peer Engagement and Delayed Prescribing Option"

The protocol:
- At 48 hours, all broad-spectrum antibiotics require review
- If culture negative, consider narrowing or stopping
- If culture positive, prescriber must document why they're choosing 
  ALTERNATIVE to appropriate choice

But here's the complexity:
1. Prescribers have competing incentives (safety vs. speed)
2. Residents feel supervised/judged
3. Seniors feel their autonomy is threatened
4. APPs don't know how to question attendings
5. Nurses worry about delayed changes affecting clinical care
6. Patients/families may worry about "stopping antibiotics too soon"

Challenge: Design an intervention that addresses all these competing 
forces while actually changing behavior.

ALSO: Your hospital has significant racial/ethnic inequities in antibiotic 
use. Lower-income patients get MORE broad-spectrum antibiotics. You need 
to make sure your intervention doesn't inadvertently reinforce these inequities.
```

**AI Coaching Response**:

```
This is genuinely complex. You have multiple layers of social, 
psychological, and systemic factors. Let me approach this carefully.

[STAKEHOLDER ANALYSIS - Who has power? Competing incentives?]

Prescribers (MDs/attendings):
- Concern: "Is this going to slow down my decision-making?"
- Incentive: "I want to do the right thing for patients, but I'm busy"
- Power: HIGH (They decide what to prescribe)

Residents:
- Concern: "I don't want to be second-guessed by someone watching my work"
- Incentive: "I want to learn, but I'm afraid of being wrong"
- Power: LOW (Attendings can override them anyway)

APPs:
- Concern: "I don't want to overstep my role"
- Incentive: "I want to improve patient care but not step on toes"
- Power: MEDIUM (Can initiate conversations, not override)

Nurses:
- Concern: "I need clear orders to execute; ambiguity is confusing"
- Incentive: "I want patient safety; I also want clear expectations"
- Power: MEDIUM (Can flag issues, ensure communication)

Patients/Families:
- Concern: "Stop antibiotics too soon and my child gets worse"
- Incentive: "I want my child to recover safely"
- Power: LOW (But can demand care, create complaints)

[EQUITY ANALYSIS]

Current data shows: Lower-income patients → MORE broad-spectrum antibiotics

Possible reasons:
- Differential severity (lower SES patients sicker?) → check baseline severity
- Prescriber bias ("These patients need more intensive coverage") → CRITICAL
- Differential access to rapid diagnostics (Can we get cultures faster 
  for low-income patients?) → Infrastructure issue
- Language barriers in communication → Communication issue

Your intervention MUST address this explicitly, or it may make things worse.

Scenario: Your timeout protocol is well-implemented in Pediatric ICU 
(mostly insured). But on General Pediatrics (mostly low-income), 
implementation is weak, compliance is low. Result: Inequity widens.

How to prevent this:
- Stratify outcomes by race/ethnicity and insurance from day 1
- If inequities are widening, PAUSE and investigate before continuing
- Ensure equitable access to rapid diagnostics (can't de-escalate without 
  good culture data)
- Train providers on recognizing own unconscious bias

[INTERVENTION DESIGN - Multi-layer approach]

LAYER 1: SYSTEM/INFRASTRUCTURE
- EHR prompt at 48 hours: "Culture resulted. Review antibiotic appropriateness"
- Default: If no action taken, broad-spectrum continues (status quo)
- But: Clear flag that review is due
- This puts the responsibility on prescriber without forcing immediate change

LAYER 2: PROFESSIONAL NORMS
- Data dashboard showing peer performance (by provider, by unit, anonymous)
- "Your colleagues de-escalated 35% of eligible patients; you're at 15%"
- Social proof is powerful (Especially for mid-level performers)
- Avoid public shaming; private data for individuals, aggregate for team

LAYER 3: COMMUNICATION STRATEGY
Senior attendings:
- Frame as "safety": "We want to make sure we're using targeted therapy 
  based on actual cultures, not empiric overuse"
- Not: "You're prescribing too many antibiotics"
- Invite collaboration: "Help us understand barriers to narrowing"

Residents:
- Frame as "learning support": "Here's a case study of how to safely 
  de-escalate. Let's discuss your recent cases"
- Empower with decision tools: "Here's when narrowing is safe"
- Normalize mistakes: "Even experienced clinicians sometimes miss 
  narrowing opportunities"

APPs:
- Frame as "frontline advocates": "You're in the best position to ask 
  at 24-48 hours: What does the culture show?"
- Coach them: "Here are ways to suggest narrowing without overstepping"
  ("I noticed the culture came back; what are your thoughts on narrowing?")

Nurses:
- Frame as "patient advocates": "Help us make sure we're following the 
  right antibiotic based on cultures"
- Clarify roles: "Your job is to execute orders, flag when protocols 
  aren't being followed"
- Give them language: "The protocol calls for review at 48 hours. 
  Has the team reviewed cultures?"

Patients/families:
- Proactive communication: "We culture blood/CSF to find out exactly 
  what's causing infection so we can target the right antibiotic"
- Reassurance: "Targeted antibiotics are actually more effective than 
  broad-spectrum"
- Education: "Unnecessary antibiotics can cause resistant infections 
  that are harder to treat"

LAYER 4: FEEDBACK & ACCOUNTABILITY
- Monthly individual feedback (private): "Your de-escalation rate: 18%, 
  peer average: 35%"
- Monthly team feedback: "As a unit, we successfully narrowed 31 
  patients this month"
- Celebrate wins: "This week, residents led de-escalation for 6 
  complex cases—excellent work"
- Investigate problems: If one prescriber is consistently NOT narrowing 
  despite negative cultures, have a conversation

LAYER 5: EQUITY SAFEGUARDS
- Measure de-escalation STRATIFIED by race, insurance, patient acuity
- Red flag: If low-income patients have lower de-escalation rates 
  → investigate why
- Hypothesis: Are prescriber biases at play? Are diagnostics slower 
  in lower-income units?
- Intervention: Enhanced provider training on bias + faster diagnostics 
  in lower-income units

[CHANGE MANAGEMENT TIMELINE]

Phase 1 (Month 1-2): Build infrastructure & align stakeholders
- Install EHR prompts, dashboard
- 1:1 meetings with senior attendings (explain rationale, invite partnership)
- Resident teaching: "How to safely narrow antibiotics"
- APP training: "Communication strategies"
- Patient education materials

Phase 2 (Month 3-4): Launch with high support
- Soft launch in medical ICU (most ready group)
- Daily huddles: "Who's eligible for narrowing today?"
- Real-time coaching: "Let's talk about this patient"
- Monitor for barriers (What's making this hard?)

Phase 3 (Month 5-6): Expand with learning
- Roll out to other units (using learning from ICU)
- Regular feedback sessions (monthly)
- Celebrate successes, troubleshoot barriers
- Monitor equity metrics closely

Phase 4 (Month 7-12): Sustain & spread
- Responsibility shifts from ASP to units (you're coaching, not driving)
- Annual data showing outcomes: "We prevented X broad-spectrum courses, 
  saved $Y, with no increase in complications"
- Continued monitoring of equity metrics

[REALISTIC EXPECTATIONS]

- Month 1-2: Lots of resistance. This is normal.
- Month 3-4: Early adopters succeed. Skeptics delay. Residents hesitant.
- Month 6: Maybe 25-30% de-escalation rate (50% of your goal)
- Month 12: Maybe 45-50% de-escalation rate (approaching goal)
- Year 2: 55-60% as culture shifts

Why slow? Because behavior change is HARD. You're fighting against:
- Years of ingrained habits
- Fear of patient harm
- Organizational inertia
- Individual personalities

But it's worth it. In 2 years, you'll have prevented thousands of 
unnecessary antibiotic exposures.

What's your biggest concern about this multi-layer approach?
```

### 3.3 Behavioral Science Assessment Rubric

```
DIMENSION 1: COGNITIVE BIAS RECOGNITION (20% weight)

Novice (0-0.3):
□ Cannot identify obvious cognitive biases in scenarios
□ May dismiss biases as "just bad prescribers"
□ No framework for understanding prescriber psychology

Developing (0.3-0.6):
□ Identifies 1-2 common biases per scenario
□ Can name the bias but struggles to explain mechanism
□ May recognize some social/environmental factors

Proficient (0.6-0.85):
□ Identifies 2-3 relevant biases per scenario
□ Explains mechanism clearly (e.g., "Status quo bias makes change 
   feel risky even when data supports it")
□ Connects biases to observable behavior
□ Recognizes how biases interact (e.g., confirmation bias + status quo bias 
   = very resistant prescriber)

Advanced (0.85+):
□ Sophisticated analysis of cognitive barriers:
  - Identifies biases AND systemic factors (incentive misalignment, 
    time pressure, fear)
  - Predicts how biases might manifest differently across prescriber types
  - Considers how organizational culture reinforces biases
  - Discusses individual differences (some people more susceptible 
    to certain biases)
□ References behavior change literature appropriately

---

DIMENSION 2: COMMUNICATION STRATEGY DESIGN (25% weight)

Novice (0-0.3):
□ Communication strategy is didactic/lecturing ("Tell them the data")
□ No consideration of prescriber perspective
□ Likely to alienate rather than engage

Developing (0.3-0.6):
□ Shows some insight into effective communication
□ May use one communication technique (e.g., "I'll do academic detailing")
□ Doesn't adapt approach based on prescriber type

Proficient (0.6-0.85):
□ Selects appropriate communication technique:
  - Motivational Interviewing for ambivalent prescribers
  - Academic Detailing for opinion leaders
  - Peer feedback for socially-motivated prescribers
□ Considers prescriber values and concerns
□ Plans for multiple conversations, not one-time education
□ Addresses potential defensiveness

Advanced (0.85+):
□ Multi-method communication strategy:
  - Combines techniques (MI + Academic Detailing + Social Norms + Systems design)
  - Tailors to specific prescriber archetype and their unique drivers
  - Anticipates resistance and plans responses
  - Includes framing choices (Loss-framing vs. gain-framing; when to use each)
□ Plans for timing and sequencing of conversations
□ Considers organizational factors that enable or hinder communication

---

DIMENSION 3: INTERVENTION DESIGN FOR BEHAVIOR CHANGE (25% weight)

Novice (0-0.3):
□ Proposes interventions without clear mechanism
□ "Just educate them" or "Send out a memo"
□ No consideration of incentives or barriers

Developing (0.3-0.6):
□ Identifies ONE barrier and ONE solution
□ May propose reasonable intervention but incomplete
□ Doesn't think through implementation challenges

Proficient (0.6-0.85):
□ Multi-component intervention addressing:
  - Motivation (Why should they care?)
  - Ability (Can they feasibly do this?)
  - Prompt (When/how will they remember?)
□ Uses evidence-based behavior change theory (Fogg model, SCT, etc.)
□ Considers unintended consequences
□ Plans for different prescriber types

Advanced (0.85+):
□ Sophisticated intervention design:
  - LAYER 1: System design (Default options, EHR prompts, workflow integration)
  - LAYER 2: Social factors (Peer feedback, norms, culture change)
  - LAYER 3: Individual factors (Training, coaching, psychology)
  - LAYER 4: Feedback loops (Measurement, learning, adjustment)
□ Addresses equity explicitly (Will intervention widen or narrow disparities?)
□ Plans for sustainability (How does behavior stick long-term?)
□ Realistic timeline acknowledges behavior change is slow

---

DIMENSION 4: ANTICIPATING RESISTANCE & BARRIERS (25% weight)

Novice (0-0.3):
□ Doesn't anticipate resistance
□ Assumes people will simply comply if they have information

Developing (0.3-0.6):
□ Identifies SOME barriers
□ Proposes solutions but may be surface-level
□ Misses systemic factors

Proficient (0.6-0.85):
□ Identifies major barriers:
  - Psychological (status quo bias, fear of harm)
  - Practical (time, workflow burden, lack of resources)
  - Professional (autonomy concerns, peer pressure)
  - Organizational (competing incentives, poor communication)
□ Proposes specific mitigation for each
□ Recognizes that some people won't change (and that's okay)

Advanced (0.85+):
□ Nuanced understanding of resistance:
  - Different barriers for different people (tailored analysis)
  - Recognizes when barrier is legitimate vs. when it's cognitive bias
  - Plans for staged adoption (Early adopters → majority → laggards)
  - Identifies which barriers are changeable vs. which require acceptance
  - Considers how to harness resistance as learning opportunity
□ Discusses burnout/morale implications of poorly-designed interventions
□ Plans for failure modes ("What if this doesn't work? Here's Plan B...")

---

OVERALL SCORE = Average of 4 dimensions
```

---

## FINAL IMPLEMENTATION CHECKLIST

```
□ Session Management
  □ UserSession class with database persistence
  □ Progress dashboard for each fellow
  □ /api/user/progress endpoint

□ Multi-Turn Conversations
  □ ConversationManager tracking exchanges
  □ System prompts with conversation history
  □ Context-aware feedback

□ Citation Integration
  □ PubMedBERT search integration
  □ Evidence level filtering
  □ Citation ranking by quality

□ Module 1: Leadership
  □ 3-level scenario progression
  □ Business case rubric
  □ Change management prompts

□ Module 2: Data Analytics
  □ 3-level data analysis scenarios
  □ Calculation accuracy checking
  □ Benchmarking strategy guidance
  □ Visualization coaching

□ Module 3: Behavioral Science
  □ Prescriber archetype scenarios
  □ Behavior change frameworks
  □ Communication strategy coaching
  □ Role-play infrastructure

□ Module 4: Advanced Interventions
  □ Case-based learning scenarios
  □ Design and evaluation guidance
  □ Safety considerations

□ Assessment & Feedback
  □ Rubrics for each module
  □ Formative assessment integration
  □ Mastery tracking
  □ Adaptive difficulty engine

□ Reporting & Analytics
  □ Individual progress dashboards
  □ Cohort analytics (by institution)
  □ Equity metrics tracking
  □ Impact evaluation framework
```

---

**Document prepared**: November 2025