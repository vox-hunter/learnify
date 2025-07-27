"""
Home Page - Main course generation interface
"""
import streamlit as st
import sys
import os
from streamlit_cookies_manager import EncryptedCookieManager
import io

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Add the parent directory (Quiz app) to sys.path to allow imports from it
# __file__ is pages/1_🏠_Home.py -> dirname is pages -> dirname is Quiz app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    MONGO_AVAILABLE = True
except ImportError as e:
    # Don't show error immediately - just set flag
    MONGO_AVAILABLE = False
    # Store error for later display if needed
    st.session_state['mongo_import_error'] = str(e)
    
    # Provide fallback functions
    def analyze_pdf_content(content):
        return {"word_count": 1000}  # Fallback
    
    def analyze_file_content(file_content, filename):
        """
        Analyze any text-based file content.
        For PDFs, extract text for faster processing.
        For other files, let AI handle them directly (more reliable).
        """
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if file_ext == 'pdf':
            # Use PDF text extraction for faster processing
            try:
                pdf_analysis = analyze_pdf_content(file_content)
                return {
                    'file_type': 'pdf',
                    'word_count': pdf_analysis.get('word_count', 0),
                    'extracted_text': pdf_analysis.get('extracted_text', ''),
                    'error': pdf_analysis.get('error')
                }
            except Exception as e:
                return {
                    'file_type': 'pdf',
                    'word_count': 0,
                    'extracted_text': '',
                    'error': f"PDF processing error: {str(e)}"
                }
        else:
            # For non-PDF files, just validate they're readable and let AI handle extraction
            try:
                # Quick validation - try to read the file
                if file_ext in ['txt', 'md', 'markdown', 'csv', 'json', 'xml', 'html', 'htm']:
                    # Text files - do basic word count
                    text_content = file_content.decode('utf-8', errors='ignore')
                    word_count = len(text_content.split())
                    return {
                        'file_type': file_ext,
                        'word_count': word_count,
                        'extracted_text': text_content[:1000] + '...' if len(text_content) > 1000 else text_content,
                        'error': None
                    }
                else:
                    # Binary files (docx, doc, etc.) - let AI handle them
                    return {
                        'file_type': file_ext,
                        'word_count': None,  # Unknown, let AI handle
                        'extracted_text': f"[{file_ext.upper()} file - will be processed by AI]",
                        'error': None
                    }
            except Exception as e:
                return {
                    'file_type': file_ext,
                    'word_count': 0,
                    'extracted_text': '',
                    'error': f"File reading error: {str(e)}"
                }
    
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
        st.subheader("📄 Upload your document")
        st.markdown("🎯 **Upload ANY text-based file!** We support:")
        st.markdown("• **Documents:** PDF, DOCX, DOC, RTF, TXT")
        st.markdown("• **Code & Data:** JSON, CSV, XML, HTML")  
        st.markdown("• **Markup:** Markdown, TeX, HTML")
        st.markdown("• **And more!** Any file containing text can be processed by our AI")
        st.markdown("---")
        uploaded_file = st.file_uploader(
            "Choose any text-based document",
            type=["pdf", "txt", "docx", "doc", "rtf", "md", "markdown", "tex", "csv", "json", "xml", "html", "htm"],
            help="📁 Upload ANY text file! PDFs, Word docs, text files, markdown, CSV, JSON, XML, HTML - we support them all! Large files are automatically optimized.",
            label_visibility="collapsed"
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            file_size_mb = file_size / (1024*1024)
              # Show file info and size warning if large
            if file_size > 10 * 1024 * 1024:
                st.warning(f"📦 Large file detected: {file_size_mb:.1f} MB (above 10MB limit)")
                st.info("💡 **Note:** File will be automatically compressed during course generation to fit within limits.")
            if uploaded_file:
                if file_size > 10 * 1024 * 1024:
                    # Large file: do quick validation only
                    try:
                        # Quick validation - just check if file is readable
                        file_content = uploaded_file.getvalue()
                        file_ext = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else ''
                        
                        if file_ext == 'pdf' and not file_content.startswith(b'%PDF'):
                            st.error("❌ Invalid PDF file format detected.")
                            uploaded_file = None
                        else:
                            # For large files, just show basic info and let AI handle the rest
                            st.success(f"📄 Large file uploaded: {uploaded_file.name} ({file_size_mb:.1f} MB)")
                            st.info("🤖 File will be processed by AI during course generation (optimized for large files)")
                    except Exception as e:
                        st.error(f"❌ Error reading file: {str(e)}")
                        uploaded_file = None
                else:
                    # Small file: do analysis during upload
                    try:
                        file_analysis = analyze_file_content(uploaded_file.getvalue(), uploaded_file.name)
                        
                        if file_analysis['error']:
                            st.error(f"❌ {file_analysis['error']}")
                            uploaded_file = None
                        else:
                            file_type = file_analysis['file_type'].upper()
                            word_count = file_analysis['word_count']
                            
                            if word_count and word_count > 15000:
                                st.error(f"❌ File contains too many words ({word_count:,}). Maximum allowed: 15,000 words.")
                                st.info("💡 **Tip:** Try uploading a shorter document or specific sections.")
                                uploaded_file = None
                            elif word_count == 0 and file_analysis['file_type'] == 'pdf':
                                st.error("❌ Could not extract text from this PDF. Please try a different file.")
                                uploaded_file = None
                            else:
                                # Success message based on file type
                                if word_count:
                                    st.success(f"📄 {file_type} file processed: {uploaded_file.name} ({file_size_mb:.1f} MB, {word_count:,} words)")
                                else:
                                    st.success(f"📄 {file_type} file uploaded: {uploaded_file.name} ({file_size_mb:.1f} MB) - ready for AI processing")
                            
                            if word_count > 12000:
                                st.warning("⚠️ Large document detected. Generation may take longer than usual.")
                                
                    except Exception as e:
                        st.error(f"❌ Error analyzing PDF: {str(e)}")
                        uploaded_file = None
    
    with tab2:
        st.subheader("🔗 Enter PDF URL")
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
            st.info("⚠️ **Limits:** Maximum 10MB file size, 15,000 words")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Check if user can generate courses
    can_generate = check_course_limit()
    
    if st.session_state.get('is_generating_course', False):
        st.button("🤖 Generating Course...", disabled=True, key="generating_btn")        # Show progress
        show_generation_progress()
    elif can_generate:
        if st.button("✨ Generate Course", type="primary", key="generate_btn"):
            if uploaded_file or pdf_url:
                # Double-check course limit before generating
                if not check_course_limit():
                    st.error("🔐 Course limit reached. Please login to continue.")
                    st.rerun()  # Rerun to show the main UI again
                    
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
    
    # Sidebar is now handled by main.py for consistency

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
            progress_bar.progress(progress_percent / 100)
            status_text.text(status_message)
            import time
            time.sleep(1.5)  # Allow users to read the status
        
        try:
            # Handle file compression if needed before generation
            if uploaded_file:
                # Check file size and compress if necessary
                file_content = uploaded_file.read()
                file_size_mb = len(file_content) / (1024 * 1024)
                
                if file_size_mb > 10:
                    status_text.text(f"📦 Large file detected ({file_size_mb:.1f}MB). Compressing...")
                    progress_bar.progress(5)
                      # Compress the file
                    compressed_content, final_size_mb, _, _ = smart_pdf_compression(
                        file_content, target_size_mb=10
                    )
                    
                    if final_size_mb <= 10:
                        status_text.text(f"✅ Compression successful: {file_size_mb:.1f}MB → {final_size_mb:.1f}MB")
                        progress_bar.progress(10)
                        import time
                        time.sleep(1.0)  # Show compression success briefly
                        file_content = compressed_content
                    else:
                        # Compression didn't achieve target, but continue anyway
                        status_text.text(f"⚠️ Partial compression: {file_size_mb:.1f}MB → {final_size_mb:.1f}MB")
                        progress_bar.progress(10)
                        import time
                        time.sleep(1.0)
                        file_content = compressed_content                
                # For large files that were compressed, validate word count on compressed content
                if file_size_mb > 10:
                    status_text.text("📝 Analyzing compressed file content...")
                    progress_bar.progress(12)
                    
                    try:
                        # Use general file analysis instead of PDF-specific
                        file_analysis = analyze_file_content(file_content, uploaded_file.name)
                        
                        if file_analysis['error']:
                            status_text.text("❌ Analysis failed: file processing error")
                            st.error(f"❌ {file_analysis['error']}")
                            st.session_state.is_generating_course = False
                            st.rerun()
                        else:
                            word_count = file_analysis['word_count']
                            file_type = file_analysis['file_type'].upper()
                            
                            if word_count and word_count > 15000:
                                status_text.text("❌ Analysis failed: too many words even after compression")
                                st.error(f"❌ Compressed {file_type} file still contains too many words ({word_count:,}). Maximum allowed: 15,000 words.")
                                st.info("💡 **Tip:** Try uploading a shorter document or specific sections.")
                                st.session_state.is_generating_course = False
                                st.rerun()
                            elif word_count == 0 and file_analysis['file_type'] == 'pdf':
                                status_text.text("❌ Analysis failed: no text found")
                                st.error("❌ Could not extract text from the compressed PDF. Please try a different file.")
                                st.session_state.is_generating_course = False
                                st.rerun()
                            else:
                                if word_count:
                                    status_text.text(f"✅ {file_type} content validated: {word_count:,} words found")
                                else:
                                    status_text.text(f"✅ {file_type} file ready for AI processing")
                                progress_bar.progress(14)
                            
                    except Exception as e:
                        status_text.text("❌ Analysis failed: error reading content")
                        st.error(f"❌ Error analyzing compressed PDF: {str(e)}")
                        st.session_state.is_generating_course = False
                        st.rerun()  # Rerun to show the main UI again
                
                # Reset file pointer and generate course
                status_text.text("🚀 Starting course generation...")
                progress_bar.progress(15)
                
                course_data, error_message = generate_course(
                    file_content=file_content, 
                    status_callback=status_callback
                )
            else:
                # URL-based generation (no compression needed)
                course_data, error_message = generate_course(
                    file_url=pdf_url, 
                    status_callback=status_callback
                )
            
            if course_data and not error_message:
                # Process successful generation
                progress_bar.progress(100)
                status_text.text("✅ Course created successfully! Processing save...")

                # Extract AI-generated course title or use fallback
                if hasattr(course_data, 'course_title') and course_data.course_title:
                    course_title = course_data.course_title
                elif isinstance(course_data, dict) and 'course_title' in course_data:
                    course_title = course_data['course_title']
                else:
                    # Fallback to file-based naming if AI didn't provide a title
                    if uploaded_file:
                        course_title = f"📄 {uploaded_file.name.replace('.pdf', '')}"
                    else:
                        course_title = "🔗 Course from URL"

                generated_course_id = None  # Will store the ID if successfully saved
                save_error_occurred = False

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
                        
                        # Extract sections from course_data for saving
                        if hasattr(course_data, 'sections'):
                            sections_to_save = course_data.sections
                        elif isinstance(course_data, dict) and 'sections' in course_data:
                            sections_to_save = course_data['sections']
                        else:
                            # Fallback: assume course_data is already the sections list
                            sections_to_save = course_data
                        
                        temp_mongo_id, save_db_error = course_manager.save_course(
                            course_data=sections_to_save,
                            course_title=course_title,
                            creator=creator,
                            is_guest=is_guest,
                            session_id=session_id,
                            is_public=True 
                        )
                        
                        if save_db_error:
                            st.error(f"❌ Failed to save course to database: {save_db_error}")
                            save_error_occurred = True
                        else:
                            generated_course_id = temp_mongo_id
                            if generated_course_id: # Ensure generated_course_id is not None
                                st.query_params["course_id"] = str(generated_course_id)
                                status_text.text("✅ Course saved! Redirecting...")
                            else:
                                st.error("❌ Failed to get a valid course ID after saving.")
                                save_error_occurred = True
                                
                    except Exception as e_mongo_save:
                        st.error(f"❌ Critical error during course saving: {e_mongo_save}")
                        save_error_occurred = True
                else:
                    st.warning("⚠️ MongoDB not available. Course generated but not saved persistently.")
                    # For non-MongoDB (session-based) flow, we might need a different ID mechanism
                    # For now, if Mongo is the target, this is effectively a save failure for persistence.
                    save_error_occurred = True 

                if not save_error_occurred and generated_course_id:
                    st.session_state.current_course_id = generated_course_id
                    
                    if not st.session_state.get('authentication_status'):
                        increment_guest_course_count()
                    st.session_state.is_generating_course = False
                    st.session_state.current_uploaded_file = None
                    st.session_state.current_pdf_url = None
                    
                    import time
                    time.sleep(1.5) # Allow messages to be seen
                    st.switch_page("pages/3_Course.py")
                else:
                    # Save failed or MONGO_AVAILABLE was false and no alternative ID was generated
                    status_text.error("Course generation finished, but could not be saved for persistent access.")
                    st.session_state.is_generating_course = False
                    st.session_state.current_uploaded_file = None
                    st.session_state.current_pdf_url = None
                    # Do not redirect, allow user to see the error and try again.
                    
            else:  # error_message from local_backend.generate_course
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
    if st.button("🔒 Privacy Policy", use_container_width=True, key="footer_privacy"):
        st.switch_page("pages/4_Privacy.py")
with col2:
    st.markdown('<div style="text-align: center; padding: 1rem;">•</div>', unsafe_allow_html=True)
with col3:
    if st.button("📋 Terms & Conditions", use_container_width=True, key="footer_terms"):
        st.switch_page("pages/5_Terms.py")
