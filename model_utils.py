"""
Model utilities for workout recommender.

This module provides functions for:
- Loading and caching the trained ML model
- Making predictions for workout plan recommendations
- Retrieving plan templates and personalizing them
- Handling exercise replacements based on user preferences
"""

import os
import joblib
import pandas as pd
import random
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Import plans module
try:
    import plans
except ImportError:
    raise ImportError("Could not import plans.py. Make sure it exists in the same directory.")

# Configuration
MODEL_PATH = "models/plan_model.pkl"
EXERCISES_CSV = "data/exercises_reduced.csv"

# Global cache for model
_cached_model = None
_exercises_df = None

class ModelNotFoundError(Exception):
    """Raised when the trained model file is not found."""
    pass

class PlansNotFoundError(Exception):
    """Raised when a plan ID is not found in the plans module."""
    pass

def _load_model():
    """Load the trained model from disk with caching."""
    global _cached_model
    
    if _cached_model is None:
        if not os.path.exists(MODEL_PATH):
            raise ModelNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                f"Please run train.py first to train the model."
            )
        
        try:
            _cached_model = joblib.load(MODEL_PATH)
            print(f"✓ Model loaded from {MODEL_PATH}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {MODEL_PATH}: {str(e)}")
    
    return _cached_model

def _load_exercises_df():
    """Load exercises DataFrame with caching."""
    global _exercises_df
    
    if _exercises_df is None:
        if not os.path.exists(EXERCISES_CSV):
            print(f"Warning: Exercises file not found at {EXERCISES_CSV}. Using fallback exercises.")
            # Use fallback exercises if CSV is missing
            fallback_exercises = [
                {"name": "Push Up", "equipment_cat": "none", "body_part": "chest", "difficulty": "beginner", "gif_url": ""},
                {"name": "Bodyweight Squat", "equipment_cat": "none", "body_part": "legs", "difficulty": "beginner", "gif_url": ""},
                {"name": "Plank", "equipment_cat": "none", "body_part": "core", "difficulty": "beginner", "gif_url": ""},
                {"name": "Jumping Jacks", "equipment_cat": "none", "body_part": "cardio", "difficulty": "beginner", "gif_url": ""},
                {"name": "Burpee", "equipment_cat": "none", "body_part": "full body", "difficulty": "intermediate", "gif_url": ""},
                {"name": "Mountain Climbers", "equipment_cat": "none", "body_part": "cardio", "difficulty": "intermediate", "gif_url": ""},
                {"name": "Lunges", "equipment_cat": "none", "body_part": "legs", "difficulty": "beginner", "gif_url": ""},
                {"name": "Side Plank", "equipment_cat": "none", "body_part": "core", "difficulty": "intermediate", "gif_url": ""},
            ]
            _exercises_df = pd.DataFrame(fallback_exercises)
        else:
            try:
                _exercises_df = pd.read_csv(EXERCISES_CSV)
                required_cols = {'name', 'equipment_cat', 'body_part', 'difficulty'}
                if not required_cols.issubset(set(_exercises_df.columns)):
                    missing = required_cols - set(_exercises_df.columns)
                    raise ValueError(f"Exercises CSV missing required columns: {missing}")
                print(f"✓ Loaded {len(_exercises_df)} exercises from {EXERCISES_CSV}")
            except Exception as e:
                raise RuntimeError(f"Failed to load exercises from {EXERCISES_CSV}: {str(e)}")
    
    return _exercises_df

def predict_plan(input_dict: Dict[str, Any]) -> Tuple[str, float]:
    """
    Predict workout plan for a given user profile.
    
    Args:
        input_dict (dict): User profile with keys:
            - goal: str ('build_muscle', 'endurance', 'flexibility', 'lose_weight')
            - equipment: str ('basic', 'gym', 'none')  
            - experience: str ('beginner', 'intermediate', 'advanced')
            - time_per_day: int (minutes available per day)
            - days_per_week: int (days per week for workout)
    
    Returns:
        tuple: (predicted_plan_id, confidence_probability)
    
    Example:
        >>> user_profile = {
        ...     'goal': 'build_muscle',
        ...     'equipment': 'gym', 
        ...     'experience': 'intermediate',
        ...     'time_per_day': 60,
        ...     'days_per_week': 5
        ... }
        >>> plan_id, confidence = predict_plan(user_profile)
        >>> print(f"Recommended plan: {plan_id} (confidence: {confidence:.3f})")
    """
    
    # Validate input
    required_keys = {'goal', 'equipment', 'experience', 'time_per_day', 'days_per_week'}
    missing_keys = required_keys - set(input_dict.keys())
    if missing_keys:
        raise ValueError(f"Missing required keys in input_dict: {missing_keys}")
    
    # Load model
    model = _load_model()
    
    # Convert input to DataFrame
    input_df = pd.DataFrame([input_dict])
    
    # Make prediction
    try:
        predicted_plan = model.predict(input_df)[0]
        probabilities = model.predict_proba(input_df)[0]
        max_probability = max(probabilities)
        
        return predicted_plan, max_probability
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {str(e)}")

def get_plan_template(plan_id: str) -> Dict[str, Any]:
    """
    Get a plan template by plan ID from the plans module.
    
    Args:
        plan_id (str): Plan identifier (e.g., 'P1', 'P2', etc.)
    
    Returns:
        dict: Plan template with metadata and exercises
    
    Raises:
        PlansNotFoundError: If plan_id is not found
    
    Example:
        >>> plan = get_plan_template('P1')
        >>> print(f"Plan: {plan['meta']['name']}")
        >>> print(f"Days in plan: {len(plan['week'])}")
    """
    
    try:
        plan_template = plans.get_plan(plan_id)
        if plan_template is None:
            available_plans = plans.list_plans()
            raise PlansNotFoundError(
                f"Plan '{plan_id}' not found. Available plans: {available_plans}"
            )
        
        # Return a deep copy to avoid modifying the original
        import copy
        return copy.deepcopy(plan_template)
    
    except AttributeError:
        raise RuntimeError(
            "Plans module is missing required functions. "
            "Make sure plans.py has get_plan() and list_plans() functions."
        )

def personalize_plan(
    plan: Dict[str, Any], 
    liked_exercises: List[str] = None,
    disliked_exercises: List[str] = None,
    exercises_csv: str = EXERCISES_CSV
) -> Dict[str, Any]:
    """
    Personalize a workout plan by replacing disliked exercises with suitable alternatives.
    
    Args:
        plan (dict): Plan template from get_plan_template()
        liked_exercises (list, optional): List of exercise names user likes
        disliked_exercises (list, optional): List of exercise names to replace
        exercises_csv (str): Path to exercises CSV file
    
    Returns:
        dict: Personalized plan with exercise replacements
    
    Example:
        >>> plan = get_plan_template('P1')
        >>> personalized = personalize_plan(
        ...     plan, 
        ...     liked_exercises=['Push Up', 'Squat'],
        ...     disliked_exercises=['Burpee', 'Mountain Climbers']
        ... )
    """
    
    if liked_exercises is None:
        liked_exercises = []
    if disliked_exercises is None:
        disliked_exercises = []
    
    if not disliked_exercises:
        # No changes needed
        return plan
    
    # Load exercises database
    try:
        exercises_df = _load_exercises_df()
    except Exception as e:
        print(f"Warning: Could not load exercises database: {e}")
        print("Returning plan without personalization.")
        return plan
    
    # Get plan equipment constraints
    plan_equipment = plan['meta'].get('equipment', 'none')
    allowed_equipment = _get_allowed_equipment(plan_equipment)
    
    # Create working copy of the plan
    import copy
    personalized_plan = copy.deepcopy(plan)
    
    replacements_made = 0
    
    # Process each day in the plan
    for day_idx, day in enumerate(personalized_plan['week']):
        for ex_idx, exercise in enumerate(day['exercises']):
            exercise_name = exercise.get('name', '')
            
            # Check if this exercise should be replaced
            if exercise_name in disliked_exercises:
                # Find a suitable replacement
                replacement = _find_exercise_replacement(
                    exercise, exercises_df, allowed_equipment, disliked_exercises + [exercise_name]
                )
                
                if replacement:
                    # Update the exercise
                    personalized_plan['week'][day_idx]['exercises'][ex_idx].update({
                        'name': replacement['name'],
                        'equipment': replacement.get('equipment_cat', exercise.get('equipment', '')),
                        'body_part': replacement.get('body_part', exercise.get('body_part', '')),
                        'gif_url': replacement.get('gif_url', exercise.get('gif_url', ''))
                    })
                    replacements_made += 1
                    print(f"✓ Replaced '{exercise_name}' with '{replacement['name']}'")
                else:
                    print(f"⚠ Could not find suitable replacement for '{exercise_name}'")
    
    if replacements_made > 0:
        print(f"✓ Made {replacements_made} exercise replacements")
    else:
        print("ℹ No exercise replacements were needed or possible")
    
    return personalized_plan

def _get_allowed_equipment(plan_equipment: str) -> List[str]:
    """Get allowed equipment categories for a plan."""
    if plan_equipment == 'gym':
        return ['gym', 'basic', 'none']
    elif plan_equipment == 'basic':
        return ['basic', 'none']
    else:  # 'none'
        return ['none']

def _find_exercise_replacement(
    original_exercise: Dict[str, Any],
    exercises_df: pd.DataFrame,
    allowed_equipment: List[str],
    excluded_names: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Find a suitable replacement exercise matching the same body part and equipment constraints.
    
    Args:
        original_exercise: The exercise to replace
        exercises_df: DataFrame of available exercises
        allowed_equipment: List of allowed equipment categories
        excluded_names: List of exercise names to exclude from replacements
    
    Returns:
        dict or None: Replacement exercise data or None if no suitable replacement found
    """
    
    original_body_part = original_exercise.get('body_part', '')
    original_equipment = original_exercise.get('equipment', '')
    
    # Filter exercises by constraints
    candidates = exercises_df[
        (exercises_df['equipment_cat'].isin(allowed_equipment)) &
        (~exercises_df['name'].isin(excluded_names))
    ].copy()
    
    if candidates.empty:
        return None
    
    # First preference: Same body part
    if original_body_part:
        same_body_part = candidates[candidates['body_part'] == original_body_part]
        if not same_body_part.empty:
            candidates = same_body_part
    
    # Second preference: Same equipment category
    if original_equipment:
        same_equipment = candidates[candidates['equipment_cat'] == original_equipment]
        if not same_equipment.empty:
            candidates = same_equipment
    
    # Randomly select from remaining candidates
    if not candidates.empty:
        replacement_row = candidates.sample(n=1, random_state=random.randint(1, 10000)).iloc[0]
        return {
            'name': replacement_row['name'],
            'equipment_cat': replacement_row['equipment_cat'],
            'body_part': replacement_row['body_part'],
            'difficulty': replacement_row['difficulty'],
            'gif_url': replacement_row.get('gif_url', '')
        }
    
    return None

# Convenience function to get a complete personalized recommendation
def get_personalized_recommendation(
    user_profile: Dict[str, Any],
    liked_exercises: List[str] = None,
    disliked_exercises: List[str] = None
) -> Dict[str, Any]:
    """
    Get a complete personalized workout recommendation.
    
    This combines prediction, plan retrieval, and personalization in one call.
    
    Args:
        user_profile: User characteristics for prediction
        liked_exercises: List of exercise names user likes
        disliked_exercises: List of exercise names to replace
    
    Returns:
        dict: Complete recommendation with plan_id, confidence, and personalized plan
    
    Example:
        >>> user_profile = {
        ...     'goal': 'build_muscle',
        ...     'equipment': 'gym',
        ...     'experience': 'intermediate', 
        ...     'time_per_day': 60,
        ...     'days_per_week': 5
        ... }
        >>> recommendation = get_personalized_recommendation(
        ...     user_profile,
        ...     disliked_exercises=['Burpee']
        ... )
        >>> print(f"Plan: {recommendation['plan_id']} ({recommendation['confidence']:.1%})")
        >>> print(f"Name: {recommendation['plan']['meta']['name']}")
    """
    
    # Get prediction
    plan_id, confidence = predict_plan(user_profile)
    
    # Get plan template
    plan_template = get_plan_template(plan_id)
    
    # Personalize the plan
    personalized_plan = personalize_plan(
        plan_template, 
        liked_exercises=liked_exercises,
        disliked_exercises=disliked_exercises
    )
    
    return {
        'plan_id': plan_id,
        'confidence': confidence,
        'plan': personalized_plan,
        'user_profile': user_profile
    }

# Utility functions for debugging and exploration
def list_available_plans() -> List[str]:
    """Get list of all available plan IDs."""
    try:
        return plans.list_plans()
    except AttributeError:
        return []

def get_model_info() -> Dict[str, Any]:
    """Get information about the loaded model."""
    try:
        model = _load_model()
        return {
            'model_type': type(model).__name__,
            'model_path': MODEL_PATH,
            'model_loaded': True
        }
    except Exception as e:
        return {
            'model_type': None,
            'model_path': MODEL_PATH,
            'model_loaded': False,
            'error': str(e)
        }

def adapt_week_plan(plan: dict, days_per_week: int, keep_rest_days: bool = True) -> list:
    """
    Adapt a 7-day workout plan to a specific number of training days per week.
    
    This function takes a workout plan template and returns a modified week schedule
    with exactly the specified number of training days, evenly distributed across
    the week. Non-training days can either be marked as rest days or removed entirely.
    
    Args:
        plan (dict): Plan dictionary containing 'week' key with 7-day list
        days_per_week (int): Number of training days desired (1-7)
        keep_rest_days (bool): If True, return 7-day list with rest days filled in.
                              If False, return only training days (length N)
    
    Returns:
        list: Modified week schedule
            - If keep_rest_days=True: 7-element list with training days and rest days
            - If keep_rest_days=False: N-element list with only training days
    
    Raises:
        ValueError: If days_per_week <= 0
        KeyError: If plan doesn't contain 'week' key
    
    Examples:
        >>> # Original 7-day plan
        >>> plan = {
        ...     'week': [
        ...         {'day': 1, 'focus': 'Upper Body', 'exercises': ['Push Up']},
        ...         {'day': 2, 'focus': 'Lower Body', 'exercises': ['Squat']},
        ...         {'day': 3, 'focus': 'Cardio', 'exercises': ['Running']},
        ...         {'day': 4, 'focus': 'Upper Body', 'exercises': ['Pull Up']},
        ...         {'day': 5, 'focus': 'Lower Body', 'exercises': ['Deadlift']},
        ...         {'day': 6, 'focus': 'Full Body', 'exercises': ['Burpee']},
        ...         {'day': 7, 'focus': 'Cardio', 'exercises': ['Cycling']}
        ...     ]
        ... }
        >>> 
        >>> # Get 4 training days with rest days
        >>> adapted = adapt_week_plan(plan, 4, keep_rest_days=True)
        >>> len(adapted)  # Returns 7
        7
        >>> 
        >>> # Get 3 training days only
        >>> adapted = adapt_week_plan(plan, 3, keep_rest_days=False)
        >>> len(adapted)  # Returns 3
        3
    """
    
    # Validate inputs
    if days_per_week <= 0:
        raise ValueError(f"days_per_week must be positive, got {days_per_week}")
    
    if 'week' not in plan:
        raise KeyError("Plan must contain 'week' key with workout days")
    
    original_week = plan['week']
    
    # Handle edge cases
    if not original_week:
        if keep_rest_days:
            return [{"day": i+1, "focus": "Rest Day", "exercises": []} for i in range(7)]
        else:
            return []
    
    # Clamp days_per_week to maximum available or 7
    max_days = min(len(original_week), 7)
    days_per_week = min(days_per_week, max_days)
    
    # If requesting all 7 days (or all available days), return original
    if days_per_week >= len(original_week) and len(original_week) >= 7:
        if keep_rest_days:
            # Ensure we have exactly 7 days
            result = original_week[:7]
            while len(result) < 7:
                result.append({"day": len(result) + 1, "focus": "Rest Day", "exercises": []})
            return result
        else:
            return original_week[:days_per_week]
    
    # Calculate evenly distributed indices
    if days_per_week == 1:
        selected_indices = [0]  # Just take the first day
    else:
        # Use linspace-like distribution to spread days evenly
        import math
        step = (len(original_week) - 1) / (days_per_week - 1)
        selected_indices = []
        for i in range(days_per_week):
            idx = round(i * step)
            idx = min(idx, len(original_week) - 1)  # Ensure within bounds
            if idx not in selected_indices:  # Avoid duplicates
                selected_indices.append(idx)
        
        # If we have duplicates due to rounding, fill gaps
        while len(selected_indices) < days_per_week:
            for i in range(len(original_week)):
                if i not in selected_indices:
                    selected_indices.append(i)
                    break
        
        # Sort to maintain order and trim to exact count
        selected_indices = sorted(selected_indices[:days_per_week])
    
    # Build the result
    if keep_rest_days:
        # Create 7-day schedule with training days and rest days
        final_week = []
        selected_set = set(selected_indices)
        
        for day_idx in range(7):
            if day_idx < len(original_week) and day_idx in selected_set:
                # Copy training day, ensure day number is correct
                training_day = original_week[day_idx].copy()
                training_day['day'] = day_idx + 1
                final_week.append(training_day)
            else:
                # Add rest day
                final_week.append({
                    "day": day_idx + 1,
                    "focus": "Rest Day",
                    "exercises": []
                })
        
        return final_week
    else:
        # Return only selected training days
        return [original_week[i] for i in selected_indices]


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("MODEL_UTILS.PY DEMO")
    print("=" * 60)
    
    # Test model loading
    print("\n1. Model Information:")
    model_info = get_model_info()
    for key, value in model_info.items():
        print(f"   {key}: {value}")
    
    # Test available plans
    print(f"\n2. Available Plans: {list_available_plans()}")
    
    # Test prediction (if model is available)
    if model_info.get('model_loaded', False):
        print("\n3. Sample Prediction:")
        sample_profile = {
            'goal': 'build_muscle',
            'equipment': 'gym',
            'experience': 'intermediate',
            'time_per_day': 60,
            'days_per_week': 5
        }
        try:
            plan_id, confidence = predict_plan(sample_profile)
            print(f"   Profile: {sample_profile}")
            print(f"   Prediction: {plan_id} (confidence: {confidence:.3f})")
            
            # Test plan retrieval
            print("\n4. Plan Template:")
            plan = get_plan_template(plan_id)
            print(f"   Plan Name: {plan['meta']['name']}")
            print(f"   Days in week: {len(plan['week'])}")
            
        except Exception as e:
            print(f"   Error during prediction: {e}")
    else:
        print("\n3. Skipping prediction demo (model not loaded)")
    
    # Test adapt_week_plan function
    print("\n5. Testing adapt_week_plan Function:")
    
    # Create a sample 7-day plan for testing
    sample_plan = {
        'meta': {'name': 'Test Plan'},
        'week': [
            {'day': 1, 'focus': 'Upper Body', 'exercises': ['Push Up', 'Pull Up']},
            {'day': 2, 'focus': 'Lower Body', 'exercises': ['Squat', 'Lunge']},
            {'day': 3, 'focus': 'Cardio', 'exercises': ['Running', 'Jumping Jacks']},
            {'day': 4, 'focus': 'Upper Body', 'exercises': ['Bench Press', 'Row']},
            {'day': 5, 'focus': 'Lower Body', 'exercises': ['Deadlift', 'Calf Raises']},
            {'day': 6, 'focus': 'Full Body', 'exercises': ['Burpee', 'Mountain Climbers']},
            {'day': 7, 'focus': 'Cardio', 'exercises': ['Cycling', 'Swimming']}
        ]
    }
    
    # Test cases
    test_cases = [
        (4, True, "4 days with rest days"),
        (3, True, "3 days with rest days"), 
        (7, True, "7 days (all days)"),
        (8, True, "8 days (clamped to 7)"),
        (4, False, "4 days only (no rest)"),
        (3, False, "3 days only (no rest)")
    ]
    
    for days, keep_rest, description in test_cases:
        try:
            result = adapt_week_plan(sample_plan, days, keep_rest)
            training_days = sum(1 for day in result if day.get('focus') != 'Rest Day')
            print(f"   {description}: {len(result)} total days, {training_days} training days")
            
            # Show which days are training days
            training_focuses = [day.get('focus', 'Unknown') for day in result if day.get('focus') != 'Rest Day']
            print(f"     Training focuses: {training_focuses}")
            
        except Exception as e:
            print(f"   {description}: ERROR - {e}")
    
    # Unit test assertions
    print("\n6. Unit Test Assertions:")
    try:
        # Test N=4 with rest days
        result_4 = adapt_week_plan(sample_plan, 4, True)
        assert len(result_4) == 7, f"Expected 7 days, got {len(result_4)}"
        training_count_4 = sum(1 for day in result_4 if day.get('focus') != 'Rest Day')
        assert training_count_4 == 4, f"Expected 4 training days, got {training_count_4}"
        print("   ✓ N=4 with rest days: PASSED")
        
        # Test N=3 without rest days
        result_3 = adapt_week_plan(sample_plan, 3, False)
        assert len(result_3) == 3, f"Expected 3 days, got {len(result_3)}"
        assert all(day.get('focus') != 'Rest Day' for day in result_3), "Should contain only training days"
        print("   ✓ N=3 without rest days: PASSED")
        
        # Test N=7 (all days)
        result_7 = adapt_week_plan(sample_plan, 7, True)
        assert len(result_7) == 7, f"Expected 7 days, got {len(result_7)}"
        training_count_7 = sum(1 for day in result_7 if day.get('focus') != 'Rest Day')
        assert training_count_7 == 7, f"Expected 7 training days, got {training_count_7}"
        print("   ✓ N=7 (all days): PASSED")
        
        # Test N>7 clamped to 7
        result_8 = adapt_week_plan(sample_plan, 8, True)
        assert len(result_8) == 7, f"Expected 7 days, got {len(result_8)}"
        training_count_8 = sum(1 for day in result_8 if day.get('focus') != 'Rest Day')
        assert training_count_8 == 7, f"Expected 7 training days, got {training_count_8}"
        print("   ✓ N>7 clamped to 7: PASSED")
        
        # Test error case
        try:
            adapt_week_plan(sample_plan, 0, True)
            assert False, "Should have raised ValueError for days_per_week=0"
        except ValueError:
            print("   ✓ ValueError for days_per_week=0: PASSED")
        
        print("   🎉 All unit tests PASSED!")
        
    except AssertionError as e:
        print(f"   ❌ Unit test FAILED: {e}")
    except Exception as e:
        print(f"   ❌ Unit test ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
