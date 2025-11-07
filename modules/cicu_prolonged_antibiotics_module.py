"""
CICU Prolonged Antibiotics Module - ASP Educational Module
Clinical Problem: Overuse of meropenem and vancomycin in CICU for prolonged periods
despite negative cultures

Module Focus: Addressing prolonged broad-spectrum antibiotic use in the Cardiac Intensive Care Unit
Target Learners: ASP Fellows (PGY 4-6)
Competencies: All 4 domains (Leadership, Analytics, Behavioral Science, Clinical)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"  
    ADVANCED = "advanced"
    EXPERT = "expert"

class CICUAntibioticsModule:
    """
    Educational module for addressing prolonged broad-spectrum antibiotic use in CICU
    """
    
    def __init__(self):
        self.module_id = "cicu_prolonged_antibiotics"
        self.module_title = "Reducing Prolonged Broad-Spectrum Antibiotic Use in the CICU"
        self.clinical_problem = """
        The Cardiac Intensive Care Unit (CICU) frequently uses meropenem and vancomycin 
        for prolonged periods (>7 days) in children with fever, even when all cultures 
        have been negative after 48-72 hours. This represents inappropriate antibiotic 
        use that increases resistance risk, adverse events, and costs.
        """
        
        self.learning_objectives = [
            "Analyze antibiotic utilization data to identify inappropriate prolonged use patterns",
            "Design an evidence-based intervention to reduce unnecessary broad-spectrum antibiotics",
            "Implement behavioral change strategies to modify prescriber habits",
            "Create metrics to track success and identify areas needing countermeasures"
        ]
        
        self.scenarios = self._initialize_scenarios()
        self.rubrics = self._initialize_rubrics()
        self.hints = self._initialize_hints()
        self.scaffolding = self._initialize_scaffolding()
        
    def _initialize_scenarios(self) -> Dict[DifficultyLevel, Dict]:
        """Initialize progressive scenarios from beginner to expert"""
        return {
            DifficultyLevel.BEGINNER: {
                "title": "Data Analysis & Problem Identification",
                "description": """
                You've been asked to review CICU antibiotic use data. You find:
                - 65% of patients receive meropenem + vancomycin empirically
                - Average duration: 8.5 days
                - 78% have negative cultures at 48 hours
                - Only 12% have documented de-escalation discussions
                
                How would you approach analyzing this problem and presenting it to CICU leadership?
                """,
                "key_tasks": [
                    "Calculate days of therapy (DOT) per 1000 patient days",
                    "Identify the gap between guidelines and practice",
                    "Create a compelling data visualization",
                    "Draft initial problem statement for leadership"
                ],
                "expected_competencies": ["data_analysis", "communication", "problem_identification"]
            },
            
            DifficultyLevel.INTERMEDIATE: {
                "title": "Intervention Design & Stakeholder Engagement",
                "description": """
                CICU leadership acknowledges the problem but cites several barriers:
                - "These are critically ill cardiac patients - we can't take risks"
                - "Our patients are different from general PICU"
                - "Attendings rotate weekly - hard to maintain consistency"
                - "Fellows are afraid to challenge antibiotic decisions"
                
                Design a multi-faceted intervention addressing these specific barriers.
                """,
                "key_tasks": [
                    "Develop cardiac-specific antibiotic guidelines with stop points",
                    "Create a 48-hour timeout protocol with clear criteria",
                    "Design a communication framework for antibiotic discussions",
                    "Build a champion network including nurses and pharmacists",
                    "Address the hierarchy/fear issues with psychological safety measures"
                ],
                "expected_competencies": ["behavioral_science", "change_management", "protocol_development"]
            },
            
            DifficultyLevel.ADVANCED: {
                "title": "Implementation & Real-Time Problem Solving",
                "description": """
                Your intervention launched 2 months ago. Initial results show:
                - 30% reduction in meropenem+vancomycin starts (good!)
                - But duration only decreased from 8.5 to 7.2 days (not enough)
                - 3 attendings consistently bypass the protocol
                - 1 case of late-onset sepsis has everyone scared
                - Nurses report confusion about who makes de-escalation decisions
                
                How do you adapt your approach to maintain momentum while addressing these challenges?
                """,
                "key_tasks": [
                    "Perform root cause analysis on the late sepsis case",
                    "Develop targeted interventions for resistant attendings",
                    "Clarify decision-making roles and responsibilities",
                    "Create positive reinforcement strategies for early adopters",
                    "Implement real-time audit and feedback system",
                    "Address the fear response with data and education"
                ],
                "expected_competencies": ["adaptive_leadership", "quality_improvement", "conflict_resolution"]
            },
            
            DifficultyLevel.EXPERT: {
                "title": "Sustainability, Scale & System-Level Change",
                "description": """
                After 6 months, your CICU intervention shows:
                - 45% reduction in inappropriate broad-spectrum use
                - $380,000 in cost savings
                - No increase in sepsis or mortality
                - Improved nurse satisfaction scores
                
                However:
                - The NICU wants to adopt but has different patient population
                - New cardiac surgery fellows arrive who weren't part of initial training
                - Hospital administration wants to make this a quality metric
                - You discover similar issues in step-down units
                - Insurance denials for prolonged antibiotics are increasing
                
                Create a comprehensive plan for sustaining gains, scaling success, and 
                embedding this into the hospital's culture and systems.
                """,
                "key_tasks": [
                    "Develop unit-specific adaptation framework",
                    "Create onboarding program for rotating staff",
                    "Design quality metrics and accountability structures",
                    "Build automated clinical decision support tools",
                    "Establish antimicrobial stewardship rounds in all ICUs",
                    "Navigate insurance/financial implications",
                    "Publish and disseminate findings for broader impact"
                ],
                "expected_competencies": ["systems_thinking", "strategic_planning", "sustainability", "dissemination"]
            }
        }
    
    def _initialize_rubrics(self) -> Dict[str, Dict]:
        """Initialize assessment rubrics for each competency area"""
        return {
            "data_analysis": {
                "exemplary": {
                    "score": 5,
                    "criteria": [
                        "Calculates multiple relevant metrics (DOT, LOT, SIR)",
                        "Performs risk-adjusted comparisons with benchmarks",
                        "Identifies patterns by provider, timing, and patient factors",
                        "Creates compelling visualizations with actionable insights",
                        "Includes cost and resistance impact analysis"
                    ]
                },
                "proficient": {
                    "score": 4,
                    "criteria": [
                        "Calculates DOT correctly",
                        "Makes appropriate benchmark comparisons",
                        "Identifies major patterns in the data",
                        "Creates clear data presentations",
                        "Mentions cost or resistance implications"
                    ]
                },
                "developing": {
                    "score": 3,
                    "criteria": [
                        "Attempts DOT calculation with minor errors",
                        "Makes some comparisons to guidelines",
                        "Identifies obvious patterns",
                        "Creates basic charts or tables",
                        "Limited analysis depth"
                    ]
                },
                "emerging": {
                    "score": 2,
                    "criteria": [
                        "Recognizes need for metrics but calculation errors",
                        "Minimal benchmark awareness",
                        "Describes data without pattern recognition",
                        "Presentation lacks clarity",
                        "Missing key analytical elements"
                    ]
                },
                "not_evident": {
                    "score": 1,
                    "criteria": [
                        "No meaningful metrics calculated",
                        "No benchmark comparisons",
                        "No pattern identification",
                        "Poor or no data presentation",
                        "Lacks analytical approach"
                    ]
                }
            },
            
            "behavioral_intervention": {
                "exemplary": {
                    "score": 5,
                    "criteria": [
                        "Identifies multiple cognitive biases and addresses each",
                        "Uses evidence-based behavior change frameworks",
                        "Creates psychological safety while maintaining accountability",
                        "Designs nudges and choice architecture changes",
                        "Includes social influence and peer comparison strategies"
                    ]
                },
                "proficient": {
                    "score": 4,
                    "criteria": [
                        "Identifies key cognitive biases",
                        "Applies some behavior change principles",
                        "Addresses hierarchy and fear issues",
                        "Includes feedback mechanisms",
                        "Uses champion/opinion leader strategy"
                    ]
                },
                "developing": {
                    "score": 3,
                    "criteria": [
                        "Recognizes behavioral barriers exist",
                        "Suggests education as primary intervention",
                        "Some attention to communication issues",
                        "Basic feedback planned",
                        "Limited behavior change theory application"
                    ]
                },
                "emerging": {
                    "score": 2,
                    "criteria": [
                        "Minimal behavioral insight",
                        "Relies solely on policies/mandates",
                        "Doesn't address psychological factors",
                        "No feedback mechanisms",
                        "One-size-fits-all approach"
                    ]
                },
                "not_evident": {
                    "score": 1,
                    "criteria": [
                        "No behavioral considerations",
                        "Ignores human factors",
                        "No change management approach",
                        "Policy-only focus",
                        "No stakeholder engagement"
                    ]
                }
            },
            
            "implementation_science": {
                "exemplary": {
                    "score": 5,
                    "criteria": [
                        "Uses implementation framework (PDSA, RE-AIM, etc.)",
                        "Plans for adoption, implementation, and sustainability",
                        "Includes process and outcome metrics",
                        "Addresses contextual factors and adaptation",
                        "Plans for scale and spread with fidelity measures"
                    ]
                },
                "proficient": {
                    "score": 4,
                    "criteria": [
                        "Structured implementation approach",
                        "Includes pilot testing phase",
                        "Defines success metrics",
                        "Some adaptation planning",
                        "Considers sustainability"
                    ]
                },
                "developing": {
                    "score": 3,
                    "criteria": [
                        "Basic implementation plan",
                        "Limited pilot testing",
                        "Few metrics defined",
                        "Minimal adaptation consideration",
                        "Short-term focus"
                    ]
                },
                "emerging": {
                    "score": 2,
                    "criteria": [
                        "Vague implementation approach",
                        "No pilot testing",
                        "Unclear success metrics",
                        "No adaptation planning",
                        "No sustainability consideration"
                    ]
                },
                "not_evident": {
                    "score": 1,
                    "criteria": [
                        "No implementation planning",
                        "No methodology",
                        "No metrics",
                        "No consideration of context",
                        "No long-term thinking"
                    ]
                }
            },
            
            "clinical_decision_making": {
                "exemplary": {
                    "score": 5,
                    "criteria": [
                        "Creates evidence-based, cardiac-specific guidelines",
                        "Includes clear start, continue, and stop criteria",
                        "Addresses special populations (ECMO, VAD, transplant)",
                        "Incorporates biomarkers and clinical trajectories",
                        "Balances safety with stewardship optimally"
                    ]
                },
                "proficient": {
                    "score": 4,
                    "criteria": [
                        "Develops reasonable clinical criteria",
                        "Clear stop points at 48-72 hours",
                        "Some special population considerations",
                        "Uses some biomarkers appropriately",
                        "Good safety/stewardship balance"
                    ]
                },
                "developing": {
                    "score": 3,
                    "criteria": [
                        "Basic clinical guidelines",
                        "Some stop criteria",
                        "Limited special cases addressed",
                        "Minimal biomarker integration",
                        "Overemphasis on either safety or stewardship"
                    ]
                },
                "emerging": {
                    "score": 2,
                    "criteria": [
                        "Vague clinical recommendations",
                        "Unclear decision points",
                        "No special population considerations",
                        "No biomarker use",
                        "Poor risk/benefit assessment"
                    ]
                },
                "not_evident": {
                    "score": 1,
                    "criteria": [
                        "No clinical framework",
                        "No decision criteria",
                        "Ignores clinical complexity",
                        "No evidence base",
                        "Unsafe or impractical recommendations"
                    ]
                }
            }
        }
    
    def _initialize_hints(self) -> Dict[DifficultyLevel, List[str]]:
        """Progressive hints for each difficulty level"""
        return {
            DifficultyLevel.BEGINNER: [
                "Start by calculating DOT/1000 patient days for meropenem and vancomycin separately",
                "Compare your CICU rates to national NHSN benchmarks for pediatric ICUs",
                "Consider creating a run chart showing daily antibiotic use over time",
                "Think about framing the problem in terms of patient safety AND quality",
                "Don't forget to calculate the number of excess antibiotic days that could be avoided"
            ],
            
            DifficultyLevel.INTERMEDIATE: [
                "Consider using the COM-B model (Capability, Opportunity, Motivation) for behavior change",
                "Think about how cognitive biases like 'commission bias' affect antibiotic decisions",
                "A hard stop at 48-72 hours with required documentation might help",
                "Peer comparison data can be powerful - consider provider-specific feedback",
                "Address psychological safety by framing de-escalation as 'optimizing' rather than 'stopping'",
                "Include nurses and pharmacists as active partners, not just physicians"
            ],
            
            DifficultyLevel.ADVANCED: [
                "The late sepsis case needs careful review - was it truly related to de-escalation?",
                "Consider one-on-one academic detailing for resistant attendings",
                "Real-time nudges in the EMR at day 3, 5, and 7 might help",
                "Positive deviance - highlight and learn from attendings with best practices",
                "Create a 'de-escalation champion' role that rotates among fellows",
                "Address the fear with data showing outcomes from other CICUs that improved"
            ],
            
            DifficultyLevel.EXPERT: [
                "Think about creating a toolkit for adaptation rather than rigid protocols",
                "Consider automated EMR alerts with embedded decision support",
                "Quality metrics should be process AND outcome-based with risk adjustment",
                "Create a business case showing ROI for hospital administration",
                "Plan for continuous PDSA cycles rather than one-time implementation",
                "Consider research opportunities - this could be a multi-center collaborative",
                "Think about health equity - are there disparities in who gets prolonged antibiotics?"
            ]
        }
    
    def _initialize_scaffolding(self) -> Dict[str, Dict]:
        """Scaffolding templates for different support levels"""
        return {
            "minimal": {
                "description": "Expert learner needing minimal guidance",
                "support_elements": [
                    "Open-ended problem statement",
                    "Access to literature and guidelines",
                    "Self-directed exploration",
                    "Reflection prompts only"
                ]
            },
            "moderate": {
                "description": "Developing learner needing structured guidance",
                "support_elements": [
                    "Problem broken into sub-components",
                    "Suggested frameworks and models",
                    "Checkpoint questions",
                    "Examples from other settings",
                    "Structured reflection template"
                ]
            },
            "extensive": {
                "description": "Novice learner needing significant support",
                "support_elements": [
                    "Step-by-step guidance",
                    "Templates and worksheets",
                    "Worked examples",
                    "Frequent check-ins",
                    "Collaborative problem-solving",
                    "Direct feedback on each component"
                ]
            }
        }
    
    def get_scenario(self, difficulty: DifficultyLevel) -> Dict:
        """Get scenario for specified difficulty level"""
        return self.scenarios.get(difficulty, self.scenarios[DifficultyLevel.BEGINNER])
    
    def evaluate_response(self, response: str, difficulty: DifficultyLevel) -> Dict:
        """
        Evaluate learner response using rubrics
        Returns scores and specific feedback
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "difficulty": difficulty.value,
            "scores": {},
            "feedback": [],
            "strengths": [],
            "improvements": [],
            "next_steps": []
        }
        
        # This would integrate with the LLM to analyze the response
        # For now, returning structure for integration
        return evaluation
    
    def get_hint(self, difficulty: DifficultyLevel, hint_number: int) -> Optional[str]:
        """Get progressive hint for current difficulty"""
        hints = self.hints.get(difficulty, [])
        if 0 <= hint_number < len(hints):
            return hints[hint_number]
        return None
    
    def get_scaffolding_level(self, performance_history: List[float]) -> str:
        """Determine appropriate scaffolding based on performance"""
        if not performance_history:
            return "extensive"
        
        avg_performance = sum(performance_history) / len(performance_history)
        if avg_performance >= 4.0:
            return "minimal"
        elif avg_performance >= 3.0:
            return "moderate"
        else:
            return "extensive"
    
    def generate_implementation_tracker(self) -> Dict:
        """Generate tracking template for implementation metrics"""
        return {
            "process_metrics": {
                "antibiotic_timeout_compliance": {
                    "description": "% of cases with documented 48-hour timeout",
                    "target": 90,
                    "measurement": "weekly",
                    "data_source": "EMR audit"
                },
                "de_escalation_rate": {
                    "description": "% of cases de-escalated when cultures negative",
                    "target": 80,
                    "measurement": "weekly",
                    "data_source": "Pharmacy database"
                },
                "guideline_adherence": {
                    "description": "% following cardiac-specific antibiotic guidelines",
                    "target": 85,
                    "measurement": "monthly",
                    "data_source": "Chart review"
                }
            },
            "outcome_metrics": {
                "dot_per_1000_days": {
                    "description": "Days of therapy per 1000 patient days",
                    "baseline": 850,
                    "target": 600,
                    "measurement": "monthly",
                    "data_source": "Pharmacy database"
                },
                "sepsis_rate": {
                    "description": "Late-onset sepsis rate",
                    "baseline": 2.1,
                    "target": "<= 2.1",
                    "measurement": "monthly",
                    "data_source": "Infection control"
                },
                "cost_savings": {
                    "description": "Monthly medication cost savings",
                    "target": 30000,
                    "measurement": "monthly",
                    "data_source": "Finance"
                }
            },
            "balancing_metrics": {
                "mortality": {
                    "description": "CICU mortality rate",
                    "monitoring": "No increase from baseline",
                    "measurement": "monthly"
                },
                "readmission": {
                    "description": "7-day readmission for infection",
                    "monitoring": "No increase from baseline",
                    "measurement": "monthly"
                },
                "staff_satisfaction": {
                    "description": "Provider satisfaction with protocol",
                    "target": "> 70% satisfied",
                    "measurement": "quarterly"
                }
            }
        }
    
    def generate_countermeasure_template(self, barrier_type: str) -> Dict:
        """Generate countermeasure strategies for common barriers"""
        countermeasures = {
            "provider_resistance": {
                "barrier": "Attending physicians resistant to change",
                "strategies": [
                    "Academic detailing with peer-reviewed evidence",
                    "Provider-specific feedback with peer comparison",
                    "Identify and elevate early adopters as champions",
                    "Frame as quality improvement, not criticism",
                    "Share success stories from similar institutions"
                ],
                "timeline": "2-4 weeks per resistant provider",
                "success_metric": "Provider antibiotic prescribing patterns"
            },
            "fear_of_adverse_outcomes": {
                "barrier": "Fear of missing infection after de-escalation",
                "strategies": [
                    "Share data on safety from published studies",
                    "Implement robust monitoring protocol post-de-escalation",
                    "Create clear re-escalation criteria",
                    "Regular case reviews of successful de-escalations",
                    "Morbidity & mortality conference for any adverse events"
                ],
                "timeline": "Ongoing with monthly reviews",
                "success_metric": "De-escalation rate without increase in sepsis"
            },
            "workflow_disruption": {
                "barrier": "Process disrupts established workflows",
                "strategies": [
                    "Map current workflow and identify minimal change points",
                    "Pilot with willing teams first",
                    "Automate reminders and documentation",
                    "Integrate into existing rounds structure",
                    "Provide real-time support during initial weeks"
                ],
                "timeline": "4-week pilot, then phased rollout",
                "success_metric": "Protocol adherence and time to decision"
            },
            "communication_gaps": {
                "barrier": "Unclear roles in antibiotic decisions",
                "strategies": [
                    "Create RACI matrix for antibiotic decisions",
                    "Standardize handoff communication about antibiotics",
                    "Implement antibiotic timeout huddles",
                    "Document decision rationale in standard location",
                    "Train all team members on communication protocol"
                ],
                "timeline": "2-week training, then implementation",
                "success_metric": "Communication audit scores"
            }
        }
        
        return countermeasures.get(barrier_type, {
            "barrier": "Unknown barrier",
            "strategies": ["Conduct root cause analysis", "Engage stakeholders"],
            "timeline": "TBD",
            "success_metric": "TBD"
        })
    
    def export_module_content(self) -> str:
        """Export full module content as JSON"""
        module_data = {
            "module_id": self.module_id,
            "title": self.module_title,
            "clinical_problem": self.clinical_problem,
            "learning_objectives": self.learning_objectives,
            "scenarios": {
                level.value: scenario 
                for level, scenario in self.scenarios.items()
            },
            "rubrics": self.rubrics,
            "hints": {
                level.value: hints 
                for level, hints in self.hints.items()
            },
            "scaffolding": self.scaffolding,
            "implementation_tracker": self.generate_implementation_tracker(),
            "countermeasure_templates": {
                barrier: self.generate_countermeasure_template(barrier)
                for barrier in ["provider_resistance", "fear_of_adverse_outcomes", 
                               "workflow_disruption", "communication_gaps"]
            }
        }
        
        return json.dumps(module_data, indent=2)


# Integration with main system
def integrate_with_asp_system():
    """
    Integration code for the unified ASP education system
    """
    module = CICUAntibioticsModule()
    
    # This would connect to the existing system components
    integration_config = {
        "module_id": module.module_id,
        "routes": {
            "/api/modules/cicu-antibiotics/scenario": "get_scenario",
            "/api/modules/cicu-antibiotics/evaluate": "evaluate_response",
            "/api/modules/cicu-antibiotics/hint": "get_hint",
            "/api/modules/cicu-antibiotics/scaffold": "get_scaffolding_level",
            "/api/modules/cicu-antibiotics/metrics": "generate_implementation_tracker",
            "/api/modules/cicu-antibiotics/countermeasures": "generate_countermeasure_template"
        },
        "database_tables": [
            "cicu_module_progress",
            "cicu_response_history",
            "cicu_implementation_metrics"
        ],
        "integration_points": [
            "conversation_manager.py",
            "adaptive_engine.py",
            "rubric_scorer.py",
            "equity_analytics.py"
        ]
    }
    
    return integration_config


if __name__ == "__main__":
    # Test module creation and export
    module = CICUAntibioticsModule()
    
    # Test getting scenarios
    print("Testing CICU Module...")
    print("\nBeginner Scenario:")
    print(json.dumps(module.get_scenario(DifficultyLevel.BEGINNER), indent=2))
    
    # Test hint system
    print("\nFirst Hint for Intermediate Level:")
    print(module.get_hint(DifficultyLevel.INTERMEDIATE, 0))
    
    # Test metric tracker generation
    print("\nImplementation Metrics Template:")
    print(json.dumps(module.generate_implementation_tracker(), indent=2))
    
    # Export full module
    with open("/home/david/projects/asp_ai_agent/modules/cicu_module_export.json", "w") as f:
        f.write(module.export_module_content())
    
    print("\nModule exported successfully to cicu_module_export.json")