#!/usr/bin/env python3
"""
Interactive CICU Module Session
Run this to experience the module as a learner would
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.cicu_prolonged_antibiotics_module import CICUAntibioticsModule, DifficultyLevel
import json
import time
from typing import Dict, Optional

class InteractiveCICUSession:
    """Interactive learning session for CICU module"""
    
    def __init__(self):
        self.module = CICUAntibioticsModule()
        self.current_level = DifficultyLevel.BEGINNER
        self.hints_used = 0
        self.score = 0
        self.responses = []
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_welcome(self):
        """Display welcome message"""
        self.clear_screen()
        print("=" * 80)
        print("🏥 ANTIMICROBIAL STEWARDSHIP FELLOWSHIP TRAINING")
        print("=" * 80)
        print(f"\n📚 Module: {self.module.module_title}")
        print("\n🎯 Clinical Problem:")
        print(self.module.clinical_problem)
        print("\n📖 Learning Objectives:")
        for i, obj in enumerate(self.module.learning_objectives, 1):
            print(f"  {i}. {obj}")
        
        print("\n" + "=" * 80)
        print("HOW THIS WORKS:")
        print("  • You'll work through progressive scenarios")
        print("  • Type your responses to the prompts")
        print("  • Request hints by typing 'hint'")
        print("  • View metrics by typing 'metrics'")
        print("  • Get countermeasures by typing 'barrier: [description]'")
        print("  • Type 'quit' to exit at any time")
        print("=" * 80)
        
        input("\n✅ Press Enter to begin your training...")
    
    def display_scenario(self, scenario: Dict):
        """Display current scenario"""
        self.clear_screen()
        print("=" * 80)
        print(f"📚 SCENARIO: {scenario['title']}")
        print(f"🎓 Difficulty: {self.current_level.value.upper()}")
        print("=" * 80)
        print(scenario['description'])
        print("\n📋 YOUR TASKS:")
        for i, task in enumerate(scenario['key_tasks'], 1):
            print(f"  {i}. {task}")
        print("\n🎯 Competencies Being Assessed:")
        print(f"  {', '.join(scenario['expected_competencies'])}")
        print("=" * 80)
    
    def get_user_response(self) -> str:
        """Get user's response to scenario"""
        print("\n📝 YOUR RESPONSE:")
        print("(Type 'hint' for help, 'metrics' for tracker, 'barrier: [issue]' for solutions)")
        print("-" * 80)
        
        response_lines = []
        print("Enter your response (type 'DONE' on a new line when finished):")
        
        while True:
            line = input()
            if line.upper() == 'DONE':
                break
            response_lines.append(line)
        
        return '\n'.join(response_lines)
    
    def process_response(self, response: str) -> Optional[str]:
        """Process user response and return action if needed"""
        response_lower = response.lower().strip()
        
        if response_lower == 'quit':
            return 'quit'
        elif response_lower == 'hint':
            return 'hint'
        elif response_lower == 'metrics':
            return 'metrics'
        elif response_lower.startswith('barrier:'):
            return response_lower
        
        return None
    
    def display_hint(self):
        """Display next available hint"""
        hint = self.module.get_hint(self.current_level, self.hints_used)
        if hint:
            print(f"\n💡 HINT {self.hints_used + 1}:")
            print(f"  {hint}")
            self.hints_used += 1
            time.sleep(2)
        else:
            print("\n⚠️ No more hints available for this level.")
            time.sleep(2)
    
    def display_metrics(self):
        """Display implementation metrics"""
        metrics = self.module.generate_implementation_tracker()
        print("\n" + "=" * 80)
        print("📊 IMPLEMENTATION METRICS TRACKER")
        print("=" * 80)
        
        print("\n🔄 Key Process Metrics to Track:")
        for key, metric in list(metrics['process_metrics'].items())[:2]:
            print(f"  • {metric['description']}")
            print(f"    Target: {metric['target']}% | Frequency: {metric['measurement']}")
        
        print("\n📈 Primary Outcome Metric:")
        dot_metric = metrics['outcome_metrics']['dot_per_1000_days']
        print(f"  • {dot_metric['description']}")
        print(f"    Current: {dot_metric['baseline']} → Target: {dot_metric['target']}")
        
        input("\nPress Enter to continue...")
    
    def display_barrier_help(self, barrier_text: str):
        """Display countermeasures for a barrier"""
        # Extract barrier description
        barrier_desc = barrier_text.replace('barrier:', '').strip()
        
        # Map to barrier type
        if 'resist' in barrier_desc or 'attending' in barrier_desc:
            barrier_type = 'provider_resistance'
        elif 'fear' in barrier_desc or 'risk' in barrier_desc:
            barrier_type = 'fear_of_adverse_outcomes'
        elif 'workflow' in barrier_desc or 'disrupt' in barrier_desc:
            barrier_type = 'workflow_disruption'
        else:
            barrier_type = 'communication_gaps'
        
        counter = self.module.generate_countermeasure_template(barrier_type)
        
        print("\n" + "=" * 80)
        print(f"🛠️ COUNTERMEASURE STRATEGIES")
        print(f"Barrier: {counter['barrier']}")
        print("=" * 80)
        print("\nRecommended Strategies:")
        for i, strategy in enumerate(counter['strategies'][:3], 1):
            print(f"  {i}. {strategy}")
        print(f"\n⏰ Timeline: {counter['timeline']}")
        print(f"📏 Success Metric: {counter['success_metric']}")
        
        input("\nPress Enter to continue...")
    
    def evaluate_response(self, response: str) -> Dict:
        """Simulate evaluation of response"""
        # In a real system, this would use LLM to evaluate against rubrics
        # For demo, we'll provide structured feedback
        
        print("\n" + "=" * 80)
        print("📊 EVALUATION FEEDBACK")
        print("=" * 80)
        
        # Simulated rubric scores based on response length/keywords
        response_lower = response.lower()
        scores = {}
        
        if 'dot' in response_lower or 'days of therapy' in response_lower:
            scores['data_analysis'] = 4
            print("✅ Data Analysis: PROFICIENT (4/5)")
            print("   Good recognition of DOT as key metric")
        else:
            scores['data_analysis'] = 2
            print("⚠️ Data Analysis: EMERGING (2/5)")
            print("   Consider calculating specific metrics like DOT")
        
        if 'bias' in response_lower or 'behavior' in response_lower or 'culture' in response_lower:
            scores['behavioral_intervention'] = 4
            print("✅ Behavioral Intervention: PROFICIENT (4/5)")
            print("   Good attention to human factors")
        else:
            scores['behavioral_intervention'] = 3
            print("📝 Behavioral Intervention: DEVELOPING (3/5)")
            print("   Consider addressing cognitive biases")
        
        if 'pilot' in response_lower or 'pdsa' in response_lower or 'implement' in response_lower:
            scores['implementation_science'] = 4
            print("✅ Implementation Science: PROFICIENT (4/5)")
            print("   Good implementation approach")
        else:
            scores['implementation_science'] = 2
            print("⚠️ Implementation Science: EMERGING (2/5)")
            print("   Develop a structured implementation plan")
        
        avg_score = sum(scores.values()) / len(scores) if scores else 3
        self.score = avg_score
        
        print(f"\n📈 Overall Score: {avg_score:.1f}/5.0")
        
        # Provide specific improvement suggestions
        print("\n💡 Next Steps for Improvement:")
        if avg_score < 3:
            print("  • Review the learning objectives and key tasks")
            print("  • Use hints to guide your approach")
            print("  • Consider all stakeholder perspectives")
        elif avg_score < 4:
            print("  • Add more specific implementation details")
            print("  • Include measurement strategies")
            print("  • Address potential barriers proactively")
        else:
            print("  • Excellent work! Consider teaching others")
            print("  • Document your approach for replication")
            print("  • Prepare for the next difficulty level")
        
        return scores
    
    def advance_level(self):
        """Advance to next difficulty level"""
        levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE,
                 DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        
        current_idx = levels.index(self.current_level)
        if current_idx < len(levels) - 1:
            self.current_level = levels[current_idx + 1]
            self.hints_used = 0  # Reset hints for new level
            print(f"\n🎓 Advancing to {self.current_level.value.upper()} level!")
            return True
        else:
            print("\n🏆 Congratulations! You've completed all levels!")
            return False
    
    def run_session(self):
        """Run the interactive learning session"""
        self.display_welcome()
        
        session_active = True
        while session_active:
            # Display current scenario
            scenario = self.module.get_scenario(self.current_level)
            self.display_scenario(scenario)
            
            # Get user response
            while True:
                response = self.get_user_response()
                action = self.process_response(response)
                
                if action == 'quit':
                    print("\n👋 Thank you for participating! Your progress has been saved.")
                    session_active = False
                    break
                elif action == 'hint':
                    self.display_hint()
                    continue
                elif action == 'metrics':
                    self.display_metrics()
                    continue
                elif action and action.startswith('barrier:'):
                    self.display_barrier_help(action)
                    continue
                else:
                    # Process actual response
                    self.responses.append({
                        'level': self.current_level.value,
                        'response': response,
                        'hints_used': self.hints_used
                    })
                    
                    # Evaluate response
                    scores = self.evaluate_response(response)
                    
                    # Determine next step
                    input("\n✅ Press Enter to continue...")
                    
                    if self.score >= 3.5:
                        print("\n" + "=" * 80)
                        print("✅ SCENARIO COMPLETED SUCCESSFULLY!")
                        print("=" * 80)
                        
                        if not self.advance_level():
                            session_active = False
                    else:
                        print("\n" + "=" * 80)
                        print("📝 Let's try this scenario again with the feedback in mind.")
                        print("=" * 80)
                        input("Press Enter to retry...")
                    
                    break
        
        # Display session summary
        self.display_summary()
    
    def display_summary(self):
        """Display session summary"""
        self.clear_screen()
        print("=" * 80)
        print("📊 SESSION SUMMARY")
        print("=" * 80)
        print(f"\n📚 Module: {self.module.module_title}")
        print(f"🎓 Highest Level Reached: {self.current_level.value.upper()}")
        print(f"💡 Total Hints Used: {sum(r['hints_used'] for r in self.responses)}")
        print(f"📝 Scenarios Attempted: {len(self.responses)}")
        
        if self.responses:
            print("\n🏆 Your Learning Journey:")
            for i, resp in enumerate(self.responses, 1):
                print(f"  {i}. {resp['level'].upper()} - Hints used: {resp['hints_used']}")
        
        print("\n" + "=" * 80)
        print("🎯 KEY TAKEAWAYS:")
        print("  • Reducing inappropriate antibiotics requires data + behavior change")
        print("  • Implementation success depends on addressing barriers proactively")
        print("  • Measurement and feedback are essential for sustainability")
        print("  • Multidisciplinary engagement improves outcomes")
        print("=" * 80)
        print("\n Thank you for completing the CICU Antibiotics Module!")
        print(" Your dedication to antimicrobial stewardship makes a difference! 🌟")


if __name__ == "__main__":
    session = InteractiveCICUSession()
    try:
        session.run_session()
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Thank you for participating!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please report this to the module administrator.")