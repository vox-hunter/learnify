"""
Home Page - Main course generation interface
"""
import streamlit as st
import sys
import os
from streamlit_cookies_manager import EncryptedCookieManager
from utils.background_jobs import start_course_generation, get_job, cleanup_finished
from utils.lazy_imports import lazy_import
import io

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Add the parent directory to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.shared_styles import get_combined_css

# Apply modern CSS styling
st.markdown("""
<style>
    /* Cache buster: 2025-07-02-14:30 - Force CSS reload */
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Ensure all text is light colored */
    .stMarkdown, .stText, p, div, span, label {
        color: #e2e8f0 !important;
    }
    
    /* Dark theme for Streamlit elements */
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
    }
    
    /* Heading styles */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
    }
    
    /* Streamlit specific text elements - only for main content */
    .main .stButton > button,
    .stMain .stButton > button {
        color: white !important;
    }
    
    /* Hide cookie manager component that takes up horizontal space */
    iframe[title*="cookie_manager"], 
    iframe[src*="cookie_manager"],
    .stCustomComponentV1:has(iframe[src*="cookie_manager"]) {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    
    /* Hide any empty custom components that might be taking space */
    .stCustomComponentV1[data-testid="stCustomComponentV1"]:has(iframe[height="0"]) {
        display: none !important;
    }
    
    /* Main content container */
    .main-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1000px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #cbd5e0;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Modern card styling */
    .generation-card {
        background: transparent;
        border: none;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(6, 182, 212, 0.1);
        border-radius: 10px;
        padding: 4px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a0aec0;
        font-weight: 500;
        padding: 12px 20px;
        border: none;
        font-size: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        color: white !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid rgba(6, 182, 212, 0.2);
        background: rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        font-weight: 400;
        padding: 12px 16px;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #06b6d4;
        box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(6, 182, 212, 0.05);
        border: 2px dashed rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #06b6d4;
        background: rgba(6, 182, 212, 0.1);
    }
    
    /* Button styling - only for main content area, not sidebar */
    .main .stButton > button,
    .stMain .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
        font-size: 1rem;
    }
    
    .main .stButton > button:hover,
    .stMain .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }
    
    /* Primary button styling - only for main content area */
    .main .stButton[data-testid="baseButton-primary"] > button,
    .stMain .stButton[data-testid="baseButton-primary"] > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        font-size: 1.1rem;
        padding: 1rem 2rem;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        border-radius: 8px;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
        border-radius: 8px;
        border: none;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        border-radius: 8px;
        border: none;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #2196F3, #1976D2);
        color: white;
        border-radius: 8px;
        border: none;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        border-radius: 10px;
    }
    
    /* Feature grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Limits notice styling */
    .limits-notice {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    /* Guest mode styling */
    .guest-mode {
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Import loading animation utilities if available
try:
    from loading_animation import show_loading_status
    from streamlit_loading import ensure_loading_cleanup
    
    # Ensure loading UI is cleaned up on this page
    ensure_loading_cleanup()
except ImportError:
    def show_loading_status(message, progress=None):
        pass  # Fallback if loading animation is not available

try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import get_course_manager, get_session_id
    from local_backend import analyze_pdf_content, generate_course
    from file_security import validate_file_security, get_mime_type, get_file_type_category, get_supported_file_types_display, get_file_processing_info, MAX_FILE_SIZE, MAX_CONTENT_WORDS
    from document_converter import get_conversion_info
    MONGO_AVAILABLE = True
except ImportError as e:
    # Don't show error immediately - just set flag
    MONGO_AVAILABLE = False
    # Store error for later display if needed
    st.session_state['mongo_import_error'] = str(e)
    
    # Provide fallback functions
    def analyze_pdf_content(content):
        return {"word_count": 1000}  # Fallback
    
    def generate_course(*args, **kwargs):
        return None, "MongoDB backend not available"

# --- Get Cookie Manager from Session State ---
cookies = st.session_state.get('cookies')
if cookies is None:
    # Try fallback initialization
    try:
        from cookie_fallback import ensure_cookie_manager
        if ensure_cookie_manager():
            cookies = st.session_state.get('cookies')
        else:
            # Don't stop - just warn and continue without cookies
            st.warning("Cookie manager not available. Some features may be limited.")
            cookies = None
    except (ImportError, Exception):
        st.warning("Cookie manager not available. Some features may be limited.")
        cookies = None
    except ImportError:
        st.error("Cookie manager not found in session state. Please run the app from the main entry point.")
        st.markdown("Please refresh the page or go back to the [Home page](/) to start the application properly.")
        st.stop()

# Initialize cookies if they haven't been, e.g. on first run
# This needs to be called early, but after st.set_page_config
# Note: On some deployment platforms, cookies might take time to initialize
try:
    cookies_ready = cookies is not None and cookies.ready()
except Exception:
    cookies_ready = False

AUTH_COOKIE_NAME = "username" # Consistent cookie name
GUEST_COURSES_COOKIE_NAME = "guest_courses_count" # Cookie to track guest course generation

# --- Authentication is now handled in main.py ---

# --- Guest Course Tracking Functions ---
def get_guest_course_count():
    """Get the number of courses generated by guest users from cookies"""
    if cookies is None:
        return 0
    try:
        if not cookies.ready():
            return 0
    except Exception:
        return 0
    try:
        return int(cookies.get(GUEST_COURSES_COOKIE_NAME, "0"))
    except (ValueError, TypeError):
        return 0

def increment_guest_course_count():
    """Increment the guest course count in cookies"""
    if cookies is None:
        return
    try:
        if not cookies.ready():
            return
    except Exception:
        return
    current_count = get_guest_course_count()
    new_count = current_count + 1
    try:
        cookies[GUEST_COURSES_COOKIE_NAME] = str(new_count)
        cookies.save()
    except Exception:
        pass  # Ignore cookie errors
    return new_count

def reset_guest_course_count():
    """Reset guest course count (called when user logs in)"""
    if cookies is None:
        return
    try:
        if cookies.ready():
            cookies[GUEST_COURSES_COOKIE_NAME] = "0"
            cookies.save()
    except Exception:
        pass  # Ignore cookie errors

def check_course_limit():
    """Check if user has reached the course generation limit"""
    if st.session_state.get('authentication_status'):
        return True # No limit for logged-in users
    
    # For guest users, check cookie-based count
    guest_count = get_guest_course_count()
    return guest_count < 3

def force_login_if_limit_reached():
    """Force login if guest user has reached the 3-course limit"""
    if st.session_state.get('authentication_status'):
        return False  # Already logged in
    
    guest_count = get_guest_course_count()
    if guest_count >= 3:
        st.warning("You have reached the guest limit of 3 courses. Please log in to create more.")
        st.page_link("pages/2_🔐_Login.py", label="Login / Sign Up", icon="🔐")
        return True  # Return True to indicate limit reached, but don't stop execution
    return False

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
        # For guest users, load count from cookies; for logged-in users, always 0
        if st.session_state.get('authentication_status'):
            st.session_state.courses_generated = 0
        else:
            st.session_state.courses_generated = get_guest_course_count()
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

# Apply modern CSS styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%);
    }
    
    /* Sidebar styling delegated to main.py */
    
    /* Hide default sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }
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
      /* Pill button styling - only for main content area */
    .main .stButton > button,
    .stMain .stButton > button {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
        width: 100%;
        font-size: 1rem;
    }
    
    .main .stButton > button:hover,
    .stMain .stButton > button:hover {
        background: linear-gradient(135deg, #0891b2, #0e7490);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4);
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
    # Always show basic hero section first
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🚀 AI Loom</h1>
        <p class="hero-subtitle">Transform any PDF into an interactive learning experience with AI-powered courses</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if a course_id is provided in the URL for sharing
    shared_course_id = st.query_params.get("course_id")
    if shared_course_id:
        # Store in session state to ensure it survives any redirects
        st.session_state.shared_course_id = shared_course_id
        
        # Redirect immediately without any other processing
        st.query_params["course_id"] = shared_course_id
        st.switch_page("pages/3_Course.py")
        return
    
    # The main.py already handles auto-login from cookies consistently
    # No need for additional logout processing here
    
    # Top navigation
    _, _, col3 = st.columns([6, 1, 1])  # Removed col2 (login/user status) - now handled by sidebar
    
    # Note: Login button and username display removed from home page
    # These are now available in the sidebar for cleaner interface

    # Status message
    if st.session_state.get('authentication_status'):
        st.markdown("""
        <div class="guest-mode">
            🎉 Welcome back, <strong>{}</strong>! You have unlimited course generation.
        </div>
        """.format(st.session_state.get('name', 'User')), unsafe_allow_html=True)
    else:
        # Force login if limit reached
        if force_login_if_limit_reached():
            # Don't return here - let the UI continue to render
            pass
        else:
            # Show remaining courses for guest users
            guest_count = get_guest_course_count()
            remaining = 3 - guest_count
            if remaining > 0:
                st.markdown(f"""
                <div class="guest-mode">
                    🎯 <strong>Guest Mode:</strong> {remaining} out of 3 free courses remaining
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="limits-notice">
                    🔒 You've used all 3 guest courses. Please login for unlimited access!
            </div>
            """, unsafe_allow_html=True)

    # Course generation section
    # Input tabs
    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 URL"])
    uploaded_file = None
    pdf_url = None
    
    with tab1:
        st.subheader("📄 Upload your file")
        supported_types = get_supported_file_types_display()
        uploaded_file = st.file_uploader(
            f"Choose a file - Supported types: {supported_types}",
            help=f"Maximum file size: {MAX_FILE_SIZE // (1024*1024)}MB, Maximum content: {MAX_CONTENT_WORDS:,} words",
            label_visibility="collapsed"
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            file_size_mb = file_size / (1024*1024)
            
            # Validate file security and type
            is_safe, error_message = validate_file_security(uploaded_file.name, file_size)
            
            if not is_safe:
                st.error(f"❌ {error_message}")
                uploaded_file = None
            else:
                # Show file info
                file_type = get_file_type_category(uploaded_file.name)
                processing_info = get_conversion_info(uploaded_file.name)
                
                # Removed per request: suppress explicit file uploaded & conversion info messages
                # st.success(f"📄 File uploaded: {uploaded_file.name} ({file_size_mb:.1f} MB, {file_type})")
                # st.info(f"🤖 {processing_info}")
                
                # Show size warning if large
                if file_size > 10 * 1024 * 1024:
                    st.warning(f"📦 Large file detected: {file_size_mb:.1f} MB (above {MAX_FILE_SIZE // (1024*1024)}MB limit)")
                    st.info("💡 **Note:** Large files will be processed using Gemini's document vision capabilities.")
                
                # For PDF files (original only, not converted), try to estimate word count
                if uploaded_file.name.lower().endswith('.pdf') and not (processing_info or '').startswith('🔄'):
                    if file_size <= 10 * 1024 * 1024:  # Small files only
                        try:
                            pdf_analysis = analyze_pdf_content(uploaded_file.getvalue())
                            word_count = pdf_analysis['word_count']
                            
                            if word_count > MAX_CONTENT_WORDS:
                                st.warning(f"⚠️ Document contains {word_count:,} words (above {MAX_CONTENT_WORDS:,} limit).")
                                st.info("💡 **Note:** AI will use document vision to process the content intelligently.")
                            elif word_count == 0:
                                st.info("💡 **Note:** AI will use document vision to analyze this file.")
                            else:
                                st.success(f"📄 Content preview: ~{word_count:,} words")
                                if word_count > 12000:
                                    st.warning("⚠️ Large document detected. Generation may take longer than usual.")
                        except Exception as e:
                            st.info("💡 **Note:** AI will use document vision to analyze this file.")
                elif not (processing_info or '').startswith('🔄'):
                    st.info("💡 **Note:** File will be processed using Gemini's advanced AI capabilities.")
    
    with tab2:
        st.subheader("🔗 Enter file URL")
        pdf_url = st.text_input(
            "File URL",
            placeholder="https://example.com/document.pdf",
            help="Enter a direct link to a file (PDF, document, image, etc.)",
            label_visibility="collapsed"
        )
        if pdf_url and not pdf_url.startswith(('http://', 'https://')):
            st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
            pdf_url = None
        elif pdf_url:
            st.info(f"⚠️ **Limits:** Maximum {MAX_FILE_SIZE // (1024*1024)}MB file size, {MAX_CONTENT_WORDS:,} words")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Check if user can generate courses
    can_generate = check_course_limit()
    
    # Background async job handling
    active_job_id = st.session_state.get('active_course_job_id')
    if active_job_id and not st.session_state.get('generated_course_result'):
        import time as _t
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        phase_placeholder = st.empty()
        PHASES = [
            (0, "Queued"), (3, "Starting"), (5, "Pre-processing"), (10, "Validating"),
            (15, "Converting"), (20, "Preparing Prompt"), (25, "AI Generation"), (60, "Parsing"),
            (80, "Building Quiz"), (95, "Finalizing"), (100, "Done")
        ]
        start_ts = _t.time()
        max_runtime = 1800
        while True:
            job = get_job(active_job_id)
            if not job:
                status_placeholder.error("❌ Job not found.")
                st.session_state.pop('active_course_job_id', None)
                break
            progress = int(job.get('progress', 0))
            status = job.get('status')
            message = job.get('message', 'Working...')
            progress_bar.progress(progress/100 if progress else 0)
            current_phase = next((label for thresh, label in reversed(PHASES) if progress >= thresh), "Queued")
            phase_placeholder.caption(f"Phase: {current_phase} | {progress}%")
            if status == 'error':
                status_placeholder.error(f"❌ {job.get('error') or message}")
                st.session_state.pop('active_course_job_id', None)
                break
            if status == 'done':
                status_placeholder.success("✅ Course generated. Saving…")
                st.session_state.generated_course_result = job.get('result')
                st.rerun()
                break
            status_placeholder.info(f"{message} ({progress}%)")
            if (_t.time() - start_ts) > max_runtime:
                status_placeholder.error("⏱️ Generation timed out.")
                st.session_state.pop('active_course_job_id', None)
                break
            _t.sleep(0.6)
    elif can_generate:
        has_input = bool(uploaded_file or pdf_url)
        btn_label = "✨ Generate Course" if has_input else "📁 Upload a file or enter a URL"
        if st.button(btn_label, type="primary", key="generate_btn", disabled=not has_input):
            if not check_course_limit():
                st.error("🔐 Course limit reached. Please login to continue.")
                st.rerun()
            # Launch background job
            try:
                backend = lazy_import('local_backend')
                file_bytes = None
                file_stream = None
                if uploaded_file:
                    # Decide between in-memory read vs streaming based on size threshold (2MB)
                    try:
                        file_size = len(uploaded_file.getbuffer())
                    except Exception:
                        # Fallback to reading to determine size
                        data_peek = uploaded_file.read()
                        file_size = len(data_peek)
                        uploaded_file.seek(0)
                    STREAM_THRESHOLD = 2 * 1024 * 1024  # 2MB
                    if file_size > STREAM_THRESHOLD:
                        file_stream = uploaded_file  # let backend stream chunks
                    else:
                        file_bytes = uploaded_file.read()
                job_id = start_course_generation(
                    file_content=file_bytes,
                    file_stream=file_stream,
                    file_url=pdf_url if (pdf_url and not uploaded_file) else None,
                    filename=uploaded_file.name if uploaded_file else (os.path.basename(pdf_url) if pdf_url else None),
                    user_context={'username': st.session_state.get('username')},
                    generate_course_fn=backend.generate_course
                )
                st.session_state.active_course_job_id = job_id
                st.rerun()
            except Exception as e:
                st.error(f"Failed to start background job: {e}")
    else:
        st.warning("⚠️ You've reached the limit of 3 guest courses. Please login for unlimited access.")
        if st.button("🔐 Go to Login", type="primary"):
            st.switch_page("pages/2_🔐_Login.py")
    
    # Sidebar is now handled by main.py for consistency

    # Post-job save & redirect logic
    if st.session_state.get('generated_course_result') and not st.session_state.get('course_save_in_progress'):
        st.session_state.course_save_in_progress = True
        course_data = st.session_state.pop('generated_course_result')
        try:
            # Normalize course_data structure
            def to_dict(obj):
                if hasattr(obj, 'model_dump'):
                    try:
                        return obj.model_dump()
                    except Exception:
                        pass
                if isinstance(obj, dict):
                    return obj
                # Fallback minimal serialization
                return {
                    'section': getattr(obj, 'section_title', 'Untitled Section'),
                    'explanation': getattr(obj, 'explanation', ''),
                    'questions': []
                }

            course_title = None
            sections_to_save = []

            if isinstance(course_data, dict):
                course_title = course_data.get('course_title')
                maybe_sections = course_data.get('sections')
                if isinstance(maybe_sections, list):
                    sections_to_save = [to_dict(s) for s in maybe_sections]
            elif hasattr(course_data, 'sections'):
                course_title = getattr(course_data, 'course_title', None)
                sections_to_save = [to_dict(s) for s in getattr(course_data, 'sections', [])]
            elif isinstance(course_data, list):
                sections_to_save = [to_dict(s) for s in course_data]

            if not course_title:
                # Try first section title as course title
                if sections_to_save:
                    course_title = sections_to_save[0].get('section', 'Generated Course')
                else:
                    course_title = 'Generated Course'

            generated_course_id = None
            if MONGO_AVAILABLE:
                from mongo_course_manager import get_course_manager, get_session_id
                cm = get_course_manager()
                is_guest = not st.session_state.get('authentication_status', False)
                creator = st.session_state.get('username') if not is_guest else get_session_id()
                generated_course_id, save_err = cm.save_course(
                    course_data=sections_to_save,
                    course_title=course_title,
                    creator=creator,
                    is_guest=is_guest,
                    session_id=None if not is_guest else creator,
                    is_public=True
                )
                if save_err:
                    st.error(f"❌ Failed to save course: {save_err}")
                else:
                    st.query_params['course_id'] = str(generated_course_id)
                    st.session_state.current_course_id = generated_course_id
                    # Invalidate / update course list cache so sidebar reflects new course immediately
                    try:
                        from utils.navigation_cache import (
                            get_cached_course_list,
                            cache_course_list,
                            invalidate_course_list_cache,
                        )
                        existing = get_cached_course_list(force=False)
                        if existing is not None:
                            # Append lightweight doc if not already present
                            gid_str = str(generated_course_id)
                            if not any(str(c.get('_id') or c.get('id') or c.get('course_id')) == gid_str for c in existing):
                                minimal_doc = {
                                    '_id': generated_course_id,
                                    'title': course_title,
                                    'is_public': True,
                                }
                                new_list = list(existing) + [minimal_doc]
                                cache_course_list(new_list)
                        else:
                            # Force refetch on next sidebar build
                            invalidate_course_list_cache()
                    except Exception:
                        pass
            if generated_course_id:
                if not st.session_state.get('authentication_status'):
                    increment_guest_course_count()
                st.session_state.pop('active_course_job_id', None)
                st.session_state.pop('course_save_in_progress', None)
                cleanup_finished()
                st.switch_page('pages/3_Course.py')
            else:
                st.session_state.pop('course_save_in_progress', None)
        except Exception as e:
            st.error(f"❌ Post-processing error: {e}")
            st.session_state.pop('course_save_in_progress', None)

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
    """Generate course and redirect to course page with improved, live background progress."""
    import time, urllib.parse

    # Helper: render intuitive phase timeline
    def render_phase_timeline(progress: int, message: str):
        PHASES = [
            (0, "Queued"),
            (3, "Starting"),
            (5, "Pre‑processing"),
            (10, "Validating"),
            (15, "Converting"),
            (20, "Preparing AI Prompt"),
            (25, "AI Generation"),
            (60, "Parsing Output"),
            (80, "Building Quiz"),
            (95, "Finalizing"),
            (100, "Done")
        ]
        timeline = []
        for thresh, label in PHASES:
            if progress >= thresh:
                icon = "✅" if progress >= thresh else "⏳"
                state_class = "done" if progress >= thresh else "pending"
                style = "color:#06b6d4;" if progress < 100 and progress >= thresh else "color:#64748b;"
                if progress >= thresh:
                    icon = "✅" if progress > thresh or progress == 100 else "🔄"
                timeline.append(f"<span style='margin-right:8px;{style}'>{icon} {label}</span>")
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:4px;font-size:0.85rem;'>" + "".join(timeline) + "</div>",
            unsafe_allow_html=True
        )
        if message:
            st.caption(message)

    st.session_state.is_generating_course = True

    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        phases_placeholder = st.empty()

        # Pre-processing (compression / validation) still synchronous before background thread
        file_content = None
        detected_filename = None

        try:
            if uploaded_file:
                file_content = uploaded_file.read()
                detected_filename = uploaded_file.name
                file_size_mb = len(file_content) / (1024 * 1024)
                status_placeholder.info(f"📄 File received: {detected_filename} ({file_size_mb:.2f} MB)")
                progress_bar.progress(5)

                if file_size_mb > 10:
                    status_placeholder.warning(f"📦 Large file ({file_size_mb:.1f}MB). Compressing…")
                    progress_bar.progress(7)
                    try:
                        compressed_content, final_size_mb, _, _ = smart_pdf_compression(file_content, target_size_mb=10)
                        file_content = compressed_content
                        status_placeholder.success(f"✅ Compression: {file_size_mb:.1f}MB → {final_size_mb:.1f}MB")
                        progress_bar.progress(10)
                    except Exception as ce:
                        status_placeholder.error(f"Compression failed, continuing uncompressed: {ce}")
                        progress_bar.progress(10)

                # Optional light content analysis only for very large originals
                if file_size_mb > 10:
                    try:
                        status_placeholder.info("📝 Analyzing text content…")
                        progress_bar.progress(12)
                        pdf_analysis = analyze_pdf_content(file_content)
                        wc = pdf_analysis.get('word_count', 0)
                        if wc == 0:
                            st.error("❌ No extractable text found.")
                            st.session_state.is_generating_course = False
                            return
                        if wc > MAX_CONTENT_WORDS:
                            st.error(f"❌ Too many words ({wc:,} > {MAX_CONTENT_WORDS:,}). Upload a shorter document.")
                            st.session_state.is_generating_course = False
                            return
                        status_placeholder.success(f"✅ Content validated: {wc:,} words")
                        progress_bar.progress(14)
                    except Exception as ae:
                        st.error(f"❌ Analysis error: {ae}")
                        st.session_state.is_generating_course = False
                        return
                status_placeholder.info("🚀 Launching background AI generation…")
                progress_bar.progress(15)
            else:
                # URL path
                parsed = urllib.parse.urlparse(pdf_url)
                detected_filename = os.path.basename(parsed.path) or "downloaded_file"
                status_placeholder.info(f"🔗 Using URL source: {pdf_url}")
                progress_bar.progress(5)

            # Start / resume background job
            job_id = st.session_state.get('active_course_job_id')
            if not job_id:
                job_id = start_course_generation(
                    file_content=file_content if uploaded_file else None,
                    file_url=None if uploaded_file else pdf_url,
                    filename=detected_filename,
                    generate_course_fn=generate_course
                )
                st.session_state.active_course_job_id = job_id

            # Poll loop
            last_progress = -1
            stagnation_start = time.time()
            while True:
                job = get_job(job_id)
                if not job:
                    status_placeholder.error("❌ Lost track of background job.")
                    st.session_state.is_generating_course = False
                    st.session_state.pop('active_course_job_id', None)
                    return
                progress = job.get('progress', 0)
                message = job.get('message', '')
                progress_bar.progress(int(progress))
                phases_placeholder.empty()
                render_phase_timeline(progress, message)

                # Stagnation detection (no progress change for 120s while running)
                if progress != last_progress:
                    last_progress = progress
                    stagnation_start = time.time()
                else:
                    if job.get('status') == 'running' and (time.time() - stagnation_start) > 120:
                        st.warning("Progress appears stalled. You can wait or cancel & retry.")

                if job.get('status') in {"done", "error"}:
                    break
                time.sleep(0.8)

            # Terminal states
            if job.get('status') == 'error':
                st.error(f"❌ Generation failed: {job.get('error') or job.get('message')}")
                st.session_state.is_generating_course = False
                st.session_state.pop('active_course_job_id', None)
                return

            course_data = job.get('result')
            if not course_data:
                st.error("❌ No course data returned.")
                st.session_state.is_generating_course = False
                st.session_state.pop('active_course_job_id', None)
                return

            status_placeholder.success("✅ Course created! Saving…")
            progress_bar.progress(100)

            # Title extraction fallback logic
            if hasattr(course_data, 'course_title') and getattr(course_data, 'course_title'):
                course_title = course_data.course_title
            elif isinstance(course_data, dict) and 'course_title' in course_data:
                course_title = course_data['course_title']
            else:
                course_title = f"📄 {detected_filename.replace('.pdf','')}" if uploaded_file else "🔗 Course from URL"

            generated_course_id = None
            save_error = False
            if MONGO_AVAILABLE:
                try:
                    course_manager = get_course_manager()
                    is_guest = not st.session_state.get('authentication_status', False)
                    if is_guest:
                        session_id = get_session_id()
                        creator = session_id
                    else:
                        session_id = None
                        creator = st.session_state.get('username', 'unknown_user')

                    if hasattr(course_data, 'sections'):
                        sections_to_save = course_data.sections
                    elif isinstance(course_data, dict) and 'sections' in course_data:
                        sections_to_save = course_data['sections']
                    else:
                        sections_to_save = course_data

                    generated_course_id, save_db_error = course_manager.save_course(
                        course_data=sections_to_save,
                        course_title=course_title,
                        creator=creator,
                        is_guest=is_guest,
                        session_id=session_id,
                        is_public=True
                    )
                    if save_db_error:
                        st.error(f"❌ Failed to save course: {save_db_error}")
                        save_error = True
                except Exception as save_exc:
                    st.error(f"❌ Critical save error: {save_exc}")
                    save_error = True
            else:
                st.warning("⚠️ MongoDB not available. Course not persisted.")
                save_error = True

            if not save_error and generated_course_id:
                st.session_state.current_course_id = generated_course_id
                if not st.session_state.get('authentication_status'):
                    increment_guest_course_count()
                # Housekeeping
                st.session_state.is_generating_course = False
                st.session_state.current_uploaded_file = None
                st.session_state.current_pdf_url = None
                st.session_state.pop('active_course_job_id', None)
                time.sleep(1.0)
                st.switch_page("pages/3_Course.py")
            else:
                st.error("Course generated but not saved. You may retry.")
                st.session_state.is_generating_course = False
                st.session_state.current_uploaded_file = None
                st.session_state.current_pdf_url = None
                st.session_state.pop('active_course_job_id', None)
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.session_state.is_generating_course = False
            st.session_state.pop('active_course_job_id', None)

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

                
# --- PDF Compression Functions ---
def compress_pdf(pdf_content, target_size_mb=10):
    """
    Compress a PDF using multiple strategies to achieve significant size reduction.
    
    Args:
        pdf_content (bytes): Original PDF content
        target_size_mb (int): Target size in MB
        
    Returns:
        tuple: (compressed_pdf_bytes, compression_ratio, success)
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter
        
        # Check if compression is needed
        original_size = len(pdf_content)
        original_size_mb = original_size / (1024 * 1024)
        
        if original_size_mb <= target_size_mb:
            return pdf_content, 1.0, True
            
        # Strategy 1: Basic PyPDF2 compression
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        pdf_writer = PdfWriter()
        
        # Apply basic compression to all pages
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            
            # Apply content stream compression
            try:
                page.compress_content_streams()
            except (AttributeError, Exception):
                pass
            
            pdf_writer.add_page(page)
        
        # Get compressed result
        compressed_pdf = io.BytesIO()
        pdf_writer.write(compressed_pdf)
        compressed_content = compressed_pdf.getvalue()
        compressed_size_mb = len(compressed_content) / (1024 * 1024)
        
        # If still too large, try page reduction strategy
        if compressed_size_mb > target_size_mb:
            total_pages = len(pdf_reader.pages)
            
            # Calculate how many pages we can keep
            target_ratio = target_size_mb / compressed_size_mb
            pages_to_keep = max(1, int(total_pages * target_ratio * 0.9))  # Keep 90% of calculated ratio for safety
            
            if pages_to_keep < total_pages:
                # Create a new PDF with subset of pages
                pdf_writer_subset = PdfWriter()
                
                for page_num in range(pages_to_keep):
                    page = pdf_reader.pages[page_num]
                    try:
                        page.compress_content_streams()
                    except Exception:
                        pass
                    pdf_writer_subset.add_page(page)
                
                # Get subset result
                subset_pdf = io.BytesIO()
                pdf_writer_subset.write(subset_pdf)
                subset_content = subset_pdf.getvalue()
                subset_size_mb = len(subset_content) / (1024 * 1024)
                
                if subset_size_mb <= target_size_mb:
                    compression_ratio = len(subset_content) / original_size
                    return subset_content, compression_ratio, True
        
        # Return the best compression we achieved
        compression_ratio = len(compressed_content) / original_size
        return compressed_content, compression_ratio, True
        
    except Exception:
        # If compression fails, return original content
        return pdf_content, 1.0, False

def smart_pdf_compression(pdf_content, target_size_mb=10):
    """
    Smart PDF compression with multiple strategies and detailed feedback.
    
    Args:
        pdf_content (bytes): Original PDF content
        target_size_mb (int): Target size in MB
        
    Returns:
        tuple: (final_pdf_bytes, final_size_mb, compression_ratio, success_message)
    """
    original_size = len(pdf_content)
    original_size_mb = original_size / (1024 * 1024)
    
    if original_size_mb <= target_size_mb:
        return pdf_content, original_size_mb, 1.0, "No compression needed"
    
    # Try aggressive compression
    compressed_content, compression_ratio, success = compress_pdf(pdf_content, target_size_mb)
    
    if success:
        final_size_mb = len(compressed_content) / (1024 * 1024)
        
        # Provide detailed feedback based on compression achieved
        if final_size_mb <= target_size_mb:
            if compression_ratio < 0.5:  # More than 50% reduction
                strategy = "Aggressive compression with significant size reduction"
            elif compression_ratio < 0.8:  # 20-50% reduction  
                strategy = "Standard compression"
            else:  # Less than 20% reduction
                strategy = "Basic compression"
                
            return compressed_content, final_size_mb, compression_ratio, f"✅ {strategy}: {original_size_mb:.1f}MB → {final_size_mb:.1f}MB"
        else:
            # Even with compression, still too large
            if compression_ratio < 0.7:  # At least 30% reduction achieved
                return compressed_content, final_size_mb, compression_ratio, f"⚠️ Compressed {original_size_mb:.1f}MB → {final_size_mb:.1f}MB but still above {target_size_mb}MB limit"
            else:
                return compressed_content, final_size_mb, compression_ratio, f"❌ Minimal compression achieved: {original_size_mb:.1f}MB → {final_size_mb:.1f}MB (still above {target_size_mb}MB)"
    else:
        return pdf_content, original_size_mb, 1.0, "❌ Compression failed - using original file"

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error in main function: {e}")
        st.write("Debug info:", str(e))
        # Still show basic UI
        st.title("🧠 AI Loom")
        st.write("There was an error loading the page. Please refresh.")

# Always show footer regardless of main function issues
# Footer with legal links
st.markdown("""
---
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: rgba(255,255,255,0.7); font-size: 0.9rem;">
    <p>© 2025 AI Loom. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

# Footer navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    # Disable privacy button during course generation
    privacy_disabled = st.session_state.get('is_generating_course', False)
    if st.button("🔒 Privacy Policy", use_container_width=True, key="footer_privacy", disabled=privacy_disabled):
        st.switch_page("pages/4_Privacy.py")
with col2:
    st.markdown('<div style="text-align: center; padding: 1rem;">•</div>', unsafe_allow_html=True)
with col3:
    # Disable terms button during course generation
    terms_disabled = st.session_state.get('is_generating_course', False)
    if st.button("📋 Terms & Conditions", use_container_width=True, key="footer_terms", disabled=terms_disabled):
        st.switch_page("pages/5_Terms.py")
