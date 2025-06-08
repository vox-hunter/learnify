"""
Dynamic Course Display Page
"""
import streamlit as st
import json
import sys
import os
import re
import random

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from st_fill_in_the_blanks import fill_in_the_blanks_input
except ImportError:
    st.error("Fill-in-the-blanks component not available")
    
import local_backend

# Initialize session state function
def initialize_session_state():
    """Initialize all session state variables"""
    if "current_section_index" not in st.session_state:  
        st.session_state.current_section_index = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "checked_answers" not in st.session_state:
        st.session_state.checked_answers = {}
    if "current_score" not in st.session_state:
        st.session_state.current_score = 0
    if "total_questions_in_course" not in st.session_state:
        st.session_state.total_questions_in_course = 0
    if "scored_correctly_keys" not in st.session_state:
        st.session_state.scored_correctly_keys = set()
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "course_history" not in st.session_state:
        st.session_state.course_history = []
    if "current_course_id" not in st.session_state:
        st.session_state.current_course_id = None

# Initialize session state
initialize_session_state()

# Set page config
st.set_page_config(
    page_title="Learnify - Course",
    page_icon="📚",
    layout="wide"
)

# Apply modern CSS styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%);
    }
    
    /* Course container */
    .course-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Course title */
    .course-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Section title */
    .section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #9d00ff;
        margin-bottom: 1rem;
    }
    
    /* Navigation buttons */
    .nav-buttons {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
    }
    
    /* Pill button styling */
    .stButton > button {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(157, 0, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7a00cc, #5c0099);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 0, 255, 0.4);
    }
    
    .stButton > button:disabled {
        background: #444;
        transform: none;
        box-shadow: none;
    }
    
    /* Score display */
    .score-container {
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.1), rgba(255, 107, 107, 0.1));
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid rgba(157, 0, 255, 0.3);
    }
    
    .score-container h3 {
        color: #9d00ff;
        margin-bottom: 0.5rem;
    }
    
    .score-container h2 {
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        margin: 0;
    }
    
    /* Question container styling */
    .question-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(157, 0, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .question-container:hover {
        border-color: rgba(255, 107, 107, 0.5);
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 0, 255, 0.2);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #9d00ff;
        border-radius: 15px;
        color: white;
        padding: 15px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.3);
    }
    
    /* Success and error messages */
    .stSuccess {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
        border-radius: 10px;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #ff0000;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Show sidebar navigation
    show_sidebar_navigation()
    
    # Get current course ID from URL or session state
    course_id = get_current_course_id()
    
    if course_id is None:
        st.error("❌ No course selected. Please go back to home and generate a course.")
        if st.button("🏠 Go to Home"):
            st.switch_page("pages/1_🏠_Home.py")
        return
    
    # Load course data
    course_data = load_course_data(course_id)
    
    if not course_data:
        st.error("❌ Course not found. It may have been deleted.")
        if st.button("🏠 Go to Home"):
            st.switch_page("pages/1_🏠_Home.py")
        return
    
    # Main course container
    st.markdown('<div class="course-container">', unsafe_allow_html=True)
      # Course title and info
    course_title = st.session_state.course_history[course_id]['title']
    st.markdown(f'<h1 class="course-title">{course_title}</h1>', unsafe_allow_html=True)
    
    # Course metadata
    total_sections = len(course_data)
    current_section = st.session_state.get('current_section_index', 0)
    st.markdown(f"**📚 Section {current_section + 1} of {total_sections}**")
    
    # Score display
    show_score_display(course_data)
    
    # Course navigation
    show_course_navigation(course_data)
    
    # Display current section
    display_current_section(course_data, course_id)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_sidebar_navigation():
    """Show navigation sidebar like ChatGPT"""
    with st.sidebar:
        st.markdown("### 🏠 Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
        
        if st.button("🔐 Login", use_container_width=True):
            st.switch_page("pages/2_🔐_Login.py")
        
        st.markdown("---")
        st.markdown("### 📚 Your Courses")
        
        # Show course history
        if 'course_history' in st.session_state and st.session_state.course_history:
            for i, course in enumerate(st.session_state.course_history):
                # Highlight current course
                current_course_id = get_current_course_id()
                button_type = "primary" if i == current_course_id else "secondary"
                
                if st.button(f"📖 {course['title']}", key=f"nav_course_{i}", use_container_width=True, type=button_type):
                    st.session_state.current_course_id = i
                    st.session_state.current_section_index = 0  # Reset to first section
                    st.rerun()
        else:
            st.info("No courses yet. Generate your first course!")

def get_current_course_id():
    """Get the current course ID"""
    # Try to get from session state first
    if 'current_course_id' in st.session_state:
        return st.session_state.current_course_id
    
    # If not available, return None
    return None

def load_course_data(course_id):
    """Load course data by ID"""
    if 'course_history' not in st.session_state:
        return None
    
    if course_id >= len(st.session_state.course_history):
        return None
    
    return st.session_state.course_history[course_id]['data']

def show_score_display(course_data):
    """Display current score"""
    total_questions = count_total_questions(course_data)
    current_score = st.session_state.get('current_score', 0)
    
    if total_questions > 0:
        score_percentage = (current_score / total_questions) * 100
        st.markdown(f"""
        <div class="score-container">
            <h3>📊 Your Progress</h3>
            <h2>{current_score}/{total_questions} ({score_percentage:.1f}%)</h2>
        </div>
        """, unsafe_allow_html=True)

def count_total_questions(course_data):
    """Count total questions in course"""
    total = 0
    for section in course_data:
        if 'quiz' in section or 'questions' in section:
            questions = section.get('quiz', section.get('questions', []))
            total += len(questions)
        # Count subsection questions
        if 'subsections' in section and section['subsections']:
            for subsection in section['subsections']:
                if 'quiz' in subsection or 'questions' in subsection:
                    sub_questions = subsection.get('quiz', subsection.get('questions', []))
                    total += len(sub_questions)
    return total

def show_course_navigation(course_data):
    """Show section navigation"""
    total_sections = len(course_data)
    current_section = st.session_state.get('current_section_index', 0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_section > 0:
            if st.button("⬅️ Previous Section"):
                st.session_state.current_section_index = current_section - 1
                st.rerun()
        else:
            st.button("⬅️ Previous Section", disabled=True)
    
    with col2:
        st.markdown(f"**Section {current_section + 1} of {total_sections}**")
    
    with col3:
        if current_section < total_sections - 1:
            if st.button("Next Section ➡️"):
                st.session_state.current_section_index = current_section + 1
                st.rerun()
        else:
            st.button("Next Section ➡️", disabled=True)

def display_current_section(course_data, course_id):
    """Display the current section content"""
    current_section_index = st.session_state.get('current_section_index', 0)
    
    if current_section_index >= len(course_data):
        st.error("Section not found")
        return
    
    current_section = course_data[current_section_index]
    section_key = f"course_{course_id}_sec_{current_section_index}"
      # Display section title
    # Check if current_section is a Pydantic model (it has __dict__ but no get method)
    is_pydantic_model = hasattr(current_section, '__dict__') and not hasattr(current_section, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access the attribute directly
        section_title = getattr(current_section, "section_title", f'Section {current_section_index + 1}')
    else:
        # For dictionaries, use get method
        section_title = current_section.get('section_title', current_section.get('section', f'Section {current_section_index + 1}'))
    
    st.markdown(f'<h2 class="section-title">{section_title}</h2>', unsafe_allow_html=True)
    
    # Display section content
    display_section_content(current_section, section_key)

def display_section_content(section_data, section_key):
    """Display section content including explanation and questions"""
    # Check if section_data is a Pydantic model (it has __dict__ but no get method)
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access the attribute directly
        explanation = getattr(section_data, "explanation", "")
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        # For dictionaries, use get method
        explanation = section_data.get('explanation', '')
        questions = section_data.get('quiz', section_data.get('questions', []))
        subsections = section_data.get('subsections', [])
    
    # Display explanation
    if explanation:
        st.markdown(f"**{explanation}**")
    
    # Display questions
    if questions:
        st.markdown("---")
        for idx, question_item in enumerate(questions):
            display_question(question_item, section_key, idx)
    
    # Display subsections if they exist
    if subsections:
        for sub_idx, subsection in enumerate(subsections):
            subsection_key = f"{section_key}_sub_{sub_idx}"
            
            # Check if subsection is a Pydantic model
            is_sub_pydantic_model = hasattr(subsection, '__dict__') and not hasattr(subsection, 'get')
            
            if is_sub_pydantic_model:
                # For Pydantic models, access the attribute directly
                sub_title = getattr(subsection, "section_title", f'Subsection {sub_idx + 1}')
            else:
                # For dictionaries, use get method
                sub_title = subsection.get('section_title', subsection.get('section', f'Subsection {sub_idx + 1}'))
            
            st.markdown(f"### {sub_title}")
            
            # Display subsection content recursively
            display_section_content(subsection, subsection_key)

def display_question(question_item, section_key, question_idx):
    """Display a single question using the proper logic from frontend.py"""
    import re  # Explicit import for VS Code language server
    # Check if question_item is a Pydantic model
    is_pydantic_model = hasattr(question_item, '__dict__') and not hasattr(question_item, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access attributes directly
        question_type = getattr(question_item, "type", "unknown").lower()
        question_text_full = getattr(question_item, "question", "No question text provided.")
        choices = getattr(question_item, "options", None)
        answer = getattr(question_item, "answer", None)
    else:
        # For dictionaries, use get method
        question_type = question_item.get("type", "unknown").lower()
        question_text_full = question_item.get("question", "No question text provided.")
        choices = question_item.get('choices', None)
        answer = question_item.get('answer', None)
    
    question_key = f"{section_key}_q_{question_idx}"
    is_answered = st.session_state.checked_answers.get(question_key, False)

    # Store question text in session state for AI validation
    st.session_state[f"{question_key}_question"] = question_text_full

    # Only display the question text here if it's NOT a fill-in-the-blank handled by the custom component
    if question_type not in ["fill_in_the_blank", "fill in the blank"]:
        st.markdown(f"**{question_idx+1}. ({question_type.replace('_', ' ').title()})**: {question_text_full}")
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we still want the question number and type, but not the text itself here.
        st.markdown(f"**{question_idx+1}. ({question_type.replace('_', ' ').title()})**:")

    if question_type in ["multiple_choice", "multiple choice"]:
        options = choices  # Use the already extracted choices
        if options is not None:
            if not options:
                st.error("Multiple choice question has no options provided.")
                return
            st.radio(
                "Your choice:", options, 
                key=question_key, 
                label_visibility="collapsed",
                on_change=handle_answer_submission,
                args=(question_key, answer, question_type),
                disabled=is_answered,
                index=None
            )
        else:
            st.warning(f"Multiple choice question '{question_text_full}': No options provided.")
            
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we need the full question text and the answer to blank out
        correct_answer_for_blank = str(answer) if answer is not None else ""

        if not question_text_full or not correct_answer_for_blank:
            st.warning(f"Fill in the blank question (key: {question_key}) is missing full text or the correct answer.")
            # Fallback to standard text input if data is incomplete
            st.text_input("Your answer:",
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, correct_answer_for_blank, question_type, None),
                          disabled=is_answered
                          )
        # Check if the question_text_full contains underscores (e.g., '___')
        elif not re.search(r'_{3,}', question_text_full):
            st.warning(f"Question text for fill-in-the-blank (key: {question_key}) does not contain '___'. Using standard input. Question: '{question_text_full}'")
            st.text_input("Your answer:",
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, correct_answer_for_blank, question_type, None),
                          disabled=is_answered
                          )
        else:
            # Use the custom component
            # Initialize component's specific state if not present
            if question_key not in st.session_state:
                st.session_state[question_key] = ""

            # Get current value from session state to pass as default_value
            current_blank_value = st.session_state[question_key]
            
            user_input_for_blank = fill_in_the_blanks_input(
                question_text_full=question_text_full,
                correctAnswer=correct_answer_for_blank,
                key=f"fitb_{question_key}",
                default_value=current_blank_value,
                disabled=is_answered
            )
            
            # If the component's value changed, update session_state and trigger submission handler
            if user_input_for_blank != current_blank_value:
                st.session_state[question_key] = user_input_for_blank
                handle_answer_submission(question_key, correct_answer_for_blank, question_type, None)
    
    elif question_type == "match":
        # Get the matching items from the question's answer
        match_data = answer  # Use the already extracted answer
        
        # Convert to dictionary format if it's an array of objects with "premise" and "response" fields
        match_dict = {}
        if isinstance(match_data, list):
            try:
                # Handle array format with objects that have premise/response fields
                for item in match_data:
                    if isinstance(item, dict):
                        # Direct premise/response format
                        if "premise" in item and "response" in item:
                            match_dict[item["premise"]] = item["response"]
                        # Indexed format like [0:{...}, 1:{...}]
                        elif len(item) == 1 and isinstance(list(item.values())[0], dict):
                            inner_item = list(item.values())[0]
                            if "premise" in inner_item and "response" in inner_item:
                                match_dict[inner_item["premise"]] = inner_item["response"]
                
                # If we successfully converted at least one item, use the dictionary
                if match_dict:
                    match_data = match_dict
                    st.success("Successfully converted match data format.")
            except Exception as e:
                st.error(f"Error processing match data: {e}")
                st.json(match_data)  # Show the problematic data
        
        # If match_data is still not a dict, try to parse it as JSON string or fix formatting issues
        elif not isinstance(match_data, dict):
            if isinstance(match_data, str):
                # Try to parse as JSON string
                fixed_data = fix_json_format(match_data)
                if fixed_data:
                    match_data = fixed_data
                    st.success("Successfully fixed JSON formatting in match question.")
                else:
                    # Try to parse as standard JSON first
                    try:
                        match_data = json.loads(match_data)
                        st.success("Successfully parsed JSON string.")
                    except json.JSONDecodeError:
                        st.error(f"Could not parse match data as JSON: {match_data}")
            else:
                # Convert to string and try to fix
                data_str = str(match_data)
                fixed_data = fix_json_format(data_str)
                if fixed_data:
                    match_data = fixed_data
                    st.success("Successfully parsed match question data.")
                else:
                    # Try to parse as standard JSON first
                    try:
                        match_data = json.loads(data_str)
                        st.success("Successfully parsed match question data.")
                    except json.JSONDecodeError:
                        # Show more detailed error information
                        raw_data_str = str(match_data)
                        if '"' in raw_data_str and '":' in raw_data_str and '","' not in raw_data_str and '}' in raw_data_str:
                            st.error("""
                            **JSON Formatting Error Detected in Match Question!**
                            
                            The match question answer appears to be missing commas between key-value pairs.
                            
                            **Expected format:** `{"key1": "value1", "key2": "value2", "key3": "value3"}`
                            
                            **Current format appears to be:** Missing commas like `{"key1": "value1" "key2": "value2"}`
                            
                            This has been automatically detected and should be handled, but parsing failed.
                            Please try regenerating the course content.
                            """)
                        else:
                            st.warning("Matching question data is not in the expected format. Expected a dictionary of left-right pairs.")
                        # Show the problematic data for debugging
                        st.json(match_data)
                        # Now proceed with match question processing if we have a valid dictionary
        
        # Check if we have a proper match format (dictionary mapping left items to right items)
        if isinstance(match_data, dict) and match_data:
            left_items = list(match_data.keys())
            right_items = list(match_data.values())
            
            # Shuffle the right items to make it more challenging
            # We'll use a fixed seed based on the question key to ensure
            # the order is consistent on reruns but different for each question
            r = random.Random(question_key)
            shuffled_right = right_items.copy()
            r.shuffle(shuffled_right)
            
            # Create a container for the matching UI
            match_container = st.container()
            
            # Initialize user's matches in session state if not already done
            match_answers_key = f"{question_key}_matches"
            if match_answers_key not in st.session_state:
                st.session_state[match_answers_key] = {}
            
            with match_container:
                st.write("Match the items on the left with the correct items on the right:")
                
                # Create two columns for left and right items
                left_col, right_col = st.columns(2)
                
                with left_col:
                    st.write("**Left Items:**")
                    for left_item in left_items:
                        st.write(f"• {left_item}")
                
                with right_col:
                    st.write("**Right Items:**")
                    for right_item in shuffled_right:
                        st.write(f"• {right_item}")
                
                # Create dropdowns for matching
                user_matches = {}
                for i, left_item in enumerate(left_items):
                    # Get the currently selected value for this left item
                    current_selection = st.session_state[match_answers_key].get(left_item, "Select...")
                    
                    # Create dropdown
                    selected = st.selectbox(
                        f"Match '{left_item}' with:",
                        ["Select..."] + shuffled_right,
                        index=0 if current_selection == "Select..." else shuffled_right.index(current_selection) + 1 if current_selection in shuffled_right else 0,
                        key=f"{question_key}_match_{i}",
                        disabled=is_answered
                    )
                    
                    if selected != "Select...":
                        user_matches[left_item] = selected
                
                # Update session state with current matches
                st.session_state[match_answers_key] = user_matches
                
                # Submit button for matching questions
                if not is_answered and len(user_matches) == len(left_items):
                    if st.button(f"Submit Matches", key=f"{question_key}_submit"):
                        # Convert matches to JSON string for submission
                        matches_json = json.dumps(user_matches)
                        handle_answer_submission(question_key, json.dumps(match_data), question_type, None)
        else:
            # Try one more time to fix the JSON format before giving up
            if not isinstance(match_data, dict):
                # Final attempt with more aggressive parsing
                st.error("Unable to parse matching question data. Falling back to text input.")
        
        if isinstance(match_data, dict) and match_data:
            # Match question processing will be handled by the existing logic above
            pass
        else:
            # Fallback to text area for malformed match questions
            st.text_area("Your answer:",
                        key=question_key,
                        on_change=handle_answer_submission,
                        args=(question_key, answer, question_type, None),
                        disabled=is_answered
                        )
    elif question_type in ["short_answer", "short answer"]:
        st.text_area("Your answer:",
                    key=question_key,
                    on_change=handle_answer_submission,
                    args=(question_key, answer, question_type, None),
                    disabled=is_answered
                    )
    elif question_type in ["true_false", "true false", "true or false"]:
        tf_options = ["True", "False"]
        st.radio("Your choice:", tf_options,
                 key=question_key,
                 label_visibility="collapsed",
                 on_change=handle_answer_submission,
                 args=(question_key, answer, question_type, None),
                 disabled=is_answered
                 )
    
    # Display feedback if answered
    if is_answered:
        feedback_message = st.session_state.feedback.get(question_key)
        if feedback_message:
            if feedback_message.startswith("Correct!"):
                st.success(f"✅ {feedback_message}")
            else:
                st.error(f"❌ {feedback_message}")


def fix_json_format(data_str):
    """
    Fix common JSON formatting issues in match question data, specifically missing commas.
    
    Args:
        data_str (str): String representation of JSON-like data
        
    Returns:
        dict or None: Parsed dictionary if successful, None if failed
    """
    import re  # Explicit import for VS Code language server
    try:
        # First try normal JSON parsing
        return json.loads(data_str)
    except json.JSONDecodeError:
        try:
            # Clean up the string for common issues
            cleaned = str(data_str).strip()
            
            # Handle case 1: Remove any trailing commas before closing braces/brackets
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            
            # Handle case 2: Missing opening/closing braces
            if not cleaned.startswith('{'):
                cleaned = '{' + cleaned
            if not cleaned.endswith('}'):
                cleaned = cleaned + '}'
            
            # Handle case 3: Missing commas between key-value pairs
            # Pattern for "value" followed directly by whitespace/newline and then "key":
            cleaned = re.sub(r'("\s*)\s*\n?\s*"([^"]+)":', r'\1, "\2":', cleaned)
            
            # Also handle cases where there's no space: "value""key":
            cleaned = re.sub(r'(")\s*"([^"]+)":', r'\1, "\2":', cleaned)
            
            # Handle case 4: Missing commas after closing quotes
            # Look for }" followed by "key without comma
            cleaned = re.sub(r'"\s*\n?\s*"([^"]+)":', r'", "\1":', cleaned)
            
            # Clean up any double commas that might have been created
            cleaned = re.sub(r',\s*,', ',', cleaned)
            
            # Remove any leading comma that might have been added after opening brace
            cleaned = re.sub(r'{\s*,', '{', cleaned)
            
            # Try parsing the fixed JSON
            result = json.loads(cleaned)
            return result
            
        except (json.JSONDecodeError, Exception):
            # If regex approach fails, try manual key-value extraction
            try:
                # Extract key-value pairs using a more robust approach
                import re
                
                # First try to handle the Key='Value' format specifically
                pattern_single_quotes = r"([A-Za-z0-9\s]+)='([^']*)'"
                matches = re.findall(pattern_single_quotes, str(data_str))
                
                if matches:
                    result_dict = {}
                    for key, value in matches:
                        # Clean up the key by removing extra whitespace
                        key = key.strip()
                        result_dict[key] = value
                    return result_dict
                
                # Pattern to match key-value pairs with various spacing and line breaks
                # This pattern looks for "key":"value" patterns regardless of spacing
                pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
                matches = re.findall(pattern, str(data_str))
                
                if matches:
                    result_dict = {}
                    for key, value in matches:
                        result_dict[key] = value
                    return result_dict
                
                # Try alternative pattern for unquoted values
                pattern2 = r'"([^"]+)"\s*:\s*([^"{}]+?)(?=\s*(?:"[^"]*"\s*:|}))'
                matches2 = re.findall(pattern2, str(data_str))
                
                if matches2:
                    result_dict = {}
                    for key, value in matches2:
                        # Clean up the value by removing extra whitespace and quotes
                        value = value.strip().strip('"').strip()
                        result_dict[key] = value
                    return result_dict
                
            except Exception:
                pass    
    return None

def handle_answer_submission(question_key, correct_answer, question_type, placeholder_option_value=None):
    user_answer = st.session_state.get(question_key)
    
    if user_answer is None: 
        return

    # If a placeholder was used (only for MCQs) and it's selected, ignore this submission.
    if placeholder_option_value is not None and user_answer == placeholder_option_value:
        return

    st.session_state.checked_answers[question_key] = True 
    st.session_state.user_answers[question_key] = user_answer 

    is_correct_locally = False
    feedback_message = ""

    if question_type in ["true_false", "true false", "true or false"]:
        correct_answer_bool = str(correct_answer).lower() == "true"
        user_answer_bool = str(user_answer).lower() == "true"
        if user_answer_bool == correct_answer_bool:
            is_correct_locally = True
        feedback_message = f"Your answer: {user_answer}, Correct answer: {correct_answer}"

    # AI-powered validation for short answer questions
    elif question_type in ["short_answer", "short answer"]:
        # First try AI validation
        try:
            # Get the original question text from session state
            question_text = st.session_state.get(f"{question_key}_question", "")
            
            # Use AI validation
            ai_result, ai_explanation = local_backend.validate_short_answer_with_ai(
                question_text, user_answer, correct_answer
            )
            
            if ai_result is not None:  # AI validation succeeded
                is_correct_locally = ai_result
                if is_correct_locally:
                    feedback_message = f"Correct! {ai_explanation}"
                else:
                    feedback_message = f"Incorrect. {ai_explanation}"
            else:  # AI validation failed, fallback to simple comparison
                if is_answer_correct(user_answer, correct_answer, question_type):
                    is_correct_locally = True
                display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
                feedback_message = f"Your answer: {user_answer}, Expected: {display_answer} (AI validation unavailable: {ai_explanation})"
                
        except Exception as e:
            # Fallback to simple string comparison if AI validation fails
            if is_answer_correct(user_answer, correct_answer, question_type):
                is_correct_locally = True
            display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
            feedback_message = f"Your answer: {user_answer}, Expected: {display_answer} (AI validation error)"

    # For match questions, we have JSON strings representing dictionaries
    elif question_type == "match":
        try:
            user_matches = json.loads(user_answer)
            correct_matches = json.loads(correct_answer)
            
            # Calculate the number of correct matches
            correct_count = sum(1 for key in user_matches if user_matches.get(key) == correct_matches.get(key))
            total_count = len(correct_matches)
            
            # Determine if the answer is completely correct
            is_correct_locally = user_answer == correct_answer
            
            if is_correct_locally:
                feedback_message = f"Correct! You matched all {total_count} items correctly."
            else:
                feedback_message = f"You matched {correct_count} out of {total_count} items correctly."
        except json.JSONDecodeError:
            feedback_message = "Error processing match answers."

    # For other text-based answers (multiple_choice, fill_in_the_blank)
    elif is_answer_correct(user_answer, correct_answer, question_type):
        is_correct_locally = True
        # Display first acceptable answer if multiple exist
        display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {display_answer}"
    else: # Default case for incorrect non-boolean, non-short-answer
        # Display first acceptable answer if multiple exist
        display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {display_answer}"

    if is_correct_locally:
        st.session_state.feedback[question_key] = "Correct!" 
        if question_key not in st.session_state.scored_correctly_keys:
            st.session_state.current_score += 1
            st.session_state.scored_correctly_keys.add(question_key)
    else:
        st.session_state.feedback[question_key] = f"Incorrect. {feedback_message}"

def is_answer_correct(user_answer, correct_answer, question_type):
    """Check if user answer matches any acceptable answer"""
    user_clean = str(user_answer).strip().lower()
    
    # Handle multiple acceptable answers
    if isinstance(correct_answer, list):
        acceptable_answers = [str(ans).strip().lower() for ans in correct_answer]
        return user_clean in acceptable_answers
    else:
        # Single answer (backward compatibility)
        return user_clean == str(correct_answer).strip().lower()

if __name__ == "__main__":
    main()
