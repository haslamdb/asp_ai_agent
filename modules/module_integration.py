"""
Module Integration for ASP Educational System
Connects the CICU module with existing system components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cicu_prolonged_antibiotics_module import CICUAntibioticsModule, DifficultyLevel
from conversation_manager import ConversationManager
from adaptive_engine import AdaptiveLearningEngine
from rubric_scorer import RubricScorer
from session_manager import SessionManager
from typing import Dict, List, Optional
import json

class ModuleIntegration:
    """
    Integrates the CICU module with the ASP education system
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.cicu_module = CICUAntibioticsModule()
        self.conversation_manager = ConversationManager()
        self.adaptive_engine = AdaptiveLearningEngine()
        self.rubric_scorer = RubricScorer()
        
    def process_module_interaction(self, user_id: str, message: str, module_id: str = "cicu_prolonged_antibiotics") -> Dict:
        """
        Process user interaction with the CICU module
        """
        # Get user session and progress
        session = self.session_manager.get_session(user_id)
        if not session:
            return {"error": "No active session found"}
        
        # Get current difficulty level from adaptive engine
        user_mastery = self.adaptive_engine.get_user_mastery(user_id, module_id)
        difficulty_map = {
            "Remembering": DifficultyLevel.BEGINNER,
            "Understanding": DifficultyLevel.BEGINNER,
            "Applying": DifficultyLevel.INTERMEDIATE,
            "Analyzing": DifficultyLevel.ADVANCED,
            "Evaluating": DifficultyLevel.EXPERT,
            "Creating": DifficultyLevel.EXPERT
        }
        difficulty = difficulty_map.get(user_mastery['mastery_level'], DifficultyLevel.BEGINNER)
        
        # Get appropriate scenario
        scenario = self.cicu_module.get_scenario(difficulty)
        
        # Process conversation with context
        conversation_state = self.conversation_manager.process_turn(
            user_id=user_id,
            user_message=message,
            module_context={
                "module_id": module_id,
                "scenario": scenario,
                "difficulty": difficulty.value
            }
        )
        
        # Evaluate response using module rubrics
        if conversation_state['state'] == 'assessment':
            evaluation = self.evaluate_with_rubrics(message, difficulty)
            
            # Update adaptive engine with performance
            self.adaptive_engine.update_performance(
                user_id=user_id,
                module_id=module_id,
                performance_data={
                    'accuracy': evaluation['overall_score'] / 5.0,
                    'time_taken': 300,  # Would be actual time in production
                    'hints_used': conversation_state.get('hints_used', 0),
                    'attempts': conversation_state.get('attempts', 1)
                }
            )
            
            # Get next recommendation
            next_step = self.adaptive_engine.get_recommendation(user_id, module_id)
            
            return {
                "response": conversation_state['response'],
                "evaluation": evaluation,
                "next_recommendation": next_step,
                "progress": user_mastery
            }
        
        # Provide hints if requested
        if "hint" in message.lower() or conversation_state.get('provide_hint'):
            hint_number = session.get('hint_count', 0)
            hint = self.cicu_module.get_hint(difficulty, hint_number)
            self.session_manager.update_session(user_id, {'hint_count': hint_number + 1})
            
            return {
                "response": conversation_state['response'],
                "hint": hint,
                "scenario": scenario
            }
        
        return {
            "response": conversation_state['response'],
            "scenario": scenario,
            "state": conversation_state['state']
        }
    
    def evaluate_with_rubrics(self, response: str, difficulty: DifficultyLevel) -> Dict:
        """
        Evaluate response using CICU module rubrics
        """
        # Map difficulty to expected competencies
        competency_map = {
            DifficultyLevel.BEGINNER: ["data_analysis", "communication", "problem_identification"],
            DifficultyLevel.INTERMEDIATE: ["behavioral_science", "change_management", "protocol_development"],
            DifficultyLevel.ADVANCED: ["adaptive_leadership", "quality_improvement", "conflict_resolution"],
            DifficultyLevel.EXPERT: ["systems_thinking", "strategic_planning", "sustainability", "dissemination"]
        }
        
        expected_competencies = competency_map[difficulty]
        rubrics = self.cicu_module.rubrics
        
        # Evaluate each competency
        scores = {}
        feedback = []
        
        for competency in expected_competencies:
            if competency in ["data_analysis", "behavioral_intervention", "implementation_science", "clinical_decision_making"]:
                rubric = rubrics.get(competency, rubrics["data_analysis"])
                # This would use LLM to evaluate against rubric criteria
                # For now, placeholder scoring
                score = self._evaluate_competency(response, rubric)
                scores[competency] = score
                feedback.append(f"{competency}: {score}/5")
        
        overall_score = sum(scores.values()) / len(scores) if scores else 0
        
        return {
            "scores": scores,
            "overall_score": overall_score,
            "feedback": feedback,
            "strengths": self._identify_strengths(scores),
            "improvements": self._identify_improvements(scores)
        }
    
    def _evaluate_competency(self, response: str, rubric: Dict) -> int:
        """
        Evaluate a single competency against rubric
        This would integrate with LLM in production
        """
        # Placeholder - would use LLM to match response to rubric criteria
        return 3  # Default to "developing" level
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Identify areas of strength"""
        return [comp for comp, score in scores.items() if score >= 4]
    
    def _identify_improvements(self, scores: Dict) -> List[str]:
        """Identify areas needing improvement"""
        return [comp for comp, score in scores.items() if score < 3]
    
    def get_implementation_tracker(self, user_id: str) -> Dict:
        """
        Get personalized implementation tracking template
        """
        tracker = self.cicu_module.generate_implementation_tracker()
        
        # Personalize based on user progress
        session = self.session_manager.get_session(user_id)
        if session and session.get('implementation_phase'):
            phase = session['implementation_phase']
            if phase == 'planning':
                tracker['current_focus'] = 'process_metrics'
            elif phase == 'active':
                tracker['current_focus'] = 'outcome_metrics'
            elif phase == 'sustaining':
                tracker['current_focus'] = 'balancing_metrics'
        
        return tracker
    
    def get_countermeasure_recommendation(self, barrier_description: str) -> Dict:
        """
        Get recommended countermeasures for identified barriers
        """
        # Map barrier description to type
        barrier_keywords = {
            "resistant": "provider_resistance",
            "fear": "fear_of_adverse_outcomes",
            "workflow": "workflow_disruption",
            "communication": "communication_gaps",
            "unclear": "communication_gaps",
            "attending": "provider_resistance"
        }
        
        barrier_type = None
        for keyword, btype in barrier_keywords.items():
            if keyword in barrier_description.lower():
                barrier_type = btype
                break
        
        if not barrier_type:
            barrier_type = "provider_resistance"  # Default
        
        return self.cicu_module.generate_countermeasure_template(barrier_type)


# API endpoints for integration
def create_module_endpoints(app, session_manager):
    """
    Create Flask endpoints for module integration
    """
    integration = ModuleIntegration(session_manager)
    
    @app.route('/api/modules/cicu/interact', methods=['POST'])
    def interact_with_cicu_module():
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        
        result = integration.process_module_interaction(user_id, message)
        return jsonify(result)
    
    @app.route('/api/modules/cicu/tracker', methods=['GET'])
    def get_cicu_tracker():
        user_id = request.args.get('user_id')
        tracker = integration.get_implementation_tracker(user_id)
        return jsonify(tracker)
    
    @app.route('/api/modules/cicu/countermeasure', methods=['POST'])
    def get_countermeasure():
        data = request.get_json()
        barrier = data.get('barrier')
        
        recommendation = integration.get_countermeasure_recommendation(barrier)
        return jsonify(recommendation)
    
    return app


if __name__ == "__main__":
    # Test integration
    from session_manager import SessionManager
    
    print("Testing Module Integration...")
    
    # Initialize components
    session_manager = SessionManager()
    integration = ModuleIntegration(session_manager)
    
    # Create test user session
    session = session_manager.create_session(
        email="test.fellow@testmed.edu",
        name="Dr. Test Fellow",
        institution="Test Medical Center",
        fellowship_year=2
    )
    user_id = session.user_id
    
    # Test interaction
    print("\nTesting module interaction...")
    response = integration.process_module_interaction(
        user_id=user_id,
        message="I want to analyze the CICU antibiotic data. The DOT seems very high at 850 per 1000 days."
    )
    print(json.dumps(response, indent=2))
    
    # Test tracker
    print("\nTesting implementation tracker...")
    tracker = integration.get_implementation_tracker(user_id)
    print(json.dumps(list(tracker.keys()), indent=2))
    
    # Test countermeasure
    print("\nTesting countermeasure recommendation...")
    countermeasure = integration.get_countermeasure_recommendation(
        "The attending physicians are very resistant to changing their practice"
    )
    print(json.dumps(countermeasure, indent=2))
    
    print("\nIntegration test complete!")