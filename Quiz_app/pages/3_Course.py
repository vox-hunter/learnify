"""
Course Page - Simplified course viewing and quiz interface
"""
import streamlit as st
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Minimal CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton > button {
        background-color: #0066cc !important;
        color: white !important;
        border-radius: 5px !important;
    }
    .question-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📚 Course")
    
    # Get course data
    course_data = get_current_course_data()
    
    if not course_data:
        st.error("No course data found")
        if st.button("Go to Home"):
            st.switch_page("pages/1_🏠_Home.py")
        return
    
    # Course navigation
    show_course_navigation(course_data)
    
    # Display current section  
    current_section = st.session_state.get('current_section', 0)
    sections = course_data.get('sections', [])
    
    if sections and current_section < len(sections):
        display_section(sections[current_section], current_section)
    
    # Show progress
    show_progress(course_data)

def get_current_course_data():
    """Get course data from session state or URL params"""
    # Try session state first
    if 'current_course' in st.session_state:
        return st.session_state['current_course']
    
    # Try to load from MongoDB if course_id in URL
    course_id = st.query_params.get('course_id')
    if course_id:
        try:
            from mongo_course_manager import get_course_manager
            course_mgr = get_course_manager()
            if course_mgr:
                course = course_mgr.get_course(course_id)
                if course:
                    st.session_state['current_course'] = course
                    return course
        except Exception as e:
            st.error(f"Error loading course: {e}")
    
    return None

def show_course_navigation(course_data):
    """Show course navigation controls"""
    sections = course_data.get('sections', [])
    current_section = st.session_state.get('current_section', 0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=current_section <= 0):
            st.session_state['current_section'] = max(0, current_section - 1)
            st.rerun()
    
    with col2:
        st.write(f"Section {current_section + 1} of {len(sections)}")
    
    with col3:
        if st.button("Next ➡️", disabled=current_section >= len(sections) - 1):
            st.session_state['current_section'] = min(len(sections) - 1, current_section + 1)
            st.rerun()

def display_section(section_data, section_index):
    """Display a course section with questions"""
    st.subheader(section_data.get('title', f'Section {section_index + 1}'))
    
    # Show explanation if available
    explanation = section_data.get('explanation', '')
    if explanation:
        st.markdown(explanation)
    
    # Show questions
    questions = section_data.get('questions', [])
    
    for i, question in enumerate(questions):
        display_question(question, section_index, i)

def display_question(question, section_index, question_index):
    """Display a single question with answer handling"""
    question_key = f"section_{section_index}_question_{question_index}"
    
    with st.container():
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        
        st.write(f"**Question {question_index + 1}:** {question.get('question', '')}")
        
        question_type = question.get('type', 'multiple_choice')
        correct_answer = question.get('correct_answer', '')
        
        user_answer = None
        
        if question_type == 'multiple_choice':
            options = question.get('options', [])
            user_answer = st.radio(
                "Choose your answer:",
                options,
                key=f"{question_key}_answer"
            )
            
        elif question_type == 'true_false':
            user_answer = st.radio(
                "Choose your answer:",
                ['True', 'False'],
                key=f"{question_key}_answer"
            )
            
        elif question_type == 'short_answer':
            user_answer = st.text_input(
                "Your answer:",
                key=f"{question_key}_answer"
            )
            
        elif question_type == 'fill_in_the_blank':
            user_answer = st.text_input(
                "Fill in the blank:",
                key=f"{question_key}_answer"
            )
        
        # Check answer button
        if st.button(f"Check Answer", key=f"{question_key}_check"):
            if user_answer:
                is_correct = check_answer(user_answer, correct_answer, question_type)
                
                if is_correct:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
                
                # Store answer in session state
                if 'answers' not in st.session_state:
                    st.session_state['answers'] = {}
                st.session_state['answers'][question_key] = {
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct
                }
            else:
                st.warning("Please provide an answer first")
        
        st.markdown('</div>', unsafe_allow_html=True)

def check_answer(user_answer, correct_answer, question_type):
    """Check if user answer is correct"""
    if question_type in ['multiple_choice', 'true_false']:
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
    elif question_type in ['short_answer', 'fill_in_the_blank']:
        # More flexible matching for text answers
        user_clean = str(user_answer).strip().lower()
        correct_clean = str(correct_answer).strip().lower()
        return user_clean == correct_clean or user_clean in correct_clean
    return False

def show_progress(course_data):
    """Show progress through the course"""
    answers = st.session_state.get('answers', {})
    
    if answers:
        total_questions = count_total_questions(course_data)
        answered_questions = len(answers)
        correct_answers = sum(1 for answer in answers.values() if answer.get('is_correct', False))
        
        st.markdown("---")
        st.subheader("Progress")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Questions Answered", f"{answered_questions}/{total_questions}")
        
        with col2:
            st.metric("Correct Answers", correct_answers)
        
        with col3:
            if answered_questions > 0:
                accuracy = (correct_answers / answered_questions) * 100
                st.metric("Accuracy", f"{accuracy:.1f}%")

def count_total_questions(course_data):
    """Count total questions in the course"""
    total = 0
    sections = course_data.get('sections', [])
    
    for section in sections:
        questions = section.get('questions', [])
        total += len(questions)
    
    return total

if __name__ == "__main__":
    main()