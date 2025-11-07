#!/usr/bin/env python3
"""
Rubric-based Scoring System for ASP AI Agent
Provides consistent, standards-based evaluation of learner responses
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime

class CriterionLevel(Enum):
    """Performance levels for rubric criteria"""
    EXEMPLARY = 4  # Exceeds expectations
    PROFICIENT = 3  # Meets expectations
    DEVELOPING = 2  # Approaching expectations
    BEGINNING = 1  # Below expectations
    NOT_EVIDENT = 0  # No evidence

@dataclass
class RubricCriterion:
    """Single criterion in a rubric"""
    name: str
    description: str
    weight: float = 1.0  # Relative importance
    levels: Dict[CriterionLevel, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default level descriptions if not provided"""
        if not self.levels:
            self.levels = {
                CriterionLevel.EXEMPLARY: f"Demonstrates exceptional understanding of {self.name.lower()}",
                CriterionLevel.PROFICIENT: f"Shows solid understanding of {self.name.lower()}",
                CriterionLevel.DEVELOPING: f"Shows partial understanding of {self.name.lower()}",
                CriterionLevel.BEGINNING: f"Shows limited understanding of {self.name.lower()}",
                CriterionLevel.NOT_EVIDENT: f"No evidence of {self.name.lower()}"
            }

@dataclass
class RubricScore:
    """Score for a single criterion"""
    criterion: RubricCriterion
    level: CriterionLevel
    score: float
    evidence: str
    feedback: str

@dataclass
class EvaluationResult:
    """Complete evaluation result using rubric"""
    rubric_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    criterion_scores: List[RubricScore] = field(default_factory=list)
    total_score: float = 0.0
    percentage: float = 0.0
    overall_level: CriterionLevel = CriterionLevel.BEGINNING
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    specific_feedback: str = ""
    next_steps: List[str] = field(default_factory=list)

class RubricLibrary:
    """Library of rubrics for different ASP competencies"""
    
    def __init__(self):
        self.rubrics = self._initialize_rubrics()
    
    def _initialize_rubrics(self) -> Dict[str, List[RubricCriterion]]:
        """Initialize standard rubrics for each module"""
        return {
            "leadership_business_case": [
                RubricCriterion(
                    name="Value Metrics Identification",
                    description="Identifies relevant metrics to demonstrate ASP value",
                    weight=1.5,
                    levels={
                        CriterionLevel.EXEMPLARY: "Identifies 5+ diverse metrics across clinical, financial, and quality domains with clear linkages",
                        CriterionLevel.PROFICIENT: "Identifies 3-4 relevant metrics across multiple domains",
                        CriterionLevel.DEVELOPING: "Identifies 2-3 metrics, mostly from one domain",
                        CriterionLevel.BEGINNING: "Identifies 1-2 basic metrics",
                        CriterionLevel.NOT_EVIDENT: "No clear metrics identified"
                    }
                ),
                RubricCriterion(
                    name="Data Utilization",
                    description="Uses data effectively to support arguments",
                    weight=1.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Uses specific, relevant data with benchmarks and trends to build compelling case",
                        CriterionLevel.PROFICIENT: "Uses appropriate data to support key points",
                        CriterionLevel.DEVELOPING: "Uses some data but lacks specificity or relevance",
                        CriterionLevel.BEGINNING: "Minimal data usage, mostly anecdotal",
                        CriterionLevel.NOT_EVIDENT: "No data provided"
                    }
                ),
                RubricCriterion(
                    name="Stakeholder Communication",
                    description="Tailors message to audience needs",
                    weight=1.2,
                    levels={
                        CriterionLevel.EXEMPLARY: "Message perfectly tailored to administrator priorities with clear action items",
                        CriterionLevel.PROFICIENT: "Good alignment with administrator concerns",
                        CriterionLevel.DEVELOPING: "Some attempt to address administrator perspective",
                        CriterionLevel.BEGINNING: "Generic messaging, not audience-specific",
                        CriterionLevel.NOT_EVIDENT: "No consideration of audience"
                    }
                ),
                RubricCriterion(
                    name="ROI Calculation",
                    description="Demonstrates financial return on investment",
                    weight=1.3,
                    levels={
                        CriterionLevel.EXEMPLARY: "Clear ROI calculation with both cost savings and cost avoidance, time horizon specified",
                        CriterionLevel.PROFICIENT: "Basic ROI presented with supporting calculations",
                        CriterionLevel.DEVELOPING: "Mentions financial benefit but lacks clear calculation",
                        CriterionLevel.BEGINNING: "Vague financial references",
                        CriterionLevel.NOT_EVIDENT: "No financial analysis"
                    }
                )
            ],
            
            "analytics_dot_calculation": [
                RubricCriterion(
                    name="Calculation Accuracy",
                    description="Correctly calculates DOT/1000 patient days",
                    weight=2.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Perfect calculation with clear methodology and verification",
                        CriterionLevel.PROFICIENT: "Correct calculation with appropriate formula",
                        CriterionLevel.DEVELOPING: "Minor calculation errors but correct approach",
                        CriterionLevel.BEGINNING: "Major calculation errors or wrong formula",
                        CriterionLevel.NOT_EVIDENT: "No calculation attempted"
                    }
                ),
                RubricCriterion(
                    name="Data Validation",
                    description="Identifies data quality considerations",
                    weight=1.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Identifies multiple validation needs and proposes verification methods",
                        CriterionLevel.PROFICIENT: "Recognizes key data limitations",
                        CriterionLevel.DEVELOPING: "Some awareness of data quality issues",
                        CriterionLevel.BEGINNING: "Minimal consideration of data validity",
                        CriterionLevel.NOT_EVIDENT: "No data validation considered"
                    }
                ),
                RubricCriterion(
                    name="Interpretation",
                    description="Interprets results in clinical context",
                    weight=1.2,
                    levels={
                        CriterionLevel.EXEMPLARY: "Comprehensive interpretation with benchmarks, trends, and clinical significance",
                        CriterionLevel.PROFICIENT: "Good interpretation with context",
                        CriterionLevel.DEVELOPING: "Basic interpretation provided",
                        CriterionLevel.BEGINNING: "Limited interpretation",
                        CriterionLevel.NOT_EVIDENT: "No interpretation"
                    }
                ),
                RubricCriterion(
                    name="Next Steps",
                    description="Identifies appropriate follow-up actions",
                    weight=0.8,
                    levels={
                        CriterionLevel.EXEMPLARY: "Detailed action plan with priorities and timeline",
                        CriterionLevel.PROFICIENT: "Clear next steps identified",
                        CriterionLevel.DEVELOPING: "Some next steps mentioned",
                        CriterionLevel.BEGINNING: "Vague recommendations",
                        CriterionLevel.NOT_EVIDENT: "No next steps identified"
                    }
                )
            ],
            
            "behavioral_bias_identification": [
                RubricCriterion(
                    name="Bias Recognition",
                    description="Correctly identifies cognitive bias",
                    weight=1.5,
                    levels={
                        CriterionLevel.EXEMPLARY: "Identifies specific bias with clear explanation and additional biases that may be present",
                        CriterionLevel.PROFICIENT: "Correctly identifies primary bias",
                        CriterionLevel.DEVELOPING: "Recognizes bias presence but imprecise identification",
                        CriterionLevel.BEGINNING: "Vague understanding of bias",
                        CriterionLevel.NOT_EVIDENT: "No bias identified"
                    }
                ),
                RubricCriterion(
                    name="Communication Approach",
                    description="Develops respectful, effective communication strategy",
                    weight=1.3,
                    levels={
                        CriterionLevel.EXEMPLARY: "Sophisticated approach respecting expertise while addressing bias, multiple strategies",
                        CriterionLevel.PROFICIENT: "Respectful approach with clear strategy",
                        CriterionLevel.DEVELOPING: "Basic approach, somewhat respectful",
                        CriterionLevel.BEGINNING: "Potentially confrontational or ineffective",
                        CriterionLevel.NOT_EVIDENT: "No communication strategy"
                    }
                ),
                RubricCriterion(
                    name="Evidence Integration",
                    description="Uses evidence to address bias",
                    weight=1.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Multiple evidence sources strategically presented",
                        CriterionLevel.PROFICIENT: "Good use of relevant evidence",
                        CriterionLevel.DEVELOPING: "Some evidence mentioned",
                        CriterionLevel.BEGINNING: "Limited evidence use",
                        CriterionLevel.NOT_EVIDENT: "No evidence provided"
                    }
                ),
                RubricCriterion(
                    name="Behavior Change Strategy",
                    description="Proposes effective behavior change approach",
                    weight=1.2,
                    levels={
                        CriterionLevel.EXEMPLARY: "Evidence-based behavior change framework with specific techniques",
                        CriterionLevel.PROFICIENT: "Clear behavior change strategy",
                        CriterionLevel.DEVELOPING: "Basic ideas for behavior change",
                        CriterionLevel.BEGINNING: "Vague or ineffective approach",
                        CriterionLevel.NOT_EVIDENT: "No behavior change strategy"
                    }
                )
            ],
            
            "clinical_protocol_development": [
                RubricCriterion(
                    name="Clinical Criteria",
                    description="Develops clear, evidence-based clinical criteria",
                    weight=1.5,
                    levels={
                        CriterionLevel.EXEMPLARY: "Comprehensive criteria with clear inclusion/exclusion, evidence-based",
                        CriterionLevel.PROFICIENT: "Good clinical criteria with rationale",
                        CriterionLevel.DEVELOPING: "Basic criteria but lacks detail",
                        CriterionLevel.BEGINNING: "Vague or incomplete criteria",
                        CriterionLevel.NOT_EVIDENT: "No clinical criteria"
                    }
                ),
                RubricCriterion(
                    name="Safety Considerations",
                    description="Addresses patient safety comprehensively",
                    weight=2.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Thorough safety analysis with mitigation strategies and monitoring plan",
                        CriterionLevel.PROFICIENT: "Good safety considerations addressed",
                        CriterionLevel.DEVELOPING: "Some safety aspects considered",
                        CriterionLevel.BEGINNING: "Limited safety consideration",
                        CriterionLevel.NOT_EVIDENT: "No safety considerations"
                    }
                ),
                RubricCriterion(
                    name="Implementation Feasibility",
                    description="Considers practical implementation aspects",
                    weight=1.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Detailed implementation plan with workflow integration and contingencies",
                        CriterionLevel.PROFICIENT: "Good consideration of implementation",
                        CriterionLevel.DEVELOPING: "Basic implementation ideas",
                        CriterionLevel.BEGINNING: "Limited feasibility consideration",
                        CriterionLevel.NOT_EVIDENT: "No implementation planning"
                    }
                ),
                RubricCriterion(
                    name="Monitoring and Evaluation",
                    description="Includes plan for monitoring and evaluation",
                    weight=1.0,
                    levels={
                        CriterionLevel.EXEMPLARY: "Comprehensive monitoring with metrics, timeline, and adjustment triggers",
                        CriterionLevel.PROFICIENT: "Clear monitoring plan",
                        CriterionLevel.DEVELOPING: "Basic monitoring mentioned",
                        CriterionLevel.BEGINNING: "Vague monitoring ideas",
                        CriterionLevel.NOT_EVIDENT: "No monitoring plan"
                    }
                )
            ]
        }
    
    def get_rubric(self, rubric_id: str) -> Optional[List[RubricCriterion]]:
        """Get a specific rubric by ID"""
        return self.rubrics.get(rubric_id)
    
    def list_available_rubrics(self) -> List[str]:
        """List all available rubric IDs"""
        return list(self.rubrics.keys())

class RubricScorer:
    """Scores responses using rubrics"""
    
    def __init__(self):
        self.library = RubricLibrary()
        self.scoring_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize text patterns for automated scoring hints"""
        return {
            "value_metrics": [
                re.compile(r'(cost|saving|ROI|return|investment)', re.I),
                re.compile(r'(length.*stay|LOS|readmission)', re.I),
                re.compile(r'(mortality|adverse|safety|harm)', re.I),
                re.compile(r'(resistance|susceptibility|CDI|C\.?\s?diff)', re.I),
                re.compile(r'(satisfaction|quality|metric)', re.I)
            ],
            "data_usage": [
                re.compile(r'\d+\.?\d*\s*(%|percent|days|dollars|\$)', re.I),
                re.compile(r'(baseline|benchmark|compare|trend)', re.I),
                re.compile(r'(data|evidence|study|research)', re.I)
            ],
            "bias_terms": [
                re.compile(r'(availability|heuristic|confirmation|bias)', re.I),
                re.compile(r'(anchor|recency|experience)', re.I),
                re.compile(r'(cognitive|thinking|pattern)', re.I)
            ],
            "safety_terms": [
                re.compile(r'(safety|adverse|harm|risk)', re.I),
                re.compile(r'(monitor|track|review|assess)', re.I),
                re.compile(r'(contraindication|allergy|interaction)', re.I)
            ]
        }
    
    def evaluate_response(self, response: str, rubric_id: str, 
                         context: Optional[Dict] = None) -> EvaluationResult:
        """Evaluate a response using the specified rubric"""
        rubric = self.library.get_rubric(rubric_id)
        if not rubric:
            raise ValueError(f"Rubric '{rubric_id}' not found")
        
        result = EvaluationResult(rubric_id=rubric_id)
        total_weight = sum(criterion.weight for criterion in rubric)
        weighted_score = 0.0
        
        # Score each criterion
        for criterion in rubric:
            score = self._score_criterion(response, criterion, context)
            result.criterion_scores.append(score)
            weighted_score += score.score * criterion.weight
            
            # Track strengths and improvements
            if score.level in [CriterionLevel.EXEMPLARY, CriterionLevel.PROFICIENT]:
                result.strengths.append(f"{criterion.name}: {score.feedback}")
            elif score.level in [CriterionLevel.BEGINNING, CriterionLevel.NOT_EVIDENT]:
                result.areas_for_improvement.append(f"{criterion.name}: {score.feedback}")
        
        # Calculate overall scores
        result.total_score = weighted_score
        result.percentage = (weighted_score / (total_weight * 4)) * 100  # 4 is max score per criterion
        
        # Determine overall level
        if result.percentage >= 85:
            result.overall_level = CriterionLevel.EXEMPLARY
        elif result.percentage >= 70:
            result.overall_level = CriterionLevel.PROFICIENT
        elif result.percentage >= 50:
            result.overall_level = CriterionLevel.DEVELOPING
        elif result.percentage >= 25:
            result.overall_level = CriterionLevel.BEGINNING
        else:
            result.overall_level = CriterionLevel.NOT_EVIDENT
        
        # Generate specific feedback
        result.specific_feedback = self._generate_specific_feedback(result, response)
        
        # Suggest next steps
        result.next_steps = self._suggest_next_steps(result, rubric_id)
        
        return result
    
    def _score_criterion(self, response: str, criterion: RubricCriterion, 
                        context: Optional[Dict]) -> RubricScore:
        """Score a single criterion"""
        # This is where you'd integrate with the LLM for sophisticated scoring
        # For now, using pattern matching as a demonstration
        
        evidence_found = []
        score_indicators = 0
        
        # Check for relevant patterns based on criterion name
        if "metric" in criterion.name.lower():
            patterns = self.scoring_patterns.get("value_metrics", [])
            for pattern in patterns:
                if pattern.search(response):
                    score_indicators += 1
                    match = pattern.search(response)
                    if match:
                        evidence_found.append(match.group(0))
                        
        elif "data" in criterion.name.lower():
            patterns = self.scoring_patterns.get("data_usage", [])
            for pattern in patterns:
                if pattern.search(response):
                    score_indicators += 1
                    match = pattern.search(response)
                    if match:
                        evidence_found.append(match.group(0))
                        
        elif "bias" in criterion.name.lower():
            patterns = self.scoring_patterns.get("bias_terms", [])
            for pattern in patterns:
                if pattern.search(response):
                    score_indicators += 1
                    match = pattern.search(response)
                    if match:
                        evidence_found.append(match.group(0))
                        
        elif "safety" in criterion.name.lower():
            patterns = self.scoring_patterns.get("safety_terms", [])
            for pattern in patterns:
                if pattern.search(response):
                    score_indicators += 1
                    match = pattern.search(response)
                    if match:
                        evidence_found.append(match.group(0))
        
        # Determine level based on indicators found
        if score_indicators >= 4:
            level = CriterionLevel.EXEMPLARY
        elif score_indicators >= 3:
            level = CriterionLevel.PROFICIENT
        elif score_indicators >= 2:
            level = CriterionLevel.DEVELOPING
        elif score_indicators >= 1:
            level = CriterionLevel.BEGINNING
        else:
            level = CriterionLevel.NOT_EVIDENT
        
        # Create score
        return RubricScore(
            criterion=criterion,
            level=level,
            score=float(level.value),
            evidence=", ".join(evidence_found[:3]) if evidence_found else "Limited evidence found",
            feedback=criterion.levels[level]
        )
    
    def _generate_specific_feedback(self, result: EvaluationResult, response: str) -> str:
        """Generate specific, actionable feedback"""
        feedback_parts = []
        
        # Overall performance
        if result.overall_level == CriterionLevel.EXEMPLARY:
            feedback_parts.append("Excellent work! You've demonstrated mastery of this competency.")
        elif result.overall_level == CriterionLevel.PROFICIENT:
            feedback_parts.append("Good job! You've shown solid understanding.")
        elif result.overall_level == CriterionLevel.DEVELOPING:
            feedback_parts.append("You're making progress. Let's focus on strengthening key areas.")
        else:
            feedback_parts.append("Let's work on building foundational understanding.")
        
        # Specific strengths
        if result.strengths:
            feedback_parts.append(f"Strengths: {result.strengths[0]}")
        
        # Key improvement area
        if result.areas_for_improvement:
            feedback_parts.append(f"Focus area: {result.areas_for_improvement[0]}")
        
        return " ".join(feedback_parts)
    
    def _suggest_next_steps(self, result: EvaluationResult, rubric_id: str) -> List[str]:
        """Suggest specific next steps based on performance"""
        steps = []
        
        if result.overall_level == CriterionLevel.EXEMPLARY:
            steps.append("Try a more complex scenario in this domain")
            steps.append("Consider mentoring others on this topic")
            
        elif result.overall_level == CriterionLevel.PROFICIENT:
            steps.append("Practice with edge cases and exceptions")
            steps.append("Explore system-level applications")
            
        elif result.overall_level == CriterionLevel.DEVELOPING:
            if result.areas_for_improvement:
                area = result.areas_for_improvement[0].split(":")[0]
                steps.append(f"Review resources on {area}")
                steps.append("Try a similar scenario with more scaffolding")
                
        else:
            steps.append("Review the fundamental concepts")
            steps.append("Work through a guided example")
            steps.append("Practice with simplified scenarios")
        
        return steps
    
    def compare_evaluations(self, evaluations: List[EvaluationResult]) -> Dict:
        """Compare multiple evaluations to show progress"""
        if not evaluations:
            return {}
        
        comparison = {
            "total_evaluations": len(evaluations),
            "score_progression": [],
            "level_progression": [],
            "consistent_strengths": [],
            "persistent_challenges": [],
            "improvement_rate": 0.0
        }
        
        # Track progression
        for eval in evaluations:
            comparison["score_progression"].append(round(eval.percentage, 1))
            comparison["level_progression"].append(eval.overall_level.name)
        
        # Calculate improvement rate
        if len(evaluations) >= 2:
            first_score = evaluations[0].percentage
            last_score = evaluations[-1].percentage
            comparison["improvement_rate"] = round(last_score - first_score, 1)
        
        # Find consistent patterns
        all_strengths = []
        all_improvements = []
        for eval in evaluations:
            all_strengths.extend(eval.strengths)
            all_improvements.extend(eval.areas_for_improvement)
        
        # Most common strengths and challenges
        from collections import Counter
        strength_counts = Counter(all_strengths)
        improvement_counts = Counter(all_improvements)
        
        comparison["consistent_strengths"] = [s for s, c in strength_counts.most_common(3)]
        comparison["persistent_challenges"] = [i for i, c in improvement_counts.most_common(3)]
        
        return comparison

# Global rubric scorer instance
rubric_scorer = RubricScorer()