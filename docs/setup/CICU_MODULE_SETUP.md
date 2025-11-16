# CICU Antibiotics Training Module - Setup Guide

## Overview

The CICU (Cardiac Intensive Care Unit) Antibiotics Training Module is an interactive educational platform designed to help Infectious Disease fellows develop expertise in reducing prolonged broad-spectrum antibiotic use.

## Module Focus

**Clinical Problem**: Overuse of meropenem and vancomycin in CICU for prolonged periods (>7 days) despite negative cultures after 48-72 hours.

**Learning Objectives**:
1. Analyze antibiotic utilization data to identify inappropriate prolonged use patterns
2. Design evidence-based interventions to reduce unnecessary broad-spectrum antibiotics
3. Implement behavioral change strategies to modify prescriber habits
4. Create metrics to track success and identify areas needing countermeasures

## How to Access the Module

### Option 1: Web Interface (Recommended)

1. **Start the unified server**:
   ```bash
   cd /home/david/projects/asp_ai_agent
   python3 unified_server.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Access the CICU module**:
   - Click on "CICU Antibiotics Training Module" from the home page
   - Or directly navigate to: `http://localhost:5000/cicu_module.html`

### Option 2: Command-Line Interactive Session

Run the interactive Python script:
```bash
cd /home/david/projects/asp_ai_agent
python3 run_cicu_interactive.py
```

## Module Structure

### Difficulty Levels

The module includes 4 progressive difficulty levels:

1. **Beginner**: Data Analysis & Problem Identification
   - Focus on calculating metrics (DOT/1000 patient days)
   - Identifying gaps between guidelines and practice
   - Creating data visualizations
   - Presenting to leadership

2. **Intermediate**: Intervention Design & Stakeholder Engagement
   - Developing cardiac-specific guidelines
   - Creating timeout protocols
   - Designing communication frameworks
   - Building champion networks
   - Addressing psychological safety

3. **Advanced**: Implementation & Real-Time Problem Solving
   - Root cause analysis
   - Handling resistant attendings
   - Clarifying decision-making roles
   - Implementing audit and feedback systems
   - Addressing adverse events

4. **Expert**: Sustainability, Scale & System-Level Change
   - Creating adaptation frameworks
   - Onboarding programs for rotating staff
   - Quality metrics and accountability
   - Clinical decision support tools
   - Publishing and dissemination

### Features

- **Progressive Scenarios**: Each difficulty level presents realistic clinical challenges
- **AI-Powered Feedback**: Get detailed, personalized feedback on your responses using Gemini or Claude AI
- **Hint System**: Access progressive hints when you need guidance
- **Metrics Tracker**: View implementation metrics and targets
- **Countermeasure Strategies**: Get specific strategies for common barriers

## API Endpoints

The following API endpoints are available:

- `GET /api/modules/cicu/scenario?level=beginner` - Get scenario for specified level
- `GET /api/modules/cicu/hint?level=beginner&hint_number=0` - Get hints
- `POST /api/modules/cicu/evaluate` - Evaluate user responses
- `GET /api/modules/cicu/metrics` - Get implementation metrics tracker
- `GET /api/modules/cicu/countermeasures?barrier_type=provider_resistance` - Get countermeasure strategies

## Integration with ASP System

The CICU module integrates with the broader ASP AI Agent system:

- **Session Management**: Tracks user progress across difficulty levels
- **Adaptive Learning**: Adjusts difficulty based on performance
- **Rubric Scoring**: Evaluates responses across 4 competency domains:
  - Data Analysis
  - Behavioral Intervention
  - Implementation Science
  - Clinical Decision Making

## File Locations

- **Module Code**: `/home/david/projects/asp_ai_agent/modules/cicu_prolonged_antibiotics_module.py`
- **Web Interface**: `/home/david/projects/asp_ai_agent/cicu_module.html`
- **Interactive CLI**: `/home/david/projects/asp_ai_agent/run_cicu_interactive.py`
- **Server Integration**: `/home/david/projects/asp_ai_agent/unified_server.py`

## Requirements

- Python 3.8+
- Flask and Flask-CORS
- Access to AI models (Gemini API key or local Ollama)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Tips for Learners

1. **Start at Beginner Level**: Even experienced clinicians should start at the beginner level to understand the scenario progression
2. **Use Hints Wisely**: Hints are designed to guide thinking, not provide answers
3. **Be Comprehensive**: Address all tasks in each scenario
4. **Think Systems-Level**: Consider multiple stakeholders and long-term sustainability
5. **Reference Evidence**: Mention specific guidelines, frameworks, or published literature

## Support

For questions or issues:
- Check the main ASP AI Agent documentation
- Review the module code for detailed rubrics and expected competencies
- Contact the module administrator

## Future Enhancements

Planned features:
- Multi-user collaboration scenarios
- Real-time peer comparison
- Exportable progress reports
- Integration with institutional EMR data
- Mobile-responsive design improvements
