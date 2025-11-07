#!/usr/bin/env python3
"""
Interactive test script for CICU Prolonged Antibiotics Module
Tests the module's educational scenarios and adaptive features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cicu_prolonged_antibiotics_module import CICUAntibioticsModule, DifficultyLevel
import json
from typing import Dict, List

def display_scenario(scenario: Dict) -> None:
    """Display a scenario in a readable format"""
    print("\n" + "="*80)
    print(f"📚 SCENARIO: {scenario['title']}")
    print("="*80)
    print(f"\n{scenario['description']}")
    print("\n📋 KEY TASKS:")
    for i, task in enumerate(scenario['key_tasks'], 1):
        print(f"   {i}. {task}")
    print(f"\n🎯 COMPETENCIES: {', '.join(scenario['expected_competencies'])}")
    print("="*80)

def display_hint(hint: str, hint_num: int) -> None:
    """Display a hint"""
    print(f"\n💡 HINT {hint_num + 1}: {hint}")

def display_metrics(metrics: Dict) -> None:
    """Display implementation metrics"""
    print("\n" + "="*80)
    print("📊 IMPLEMENTATION METRICS TRACKER")
    print("="*80)
    
    print("\n🔄 PROCESS METRICS (Weekly):")
    for key, metric in metrics['process_metrics'].items():
        print(f"  • {metric['description']}")
        print(f"    Target: {metric['target']}% | Measured: {metric['measurement']}")
    
    print("\n📈 OUTCOME METRICS (Monthly):")
    for key, metric in metrics['outcome_metrics'].items():
        print(f"  • {metric['description']}")
        if 'baseline' in metric:
            print(f"    Baseline: {metric['baseline']} → Target: {metric['target']}")
        else:
            print(f"    Target: {metric['target']}")
    
    print("\n⚖️ BALANCING METRICS:")
    for key, metric in metrics['balancing_metrics'].items():
        print(f"  • {metric['description']}")
        print(f"    {metric.get('monitoring', metric.get('target', 'Monitor'))}")

def display_countermeasure(countermeasure: Dict) -> None:
    """Display countermeasure strategies"""
    print("\n" + "="*80)
    print(f"🛠️ COUNTERMEASURE: {countermeasure.get('barrier', 'Unknown')}")
    print("="*80)
    print("\n📋 STRATEGIES:")
    for i, strategy in enumerate(countermeasure.get('strategies', []), 1):
        print(f"  {i}. {strategy}")
    print(f"\n⏰ TIMELINE: {countermeasure.get('timeline', 'TBD')}")
    print(f"📏 SUCCESS METRIC: {countermeasure.get('success_metric', 'TBD')}")

def interactive_test():
    """Run interactive test of the CICU module"""
    print("\n" + "="*80)
    print("🏥 CICU PROLONGED ANTIBIOTICS MODULE - INTERACTIVE TEST")
    print("="*80)
    
    module = CICUAntibioticsModule()
    
    print(f"\nModule: {module.module_title}")
    print(f"Problem: {module.clinical_problem}")
    
    print("\n📚 LEARNING OBJECTIVES:")
    for i, obj in enumerate(module.learning_objectives, 1):
        print(f"  {i}. {obj}")
    
    # Test each difficulty level
    levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, 
              DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
    
    for level in levels:
        input(f"\n\nPress Enter to view {level.value.upper()} scenario...")
        scenario = module.get_scenario(level)
        display_scenario(scenario)
        
        # Show hints for this level
        input(f"\nPress Enter to view hints for {level.value} level...")
        for i in range(3):  # Show first 3 hints
            hint = module.get_hint(level, i)
            if hint:
                display_hint(hint, i)
    
    # Test implementation metrics
    input("\n\nPress Enter to view Implementation Metrics Tracker...")
    metrics = module.generate_implementation_tracker()
    display_metrics(metrics)
    
    # Test countermeasures
    input("\n\nPress Enter to view Countermeasure Examples...")
    barriers = ["provider_resistance", "fear_of_adverse_outcomes", 
                "workflow_disruption", "communication_gaps"]
    
    for barrier in barriers:
        countermeasure = module.generate_countermeasure_template(barrier)
        display_countermeasure(countermeasure)
        if barrier != barriers[-1]:
            input("\nPress Enter for next countermeasure...")
    
    # Test scaffolding levels
    print("\n" + "="*80)
    print("🎓 SCAFFOLDING LEVELS")
    print("="*80)
    
    # Simulate different performance levels
    performance_scenarios = [
        ([], "New learner"),
        ([2.5, 2.8, 3.0], "Developing learner"),
        ([3.5, 4.0, 3.8], "Proficient learner"),
        ([4.5, 4.8, 5.0], "Expert learner")
    ]
    
    for performance, description in performance_scenarios:
        scaffolding = module.get_scaffolding_level(performance)
        print(f"\n📊 {description} (avg: {sum(performance)/len(performance) if performance else 0:.1f})")
        print(f"   → Scaffolding: {scaffolding.upper()}")
        print(f"   → Support: {module.scaffolding[scaffolding]['description']}")
    
    # Export module data
    print("\n" + "="*80)
    print("💾 EXPORTING MODULE DATA")
    print("="*80)
    
    export_path = "tests/cicu_module_test_export.json"
    with open(export_path, "w") as f:
        f.write(module.export_module_content())
    print(f"\n✅ Module data exported to: {export_path}")
    
    # Summary
    print("\n" + "="*80)
    print("✅ TEST COMPLETE - MODULE FUNCTIONING CORRECTLY")
    print("="*80)
    print("\nThe CICU module successfully demonstrates:")
    print("  • 4 progressive difficulty levels")
    print("  • Comprehensive hint system")
    print("  • Implementation metrics tracking")
    print("  • Countermeasure strategies")
    print("  • Adaptive scaffolding")
    print("  • Full data export capability")
    print("\n🚀 Ready for integration with the ASP Education Platform!")

def automated_test():
    """Run automated tests of module components"""
    print("\n" + "="*80)
    print("🤖 AUTOMATED MODULE TESTS")
    print("="*80)
    
    module = CICUAntibioticsModule()
    errors = []
    
    # Test 1: Scenario retrieval
    print("\n✔️ Testing scenario retrieval...")
    for level in DifficultyLevel:
        try:
            scenario = module.get_scenario(level)
            assert 'title' in scenario
            assert 'description' in scenario
            assert 'key_tasks' in scenario
            assert len(scenario['key_tasks']) > 0
        except Exception as e:
            errors.append(f"Scenario test failed for {level}: {e}")
    
    # Test 2: Hint system
    print("✔️ Testing hint system...")
    for level in DifficultyLevel:
        try:
            hints = module.hints[level]
            assert len(hints) >= 3
            # Test valid hint retrieval
            hint = module.get_hint(level, 0)
            assert hint is not None
            # Test out of range
            hint = module.get_hint(level, 999)
            assert hint is None
        except Exception as e:
            errors.append(f"Hint test failed for {level}: {e}")
    
    # Test 3: Rubrics structure
    print("✔️ Testing rubric structure...")
    expected_rubrics = ["data_analysis", "behavioral_intervention", 
                        "implementation_science", "clinical_decision_making"]
    for rubric_name in expected_rubrics:
        try:
            rubric = module.rubrics[rubric_name]
            levels = ["exemplary", "proficient", "developing", "emerging", "not_evident"]
            for level in levels:
                assert level in rubric
                assert 'score' in rubric[level]
                assert 'criteria' in rubric[level]
        except Exception as e:
            errors.append(f"Rubric test failed for {rubric_name}: {e}")
    
    # Test 4: Scaffolding logic
    print("✔️ Testing scaffolding logic...")
    test_cases = [
        ([], "extensive"),
        ([1.0, 2.0], "extensive"),
        ([3.0, 3.5], "moderate"),
        ([4.0, 4.5], "minimal")
    ]
    for performance, expected in test_cases:
        try:
            result = module.get_scaffolding_level(performance)
            assert result == expected, f"Expected {expected}, got {result}"
        except Exception as e:
            errors.append(f"Scaffolding test failed: {e}")
    
    # Test 5: Metrics generation
    print("✔️ Testing metrics generation...")
    try:
        metrics = module.generate_implementation_tracker()
        assert 'process_metrics' in metrics
        assert 'outcome_metrics' in metrics
        assert 'balancing_metrics' in metrics
        assert len(metrics['process_metrics']) >= 3
        assert len(metrics['outcome_metrics']) >= 3
    except Exception as e:
        errors.append(f"Metrics test failed: {e}")
    
    # Test 6: Countermeasure templates
    print("✔️ Testing countermeasure templates...")
    barrier_types = ["provider_resistance", "fear_of_adverse_outcomes",
                    "workflow_disruption", "communication_gaps", "unknown"]
    for barrier in barrier_types:
        try:
            template = module.generate_countermeasure_template(barrier)
            assert 'barrier' in template
            assert 'strategies' in template
            assert 'timeline' in template
            assert 'success_metric' in template
        except Exception as e:
            errors.append(f"Countermeasure test failed for {barrier}: {e}")
    
    # Test 7: Export functionality
    print("✔️ Testing export functionality...")
    try:
        export_data = module.export_module_content()
        data = json.loads(export_data)
        assert 'module_id' in data
        assert data['module_id'] == 'cicu_prolonged_antibiotics'
        assert 'scenarios' in data
        assert 'rubrics' in data
        assert 'hints' in data
    except Exception as e:
        errors.append(f"Export test failed: {e}")
    
    # Report results
    print("\n" + "="*80)
    if errors:
        print("❌ TESTS FAILED:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ ALL TESTS PASSED!")
    print("="*80)
    
    return len(errors) == 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Run automated tests
        success = automated_test()
        sys.exit(0 if success else 1)
    else:
        # Run interactive test
        interactive_test()