# Blueprint for an ASP Educational Module

This document outlines a standardized structure for creating new educational modules for the AI-assisted Antimicrobial Stewardship Program (ASP) trainer. It is based on established pedagogical principles for medical education and is designed to be implemented within the existing project architecture.

## Guiding Pedagogical Principles

- **Case-Based Learning (CBL):** Anchor learning in realistic clinical scenarios to enhance engagement and knowledge application.
- **Constructive Alignment:** Ensure all learning activities (didactics, cases, assessments) are directly aligned with clear learning objectives.
- **Scaffolding:** Structure content to build from foundational knowledge to complex decision-making.
- **Active Recall & Spaced Repetition:** Integrate quizzes and follow-up activities to promote long-term retention.
- **Immediate, AI-Driven Feedback:** Provide learners with instant, evidence-based feedback on their clinical reasoning and decisions.

---

## Module Structure

Each module will be composed of the following sections, presented to the learner in sequence.

### 1. Title and Author
- **Title:** A clear, descriptive title for the module (e.g., "Management of Community-Acquired Pneumonia").
- **Author(s):** The expert(s) who designed the module content.

### 2. Target Audience & Prerequisites
- **Primary Audience:** Define the intended learners (e.g., Medical Students, PGY-2 Internal Medicine Residents, Infectious Diseases Fellows).
- **Prerequisites:** List any required prior knowledge or completed modules.

### 3. Learning Objectives
- A list of 3-5 specific, measurable, achievable, relevant, and time-bound (SMART) learning objectives.
- **Example:** "After completing this module, the learner will be able to formulate an appropriate empiric antibiotic regimen for a patient with hospital-acquired pneumonia, including justification for gram-negative coverage."

### 4. Pre-Test (Optional but Recommended)
- A short (3-5 question) multiple-choice quiz to assess baseline knowledge.
- This allows for self-assessment and primes the learner for the upcoming content.
- **Implementation:** Questions and answers can be stored in the module's Python file.

### 5. Didactic Mini-Lecture
- A concise, text-based overview of the core concepts. This should not be exhaustive but should provide the foundational knowledge needed for the case.
- **Content:**
    - Key definitions and principles.
    - "Clinical Pearls" or common pitfalls.
    - Links to 1-2 key external resources (e.g., IDSA guidelines, landmark papers).
- **Implementation:** This content will be a static text block within the module's Python file and displayed on the module's HTML page.

### 6. Interactive Case Simulation
This is the core of the module. It will present a clinical case that unfolds over several steps.

- **Step 1: Initial Patient Presentation**
    - **Content:** A rich clinical vignette including patient history, vital signs, and physical exam findings.
    - **User Task:** Ask the learner to provide an initial assessment, differential diagnosis, and plan for initial workup.
    - **AI Feedback:** The AI will evaluate the learner's response against a pre-defined rubric focusing on appropriate differential and initial orders.

- **Step 2: Data & Imaging Results**
    - **Content:** Provide the results of the initial workup (e.g., labs, chest X-ray report, gram stain).
    - **User Task:** Ask the learner to interpret the new data and propose an empiric antibiotic regimen. This is a critical decision point.
    - **AI Feedback:** The AI will use a detailed rubric and the RAG system to evaluate the chosen antibiotics, dose, route, and duration. It will provide evidence-based feedback on the appropriateness of the choice.

- **Step 3: Clinical Course & De-escalation**
    - **Content:** Describe the patient's response to therapy after 48-72 hours and provide final microbiology results (e.g., culture and sensitivity).
    - **User Task:** Ask the learner if and how they would modify the antibiotic regimen based on the new data.
    - **AI Feedback:** The AI will evaluate the learner's decision to de-escalate, broaden, or continue therapy, referencing the provided sensitivities.

### 7. Post-Case Debrief
- A summary of the case highlighting key decisions and outcomes.
- **Content:**
    - **"Expert Path":** A brief description of the ideal decision-making process for this case.
    - **Key Takeaways:** Bullet points summarizing the main teaching points from the module.
    - **Further Reading:** A curated list of references for deeper study.

### 8. Post-Test & Assessment
- A short (3-5 question) quiz that directly assesses the learning objectives.
- These questions should be application-focused, potentially using a mini-vignette.
- The learner's score can be displayed to show knowledge gain when compared to the pre-test.

---
## Implementation Guide

To create a new module based on this blueprint:

1.  **Create the Module File:** Copy `modules/cicu_prolonged_antibiotics_module.py` to a new file (e.g., `modules/new_module_name.py`).
2.  **Define Content:** Within the new file, systematically replace the CICU content with the new module's content, following the structure above (Objectives, Didactics, Case Steps, Rubrics). Each case step and its corresponding rubric will be a separate entry in the `_initialize_scenarios` and `_initialize_rubrics` methods.
3.  **Create API Endpoints:** In `unified_server.py`, add new API routes for your module by copying and renaming the existing `/api/modules/cicu/*` endpoints.
4.  **Build the Frontend:** Copy `cicu_module.html` to a new file (e.g., `new_module_name.html`) and update the JavaScript `fetch` calls to point to your new API endpoints.
5.  **Test Interactively:** Use `run_cicu_interactive.py` (adapted for your new module) to quickly test the flow and content of your case scenarios without needing the web interface.
