# Google Form for Expert Reviews - Setup Guide

This guide helps you create a Google Form to collect expert corrections of AI feedback, which can then be imported into the Expert RAG system.

## 📋 Form Structure

### Section 1: Expert Information
- **Expert Name** (Short answer, Required)
- **Email** (Email, Required)
- **Institution/Affiliation** (Short answer, Optional)

### Section 2: Scenario Context
- **Module ID** (Dropdown, Required)
  - Options:
    - cicu_prolonged_antibiotics
    - [Add other modules as you create them]

- **Scenario ID** (Dropdown, Required)
  - Options:
    - cicu_beginner_data_analysis
    - cicu_beginner_intervention
    - cicu_intermediate_implementation
    - cicu_advanced_sustainability
    - [Customize based on your scenarios]

- **Difficulty Level** (Dropdown, Required)
  - Options: beginner, intermediate, advanced, expert

- **Competency Area** (Dropdown, Required)
  - Options:
    - data_analysis
    - behavioral_intervention
    - implementation_science
    - clinical_decision_making

### Section 3: The Response and Feedback
- **Fellow's Original Response** (Paragraph, Required)
  - Description: "Copy the fellow's response that you're reviewing"

- **AI-Generated Feedback** (Paragraph, Required)
  - Description: "Copy the AI feedback that was provided to the fellow"

### Section 4: Your Expert Evaluation

- **Was the AI feedback medically accurate?** (Multiple choice, Required)
  - Options: Yes / No / Partially

- **Was the AI feedback pedagogically helpful?** (Multiple choice, Required)
  - Options: Yes / No / Partially

- **Accuracy Rating** (Linear scale, Required)
  - Scale: 1-5
  - Labels: 1 = Inaccurate/Harmful, 3 = Acceptable, 5 = Excellent

- **Helpfulness Rating** (Linear scale, Required)
  - Scale: 1-5
  - Labels: 1 = Not helpful, 3 = Somewhat helpful, 5 = Very helpful

### Section 5: Your Corrections

- **Expert Correction** (Paragraph, Required)
  - Description: "What feedback would YOU give instead? Be specific and actionable."

- **Expert Reasoning** (Paragraph, Required)
  - Description: "Why did you make these changes? What was the AI missing?"

- **What did the AI miss?** (Paragraph, Required)
  - Description: "List the key things the AI overlooked (comma-separated). For example: 'Requiring specific formula, Addressing power dynamics, Checking for safety protocols'"

- **What did the AI do well?** (Paragraph, Optional)
  - Description: "List things the AI got right (comma-separated)"

### Section 6: Additional Comments
- **Additional Comments** (Paragraph, Optional)
  - Description: "Any other observations or suggestions for improving the AI feedback?"

---

## 🔧 Step-by-Step Setup Instructions

### 1. Create the Google Form

1. Go to https://forms.google.com
2. Click **"+ Blank"** to create a new form
3. Name it: **"ASP AI Agent - Expert Feedback Review"**
4. Add this description:
   ```
   EXPERT FEEDBACK REQUEST
   ASP Fellowship AI Curriculum Development

   BACKGROUND & PURPOSE

   A recent national survey of pediatric infectious diseases fellowship directors
   (41.5% response rate) found that while 63% of programs have a formal antimicrobial
   stewardship (AS) curriculum, significant gaps exist in advanced competencies.
   Program directors expressed low satisfaction with fellows' readiness for leadership
   roles and identified key training deficits in:

   • Leadership skills
   • Data analytics
   • Understanding psychosocial factors of prescribing

   All respondents agreed on the need for a standardized curriculum. These findings
   support the development of a national, advanced pediatric AS curriculum to
   complement existing foundational training.

   WHY WE'RE DEVELOPING AN AI-POWERED CURRICULUM

   To address these identified gaps, we are developing an AI-powered adaptive learning
   platform that provides fellows with individualized feedback on complex ASP scenarios.
   The AI generates real-time feedback on fellows' responses across four key competency
   domains: data analysis, behavioral intervention, implementation science, and clinical
   decision making.

   YOUR ROLE AS AN EXPERT REVIEWER

   You have been selected for this review because of your recognized expertise in
   antimicrobial stewardship. Your input is critical to ensure the AI feedback is
   both clinically accurate and pedagogically effective.

   This form collects your expert corrections of AI-generated feedback. Your insights
   will directly improve the quality of feedback provided to fellows nationwide.

   PUBLICATION & CO-AUTHORSHIP

   We intend to publish a manuscript describing this curriculum development process
   and its validation. All experts who provide substantive input (defined as reviewing
   3 or more AI feedback samples) will be offered co-authorship on the manuscript.

   ESTIMATED TIME: 10-15 minutes per review

   Thank you for contributing your expertise to advance ASP fellowship training!
   ```

### 2. Add Questions

Copy the questions from the structure above. Here's the exact format for each:

#### Question 1: Expert Name
- Type: **Short answer**
- Make it: **Required**
- Add validation: None

#### Question 2: Email
- Type: **Short answer** (or use Email if you want validation)
- Make it: **Required**

#### Question 3: Institution/Affiliation
- Type: **Short answer**
- Make it: **Optional**

#### Question 4: Module ID
- Type: **Dropdown**
- Options:
  ```
  cicu_prolonged_antibiotics
  [Add others as needed]
  ```
- Make it: **Required**

#### Question 5: Scenario ID
- Type: **Dropdown**
- Options:
  ```
  cicu_beginner_data_analysis
  cicu_beginner_intervention
  cicu_intermediate_implementation
  cicu_advanced_sustainability
  ```
- Make it: **Required**

#### Question 6: Difficulty Level
- Type: **Dropdown**
- Options: `beginner`, `intermediate`, `advanced`, `expert`
- Make it: **Required**

#### Question 7: Competency Area
- Type: **Dropdown**
- Options:
  ```
  data_analysis
  behavioral_intervention
  implementation_science
  clinical_decision_making
  ```
- Make it: **Required**

#### Question 8: Fellow's Original Response
- Type: **Paragraph**
- Description: "Copy the fellow's response that you're reviewing"
- Make it: **Required**

#### Question 9: AI-Generated Feedback
- Type: **Paragraph**
- Description: "Copy the AI feedback that was provided to the fellow"
- Make it: **Required**

#### Question 10: Was the AI feedback medically accurate?
- Type: **Multiple choice**
- Options: `Yes`, `No`, `Partially`
- Make it: **Required**

#### Question 11: Was the AI feedback pedagogically helpful?
- Type: **Multiple choice**
- Options: `Yes`, `No`, `Partially`
- Make it: **Required**

#### Question 12: Accuracy Rating
- Type: **Linear scale**
- Scale: 1 to 5
- Label for 1: "Inaccurate/Harmful"
- Label for 5: "Excellent"
- Make it: **Required**

#### Question 13: Helpfulness Rating
- Type: **Linear scale**
- Scale: 1 to 5
- Label for 1: "Not helpful"
- Label for 5: "Very helpful"
- Make it: **Required**

#### Question 14: Expert Correction
- Type: **Paragraph**
- Description: "What feedback would YOU give instead? Be specific and actionable."
- Make it: **Required**

#### Question 15: Expert Reasoning
- Type: **Paragraph**
- Description: "Why did you make these changes? What was the AI missing?"
- Make it: **Required**

#### Question 16: What did the AI miss?
- Type: **Paragraph**
- Description: "List the key things the AI overlooked (comma-separated). Example: 'Requiring specific formula, Addressing power dynamics, Checking for safety protocols'"
- Make it: **Required**

#### Question 17: What did the AI do well?
- Type: **Paragraph**
- Description: "List things the AI got right (comma-separated)"
- Make it: **Optional**

#### Question 18: Additional Comments
- Type: **Paragraph**
- Description: "Any other observations or suggestions for improving the AI feedback?"
- Make it: **Optional**

### 3. Configure Form Settings

1. Click the **Settings** gear icon (⚙️) at the top
2. Under **General**:
   - ✅ Check "Limit to 1 response" (optional - uncheck if you want experts to submit multiple reviews)
   - ✅ Check "Collect email addresses" (to track who submitted what)
3. Under **Presentation**:
   - ✅ Check "Show progress bar"
   - Confirmation message: "Thank you for your expert review! Your feedback will help improve the ASP AI Agent."
4. Click **Save**

### 4. Customize Appearance (Optional)

1. Click the **Palette** icon at the top
2. Choose a theme color (suggest using your institution's colors)
3. Add a header image if desired

### 5. Test the Form

1. Click **Preview** (eye icon) to test
2. Fill out a sample review to ensure all questions work
3. Check that required fields are enforced

---

## 📤 Collecting Responses

### Sharing the Form

1. Click **Send** button at the top right
2. Choose sharing method:
   - **Email**: Send directly to expert reviewers
   - **Link**: Copy the link to share via other channels
   - **Embed**: Embed on a website

**Sample Email Template:**

```
Subject: Expert Review Needed - ASP AI Agent Feedback

Dear [Expert Name],

I'm developing an AI-powered teaching tool for antimicrobial stewardship fellowship training. Before we launch, I need expert validation of the AI-generated feedback to ensure it's clinically accurate and pedagogically sound.

Would you be willing to spend 10-15 minutes reviewing 1-2 AI feedback samples?

Review Form: [Insert Google Form Link]

Your expertise would really strengthen this tool, and you'll be acknowledged in all related publications.

Thank you for considering!

Best regards,
[Your Name]
```

### Tracking Responses

1. Click the **Responses** tab in your form
2. You'll see:
   - Summary view (charts and graphs)
   - Individual responses
   - Link to view in Google Sheets

---

## 📊 Exporting Data to Import into Expert RAG

### Method 1: Export to CSV (Recommended)

1. Open your Google Form
2. Click **Responses** tab
3. Click the **Google Sheets** icon (green spreadsheet) - "View responses in Sheets"
4. In the Google Sheet:
   - Click **File** → **Download** → **Comma-separated values (.csv)**
   - Save as: `expert_reviews_[DATE].csv`

### Method 2: Direct Spreadsheet Export

1. In Google Sheets (from step 3 above)
2. **Important**: The column headers need to match exactly what the import script expects

**Expected Column Headers:**

```csv
Timestamp,Expert Name,Module ID,Scenario ID,Difficulty Level,Competency Area,User Response,AI Feedback,Expert Correction,Expert Reasoning,What AI Missed,What AI Did Well
```

**If your headers don't match**, you have two options:

**Option A: Rename in Google Sheets**
1. Edit the first row to use the exact header names above
2. Then export to CSV

**Option B: Edit CSV after export**
1. Open the CSV in a text editor
2. Replace the first line with the expected headers

### Method 3: Using Apps Script (Advanced)

If you want automatic exports, you can set up a Google Apps Script trigger. See Appendix A below.

---

## 📥 Importing into Expert RAG System

Once you have your CSV file:

```bash
# Navigate to your project directory
cd /home/david/projects/asp_ai_agent

# Import the expert corrections
python add_expert_knowledge.py corrections expert_reviews_2025-01-16.csv
```

The script will:
- ✅ Validate each row
- ✅ Show progress for each imported correction
- ✅ Display summary with success/error counts
- ✅ Add corrections to both SQLite database and ChromaDB vector store

**Example Output:**

```
Importing expert corrections from: expert_reviews_2025-01-16.csv

✓ Row 2: Added correction from Dr. Sarah Martinez
✓ Row 3: Added correction from Dr. John Chen
✓ Row 4: Added correction from Dr. Emily Rodriguez
✗ Row 5: Missing required column: Expert Reasoning

============================================================
Summary:
  Successfully added: 3 corrections
  Errors: 1

Error details:
  - Row 5: Missing required column: Expert Reasoning
============================================================
```

---

## 🎯 Best Practices for Expert Reviewers

Include these tips in your invitation email or form introduction:

### For Expert Reviewers:

1. **Be Specific**: Instead of "needs improvement", write "Should specify the DOT calculation formula: DOT/1000 PD = (days/patient-days) × 1000"

2. **Focus on Gaps**: What did the AI miss that you would have emphasized?

3. **Use Examples**: When the AI is too vague, provide the concrete example you'd give

4. **Think Pedagogically**: Not just "is this right?" but "will this help the learner improve?"

5. **Comma-Separate Lists**: In "What AI Missed", use commas: "Formula missing, No benchmark specified, Too vague"

6. **Complete One Form Per Review**: Each form submission should be for ONE fellow response

---

## 📋 Sample Completed Review

Here's what a good expert review looks like:

**Fellow's Response:**
```
I would calculate DOT for the CICU and compare it to benchmarks to see if we're using too many antibiotics.
```

**AI Feedback:**
```
Good approach. Calculating DOT and comparing to benchmarks is appropriate for identifying opportunities.
```

**Expert Correction:**
```
You've identified the right approach, but let's make it concrete.

When you say "calculate DOT," show me the formula: DOT/1000 patient-days = (total antibiotic days / total patient days) × 1000.

And which benchmark would you use? NHSN? SHARPS? Each has different populations and risk adjustment. For a cardiac ICU, I'd recommend NHSN PICU data as the closest comparison.

Try recalculating with actual numbers: If you have 450 meropenem days and 1000 patient days, what's your DOT/1000 PD? How does that compare to the NHSN 50th percentile of ~380?
```

**Expert Reasoning:**
```
The AI accepted vague statements without pushing for specificity. Fellows need to demonstrate they can actually DO the calculation, not just name it. The AI also missed that benchmark selection matters—different benchmarks have different inclusion criteria and case mix.
```

**What AI Missed:**
```
Requiring specific DOT formula, Asking which benchmark source, Pushing for actual numbers, Addressing benchmark selection rationale
```

**What AI Did Well:**
```
Acknowledged correct general approach, Positive tone
```

---

## 🔄 Workflow Summary

```
1. Expert receives Google Form link
         ↓
2. Expert reviews AI feedback sample
         ↓
3. Expert completes form with corrections
         ↓
4. Responses collect in Google Form/Sheets
         ↓
5. Export to CSV weekly/monthly
         ↓
6. Import: python add_expert_knowledge.py corrections file.csv
         ↓
7. Expert knowledge added to RAG system
         ↓
8. Enhanced prompts now include expert patterns
```

---

## 📈 Recommended Collection Schedule

### Phase 1: Initial Validation (Week 1-2)
- **Goal**: 20-30 expert corrections
- **Approach**: Send form to 2-3 experts with 10 pre-selected AI feedback samples
- **Import**: After each expert completes their batch

### Phase 2: Ongoing Collection (Monthly)
- **Goal**: 10-20 new corrections per month
- **Approach**: Sample recent AI feedback, flag the uncertain/low-rated ones
- **Import**: Monthly batch import

### Phase 3: Continuous (Ongoing)
- **Goal**: Build to 100+ corrections over 6 months
- **Approach**: In-app feedback flags responses for expert review
- **Import**: Quarterly batch imports

---

## 🚨 Troubleshooting

### Issue: Column headers don't match

**Solution**: Edit the CSV file's first line to match exactly:
```csv
Timestamp,Expert Name,Module ID,Scenario ID,Difficulty Level,Competency Area,User Response,AI Feedback,Expert Correction,Expert Reasoning,What AI Missed,What AI Did Well
```

### Issue: Import shows "Missing required column" error

**Solution**: Check that ALL required fields are included and column names match exactly (case-sensitive).

### Issue: Expert can't access form

**Solution**: Check form sharing settings - make sure "Anyone with the link" can respond, or add their email specifically.

### Issue: Responses not appearing in Sheets

**Solution**: Make sure you clicked the green Sheets icon in the Responses tab to create the linked spreadsheet.

---

## 📎 Appendix A: Google Apps Script for Auto-Export (Advanced)

If you want to automatically export responses to a CSV on a schedule:

1. In Google Sheets (linked to your form), click **Extensions** → **Apps Script**
2. Paste this code:

```javascript
function exportToCSV() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheets()[0];
  var fileName = "expert_reviews_" + Utilities.formatDate(new Date(), "GMT", "yyyy-MM-dd") + ".csv";

  var csvFile = convertRangeToCsvFile_(sheet);

  // Save to Google Drive
  DriveApp.createFile(fileName, csvFile);
}

function convertRangeToCsvFile_(sheet) {
  var activeRange = sheet.getDataRange();
  try {
    var data = activeRange.getValues();
    var csvFile = undefined;

    if (data.length > 1) {
      var csv = "";
      for (var row = 0; row < data.length; row++) {
        for (var col = 0; col < data[row].length; col++) {
          if (data[row][col].toString().indexOf(",") != -1) {
            data[row][col] = "\"" + data[row][col] + "\"";
          }
        }
        if (row < data.length-1) {
          csv += data[row].join(",") + "\r\n";
        } else {
          csv += data[row];
        }
      }
      csvFile = csv;
    }
    return csvFile;
  }
  catch(err) {
    Logger.log(err);
    Browser.msgBox(err);
  }
}
```

3. Set up a trigger:
   - Click **Triggers** (clock icon)
   - **Add Trigger**
   - Function: `exportToCSV`
   - Event source: Time-driven
   - Type: Week timer
   - Day: Monday
   - Time: 9am-10am

This will automatically export your responses to Google Drive every Monday morning.

---

## 📚 Additional Resources

- **Expert RAG Setup Guide**: `EXPERT_RAG_SETUP.md`
- **Import Script Help**: `python add_expert_knowledge.py` (no arguments shows usage)
- **Sample CSV Template**: `python add_expert_knowledge.py template-csv`

---

## 💡 Tips for Maximum Impact

1. **Batch Reviews**: Have experts review 5-10 samples at once for efficiency
2. **Diversity**: Get corrections from experts with different backgrounds (academic vs. community, pediatric vs. adult)
3. **Focus on Gaps**: Prioritize scenarios where AI struggled (low user ratings, flagged responses)
4. **Iterate**: Start with 20 corrections, test improvement, then collect more
5. **Feedback Loop**: Share with experts how their corrections improved the system

---

## ✅ Quick Start Checklist

- [ ] Create Google Form using the structure above
- [ ] Test the form with a sample submission
- [ ] Send to 2-3 expert reviewers with pre-selected AI feedback samples
- [ ] Collect 10-20 initial corrections
- [ ] Export to CSV from Google Sheets
- [ ] Import: `python add_expert_knowledge.py corrections file.csv`
- [ ] Test enhanced feedback generation
- [ ] Measure improvement vs. baseline

---

**Questions?** Contact: aspfeedback@cchmc.org or dbhaslam@gmail.com
