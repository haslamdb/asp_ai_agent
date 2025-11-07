#!/usr/bin/env python3
"""
Integration test for enhanced ASP AI Agent modules
Tests session management, conversation context, adaptive learning, rubric scoring, and equity analytics
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules
from session_manager import SessionManager, UserSession, ConversationTurn, ModuleProgress, DifficultyLevel
from conversation_manager import ConversationManager, ConversationState
from adaptive_engine import AdaptiveLearningEngine, MasteryLevel
from rubric_scorer import RubricScorer, CriterionLevel
from equity_analytics import EquityAnalytics

def test_session_management():
    """Test session management functionality"""
    print("\n=== Testing Session Management ===")
    
    # Initialize manager
    mgr = SessionManager()
    
    # Create a new session
    session = mgr.create_session(
        email="test@example.com",
        name="Test Fellow",
        institution="Test Medical Center",
        fellowship_year=4
    )
    
    print(f"✓ Created session: {session.user_id}")
    print(f"  - Name: {session.name}")
    print(f"  - Institution: {session.institution}")
    print(f"  - Current difficulty: {session.current_difficulty.value}")
    
    # Add conversation turn
    turn = ConversationTurn(
        user_message="How do I calculate DOT?",
        ai_response="DOT (Days of Therapy) is calculated by counting the number of days a patient receives an antibiotic...",
        module_id="analytics",
        citations=[{"title": "IDSA Guidelines", "year": 2023}]
    )
    session.add_turn(turn)
    mgr.save_conversation_turn(session.user_id, turn)
    
    print(f"✓ Added conversation turn")
    print(f"  - Conversation history length: {len(session.conversation_history)}")
    
    # Update module progress
    session.update_module_progress("analytics", 0.75, {"feedback": "Good understanding shown"})
    print(f"✓ Updated module progress")
    print(f"  - Analytics module mastery: {session.module_progress['analytics'].mastery_level}")
    
    return session

def test_conversation_manager(session):
    """Test conversation management with context"""
    print("\n=== Testing Conversation Manager ===")
    
    mgr = ConversationManager()
    
    # Process a conversation turn
    result = mgr.process_turn(session, "Hello, I want to learn about ASP", None)
    
    print(f"✓ Processed greeting")
    print(f"  - Intent detected: {result['intent']}")
    print(f"  - Current state: {result['context'].state.value}")
    print(f"  - Response strategy: {result['response_strategy']['type']}")
    
    # Process module selection
    result = mgr.process_turn(session, "I want to work on leadership skills", "leadership")
    print(f"✓ Processed module selection")
    print(f"  - New state: {result['context'].state.value}")
    print(f"  - Scaffolding level: {result['scaffolding_level']}")
    
    # Get scenario
    scenario = mgr.get_scenario_for_user(session, "leadership")
    if scenario:
        print(f"✓ Retrieved scenario: {scenario['title']}")
        print(f"  - Learning objectives: {len(scenario['learning_objectives'])} objectives")
    
    return result

def test_adaptive_engine(session):
    """Test adaptive learning engine"""
    print("\n=== Testing Adaptive Learning Engine ===")
    
    engine = AdaptiveLearningEngine()
    
    # Create learner profile
    profile = engine.get_or_create_profile(session.user_id)
    print(f"✓ Created learner profile")
    print(f"  - Learning style: {profile.learning_style}")
    print(f"  - Pace preference: {profile.pace_preference}")
    
    # Assess mastery level
    mastery = engine.assess_mastery_level(session, "analytics")
    print(f"✓ Assessed mastery level: {mastery.name}")
    
    # Calculate difficulty adjustment
    performance = {
        'accuracy': 0.85,
        'response_time': 25,
        'hints_used': 0,
        'attempts': 1
    }
    new_difficulty, reasoning = engine.calculate_difficulty_adjustment(session, performance)
    print(f"✓ Calculated difficulty adjustment")
    print(f"  - Current: {session.current_difficulty.value}")
    print(f"  - Recommended: {new_difficulty.value}")
    print(f"  - Reasoning: {reasoning}")
    
    # Generate personalized path
    path = engine.generate_personalized_path(session)
    print(f"✓ Generated personalized learning path")
    for i, recommendation in enumerate(path[:2], 1):
        print(f"  {i}. {recommendation['module']} ({recommendation['priority']}): {recommendation['reason']}")
    
    # Predict time to mastery
    prediction = engine.predict_time_to_mastery(session, "analytics", MasteryLevel.EVALUATING)
    print(f"✓ Predicted time to mastery")
    if prediction['already_achieved']:
        print(f"  - Already at {prediction['current_level']}")
    else:
        print(f"  - Estimated hours: {prediction.get('estimated_hours', 'N/A')}")
        print(f"  - Estimated sessions: {prediction.get('estimated_sessions', 'N/A')}")
    
    return engine

def test_rubric_scorer():
    """Test rubric-based scoring"""
    print("\n=== Testing Rubric Scorer ===")
    
    scorer = RubricScorer()
    
    # List available rubrics
    rubrics = scorer.library.list_available_rubrics()
    print(f"✓ Available rubrics: {len(rubrics)}")
    for rubric in rubrics[:3]:
        print(f"  - {rubric}")
    
    # Evaluate a sample response
    sample_response = """
    To demonstrate the ROI of our ASP program, I would focus on three key metrics:
    1. Cost savings from reduced antibiotic expenditure - We've seen a 25% reduction in broad-spectrum antibiotic costs
    2. Decreased length of stay - Average LOS reduced by 1.2 days for patients with appropriate de-escalation
    3. Reduction in C. difficile infections - 30% decrease in hospital-acquired CDI rates
    
    The total annual cost savings is approximately $1.5 million, with cost avoidance from prevented complications
    adding another $800,000. This gives us an ROI of 3.2:1 for our program investment.
    """
    
    evaluation = scorer.evaluate_response(sample_response, "leadership_business_case")
    
    print(f"✓ Evaluated response")
    print(f"  - Overall score: {evaluation.percentage:.1f}%")
    print(f"  - Level: {evaluation.overall_level.name}")
    print(f"  - Strengths: {len(evaluation.strengths)}")
    print(f"  - Areas for improvement: {len(evaluation.areas_for_improvement)}")
    
    if evaluation.strengths:
        print(f"  - Top strength: {evaluation.strengths[0][:50]}...")
    
    return evaluation

def test_equity_analytics():
    """Test equity analytics"""
    print("\n=== Testing Equity Analytics ===")
    
    analytics = EquityAnalytics()
    
    # Generate sample data by creating multiple sessions
    mgr = SessionManager()
    institutions = [
        ("Academic Medical Center", 5, 0.85),
        ("Community Hospital", 3, 0.65),
        ("VA Medical Center", 4, 0.70),
        ("Children's Hospital", 4, 0.80)
    ]
    
    print("✓ Creating sample user data...")
    for inst, year, mastery in institutions:
        session = mgr.create_session(
            institution=inst,
            fellowship_year=year,
            name=f"Fellow at {inst}"
        )
        # Add some progress
        session.update_module_progress("leadership", mastery, {"test": "data"})
        mgr.update_session(session)
    
    # Run equity analysis
    report = analytics.analyze_equity(30)
    
    print(f"✓ Generated equity report")
    print(f"  - Total users analyzed: {report.total_users}")
    print(f"  - Disparities found: {len(report.disparities_found)}")
    print(f"  - Demographic categories analyzed: {len(report.demographic_breakdowns)}")
    
    # Display any high-severity disparities
    high_severity = [d for d in report.disparities_found if d.severity == "high"]
    if high_severity:
        print(f"  - High severity issues: {len(high_severity)}")
        for disparity in high_severity[:2]:
            print(f"    • {disparity.description}")
    
    # Get dashboard data
    dashboard = analytics.generate_dashboard_data()
    print(f"✓ Generated dashboard data")
    print(f"  - Alerts: {len(dashboard['alerts'])}")
    print(f"  - Recommendations: {len(dashboard['recommendations'])}")
    
    return report

def test_integration():
    """Test full integration of all components"""
    print("\n=== Testing Full Integration ===")
    
    # Create managers
    session_mgr = SessionManager()
    conv_mgr = ConversationManager()
    adaptive = AdaptiveLearningEngine()
    scorer = RubricScorer()
    
    # Simulate a complete learning interaction
    print("✓ Simulating complete learner journey...")
    
    # 1. Create new learner
    learner = session_mgr.create_session(
        name="Integration Test Fellow",
        institution="Test University Hospital",
        fellowship_year=4,
        email="test@testuniversity.edu"
    )
    
    # 2. Process initial conversation
    conv_result = conv_mgr.process_turn(learner, "I want to improve my ASP leadership skills", "leadership")
    
    # 3. Get appropriate scenario
    scenario = conv_mgr.get_scenario_for_user(learner, "leadership")
    if scenario:
        adapted = adaptive.adapt_scenario_complexity(scenario, learner)
        print(f"  - Scenario: {adapted['title']}")
        print(f"  - Complexity adapted for: {learner.current_difficulty.value}")
    
    # 4. Simulate learner response and evaluate
    learner_response = "I would present data on cost savings and quality improvements"
    evaluation = scorer.evaluate_response(learner_response, "leadership_business_case")
    
    # 5. Update progress based on evaluation
    learner.update_module_progress("leadership", evaluation.percentage / 100, 
                                  {"rubric_feedback": evaluation.specific_feedback})
    
    # 6. Adjust difficulty
    performance = {
        'accuracy': evaluation.percentage / 100,
        'response_time': 30,
        'hints_used': 0,
        'attempts': 1
    }
    new_diff, reasoning = adaptive.calculate_difficulty_adjustment(learner, performance)
    
    print(f"  - Evaluation score: {evaluation.percentage:.1f}%")
    print(f"  - Difficulty adjustment: {learner.current_difficulty.value} → {new_diff.value}")
    print(f"  - Next steps: {evaluation.next_steps[0] if evaluation.next_steps else 'Continue practicing'}")
    
    print("\n✅ All integration tests completed successfully!")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("ASP AI Agent Integration Test Suite")
    print("=" * 60)
    
    try:
        # Test individual components
        session = test_session_management()
        test_conversation_manager(session)
        test_adaptive_engine(session)
        test_rubric_scorer()
        test_equity_analytics()
        
        # Test full integration
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())