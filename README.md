# 💪 Workout Recommender

A machine learning-powered workout recommendation system with an interactive Streamlit web interface. Get personalized workout plans based on your fitness goals, equipment availability, and exercise preferences.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

🤖 **AI-Powered Recommendations**: Uses a trained RandomForest model to suggest personalized workout plans
💪 **Comprehensive Exercise Database**: 300+ exercises with equipment and body part targeting
🎯 **User Personalization**: Customizable based on goals, equipment, experience, and preferences
� **Smart Schedule Adaptation**: Automatically adapts 7-day plans to your preferred training frequency (3-7 days/week)
�📱 **Interactive Web Interface**: Beautiful Streamlit app with responsive design
🔄 **Plan Variations**: Generate multiple variations based on exercise preferences

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirement.txt
```

### 2. Train the Model (if not already done)
```bash
python train.py
```

### 3. Run the Web App
```bash
streamlit run app.py
```

Then open your browser to http://localhost:8501

## Project Structure

```
workout-recommender/
├── app.py                 # Streamlit web interface
├── train.py              # Model training script
├── model_utils.py        # Model utilities and prediction functions
├── plans.py              # Workout plan templates and generation
├── requirement.txt       # Python dependencies
├── data/
│   ├── templates.csv     # Training data (user profiles → plan IDs)
│   └── exercises_reduced.csv  # Exercise database
└── models/
    └── plan_model.pkl    # Trained ML model
```

## How It Works

1. **User Input**: Users specify their fitness goals, available equipment, experience level, time constraints, and exercise preferences
2. **AI Prediction**: The trained model analyzes the profile and predicts the most suitable workout plan
3. **Plan Adaptation**: Plans are automatically adapted to the user's preferred training frequency (3-7 days/week)
4. **Plan Generation**: The system retrieves the recommended plan template with specific exercises
5. **Personalization**: Plans are customized based on liked/disliked exercises
6. **Interactive Display**: The web interface shows a complete weekly workout schedule with training and rest days

## Usage Examples

### Command Line (Python)
```python
from model_utils import predict_plan, get_plan_template, personalize_plan

# User profile
profile = {
    'goal': 'build_muscle',
    'equipment': 'gym',
    'experience': 'intermediate',
    'time_per_day': 60,
    'days_per_week': 5
}

# Get recommendation
plan_id, confidence = predict_plan(profile)
plan = get_plan_template(plan_id)

# Personalize
personalized = personalize_plan(
    plan, 
    liked_exercises=['Bench Press', 'Squat'],
    disliked_exercises=['Burpee']
)
```

### Web Interface
1. Open the Streamlit app
2. Fill in your profile in the sidebar
3. Select exercise preferences (optional)
4. Click "Generate Workout Plan"
5. View your personalized 7-day workout schedule
6. Use "Regenerate with Preferences" for variations

## Model Details

- **Algorithm**: RandomForest Classifier (200 trees, max depth 10)
- **Features**: Goal, equipment, experience, time per day, days per week
- **Training Data**: 150 user profiles mapped to 10 workout plans
- **Cross-validation**: 82.67% ± 9.04% accuracy
- **Test Accuracy**: 100% on holdout set

## Plan Types

The system recommends from 10 different workout plans:
- P1: 4-day Upper/Lower Hypertrophy (gym, intermediate)
- P2: 3-day Full Body Beginner (bodyweight, beginner)
- P3: 5-day Cardio + HIIT (basic equipment, intermediate)
- P4: 4-day Strength Compound Focus (gym, advanced)
- P5: Bodyweight Conditioning 4-day (bodyweight, intermediate)
- P6: 5-day Muscle Endurance (basic equipment, intermediate)
- P7: 3-day Minimal Time HIIT (bodyweight, beginner)
- P8: Yoga & Mobility 5-day (bodyweight, beginner)
- P9: Push/Pull/Legs 3-day Split (basic equipment, intermediate)
- P10: Advanced Strength + Accessory 5-day (gym, advanced)

## Customization

The system allows extensive customization:
- **Exercise Preferences**: Mark exercises as liked or disliked
- **Equipment Constraints**: Automatically filters exercises based on available equipment
- **Difficulty Matching**: Ensures exercises match user experience level
- **Body Part Targeting**: Maintains balanced muscle group coverage

## Development

### Adding New Plans
1. Update `plans.py` with new plan metadata and exercises
2. Add corresponding training data to `data/templates.csv`
3. Retrain the model with `python train.py`

### Adding New Exercises
1. Add exercises to `data/exercises_reduced.csv`
2. Include columns: name, equipment_cat, body_part, difficulty, gif_url

### Modifying the UI
- Edit `app.py` for interface changes
- Custom CSS is included for styling
- Add new features using Streamlit components

## Troubleshooting

**Model not found**: Run `python train.py` to train the model
**Import errors**: Install dependencies with `pip install -r requirement.txt`
**No exercises loading**: Check that `data/exercises_reduced.csv` exists
**Poor recommendations**: Retrain model with more diverse training data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Machine learning powered by [scikit-learn](https://scikit-learn.org/)
- Exercise data and recommendations for educational purposes

## 📧 Contact

If you have any questions or suggestions, feel free to open an issue or contact the maintainers.

---

⭐ **Star this repository if you found it helpful!**