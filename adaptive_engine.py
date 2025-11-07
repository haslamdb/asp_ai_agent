#!/usr/bin/env python3
"""
Adaptive Learning Engine for ASP AI Agent
Implements mastery-based progression and personalized difficulty adjustment
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
import json

from session_manager import UserSession, DifficultyLevel, ModuleProgress

class MasteryLevel(Enum):
    """Mastery levels based on Bloom's taxonomy"""
    REMEMBERING = 1  # Can recall facts and basic concepts
    UNDERSTANDING = 2  # Can explain ideas or concepts  
    APPLYING = 3  # Can use information in new situations
    ANALYZING = 4  # Can draw connections among ideas
    EVALUATING = 5  # Can justify decisions
    CREATING = 6  # Can produce original work

class PerformanceMetrics:
    """Track performance metrics for adaptation"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.accuracy_scores: List[float] = []
        self.hint_requests: List[int] = []
        self.attempt_counts: List[int] = []
        self.completion_rates: List[float] = []
        
    def add_performance(self, response_time: float, accuracy: float, 
                       hints_used: int, attempts: int):
        """Add a performance data point"""
        self.response_times.append(response_time)
        self.accuracy_scores.append(accuracy)
        self.hint_requests.append(hints_used)
        self.attempt_counts.append(attempts)
        
    def get_trend(self, metric: str, window: int = 5) -> str:
        """Analyze trend in recent performance"""
        if metric == "accuracy":
            data = self.accuracy_scores
        elif metric == "hints":
            data = self.hint_requests
        elif metric == "attempts":
            data = self.attempt_counts
        else:
            return "stable"
            
        if len(data) < 2:
            return "insufficient_data"
            
        recent = data[-window:] if len(data) >= window else data
        if len(recent) < 2:
            return "insufficient_data"
            
        # Calculate trend
        x = np.arange(len(recent))
        coefficients = np.polyfit(x, recent, 1)
        slope = coefficients[0]
        
        if abs(slope) < 0.05:
            return "stable"
        elif slope > 0:
            return "improving" if metric == "accuracy" else "increasing"
        else:
            return "declining" if metric == "accuracy" else "decreasing"

@dataclass
class LearnerProfile:
    """Profile of learner characteristics for personalization"""
    user_id: str
    learning_style: str = "balanced"  # visual, verbal, kinesthetic, balanced
    pace_preference: str = "moderate"  # slow, moderate, fast
    feedback_preference: str = "immediate"  # immediate, delayed, on-demand
    
    # Strengths and weaknesses by competency
    competency_scores: Dict[str, float] = field(default_factory=dict)
    
    # Time patterns
    peak_performance_time: Optional[str] = None  # morning, afternoon, evening
    average_session_duration: float = 0.0
    
    # Engagement metrics
    engagement_level: float = 1.0  # 0-1 scale
    persistence_score: float = 1.0  # How long they stick with difficult problems
    
    def update_from_session(self, session_data: Dict):
        """Update profile based on session data"""
        # Update engagement based on session length and activity
        if "session_duration" in session_data:
            self.average_session_duration = (
                0.7 * self.average_session_duration + 
                0.3 * session_data["session_duration"]
            )
        
        if "completion_rate" in session_data:
            self.engagement_level = (
                0.8 * self.engagement_level + 
                0.2 * session_data["completion_rate"]
            )

class AdaptiveLearningEngine:
    """Engine for adaptive difficulty and personalized learning paths"""
    
    def __init__(self):
        self.learner_profiles: Dict[str, LearnerProfile] = {}
        self.performance_history: Dict[str, PerformanceMetrics] = {}
        self.mastery_thresholds = {
            MasteryLevel.REMEMBERING: 0.6,
            MasteryLevel.UNDERSTANDING: 0.7,
            MasteryLevel.APPLYING: 0.75,
            MasteryLevel.ANALYZING: 0.8,
            MasteryLevel.EVALUATING: 0.85,
            MasteryLevel.CREATING: 0.9
        }
        
    def get_or_create_profile(self, user_id: str) -> LearnerProfile:
        """Get or create learner profile"""
        if user_id not in self.learner_profiles:
            self.learner_profiles[user_id] = LearnerProfile(user_id=user_id)
            self.performance_history[user_id] = PerformanceMetrics()
        return self.learner_profiles[user_id]
    
    def assess_mastery_level(self, user_session: UserSession, module_id: str) -> MasteryLevel:
        """Assess current mastery level for a module"""
        if module_id not in user_session.module_progress:
            return MasteryLevel.REMEMBERING
            
        progress = user_session.module_progress[module_id]
        score = progress.mastery_level
        
        # Determine mastery based on score and consistency
        for level in reversed(list(MasteryLevel)):
            if score >= self.mastery_thresholds[level]:
                # Check consistency (need 3+ attempts at this level)
                recent_scores = [
                    fb['score'] for fb in progress.feedback_history[-3:]
                    if 'score' in fb
                ]
                if len(recent_scores) >= 2:
                    avg_recent = np.mean(recent_scores)
                    if avg_recent >= self.mastery_thresholds[level]:
                        return level
                        
        return MasteryLevel.REMEMBERING
    
    def calculate_difficulty_adjustment(self, user_session: UserSession,
                                      recent_performance: Dict) -> Tuple[DifficultyLevel, str]:
        """Calculate difficulty adjustment based on performance"""
        user_id = user_session.user_id
        profile = self.get_or_create_profile(user_id)
        metrics = self.performance_history[user_id]
        
        # Add recent performance
        metrics.add_performance(
            response_time=recent_performance.get('response_time', 0),
            accuracy=recent_performance.get('accuracy', 0),
            hints_used=recent_performance.get('hints_used', 0),
            attempts=recent_performance.get('attempts', 1)
        )
        
        # Analyze trends
        accuracy_trend = metrics.get_trend("accuracy")
        hint_trend = metrics.get_trend("hints")
        
        current_difficulty = user_session.current_difficulty
        recommendation = current_difficulty
        reasoning = ""
        
        # Decision logic for difficulty adjustment
        recent_accuracy = metrics.accuracy_scores[-1] if metrics.accuracy_scores else 0
        avg_recent_accuracy = np.mean(metrics.accuracy_scores[-3:]) if len(metrics.accuracy_scores) >= 3 else recent_accuracy
        
        if avg_recent_accuracy >= 0.85 and accuracy_trend in ["stable", "improving"]:
            # Performance is high and stable/improving - increase difficulty
            if current_difficulty != DifficultyLevel.EXPERT:
                levels = list(DifficultyLevel)
                current_idx = levels.index(current_difficulty)
                recommendation = levels[min(current_idx + 1, len(levels) - 1)]
                reasoning = "Consistent high performance warrants increased challenge"
                
        elif avg_recent_accuracy < 0.5 or (accuracy_trend == "declining" and hint_trend == "increasing"):
            # Struggling - decrease difficulty
            if current_difficulty != DifficultyLevel.BEGINNER:
                levels = list(DifficultyLevel)
                current_idx = levels.index(current_difficulty)
                recommendation = levels[max(current_idx - 1, 0)]
                reasoning = "Reducing difficulty to build confidence and understanding"
                
        elif 0.5 <= avg_recent_accuracy < 0.7:
            # In learning zone - maintain with more support
            reasoning = "Performance in optimal learning zone - maintaining difficulty with increased scaffolding"
            
        else:
            # Stable performance - maintain
            reasoning = "Performance stable at current level"
            
        return recommendation, reasoning
    
    def generate_personalized_path(self, user_session: UserSession) -> List[Dict]:
        """Generate personalized learning path based on profile and progress"""
        profile = self.get_or_create_profile(user_session.user_id)
        
        # Identify gaps and strengths
        module_scores = {}
        for module_id, progress in user_session.module_progress.items():
            module_scores[module_id] = progress.mastery_level
            
        # Modules to focus on (lowest scores or not attempted)
        all_modules = ["leadership", "analytics", "behavioral", "clinical"]
        recommendations = []
        
        # First, modules not attempted
        for module in all_modules:
            if module not in module_scores:
                recommendations.append({
                    "module": module,
                    "priority": "high",
                    "reason": "Not yet attempted",
                    "suggested_time": self._estimate_time(module, user_session.current_difficulty),
                    "prerequisites": []
                })
                
        # Then, modules needing improvement
        for module, score in sorted(module_scores.items(), key=lambda x: x[1]):
            if score < 0.7:
                mastery = self.assess_mastery_level(user_session, module)
                recommendations.append({
                    "module": module,
                    "priority": "medium" if score >= 0.5 else "high",
                    "reason": f"Current mastery: {mastery.name.lower()}",
                    "suggested_time": self._estimate_time(module, user_session.current_difficulty),
                    "focus_areas": self._identify_focus_areas(user_session, module)
                })
                
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations[:3]  # Top 3 recommendations
    
    def adapt_scenario_complexity(self, base_scenario: Dict, 
                                 user_session: UserSession) -> Dict:
        """Adapt scenario complexity based on learner level"""
        adapted = base_scenario.copy()
        profile = self.get_or_create_profile(user_session.user_id)
        
        # Adjust based on difficulty level
        if user_session.current_difficulty == DifficultyLevel.BEGINNER:
            adapted["scaffolding"] = "high"
            adapted["hints_available"] = 3
            adapted["partial_credit"] = True
            adapted["complexity_factors"] = 1  # Single factor to consider
            
        elif user_session.current_difficulty == DifficultyLevel.INTERMEDIATE:
            adapted["scaffolding"] = "moderate"
            adapted["hints_available"] = 2
            adapted["partial_credit"] = True
            adapted["complexity_factors"] = 2  # Multiple factors
            
        elif user_session.current_difficulty == DifficultyLevel.ADVANCED:
            adapted["scaffolding"] = "minimal"
            adapted["hints_available"] = 1
            adapted["partial_credit"] = False
            adapted["complexity_factors"] = 3  # Multiple interacting factors
            
        else:  # EXPERT
            adapted["scaffolding"] = "none"
            adapted["hints_available"] = 0
            adapted["partial_credit"] = False
            adapted["complexity_factors"] = 4  # System-level thinking required
            adapted["time_pressure"] = True
            
        # Adjust based on learning style
        if profile.learning_style == "visual":
            adapted["include_visuals"] = True
            adapted["data_presentation"] = "graphical"
        elif profile.learning_style == "verbal":
            adapted["include_examples"] = True
            adapted["explanation_style"] = "detailed"
            
        # Adjust pacing
        if profile.pace_preference == "slow":
            adapted["allow_review"] = True
            adapted["step_by_step"] = True
        elif profile.pace_preference == "fast":
            adapted["combined_steps"] = True
            adapted["skip_basics"] = True
            
        return adapted
    
    def predict_time_to_mastery(self, user_session: UserSession, 
                               module_id: str, target_level: MasteryLevel) -> Dict:
        """Predict time to reach target mastery level"""
        current_mastery = self.assess_mastery_level(user_session, module_id)
        profile = self.get_or_create_profile(user_session.user_id)
        
        if current_mastery.value >= target_level.value:
            return {
                "already_achieved": True,
                "current_level": current_mastery.name,
                "target_level": target_level.name
            }
            
        # Estimate based on learning velocity and gap
        level_gap = target_level.value - current_mastery.value
        base_hours_per_level = 2.5  # Base estimate
        
        # Adjust based on individual learning velocity
        adjusted_hours = base_hours_per_level * level_gap / user_session.learning_velocity
        
        # Adjust based on engagement
        adjusted_hours *= (2 - profile.engagement_level)  # Lower engagement = more time
        
        # Calculate sessions needed
        avg_session = profile.average_session_duration if profile.average_session_duration > 0 else 30
        sessions_needed = int(np.ceil((adjusted_hours * 60) / avg_session))
        
        return {
            "already_achieved": False,
            "current_level": current_mastery.name,
            "target_level": target_level.name,
            "estimated_hours": round(adjusted_hours, 1),
            "estimated_sessions": sessions_needed,
            "confidence": self._calculate_prediction_confidence(user_session, module_id)
        }
    
    def _estimate_time(self, module: str, difficulty: DifficultyLevel) -> int:
        """Estimate time to complete module at given difficulty (minutes)"""
        base_times = {
            "leadership": 45,
            "analytics": 40,
            "behavioral": 35,
            "clinical": 50
        }
        
        difficulty_multipliers = {
            DifficultyLevel.BEGINNER: 0.8,
            DifficultyLevel.INTERMEDIATE: 1.0,
            DifficultyLevel.ADVANCED: 1.3,
            DifficultyLevel.EXPERT: 1.5
        }
        
        base = base_times.get(module, 40)
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        
        return int(base * multiplier)
    
    def _identify_focus_areas(self, user_session: UserSession, module: str) -> List[str]:
        """Identify specific areas to focus on within a module"""
        if module not in user_session.module_progress:
            return ["Introduction to key concepts"]
            
        progress = user_session.module_progress[module]
        focus_areas = []
        
        # Analyze feedback history for patterns
        if progress.feedback_history:
            recent_feedback = progress.feedback_history[-3:]
            
            # Look for recurring issues
            common_issues = {}
            for feedback in recent_feedback:
                if isinstance(feedback.get('feedback'), dict):
                    issues = feedback['feedback'].get('improvement_areas', [])
                    for issue in issues:
                        common_issues[issue] = common_issues.get(issue, 0) + 1
                        
            # Focus on most common issues
            sorted_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)
            focus_areas = [issue for issue, _ in sorted_issues[:3]]
            
        if not focus_areas:
            # Default focus areas by module
            defaults = {
                "leadership": ["Stakeholder engagement", "ROI communication", "Change management"],
                "analytics": ["Metric calculation", "Trend interpretation", "Benchmarking"],
                "behavioral": ["Bias identification", "Intervention design", "Communication strategies"],
                "clinical": ["Protocol development", "Safety considerations", "Implementation planning"]
            }
            focus_areas = defaults.get(module, ["Core concepts"])[:2]
            
        return focus_areas
    
    def _calculate_prediction_confidence(self, user_session: UserSession, module: str) -> str:
        """Calculate confidence in time prediction"""
        if module not in user_session.module_progress:
            return "low"  # No data
            
        progress = user_session.module_progress[module]
        
        # More attempts = higher confidence
        if progress.attempts < 3:
            return "low"
        elif progress.attempts < 7:
            return "medium"
        else:
            return "high"
    
    def generate_performance_report(self, user_session: UserSession) -> Dict:
        """Generate comprehensive performance report"""
        profile = self.get_or_create_profile(user_session.user_id)
        metrics = self.performance_history.get(user_session.user_id)
        
        report = {
            "user_id": user_session.user_id,
            "current_level": user_session.current_difficulty.value,
            "learning_velocity": round(user_session.learning_velocity, 2),
            "modules": {},
            "strengths": [],
            "areas_for_improvement": [],
            "recommendations": []
        }
        
        # Analyze each module
        for module_id, progress in user_session.module_progress.items():
            mastery = self.assess_mastery_level(user_session, module_id)
            report["modules"][module_id] = {
                "mastery_level": mastery.name,
                "mastery_score": round(progress.mastery_level, 2),
                "attempts": progress.attempts,
                "best_score": round(progress.best_score, 2),
                "time_spent_hours": round(progress.time_spent_seconds / 3600, 1),
                "status": progress.status.value
            }
            
            if progress.mastery_level >= 0.8:
                report["strengths"].append(f"{module_id.title()} competency")
            elif progress.mastery_level < 0.6:
                report["areas_for_improvement"].append(f"{module_id.title()} skills")
                
        # Performance trends
        if metrics and len(metrics.accuracy_scores) >= 5:
            report["trends"] = {
                "accuracy": metrics.get_trend("accuracy"),
                "hint_usage": metrics.get_trend("hints"),
                "attempts": metrics.get_trend("attempts")
            }
            
        # Personalized recommendations
        learning_path = self.generate_personalized_path(user_session)
        report["recommendations"] = learning_path
        
        # Engagement metrics
        report["engagement"] = {
            "level": round(profile.engagement_level, 2),
            "persistence": round(profile.persistence_score, 2),
            "average_session_minutes": round(profile.average_session_duration, 1),
            "learning_style": profile.learning_style,
            "pace_preference": profile.pace_preference
        }
        
        return report

# Global adaptive engine instance
adaptive_engine = AdaptiveLearningEngine()