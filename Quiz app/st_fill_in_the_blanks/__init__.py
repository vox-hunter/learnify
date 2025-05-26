\
import streamlit.components.v1 as components
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
        # Fallback for environments where build might not be present during generation
        # In a real scenario, you'd build the frontend first.
        print(f"WARNING: Build directory {build_dir} not found for st_fill_in_the_blanks component.")
        # Provide a dummy function so the app doesn't crash, but the component won't work.
        def _component_func(**kwargs):
            components.html(f"<div>Custom component 'st_fill_in_the_blanks' not built. Args: {kwargs}</div>", height=50)
            return kwargs.get("default_value", "") # Return default or empty string
    else:
        _component_func = components.declare_component(
            "st_fill_in_the_blanks", path=build_dir  # Remove unsupported default_height
        )

def fill_in_the_blanks_input(question_text_full, correctAnswer, key=None, default_value="", disabled=False): # Renamed answer_to_blank to correctAnswer
    """
    Custom Streamlit component for a fill-in-the-blanks input.

    Parameters
    ----------
    question_text_full : str
        The full question text that includes underscore placeholders (e.g., "___").
        Example: "The capital of France is ___.")
    correctAnswer : str # Changed from answer_to_blank
        The correct answer for the blank.
        Example: "Paris"
    key : str, optional
        An optional key that uniquely identifies this component.
    default_value : str, optional
        The initial value for the input field.
    disabled : bool, optional
        Whether the input should be disabled.

    Returns
    -------
    str
        The current text entered by the user in the blank.
    """
    component_value = _component_func(
        question_text_full=question_text_full,
        correctAnswer=correctAnswer, # Changed from answer_to_blank
        key=key,
        default=default_value, # This 'default' is passed to the frontend if no value is sent back from JS
        disabled=disabled
    )
    return component_value

# Example usage (for testing the component independently)
if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(layout="wide")
    st.subheader("Custom Fill-in-the-Blanks Component Test")

    question = "The quick brown ___ jumps over the lazy ___." # Example with underscores
    answer_fox = "fox"
    # answer_dog = "dog" # For a more complex example, but let's stick to one blank for now in this test
    
    # Initialize session state for the component's value
    if 'blank_input_value' not in st.session_state:
        st.session_state.blank_input_value = ""

    # Simulate on_change behavior
    # The component's return value is the latest from JS
    # We store it in session_state to persist it and pass it back as `default_value`
    # to allow Python to control/reset the component's displayed text.

    user_input = fill_in_the_blanks_input(
        question, 
        answer_fox, # Pass the correct answer for the blank
        key="fitb1", 
        default_value=st.session_state.blank_input_value,
        disabled=st.session_state.get("fitb1_disabled", False)
    )

    # If the component returned a new value, update session state
    # This check helps avoid infinite loops if not careful with state updates
    if user_input != st.session_state.blank_input_value:
        st.session_state.blank_input_value = user_input
        # Typically, you'd trigger a rerun if you want other parts of the app to react immediately
        # For this example, we'll just show the value.
        # st.rerun() 

    st.write("You entered:", user_input)

    if st.button("Check Answer (fox)"):
        if user_input.lower() == answer_fox.lower(): # Compare with the correct answer
            st.success("Correct!")
            st.session_state.fitb1_disabled = True # Disable after checking
            st.rerun()
        else:
            st.error(f"Incorrect. The answer was '{answer_fox}'. You typed '{user_input}'.")
    
    if st.button("Reset"):
        st.session_state.blank_input_value = ""
        st.session_state.fitb1_disabled = False
        st.rerun()

