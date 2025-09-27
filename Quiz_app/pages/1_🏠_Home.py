"""
Home Page - Simplified course generation interface
"""
import streamlit as st
import sys
import os
from utils.background_jobs import start_course_generation, get_job, cleanup_finished
from utils.lazy_imports import lazy_import
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Minimal CSS for core functionality only
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
    .stButton > button:hover {
        background-color: #0052a3 !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🧠 AI Course Generator")
    
    # Check authentication status
    is_authenticated = st.session_state.get('authentication_status', False)
    
    if is_authenticated:
        st.success(f"Welcome {st.session_state.get('name', 'User')}!")
        
        # Course generation form
        with st.form("course_generation"):
            st.subheader("Generate Course from PDF")
            
            # File upload or URL input
            col1, col2 = st.columns(2)
            
            with col1:
                uploaded_file = st.file_uploader(
                    "Upload PDF File", 
                    type=['pdf'],
                    help="Upload a PDF file to generate a course"
                )
            
            with col2:
                pdf_url = st.text_input(
                    "Or enter PDF URL",
                    placeholder="https://example.com/document.pdf"
                )
            
            generate_button = st.form_submit_button("Generate Course", type="primary")
            
            if generate_button:
                if uploaded_file or pdf_url:
                    generate_and_redirect(uploaded_file, pdf_url)
                else:
                    st.error("Please upload a file or provide a URL")
    else:
        st.info("Please log in to generate courses")
        if st.button("Go to Login"):
            st.switch_page("pages/2_🔐_Login.py")

def generate_and_redirect(uploaded_file, pdf_url):
    """Generate course and redirect to course page"""
    try:
        # Import backend
        local_backend = lazy_import("local_backend")
        
        # Prepare file data
        file_content = None
        filename = None
        
        if uploaded_file:
            file_content = uploaded_file.read()
            filename = uploaded_file.name
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message, percent):
            progress_bar.progress(percent)
            status_text.text(message)
        
        # Start course generation
        job_id = start_course_generation(
            file_content=file_content,
            file_url=pdf_url,
            filename=filename,
            user_context={'username': st.session_state.get('username')},
            generate_course_fn=local_backend.generate_course
        )
        
        # Wait for completion
        import time
        while True:
            job = get_job(job_id)
            if job:
                if job.get('status') == 'done':
                    course_data = job.get('result')
                    if course_data:
                        st.session_state['current_course'] = course_data
                        st.success("Course generated successfully!")
                        st.switch_page("pages/3_Course.py")
                    break
                elif job.get('status') == 'error':
                    st.error(f"Error generating course: {job.get('error', 'Unknown error')}")
                    break
                else:
                    progress = job.get('progress', 0)
                    message = job.get('message', 'Processing...')
                    update_progress(message, progress)
                    time.sleep(1)
            else:
                time.sleep(1)
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error loading page: {e}")
        st.title("🧠 AI Course Generator")
        st.write("Please refresh the page.")