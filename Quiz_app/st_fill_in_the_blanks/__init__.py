import streamlit.components.v1 as components
import streamlit as st
import os

# Set to True when deploying, False for local development of the component
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_fill_in_the_blanks",
        url="http://localhost:3001",  # URL of the frontend development server
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    if not os.path.exists(build_dir):
        # Fallback for environments where build might not be present (like Streamlit Cloud)
        st.warning(f"⚠️ Fill-in-the-blanks component build directory not found: {build_dir}")
        st.info("🔄 Falling back to standard text input for fill-in-the-blanks questions.")
        _component_func = None  # Will be handled in the wrapper function
    else:
        try:
            _component_func = components.declare_component(
                "st_fill_in_the_blanks", path=build_dir
            )
        except Exception as e:
            st.error(f"❌ Error loading fill-in-the-blanks component: {str(e)}")
            st.info("🔄 Falling back to standard text input for fill-in-the-blanks questions.")
            _component_func = None

def fill_in_the_blanks_input(question_text_full, correctAnswer, key=None, default_value="", disabled=False):
    """
    Custom Streamlit component for a fill-in-the-blanks input with support for multiple blanks.

    Parameters
    ----------
    question_text_full : str
        The full question text that includes underscore placeholders (e.g., "___").
        Example: "The capital of France is ___ and its language is ___."
    correctAnswer : str or list
        The correct answer(s) for the blank(s).
        For single blank: "Paris"
        For multiple blanks: ["Paris", "French"]
    key : str, optional
        An optional key that uniquely identifies this component.
    default_value : str or list, optional
        The initial value(s) for the input field(s).
    disabled : bool, optional
        Whether the input should be disabled.

    Returns
    -------
    dict or str
        For multiple blanks: Returns a dict with 'value', 'isCorrect', 'correctCount', 'totalBlanks', 'action'
        For single blank: Returns the current text entered by the user in the blank.
    """
    # Validate input types and convert to appropriate formats
    if not isinstance(question_text_full, str):
        print(f"WARNING: question_text_full should be a string, got {type(question_text_full)}")
        question_text_full = str(question_text_full) if question_text_full else ""
    
    # Handle both single answer and multiple answers
    if isinstance(correctAnswer, list):
        answers_array = [str(ans) if ans else "" for ans in correctAnswer]
    else:
        if not isinstance(correctAnswer, str):
            print(f"WARNING: correctAnswer should be a string or list, got {type(correctAnswer)}")
            correctAnswer = str(correctAnswer) if correctAnswer else ""
        answers_array = [correctAnswer]
    
    # Count blanks in question to determine if we have multiple blanks
    import re
    blank_count = len(re.findall(r'_{3,}', question_text_full))
    is_multiple_blanks = blank_count > 1
    
    if _component_func is None:
        # Fallback to standard Streamlit text input when component build is not available
        if is_multiple_blanks:
            st.warning("⚠️ Multiple blanks detected, but custom component not available. Using simplified input.")
            return st.text_input(
                f"Fill in the blanks (answers: {', '.join(answers_array)}): {question_text_full}",
                value=default_value if isinstance(default_value, str) else "",
                key=key,
                disabled=disabled,
                help=f"Answers: {', '.join(answers_array)}" if disabled else None
            )
        else:
            return st.text_input(
                f"Fill in the blank: {question_text_full.replace('___', '_____')}",
                value=default_value if isinstance(default_value, str) else "",
                key=key,
                disabled=disabled,
                help=f"Correct answer: {answers_array[0]}" if disabled else None
            )
    else:
        try:
            component_value = _component_func(
                question_text_full=question_text_full,
                correctAnswer=answers_array if is_multiple_blanks else answers_array[0],
                key=key,
                default=default_value,
                disabled=disabled
            )
            return component_value
        except Exception as e:
            # If component fails, fall back to text input
            st.error(f"❌ Fill-in-the-blanks component error: {str(e)}")
            st.info("🔄 Using fallback text input")
            if is_multiple_blanks:
                return st.text_input(
                    f"Fill in the blanks: {question_text_full}",
                    value=default_value if isinstance(default_value, str) else "",
                    key=f"{key}_fallback" if key else None,
                    disabled=disabled,
                    help=f"Answers: {', '.join(answers_array)}" if disabled else None
                )
            else:
                return st.text_input(
                    f"Fill in the blank: {question_text_full.replace('___', '_____')}",
                    value=default_value if isinstance(default_value, str) else "",
                    key=f"{key}_fallback" if key else None,
                    disabled=disabled,
                    help=f"Correct answer: {answers_array[0]}" if disabled else None
                )

# Alias for backwards compatibility
st_fill_in_the_blanks = fill_in_the_blanks_input

# Make the component available for import
__all__ = ['fill_in_the_blanks_input', 'st_fill_in_the_blanks']

# Example usage (for testing the component independently)
if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(layout="wide")
    st.subheader("Custom Fill-in-the-Blanks Component Test")

    # Test 1: Single blank
    st.write("**Test 1: Single Blank**")
    question1 = "The quick brown ___ jumps over the lazy dog."
    answer1 = "fox"
    
    if 'blank_input_value1' not in st.session_state:
        st.session_state.blank_input_value1 = ""

    user_input1 = fill_in_the_blanks_input(
        question1, 
        answer1,
        key="fitb1", 
        default_value=st.session_state.blank_input_value1,
        disabled=st.session_state.get("fitb1_disabled", False)
    )

    if isinstance(user_input1, dict):
        st.write("Component result:", user_input1)
        if user_input1.get('action') == 'question_complete':
            st.session_state.fitb1_disabled = True
            if user_input1.get('isCorrect'):
                st.success("🎉 Perfect! All answers correct!")
            else:
                st.info(f"✅ {user_input1.get('correctCount', 0)} out of {user_input1.get('totalBlanks', 1)} correct.")
    else:
        st.write("You entered:", user_input1)
        if user_input1 != st.session_state.blank_input_value1:
            st.session_state.blank_input_value1 = user_input1

    # Test 2: Multiple blanks
    st.write("**Test 2: Multiple Blanks**")
    question2 = "The capital of France is ___ and its language is ___."
    answers2 = ["Paris", "French"]
    
    if 'blank_input_value2' not in st.session_state:
        st.session_state.blank_input_value2 = ""

    user_input2 = fill_in_the_blanks_input(
        question2, 
        answers2,
        key="fitb2", 
        default_value=st.session_state.blank_input_value2,
        disabled=st.session_state.get("fitb2_disabled", False)
    )

    if isinstance(user_input2, dict):
        st.write("Component result:", user_input2)
        if user_input2.get('action') == 'question_complete':
            st.session_state.fitb2_disabled = True
            if user_input2.get('isCorrect'):
                st.success("🎉 Perfect! All answers correct!")
            else:
                st.info(f"✅ {user_input2.get('correctCount', 0)} out of {user_input2.get('totalBlanks', 2)} correct.")
    else:
        st.write("You entered:", user_input2)
        if user_input2 != st.session_state.blank_input_value2:
            st.session_state.blank_input_value2 = user_input2

    # Test 3: Three blanks
    st.write("**Test 3: Three Blanks**")
    question3 = "The ___ is the largest ___ in our ___."
    answers3 = ["sun", "star", "galaxy"]
    
    if 'blank_input_value3' not in st.session_state:
        st.session_state.blank_input_value3 = ""

    user_input3 = fill_in_the_blanks_input(
        question3, 
        answers3,
        key="fitb3", 
        default_value=st.session_state.blank_input_value3,
        disabled=st.session_state.get("fitb3_disabled", False)
    )

    if isinstance(user_input3, dict):
        st.write("Component result:", user_input3)
        if user_input3.get('action') == 'question_complete':
            st.session_state.fitb3_disabled = True
            if user_input3.get('isCorrect'):
                st.success("🎉 Perfect! All answers correct!")
            else:
                st.info(f"✅ {user_input3.get('correctCount', 0)} out of {user_input3.get('totalBlanks', 3)} correct.")
    else:
        st.write("You entered:", user_input3)
        if user_input3 != st.session_state.blank_input_value3:
            st.session_state.blank_input_value3 = user_input3

    # Reset buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Reset Test 1"):
            st.session_state.blank_input_value1 = ""
            st.session_state.fitb1_disabled = False
            st.rerun()
    
    with col2:
        if st.button("Reset Test 2"):
            st.session_state.blank_input_value2 = ""
            st.session_state.fitb2_disabled = False
            st.rerun()
            
    with col3:
        if st.button("Reset Test 3"):
            st.session_state.blank_input_value3 = ""
            st.session_state.fitb3_disabled = False
            st.rerun()

