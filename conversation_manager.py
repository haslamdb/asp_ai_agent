#!/usr/bin/env python3
"""
Multi-Turn Conversation Context Manager for ASP AI Agent
Manages conversation flow, context windows, and pedagogical scaffolding
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import re
from enum import Enum

from session_manager import ConversationTurn, UserSession, DifficultyLevel, ModuleProgress

class ConversationState(Enum):
    """Current state of the conversation"""
    GREETING = "greeting"
    MODULE_SELECTION = "module_selection"
    SCENARIO_INTRODUCTION = "scenario_introduction"
    ACTIVE_COACHING = "active_coaching"
    REFLECTION = "reflection"
    ASSESSMENT = "assessment"
    COMPLETION = "completion"

class ScaffoldingLevel(Enum):
    """Level of support provided"""
    MINIMAL = "minimal"  # Just hints
    MODERATE = "moderate"  # Guided questions
    EXTENSIVE = "extensive"  # Step-by-step walkthrough

@dataclass
class ConversationContext:
    """Context for current conversation"""
    state: ConversationState = ConversationState.GREETING
    current_module: Optional[str] = None
    current_scenario: Optional[Dict] = None
    scaffolding_level: ScaffoldingLevel = ScaffoldingLevel.MODERATE
    attempts_on_current: int = 0
    hints_provided: List[str] = field(default_factory=list)
    key_concepts_covered: List[str] = field(default_factory=list)
    misconceptions_identified: List[str] = field(default_factory=list)
    
class ConversationManager:
    """Manages multi-turn conversations with context and pedagogical scaffolding"""
    
    def __init__(self):
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.module_scenarios = self._load_module_scenarios()
        
    def _load_module_scenarios(self) -> Dict:
        """Load teaching scenarios for each module"""
        return {
            "leadership": {
                "beginner": [
                    {
                        "id": "lead_1_1",
                        "title": "Making the Business Case",
                        "scenario": "Your hospital administrator asks about the ROI of your ASP program. How do you respond?",
                        "learning_objectives": ["ROI calculation", "stakeholder communication", "value demonstration"],
                        "key_concepts": ["cost avoidance", "LOS reduction", "quality metrics"],
                        "success_criteria": ["identifies 3+ value metrics", "uses data appropriately", "clear communication"]
                    }
                ],
                "intermediate": [
                    {
                        "id": "lead_2_1", 
                        "title": "Multi-Stakeholder Engagement",
                        "scenario": "You need buy-in from ICU, surgery, and pharmacy for a new antibiotic timeout protocol. Design your engagement strategy.",
                        "learning_objectives": ["stakeholder mapping", "change management", "protocol implementation"],
                        "key_concepts": ["RACI matrix", "pilot testing", "feedback loops"],
                        "success_criteria": ["identifies all stakeholders", "phased approach", "metrics for success"]
                    }
                ],
                "advanced": [
                    {
                        "id": "lead_3_1",
                        "title": "System-Wide ASP Expansion", 
                        "scenario": "The health system wants to expand ASP to 5 community hospitals with varying resources. Create an implementation plan.",
                        "learning_objectives": ["resource allocation", "standardization vs customization", "remote monitoring"],
                        "key_concepts": ["hub-and-spoke model", "technology enablement", "outcome harmonization"],
                        "success_criteria": ["tiered support model", "clear metrics", "sustainability plan"]
                    }
                ]
            },
            "analytics": {
                "beginner": [
                    {
                        "id": "data_1_1",
                        "title": "DOT Calculation Basics",
                        "scenario": "Calculate DOT/1000 patient days for ceftriaxone in the PICU last month. You have: 45 doses given, average census 12 patients.",
                        "learning_objectives": ["DOT calculation", "metric interpretation", "data validation"],
                        "key_concepts": ["DOT definition", "patient days", "benchmarking"],
                        "success_criteria": ["correct calculation", "identifies limitations", "suggests next steps"]
                    }
                ],
                "intermediate": [
                    {
                        "id": "data_2_1",
                        "title": "Trend Analysis with Confounders",
                        "scenario": "Vancomycin use increased 30% after opening a new cardiac surgery unit. Analyze whether this represents inappropriate use.",
                        "learning_objectives": ["confounding factors", "risk adjustment", "appropriate use assessment"],
                        "key_concepts": ["case-mix adjustment", "indication review", "statistical process control"],
                        "success_criteria": ["identifies confounders", "proposes analysis plan", "actionable recommendations"]
                    }
                ],
                "advanced": [
                    {
                        "id": "data_3_1",
                        "title": "Multi-Site Benchmarking",
                        "scenario": "Compare your ASP metrics with 10 similar children's hospitals. Your DOT is 450 vs median 380. Develop an action plan.",
                        "learning_objectives": ["benchmarking interpretation", "gap analysis", "improvement planning"],
                        "key_concepts": ["risk stratification", "best practice identification", "PDSA cycles"],
                        "success_criteria": ["appropriate comparisons", "root cause analysis", "measurable interventions"]
                    }
                ]
            },
            "behavioral": {
                "beginner": [
                    {
                        "id": "behav_1_1",
                        "title": "Identifying Cognitive Biases",
                        "scenario": "A senior physician always prescribes azithromycin for pneumonia 'because it's always worked.' How do you address this?",
                        "learning_objectives": ["bias recognition", "respectful communication", "evidence presentation"],
                        "key_concepts": ["availability heuristic", "confirmation bias", "motivational interviewing"],
                        "success_criteria": ["identifies bias type", "non-confrontational approach", "data-driven discussion"]
                    }
                ],
                "intermediate": [
                    {
                        "id": "behav_2_1",
                        "title": "Designing Behavior Change Interventions",
                        "scenario": "Prophylactic antibiotic duration exceeds guidelines in 60% of surgical cases. Design a behavior change intervention.",
                        "learning_objectives": ["behavior analysis", "intervention design", "implementation science"],
                        "key_concepts": ["COM-B model", "nudge theory", "audit and feedback"],
                        "success_criteria": ["behavioral diagnosis", "multi-modal intervention", "evaluation plan"]
                    }
                ],
                "advanced": [
                    {
                        "id": "behav_3_1",
                        "title": "Culture Change Initiative",
                        "scenario": "Create a campaign to shift from 'antibiotic request' to 'infection consultation' culture in your ED.",
                        "learning_objectives": ["organizational culture", "systems thinking", "sustained change"],
                        "key_concepts": ["social norms", "opinion leaders", "positive deviance"],
                        "success_criteria": ["stakeholder engagement", "messaging strategy", "sustainability measures"]
                    }
                ]
            },
            "clinical": {
                "beginner": [
                    {
                        "id": "clin_1_1",
                        "title": "Antibiotic Timeout Protocol",
                        "scenario": "Implement a 48-hour antibiotic timeout for empiric therapy in your PICU. Draft the protocol.",
                        "learning_objectives": ["protocol development", "clinical criteria", "workflow integration"],
                        "key_concepts": ["time-out triggers", "exclusion criteria", "documentation"],
                        "success_criteria": ["clear criteria", "safety measures", "actionable steps"]
                    }
                ],
                "intermediate": [
                    {
                        "id": "clin_2_1",
                        "title": "Penicillin Allergy De-labeling",
                        "scenario": "30% of patients have documented penicillin allergies. Create a de-labeling program for low-risk patients.",
                        "learning_objectives": ["risk stratification", "testing protocols", "EHR integration"],
                        "key_concepts": ["allergy history", "skin testing", "oral challenges"],
                        "success_criteria": ["risk assessment tool", "testing pathway", "documentation plan"]
                    }
                ],
                "advanced": [
                    {
                        "id": "clin_3_1",
                        "title": "Drug Shortage Management",
                        "scenario": "Critical piperacillin-tazobactam shortage. Develop substitution protocols maintaining quality and equity.",
                        "learning_objectives": ["therapeutic alternatives", "prioritization", "equity considerations"],
                        "key_concepts": ["therapeutic equivalence", "restriction criteria", "monitoring"],
                        "success_criteria": ["evidence-based alternatives", "fair allocation", "outcome monitoring"]
                    }
                ]
            }
        }
    
    def get_or_create_context(self, user_id: str) -> ConversationContext:
        """Get existing or create new conversation context"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext()
        return self.conversation_contexts[user_id]
    
    def process_turn(self, user_session: UserSession, user_message: str, 
                    module_id: Optional[str] = None) -> Dict:
        """Process a conversation turn and determine response strategy"""
        context = self.get_or_create_context(user_session.user_id)
        
        # Analyze user message intent
        intent = self._analyze_intent(user_message, context)
        
        # Get conversation history for context
        recent_turns = user_session.get_context_window(num_turns=5)
        
        # Determine pedagogical response
        response_strategy = self._determine_response_strategy(
            intent, context, user_session, recent_turns
        )
        
        # Update context based on interaction
        self._update_context(context, intent, response_strategy)
        
        return {
            "context": context,
            "intent": intent,
            "response_strategy": response_strategy,
            "recent_context": self._format_context_for_llm(recent_turns),
            "scaffolding_level": context.scaffolding_level.value,
            "current_scenario": context.current_scenario,
            "hints_available": self._get_available_hints(context),
            "next_steps": self._suggest_next_steps(context, user_session)
        }
    
    def _analyze_intent(self, message: str, context: ConversationContext) -> str:
        """Analyze the intent of the user's message"""
        message_lower = message.lower()
        
        # Check for common intents
        if any(greeting in message_lower for greeting in ["hello", "hi", "start", "begin"]):
            return "greeting"
        elif any(word in message_lower for word in ["help", "hint", "stuck", "don't know"]):
            return "request_help"
        elif any(word in message_lower for word in ["why", "explain", "reasoning"]):
            return "request_explanation"
        elif any(word in message_lower for word in ["next", "continue", "move on"]):
            return "next_scenario"
        elif any(word in message_lower for word in ["module", "topic", "learn about"]):
            return "module_selection"
        elif context.state == ConversationState.ACTIVE_COACHING:
            return "scenario_response"
        else:
            return "general_query"
    
    def _determine_response_strategy(self, intent: str, context: ConversationContext,
                                    user_session: UserSession, recent_turns: List) -> Dict:
        """Determine the pedagogical response strategy"""
        strategy = {
            "type": "standard",
            "tone": "encouraging",
            "scaffolding": context.scaffolding_level.value,
            "include_hints": False,
            "include_example": False,
            "prompt_reflection": False,
            "provide_feedback": True
        }
        
        # Adjust based on intent
        if intent == "request_help":
            strategy["include_hints"] = True
            strategy["type"] = "supportive"
            context.attempts_on_current += 1
            
            # Increase scaffolding if struggling
            if context.attempts_on_current > 2:
                context.scaffolding_level = ScaffoldingLevel.EXTENSIVE
                strategy["include_example"] = True
                
        elif intent == "scenario_response":
            strategy["type"] = "coaching"
            strategy["provide_feedback"] = True
            strategy["prompt_reflection"] = context.attempts_on_current > 0
            
        elif intent == "greeting":
            strategy["type"] = "welcome"
            strategy["tone"] = "friendly"
            
        elif intent == "module_selection":
            strategy["type"] = "menu"
            strategy["provide_feedback"] = False
            
        # Adjust based on performance
        if user_session.learning_velocity < 0.8:
            strategy["scaffolding"] = ScaffoldingLevel.EXTENSIVE.value
            strategy["tone"] = "patient"
        elif user_session.learning_velocity > 1.2:
            strategy["scaffolding"] = ScaffoldingLevel.MINIMAL.value
            strategy["tone"] = "challenging"
            
        return strategy
    
    def _update_context(self, context: ConversationContext, intent: str, 
                       response_strategy: Dict):
        """Update conversation context based on interaction"""
        # State transitions
        if intent == "greeting":
            context.state = ConversationState.MODULE_SELECTION
        elif intent == "module_selection" and context.current_module:
            context.state = ConversationState.SCENARIO_INTRODUCTION
        elif intent == "scenario_response":
            context.state = ConversationState.ACTIVE_COACHING
        elif intent == "next_scenario":
            context.state = ConversationState.SCENARIO_INTRODUCTION
            context.attempts_on_current = 0
            context.hints_provided = []
    
    def _format_context_for_llm(self, recent_turns: List[ConversationTurn]) -> str:
        """Format recent conversation history for LLM context"""
        if not recent_turns:
            return "No previous conversation history."
        
        formatted = "Recent conversation context:\n"
        for turn in recent_turns[-3:]:  # Last 3 turns for context
            formatted += f"\nUser: {turn.user_message[:200]}...\n" if len(turn.user_message) > 200 else f"\nUser: {turn.user_message}\n"
            formatted += f"Assistant: {turn.ai_response[:200]}...\n" if len(turn.ai_response) > 200 else f"Assistant: {turn.ai_response}\n"
        
        return formatted
    
    def _get_available_hints(self, context: ConversationContext) -> List[str]:
        """Get progressive hints for current scenario"""
        if not context.current_scenario:
            return []
        
        hints = []
        if context.attempts_on_current >= 1:
            hints.append("Think about the key stakeholders involved.")
        if context.attempts_on_current >= 2:
            hints.append("Consider what data would be most compelling.")
        if context.attempts_on_current >= 3:
            hints.append("Review the success criteria for this scenario.")
            
        return [h for h in hints if h not in context.hints_provided]
    
    def _suggest_next_steps(self, context: ConversationContext, 
                           user_session: UserSession) -> List[str]:
        """Suggest next learning steps based on progress"""
        suggestions = []
        
        if context.state == ConversationState.MODULE_SELECTION:
            suggestions.append("Choose a module to begin practicing")
            
        elif context.state == ConversationState.COMPLETION:
            # Check which modules haven't been attempted
            unattempted = []
            for module in ["leadership", "analytics", "behavioral", "clinical"]:
                if module not in user_session.module_progress:
                    unattempted.append(module)
            
            if unattempted:
                suggestions.append(f"Try the {unattempted[0]} module next")
            else:
                suggestions.append("Review your performance in completed modules")
                
        elif context.state == ConversationState.ACTIVE_COACHING:
            if context.attempts_on_current > 3:
                suggestions.append("Would you like to try a different scenario?")
            else:
                suggestions.append("Continue working through this scenario")
                
        return suggestions
    
    def get_scenario_for_user(self, user_session: UserSession, 
                             module_id: str) -> Optional[Dict]:
        """Get appropriate scenario based on user's level"""
        difficulty = user_session.current_difficulty.value.lower()
        
        # Map difficulty to scenario level
        if difficulty in ["beginner"]:
            level = "beginner"
        elif difficulty in ["intermediate"]:
            level = "intermediate"
        else:
            level = "advanced"
            
        if module_id in self.module_scenarios:
            scenarios = self.module_scenarios[module_id].get(level, [])
            if scenarios:
                # Get first uncompleted scenario or repeat last
                for scenario in scenarios:
                    scenario_id = scenario["id"]
                    if module_id in user_session.module_progress:
                        progress = user_session.module_progress[module_id]
                        # Check if this scenario was attempted
                        attempted = any(scenario_id in str(fb) for fb in progress.feedback_history)
                        if not attempted:
                            return scenario
                # Return first scenario if all attempted
                return scenarios[0]
        
        return None
    
    def generate_coaching_prompt(self, context: ConversationContext, 
                                response_strategy: Dict) -> str:
        """Generate prompt for LLM to provide coaching response"""
        prompt = f"""You are an expert ASP educator providing coaching on antimicrobial stewardship.

Current scenario: {context.current_scenario.get('scenario', 'No scenario loaded') if context.current_scenario else 'No scenario active'}

Learning objectives: {context.current_scenario.get('learning_objectives', []) if context.current_scenario else []}

Scaffolding level: {response_strategy['scaffolding']}
Response type: {response_strategy['type']}
Tone: {response_strategy['tone']}

Previous attempts on this scenario: {context.attempts_on_current}
Concepts covered so far: {context.key_concepts_covered}
Misconceptions identified: {context.misconceptions_identified}

Instructions:
"""
        
        if response_strategy['type'] == 'coaching':
            prompt += """
- Provide specific, actionable feedback on their response
- Use Socratic questioning to guide deeper thinking
- Acknowledge what they got right before addressing gaps
"""
        
        if response_strategy['include_hints']:
            prompt += f"""
- Provide a helpful hint without giving away the answer
- Focus on: {context.current_scenario.get('key_concepts', [])[0] if context.current_scenario and context.current_scenario.get('key_concepts') else 'core concepts'}
"""
        
        if response_strategy['include_example']:
            prompt += """
- Include a relevant example to illustrate the concept
- Make it concrete and applicable to their scenario
"""
        
        if response_strategy['prompt_reflection']:
            prompt += """
- End with a reflection question to deepen understanding
- Connect to real-world ASP practice
"""
        
        return prompt

# Global conversation manager instance
conversation_manager = ConversationManager()