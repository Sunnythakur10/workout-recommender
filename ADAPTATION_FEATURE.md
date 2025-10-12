# 📅 Workout Plan Adaptation Feature

## Overview

The workout recommender now includes smart plan adaptation that allows users to customize their weekly training schedule based on their preferred number of workout days per week.

## 🚀 New Functionality

### `adapt_week_plan()` Function

**Location:** `model_utils.py`

**Purpose:** Adapts a 7-day workout plan template to a user-specified number of training days per week, with intelligent distribution of workouts across the week.

### Key Features

1. **Even Distribution**: Training days are spread evenly across the week to avoid clustering workouts together
2. **Rest Day Management**: Non-training days can be marked as rest days or removed entirely
3. **Flexible Scheduling**: Supports 1-7 training days per week
4. **Deterministic Results**: Same inputs always produce same outputs (no randomness)
5. **Error Handling**: Graceful handling of edge cases and invalid inputs

## 🎯 How It Works

### Algorithm

1. **Input Validation**: Checks for valid `days_per_week` (>0) and proper plan structure
2. **Distribution Calculation**: Uses mathematical spacing to select training days evenly across the week
3. **Index Selection**: Selects specific days from the original 7-day template
4. **Schedule Building**: Creates final schedule with training days and optional rest days

### Examples

```python
# Original 7-day plan
original_plan = {
    'week': [
        {'day': 1, 'focus': 'Upper Body', 'exercises': ['Push Up']},
        {'day': 2, 'focus': 'Lower Body', 'exercises': ['Squat']},
        {'day': 3, 'focus': 'Cardio', 'exercises': ['Running']},
        {'day': 4, 'focus': 'Upper Body', 'exercises': ['Pull Up']},
        {'day': 5, 'focus': 'Lower Body', 'exercises': ['Deadlift']},
        {'day': 6, 'focus': 'Full Body', 'exercises': ['Burpee']},
        {'day': 7, 'focus': 'Cardio', 'exercises': ['Cycling']}
    ]
}

# Adapt to 4 days per week
adapted = adapt_week_plan(original_plan, 4, keep_rest_days=True)
# Result: Days 1, 3, 5, 7 as training days, others as rest days

# Adapt to 3 days per week (training days only)
adapted = adapt_week_plan(original_plan, 3, keep_rest_days=False)
# Result: Only 3 training days returned
```

## 📱 UI Integration

### Streamlit App Changes

1. **Automatic Adaptation**: Plans are automatically adapted based on the user's "Days per Week" slider setting
2. **Updated Statistics**: Plan statistics reflect the adapted schedule
3. **Clear Labeling**: Rest days are clearly marked in the weekly schedule
4. **Seamless Experience**: Users see their preferred schedule without additional steps

### User Experience

- **Input**: User sets "Days per Week" slider (3-7 days typically)
- **Processing**: App automatically adapts the AI-recommended plan
- **Output**: User sees customized weekly schedule matching their preference
- **Flexibility**: Can regenerate with different day preferences instantly

## 🧪 Testing

### Automated Tests

The implementation includes comprehensive testing:

- ✅ **Unit Tests**: Basic functionality validation
- ✅ **Integration Tests**: Real plan template testing
- ✅ **Edge Cases**: Minimal plans, error conditions
- ✅ **Error Handling**: Invalid inputs, missing data

### Test Coverage

- Days per week: 1-7 and beyond (clamping)
- Plan sizes: Full 7-day, partial, empty
- Rest day modes: With/without rest days
- Error conditions: Invalid inputs, missing keys

## 📊 Benefits

### For Users

1. **Flexibility**: Match workout schedule to available time
2. **Realistic Planning**: Avoid overcommitting to too many workout days
3. **Better Adherence**: Plans match actual lifestyle constraints
4. **Progressive Training**: Start with fewer days, increase over time

### For Trainers/Coaches

1. **Customization**: Easy adaptation of standard templates
2. **Client Management**: Different schedules for different clients
3. **Program Progression**: Systematic increase in training frequency
4. **Retention**: More achievable plans lead to better client outcomes

## 🔧 Technical Details

### Function Signature

```python
def adapt_week_plan(
    plan: dict, 
    days_per_week: int, 
    keep_rest_days: bool = True
) -> list:
```

### Parameters

- `plan`: Plan dictionary with 'week' key containing 7-day list
- `days_per_week`: Desired number of training days (1-7)
- `keep_rest_days`: Whether to include rest days in result (bool)

### Return Value

- If `keep_rest_days=True`: 7-element list with training + rest days
- If `keep_rest_days=False`: N-element list with only training days

### Dependencies

- Standard Python libraries only (no external dependencies)
- Compatible with existing plan structure
- Pure function (no side effects)

## 🚀 Future Enhancements

### Potential Improvements

1. **Custom Rest Day Placement**: Allow users to specify preferred rest days
2. **Workout Intensity Balancing**: Ensure high/low intensity days are distributed
3. **Body Part Rotation**: Optimize muscle group targeting across selected days
4. **Progressive Overload**: Automatic adjustment of volume based on frequency
5. **Calendar Integration**: Respect user's actual available days

### Advanced Features

1. **Multi-Week Periodization**: Vary days per week across training phases
2. **Deload Week Support**: Automatic reduction in training days for recovery
3. **Sport-Specific Scheduling**: Adapt based on competition/practice schedules
4. **Recovery Optimization**: Intelligent rest day placement based on workout intensity

## 📝 Usage Examples

### Basic Usage

```python
import model_utils

# Get a plan
plan = model_utils.get_plan_template('P1')

# Adapt to 4 days per week
adapted = model_utils.adapt_week_plan(plan, 4)

# Use in Streamlit app
for day in adapted:
    if day['focus'] == 'Rest Day':
        st.write(f"Day {day['day']}: Rest Day 😴")
    else:
        st.write(f"Day {day['day']}: {day['focus']} 💪")
```

### Advanced Usage

```python
# Different scenarios
scenarios = [
    (3, True, "Beginner: 3 days + rest days"),
    (4, True, "Intermediate: 4 days + rest days"),
    (5, False, "Advanced: 5 training days only"),
    (7, True, "Elite: Full 7-day program")
]

for days, keep_rest, description in scenarios:
    adapted = model_utils.adapt_week_plan(plan, days, keep_rest)
    print(f"{description}: {len(adapted)} days total")
```

---

*This feature enhances the workout recommender's flexibility and user experience by providing intelligent plan adaptation based on individual scheduling preferences.*