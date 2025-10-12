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
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
