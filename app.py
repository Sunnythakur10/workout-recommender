"""
Workout Recommender Streamlit App

This app provides an interactive interface for:
- Getting personalized workout recommendations based on user profile
- Viewing detailed workout plans with exercises
- Personalizing plans based on exercise preferences
- Regenerating plan variations
"""

import streamlit as st
import pandas as pd
import os
from typing import List, Dict, Any

# Import our model utilities
try:
    import model_utils
except ImportError:
    st.error("❌ Could not import model_utils.py. Make sure it exists in the same directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Workout Recommender",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Exercise card styling */
    .exercise-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 0.75rem;
        margin: 0.75rem 0;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    .exercise-card strong {
        color: #1a237e !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }
    .exercise-card p {
        color: #2c3e50 !important;
    }
    .exercise-card .stCaption {
        color: #5a6c7d !important;
        font-weight: 500 !important;
    }
    
    /* Day header styling */
    .day-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 1.25rem;
        border-radius: 0.75rem;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    .day-header h3 {
        color: white !important;
        margin: 0 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* Plan info styling - improved visibility */
    .plan-info {
        background: linear-gradient(135deg, #48a9d9 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #e3f2fd;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        margin: 1.5rem 0;
        position: relative;
    }
    .plan-info::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 6px;
        background: linear-gradient(to bottom, #4caf50, #2196f3);
        border-radius: 6px 0 0 6px;
    }
    .plan-info h3 {
        color: #1a237e !important;
        margin-bottom: 1.2rem !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    .plan-info p {
        color: #263238 !important;
        font-size: 1rem !important;
        margin: 0.8rem 0 !important;
        line-height: 1.7 !important;
        font-weight: 500 !important;
    }
    .plan-info strong {
        color: #1a237e !important;
        font-weight: 700 !important;
    }
    
    /* Confidence badges - enhanced visibility */
    .confidence-high { 
        color: #1b5e20 !important; 
        font-weight: bold; 
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        padding: 0.3rem 0.7rem;
        border-radius: 0.5rem;
        border: 1px solid #4caf50;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }
    .confidence-medium { 
        color: #e65100 !important; 
        font-weight: bold; 
        background: linear-gradient(135deg, #ffe0b2, #ffcc02);
        padding: 0.3rem 0.7rem;
        border-radius: 0.5rem;
        border: 1px solid #ff9800;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }
    .confidence-low { 
        color: #b71c1c !important; 
        font-weight: bold; 
        background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
        padding: 0.3rem 0.7rem;
        border-radius: 0.5rem;
        border: 1px solid #f44336;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }
    
    /* Global text improvements for entire website - LIGHT COLORS FOR DARK THEME */
    .stMarkdown p {
        color: #ffffff !important;
        font-weight: 400 !important;
    }
    .stMarkdown strong {
        color: #64b5f6 !important;
        font-weight: 700 !important;
    }
    
    /* Main content text styling */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #81c784 !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar text improvements */
    .stSidebar .stMarkdown p {
        color: #ffffff !important;
    }
    .stSidebar .stMarkdown strong {
        color: #64b5f6 !important;
    }
    .stSidebar label {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    
    /* Button text */
    .stButton button {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Input labels and help text */
    .stSelectbox label, .stSlider label, .stMultiSelect label {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    
    /* Caption text */
    .stCaption {
        color: #b0bec5 !important;
    }
    
    /* Tab text */
    .stTabs [data-baseweb="tab-list"] button {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #81c784 !important;
        font-weight: 700 !important;
    }
    
    /* Metric text */
    .stMetric label {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    .stMetric [data-testid="metric-value"] {
        color: #81c784 !important;
        font-weight: 700 !important;
    }
    
    /* Info, success, warning, error text */
    .stInfo, .stSuccess, .stWarning, .stError {
        color: #ffffff !important;
    }
    
    /* Expander text */
    .stExpander details summary {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    
    /* Additional comprehensive text styling */
    .stApp {
        color: #ffffff !important;
    }
    
    /* Ensure all paragraph text has good contrast */
    p, span, div {
        color: #ffffff !important;
    }
    
    /* List items */
    li {
        color: #ffffff !important;
    }
    
    /* Table text */
    .stDataFrame, .stTable {
        color: #ffffff !important;
    }
    
    /* Code blocks */
    .stCode {
        color: #ffffff !important;
    }
    
    /* Checkbox and radio text */
    .stCheckbox label, .stRadio label {
        color: #e8eaf6 !important;
        font-weight: 500 !important;
    }
    
    /* Text input labels */
    .stTextInput label, .stTextArea label, .stNumberInput label {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    
    /* Ensure headers in containers are visible */
    .stContainer h1, .stContainer h2, .stContainer h3, .stContainer h4, .stContainer h5, .stContainer h6 {
        color: #81c784 !important;
        font-weight: 700 !important;
    }
    
    /* Progress bar text */
    .stProgress .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Spinner text */
    .stSpinner .stMarkdown {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Main app title styling */
    .stApp > div > div > div > div > h1 {
        color: #81c784 !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin-bottom: 0.5rem !important;
    }
    
    /* Main app description styling */
    .stApp > div > div > div > div > div > .stMarkdown:first-of-type p {
        color: #b0bec5 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin-bottom: 2rem !important;
    }
    
    /* Profile summary section headers */
    .stMarkdown h3 {
        color: #81c784 !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #455a64;
        padding-bottom: 0.5rem;
    }
    
    /* Additional overrides for dark theme compatibility */
    .stApp, .stApp * {
        color: #ffffff !important;
    }
    
    /* Specific overrides for components on light backgrounds */
    .exercise-card, .exercise-card * {
        color: #2c3e50 !important;
    }
    .exercise-card strong {
        color: #1a237e !important;
    }
    
    .plan-info, .plan-info * {
        color: #263238 !important;
    }
    .plan-info h3, .plan-info strong {
        color: #1a237e !important;
    }
    
    /* Confidence badges remain as they have their own backgrounds */
    .confidence-high, .confidence-medium, .confidence-low {
        /* Keep existing colors as they have colored backgrounds */
    }
    
    /* Input fields and form elements */
    .stSelectbox > div, .stSlider > div, .stMultiSelect > div {
        color: #ffffff !important;
    }
    
    /* Ensure button text remains visible */
    .stButton > button {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_exercises():
    """Load exercises data with caching."""
    try:
        if os.path.exists("data/exercises_reduced.csv"):
            df = pd.read_csv("data/exercises_reduced.csv")
            return df['name'].unique().tolist()
        else:
            # Fallback exercise list
            return [
                "Push Up", "Bodyweight Squat", "Plank", "Jumping Jacks", 
                "Burpee", "Mountain Climbers", "Lunges", "Side Plank",
                "Pull Up", "Dips", "Bench Press", "Deadlift", "Squat"
            ]
    except Exception as e:
        st.warning(f"Could not load exercises: {e}")
        return []

@st.cache_data
def get_image_statistics():
    """Get statistics about available exercise images."""
    try:
        if os.path.exists("data/exercises_reduced.csv"):
            df = pd.read_csv("data/exercises_reduced.csv")
            total_exercises = len(df)
            
            # Count exercises with actual image URLs
            has_images = df['gif_url'].notna() & (df['gif_url'].astype(str).str.strip() != '') & (df['gif_url'].astype(str).str.strip().str.lower() != 'nan')
            images_available = has_images.sum()
            
            return {
                'total': total_exercises,
                'with_images': images_available,
                'percentage': (images_available / total_exercises * 100) if total_exercises > 0 else 0
            }
        else:
            return {'total': 0, 'with_images': 0, 'percentage': 0}
    except Exception as e:
        return {'total': 0, 'with_images': 0, 'percentage': 0}

@st.cache_data
def get_model_status():
    """Check model availability with caching."""
    try:
        model_info = model_utils.get_model_info()
        return model_info['model_loaded']
    except:
        return False

def format_confidence(confidence: float) -> str:
    """Format confidence with color coding."""
    percentage = confidence * 100
    if percentage >= 80:
        return f'<span class="confidence-high">{percentage:.1f}%</span>'
    elif percentage >= 60:
        return f'<span class="confidence-medium">{percentage:.1f}%</span>'
    else:
        return f'<span class="confidence-low">{percentage:.1f}%</span>'

def render_exercise_card(exercise: Dict[str, Any], show_images: bool = True):
    """Render an individual exercise card."""
    
    with st.container():
        st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{exercise.get('name', 'Unknown Exercise')}**")
            
            # Exercise details
            details = []
            if exercise.get('sets'):
                details.append(f"Sets: {exercise['sets']}")
            if exercise.get('reps'):
                details.append(f"Reps: {exercise['reps']}")
            if exercise.get('body_part'):
                details.append(f"Target: {exercise['body_part'].title()}")
            if exercise.get('equipment'):
                details.append(f"Equipment: {exercise['equipment'].title()}")
            
            if details:
                st.caption(" • ".join(details))
        
        with col2:
            # Show GIF if available and enabled
            if show_images:
                if exercise.get('gif_url') and pd.notna(exercise['gif_url']) and str(exercise['gif_url']).strip() and str(exercise['gif_url']).strip().lower() != 'nan':
                    try:
                        st.image(exercise['gif_url'], width=100, caption="Exercise Demo")
                        st.caption("🎬 GIF loaded")
                    except Exception as e:
                        st.caption("❌ GIF failed to load")
                        st.caption(f"URL: {exercise['gif_url'][:30]}...")
                else:
                    st.caption("📷 No image available")
            else:
                st.caption("💪 Exercise")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_day_plan(day_data: Dict[str, Any], show_images: bool = True):
    """Render a single day's workout plan."""
    
    # Day header
    day_num = day_data.get('day', 'Unknown')
    focus = day_data.get('focus', 'General workout')
    
    st.markdown(f'''
    <div class="day-header">
        <h3>Day {day_num}: {focus.title()}</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Exercises for this day
    exercises = day_data.get('exercises', [])
    
    if exercises:
        for i, exercise in enumerate(exercises, 1):
            st.markdown(f"**Exercise {i}:**")
            render_exercise_card(exercise, show_images)
    else:
        st.info("No exercises scheduled for this day.")

def main():
    """Main Streamlit app."""
    
    # App header
    st.title("💪 Workout Recommender")
    st.markdown("Get personalized workout plans based on your fitness goals and preferences!")
    
    # Check if model is available
    if not get_model_status():
        st.error("❌ **Model not found!** Please run `train.py` first to train the recommendation model.")
        st.stop()
    
    # Sidebar for user inputs
    st.sidebar.header("🎯 Your Profile")
    
    # Basic profile inputs
    goal = st.sidebar.selectbox(
        "Fitness Goal:",
        options=["build_muscle", "lose_weight", "endurance", "flexibility"],
        format_func=lambda x: {
            "build_muscle": "🏋️ Build Muscle",
            "lose_weight": "🔥 Lose Weight", 
            "endurance": "🏃 Endurance",
            "flexibility": "🧘 Flexibility"
        }[x]
    )
    
    equipment = st.sidebar.selectbox(
        "Available Equipment:",
        options=["none", "basic", "gym"],
        format_func=lambda x: {
            "none": "🏠 No Equipment (Bodyweight)",
            "basic": "🏋️‍♀️ Basic Equipment", 
            "gym": "🏟️ Full Gym Access"
        }[x]
    )
    
    experience = st.sidebar.selectbox(
        "Experience Level:",
        options=["beginner", "intermediate", "advanced"],
        format_func=lambda x: {
            "beginner": "🌱 Beginner",
            "intermediate": "💪 Intermediate",
            "advanced": "🚀 Advanced"
        }[x]
    )
    
    time_per_day = st.sidebar.slider(
        "Time Available (minutes/day):",
        min_value=15,
        max_value=90,
        value=45,
        step=5
    )
    
    days_per_week = st.sidebar.slider(
        "Days per Week:",
        min_value=3,
        max_value=6,
        value=4
    )
    
    # Exercise preferences
    st.sidebar.header("🎪 Exercise Preferences")
    
    # Load available exercises
    available_exercises = load_exercises()
    
    if available_exercises:
        liked_exercises = st.sidebar.multiselect(
            "Exercises you like:",
            options=available_exercises,
            help="Select exercises you enjoy or want to include"
        )
        
        disliked_exercises = st.sidebar.multiselect(
            "Exercises to avoid:",
            options=available_exercises,
            help="Select exercises you want to avoid or replace"
        )
    else:
        liked_exercises = []
        disliked_exercises = []
        st.sidebar.warning("Could not load exercise list")
    
    # Display options
    st.sidebar.header("🎨 Display Options")
    show_images = st.sidebar.checkbox(
        "Show exercise images/GIFs", 
        value=True,
        help="Toggle to show/hide exercise demonstration images when available"
    )
    
    # Show status of image display and statistics
    image_stats = get_image_statistics()
    
    if show_images:
        st.sidebar.success("📷 Images enabled")
        if image_stats['with_images'] > 0:
            st.sidebar.info(f"🖼️ {image_stats['with_images']}/{image_stats['total']} exercises have images ({image_stats['percentage']:.1f}%)")
        else:
            st.sidebar.warning("⚠️ No exercise images found in database")
    else:
        st.sidebar.info("📷 Images disabled")
    
    # Create user profile
    user_profile = {
        'goal': goal,
        'equipment': equipment,
        'experience': experience,
        'time_per_day': time_per_day,
        'days_per_week': days_per_week
    }
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 📋 Your Profile Summary")
        st.markdown(f"🎯 **Goal:** {goal.replace('_', ' ').title()}")
        st.markdown(f"🏋️ **Equipment:** {equipment.title()}")
        st.markdown(f"📈 **Experience:** {experience.title()}")
        st.markdown(f"⏱️ **Time:** {time_per_day} min/day")
        st.markdown(f"📅 **Frequency:** {days_per_week} days/week")
        
        if liked_exercises:
            st.markdown(f"❤️ **Likes:** {', '.join(liked_exercises[:3])}{'...' if len(liked_exercises) > 3 else ''}")
        if disliked_exercises:
            st.markdown(f"❌ **Avoids:** {', '.join(disliked_exercises[:3])}{'...' if len(disliked_exercises) > 3 else ''}")
    
    with col1:
        # Generate Plan button
        if st.button("🚀 Generate Workout Plan", type="primary", use_container_width=True):
            
            with st.spinner("🤖 Analyzing your profile and generating plan..."):
                try:
                    # Get prediction
                    plan_id, confidence = model_utils.predict_plan(user_profile)
                    
                    # Store in session state
                    st.session_state.current_plan_id = plan_id
                    st.session_state.current_confidence = confidence
                    st.session_state.user_profile = user_profile
                    st.session_state.liked_exercises = liked_exercises
                    st.session_state.disliked_exercises = disliked_exercises
                    
                    # Get plan template
                    plan_template = model_utils.get_plan_template(plan_id)
                    st.session_state.current_plan = plan_template
                    
                except Exception as e:
                    st.error(f"❌ Error generating plan: {str(e)}")
                    return
        
        # Regenerate variation button (only show if plan exists)
        if hasattr(st.session_state, 'current_plan'):
            if st.button("🔄 Regenerate with Preferences", use_container_width=True):
                
                with st.spinner("🎨 Personalizing your workout plan..."):
                    try:
                        # Personalize the plan
                        personalized_plan = model_utils.personalize_plan(
                            st.session_state.current_plan,
                            liked_exercises=liked_exercises,
                            disliked_exercises=disliked_exercises
                        )
                        st.session_state.current_plan = personalized_plan
                        
                        st.success("✅ Plan personalized based on your preferences!")
                        
                    except Exception as e:
                        st.error(f"❌ Error personalizing plan: {str(e)}")
    
    # Display current plan if available
    if hasattr(st.session_state, 'current_plan'):
        
        plan = st.session_state.current_plan
        plan_id = st.session_state.current_plan_id
        confidence = st.session_state.current_confidence
        
        # Plan info section
        st.markdown("---")
        st.markdown("## 📋 Your Recommended Workout Plan")
        
        # Plan summary
        st.markdown(f'''
        <div class="plan-info">
            <h3>🎯 {plan['meta']['name']}</h3>
            <p><strong>Plan ID:</strong> {plan_id} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>AI Confidence:</strong> {format_confidence(confidence)}</p>
            <p><strong>🎯 Target:</strong> {plan['meta']['goal'].replace('_', ' ').title()}</p>
            <p><strong>🏋️ Equipment:</strong> {plan['meta']['equipment'].title()} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>📈 Level:</strong> {plan['meta']['experience'].title()}</p>
            <p><strong>⏱️ Duration:</strong> {plan['meta']['time_per_day']} min/session &nbsp;&nbsp;|&nbsp;&nbsp; <strong>📅 Schedule:</strong> {len([d for d in plan['week'] if d.get('exercises')])} active days</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Plan explanation
        with st.expander("📖 Why this plan?", expanded=False):
            confidence_text = "high" if confidence > 0.8 else "moderate" if confidence > 0.6 else "lower"
            st.markdown(f"""
            Based on your profile, our AI model recommends **{plan['meta']['name']}** with 
            {confidence_text} confidence ({confidence:.1%}).
            
            This plan is designed for:
            - **Goal:** {plan['meta']['goal'].replace('_', ' ').title()}
            - **Equipment:** {plan['meta']['equipment'].title()} equipment access
            - **Experience:** {plan['meta']['experience'].title()} level
            - **Duration:** {plan['meta']['time_per_day']} minutes per session
            
            The plan includes {len(plan['week'])} days of structured workouts targeting your specific goals.
            """)
        
        # Weekly plan display
        st.markdown("### 📅 7-Day Workout Schedule")
        
        # Create tabs for each day
        day_tabs = st.tabs([f"Day {i+1}" for i in range(len(plan['week']))])
        
        for i, (tab, day_data) in enumerate(zip(day_tabs, plan['week'])):
            with tab:
                render_day_plan(day_data, show_images)
        
        # Summary statistics
        with st.expander("📊 Plan Statistics", expanded=False):
            total_exercises = sum(len(day.get('exercises', [])) for day in plan['week'])
            active_days = len([day for day in plan['week'] if day.get('exercises')])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Exercises", total_exercises)
            with col2:
                st.metric("Active Days", active_days)
            with col3:
                st.metric("Rest Days", 7 - active_days)
            
            # Exercise breakdown by body part
            body_parts = {}
            for day in plan['week']:
                for exercise in day.get('exercises', []):
                    part = exercise.get('body_part', 'unknown')
                    body_parts[part] = body_parts.get(part, 0) + 1
            
            if body_parts:
                st.markdown("**Exercise Distribution by Body Part:**")
                for part, count in sorted(body_parts.items()):
                    st.markdown(f"- {part.title()}: {count} exercises")

if __name__ == "__main__":
    main()
