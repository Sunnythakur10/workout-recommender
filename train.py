"""
Workout Recommender Training Script

This script trains a RandomForest model to predict workout plan IDs based on user profiles.
Data includes user characteristics like fitness goals, equipment, experience level, and time constraints.
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_PATH = "data/templates.csv"
MODEL_PATH = "models/plan_model.pkl"

def validate_data(df):
    """Validate that the dataset has all required columns."""
    required_columns = ['profile_id', 'goal', 'equipment', 'experience', 
                       'time_per_day', 'days_per_week', 'plan_id']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    print(f"✓ Data validation passed. Found all required columns.")
    print(f"✓ Dataset shape: {df.shape}")
    print(f"✓ No missing values: {df.isnull().sum().sum() == 0}")

def load_and_preprocess_data():
    """Load and prepare the training data."""
    print("Loading data...")
    
    # Load data
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    validate_data(df)
    
    # Separate features and target
    X = df[['goal', 'equipment', 'experience', 'time_per_day', 'days_per_week']]
    y = df['plan_id']
    
    print(f"✓ Features shape: {X.shape}")
    print(f"✓ Target classes: {sorted(y.unique())}")
    print(f"✓ Class distribution:")
    print(y.value_counts().sort_index())
    
    return X, y

def create_preprocessing_pipeline():
    """Create preprocessing pipeline with OneHotEncoder for categorical features."""
    # Define categorical and numerical columns
    categorical_features = ['goal', 'equipment', 'experience']
    numerical_features = ['time_per_day', 'days_per_week']
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('num', 'passthrough', numerical_features)
        ]
    )
    
    return preprocessor

def train_model():
    """Main training function."""
    print("=" * 60)
    print("WORKOUT RECOMMENDER MODEL TRAINING")
    print("=" * 60)
    
    # Load data
    X, y = load_and_preprocess_data()
    
    # Create preprocessing pipeline
    preprocessor = create_preprocessing_pipeline()
    
    # Create full pipeline with RandomForest
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    print("\n" + "=" * 40)
    print("CROSS-VALIDATION EVALUATION")
    print("=" * 40)
    
    # 5-fold cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
    print(f"5-fold CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"Individual fold scores: {[f'{score:.4f}' for score in cv_scores]}")
    
    print("\n" + "=" * 40)
    print("HOLDOUT TEST EVALUATION") 
    print("=" * 40)
    
    # Train-test split (12% test split as requested)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.12, random_state=42, stratify=y
    )
    
    print(f"Training set size: {X_train.shape[0]} samples")
    print(f"Test set size: {X_test.shape[0]} samples")
    
    # Train the model
    print("\nTraining model...")
    pipeline.fit(X_train, y_train)
    
    # Predictions
    y_pred = pipeline.predict(X_test)
    holdout_accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Holdout Test Accuracy: {holdout_accuracy:.4f}")
    
    print("\n" + "=" * 40)
    print("CONFUSION MATRIX")
    print("=" * 40)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    classes = sorted(y.unique())
    
    print("Confusion Matrix:")
    print("Predicted →")
    print("Actual ↓")
    
    # Print header
    print(f"{'':>8}", end="")
    for cls in classes:
        print(f"{cls:>6}", end="")
    print()
    
    # Print matrix with row labels
    for i, cls in enumerate(classes):
        print(f"{cls:>8}", end="")
        for j in range(len(classes)):
            print(f"{cm[i,j]:>6}", end="")
        print()
    
    print("\n" + "=" * 40)
    print("FEATURE IMPORTANCE")
    print("=" * 40)
    
    # Get feature names after preprocessing
    cat_feature_names = []
    for i, cat in enumerate(['goal', 'equipment', 'experience']):
        encoder = pipeline.named_steps['preprocessor'].named_transformers_['cat']
        if hasattr(encoder, 'categories_'):
            categories = encoder.categories_[i]
            cat_feature_names.extend([f"{cat}_{category}" for category in categories])
    
    num_feature_names = ['time_per_day', 'days_per_week']
    all_feature_names = cat_feature_names + num_feature_names
    
    # Get feature importances
    importances = pipeline.named_steps['classifier'].feature_importances_
    
    # Create feature importance pairs and sort
    feature_importance_pairs = list(zip(all_feature_names, importances))
    feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
    
    print("Top 8 Feature Importances:")
    for i, (feature, importance) in enumerate(feature_importance_pairs[:8]):
        print(f"{i+1:2d}. {feature:<25} {importance:.4f}")
    
    print("\n" + "=" * 40)
    print("SAVING MODEL")
    print("=" * 40)
    
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Save the trained pipeline
    joblib.dump(pipeline, MODEL_PATH)
    print(f"✓ Model saved to: {MODEL_PATH}")
    
    return pipeline

def predict_plan(input_dict, model_path=MODEL_PATH):
    """
    Predict workout plan for a given user profile.
    
    Args:
        input_dict (dict): User profile with keys:
            - goal: str ('build_muscle', 'endurance', 'flexibility', 'lose_weight')
            - equipment: str ('basic', 'gym', 'none')  
            - experience: str ('beginner', 'intermediate', 'advanced')
            - time_per_day: int (minutes available per day)
            - days_per_week: int (days per week for workout)
        model_path (str): Path to the saved model
    
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
    
    # Load the trained model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
    
    model = joblib.load(model_path)
    
    # Convert input to DataFrame
    input_df = pd.DataFrame([input_dict])
    
    # Make prediction
    predicted_plan = model.predict(input_df)[0]
    
    # Get prediction probabilities
    probabilities = model.predict_proba(input_df)[0]
    max_probability = np.max(probabilities)
    
    return predicted_plan, max_probability

def print_usage_instructions():
    """Print clear instructions for using the trained model."""
    print("\n" + "=" * 60)
    print("HOW TO USE THE TRAINED MODEL")
    print("=" * 60)
    
    print("""
The model is now trained and saved. Here's how to use it:

1. IMPORT THE FUNCTION:
   from train import predict_plan

2. PREPARE USER INPUT:
   Create a dictionary with the following keys:
   
   user_profile = {
       'goal': 'build_muscle',      # Options: 'build_muscle', 'endurance', 'flexibility', 'lose_weight'
       'equipment': 'gym',          # Options: 'basic', 'gym', 'none'
       'experience': 'intermediate', # Options: 'beginner', 'intermediate', 'advanced'
       'time_per_day': 60,          # Minutes available per day (20-70)
       'days_per_week': 5           # Days per week for workout (3-6)
   }

3. GET PREDICTION:
   plan_id, confidence = predict_plan(user_profile)
   print(f"Recommended plan: {plan_id} (confidence: {confidence:.3f})")

4. EXAMPLE USAGE:
   
   # Example 1: Beginner with basic equipment
   beginner_profile = {
       'goal': 'lose_weight',
       'equipment': 'basic',
       'experience': 'beginner', 
       'time_per_day': 30,
       'days_per_week': 4
   }
   plan, conf = predict_plan(beginner_profile)
   print(f"Plan: {plan}, Confidence: {conf:.3f}")
   
   # Example 2: Advanced gym user
   advanced_profile = {
       'goal': 'build_muscle',
       'equipment': 'gym',
       'experience': 'advanced',
       'time_per_day': 70, 
       'days_per_week': 6
   }
   plan, conf = predict_plan(advanced_profile)
   print(f"Plan: {plan}, Confidence: {conf:.3f}")

5. MODEL FILES:
   - Trained model: {MODEL_PATH}
   - Training data: {DATA_PATH}
   
Note: The model returns plan IDs (P1-P10). You'll need to map these to 
actual workout plan details using your plans.py or other plan data.
""")

if __name__ == "__main__":
    try:
        # Train the model
        model = train_model()
        
        # Print usage instructions
        print_usage_instructions()
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        raise
