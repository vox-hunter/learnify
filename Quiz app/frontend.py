import streamlit as st
import json
import re
import random
from st_fill_in_the_blanks import fill_in_the_blanks_input
import local_backend
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import os



MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

st.set_page_config(
    layout="wide", 
    page_title="Learnique",
    page_icon="🧠"
)

# Apply custom CSS for consistent theming (fallback for cloud deployment)
st.markdown("""
<style>
    .stApp {{
        background-color: #0a0014 !important;
    }}
    .stSidebar {{
        background-color: #1a0033 !important;
    }}
    .stButton > button {{
        background-color: #9d00ff !important;
        color: white !important;
    }}
    .stButton > button:hover {{
        background-color: #7a00cc !important;
    }}
    .stFileUploader > div > div {{
        background-color: #1a0033 !important;
        border: 2px dashed #9d00ff !important;
    }}    .stProgress > div > div {{
        background-color: #9d00ff !important;
    }}
</style>
""", unsafe_allow_html=True)

# Function to initialize all session state variables
def initialize_session_state():
    # Initialize session state
    if "current_section_index" not in st.session_state:  
        st.session_state.current_section_index = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "checked_answers" not in st.session_state:
        st.session_state.checked_answers = {}
    
    # Scoring system state
    if "current_score" not in st.session_state:
        st.session_state.current_score = 0
    if "total_questions_in_course" not in st.session_state:
        st.session_state.total_questions_in_course = 0
    if "scored_correctly_keys" not in st.session_state:
        st.session_state.scored_correctly_keys = set()
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "course_data" not in st.session_state:
        st.session_state.course_data = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None
    if "is_generating_course" not in st.session_state:
        st.session_state.is_generating_course = False
    if "pending_uploaded_file" not in st.session_state:
        st.session_state.pending_uploaded_file = None
    if "pending_pdf_url" not in st.session_state:
        st.session_state.pending_pdf_url = None
    # Authentication and course limit tracking
    if "courses_generated" not in st.session_state:
        st.session_state.courses_generated = 0
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = None
    if "name" not in st.session_state:
        st.session_state.name = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "show_login" not in st.session_state:
        st.session_state.show_login = False

# Initialize session state at module level
initialize_session_state()

# Load authentication config with multiple fallback paths
def load_config():
    """Load authentication config with fallback paths for cloud deployment"""
    potential_paths = [
        # Current directory (cloud deployment)
        'authenticate.yaml',
        # Parent directory (local development)
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml'),
        # Same directory as script
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authenticate.yaml'),
        # Streamlit secrets fallback
        None  # Will use Streamlit secrets
    ]
    
    for config_path in potential_paths:
        if config_path is None:
            # Try to load from Streamlit secrets as fallback
            try:
                if hasattr(st, 'secrets') and 'authenticate' in st.secrets:
                    return dict(st.secrets['authenticate'])
            except Exception:
                continue
        else:
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as file:
                        config = yaml.load(file, Loader=SafeLoader)
                    return config
            except Exception as e:
                st.warning(f"Failed to load config from {config_path}: {e}")
                continue
    
    # Return minimal config if all methods fail
    return {
        'credentials': {'usernames': {}},
        'cookie': {'name': 'auth_cookie', 'key': 'default_key', 'expiry_days': 30},
        'api_key': 'default_key',
        'preauthorized': []
    }

# Save config function with error handling
def save_config(config):
    """Save config with error handling for cloud deployment"""
    potential_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authenticate.yaml'),
        'authenticate.yaml'
    ]
    
    for config_path in potential_paths:
        try:
            with open(config_path, 'w') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            return True
        except Exception:
            continue
    return False

# Create authenticator with error handling
def get_authenticator():
    """Create authenticator with robust error handling"""
    try:
        config = load_config()
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config.get('preauthorized', []),
            api_key=config.get('api_key')
        )
        return authenticator, config
    except Exception as e:
        st.error(f"Authentication system initialization failed: {e}")
        # Return None to indicate authentication is not available
        return None, None

def check_course_limit():
    """Check if user has reached the course generation limit"""
    if st.session_state.authentication_status:
        return True  # Authenticated users have unlimited access
    return st.session_state.courses_generated < 3

def reset_section_attempt_state():
    st.session_state.user_answers = {}
    st.session_state.checked_answers = {}

# --- Helper function to call local backend ---
def generate_course(files=None, file_url=None):
    file_content = None
    
    if files:
        # Read the file content
        file_content = files.read()
        # Reset the file pointer for potential future reads
        files.seek(0)
    elif file_url:
        # We'll pass the URL directly to the local backend
        pass
    else:
        return None, "No input provided. Please upload a file or provide a URL."

    try:
        # Call our local backend function directly
        return local_backend.generate_course(file_content=file_content, file_url=file_url)
    except Exception as e:
        st.error(f"Error generating course: {e}")
        return None, f"Error generating course: {e}"

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
        feedback_message = f"Your answer: {user_answer}, Correct answer: {correct_answer}"    # AI-powered validation for short answer questions
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
            feedback_message = "Error processing match answers."    # For other text-based answers (multiple_choice, fill_in_the_blank)
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

# --- Display Course Content ---
def display_question(question_item, section_key, question_idx):
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
                st.warning(f"Multiple choice question '{question_text_full}' received an empty list of options.")
            st.radio(
                "Your choice:", options, 
                key=question_key, 
                label_visibility="collapsed",
                on_change=handle_answer_submission,
                args=(question_key, answer, question_type),
                disabled=is_answered,
                index=None  # Ensures no option is selected by default
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
            )            # If the component's value changed, update session_state and trigger submission handler
            if user_input_for_blank != current_blank_value:
                st.session_state[question_key] = user_input_for_blank
                handle_answer_submission(question_key, correct_answer_for_blank, question_type)
                # Note: Removed st.rerun() - Streamlit automatically reruns when session state changes
    
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
                        st.success("Successfully parsed converted JSON string.")
                    except json.JSONDecodeError:
                        st.error(f"Could not parse match data: {data_str}")
        
        # Check if we have a proper match format (dictionary mapping left items to right items)
        if isinstance(match_data, dict) and match_data:
            left_items = list(match_data.keys())
            right_items = list(match_data.values())
            
            # Shuffle the right items to make it more challenging
            # We'll use a fixed seed based on the question key to ensure
            # the order is consistent on reruns but different for each question
            import random
            r = random.Random(question_key)
            shuffled_right = right_items.copy()
            r.shuffle(shuffled_right)
            
            # Create a container for the matching UI
            match_container = st.container()
            
            # Initialize user's matches in session state if not already done
            match_answers_key = f"{question_key}_matches"
            if match_answers_key not in st.session_state:
                st.session_state[match_answers_key] = {left_item: "" for left_item in left_items}
            
            with match_container:
                # Use a more visually distinct approach with a clear title
                st.markdown("### Match the following items:")
                
                # Create a more visually appealing UI with cards
                for i, left_item in enumerate(left_items):
                    with st.container():
                        cols = st.columns([4, 1, 4])
                          # Left item in a styled container
                        with cols[0]:
                            st.markdown(
                                f"""
                                <div style="background-color: transparent; border: 2px solid #e0e0e0; padding: 10px; border-radius: 5px; min-height: 50px; display: flex; align-items: center;">
                                    <span style="color: white; font-size: 1rem; font-weight: 500;">{left_item}</span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                          # Arrow in the middle
                        with cols[1]:
                            st.markdown(
                                """
                                <div style="display: flex; justify-content: center; align-items: center; height: 50px;">
                                    <span style="font-size: 24px; color: white;">→</span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        
                        # Dropdown for right items
                        with cols[2]:
                            # Create a unique key for each dropdown
                            dropdown_key = f"{question_key}_match_{i}"
                            
                            # Get current selection (if any)
                            current_selection = st.session_state[match_answers_key].get(left_item, "")
                            
                            # Create dropdown for right items
                            selected_match = st.selectbox(
                                label=f"Match for {left_item}",
                                options=[""] + shuffled_right,  # Add empty option as default
                                index=0 if not current_selection else shuffled_right.index(current_selection) + 1 if current_selection in shuffled_right else 0,
                                key=dropdown_key,
                                disabled=is_answered
                            )
                            
                            # Update session state when selection changes
                            if selected_match != current_selection:
                                st.session_state[match_answers_key][left_item] = selected_match
                
                # Add a horizontal line to separate the controls from the submit button
                st.markdown("---")
                
                # Submit button to check all matches at once
                if not is_answered and st.button("Check Matches", key=f"{question_key}_check", type="primary"):
                    # Prepare user's matches in the format expected by the answer checking function
                    user_match_dict = st.session_state[match_answers_key].copy()
                    
                    # Check if all items have been matched
                    if "" in user_match_dict.values():
                        st.warning("Please match all items before submitting.")
                    else:
                        # Convert to string format for answer checking
                        user_match_str = json.dumps(user_match_dict, sort_keys=True)
                        correct_match_str = json.dumps(match_data, sort_keys=True)
                          # Store the formatted answer in session state for the question key
                        st.session_state[question_key] = user_match_str
                        
                        # Call the answer submission handler
                        handle_answer_submission(question_key, correct_match_str, "match")
                        # Note: Removed st.rerun() - Streamlit automatically reruns when session state changes
                        
                # Display a visual summary of matches if answered
                if is_answered:
                    st.markdown("### Your Matches:")
                    user_matches = st.session_state[match_answers_key]
                    correct_matches = match_data
                    
                    for left_item, user_right_item in user_matches.items():
                        correct_right_item = correct_matches.get(left_item, "")
                        is_match_correct = user_right_item == correct_right_item
                        
                        cols = st.columns([4, 1, 4, 1])
                          # Left item
                        with cols[0]:
                            st.markdown(
                                f"""
                                <div style="background-color: transparent; border: 2px solid #e0e0e0; padding: 10px; border-radius: 5px; min-height: 50px; display: flex; align-items: center;">
                                    <span style="color: white; font-size: 1rem; font-weight: 500;">{left_item}</span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                          # Arrow
                        with cols[1]:
                            st.markdown(
                                """
                                <div style="display: flex; justify-content: center; align-items: center; height: 50px;">
                                    <span style="font-size: 24px; color: white;">→</span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                          # User's matched right item with color coding
                        with cols[2]:
                            border_color = "#4CAF50" if is_match_correct else "#f44336"  # Green border if correct, red if incorrect
                            text_color = "white"  # White text for consistency
                            st.markdown(
                                f"""
                                <div style="background-color: transparent; border: 2px solid {border_color}; padding: 10px; border-radius: 5px; min-height: 50px; display: flex; align-items: center;">
                                    <span style="color: {text_color}; font-size: 1rem; font-weight: 500;">{user_right_item}</span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        
                        # Correct/incorrect icon
                        with cols[3]:
                            if is_match_correct:
                                st.markdown(
                                    """
                                    <div style="display: flex; justify-content: center; align-items: center; height: 50px;">
                                        <span style="font-size: 24px; color: green;">✓</span>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                            else:                                st.markdown(
                                    f"""
                                    <div style="display: flex; justify-content: center; align-items: center; height: 50px;">
                                        <span style="font-size: 24px; color: red;">✗</span>
                                        <div style="font-size: 12px; color: white; margin-left: 5px; background-color: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 3px;">
                                            (Correct: {correct_right_item})
                                        </div>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
        else:
            # Try one more time to fix the JSON format before giving up
            if not isinstance(match_data, dict):
                data_str = str(match_data)
                fixed_data = fix_json_format(data_str)
                if fixed_data:
                    match_data = fixed_data
                    st.info("Successfully recovered match question data from malformed JSON.")
                else:
                    # Check if this looks like a JSON formatting error (missing commas)
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
                 st.success(feedback_message)
            else:
                 st.error(feedback_message)

def display_section_content(section_data, section_key_prefix):
    """
    Recursively displays a section and its subsections, including explanations and quizzes.
    """
    # Check if section_data is a Pydantic model (it has __dict__ but no get method)
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    # Handle both dictionary and Pydantic model formats for section title
    if is_pydantic_model:
        # For Pydantic models, access the attribute directly
        section_title = getattr(section_data, "section_title", "Unnamed Section")
        explanation = getattr(section_data, "explanation", "No explanation provided.")
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        # For dictionaries, use get method
        section_title = section_data.get("section", "Unnamed Section") 
        explanation = section_data.get("explanation", "No explanation provided.")
        questions = section_data.get("questions", [])
        subsections = section_data.get("sub_sections", [])
    
    # Display section title and explanation
    st.subheader(section_title)
    st.markdown(explanation)

    # Display questions if present
    if questions:
        for i, question_item in enumerate(questions):
            display_question(question_item, section_key_prefix, i)

    # Display subsections if present
    if subsections:
        for i, sub_section_data in enumerate(subsections):
            sub_section_key = f"{section_key_prefix}_sub_{i}"
            with st.container(): # Visually group subsections
                st.markdown("---") # Add a separator
                display_section_content(sub_section_data, sub_section_key)

def main():
    # Initialize authenticator with error handling
    authenticator, config = get_authenticator()
    
    # Simple title bar with login functionality
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("AI Quiz and Course Generator")
    
    with col2:
        # Show different buttons based on authentication status and availability
        if authenticator is None:
            # Authentication system not available (cloud deployment issue)
            st.warning("🔐 Login temporarily unavailable")
        elif st.session_state.authentication_status:
            # Show logout button for authenticated users
            try:
                authenticator.logout(location='main')
            except Exception as e:
                st.error(f"Logout error: {e}")
        else:
            # Show login/hide button for non-authenticated users
            button_text = "❌ Hide" if st.session_state.show_login else "🔐 Login"
            if st.button(button_text, type="secondary"):
                st.session_state.show_login = not st.session_state.show_login
                st.rerun()    
    # Show authentication status messages and functionality
    if authenticator is not None:
        # Authentication system is available
        if st.session_state.authentication_status:
            st.success(f'Welcome *{st.session_state.name}*! You have unlimited access to course generation.')
            
            # Add password reset widget for authenticated users
            if 'show_password_reset' not in st.session_state:
                st.session_state.show_password_reset = False
                
            if st.button("🔑 Change Password", type="secondary"):
                st.session_state.show_password_reset = not st.session_state.show_password_reset
                st.rerun()
            
            if st.session_state.show_password_reset:
                st.markdown("---")
                st.subheader("🔑 Change Password")
                try:
                    if authenticator.reset_password(st.session_state.username):
                        st.success('Password modified successfully')
                        # Save the updated config to YAML file
                        save_config(config)
                        st.session_state.show_password_reset = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Password reset error: {e}")
            
        elif st.session_state.authentication_status is False:
            st.error('Username/password is incorrect')
        elif st.session_state.authentication_status is None and st.session_state.courses_generated >= 3:
            st.warning('⚠️ You have reached the limit of 3 guest courses. Please login to continue generating courses.')
        elif st.session_state.courses_generated < 3:
            courses_remaining = 3 - st.session_state.courses_generated
            st.info(f"🆓 Guest access: {courses_remaining} course{'s' if courses_remaining != 1 else ''} remaining. Login for unlimited access!")
    else:
        # Authentication system not available - guest mode only
        if st.session_state.courses_generated >= 3:
            st.warning('⚠️ You have reached the limit of 3 guest courses. Authentication system is temporarily unavailable.')
        else:
            courses_remaining = 3 - st.session_state.courses_generated
            st.info(f"🆓 Guest access: {courses_remaining} course{'s' if courses_remaining != 1 else ''} remaining. (Authentication temporarily unavailable)")
    
    # Conditionally show authentication section
    if authenticator is not None and not st.session_state.authentication_status and st.session_state.show_login:        # Show login options
        st.markdown("---")
        st.subheader("🔐 Authentication")
        
        # Create tabs for different login methods
        login_tab, register_tab, forgot_tab = st.tabs(["Login", "Register", "Forgot Password"])
        
        with login_tab:
            st.markdown("### Login with Username/Password")
            try:
                authenticator.login()
            except Exception as e:
                st.error(f"Login error: {e}")
            
            st.markdown("### Or Login with OAuth")
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    if config and 'oauth2' in config:
                        authenticator.experimental_guest_login('Login with Google',
                                                             provider='google',
                                                             oauth2=config['oauth2'])
                    else:
                        st.info("OAuth login not configured")
                except Exception as e:
                    st.error(f"Google login error: {e}")
            
            with col2:
                try:
                    if config and 'oauth2' in config:
                        authenticator.experimental_guest_login('Login with Microsoft',
                                                             provider='microsoft',
                                                             oauth2=config['oauth2'])
                    else:
                        st.info("OAuth login not configured")
                except Exception as e:
                    st.error(f"Microsoft login error: {e}")
        
        with register_tab:
            st.markdown("### Create New Account")
            try:
                email_of_registered_user, \
                username_of_registered_user, \
                name_of_registered_user = authenticator.register_user(
                    fields={'Form name':'', 'Email':'Email', 'Username':'Username', 'Password':'Password', 'Repeat password':'Repeat password', 'Password hint':'Password hint', 'Captcha':'Captcha', 'Register':'Sign Up'},
                    two_factor_auth=True
                )
                if email_of_registered_user:
                    st.success('User registered successfully')
                    # Important: Reload the config to get the updated credentials
                    config = load_config()
                    save_config(config)
                    st.info("Please use your new credentials to login in the Login tab.")
            except Exception as e:
                st.error(f"Registration error: {e}")
        
        with forgot_tab:
            st.markdown("### Reset Password")
            try:
                username_of_forgotten_password, \
                email_of_forgotten_password, \
                new_random_password = authenticator.forgot_password(send_email=True)
                if username_of_forgotten_password:
                    st.success('New password generated. Please check your email.')
                    save_config(config)
                elif username_of_forgotten_password == False:
                    st.error('Username not found')
            except Exception as e:
                st.error(f"Password reset error: {e}")
    
    st.markdown("---")
    
    # ADD the description here
    st.write("Upload a PDF or provide a URL to generate a course with quizzes.")
    
    # Check for errors and display them prominently
    if st.session_state.error_message:
        st.error(f"❌ {st.session_state.error_message}")
        if st.button("Clear Error"):
            st.session_state.error_message = None
            st.rerun()
    
    # --- UI for input (in sidebar) ---
    st.sidebar.header("Input PDF")
    input_method = st.sidebar.radio("Choose input method:", ("Upload File", "Provide URL"))

    uploaded_file = None
    pdf_url = None

    if input_method == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload your PDF", 
            type=["pdf"],
            help="Maximum file size: 20MB"
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            st.sidebar.info(f"File size: {file_size / (1024*1024):.1f} MB")
            
    elif input_method == "Provide URL":
        pdf_url = st.sidebar.text_input(
            "Enter PDF URL",
            placeholder="https://example.com/document.pdf",
            help="Enter a direct link to a PDF file"
        )
        if pdf_url and not pdf_url.startswith(('http://', 'https://')):
            st.sidebar.warning("Please enter a valid URL starting with http:// or https://")
            pdf_url = None    # Show course generation status for unauthenticated users
    if not st.session_state.authentication_status:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Guest Access Status")
        courses_used = st.session_state.courses_generated
        courses_remaining = 3 - courses_used
        
        if courses_remaining > 0:
            st.sidebar.success(f"✅ {courses_remaining} guest course{'s' if courses_remaining != 1 else ''} remaining")
            # Show progress bar
            progress = courses_used / 3
            st.sidebar.progress(progress, text=f"Used: {courses_used}/3")
        else:
            st.sidebar.error("❌ Guest courses limit reached")
            st.sidebar.info("Login above for unlimited access!")

    # Add helpful tips in sidebar
    with st.sidebar.expander("💡 Tips"):
        st.write("""
        **For best results:**
        - Use PDFs with clear, readable text
        - Educational content works best
        - Avoid image-heavy documents
        - File size limit: 20MB
        
        **Supported question types:**
        - Multiple choice
        - Fill in the blank
        - Short answer
        - True/False
        - Matching        """)
      # Check if user can generate courses
    can_generate = check_course_limit()
    
    # Simple button logic: disable only if generating or limit reached
    if st.session_state.is_generating_course:
        button_text = "🤖 Generating..."
        button_disabled = True
    elif can_generate:
        button_text = "Generate Course"
        button_disabled = False
    else:
        button_text = "Login Required (Limit Reached)"
        button_disabled = True
      # Two-phase button logic to properly handle disable state
    if st.sidebar.button(button_text, type="primary", disabled=button_disabled):
        # Check if either input method is provided
        if uploaded_file or pdf_url:
            # Check course limit one more time before processing
            if not check_course_limit():
                st.sidebar.error("You have reached the limit of 3 guest courses. Please login to continue.")
                return
            
            # Phase 1: Set up generation state and store inputs, then rerun
            st.session_state.is_generating_course = True
            st.session_state.pending_uploaded_file = uploaded_file
            st.session_state.pending_pdf_url = pdf_url
            
            # Clear previous state
            st.session_state.course_data = None
            st.session_state.error_message = None
            st.session_state.current_section_index = 0
            reset_section_attempt_state()
            
            # Increment course count for non-authenticated users
            if not st.session_state.authentication_status:
                st.session_state.courses_generated += 1
            
            # Rerun to show disabled button immediately
            st.rerun()
        else:
            st.sidebar.warning("Please provide a PDF input.")
    
    # Phase 2: Execute generation if we're in generating state
    if st.session_state.is_generating_course and (st.session_state.pending_uploaded_file or st.session_state.pending_pdf_url):
        # Show loading message with more details
        with st.spinner("🤖 Generating course... This may take 30-60 seconds for complex PDFs."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                if st.session_state.pending_uploaded_file:
                    status_text.text("📄 Processing uploaded PDF...")
                    progress_bar.progress(25)
                    course_data, error_message = generate_course(files=st.session_state.pending_uploaded_file)
                elif st.session_state.pending_pdf_url:
                    status_text.text("🌐 Downloading PDF from URL...")
                    progress_bar.progress(25)
                    course_data, error_message = generate_course(file_url=st.session_state.pending_pdf_url)                
                progress_bar.progress(75)
                status_text.text("🧠 AI is analyzing content and creating questions...")
                
                # Reset score and calculate total questions for new course
                st.session_state.current_score = 0
                st.session_state.scored_correctly_keys = set()

                # Helper function to count questions recursively
                def _count_questions_recursively(sections_list):
                    total_q = 0
                    if not sections_list:
                        return 0
                    for section_item in sections_list:
                        # Ensure section_item is a dictionary before processing
                        if hasattr(section_item, '__dict__') and not hasattr(section_item, 'get'):
                            # This is a Pydantic model
                            total_q += len(getattr(section_item, "quiz", []))
                            sub_sections = getattr(section_item, "subsections", [])
                            if sub_sections:
                                total_q += _count_questions_recursively(sub_sections)
                        elif isinstance(section_item, dict):
                            # This is a dictionary
                            total_q += len(section_item.get('questions', [])) 
                            sub_sections = section_item.get('sub_sections')
                            # Ensure sub_sections is a list before recursing
                            if sub_sections and isinstance(sub_sections, list):
                                total_q += _count_questions_recursively(sub_sections)
                    return total_q

                if course_data and (isinstance(course_data, list) or hasattr(course_data, '__iter__')):
                    st.session_state.total_questions_in_course = _count_questions_recursively(course_data)
                else:
                    st.session_state.total_questions_in_course = 0
                
                progress_bar.progress(100)
                status_text.text("✅ Course generated successfully!")
                
                if error_message:
                    st.session_state.error_message = error_message
                if course_data:
                    st.session_state.course_data = course_data
                    
                    # Show different success messages based on authentication status
                    if st.session_state.authentication_status:
                        st.success(f"🎉 Course created with {len(course_data)} sections and {st.session_state.total_questions_in_course} questions!")
                    else:
                        remaining = 3 - st.session_state.courses_generated
                        if remaining > 0:
                            st.success(f"🎉 Course created! You have {remaining} guest course{'s' if remaining != 1 else ''} remaining.")
                        else:
                            st.success("🎉 Course created! This was your last guest course. Login for unlimited access.")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.session_state.error_message = f"Unexpected error: {str(e)}"
            finally:
                # Reset generating state and clear pending inputs
                st.session_state.is_generating_course = False
                st.session_state.pending_uploaded_file = None
                st.session_state.pending_pdf_url = None
            
            # Rerun to apply new course data and reset view
            st.rerun()

    # The score metric will be displayed here
    if st.session_state.total_questions_in_course > 0:
        score_percentage = (st.session_state.current_score / st.session_state.total_questions_in_course) * 100
        st.metric(
            "Current Score",
            f"{st.session_state.current_score} / {st.session_state.total_questions_in_course}",
            f"{score_percentage:.1f}%"
        )

    if "course_data" in st.session_state and st.session_state.course_data:
        course_data = st.session_state.course_data
        total_sections = len(course_data)

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous Section", disabled=st.session_state.current_section_index == 0):
                st.session_state.current_section_index -= 1
                st.rerun()
        with col3:
            if st.button("Next Section ➡️", disabled=st.session_state.current_section_index == total_sections - 1):
                st.session_state.current_section_index += 1
                st.rerun()
        
        with col2:
            st.write(f"Displaying Section {st.session_state.current_section_index + 1} of {total_sections}")

        # Display the current top-level section and its content (including subsections)
        current_section_data = course_data[st.session_state.current_section_index]
        # The key for a top-level section can just be its index
        display_section_content(current_section_data, f"sec_{st.session_state.current_section_index}")

    else:
        st.info("Upload a PDF or provide a URL to generate a course.")

def fix_json_format(data_str):
    """
    Fix common JSON formatting issues in match question data, specifically missing commas.
    
    Args:
        data_str (str): String representation of JSON-like data
        
    Returns:
        dict or None: Parsed dictionary if successful, None if failed
    """
    try:
        # First try normal JSON parsing
        return json.loads(data_str)
    except json.JSONDecodeError:
        try:
            # Try to fix multiple common JSON formatting issues
            import re
              # Remove extra whitespace and newlines, but preserve structure
            cleaned = str(data_str).strip()
            
            # Handle case 1: Key='Value' format (single quotes around values)
            # Convert Key='Value' to "Key":"Value"
            cleaned = re.sub(r"([A-Za-z0-9\s]+)='([^']*)'", r'"\1":"\2"', cleaned)
            
            # Clean up any extra spaces in keys that were created
            cleaned = re.sub(r'"\s+([^"]+)":', r'"\1":', cleaned)
            
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
            try:                # Extract key-value pairs using a more robust approach
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

if __name__ == "__main__":
    main()
