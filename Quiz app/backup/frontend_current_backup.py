import streamlit as st
import json
import re # Add re import
from st_fill_in_the_blanks import fill_in_the_blanks_input # Import the custom component
import local_backend # Import our new local backend module

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

st.set_page_config(layout="wide") # REMOVED max_upload_size

# REMOVE Global title, write, and metric from here
# st.title("AI Quiz and Course Generator") # REMOVED
# st.write("Upload a PDF or provide a URL to generate a course with quizzes.") # REMOVED
# st.metric(...) # REMOVED

# Function to initialize all session state variables
def initialize_session_state():
    # Initialize session state
    if "current_section_index" not in st.session_state:  
        st.session_state.current_section_index = 0     
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {} # {(section_idx, question_idx): user_input}
    if "checked_answers" not in st.session_state:
        st.session_state.checked_answers = {} # {(section_idx, question_idx): "correct" | "incorrect" | None}
    # Scoring system state
    if "current_score" not in st.session_state:
        st.session_state.current_score = 0
    if "total_questions_in_course" not in st.session_state:
        st.session_state.total_questions_in_course = 0
    if "scored_correctly_keys" not in st.session_state:
        st.session_state.scored_correctly_keys = set()
    if "feedback" not in st.session_state: 
        st.session_state.feedback = {}

# Initialize session state at module level
initialize_session_state()


def reset_section_attempt_state(): # Renamed from reset_quiz_state for clarity
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
                    for section_item in sections_list:
                        # Ensure section_item is a dictionary before processing
                        if not isinstance(section_item, dict):
                            # Optionally, log a warning here if unexpected data is encountered
                            # st.warning(f"Skipping non-dictionary item in section list: {type(section_item)}")
                            continue 
                        total_q += len(section_item.get('questions', [])) 
                        sub_sections = section_item.get('sub_sections') # Get raw value, not with default list
                        # Ensure sub_sections is a list before recursing
                        if sub_sections and isinstance(sub_sections, list):
                            total_q += _count_questions_recursively(sub_sections)
                    return total_q

                if course_data and isinstance(course_data, list):
                    st.session_state.total_questions_in_course = _count_questions_recursively(course_data)
                else:
                    st.session_state.total_questions_in_course = 0
                
                if error_message:
                    st.session_state.error_message = error_message
                if course_data:
                    st.session_state.course_data = course_data
                st.rerun() # Rerun to apply new course data and reset view
    else:
        st.sidebar.warning("Please provide a PDF input.")

# --- Display Course Content ---
def display_question(question_item, section_key, question_idx):
    question_type = question_item.get("type", "unknown").lower()
    question_text_full = question_item.get("question", "No question text provided.") # Renamed for clarity
    
    question_key = f"{section_key}_q_{question_idx}"
    is_answered = st.session_state.checked_answers.get(question_key, False)

    # Only display the question text here if it's NOT a fill-in-the-blank handled by the custom component
    if question_type not in ["fill_in_the_blank", "fill in the blank"]:
        st.markdown(f"**{question_idx+1}. ({question_type.replace('_', ' ').title()})**: {question_text_full}")
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we still want the question number and type, but not the text itself here.
        st.markdown(f"**{question_idx+1}. ({question_type.replace('_', ' ').title()})**:")

    if question_type in ["multiple_choice", "multiple choice"]:
        options = question_item.get('choices')
        if options is not None:
            if not options:
                st.warning(f"Multiple choice question '{question_text_full}' received an empty list of options.")
            st.radio(
                "Your choice:", options, 
                key=question_key, 
                label_visibility="collapsed",
                on_change=handle_answer_submission,
                args=(question_key, question_item.get('answer'), question_item.get('type')),
                disabled=is_answered,
                index=None  # Ensures no option is selected by default
            )
        else:
            st.warning(f"Multiple choice question '{question_text_full}': No options provided.")
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we need the full question text and the answer to blank out
        # Assuming the 'answer' field contains the word to be blanked
        # and 'question' contains the full sentence with underscores.
        # full_question_text was already defined above
        correct_answer_for_blank = str(question_item.get("answer", "")) # Ensure answer is a string

        if not question_text_full or not correct_answer_for_blank:
            st.warning(f"Fill in the blank question (key: {question_key}) is missing full text or the correct answer.")
            # Fallback to standard text input if data is incomplete
            st.text_input("Your answer:",
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, correct_answer_for_blank, question_item.get('type'), None),
                          disabled=is_answered
                          )
        # Check if the question_text_full contains underscores (e.g., '___')
        elif not re.search(r'_{3,}', question_text_full):
            st.warning(f"Question text for fill-in-the-blank (key: {question_key}) does not contain '___'. Using standard input. Question: '{question_text_full}'")
            st.text_input("Your answer:",
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, correct_answer_for_blank, question_item.get('type'), None),
                          disabled=is_answered
                          )
        else:
            # Use the custom component
            # The component's return value is the user's input for the blank
            # We need to manage its state for on_change behavior similar to other inputs
            
            # Initialize component's specific state if not present
            if question_key not in st.session_state:
                 st.session_state[question_key] = "" # Initial value for the blank

            # Get current value from session state to pass as default_value (for controlled component behavior)
            current_blank_value = st.session_state[question_key]

            user_input_for_blank = fill_in_the_blanks_input(
                question_text_full=question_text_full,
                correctAnswer=correct_answer_for_blank, # Pass correctAnswer
                key=f"fitb_{question_key}", # Unique key for the component instance
                default_value=current_blank_value,
                disabled=is_answered
            )
            
            # If the component's value changed, update session_state and trigger submission handler
            # This simulates on_change
            if user_input_for_blank != current_blank_value:
                st.session_state[question_key] = user_input_for_blank # Update state with new input
                # Call handle_answer_submission.
                # The `handle_answer_submission` expects the value to be in st.session_state[question_key]
                # which we just set.
                handle_answer_submission(question_key, correct_answer_for_blank, question_item.get('type')) # Pass correct_answer_for_blank
                st.rerun() # Rerun to reflect changes and feedback immediately

    elif question_type == "match":
        st.markdown("Matching questions UI not fully implemented for instant feedback. Raw answer format:")
        st.json(question_item.get('answer')) 
    elif question_type in ["short_answer", "short answer"]:
        st.text_area("Your answer:",
                    key=question_key,
                    on_change=handle_answer_submission,
                    args=(question_key, question_item.get('answer'), question_item.get('type'), None), # Pass None for placeholder
                    disabled=is_answered
                    )
    elif question_type in ["true_false", "true false", "true or false"]:
        tf_options = ["True", "False"]
        # For True/False, we don't need the placeholder logic as it's typically just two options
        # and the default selection behavior is less problematic for on_change.
        # However, to keep handle_answer_submission signature consistent:
        st.radio("Your choice:", tf_options,
                 key=question_key,
                 label_visibility="collapsed",
                 on_change=handle_answer_submission,
                 args=(question_key, question_item.get('answer'), question_item.get('type'), None), # Pass None for placeholder
                 disabled=is_answered
                 )
    
    # Display feedback if answered
    if is_answered: # Check if feedback exists for this key
        feedback_message = st.session_state.feedback.get(question_key)
        if feedback_message:
            if feedback_message.startswith("Correct!"):
                 st.success(feedback_message)
            else:
                 st.error(feedback_message)
        # Fallback if somehow checked but no feedback (should not happen with current logic)
        # else:
        #     st.info("Answer submitted.")


def handle_answer_submission(question_key, correct_answer, question_type, placeholder_option_value=None): # Added placeholder_option_value
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
    # Revert short_answer to simple string comparison
    elif question_type in ["short_answer", "short answer"]:
        if str(user_answer).strip().lower() == str(correct_answer).strip().lower():
            is_correct_locally = True
        feedback_message = f"Your answer: {user_answer}, Expected: {correct_answer}"
    # For other text-based answers (multiple_choice, fill_in_the_blank, match)
    elif str(user_answer).strip().lower() == str(correct_answer).strip().lower():
        is_correct_locally = True
        feedback_message = f"Your answer: {user_answer}, Correct answer: {correct_answer}"
    else: # Default case for incorrect non-boolean, non-short-answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {correct_answer}"

    if is_correct_locally:
        st.session_state.feedback[question_key] = "Correct!" # MODIFIED LINE
        if question_key not in st.session_state.scored_correctly_keys:
            st.session_state.current_score += 1
            st.session_state.scored_correctly_keys.add(question_key)
    else:
        st.session_state.feedback[question_key] = f"Incorrect. {feedback_message}"
    
    # REMOVE st.rerun() from here; Streamlit will rerun naturally after callback
    # st.rerun()

def display_section_content(section_data, section_key_prefix):
    """
    Recursively displays a section and its subsections, including explanations and quizzes.
    """
    # Use "section" for title (Pydantic alias for section_title)
    st.subheader(section_data.get("section", "Unnamed Section")) 
    # Explanation has no alias, so "explanation" is correct
    st.markdown(section_data.get("explanation", "No explanation provided."))

    # Use "questions" for quiz list (Pydantic alias for quiz)
    if "questions" in section_data and section_data["questions"]:
        for i, question_item in enumerate(section_data["questions"]):
            # question_key = f"{section_key_prefix}_q_{i}" # This line is already in the file
            display_question(question_item, section_key_prefix, i)

    # Use "sub_sections" for subsections list (Pydantic alias for subsections)
    if "sub_sections" in section_data and section_data["sub_sections"]:
        for i, sub_section_data in enumerate(section_data["sub_sections"]):
            sub_section_key = f"{section_key_prefix}_sub_{i}"
            with st.container(): # Visually group subsections
                st.markdown("---") # Add a separator
                display_section_content(sub_section_data, sub_section_key)

def main():
    # SET The main title for the application
    st.title("AI Quiz and Course Generator") 
    
    # ADD the description here
    st.write("Upload a PDF or provide a URL to generate a course with quizzes.")

    # --- UI for input (moved to main function) ---
    st.sidebar.header("Input PDF")
    input_method = st.sidebar.radio("Choose input method:", ("Upload File", "Provide URL"))

    uploaded_file = None
    pdf_url = None

    if input_method == "Upload File":
        uploaded_file = st.sidebar.file_uploader("Upload your PDF", type=["pdf"])
    elif input_method == "Provide URL":
        pdf_url = st.sidebar.text_input("Enter PDF URL")

    if st.sidebar.button("Generate Course"):
        if uploaded_file or pdf_url:
            st.session_state.course_data = None
            st.session_state.error_message = None
            st.session_state.current_section_index = 0
            reset_section_attempt_state() # Reset answers and checked status
            
            proceed_with_generation = True
            if pdf_url and not uploaded_file: # Check file size only if URL is the input
                # For URLs, we'll let the local backend handle the download
                st.sidebar.info("Using URL input. Large files may take longer to process.")
                proceed_with_generation = True
            
            if proceed_with_generation:
                with st.spinner("Generating course... This may take a moment."):
                    if uploaded_file:
                        course_data, error_message = generate_course(files=uploaded_file)
                    elif pdf_url:
                        course_data, error_message = generate_course(file_url=pdf_url)

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
                            if not isinstance(section_item, dict):
                                continue 
                            total_q += len(section_item.get('questions', [])) 
                            sub_sections = section_item.get('sub_sections')
                            # Ensure sub_sections is a list before recursing
                            if sub_sections and isinstance(sub_sections, list):
                                total_q += _count_questions_recursively(sub_sections)
                        return total_q

                    if course_data and isinstance(course_data, list):
                        st.session_state.total_questions_in_course = _count_questions_recursively(course_data)
                    else:
                        st.session_state.total_questions_in_course = 0
                    
                    if error_message:
                        st.session_state.error_message = error_message
                    if course_data:
                        st.session_state.course_data = course_data
                    st.rerun() # Rerun to apply new course data and reset view
        else:
            st.sidebar.warning("Please provide a PDF input.")

    # The score metric will be displayed here, once before course generation,
    # and then updated when a course is loaded.
    st.metric(
        "Current Score",
        f"{st.session_state.current_score} / {st.session_state.total_questions_in_course}"
    )

    if "course_data" in st.session_state and st.session_state.course_data:
        course_data = st.session_state.course_data
        total_sections = len(course_data)

        if "current_section_index" not in st.session_state:
            st.session_state.current_section_index = 0
        

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

if __name__ == "__main__":
    main()

