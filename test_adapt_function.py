#!/usr/bin/env python3
"""
Test script for the adapt_week_plan function integration.

This script tests the new functionality without running the full Streamlit app.
"""

import model_utils

def test_adapt_week_plan_integration():
    """Test the adapt_week_plan function with a real plan template."""
    
    print("🧪 Testing adapt_week_plan function integration")
    print("=" * 60)
    
    # Get a sample plan template
    try:
        plan_template = model_utils.get_plan_template('P1')  # 4-day Upper/Lower Hypertrophy
        print(f"✅ Successfully loaded plan: {plan_template['meta']['name']}")
        print(f"   Original plan has {len(plan_template['week'])} days")
        
        # Test different days_per_week values
        test_cases = [
            (3, "3 days per week"),
            (4, "4 days per week"), 
            (5, "5 days per week"),
            (7, "7 days per week (full plan)"),
        ]
        
        print(f"\n📋 Testing different days_per_week scenarios:")
        print("-" * 60)
        
        for days_per_week, description in test_cases:
            print(f"\n🔹 Test case: {description}")
            
            try:
                # Test with rest days
                adapted_plan = model_utils.adapt_week_plan(plan_template, days_per_week, keep_rest_days=True)
                training_days = len([d for d in adapted_plan if d.get('focus') != 'Rest Day' and d.get('exercises')])
                rest_days = len([d for d in adapted_plan if d.get('focus') == 'Rest Day'])
                
                print(f"   ✅ Adapted plan: {len(adapted_plan)} total days")
                print(f"      Training days: {training_days}")
                print(f"      Rest days: {rest_days}")
                
                # Show the schedule
                schedule = []
                for day in adapted_plan:
                    if day.get('focus') == 'Rest Day':
                        schedule.append("Rest")
                    else:
                        schedule.append(day.get('focus', 'Training')[:8])  # Truncate for display
                
                print(f"      Schedule: {' | '.join(schedule)}")
                
                # Validate
                assert len(adapted_plan) == 7, f"Expected 7 days, got {len(adapted_plan)}"
                assert training_days <= days_per_week, f"Too many training days: {training_days} > {days_per_week}"
                assert training_days >= min(days_per_week, len([d for d in plan_template['week'] if d.get('exercises')])), "Too few training days"
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        print(f"\n🎉 All integration tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading plan template: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling."""
    
    print(f"\n🧪 Testing edge cases")
    print("-" * 60)
    
    # Create a minimal plan for testing
    minimal_plan = {
        'meta': {'name': 'Test Plan'},
        'week': [
            {'day': 1, 'focus': 'Upper Body', 'exercises': ['Push Up']},
            {'day': 2, 'focus': 'Lower Body', 'exercises': ['Squat']},
        ]
    }
    
    test_cases = [
        ("Minimal plan with 1 day", minimal_plan, 1),
        ("Minimal plan with 3 days", minimal_plan, 3),
        ("Minimal plan with 5 days", minimal_plan, 5),
    ]
    
    for description, plan, days in test_cases:
        try:
            result = model_utils.adapt_week_plan(plan, days, keep_rest_days=True)
            training_count = len([d for d in result if d.get('focus') != 'Rest Day'])
            print(f"✅ {description}: {training_count} training days, {7-training_count} rest days")
        except Exception as e:
            print(f"❌ {description}: {e}")
    
    # Test error cases
    print(f"\n🔍 Testing error handling:")
    
    try:
        model_utils.adapt_week_plan({'week': []}, 0, True)
        print("❌ Should have raised ValueError for days_per_week=0")
    except ValueError:
        print("✅ Correctly raised ValueError for days_per_week=0")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    try:
        model_utils.adapt_week_plan({'no_week_key': []}, 3, True)
        print("❌ Should have raised KeyError for missing 'week' key")
    except KeyError:
        print("✅ Correctly raised KeyError for missing 'week' key")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Testing adapt_week_plan Integration")
    print("=" * 60)
    
    success = test_adapt_week_plan_integration()
    test_edge_cases()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
        print("   The adapt_week_plan function is ready for use in the Streamlit app.")
    else:
        print("❌ SOME TESTS FAILED")
        print("   Please check the errors above.")
    print("=" * 60)