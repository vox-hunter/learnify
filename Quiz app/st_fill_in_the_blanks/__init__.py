import streamlit as st # Import streamlit for the dummy component and example
import streamlit.components.v1 as components
import os

# Set to True when deploying, False for local development of the component
_RELEASE = True

# Component function will be assigned based on _RELEASE value
_component_func = None

if not _RELEASE:
    _component_func = components.declare_component(
        "st_fill_in_the_blanks",
        url="http://localhost:3001",  # URL of the frontend development server
    )
else:
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")

    expected_manifest_path = os.path.join(build_dir, "asset-manifest.json")
    
    if not (os.path.exists(build_dir) and os.path.isdir(build_dir) and os.path.exists(expected_manifest_path)):
        # This block will be entered if essential build artifacts are missing.
        print(f"ERROR: Custom component 'st_fill_in_the_blanks' build artifacts missing or incomplete in {build_dir}")
        print(f"Build directory exists: {os.path.exists(build_dir)}")
        if os.path.exists(build_dir):
            print(f"Is build directory a directory: {os.path.isdir(build_dir)}")
            print(f"Asset manifest exists: {os.path.exists(expected_manifest_path)}")

        def _dummy_component_func(*args, **kwargs):
            st.error(f"Custom component 'st_fill_in_the_blanks' not loaded. Build artifacts are missing from the expected location: {build_dir}. Please rebuild the component and ensure the 'frontend/build' directory is correctly deployed.")
            return None # Add return None
        _component_func = _dummy_component_func
    else:
        # Use a path relative to this __init__.py file for Streamlit Cloud,
        # assuming the 'frontend/build' directory is correctly placed relative to it.
        # Streamlit handles resolving this path when the component is part of the deployed package.
        _component_func = components.declare_component("st_fill_in_the_blanks", path="frontend/build")


# The public function that Streamlit apps will call
def fill_in_the_blanks_input(question_text_full: str, correctAnswer: str, key: str = None, default_value: str = "", disabled: bool = False):
    """Create a new instance of the st_fill_in_the_blanks component.

    Parameters
    ----------
    question_text_full : str
        The full text of the question, including placeholders like '___'.
    correctAnswer : str
        The correct answer for the blank (used by the component, possibly for validation or display).
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    default_value : str
        The initial value for the input blank.
    disabled : bool
        Whether the input should be disabled.

    Returns
    ------ str or None
        The current value of the input blank field, or None if the component failed to load.
    """    
    if _component_func is None:
        # This should ideally not happen if the logic above is correct,
        # but as a fallback to prevent calling None.
        st.error("FATAL: _component_func for st_fill_in_the_blanks is None. Deployment is broken.")
        return None

    component_value = _component_func(
        question_text_full=question_text_full,
        correctAnswer=correctAnswer,
        key=key,
        default=default_value, 
        disabled=disabled
    )
    return component_value

# Example usage for local testing (optional)
# Ensure this block is correctly indented and uses `st` from `import streamlit as st`
if not _RELEASE and _component_func is not None: # Also check if _component_func is callable
    st.set_page_config(layout="wide") # Ensure st is available
    st.subheader("Fill-in-the-Blanks Component Test")

    # Test case 1: Simple blank
    q1_text = "The capital of France is ___." # Corrected: removed trailing parenthesis
    q1_ans = "Paris"
    user_input1 = fill_in_the_blanks_input(q1_text, q1_ans, key="fitb1", default_value="")
    st.write("User input 1:", user_input1)
    if user_input1 is not None: # Check if user_input1 is not None
        if user_input1.lower() == q1_ans.lower():
            st.success("Correct!")
        else:
            st.error(f"Incorrect. Correct answer: {q1_ans}")

    st.markdown("---")

    # Test case 2: Disabled component with a default value
    q2_text = "Python is a ___ language."
    q2_ans = "programming"
    user_input2 = fill_in_the_blanks_input(q2_text, q2_ans, key="fitb2", default_value="scripting", disabled=True)
    st.write("User input 2 (disabled with default):", user_input2)
    
    st.markdown("---")

    # Test case 3: Question with multiple underscores but component handles one
    q3_text = "The formula for water is H__O, and it has ___ atoms."
    q3_ans = "2"
    user_input3 = fill_in_the_blanks_input(q3_text, q3_ans, key="fitb3")
    st.write("User input 3:", user_input3)

    st.markdown("---")
    st.write("Component Arguments Sent (Example):") # Added Example for clarity
    st.json({
        "q1_text": q1_text,
        "q1_ans": q1_ans,
        "q2_text": q2_text,
        "q2_ans": q2_ans,
        "q3_text": q3_text,
        "q3_ans": q3_ans
    })

