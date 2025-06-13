"""
Home Page - Main course generation interface
"""
import streamlit as st
import sys
import os
import yaml
from yaml.loader import SafeLoader

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import local_backend

# Load authentication functions
def load_config():
    """Load authentication config with fallback paths for cloud deployment"""
    potential_paths = [
        'authenticate.yaml',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authenticate.yaml'),
    ]
    
    for config_path in potential_paths:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.load(file, Loader=SafeLoader)
            return config
        except (FileNotFoundError, PermissionError):
            continue
    
    # Fallback to Streamlit secrets
    try:
        if hasattr(st, 'secrets') and 'authenticate' in st.secrets:
            return dict(st.secrets['authenticate'])
    except Exception:
        pass
    
    return None

def get_authenticator():
    """Create authenticator with robust error handling"""
    try:
        config = load_config()
        if not config:
            return None, None
            
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
        return None, None

def check_authentication():
    """Check if user is authenticated via cookies on page load"""
    try:
        authenticator, config = get_authenticator()
        if authenticator:
            # Check cookies without rendering login form
            try:
                authenticator.login(location='unrendered')
            except:
                pass  # If login widget fails, that's okay - we just want cookie check
            return authenticator, config
    except Exception as e:
        pass
    return None, None

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
    if "course_data" not in st.session_state:
        st.session_state.course_data = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None
    if "is_generating_course" not in st.session_state:
        st.session_state.is_generating_course = False
    if "courses_generated" not in st.session_state:
        st.session_state.courses_generated = 0
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = None
    if "name" not in st.session_state:
        st.session_state.name = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "course_history" not in st.session_state:
        st.session_state.course_history = []
    if "current_course_id" not in st.session_state:
        st.session_state.current_course_id = None

# Initialize session state
initialize_session_state()

# Set page config
st.set_page_config(
    page_title="Learnify - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply modern CSS styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%);
    }
    
    /* Hide default sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Center container */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        text-align: center;
    }
    
    /* Title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
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
        width: 100%;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7a00cc, #5c0099);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 0, 255, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(26, 0, 51, 0.8);
        border: 2px solid #9d00ff;
        border-radius: 25px;
        color: #ededed;
        padding: 12px 20px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.3);
    }
    
    /* File uploader enhanced styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03);
        border: 2px dashed #9d00ff;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .stFileUploader:hover {
        border-color: #ff6b6b;
        background: rgba(255, 255, 255, 0.06);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 25px;
        padding: 5px;
        gap: 10px;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 20px;
        color: rgba(255, 255, 255, 0.7);
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
        color: white;
        box-shadow: 0 4px 15px rgba(157, 0, 255, 0.3);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        border-radius: 10px;
    }
    
    /* Success/Error/Warning message styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 15px;
        border: none;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 255, 0, 0.1), rgba(0, 200, 0, 0.1));
        border-left: 4px solid #00ff00;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 150, 255, 0.1), rgba(0, 100, 255, 0.1));
        border-left: 4px solid #0096ff;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1), rgba(255, 140, 0, 0.1));
        border-left: 4px solid #ffa500;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.1), rgba(200, 0, 0, 0.1));
        border-left: 4px solid #ff0000;
    }
    
    /* Top navigation */
    .top-nav {
        position: fixed;
        top: 0;
        right: 0;
        padding: 1rem;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Top navigation
    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        if st.session_state.get('authentication_status'):
            st.success(f"👤 {st.session_state.get('name', 'User')}")
        else:
            if st.button("🔐 Login", key="login_btn"):
                st.switch_page("pages/2_🔐_Login.py")
    with col3:
        if st.session_state.get('authentication_status'):
            if st.button("🚪 Logout", key="logout_btn"):
                st.session_state.authentication_status = None
                st.session_state.name = None
                st.session_state.username = None
                st.rerun()
    
    # Main content container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
      # Main title
    st.markdown('<h1 class="main-title">What will you learn today?</h1>', unsafe_allow_html=True)
    
    # Show status message
    if st.session_state.get('authentication_status'):
        st.success(f"🎉 Welcome back, {st.session_state.get('name', 'User')}! You have unlimited course generation.")
    else:
        courses_used = st.session_state.get('courses_generated', 0)
        remaining = 3 - courses_used
        if remaining > 0:
            st.info(f"🎯 Welcome! You have {remaining} free course{'s' if remaining != 1 else ''} remaining as a guest.")
        else:
            st.warning("🔒 You've used all 3 guest courses. Please login for unlimited access!")
    
    st.markdown("---")

    # Input tabs
    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 URL"])
    uploaded_file = None
    pdf_url = None
    
    with tab1:
        st.markdown("### Upload your PDF file")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Maximum file size: 10MB, Maximum words: 15,000",
            label_visibility="collapsed"
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            file_size_mb = file_size / (1024*1024)
              # Check file size limit (10MB)
            if file_size > 10 * 1024 * 1024:
                st.error(f"❌ File too large ({file_size_mb:.1f} MB). Maximum size is 10MB.")
                uploaded_file = None
            else:                # Analyze PDF content for word count
                try:
                    pdf_analysis = local_backend.analyze_pdf_content(uploaded_file.getvalue())
                    word_count = pdf_analysis['word_count']
                    
                    if word_count > 15000:
                        st.error(f"❌ PDF contains too many words ({word_count:,}). Maximum allowed: 15,000 words.")
                        st.info("💡 **Tip:** Try uploading a shorter document or specific chapters.")
                        uploaded_file = None
                    elif word_count == 0:
                        st.error("❌ Could not extract text from this PDF. Please try a different file.")
                        uploaded_file = None
                    else:
                        st.success(f"📄 File uploaded: {uploaded_file.name} ({file_size_mb:.1f} MB)")
                        
                        if word_count > 12000:
                            st.warning("⚠️ Large document detected. Generation may take longer than usual.")
                            
                except Exception as e:
                    st.error(f"❌ Error analyzing PDF: {str(e)}")
                    uploaded_file = None
    
    with tab2:
        st.markdown("### Enter PDF URL")
        pdf_url = st.text_input(
            "PDF URL",
            placeholder="https://example.com/document.pdf",
            help="Enter a direct link to a PDF file",
            label_visibility="collapsed"
        )
        if pdf_url and not pdf_url.startswith(('http://', 'https://')):
            st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
            pdf_url = None
        elif pdf_url:
            st.info("📝 **Note:** Word count and time estimation will be shown during generation for URL uploads.")
            st.warning("⚠️ **Limits:** Maximum 10MB file size, 15,000 words")
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Check if user can generate courses
    can_generate = check_course_limit()
    
    if st.session_state.get('is_generating_course', False):
        st.button("🤖 Generating Course...", disabled=True, key="generating_btn")
        # Show progress
        show_generation_progress()
    elif can_generate:
        if st.button("✨ Generate Course", type="primary", key="generate_btn"):
            if uploaded_file or pdf_url:
                # Store file data in session state for progress function
                st.session_state.current_uploaded_file = uploaded_file
                st.session_state.current_pdf_url = pdf_url
                
                # Set generating state immediately and rerun to update UI
                st.session_state.is_generating_course = True
                st.rerun()
            else:
                st.error("⚠️ Please upload a file or enter a URL first")
    else:
        st.warning("⚠️ You've reached the limit of 3 guest courses. Please login for unlimited access.")
        if st.button("🔐 Go to Login", type="primary"):
            st.switch_page("pages/2_🔐_Login.py")
    
    # Show course history in sidebar if available
    show_course_history()
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_course_limit():
    """Check if user has reached the course generation limit"""
    if st.session_state.get('authentication_status'):
        return True
    return st.session_state.get('courses_generated', 0) < 3

def show_generation_progress():
    """Show course generation progress and start generation"""
    # Get the file data from session state (set when button was clicked)
    uploaded_file = st.session_state.get('current_uploaded_file')
    pdf_url = st.session_state.get('current_pdf_url')
    
    if uploaded_file or pdf_url:
        generate_and_redirect(uploaded_file, pdf_url)
    else:
        st.error("❌ No file or URL found for generation")

def generate_and_redirect(uploaded_file, pdf_url):
    """Generate course and redirect to course page with real-time progress"""
    # Set generation state
    st.session_state.is_generating_course = True
    
    # Create progress containers
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
          # Status callback function for real-time updates
        def status_callback(status_message, progress_percent):
            """Update progress and status in real-time"""
            print(f"DEBUG: Status callback called with: {status_message}, {progress_percent}%")
            progress_bar.progress(progress_percent / 100)
            status_text.text(status_message)
            # Use Streamlit's time delay instead of sleep
            import time
            time.sleep(2.2)  # Allow users to read the status
        
        try:
            # Generate course with real-time status updates
            if uploaded_file:
                uploaded_file.seek(0)  # Reset file pointer
                course_data, error_message = local_backend.generate_course(
                    file_content=uploaded_file.read(), 
                    status_callback=status_callback
                )
            else:
                course_data, error_message = local_backend.generate_course(
                    file_url=pdf_url, 
                    status_callback=status_callback
                )
            
            if course_data and not error_message:
                # Store course data
                course_id = len(st.session_state.course_history)
                
                # Generate a more descriptive title based on content
                if uploaded_file:
                    course_title = f"📄 {uploaded_file.name.replace('.pdf', '')}"
                else:
                    course_title = f"🔗 Course from URL"
                
                # Count total questions
                total_questions = count_total_questions(course_data)
                
                # Store course
                st.session_state.course_history.append({
                    'id': course_id,
                    'title': course_title,
                    'data': course_data,
                    'created_at': 'Just now'
                })
                
                # Reset course state for new course
                st.session_state.current_section_index = 0
                st.session_state.user_answers = {}
                st.session_state.checked_answers = {}
                st.session_state.current_score = 0
                st.session_state.total_questions_in_course = total_questions
                st.session_state.scored_correctly_keys = set()
                st.session_state.feedback = {}
                
                # Update counters
                if not st.session_state.get('authentication_status'):
                    st.session_state.courses_generated += 1                # Final status update
                progress_bar.progress(100)
                status_text.text("✅ Course created successfully!")
                
                # Reset generation state and clear stored file data
                st.session_state.is_generating_course = False
                st.session_state.current_uploaded_file = None
                st.session_state.current_pdf_url = None
                
                # Set current course and redirect
                st.session_state.current_course_id = course_id
                st.switch_page("pages/3_📚_Course.py")
            else:
                st.error(f"❌ {error_message}")
                st.session_state.is_generating_course = False
                st.session_state.current_uploaded_file = None
                st.session_state.current_pdf_url = None
                
        except Exception as e:
            st.error(f"❌ Error generating course: {str(e)}")
            st.session_state.is_generating_course = False
            st.session_state.current_uploaded_file = None
            st.session_state.current_pdf_url = None

def count_total_questions(course_data):
    """Count total questions in course recursively"""
    total = 0
    for section in course_data:
        # Count questions in main section
        if 'quiz' in section:
            total += len(section['quiz'])
        elif 'questions' in section:
            total += len(section['questions'])
        
        # Count questions in subsections
        if 'subsections' in section and section['subsections']:
            for subsection in section['subsections']:
                if 'quiz' in subsection:
                    total += len(subsection['quiz'])
                elif 'questions' in subsection:
                    total += len(subsection['questions'])
    return total

def show_course_history():
    """Show course history in sidebar"""
    if st.session_state.course_history:
        with st.sidebar:
            st.markdown("### 🏠 Navigation")
            if st.button("🏠 Home", use_container_width=True):
                st.rerun()
            
            st.markdown("### 📚 Your Courses")
            for course in st.session_state.course_history:
                # Truncate long titles
                display_title = course['title']
                if len(display_title) > 25:
                    display_title = display_title[:22] + "..."
                
                if st.button(f"{display_title}", key=f"course_{course['id']}", use_container_width=True):
                    st.session_state.current_course_id = course['id']
                    st.switch_page("pages/3_📚_Course.py")
            
            # Show user status
            st.markdown("---")
            if st.session_state.get('authentication_status'):
                st.success(f"👤 Logged in as {st.session_state.get('name', 'User')}")
            else:
                courses_used = st.session_state.get('courses_generated', 0)
                remaining = 3 - courses_used
                st.info(f"🎯 Guest: {remaining}/3 courses remaining")

# Cookie authentication check on page load (without showing login form)
try:
    authenticator, config = check_authentication()
    if authenticator and config:
        # Use 'unrendered' location to check cookies without showing login form
        authenticator.login(location='unrendered')
        
        # The authentication status is automatically updated in session state
        # No need to manually update it - streamlit-authenticator handles this
        
except Exception as e:
    # If authentication fails, continue as guest
    st.session_state.authentication_status = None
    st.session_state.name = None
    st.session_state.username = None

# Call main function to render the page
if __name__ == "__main__":
    main()
