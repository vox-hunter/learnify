"""
AI Quiz and Course Generator - Main Entry Point
This script handles navigation and session management for the Learnify app.
"""

import streamlit as st
import os
import sys
import time

# --- Page Config ---
st.set_page_config(
    page_title="AI Loom",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"  # Set to expanded - we'll handle collapse via CSS
)

# --- Simplified Loading System ---
# Initialize loading state if not present
if 'app_loading_complete' not in st.session_state:
    st.session_state['app_loading_complete'] = True  # Disable loading animation completely

# --- Custom CSS to hide navigation links and apply modern styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide the 'Course' link in the sidebar */
    a[data-testid="stSidebarNavLink"][href$="/Course"] {
        display: none;
    }
    
    /* Hide Privacy Policy and Terms & Conditions from sidebar navigation */
    a[data-testid="stSidebarNavLink"][href$="/Privacy"] {
        display: none !important;
    }
    
    a[data-testid="stSidebarNavLink"][href$="/Terms"] {
        display: none !important;
    }
    
    /* Modern sidebar styling */
    .stSidebar > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* ULTIMATE SIDEBAR BUTTON OVERRIDE - Apply to ALL buttons in sidebar */
    .stSidebar button,
    .stSidebar .stButton > button,
    .stSidebar .stPopover button,
    .stSidebar [data-testid="stPopover"] button,
    .stSidebar .element-container button,
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stPopover button,
    [data-testid="stSidebar"] [data-testid="stPopover"] button,
    [data-testid="stSidebar"] .element-container button,
    .stSidebar button[kind],
    .stSidebar button[data-testid],
    .stSidebar button[style],
    [data-testid="stSidebar"] button[kind],
    [data-testid="stSidebar"] button[data-testid],
    [data-testid="stSidebar"] button[style] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar button:hover,
    .stSidebar .stButton > button:hover,
    .stSidebar .stPopover button:hover,
    .stSidebar [data-testid="stPopover"] button:hover,
    .stSidebar .element-container button:hover,
    [data-testid="stSidebar"] button:hover,
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stPopover button:hover,
    [data-testid="stSidebar"] [data-testid="stPopover"] button:hover,
    [data-testid="stSidebar"] .element-container button:hover,
    .stSidebar button[kind]:hover,
    .stSidebar button[data-testid]:hover,
    .stSidebar button[style]:hover,
    [data-testid="stSidebar"] button[kind]:hover,
    [data-testid="stSidebar"] button[data-testid]:hover,
    [data-testid="stSidebar"] button[style]:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Enhanced Streamlit widgets */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Override default Streamlit button colors completely for main content */
    .stMain button[kind="primary"],
    .stMain button[data-testid*="stButton"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Success/Error/Info styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.2), rgba(56, 178, 172, 0.2));
        border: 1px solid rgba(72, 187, 120, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(20px);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.2), rgba(229, 62, 62, 0.2));
        border: 1px solid rgba(245, 101, 101, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(20px);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(66, 153, 225, 0.2), rgba(102, 126, 234, 0.2));
        border: 1px solid rgba(66, 153, 225, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(20px);
    }
    
    /* Container styling */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Modern card styling */
    .modern-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        border-color: rgba(102, 126, 234, 0.5);
        background: rgba(255, 255, 255, 0.12);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    /* Text styling */
    .modern-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hide any remaining loading elements */
    .loading-overlay {
        display: none !important;
    }
    
    /* Hide cookie manager component that takes up horizontal space */
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
    .stCustomComponentV1:has(iframe[height="0"]) {
        display: none !important;
    }
    
    /* Hide custom components with cookie manager */
    .st-emotion-cache-8atqhb:has(iframe[src*="cookie_manager"]) {
        display: none !important;
    }
    
    /* Force CSS re-application on sidebar buttons to prevent caching issues */
    .stSidebar {
        --sidebar-btn-bg: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        --sidebar-btn-border: rgba(102, 126, 234, 0.2);
        --sidebar-btn-color: #e2e8f0;
    }
    
    /* CSS variable-based styling to force consistent application */
    .stSidebar *[role="button"],
    .stSidebar button {
        background: var(--sidebar-btn-bg) !important;
        border: 1px solid var(--sidebar-btn-border) !important;
        color: var(--sidebar-btn-color) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar *[role="button"]:hover,
    .stSidebar button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
</style>

<script>
// Force sidebar button style consistency by periodically checking and reapplying styles
function ensureSidebarButtonConsistency() {
    const sidebar = document.querySelector('.stSidebar');
    if (sidebar) {
        const buttons = sidebar.querySelectorAll('button');
        buttons.forEach(button => {
            // Force re-application of our custom styles
            button.style.setProperty('background', 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))', 'important');
            button.style.setProperty('color', '#e2e8f0', 'important');
            button.style.setProperty('border', '1px solid rgba(102, 126, 234, 0.2)', 'important');
            button.style.setProperty('border-radius', '12px', 'important');
            button.style.setProperty('font-weight', '500', 'important');
        });
    }
}

// Run immediately and on DOM changes
ensureSidebarButtonConsistency();
const observer = new MutationObserver(ensureSidebarButtonConsistency);
observer.observe(document.body, { childList: true, subtree: true });

// Also run when Streamlit finishes loading
window.addEventListener('load', ensureSidebarButtonConsistency);
</script>
""", unsafe_allow_html=True)


# Add parent directory to path to allow imports from Quiz_app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import get_course_manager
    from streamlit_cookies_manager import EncryptedCookieManager
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# --- Auth & Cookie Management (No UI Rendering) ---
def initialize_cookie_manager():
    """Initialize cookie manager with error handling for deployment environments"""
    try:
        # Use only Streamlit secrets
        cookie_key = st.secrets.get("COOKIE_ENCRYPTION_KEY", "learnify-secure-key-2024-change-for-production")
        
        cookie_manager = EncryptedCookieManager(
            password=cookie_key,
            prefix="learnify/auth",
        )
        return cookie_manager
    except (ImportError, RuntimeError, ValueError) as e:
        st.warning(f"Could not initialize cookie manager: {e}. Authentication features will be limited.")
        return None

if MONGO_AVAILABLE:
    cookies = initialize_cookie_manager()
    st.session_state.cookies = cookies

    # Check if cookies are ready without triggering boolean evaluation
    cookies_ready = False
    if cookies is not None:
        try:
            cookies_ready = cookies.ready()
        except (AttributeError, RuntimeError):
            cookies_ready = False

    AUTH_COOKIE_NAME = "username"

    def get_auth_manager():
        if "auth_manager" not in st.session_state:
            try:
                st.session_state.auth_manager = MongoAuthManager()
            except (ImportError, ConnectionError, ValueError):
                st.session_state.auth_manager = None
        return st.session_state.auth_manager

    manager = get_auth_manager()
    
    def auto_login_from_cookie():
        if st.session_state.get('authentication_status'):
            return
        
        # Safely check if cookies are available and ready
        if not hasattr(st.session_state, 'cookies') or st.session_state.cookies is None:
            return
        
        try:
            if not st.session_state.cookies.ready():
                return
        except (AttributeError, RuntimeError):
            return
            
        cookie_username = st.session_state.cookies.get(AUTH_COOKIE_NAME)
        if cookie_username and cookie_username != "logged_out" and manager:
            user_data = manager.find_user_by_username(cookie_username)
            if user_data:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = cookie_username
                st.session_state['name'] = user_data.get('name')
                st.session_state['email'] = user_data.get('email')

    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    auto_login_from_cookie()

    def logout_user():
        st.session_state['authentication_status'] = False
        st.session_state.pop('username', None)
        st.session_state.pop('name', None)
        st.session_state.pop('email', None)
        
        # Safely check and update cookies
        if hasattr(st.session_state, 'cookies') and st.session_state.cookies is not None:
            try:
                if st.session_state.cookies.ready():
                    st.session_state.cookies[AUTH_COOKIE_NAME] = "logged_out"
                    st.session_state.cookies.save()
            except (AttributeError, RuntimeError, ValueError):
                pass  # Ignore cookie errors during logout
                
        st.query_params.clear()
        st.rerun()
else:
    st.session_state['authentication_status'] = False
    st.session_state.cookies = None  # Ensure cookies is available even when MONGO is not available
    def logout_user(): # Define for non-mongo case
        st.session_state['authentication_status'] = False
        st.rerun()

# --- Pages Definition ---
home_page = st.Page("pages/1_🏠_Home.py", title="New Course", icon="➕", default=True)

if st.session_state.get('authentication_status'):
    login_page = st.Page("pages/2_🔐_Login.py", title="Account", icon="👤")
else:
    login_page = st.Page("pages/2_🔐_Login.py", title="Login", icon="🔐")
    
course_page = st.Page("pages/3_Course.py", title="Course")
privacy_page = st.Page("pages/4_Privacy.py", title="Privacy Policy", icon="🔒")
terms_page = st.Page("pages/5_Terms.py", title="Terms & Conditions", icon="📋")

# --- Navigation Control ---
pg = st.navigation([home_page, login_page, course_page, privacy_page, terms_page])

# --- Sidebar UI (Renders after st.navigation) ---
with st.sidebar:
    # Show debug info if available
    if 'debug_last_click' in st.session_state:
        st.info(f"Debug: {st.session_state.debug_last_click}")
    
    if st.session_state.get('authentication_status') and MONGO_AVAILABLE:
        st.header("Courses")
        course_manager = get_course_manager()
        if course_manager:
            courses, error = course_manager.get_user_courses(st.session_state['username'])
            if error:
                st.error(error)
            
            if courses:
                # Calculate dynamic height based on number of courses
                num_courses = len(courses)
                
                # Each course item takes roughly 50px (button + spacing)
                # Add some padding and account for menu items
                base_height = num_courses * 50 + 20  # 20px for padding
                
                # Set minimum and maximum heights to keep it reasonable
                min_height = 60   # Minimum for at least one course
                max_height = 400  # Maximum to prevent overly tall sidebar
                
                # Use dynamic height, but only add container if more than 6 courses
                dynamic_height = max(min_height, min(base_height, max_height))
                
                if num_courses > 6:
                    # Use scrollable container for many courses
                    with st.container(height=dynamic_height):
                        for course in courses:
                            course_id_val = course.get('_id') or course.get('id') or course.get('course_id')
                            if not course_id_val:
                                continue

                            course_id = str(course_id_val)
                            course_title = course.get('title', 'Untitled Course')
                            
                            col1, col2 = st.columns([0.8, 0.2])
                            with col1:
                                if st.button(course_title, key=f"nav_{course_id}", use_container_width=True):
                                    # Set the course ID in session state and query params
                                    st.session_state.current_course_id = course_id
                                    st.query_params.course_id = course_id
                                    # Navigate to the course page using string path (like old version)
                                    st.switch_page("pages/3_Course.py")
                            with col2:
                                with st.popover("⋮", use_container_width=True):
                                    delete_key = f"delete_{course_id}"
                                    if st.button("Delete", key=delete_key, use_container_width=True):
                                        success, msg = course_manager.delete_course(course_id, st.session_state['username'])
                                        if success:
                                            st.success("Course deleted successfully!")
                                            st.rerun()
                                        else:
                                            st.error(f"Failed to delete course: {msg}")
                                            st.rerun()
                                    
                                    share_key = f"share_{course_id}"
                                    is_public = course.get('is_public', False)
                                    share_label = "Make Private" if is_public else "Make Public"
                                    if st.button(share_label, key=share_key, use_container_width=True):
                                        # Use session state to track privacy update to avoid double processing
                                        if share_key not in st.session_state:
                                            st.session_state[share_key] = True
                                            success, msg = course_manager.update_course_privacy(course_id, st.session_state['username'], not is_public)
                                            if success:
                                                st.success("Privacy updated.")
                                                # Clear the update flag after successful update
                                                del st.session_state[share_key]
                                                st.rerun()
                                            else:
                                                st.error(msg)
                                                del st.session_state[share_key]
                else:
                    # No container needed for few courses - let them expand naturally
                    for course in courses:
                        course_id_val = course.get('_id') or course.get('id') or course.get('course_id')
                        if not course_id_val:
                            continue

                        course_id = str(course_id_val)
                        course_title = course.get('title', 'Untitled Course')
                        
                        col1, col2 = st.columns([0.8, 0.2])
                        with col1:
                            if st.button(course_title, key=f"nav_{course_id}", use_container_width=True):
                                # Store debug info in session state so it persists
                                # Set the course ID in session state and query params
                                st.session_state.current_course_id = course_id
                                st.query_params.course_id = course_id
                                # Navigate to the course page using string path (like old version)
                                st.switch_page("pages/3_Course.py")
                        with col2:
                            with st.popover("⋮", use_container_width=True):
                                delete_key = f"delete_{course_id}"
                                if st.button("Delete", key=delete_key, use_container_width=True):
                                    success, msg = course_manager.delete_course(course_id, st.session_state['username'])
                                    if success:
                                        st.success("Course deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to delete course: {msg}")
                                        st.rerun()
                                
                                share_key = f"share_{course_id}"
                                is_public = course.get('is_public', False)
                                share_label = "Make Private" if is_public else "Make Public"
                                if st.button(share_label, key=share_key, use_container_width=True):
                                    # Use session state to track privacy update to avoid double processing
                                    if share_key not in st.session_state:
                                        st.session_state[share_key] = True
                                        success, msg = course_manager.update_course_privacy(course_id, st.session_state['username'], not is_public)
                                        if success:
                                            st.success("Privacy updated.")
                                            # Clear the update flag after successful update
                                            del st.session_state[share_key]
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                            del st.session_state[share_key]
            else:
                st.info("No courses yet.")
    
    st.markdown('<div style="margin-top: auto;"></div>', unsafe_allow_html=True)
    with st.container():
        if st.session_state.get('authentication_status'):
            with st.popover(f"👤 {st.session_state.get('name', st.session_state.get('username'))}", use_container_width=True):
                if st.button("Logout", use_container_width=True):
                    logout_user()
                if st.button("Reset Password", use_container_width=True, key="sidebar_reset_password"):
                    st.switch_page(login_page)
        else:
            if st.button("Sign up / Login", icon="🔐", use_container_width=True):
                st.switch_page(login_page)

# --- Run Page ---
pg.run()

# Mark app as fully loaded
st.session_state['app_fully_loaded'] = True
