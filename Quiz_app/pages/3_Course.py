import streamlit as st
import json
import sys  # Add sys import
import os  # Add os import
import random
import time
import datetime
import html
import re

def sanitize_inline(text: str) -> str:
    """Return a safe HTML fragment for inline insertion.

    Changes:
      - Fixed indentation issues.
      - Removed blanket escaping of all angle brackets (which produced visible artifacts like '&gt;').
      - Strips disallowed tags instead of escaping them.
      - Cleans common leading artifact patterns left after tag stripping (e.g. stray quote + angle remnants).
      - Keeps a conservative allowlist of inline-safe tags.
    """
    if not text:
        return ""
    try:
        t = html.unescape(str(text))
        t = re.sub(r'<\s*(script|style)[^>]*>.*?<\/\s*\1\s*>', '', t, flags=re.IGNORECASE | re.DOTALL)
        t = re.sub(r'<!--.*?-->', '', t, flags=re.DOTALL)
        allowed = {'b', 'strong', 'i', 'em', 'code', 'br', 'ul', 'ol', 'li', 'p', 'span', 'u', 'sub', 'sup', 'small'}

        def repl(match):
            full = match.group(0)
            name = match.group(1).lower().lstrip('/')
            return full if name in allowed else ''

        t = re.sub(r'</?([a-zA-Z0-9]+)(?:\s+[^>]*)?>', repl, t)
        t = re.sub(r'^["\']&gt;\s*', '', t)
        t = re.sub(r'^["\']>\s*', '', t)
        t = re.sub(r'\s{2,}', ' ', t).strip()
        return t
    except Exception:
        return html.escape(str(text))

# --- Artifact cleanup helper (targets stray leading characters like "&gt; or ">) ---
_LEADING_ARTIFACT_RE = re.compile(r'^[\s]*(["\']?(?:&gt;|>))+\s*')

def strip_leading_artifacts(text: str) -> str:
        """Remove stray leading quote/greater-than escape artifacts left from prior escaping.

        Examples removed:
            "> What is photosynthesis?" -> "What is photosynthesis?"
            "&gt; Explain X"           -> "Explain X"
            "'&gt;Term"               -> "Term"
        Safe: only trims if pattern matches at very start; leaves interior symbols intact.
        """
        if not text:
                return ""
        return _LEADING_ARTIFACT_RE.sub('', str(text))

def safe_str_convert(value):
    """Safely convert any value to string for Streamlit text widgets"""
    if value is None:
        return ""
    try:
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2)
        elif isinstance(value, (str, int, float, bool)):
            return str(value)
        else:
            # For any other type, convert to string
            return str(value)
    except (TypeError, ValueError, AttributeError):
        # If conversion fails, use empty string
        return ""

# Add the parent directory (Quiz app) to sys.path to allow imports from it
# __file__ is pages/3_📚_Course.py -> dirname is pages -> dirname is Quiz app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from st_fill_in_the_blanks import fill_in_the_blanks_input
    FILL_IN_BLANKS_AVAILABLE = True
except ImportError:
    FILL_IN_BLANKS_AVAILABLE = False
    fill_in_the_blanks_input = None
    st.warning("Fill-in-the-blanks component not available - using fallback text input")
    
try:
    import local_backend
except ImportError:
    local_backend = None
    st.warning("Local backend not available for AI validation")

try:
    from mongo_course_manager import get_course_manager, get_session_id
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# Navigation cache utilities (lightweight)
try:
    from utils.navigation_cache import get_cached_course, cache_course
except Exception:  # Fallback if not present
    def get_cached_course(_):
        return None
    def cache_course(_, __):
        return None

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

# Initialize session state function
def initialize_session_state():
    """Initialize all session state variables"""
    # Remove current_section_index since we're using progressive display
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
    if "course_finished" not in st.session_state:
        st.session_state.course_finished = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    if "course_overview_shown" not in st.session_state:
        st.session_state.course_overview_shown = False
    if "course_started_properly" not in st.session_state:
        st.session_state.course_started_properly = False
    if "course_ended_early" not in st.session_state:
        st.session_state.course_ended_early = False

def reset_course_session_state():
    """Reset course-specific session state when starting a new course"""
    # Reset course progress data
    st.session_state.user_answers = {}
    st.session_state.checked_answers = {}
    st.session_state.current_score = 0
    st.session_state.total_questions_in_course = 0
    st.session_state.scored_correctly_keys = set()
    st.session_state.feedback = {}
    st.session_state.course_finished = False
    st.session_state.start_time = time.time()
    
    # Reset overview and course state flags
    st.session_state.course_overview_shown = False
    st.session_state.course_started_properly = False
    st.session_state.course_ended_early = False
    
    # Clear any cached question counts
    keys_to_remove = [key for key in st.session_state.keys() if str(key).startswith('total_questions_')]
    for key in keys_to_remove:
        del st.session_state[key]

# Initialize session state
initialize_session_state()

def is_localhost():
    """Check if the app is running on localhost."""
    try:
        # Get the server address from Streamlit's config
        server_address = st.get_option('server.address')
        
        # Check if the address is localhost or the local IP
        if server_address in ['localhost', '127.0.0.1', '0.0.0.0']:
            return True
            
        # Fallback for other local IPs
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        return server_address == local_ip
    except (AttributeError, ImportError, ConnectionError):
        # If any error occurs, assume it's not localhost for safety
        return False

def is_admin_user():
    """Check if admin features should be enabled for specific admin users."""
    username = st.session_state.get('username', '')
    email = st.session_state.get('email', '')
    
    admin_usernames = ["vidyut"]
    admin_emails = ["vidyuts@gardenbangkok.com"]

    return username in admin_usernames or email in admin_emails

def mark_all_section_questions_correct(course_data, section_index, course_id):
    """Mark all questions in a section as correct (admin function)"""
    if section_index >= len(course_data):
        return False
    
    section_key = f"course_{course_id}_sec_{section_index}"
    section_data = course_data[section_index]
    
    # Mark main section questions as correct
    _mark_section_questions_correct_recursive(section_data, section_key)
    
    return True

def _mark_section_questions_correct_recursive(section_data, section_key):
    """Recursively mark all questions in a section and its subsections as correct"""
    # Check if section_data is a Pydantic model or dict
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    if is_pydantic_model:
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        questions = section_data.get('quiz', section_data.get('questions', []))
        subsections = section_data.get('subsections', [])
    
    # Handle None values
    if questions is None:
        questions = []
    if subsections is None:
        subsections = []
    
    # Mark main section questions as correct
    if questions:
        for i, _ in enumerate(questions):
            question_key = f"{section_key}_q_{i}"
            
            # Mark as answered correctly
            st.session_state.checked_answers[question_key] = True
            st.session_state.user_answers[question_key] = "Admin Override"
            
            # Add to score tracking if not already counted
            if question_key not in st.session_state.scored_correctly_keys:
                st.session_state.current_score += 1
                st.session_state.scored_correctly_keys.add(question_key)
            
            # Add feedback
            st.session_state.feedback[question_key] = "Correct! (Admin Override)"
    
    # Mark subsection questions as correct
    if subsections:
        for sub_idx, subsection in enumerate(subsections):
            subsection_key = f"{section_key}_sub_{sub_idx}"
            _mark_section_questions_correct_recursive(subsection, subsection_key)

# Apply ultra-modern CSS styling
st.markdown("""
<style>
    /* Cache buster: 2025-07-02-14:15 - Force CSS reload */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Hide cookies manager and reduce top spacing */
    iframe[title*="cookie_manager"], 
    iframe[src*="cookie_manager"],
    iframe[title*="streamlit_cookies_manager"],
    iframe[src*="streamlit_cookies_manager"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    /* Hide any empty custom components that might be taking space */
    div[data-testid="stAppViewContainer"] > div:first-child:empty {
        display: none !important;
    }
    
    /* Target the specific custom component container for cookies manager */
    .stCustomComponentV1:has(iframe[src*="cookie_manager"]) {
        display: none !important;
        height: 0px !important;
        width: 0px !important;
    }
    
    /* Hide empty custom component containers */
    .stCustomComponentV1[data-testid="stCustomComponentV1"]:has(iframe[height="0"]) {
        display: none !important;
    }
    
    /* Additional targeting for any wrapper elements */
    div[data-testid="stVerticalBlock"] > div:first-child:empty,
    div[data-testid="stVerticalBlock"] > div:first-child:has(iframe[src*="cookie"]) {
        display: none !important;
        height: 0px !important;
    }
    
    /* Remove top padding/margin from main container */
    .main .block-container {
        padding-top: 1rem !important;
        margin-top: 0rem !important;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Course container */
    .course-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Course title with animated gradient */
    .course-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #06b6d4 0%, #0ea5e9 25%, #3b82f6 50%, #6366f1 75%, #8b5cf6 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        text-align: center;
        animation: gradientShift 8s ease infinite;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Section title with glow effect */
    .section-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #06b6d4;
        margin-bottom: 1.5rem;
        position: relative;
        text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #06b6d4, #0ea5e9);
        border-radius: 2px;
    }
    
    /* Navigation container */
    .nav-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Modern pill buttons */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 16px 32px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.4);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0891b2 0%, #0284c7 100%);
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 16px 40px rgba(6, 182, 212, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(1.02);
    }
    
    .stButton > button:disabled {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        transform: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        opacity: 0.6;
    }
    
    /* Enhanced progress bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .progress-stats {
        display: flex;
        justify-content: space-around;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        flex: 1;
        min-width: 120px;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #06b6d4, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
    }
    
    .stat-label {
        color: #a0aec0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    /* Question card styling */
    .question-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .question-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #06b6d4, #0ea5e9, #3b82f6);
        background-size: 200% 200%;
        animation: gradientShift 3s ease infinite;
    }
    
    .question-card:hover {
        border-color: rgba(6, 182, 212, 0.5);
        background: rgba(255, 255, 255, 0.12);
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(6, 182, 212, 0.3);
    }
    
    .question-number {
        display: inline-block;
        background: linear-gradient(135deg, #06b6d4, #0ea5e9);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
    }
    
    .question-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Enhanced form controls */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stRadio > div > label:hover {
        background: rgba(6, 182, 212, 0.1);
        border-color: rgba(6, 182, 212, 0.3);
        transform: translateX(8px);
    }
    
    /* Text inputs with modern styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        color: #e2e8f0;
        padding: 16px 20px;
        font-size: 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #06b6d4;
        box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.2);
        background: rgba(255, 255, 255, 0.12);
        outline: none;
    }
    
    /* Enhanced feedback messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.2), rgba(56, 178, 172, 0.2));
        border: 1px solid rgba(72, 187, 120, 0.4);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 24px rgba(72, 187, 120, 0.2);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.2), rgba(229, 62, 62, 0.2));
        border: 1px solid rgba(245, 101, 101, 0.4);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 24px rgba(245, 101, 101, 0.2);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(66, 153, 225, 0.2), rgba(6, 182, 212, 0.2));
        border: 1px solid rgba(66, 153, 225, 0.4);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 24px rgba(66, 153, 225, 0.2);
    }
    
    /* Admin controls styling */
    .admin-section {
        background: linear-gradient(135deg, rgba(237, 137, 54, 0.1), rgba(245, 166, 35, 0.1));
        border: 1px solid rgba(237, 137, 54, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(237, 137, 54, 0.2);
    }
    
    /* Completion stats styling */
    .completion-container {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(8, 145, 178, 0.1));
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 16px 48px rgba(6, 182, 212, 0.3);
    }
    
    .completion-score {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #06b6d4, #0ea5e9, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1rem 0;
        text-shadow: 0 0 30px rgba(6, 182, 212, 0.5);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .course-title {
            font-size: 2.5rem;
        }
        
        .section-title {
            font-size: 1.8rem;
        }
        
        .question-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .progress-stats {
            flex-direction: column;
        }
        
        .nav-container {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Cache for course data to avoid repeated database calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
def _load_course_from_mongo(course_id, user_identifier, session_id):
    """Cached function to load course data from MongoDB"""
    if not MONGO_AVAILABLE:
        return None, "MongoDB not available"
    
    try:
        course_manager = get_course_manager()
        
        # Check if user can access this course
        can_access, access_error = course_manager.can_access_course(
            course_id=course_id,
            user_identifier=user_identifier,
            session_id=session_id
        )
        
        if not can_access:
            return None, access_error
        
        # Load course from MongoDB
        course_doc, load_error = course_manager.get_course(course_id)
        
        if course_doc and not load_error:
            return course_doc['content'], None  # Return the course content
        elif load_error:
            return None, load_error
        else:
            return None, "Course not found"
    except (ImportError, AttributeError, ConnectionError) as e:
        return None, f"Error accessing course database: {e}"

def optimize_session_state():
    """Optimize session state by batching updates and reducing unnecessary flags"""
    # Clear temporary flags that might cause unnecessary reruns
    flags_to_clear = ['privacy_updated', 'fitb_answered', 'match_submitted', 'course_changed']
    for flag in flags_to_clear:
        if flag in st.session_state:
            del st.session_state[flag]

def main():
    # Optimize session state and clear temporary flags
    optimize_session_state()
    
    # Sidebar navigation is now handled by main.py
    
    # Get current course ID from URL or session state
    course_id = get_current_course_id()
    
    if course_id is None:
        st.error("❌ No course selected. Please go back to home and generate a course.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app_pages/1_🏠_Home.py")
        return
    
    # Check if this is a new course (different from the last one)
    if st.session_state.get('last_course_id') != course_id:
        reset_course_session_state()
        st.session_state.last_course_id = course_id
    
    # Load course data (now with caching)
    course_data = load_course_data(course_id)
    
    if not course_data:
        st.error("❌ Course not found. It may have been deleted.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app_pages/1_🏠_Home.py")
        return

    if st.session_state.get('course_finished', False):
        display_course_completion_stats(course_data, course_id)
        return
    
    # Check if overview should be shown (for new course access or if not started properly)
    if not st.session_state.get('course_overview_shown', False) or not st.session_state.get('course_started_properly', False):
        display_course_overview(course_data, course_id)
        return
    
    # MAIN COURSE CONTENT - Only execute when course is started properly
    # Calculate progress for the sticky header
    all_questions_for_progress = []
    for section_idx, section_data in enumerate(course_data):
        is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
        if is_pydantic_model:
            questions = getattr(section_data, "quiz", [])
        else:
            questions = section_data.get('quiz', section_data.get('questions', []))
        
        if questions:
            for q_idx, _ in enumerate(questions):
                question_key = f"course_{course_id}_sec_{section_idx}_q_{q_idx}"
                all_questions_for_progress.append(question_key)
    
    total_questions_count = len(all_questions_for_progress)
    answered_questions = sum(1 for q_key in all_questions_for_progress if q_key in st.session_state and st.session_state[q_key])
    progress_percentage = (answered_questions / total_questions_count) * 100 if total_questions_count > 0 else 0
    
    # Create a sticky header using a placeholder that we'll update (only for main course content)
    header_placeholder = st.empty()
    with header_placeholder.container():
        st.markdown(f"""
        <style>
        /* Hide sidebar for course experience */
        .css-1d391kg {{display: none;}}
        .css-1rs6os {{display: none;}}
        .stSidebar {{display: none !important;}}
        section[data-testid="stSidebar"] {{display: none !important;}}
        
        /* Adjust main content area */
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: none;
        }}
        </style>
        
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background: rgba(13, 18, 32, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(6, 182, 212, 0.2);
            padding: 15px 20px;
        ">
            <div style="
                width: 100%; 
                height: 20px; 
                background: rgba(255, 255, 255, 0.1); 
                border-radius: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.2); 
                display: flex; 
                overflow: hidden; 
                box-shadow: rgba(0, 0, 0, 0.2) 0px 2px 4px inset; 
                position: relative;
            ">
                <div style="
                    width: {progress_percentage}%; 
                    background: linear-gradient(90deg, rgb(72, 187, 120), rgb(56, 178, 172)); 
                    height: 100%; 
                    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); 
                    box-shadow: rgba(72, 187, 120, 0.5) 0px 0px 10px;
                "></div>
                <div style="
                    width: 0%; 
                    background: linear-gradient(90deg, rgb(245, 101, 101), rgb(229, 62, 62)); 
                    height: 100%; 
                    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); 
                    box-shadow: rgba(245, 101, 101, 0.5) 0px 0px 10px;
                "></div>
                <div style="
                    width: {100 - progress_percentage}%; 
                    background: rgba(255, 255, 255, 0.1); 
                    height: 100%; 
                    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                "></div>
            </div>
            <div style="
                display: flex; 
                justify-content: space-between; 
                font-size: 0.8rem; 
                color: rgb(160, 174, 192); 
                margin-top: 8px;
            ">
                <span>0</span>
                <span style="font-weight: 600; color: rgb(102, 126, 234);">{answered_questions}/{total_questions_count} Answered</span>
                <span>{total_questions_count}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    course_id = get_current_course_id()
    
    if course_id is None:
        st.error("❌ No course selected. Please go back to home and generate a course.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app_pages/1_🏠_Home.py")
        return
    
    # Check if this is a new course (different from the last one)
    if st.session_state.get('last_course_id') != course_id:
        reset_course_session_state()
        st.session_state.last_course_id = course_id
    
    # Load course data (now with caching)
    course_data = load_course_data(course_id)
    
    if not course_data:
        st.error("❌ Course not found. It may have been deleted.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app_pages/1_🏠_Home.py")
        return

    if st.session_state.get('course_finished', False):
        display_course_completion_stats(course_data, course_id)
        return
      # Main course container with enhanced styling
    
    # Course title and info - handle both MongoDB and session data
    course_title = "📚 Course"  # Default title
    
    # Try to get title from MongoDB first
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:
        try:
            course_manager = get_course_manager()
            course_doc, _ = course_manager.get_course(course_id)
            if course_doc:
                course_title = course_doc.get('title', '📚 Course')
        except (ImportError, AttributeError, ConnectionError) as e:
            st.error(f"An error occurred while fetching the course title from MongoDB: {e}")
    
    # Fall back to session state
    if course_title == "📚 Course" and 'course_history' in st.session_state:
        try:
            course_id_int = int(course_id)
            if course_id_int < len(st.session_state.course_history):
                course_title = st.session_state.course_history[course_id_int]['title']
        except (ValueError, TypeError):
            pass
    
    st.markdown(f'<h1 class="course-title">{sanitize_inline(course_title)}</h1>', unsafe_allow_html=True)
    
    # Enhanced course metadata with modern styling
    total_sections = len(course_data)
    
    # Create a modern info card for course metadata
    st.markdown(f"""
    <div class="nav-container">
        <div style="text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #06b6d4; margin-bottom: 0.5rem;">
                📚 {total_sections} Sections - Progressive Learning
            </div>
            <div style="color: #a0aec0; font-size: 0.9rem;">
                Complete sections to unlock the next ones
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Admin controls with enhanced styling (enabled on localhost or for admin users)
    if is_admin_user():
        st.markdown("""
        <div class="admin-section">
            <h3 style="color: #f6ad55; margin-bottom: 1rem; font-weight: 700;">
                🔧 Admin Controls
            </h3>
        """, unsafe_allow_html=True)
        
        # Show localhost indicator
        if is_localhost():
            st.info("💻 Admin features are enabled because you're running on localhost")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Mark Next Question Complete", key="admin_mark_question"):
                # Flatten questions to find next incomplete one
                all_questions = []
                for section_idx, section_data in enumerate(course_data):
                    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
                    if is_pydantic_model:
                        questions = getattr(section_data, "quiz", [])
                    else:
                        questions = section_data.get('quiz', section_data.get('questions', []))
                    
                    if questions:
                        for q_idx, _ in enumerate(questions):
                            question_key = f"course_{course_id}_sec_{section_idx}_q_{q_idx}"
                            all_questions.append(question_key)
                
                # Find first unanswered question
                found_incomplete = False
                for question_key in all_questions:
                    if question_key not in st.session_state or not st.session_state[question_key]:
                        st.session_state[question_key] = True
                        st.success("✅ Marked next question as complete!")
                        found_incomplete = True
                        st.rerun()
                
                if not found_incomplete:
                    st.info("All questions are already complete!")
        
        with col2:
            if st.button("✅ Mark All Questions Complete", key="admin_mark_all"):
                # Flatten questions and mark all as complete
                for section_idx, section_data in enumerate(course_data):
                    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
                    if is_pydantic_model:
                        questions = getattr(section_data, "quiz", [])
                    else:
                        questions = section_data.get('quiz', section_data.get('questions', []))
                    
                    if questions:
                        for q_idx, _ in enumerate(questions):
                            question_key = f"course_{course_id}_sec_{section_idx}_q_{q_idx}"
                            st.session_state[question_key] = True
                
                st.session_state.course_finished = True
                st.success("✅ Marked all questions as complete and finished the course!")
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset Course Progress", key="admin_reset"):
                reset_course_session_state()
                st.success("✅ Course progress reset!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add End Course button (always available during course)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("🔚 End Course", key="end_course_early", use_container_width=True, 
                     help="End the course early and view conclusion"):
            # Set flag for early ending
            st.session_state.course_ended_early = True
            st.session_state.course_finished = True
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display all questions progressively (Seneca-style)
    display_progressive_questions(course_data, course_id)

def get_current_course_id():
    """Get the current course ID from URL params or session state"""
    # First check URL parameters for course_id
    if "course_id" in st.query_params:
        course_id = st.query_params["course_id"]
        # Cache the course_id in session state to avoid repeated URL param reads
        if st.session_state.get('current_course_id') != course_id:
            st.session_state.current_course_id = course_id
        return course_id
    
    # Check URL for section parameter and update session state
    if "section" in st.query_params:
        try:
            section_idx = int(st.query_params["section"])
            if st.session_state.get('current_section_index') != section_idx:
                st.session_state.current_section_index = section_idx
        except (ValueError, TypeError):
            pass
    
    # Check if we have a shared course ID in session state (from redirect)
    if 'shared_course_id' in st.session_state:
        shared_id = st.session_state.shared_course_id
        # Clear it after use to avoid confusion
        del st.session_state.shared_course_id
        st.session_state.current_course_id = shared_id
        return shared_id
    
    # Try to get from session state (for backward compatibility)
    if 'current_course_id' in st.session_state:
        return st.session_state.current_course_id
    
    # If not available, return None
    return None

def load_course_data(course_id):
    """Load course data by ID from MongoDB or session state"""
    # First try to load from MongoDB if available
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:  # MongoDB ObjectId is 24 chars
        # First see if we already have it cached from navigation prefetch
        cached = get_cached_course(course_id)
        if cached is not None:
            return cached
        # Check if user can access this course
        user_identifier = st.session_state.get('username')
        session_id = get_session_id() if not user_identifier else None
        
        # Use cached function to avoid repeated database calls
        course_content, error = _load_course_from_mongo(course_id, user_identifier, session_id)
        
        if course_content and not error:
            cache_course(course_id, course_content)
            return course_content
        elif error:
            st.error(f"❌ Error loading course: {error}")
            return None
    
    # Fall back to session state for backward compatibility
    if 'course_history' not in st.session_state:
        return None
    
    try:
        course_id_int = int(course_id)
        if course_id_int >= len(st.session_state.course_history):
            return None
        
        return st.session_state.course_history[course_id_int]['data']
    except (ValueError, TypeError):
        return None

def show_score_display(course_data):
    """Display modern color-coded progress bar only"""
    total_questions = count_total_questions(course_data)
    
    if total_questions > 0:
        # Get current stats
        correct_answers = st.session_state.get('current_score', 0)
        answered_questions = len(st.session_state.get('checked_answers', {}))
        incorrect_answers = answered_questions - correct_answers
        unanswered_questions = total_questions - answered_questions
        
        # Calculate percentages
        correct_pct = (correct_answers / total_questions) * 100
        incorrect_pct = (incorrect_answers / total_questions) * 100
        unanswered_pct = (unanswered_questions / total_questions) * 100
        
        # Enhanced progress bar with gradient and glow effects
        progress_html = f"""
        <div style="
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
            position: relative;
        ">
            <div style="
                width: {correct_pct}%;
                background: linear-gradient(90deg, #48bb78, #38b2ac);
                height: 100%;
                transition: width 0.8s cubic-bezier(0.4, 0.0, 0.2, 1);
                box-shadow: 0 0 10px rgba(72, 187, 120, 0.5);
            "></div>
            <div style="
                width: {incorrect_pct}%;
                background: linear-gradient(90deg, #f56565, #e53e3e);
                height: 100%;
                transition: width 0.8s cubic-bezier(0.4, 0.0, 0.2, 1);
                box-shadow: 0 0 10px rgba(245, 101, 101, 0.5);
            "></div>
            <div style="
                width: {unanswered_pct}%;
                background: rgba(255, 255, 255, 0.1);
                height: 100%;
                transition: width 0.8s cubic-bezier(0.4, 0.0, 0.2, 1);
            "></div>
        </div>
        <div style="
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #a0aec0;
            margin-top: 8px;
        ">
            <span>0</span>
            <span style="font-weight: 600; color: #06b6d4;">{answered_questions}/{total_questions} Answered</span>
            <span>{total_questions}</span>
        </div>
        """
        
        st.markdown(progress_html, unsafe_allow_html=True)
    else:
        # Show empty state with modern styling
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
            <div style="color: #a0aec0; font-size: 1.1rem;">No questions available in this course</div>
        </div>
        """, unsafe_allow_html=True)

def count_total_questions(course_data):
    """Count total questions in course - optimized version"""
    if not course_data:
        return 0
    
    # Use cached count if available
    cache_key = f"total_questions_{hash(str(course_data))}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
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
    
    # Cache the result
    st.session_state[cache_key] = total
    return total

def are_all_questions_in_section_answered(course_data, section_index):
    """Check if all questions in the current section are answered."""
    if section_index >= len(course_data):
        return False

    # Get the course ID to construct proper question keys
    course_id = st.session_state.get('current_course_id', 'unknown')
    section_key = f"course_{course_id}_sec_{section_index}"
    
    # Check if all questions in this section (and its subsections) are answered
    return _check_section_questions_answered(course_data[section_index], section_key)

def _check_section_questions_answered(section_data, section_key):
    """Recursively check if all questions in a section and its subsections are answered."""
    # Check if section_data is a Pydantic model or dict
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    if is_pydantic_model:
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        questions = section_data.get('quiz', section_data.get('questions', []))
        subsections = section_data.get('subsections', [])
    
    # Handle None values
    if questions is None:
        questions = []
    if subsections is None:
        subsections = []
    
    # Check main section questions
    if questions:
        for i, _ in enumerate(questions):
            question_key = f"{section_key}_q_{i}"
            is_answered = question_key in st.session_state.get('checked_answers', {})
            if not is_answered:
                return False
    
    # Check subsection questions
    if subsections:
        for sub_idx, subsection in enumerate(subsections):
            subsection_key = f"{section_key}_sub_{sub_idx}"
            if not _check_section_questions_answered(subsection, subsection_key):
                return False
    
    return True

def show_course_navigation(course_data, course_id=None):  # course_id kept for API compatibility
    """Show enhanced section navigation with modern styling"""
    total_sections = len(course_data)
    current_section = st.session_state.get('current_section_index', 0)
    
    # Progress indicator
    progress_pct = (current_section / max(total_sections - 1, 1)) * 100
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="color: #a0aec0; font-size: 0.9rem;">Section Progress</span>
            <span style="color: #06b6d4; font-weight: 600;">{current_section + 1}/{total_sections}</span>
        </div>
        <div style="
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
        ">
            <div style="
                width: {progress_pct}%;
                height: 100%;
                background: linear-gradient(90deg, #06b6d4, #0ea5e9);
                transition: width 0.8s cubic-bezier(0.4, 0.0, 0.2, 1);
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_section > 0:
            if st.button("⬅️ Previous Section", key="prev_section_btn"):
                st.session_state.current_section_index = current_section - 1
                st.query_params.section = str(current_section - 1)
                st.rerun()
        else:
            st.button("⬅️ Previous Section", disabled=True, key="prev_section_btn_disabled")
    
    with col2:
        # Section indicator with enhanced styling
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="
                display: inline-block;
                background: linear-gradient(135deg, #06b6d4, #0ea5e9);
                color: white;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: 600;
                font-size: 1rem;
                box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
            ">
                📖 Section {current_section + 1} of {total_sections}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        all_answered = are_all_questions_in_section_answered(course_data, current_section)
        
        # Debug expander with modern styling
        
        
        if current_section < total_sections - 1:
            if st.button("Next Section ➡️", key="next_section_btn", disabled=not all_answered):
                st.session_state.current_section_index = current_section + 1
                st.query_params.section = str(current_section + 1)
                st.rerun()
        else:
            if st.button("🏁 Finish Course", key="finish_course_btn", disabled=not all_answered):
                st.session_state.course_finished = True
                st.rerun()

def display_course_overview(course_data, course_id):
    """Display course overview page before starting the course."""
    
    # Get course title and metadata
    course_title = "📚 Course"  # Default title
    total_sections = len(course_data)
    total_questions = count_total_questions(course_data)
    
    # Try to get title from MongoDB first
    memory_strength = 0
    last_attempt_timestamp = None
    show_memory_tip = False
    course_creator = "Unknown"
    
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:
        try:
            course_manager = get_course_manager()
            course_doc, _ = course_manager.get_course(course_id)
            if course_doc:
                course_title = course_doc.get('title', '📚 Course')
                memory_strength = course_doc.get('memory_strength', 0)
                last_attempt_timestamp = course_doc.get('last_attempt_timestamp')
                course_creator = course_doc.get('creator', 'Unknown')
                
                # Check if it's been more than 24 hours for memory strength upgrade
                if last_attempt_timestamp:
                    current_time = datetime.datetime.now(datetime.timezone.utc)
                    if last_attempt_timestamp.tzinfo is None:
                        last_attempt_timestamp = last_attempt_timestamp.replace(tzinfo=datetime.timezone.utc)
                    time_since_last_attempt = current_time - last_attempt_timestamp
                    if time_since_last_attempt >= datetime.timedelta(hours=24):
                        show_memory_tip = True
        except (ImportError, AttributeError, ConnectionError) as e:
            st.error(f"An error occurred while fetching course data: {e}")
    
    # Fall back to session state for title if needed
    if course_title == "📚 Course" and 'course_history' in st.session_state:
        try:
            course_id_int = int(course_id)
            if course_id_int < len(st.session_state.course_history):
                course_title = st.session_state.course_history[course_id_int]['title']
        except (ValueError, TypeError):
            pass
    
    # Course overview UI
    st.markdown("""
    <style>
    .overview-container {
        background: linear-gradient(135deg, rgba(13, 18, 32, 0.8), rgba(6, 78, 149, 0.1));
        border: 2px solid rgba(6, 182, 212, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .overview-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #06b6d4, #0ea5e9, #f093fb);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
        margin-bottom: 1rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #06b6d4;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .memory-strength {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .memory-warning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
        border: 1px solid rgba(255, 193, 7, 0.5);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="overview-container">', unsafe_allow_html=True)
    
    # Title
    st.markdown(f'<h1 class="overview-title">Course Overview</h1>', unsafe_allow_html=True)
    
    # Course name
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <h2 style="color: #e2e8f0; font-size: 1.5rem; font-weight: 600;">
            {sanitize_inline(course_title)}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats grid
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_sections}</div>
            <div class="stat-label">Sections</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_questions}</div>
            <div class="stat-label">Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Memory strength display
        lightning_icons = []
        for i in range(5):
            if i < memory_strength:
                lightning_icons.append('⚡')
            else:
                lightning_icons.append('⚪')
        memory_display = ''.join(lightning_icons)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="font-size: 1.5rem;">{memory_display}</div>
            <div class="stat-label">Memory Strength</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Removed an extra unmatched closing </div> that caused stray characters ("'>") to appear
    # before each question due to malformed DOM structure. Each question card div is already
    # properly opened and closed inside the loop above, so this additional closing tag was
    # superfluous and produced rendering artifacts.
    # (Previously: st.markdown('</div>', unsafe_allow_html=True))
    
    # Memory strength warning if applicable
    if show_memory_tip and memory_strength < 5:
        st.markdown(f"""
        <div class="memory-warning">
            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🔄 Memory Strength Upgrade Available!</div>
            <div style="color: #a0aec0;">
                It's been more than 24 hours since your last attempt. 
                Completing this course will upgrade your memory strength from {memory_strength} to {min(memory_strength + 1, 5)}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif memory_strength >= 5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(72, 187, 120, 0.2), rgba(56, 178, 172, 0.2)); 
                   border: 1px solid rgba(72, 187, 120, 0.5); border-radius: 12px; padding: 1rem; 
                   margin: 1rem 0; text-align: center;">
            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🏆 Maximum Memory Strength Achieved!</div>
            <div style="color: #a0aec0;">You've mastered this course with perfect memory retention.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Go Back", key="overview_back", use_container_width=True):
            # Clear course selection and go back to home
            if 'current_course_id' in st.session_state:
                del st.session_state.current_course_id
            if 'course_id' in st.query_params:
                del st.query_params.course_id
            st.switch_page("pages/1_🏠_Home.py")
    
    with col2:
        if st.button("🚀 Start Course", key="overview_start", use_container_width=True):
            # Set flags to indicate course was started properly
            st.session_state.course_overview_shown = True
            st.session_state.course_started_properly = True
            st.session_state.course_ended_early = False
            st.rerun()
    
    with col3:
        st.write("")  # Placeholder for symmetry
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_course_completion_stats(course_data, course_id):
    """Displays compact course completion statistics optimized for no-scroll experience."""
    
    st.markdown('<div class="course-container">', unsafe_allow_html=True)
    
    # --- Enhanced Score Display (Compact) ---
    total_questions = count_total_questions(course_data)
    correct_answers = st.session_state.get('current_score', 0)
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    if score_percentage >= 95:
        st.balloons()

    # Check if course was ended early
    course_ended_early = st.session_state.get('course_ended_early', False)
    
    # Message based on score with emojis
    if course_ended_early:
        # Different messages for early end
        completion_title = "Course Ended Early"
        message = "Thanks for your time! Your progress is saved. 📚"
        emoji = "⏹️"
        color = "#f0ad4e"
    elif score_percentage == 100:
        completion_title = "Course Completed!"
        message = "Perfect Score! Master level! 🥇"
        emoji = "🎉"
        color = "#ffd700"
    elif score_percentage >= 95:
        completion_title = "Course Completed!"
        message = "Outstanding! Nearly perfect! 🥈"
        emoji = "🌟"
        color = "#c0c0c0"
    elif score_percentage >= 70:
        completion_title = "Course Completed!"
        message = "Great job! Solid understanding. 🥉"
        emoji = "👍"
        color = "#cd7f32"
    elif score_percentage >= 40:
        completion_title = "Course Completed!"
        message = "Good effort! Keep practicing. 📚"
        emoji = "�"
        color = "#06b6d4"
    else:
        completion_title = "Course Completed!"
        message = "Keep going! Every attempt counts. 🎯"
        emoji = "🔄"
        color = "#f56565"

    # Get memory strength data first
    memory_strength = 0
    show_memory_tip = False
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:
        course_manager = get_course_manager()
        course_doc, _ = course_manager.get_course(course_id)

        if course_doc:
            memory_strength = course_doc.get('memory_strength', 0)
            last_attempt_timestamp = course_doc.get('last_attempt_timestamp')
            
            update_strength = False
            new_strength = memory_strength

            if last_attempt_timestamp is None:
                update_strength = True
                new_strength = 1
            else:
                # Handle timezone issues - ensure both datetimes have the same timezone info
                current_time = datetime.datetime.now(datetime.timezone.utc)
                
                # If last_attempt_timestamp is timezone-naive, make it UTC
                if last_attempt_timestamp.tzinfo is None:
                    last_attempt_timestamp = last_attempt_timestamp.replace(tzinfo=datetime.timezone.utc)
                
                time_since_last_attempt = current_time - last_attempt_timestamp
                if time_since_last_attempt >= datetime.timedelta(hours=24):
                    update_strength = True
                    new_strength = min(memory_strength + 1, 5)
            
            if update_strength and not st.session_state.get('course_ended_early', False):
                time_spent = time.time() - st.session_state.start_time
                course_manager.update_course_memory_strength(course_id, new_strength, time_spent)
                memory_strength = new_strength
            
            show_memory_tip = memory_strength < 5

    # Compact completion display with all info in one section
    # Build lightning icons first
        # --- Build memory strength lightning icons (visual only, not user-supplied) ---
        lightning_icons = []
        for i in range(5):
                if i < memory_strength:
                        lightning_icons.append('<span style="font-size:1.5rem;color:#ffd700;text-shadow:0 0 8px #ffd700;margin:0 2px;">⚡</span>')
                else:
                        lightning_icons.append('<span style="font-size:1.5rem;color:#4a5568;margin:0 2px;">⚪</span>')
        lightning_html = ''.join(lightning_icons)

        # Status text (internal strings – safe to interpolate directly)
        status_msg = "Max level reached! 🎯" if memory_strength >= 5 else "Re-attempt after 24hrs to level up!"
        if course_ended_early:
                status_msg += " • Memory strength not upgraded (ended early)"

        # Consolidated HTML template to avoid stray standalone closing tags rendering as raw text
        completion_html = f"""
<div class="completion-container">
    <div style="text-align:center;padding:1rem;">
        <div style="display:flex;align-items:center;justify-content:center;gap:1rem;margin-bottom:1.5rem;">
            <div style="font-size:2.5rem;">{emoji}</div>
            <div>
                <h1 style="font-size:2rem;font-weight:700;background:linear-gradient(45deg,#06b6d4,#0ea5e9,#f093fb);background-size:200% 200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 3s ease infinite;margin:0;">{completion_title}</h1>
                <div style="font-size:1.1rem;color:{color};font-weight:600;margin-top:0.5rem;">{message}</div>
            </div>
        </div>
        <div style="display:flex;justify-content:center;align-items:center;gap:2rem;margin:1.5rem 0;flex-wrap:wrap;">
            <div style="background:linear-gradient(135deg,rgba(6,182,212,0.2),rgba(8,145,178,0.2));border:2px solid {color}40;border-radius:16px;padding:1rem 1.5rem;min-width:120px;">
                <div class="completion-score" style="font-size:2.5rem;margin:0;">{score_percentage:.1f}%</div>
                <div style="font-size:0.9rem;color:#a0aec0;margin-top:0.25rem;">Final Score</div>
            </div>
            <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
                <div class="stat-item" style="text-align:center;">
                    <span class="stat-number" style="font-size:1.8rem;color:#48bb78;">{correct_answers}</span>
                    <div class="stat-label" style="font-size:0.85rem;">Correct</div>
                </div>
                <div class="stat-item" style="text-align:center;">
                    <span class="stat-number" style="font-size:1.8rem;color:#06b6d4;">{total_questions}</span>
                    <div class="stat-label" style="font-size:0.85rem;">Total</div>
                </div>
                <div class="stat-item" style="text-align:center;">
                    <span class="stat-number" style="font-size:1.8rem;color:#f56565;">{total_questions - correct_answers}</span>
                    <div class="stat-label" style="font-size:0.85rem;">Missed</div>
                </div>
            </div>
        </div>
        <div style="background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,165,0,0.1));border:1px solid rgba(255,215,0,0.3);border-radius:12px;padding:1rem;margin:1rem 0;">
            <div style="display:flex;align-items:center;justify-content:center;gap:0.75rem;margin-bottom:0.5rem;">
                <span style="font-size:1.2rem;color:#06b6d4;font-weight:600;">🧠 Memory Strength:</span>
                {lightning_html}
            </div>
            <div style="text-align:center;font-size:0.9rem;color:#a0aec0;">
                Level {memory_strength}/5 • {status_msg}
            </div>
        </div>
    </div>
</div>
""".strip()

        st.markdown(completion_html, unsafe_allow_html=True)

    # Add specific styling for action buttons
    st.markdown("""
    <style>
    /* Re-attempt button - Orange gradient */
    div[data-testid="column"]:nth-child(1) .stButton > button {
        background: linear-gradient(135deg, #ff8a00 0%, #e52e71 100%) !important;
        box-shadow: 0 8px 24px rgba(255, 138, 0, 0.4) !important;
    }
    
    div[data-testid="column"]:nth-child(1) .stButton > button:hover {
        background: linear-gradient(135deg, #ff6b00 0%, #d62d72 100%) !important;
        transform: translateY(-4px) scale(1.05) !important;
        box-shadow: 0 16px 40px rgba(255, 138, 0, 0.6) !important;
    }
    
    /* Home button - Green gradient */
    div[data-testid="column"]:nth-child(3) .stButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38b2ac 100%) !important;
        box-shadow: 0 8px 24px rgba(72, 187, 120, 0.4) !important;
    }
    
    div[data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: linear-gradient(135deg, #38a169 0%, #319795 100%) !important;
        transform: translateY(-4px) scale(1.05) !important;
        box-shadow: 0 16px 40px rgba(72, 187, 120, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add some spacing before the action buttons
    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons - Re-attempt and Home
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Re-attempt Course", key="reattempt_course_btn", use_container_width=True):
            # Reset course progress while keeping course data
            st.session_state.course_finished = False
            
            # Convert course_id to string for comparison
            course_id_str = str(course_id)
            
            # Reset all question answers and progress
            for key in list(st.session_state.keys()):
                if (isinstance(key, str) and key.startswith(f"course_{course_id_str}_")) or key in ['checked_answers', 'user_answers', 'feedback', 'current_score', 'scored_correctly_keys']:
                    del st.session_state[key]
            
            # Reinitialize progress tracking
            st.session_state.checked_answers = {}
            st.session_state.user_answers = {}
            st.session_state.feedback = {}
            st.session_state.current_score = 0
            st.session_state.scored_correctly_keys = set()
            st.session_state.start_time = time.time()
            
            # Reset overview state so it shows again
            st.session_state.course_overview_shown = False
            st.session_state.course_started_properly = False
            st.session_state.course_ended_early = False
            
            st.success("🔄 Course reset! You can now re-attempt all questions.")
            st.rerun()
    
    with col3:
        if st.button("🏠 Return to Home", key="return_home_btn", use_container_width=True):
            # Use session state to prevent double processing
            if "going_home" not in st.session_state:
                st.session_state["going_home"] = True
                st.session_state.course_finished = False
                
                # Preserve authentication and essential app state when returning home
                keys_to_preserve = [
                    'authentication_status', 'username', 'name', 'email',  # Auth data
                    'cookies', 'auth_manager',  # Auth infrastructure
                    'app_loading_complete', 'app_fully_loaded',  # App state
                    'course_history', 'logged_in', 'going_home'  # Navigation state
                ]
                
                # Clear only course-related session state
                for key in list(st.session_state.keys()):
                    if key not in keys_to_preserve:
                        del st.session_state[key]
                
                initialize_session_state()
                st.switch_page("pages/1_🏠_Home.py")

def display_progressive_questions(course_data, course_id):
    """Display questions progressively one by one (Seneca-style)"""
    if not course_data:
        return
    
    # Flatten all questions from all sections with their metadata
    all_questions = []
    for section_idx, section_data in enumerate(course_data):
        # Check if section_data is a Pydantic model
        is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
        
        if is_pydantic_model:
            section_title = getattr(section_data, "section_title", f'Section {section_idx + 1}')
            questions = getattr(section_data, "quiz", [])
        else:
            section_title = section_data.get('section_title', section_data.get('section', f'Section {section_idx + 1}'))
            questions = section_data.get('quiz', section_data.get('questions', []))
        
        if questions:
            for q_idx, question in enumerate(questions):
                all_questions.append({
                    'section_idx': section_idx,
                    'section_title': section_title,
                    'question_idx': q_idx,
                    'question': question,
                    'key': f"course_{course_id}_sec_{section_idx}_q_{q_idx}"
                })
    
    total_questions = len(all_questions)
    if total_questions == 0:
        st.info("No questions found in this course.")
        return
    
    # Determine how many questions to show based on progress
    questions_to_show = 1  # Always show at least the first question
    
    # Track the previous number of questions shown for auto-scroll detection
    prev_questions_shown_key = f"prev_questions_shown_{course_id}"
    prev_questions_shown = st.session_state.get(prev_questions_shown_key, 1)
    
    # Check each question to see if it's answered
    for i in range(total_questions):
        if i == 0:
            continue  # First question is always shown
        
        # Check if previous question is answered
        prev_question_key = all_questions[i - 1]['key']
        if prev_question_key in st.session_state and st.session_state[prev_question_key]:
            questions_to_show = i + 1
        else:
            break
    
    # Detect if a new question has appeared (for progress tracking only)
    new_question_appeared = questions_to_show > prev_questions_shown
    if new_question_appeared:
        st.session_state[prev_questions_shown_key] = questions_to_show
    
    # Display questions with section headers when needed
    current_section = None
    
    for i in range(questions_to_show):
        question_info = all_questions[i]
        section_idx = question_info['section_idx']
        section_title = question_info['section_title']
        question = question_info['question']
        question_key = question_info['key']
        
        # Show section header when we enter a new section
        if current_section != section_idx:
            current_section = section_idx
            total_sections = len(course_data)
            
            # Check if this is a newly unlocked section
            is_newly_unlocked_section = f"section_{section_idx}_shown" not in st.session_state
            if is_newly_unlocked_section:
                st.session_state[f"section_{section_idx}_shown"] = True
            
            st.markdown(f"""
            <div class="{'fade-in-up' if is_newly_unlocked_section else ''}" style="
                background: linear-gradient(135deg, rgba(6, 182, 212, 0.05), rgba(8, 145, 178, 0.05));
                border: 1px solid rgba(6, 182, 212, 0.2);
                border-radius: 20px;
                padding: 1.5rem;
                margin: 2rem 0 1rem 0;
                backdrop-filter: blur(10px);
                text-align: center;
            ">
                <h2 style="
                    color: #06b6d4;
                    margin: 0;
                    font-size: 1.6rem;
                    font-weight: 600;
                ">
                    📚 {section_title}
                </h2>
                <div style="
                    background: linear-gradient(135deg, #06b6d4, #0ea5e9);
                    color: white;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    display: inline-block;
                    margin-top: 0.5rem;
                ">
                    Section {section_idx + 1} of {total_sections}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display section explanation
            section_data = course_data[section_idx]
            is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
            
            if is_pydantic_model:
                explanation = getattr(section_data, "explanation", "")
            else:
                explanation = section_data.get('explanation', '')
            
            if explanation:
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid #06b6d4;
                    border-radius: 0 12px 12px 0;
                    padding: 1.5rem;
                    margin: 1rem 0 2rem 0;
                    backdrop-filter: blur(10px);
                    font-size: 1.1rem;
                    line-height: 1.6;
                    color: #e2e8f0;
        ">
            💡 {html.escape(explanation)}
        </div>
        """, unsafe_allow_html=True)
        
        # Check if this is a newly unlocked question
        is_newly_unlocked = (i == questions_to_show - 1 and 
                           i > 0 and 
                           f"question_{i}_shown" not in st.session_state)
        
        if is_newly_unlocked:
            st.session_state[f"question_{i}_shown"] = True
        
        # Display question with enhanced styling
        is_answered = question_key in st.session_state and st.session_state[question_key]
        
        st.markdown(f"""
        <div class="{'fade-in-up glow-animation' if is_newly_unlocked else ''}" 
             id="question-{i}"
             style="
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            border: 1px solid rgba(6, 182, 212, 0.2);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            scroll-margin-bottom: 150px;
            {'border-color: rgba(6, 182, 212, 0.6); box-shadow: 0 0 30px rgba(6, 182, 212, 0.3);' if is_newly_unlocked else ''}
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
            ">
                <div style="
                    background: linear-gradient(135deg, #06b6d4, #0ea5e9);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: 600;
                ">
                    Question {i + 1} of {total_questions}
                </div>
                <div style="
                    color: {'#10b981' if is_answered else '#6b7280'};
                    font-size: 1.2rem;
                ">
                    {'✅ Completed' if is_answered else '📝 In Progress'}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Display the actual question content
        display_question(question, f"course_{course_id}_sec_{section_idx}", question_info['question_idx'])
        
        # Close the question container
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Check if we need to scroll to a specific question (manual scroll only)
    scroll_target = st.session_state.get(f"scroll_to_question_{course_id}")
    if scroll_target is not None:
        # Clear the scroll flag
        del st.session_state[f"scroll_to_question_{course_id}"]
        # Add a simple scroll indicator
        st.info(f"📍 Scrolled to Question {scroll_target + 1}")

    # Calculate completion for course finished check (without displaying progress)
    completed_questions = sum(1 for i in range(questions_to_show) if all_questions[i]['key'] in st.session_state and st.session_state[all_questions[i]['key']])
    
    # Check if course is finished
    if completed_questions == total_questions:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.2), rgba(56, 178, 172, 0.2));
            border: 1px solid rgba(72, 187, 120, 0.4);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            margin: 2rem 0;
            backdrop-filter: blur(20px);
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
            <h2 style="color: #48bb78; margin-bottom: 1rem;">Congratulations!</h2>
            <div style="color: #e2e8f0; font-size: 1.2rem;">
                You have completed all sections of this course!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mark course as finished
        if not st.session_state.get('course_finished', False):
            st.session_state.course_finished = True
            st.rerun()
    else:
        # Add floating progress indicator and manual scroll button for incomplete courses
        current_question_number = questions_to_show
        
        # Simplified floating indicator
        st.markdown(f"""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #06b6d4, #0ea5e9);
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            z-index: 1000;
            font-size: 0.9rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <span>📍</span>
            <span>Question {current_question_number} of {total_questions}</span>
        </div>
        
        <style>
            /* Global smooth scrolling */
            html {{
                scroll-behavior: smooth;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_current_section(course_data, course_id):
    """Display the current section content with modern styling"""
    current_section_index = st.session_state.get('current_section_index', 0)
    
    if current_section_index >= len(course_data):
        st.error("Section not found")
        return
    
    current_section = course_data[current_section_index]
    section_key = f"course_{course_id}_sec_{current_section_index}"
    
    # Display section title with enhanced styling
    # Check if current_section is a Pydantic model (it has __dict__ but no get method)
    is_pydantic_model = hasattr(current_section, '__dict__') and not hasattr(current_section, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access the attribute directly
        section_title = getattr(current_section, "section_title", f'Section {current_section_index + 1}')
    else:
        # For dictionaries, use get method
        section_title = current_section.get('section_title', current_section.get('section', f'Section {current_section_index + 1}'))
    
    st.markdown(f'<h2 class="section-title">{html.escape(section_title)}</h2>', unsafe_allow_html=True)
    
    # Display section content
    display_section_content(current_section, section_key)

def display_section_content(section_data, section_key):
    """Display section content including explanation and questions with modern styling"""
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
    
    # Display explanation with modern styling
    if explanation:
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #06b6d4;
            border-radius: 0 12px 12px 0;
            padding: 1.5rem;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
            font-size: 1.1rem;
            line-height: 1.6;
            color: #e2e8f0;
        ">
            💡 {html.escape(explanation)}
        </div>
        """, unsafe_allow_html=True)
    
    # Display questions
    if questions:
        st.markdown("""
        <div style="
            text-align: center;
            margin: 3rem 0 2rem 0;
            color: #06b6d4;
            font-size: 1.2rem;
            font-weight: 600;
        ">
            📝 Questions
        </div>
        """, unsafe_allow_html=True)
        
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
            
            # Enhanced subsection styling
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(8, 145, 178, 0.1));
                border: 1px solid rgba(6, 182, 212, 0.3);
                border-radius: 20px;
                padding: 2rem;
                margin: 2rem 0;
                backdrop-filter: blur(20px);
            ">
                <h3 style="
                    color: #06b6d4;
                    margin-bottom: 1.5rem;
                    font-size: 1.5rem;
                    font-weight: 600;
                ">
                    🔸 {sanitize_inline(sub_title)}
                </h3>
            """, unsafe_allow_html=True)
            
            # Display subsection content recursively
            display_section_content(subsection, subsection_key)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_question(question_item, section_key, question_idx):
    """Display a single question with modern card styling"""
    import re  # Import for this function only
    # Check if question_item is a Pydantic model
    is_pydantic_model = hasattr(question_item, '__dict__') and not hasattr(question_item, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access attributes directly
        question_type = getattr(question_item, "type", "unknown").lower()
        question_text_full = getattr(question_item, "question", "No question text provided.")
        # Try both 'choices' and 'options' for flexibility
        choices = getattr(question_item, "choices", None) or getattr(question_item, "options", None)
        answer = getattr(question_item, "answer", None)
    else:
        # For dictionaries, use get method
        question_type = question_item.get("type", "unknown").lower()
        question_text_full = question_item.get("question", "No question text provided.")
        # Try both 'choices' and 'options' for flexibility
        choices = question_item.get('choices', None) or question_item.get('options', None)
        answer = question_item.get('answer', None)
    
    question_key = f"{section_key}_q_{question_idx}"
    is_answered = st.session_state.checked_answers.get(question_key, False)
    
    # Store question text in session state for AI validation
    st.session_state[f"{question_key}_question"] = question_text_full

    # Question number and type with modern styling
    type_display = question_type.replace('_', ' ').title()
    st.markdown(f"""
    <div class="question-number">
        Question {question_idx+1} • {type_display}
    </div>
    """, unsafe_allow_html=True)

    # Clean leading artifacts then sanitize for safe inline HTML
    cleaned_question = strip_leading_artifacts(question_text_full)
    safe_question_html = sanitize_inline(cleaned_question)
    st.markdown(f'<div class="question-text">{safe_question_html}</div>', unsafe_allow_html=True)

    if question_type in ["multiple_choice", "multiple choice"]:
        options = choices  # Use the already extracted choices
        
        # Debug information (can be removed in production)
        if options is None:
            st.warning(f"Debug: Multiple choice question has options=None. Question data: {dict(question_item) if hasattr(question_item, 'items') else 'Pydantic model'}")
        
        if options is not None:
            if not options:
                st.error("Multiple choice question has no options provided.")
                # Don't return here, let the function continue to close the div properly
            else:
                st.radio(
                    "Your choice:", options, 
                    key=question_key, 
                    label_visibility="collapsed",
                    on_change=handle_answer_submission,
                    args=(question_key, answer, question_type, None),
                    disabled=is_answered,
                    index=None
                )
        else:
            st.warning(f"Multiple choice question '{question_text_full}': No options provided.")
            
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we need the full question text and the answer to blank out
        correct_answer_for_blank = str(answer) if answer is not None else ""
        component_instance_key = f"fitb_{question_key}" # Key for the custom component's state        # Store question text in session state for AI validation (if applicable, though not used by FITB directly)
        st.session_state[f"{question_key}_question"] = question_text_full
        
        if not question_text_full or not correct_answer_for_blank:
            st.warning(f"Fill in the blank question (key: {question_key}) is missing full text or the correct answer. Using standard input.")
            # Fallback to standard text input using safe conversion
            current_value = safe_str_convert(st.session_state.get(question_key))
            
            st.text_input("Your answer:",
                          value=current_value,
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, str(correct_answer_for_blank) if correct_answer_for_blank is not None else "", question_type, None),
                          disabled=is_answered
                          )
        # Check if the question_text_full contains underscores (e.g., '___')
        elif not re.search(r'_{3,}', question_text_full):
            st.warning(f"Question text for fill-in-the-blank (key: {question_key}) does not contain '___'. Using standard input. Question: '{question_text_full}'")
            # Fallback to standard text input
            current_value = ""
            if question_key in st.session_state:
                session_value = st.session_state[question_key]
                if session_value is not None:
                    # Convert to string safely, handling various data types
                    try:
                        if isinstance(session_value, (dict, list)):
                            current_value = json.dumps(session_value)
                        elif isinstance(session_value, (str, int, float, bool)):
                            current_value = str(session_value)
                        else:
                            # For any other type, convert to string
                            current_value = str(session_value)
                    except (TypeError, ValueError, AttributeError):
                        # If conversion fails, use empty string
                        current_value = ""
                else:
                    current_value = ""
            
            # Final safety check to ensure current_value is a string
            if not isinstance(current_value, str):
                current_value = ""
            
            st.text_input("Your answer:",
                          value=current_value,
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, str(correct_answer_for_blank) if correct_answer_for_blank is not None else "", question_type, None),
                          disabled=is_answered
                          )
        else:
            # Use the custom component
            # Initialize component's specific state if not present
            if component_instance_key not in st.session_state:
                st.session_state[component_instance_key] = ""

            # Initialize session state variables if not present
            if "answers" not in st.session_state:
                st.session_state.answers = {}
            if "feedback" not in st.session_state:
                st.session_state.feedback = {}            # Check if this question has been answered correctly
            answer_data = st.session_state.answers.get(question_key, {})
            is_correct = answer_data.get("is_correct", False)
            is_answered = bool(answer_data)  # True if question has been answered (correctly or incorrectly)
              # Process the answer to ensure it's a string
            correct_answer_for_component = answer
            if isinstance(answer, list) and len(answer) > 0:
                correct_answer_for_component = str(answer[0])
            else:
                correct_answer_for_component = str(answer)
              # Add debug output for component data
            # Process the answer to ensure it's a string
            user_input = None
            component_error = None            
            
            if not FILL_IN_BLANKS_AVAILABLE or fill_in_the_blanks_input is None:
                st.info("🔄 Fill-in-the-blanks component not available - using fallback text input")
                # Fallback to standard text input
                fallback_key = f"{component_instance_key}_fallback"
                user_input = st.text_input(
                    f"Fill in the blank: {question_text_full.replace('___', '_____')}",
                    key=fallback_key,
                    disabled=is_answered,
                    help=f"Correct answer: {correct_answer_for_component}" if is_answered else None
                )
            else:
                try:
                    user_input = fill_in_the_blanks_input(
                        question_text_full=question_text_full, 
                        correctAnswer=correct_answer_for_component,
                        key=component_instance_key,
                        disabled=is_answered  # Disable input if question has been answered
                    )
                except (ImportError, ModuleNotFoundError, AttributeError, TypeError) as e:
                    component_error = str(e)
                    st.error(f"❌ Fill-in-the-blanks component error: {component_error}")
                    st.info("🔄 Using fallback text input")
                    # Fallback to standard text input
                    fallback_key = f"{component_instance_key}_fallback"
                    user_input = st.text_input(
                        f"Fill in the blank: {question_text_full.replace('___', '_____')}",
                        key=fallback_key,
                        disabled=is_answered,
                        help=f"Correct answer: {correct_answer_for_component}" if is_answered else None
                    )
              # Handle both string input and object input (for enhanced component behavior)
            current_answer = ""
            is_give_up_action = False
            is_correct_action = False
            # is_wrong_action = False  # Removed unused variable
              # Early exit if question is already answered to prevent infinite loops
            if is_answered:
                # Question already answered, don't process any new input
                current_answer = ""
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                # is_wrong_action = False  # Removed unused variable
            elif isinstance(user_input, dict):
                # Handle enhanced component return format
                raw_value = user_input.get("value", "")
                # Handle both string and list values from component
                if isinstance(raw_value, list):
                    current_answer = raw_value[0] if len(raw_value) > 0 else ""
                else:
                    current_answer = str(raw_value)
                
                action = user_input.get("action", "")
                component_says_correct = user_input.get("isCorrect", False)
                is_give_up_action = action == "give_up"
                is_completed_wrong = action == "question_complete" and not component_says_correct
                is_correct_action = (action == "correct_answer" or action == "question_complete") and component_says_correct
                # Note: isWrong flag is available but not used in current logic
                
                # Debug info
                # if action:  # Only show if there's an action
                #     st.write(f"🔍 Debug: Action={action}, Raw Value={raw_value}, Answer='{current_answer}', Correct={user_input.get('isCorrect', False)}")
            elif isinstance(user_input, str):
                # Fallback for standard text input or when component returns string
                current_answer = user_input
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                # is_wrong_action = False  # Unused variable
            elif user_input is None:
                current_answer = ""
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                # is_wrong_action = False  # Unused variable
            else:
                st.warning(f"⚠️ Unexpected input type: {type(user_input)}, value: {user_input}")
                current_answer = str(user_input) if user_input is not None else ""
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                # is_wrong_action = False  # Unused variable
            
            # Real-time checking as user types or on specific actions
            if current_answer is not None and isinstance(current_answer, str):
                current_answer = current_answer.strip()
                
                # Handle answer format - extract from list if needed
                correct_answer_str = answer
                if isinstance(answer, list) and len(answer) > 0:
                    correct_answer_str = str(answer[0])  # Take first element if it's a list                else:
                    correct_answer_str = str(answer)
                
                answer_matches = False
                if isinstance(current_answer, str) and isinstance(correct_answer_str, str):
                    answer_matches = current_answer.lower() == correct_answer_str.lower()
                
                # Only process specific component actions to avoid infinite loops
                should_process = (isinstance(user_input, dict) and 
                                action in ["give_up", "correct_answer", "question_complete"]) or isinstance(user_input, str)
                
                # If answer is correct and not already processed
                if should_process and (answer_matches or is_correct_action) and not is_correct:
                    # Mark as correct
                    if "answers" not in st.session_state:
                        st.session_state.answers = {}
                    if "feedback" not in st.session_state:
                        st.session_state.feedback = {}
                    
                    st.session_state.answers[question_key] = {
                        "user_answer": current_answer,
                        "is_correct": True,
                        "question_type": question_type
                    }
                    st.session_state.feedback[question_key] = "Correct! 🎉"
                    st.session_state.fitb_answered = True
                    
                    # IMPORTANT: Mark in all necessary session state locations for navigation system
                    st.session_state.checked_answers[question_key] = True
                    st.session_state.user_answers[question_key] = current_answer
                    st.session_state[question_key] = True  # Add this for progressive question system
                    
                    # Update score tracking
                    if question_key not in st.session_state.scored_correctly_keys:
                        st.session_state.current_score += 1
                        st.session_state.scored_correctly_keys.add(question_key)
                    
                      # Also update the local is_correct variable for immediate UI update
                    is_correct = True
                    st.rerun()  # Immediate rerun for correct answers to update UI                # Handle give up action or completed wrong answer
                elif should_process and (is_give_up_action or is_completed_wrong) and not is_correct:
                    if "answers" not in st.session_state:
                        st.session_state.answers = {}
                    if "feedback" not in st.session_state:
                        st.session_state.feedback = {}
                    
                    st.session_state.answers[question_key] = {
                        "user_answer": current_answer,
                        "is_correct": False,
                        "question_type": question_type
                    }
                    st.session_state.feedback[question_key] = f"The correct answer is: {answer}"
                    st.session_state.fitb_answered = True
                    
                    # IMPORTANT: Mark in all necessary session state locations for navigation system
                    st.session_state.checked_answers[question_key] = True
                    st.session_state.user_answers[question_key] = current_answer
                    st.session_state[question_key] = True  # Add this for progressive question system
                    
                    st.rerun()  # Rerun to update UI and disable component              # Display feedback for fill-in-the-blank questions
            answer_data = st.session_state.answers.get(question_key, {})
            if answer_data:  # If there's any answer data (correct or incorrectly)
                feedback_text = st.session_state.feedback.get(question_key)
                if feedback_text:
                    # Mark that feedback has been displayed for this question to prevent duplicate display
                    feedback_displayed_key = f"{question_key}_feedback_displayed"
                    if feedback_displayed_key not in st.session_state:
                        st.session_state[feedback_displayed_key] = True
                        if "Correct!" in feedback_text:
                            st.success(f"✅ {feedback_text}")
                        else:
                            st.error(f"❌ {feedback_text}")
    
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
            except (TypeError, ValueError, AttributeError) as e:
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
            
            # Initialize user's matches in session state if not already done
            match_answers_key = f"{question_key}_matches"
            if match_answers_key not in st.session_state:
                st.session_state[match_answers_key] = {}
            
            # Modern matching interface
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(8, 145, 178, 0.1));
                border: 1px solid rgba(6, 182, 212, 0.2);
                border-radius: 16px;
                padding: 2rem;
                margin: 1rem 0;
            ">
                <h4 style="
                    color: #06b6d4; 
                    margin-bottom: 1.5rem; 
                    text-align: center;
                    font-size: 1.2rem;
                ">🔗 Match the items</h4>
            """, unsafe_allow_html=True)
            
            # Create a beautiful matching interface
            for i, left_item in enumerate(left_items):
                # Get the current selection for this dropdown from session state
                current_selection_for_left_item = st.session_state[match_answers_key].get(left_item)

                # Create a styled container for each match pair
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(6, 182, 212, 0.2);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    transition: all 0.3s ease;
                ">
                    <div style="
                        color: #e2e8f0;
                        font-weight: 600;
                        margin-bottom: 0.8rem;
                        font-size: 1.1rem;
                    ">
                        <span style="
                            background: linear-gradient(135deg, #06b6d4, #0ea5e9);
                            color: white;
                            padding: 4px 8px;
                            border-radius: 6px;
                            font-size: 0.8rem;
                            margin-right: 10px;
                        ">{i+1}</span>
                        {html.escape(left_item)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a more intuitive selectbox with better styling
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
                with col2:
                    # Prepare options and determine current selection index
                    all_options = ["🔍 Choose an option..."] + [f"➤ {item}" for item in shuffled_right]
                    current_index = 0  # Default to placeholder
                    
                    # If user has a previous selection, find its index
                    if current_selection_for_left_item and current_selection_for_left_item in shuffled_right:
                        target_option = f"➤ {current_selection_for_left_item}"
                        if target_option in all_options:
                            current_index = all_options.index(target_option)
                    
                    # Use a unique key that incorporates the left_item text to handle duplicates
                    unique_dropdown_key = f"match_select_{question_key}_{i}_{hash(left_item) % 10000}"
                    
                    selected_right_item = st.selectbox(
                        f"Select match for item {i+1}",
                        options=all_options,
                        index=current_index,
                        key=unique_dropdown_key,
                        label_visibility="collapsed",
                        disabled=is_answered,
                        help=f"Select the correct match for: {left_item}"
                    )
                    
                    # Store the selection (remove the arrow prefix) based on widget state
                    if selected_right_item and selected_right_item != "🔍 Choose an option...":
                        clean_selection = selected_right_item.replace("➤ ", "")
                        st.session_state[match_answers_key][left_item] = clean_selection
                    elif left_item in st.session_state[match_answers_key]:
                        # Remove the selection if user chose the placeholder
                        del st.session_state[match_answers_key][left_item]
            
            # Get current user matches for submission check
            user_matches_for_ui = st.session_state.get(match_answers_key, {})
            all_items_matched_in_ui = len(user_matches_for_ui) == len(left_items)
            
            # Progress indicator
            progress = len(user_matches_for_ui) / len(left_items) if left_items else 0
            st.markdown(f"""
            <div style="margin: 1.5rem 0;">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                ">
                    <span style="color: #a0aec0; font-size: 0.9rem;">Progress</span>
                    <span style="color: #06b6d4; font-weight: 600;">{len(user_matches_for_ui)}/{len(left_items)} matched</span>
                </div>
                <div style="
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    height: 8px;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(135deg, #06b6d4, #0ea5e9);
                        height: 100%;
                        width: {progress * 100}%;
                        transition: width 0.3s ease;
                        border-radius: 10px;
                    "></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Enhanced submit button
            if not is_answered:
                if all_items_matched_in_ui:
                    if st.button("✅ Submit Matches", 
                                key=f"submit_match_{question_key}",
                                type="primary",
                                use_container_width=True):
                        # Submit the matches
                        user_selections_to_submit = st.session_state.get(match_answers_key, {})
                        st.session_state[question_key] = json.dumps(user_selections_to_submit)
                        
                        # Handle submission
                        if isinstance(match_data, dict):
                            correct_answer_json = json.dumps(match_data)
                            handle_answer_submission(question_key, correct_answer_json, "match", None)
                        else:
                            st.error("Internal error: Correct answer data for matching is not in the expected dictionary format.")
                            st.session_state.checked_answers[question_key] = True
                            st.session_state.user_answers[question_key] = json.dumps(user_selections_to_submit)
                            st.session_state.feedback[question_key] = "Error: Could not process the correct answer data."
                        
                        st.session_state.match_submitted = True
                else:
                    # Show disabled button with helpful message
                    st.button("🔍 Complete all matches to submit", 
                             key=f"submit_match_{question_key}_disabled", 
                             disabled=True,
                             use_container_width=True,
                             help="Please select a match for all items before submitting")
                    
                    # Show which items still need matching
                    unmatched = [item for item in left_items if item not in user_matches_for_ui]
                    if unmatched:
                        st.info(f"💡 Still need to match: {', '.join(unmatched[:3])}" + 
                               (f" and {len(unmatched)-3} more" if len(unmatched) > 3 else ""))
            
            # Close the styled container
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            # Fallback for malformed match questions
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 152, 0, 0.1));
                border: 1px solid rgba(255, 193, 7, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    color: #ffc107;
                    font-weight: 600;
                    margin-bottom: 1rem;
                ">
                    <span style="font-size: 1.2rem;">⚠️</span>
                    Match Question Format Issue
                </div>
                <div style="color: #e2e8f0; line-height: 1.5;">
                    The matching question data couldn't be processed in the standard format.
                    Please provide your answer as a JSON object mapping items to their matches.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show example format
            st.code('{"Item 1": "Match A", "Item 2": "Match B", "Item 3": "Match C"}', language="json")
        
        # Enhanced fallback text area with better styling
        current_value = safe_str_convert(st.session_state.get(question_key))
        
        st.text_area(
            "📝 Your answer (as JSON):",
            value=current_value,
            key=question_key,
            on_change=handle_answer_submission,
            args=(question_key, str(answer) if answer is not None else "", question_type, None),
            disabled=is_answered,
            help="Enter your matches as a JSON object, e.g., {\"premise1\": \"responseA\", \"premise2\": \"responseB\"}"
        )
    
    elif question_type in ["short_answer", "short answer"]:
        # Ensure we have a string value for the text area using safe conversion
        current_value = safe_str_convert(st.session_state.get(question_key))
        
        st.text_area("Your answer:",
                    value=current_value,
                    key=question_key,
                    on_change=handle_answer_submission,
                    args=(question_key, str(answer) if answer is not None else "", question_type, None),
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
                 )      # Display feedback if answered
    if is_answered: # This relies on checked_answers[question_key] being True
        # Check if feedback has already been displayed (e.g., by fill-in-the-blank component)
        feedback_displayed_key = f"{question_key}_feedback_displayed"
        if feedback_displayed_key not in st.session_state:
            feedback_text = st.session_state.feedback.get(question_key)
            if feedback_text: # Check if feedback text exists and is not empty
                if "Correct!" in feedback_text:
                    st.success(f"✅ {feedback_text}")
                elif feedback_text.startswith("Incorrect."):
                    # Extract the part after "Incorrect. " to check for errors vs. partial scores
                    detailed_feedback = feedback_text[len("Incorrect. "):]
                    if any(err_keyword in detailed_feedback.lower() for err_keyword in ["error", "unexpected", "invalid", "malformed"]):
                        st.error(f"❌ {feedback_text}") # e.g., "Incorrect. Error: Malformed data."
                    else:
                        # For partial scores or simple incorrect messages without specific error keywords
                        st.info(f"ℹ️ {feedback_text}") # e.g., "Incorrect. You matched 2 out of 3." or "Incorrect. Your answer: X, Correct answer: Y"
                elif any(err_keyword in feedback_text.lower() for err_keyword in ["error", "unexpected", "invalid", "malformed"]):
                    # For direct error messages not prepended with "Incorrect."
                    st.error(f"❌ {feedback_text}")
                else:
                    # Fallback for any other non-empty feedback, treat as informational
                    # This could catch custom feedback messages that don't fit the patterns above
                    st.info(f"ℹ️ {feedback_text}")
        # else: No feedback message was found in session state for this question_key.
        # If is_answered is True but feedback_text is None or empty, nothing will be shown here.
        # This would be a state inconsistency if it occurs.

def fix_json_format(data_str):
    """
    Fix common JSON formatting issues in match question data, specifically missing commas.
    
    Args:
        data_str (str): String representation of JSON-like data
        
    Returns:
        dict or None: Parsed dictionary if successful, None if failed
    """
    import re  # Import for this function only
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
            
        except (json.JSONDecodeError, ValueError, TypeError):
            # If regex approach fails, try manual key-value extraction
            try:
                # Extract key-value pairs using a more robust approach
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
                
            except (json.JSONDecodeError, ValueError, TypeError):
                pass    
    return None

def handle_answer_submission(question_key, correct_answer, question_type, selected_match_key=None, submitted_answer=None):  # selected_match_key and submitted_answer kept for API compatibility
    # Initialize session state for answer tracking if not already present
    if "answers" not in st.session_state:
        st.session_state.answers = {}
      # For fill-in-the-blank, skip this function as it's handled by dedicated component logic
    if question_type == "fill_in_the_blank":
        return # Let the custom component handle all fill-in-the-blank logic# For other question types, proceed with existing logic
    user_answer = st.session_state.get(question_key)
    
    if user_answer is None: 
        # If it's a new question, it might be None if not initialized by the input element yet.
        # For fill-in-the-blank custom component, it's initialized to "".
        # For standard inputs, if not touched, it might be None.
        # Let's allow submission to proceed; empty/None answers will be marked by is_answer_correct.
        pass # Allow None to be processed by is_answer_correct, which handles str(user_answer)

    # For match questions, check if a blank/placeholder option was selected
    # Match questions use "" as placeholder in dropdowns
    if question_type == "match" and user_answer and isinstance(user_answer, str):
        try:
            # Parse the user answer JSON to check for empty selections
            user_selections = json.loads(user_answer)
            if isinstance(user_selections, dict):
                # Check if any selection is empty (placeholder)
                for _left_item, right_selection in user_selections.items():
                    if not right_selection or right_selection == "":
                        return  # Don't process submission if placeholder is selected
        except (json.JSONDecodeError, TypeError):
            pass  # Continue with normal processing if JSON parsing fails

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
        if user_answer is None: # Explicitly handle None for short answer if it makes sense
            user_answer = "" # Or handle as an error/incomplete submission
        # First try AI validation
        try:
            # Get the original question text from session state
            question_text = st.session_state.get(f"{question_key}_question", "")
            
            # Use AI validation if available
            if local_backend is not None:
                ai_result, ai_explanation = local_backend.validate_short_answer_with_ai(
                    question_text, user_answer, correct_answer
                )
                
                if ai_result is not None: # AI validation was successful               
                    is_correct_locally = ai_result
                    feedback_message = ai_explanation # AI explanation is the full feedback
                else: # AI validation failed or returned None, fallback to simple check               
                    is_correct_locally = is_answer_correct(user_answer, correct_answer, question_type)
                    display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
                    if is_correct_locally:
                        feedback_message = f"Correct! Your answer: {user_answer}, Expected: {display_answer}. (AI validation was skipped)"
                    else:
                        feedback_message = f"Your answer: {user_answer}, Expected: {display_answer}. (AI validation was skipped)"
            else:
                # Local backend not available, use simple validation
                is_correct_locally = is_answer_correct(user_answer, correct_answer, question_type)
                display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
                if is_correct_locally:
                    feedback_message = f"Correct! Your answer: {user_answer}, Expected: {display_answer} (AI validation unavailable)"
                else:
                    feedback_message = f"Your answer: {user_answer}, Expected: {display_answer} (AI validation unavailable)"
                
        except (ImportError, AttributeError, ConnectionError, TypeError, ValueError) as e:
            # Fallback to simple string comparison if AI validation fails
            is_correct_locally = is_answer_correct(user_answer, correct_answer, question_type)
            display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
            if is_correct_locally:
                feedback_message = f"Correct! Your answer: {user_answer}, Expected: {display_answer} (AI validation error: {str(e)})"
            else:
                feedback_message = f"Your answer: {user_answer}, Expected: {display_answer} (AI validation error: {str(e)})"

    # For match questions, we have JSON strings representing dictionaries
    elif question_type == "match":
        if isinstance(user_answer, str): # Ensure user_answer is a string before json.loads
            try:
                # user_answer is st.session_state.get(question_key), a JSON string of user's matches.
                # correct_answer is a JSON string of the correct matches, passed from display_question.
                user_matches_dict = json.loads(user_answer)
                correct_matches_dict = json.loads(correct_answer) # Assuming correct_answer is always a valid JSON string here

                # Validate that both parsed objects are dictionaries
                if not isinstance(user_matches_dict, dict) or not isinstance(correct_matches_dict, dict):
                    is_correct_locally = False
                    feedback_message = "Error: Match data is not in the expected dictionary format after parsing."
                else:
                    # Compare the dictionaries for logical equality
                    is_correct_locally = (user_matches_dict == correct_matches_dict)
                    
                    # Calculate partial score for feedback message
                    correct_count = 0
                    # Iterate through the keys in the user's submitted matches
                    for item_key in user_matches_dict:
                        # Check if the item exists in correct answers and if the user's match for it is correct
                        if item_key in correct_matches_dict and user_matches_dict[item_key] == correct_matches_dict[item_key]:
                            correct_count += 1
                
                total_items_to_match = len(correct_matches_dict) # Total number of items that should be matched

                if is_correct_locally:
                    feedback_message = f"Correct! You matched all {total_items_to_match} items."
                else:
                    if total_items_to_match > 0:
                        feedback_message = f"You matched {correct_count} out of {total_items_to_match} items correctly."
                    else: # Should not happen with well-formed question data
                        feedback_message = "Could not determine the number of items to match, or there were no items to match."
            
            except json.JSONDecodeError:
                is_correct_locally = False
                feedback_message = "Error processing your selections: the answer format was unexpected. Please ensure your selections are valid."
            except (TypeError, ValueError, KeyError) as e: # Catch any other unexpected error during match processing
                is_correct_locally = False
                feedback_message = f"An unexpected error occurred while checking your match answer: {str(e)}"
        else:
            # Handle cases where user_answer is None or not a string (e.g. if not answered)
            is_correct_locally = False
            feedback_message = "No answer submitted or answer is in an invalid format for matching."

    # For other text-based answers (multiple_choice, fill_in_the_blank)
    elif is_answer_correct(user_answer, correct_answer, question_type):
        is_correct_locally = True
        # Display first acceptable answer if multiple exist
        display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {display_answer}"
    else: # Default case for incorrect non-boolean, non-short-answer
        is_correct_locally = False # Ensure this is set if not already by other branches
        # Display first acceptable answer if multiple exist
        display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {display_answer}"

    if is_correct_locally:
        # For "match" and "short_answer" (with AI), feedback_message is already the complete success message.
        # For "true_false", and other types like MC/FITB, we might want to prepend "Correct!" if not already there.
        if question_type == "match":
            st.session_state.feedback[question_key] = feedback_message # e.g., "Correct! You matched all X items."
        elif question_type in ["short_answer", "short answer"] and feedback_message:
            # Assuming ai_explanation (feedback_message) is a full sentence like "Correct, because..." or "That's right..."
            st.session_state.feedback[question_key] = feedback_message
        elif question_type in ["true_false", "true false", "true or false"] and feedback_message:
            # feedback_message for TF correct is "Your answer: X, Correct answer: X"
            st.session_state.feedback[question_key] = f"Correct! {feedback_message}"
        else: # Default for MC, FITB if correct (feedback_message is "Your answer: X, Correct: X")
            st.session_state.feedback[question_key] = f"Correct! {feedback_message}"
        
        if question_key not in st.session_state.scored_correctly_keys:
            st.session_state.current_score += 1
            st.session_state.scored_correctly_keys.add(question_key)
    else:
        # For incorrect answers, feedback_message should contain the reason/details.
        # Prepend "Incorrect." to this detailed message.
        st.session_state.feedback[question_key] = f"Incorrect. {feedback_message}"

def is_answer_correct(user_answer, correct_answer, question_type=None):  # question_type kept for API compatibility
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
