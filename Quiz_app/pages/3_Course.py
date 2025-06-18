"""
Course Display and Quiz Interface - Optimized Version
"""
import streamlit as st
import sys
import os
from typing import Dict, List, Any, Union
import json
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from mongo_course_manager import get_course_manager, get_session_id
    from local_backend import validate_short_answer_with_ai
    MONGO_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    MONGO_AVAILABLE = False
    st.stop()

# Optimized CSS - Reduced and simplified
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%); }
    .main-container { max-width: 900px; margin: 0 auto; padding: 1rem; }
    .section-card { 
        background: rgba(157, 0, 255, 0.1); 
        border: 1px solid #9d00ff; 
        border-radius: 15px; 
        padding: 1.5rem; 
        margin: 1rem 0; 
    }
    .question-card { 
        background: rgba(255, 255, 255, 0.05); 
        border-radius: 10px; 
        padding: 1rem; 
        margin: 0.5rem 0; 
    }
    .stButton > button {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #7a00cc, #5c0099);
        transform: translateY(-1px);
    }
    .score-display {
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with optimized structure
def initialize_session_state():
    """Initialize session state variables efficiently"""
    defaults = {
        "current_section_index": 0,
        "user_answers": {},
        "checked_answers": {},
        "current_score": 0,
        "total_questions_in_course": 0,
        "scored_correctly_keys": set(),
        "feedback": {},
        "course_data": None,
        "current_course_id": None,
        "show_explanation": {},
        "question_states": {},  # Track question interaction states
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Optimized course loading with caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_course_from_db(course_id: str):
    """Load course data with caching"""
    if not MONGO_AVAILABLE:
        return None, "Database not available"
    
    try:
        course_manager = get_course_manager()
        course_data, error = course_manager.get_course(course_id)
        return course_data, error
    except Exception as e:
        return None, str(e)

def load_course_data():
    """Load course data efficiently"""
    course_id = st.query_params.get("course_id") or st.session_state.get("current_course_id")
    
    if not course_id:
        st.error("❌ No course ID provided")
        if st.button("🏠 Go to Home"):
            st.switch_page("pages/1_🏠_Home.py")
        return False
    
    # Use cached loading
    course_data, error = load_course_from_db(course_id)
    
    if error:
        st.error(f"❌ Error loading course: {error}")
        if st.button("🏠 Go to Home"):
            st.switch_page("pages/1_🏠_Home.py")
        return False
    
    if not course_data:
        st.error("❌ Course not found")
        if st.button("🏠 Go to Home"):
            st.switch_page("pages/1_🏠_Home.py")
        return False
    
    # Store in session state only if different
    if st.session_state.course_data != course_data.get('content'):
        st.session_state.course_data = course_data.get('content', [])
        st.session_state.current_course_id = course_id
        st.session_state.total_questions_in_course = count_total_questions(st.session_state.course_data)
    
    return True

def count_total_questions(course_data):
    """Efficiently count total questions"""
    if not course_data:
        return 0
    
    total = 0
    for section in course_data:
        # Count main section questions
        quiz = section.get('quiz', section.get('questions', []))
        total += len(quiz) if isinstance(quiz, list) else 0
        
        # Count subsection questions
        subsections = section.get('subsections', [])
        if isinstance(subsections, list):
            for subsection in subsections:
                sub_quiz = subsection.get('quiz', subsection.get('questions', []))
                total += len(sub_quiz) if isinstance(sub_quiz, list) else 0
    
    return total

def render_question(question, question_key, section_title=""):
    """Render a single question with optimized state management"""
    question_type = question.get('type', '').lower().replace(' ', '_')
    question_text = question.get('question', '')
    
    # Create unique question identifier
    q_id = f"{question_key}_{hash(question_text)}"
    
    # Initialize question state if not exists
    if q_id not in st.session_state.question_states:
        st.session_state.question_states[q_id] = {
            'answered': False,
            'correct': False,
            'show_feedback': False
        }
    
    q_state = st.session_state.question_states[q_id]
    
    with st.container():
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"**❓ {question_text}**")
        
        user_answer = None
        is_correct = False
        
        # Handle different question types efficiently
        if question_type == "multiple_choice":
            user_answer, is_correct = handle_multiple_choice(question, q_id, q_state)
        elif question_type in ["fill_in_the_blank", "fill_in_blank"]:
            user_answer, is_correct = handle_fill_in_blank(question, q_id, q_state)
        elif question_type == "short_answer":
            user_answer, is_correct = handle_short_answer(question, q_id, q_state)
        elif question_type in ["true_false", "true_or_false"]:
            user_answer, is_correct = handle_true_false(question, q_id, q_state)
        elif question_type == "match":
            user_answer, is_correct = handle_matching(question, q_id, q_state)
        
        # Update score efficiently
        if q_state['answered'] and is_correct and q_id not in st.session_state.scored_correctly_keys:
            st.session_state.current_score += 1
            st.session_state.scored_correctly_keys.add(q_id)
        
        st.markdown('</div>', unsafe_allow_html=True)

def handle_multiple_choice(question, q_id, q_state):
    """Handle multiple choice questions"""
    choices = question.get('choices', question.get('options', []))
    correct_answer = question.get('answer', '')
    
    if not choices:
        st.error("No choices provided for multiple choice question")
        return None, False
    
    # Use radio button with unique key
    selected = st.radio(
        "Choose your answer:",
        choices,
        key=f"mc_{q_id}",
        disabled=q_state['answered']
    )
    
    if st.button("Submit Answer", key=f"submit_mc_{q_id}", disabled=q_state['answered']):
        is_correct = selected == correct_answer
        q_state['answered'] = True
        q_state['correct'] = is_correct
        q_state['show_feedback'] = True
        
        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
        
        st.rerun()
    
    return selected, q_state.get('correct', False)

def handle_fill_in_blank(question, q_id, q_state):
    """Handle fill in the blank questions"""
    correct_answer = question.get('answer', '')
    
    # Use simple text input instead of custom component for better performance
    user_input = st.text_input(
        "Fill in the blank:",
        key=f"fitb_{q_id}",
        disabled=q_state['answered'],
        placeholder="Type your answer here..."
    )
    
    if st.button("Submit Answer", key=f"submit_fitb_{q_id}", disabled=q_state['answered']):
        # Handle multiple correct answers
        if isinstance(correct_answer, list):
            is_correct = any(user_input.lower().strip() == ans.lower().strip() for ans in correct_answer)
            display_answer = " or ".join(correct_answer)
        else:
            is_correct = user_input.lower().strip() == correct_answer.lower().strip()
            display_answer = correct_answer
        
        q_state['answered'] = True
        q_state['correct'] = is_correct
        q_state['show_feedback'] = True
        
        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer is: {display_answer}")
        
        st.rerun()
    
    return user_input, q_state.get('correct', False)

def handle_short_answer(question, q_id, q_state):
    """Handle short answer questions with simplified validation"""
    correct_answer = question.get('answer', '')
    
    user_input = st.text_area(
        "Your answer:",
        key=f"sa_{q_id}",
        disabled=q_state['answered'],
        height=100
    )
    
    if st.button("Submit Answer", key=f"submit_sa_{q_id}", disabled=q_state['answered']):
        # Simplified validation - just check if answer contains key terms
        if isinstance(correct_answer, list):
            is_correct = any(ans.lower() in user_input.lower() for ans in correct_answer)
            display_answer = " or ".join(correct_answer)
        else:
            is_correct = correct_answer.lower() in user_input.lower()
            display_answer = correct_answer
        
        q_state['answered'] = True
        q_state['correct'] = is_correct
        q_state['show_feedback'] = True
        
        if is_correct:
            st.success("✅ Good answer!")
        else:
            st.info(f"💡 Expected answer: {display_answer}")
        
        st.rerun()
    
    return user_input, q_state.get('correct', False)

def handle_true_false(question, q_id, q_state):
    """Handle true/false questions"""
    correct_answer = question.get('answer', False)
    
    # Convert string answers to boolean
    if isinstance(correct_answer, str):
        correct_answer = correct_answer.lower() in ['true', 'yes', '1']
    
    selected = st.radio(
        "Choose your answer:",
        [True, False],
        format_func=lambda x: "True" if x else "False",
        key=f"tf_{q_id}",
        disabled=q_state['answered']
    )
    
    if st.button("Submit Answer", key=f"submit_tf_{q_id}", disabled=q_state['answered']):
        is_correct = selected == correct_answer
        q_state['answered'] = True
        q_state['correct'] = is_correct
        q_state['show_feedback'] = True
        
        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer is: {'True' if correct_answer else 'False'}")
        
        st.rerun()
    
    return selected, q_state.get('correct', False)

def handle_matching(question, q_id, q_state):
    """Handle matching questions with simplified interface"""
    correct_matches = question.get('answer', {})
    
    if not isinstance(correct_matches, dict):
        st.error("Invalid matching question format")
        return None, False
    
    items = list(correct_matches.keys())
    options = list(correct_matches.values())
    
    st.write("Match each item with its correct answer:")
    
    user_matches = {}
    for i, item in enumerate(items):
        selected = st.selectbox(
            f"{item}:",
            ["Select..."] + options,
            key=f"match_{q_id}_{i}",
            disabled=q_state['answered']
        )
        if selected != "Select...":
            user_matches[item] = selected
    
    if st.button("Submit Answer", key=f"submit_match_{q_id}", disabled=q_state['answered']):
        correct_count = sum(1 for item, answer in user_matches.items() 
                          if correct_matches.get(item) == answer)
        is_correct = correct_count == len(correct_matches)
        
        q_state['answered'] = True
        q_state['correct'] = is_correct
        q_state['show_feedback'] = True
        
        if is_correct:
            st.success("✅ All matches correct!")
        else:
            st.error(f"❌ {correct_count}/{len(correct_matches)} matches correct")
            st.info("Correct matches:")
            for item, answer in correct_matches.items():
                st.write(f"• {item} → {answer}")
        
        st.rerun()
    
    return user_matches, q_state.get('correct', False)

def render_section(section_data, section_index):
    """Render a section with optimized performance"""
    section_title = section_data.get('section_title', section_data.get('section', f'Section {section_index + 1}'))
    explanation = section_data.get('explanation', '')
    questions = section_data.get('quiz', section_data.get('questions', []))
    
    st.markdown(f'<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f"## 📚 {section_title}")
    
    if explanation:
        st.markdown(f"**📖 Overview:**")
        st.markdown(explanation)
    
    # Render questions
    if questions:
        st.markdown("---")
        st.markdown("### 🧠 Quiz Questions")
        
        for i, question in enumerate(questions):
            question_key = f"section_{section_index}_question_{i}"
            render_question(question, question_key, section_title)
    
    # Handle subsections
    subsections = section_data.get('subsections', [])
    if subsections:
        st.markdown("---")
        st.markdown("### 📑 Subsections")
        
        for sub_i, subsection in enumerate(subsections):
            with st.expander(f"📄 {subsection.get('section_title', subsection.get('section', f'Subsection {sub_i + 1}'))}"):
                sub_explanation = subsection.get('explanation', '')
                if sub_explanation:
                    st.markdown(sub_explanation)
                
                sub_questions = subsection.get('quiz', subsection.get('questions', []))
                if sub_questions:
                    for sub_q_i, question in enumerate(sub_questions):
                        question_key = f"section_{section_index}_subsection_{sub_i}_question_{sub_q_i}"
                        render_question(question, question_key, section_title)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main function with optimized flow"""
    st.set_page_config(
        page_title="Course - Learnify",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    initialize_session_state()
    
    # Load course data
    if not load_course_data():
        return
    
    course_data = st.session_state.course_data
    if not course_data:
        st.error("❌ No course content available")
        return
    
    # Header with navigation
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
    
    with col2:
        # Score display
        total_questions = st.session_state.total_questions_in_course
        current_score = st.session_state.current_score
        if total_questions > 0:
            score_percentage = (current_score / total_questions) * 100
            st.markdown(f'''
                <div class="score-display">
                    🎯 Score: {current_score}/{total_questions} ({score_percentage:.1f}%)
                </div>
            ''', unsafe_allow_html=True)
    
    with col3:
        # Share button
        if st.button("🔗 Share", use_container_width=True):
            share_url = f"{st.get_option('browser.serverAddress')}:{st.get_option('server.port')}/?course_id={st.session_state.current_course_id}"
            st.code(share_url)
    
    # Main content
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Section navigation
    current_index = st.session_state.current_section_index
    total_sections = len(course_data)
    
    # Navigation controls
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        if current_index > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_section_index -= 1
                st.rerun()
    
    with nav_col2:
        st.markdown(f"<div style='text-align: center; padding: 10px;'><strong>Section {current_index + 1} of {total_sections}</strong></div>", unsafe_allow_html=True)
    
    with nav_col3:
        if current_index < total_sections - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_section_index += 1
                st.rerun()
    
    # Render current section
    if 0 <= current_index < len(course_data):
        render_section(course_data[current_index], current_index)
    
    # Progress bar
    progress = (current_index + 1) / total_sections
    st.progress(progress)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()