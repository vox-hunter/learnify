"""
AI Quiz and Course Generator - Main Entry Point
This script handles navigation and session management for the Learnify app.
"""

import streamlit as st
import os
import sys
import time

# --- Helper Functions ---
def truncate_course_name(course_name, max_words=4):
    """
    Truncate course name to specified number of words, adding ellipsis if needed.
    Returns a tuple of (truncated_name, is_truncated)
    """
    if not course_name:
        return "Untitled Course", False
    
    words = course_name.split()
    if len(words) <= max_words:
        return course_name, False
    
    truncated = " ".join(words[:max_words]) + "..."
    return truncated, True

def escape_for_javascript(text):
    """Escape special characters for safe JavaScript string inclusion"""
    if not text:
        return ""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

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
    /* Cache buster: 2025-07-02-14:15 - Force CSS reload */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d35 50%, #252947 100%);
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
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8));
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(6, 182, 212, 0.2);
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
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(14, 165, 233, 0.1)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
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
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2)) !important;
        border-color: rgba(6, 182, 212, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
    }
    
    /* Enhanced Streamlit widgets */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0891b2 0%, #0284c7 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }
    
    /* Override default Streamlit button colors completely for main content */
    .stMain button[kind="primary"],
    .stMain button[data-testid*="stButton"] {
        background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%) !important;
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
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2));
        border: 1px solid rgba(6, 182, 212, 0.4);
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
        border-color: rgba(6, 182, 212, 0.5);
        background: rgba(255, 255, 255, 0.12);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(6, 182, 212, 0.2);
    }
    
    /* Text styling */
    .modern-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #06b6d4, #0ea5e9, #3b82f6);
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
        color: #06b6d4;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
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
        --sidebar-btn-bg: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(14, 165, 233, 0.1));
        --sidebar-btn-border: rgba(6, 182, 212, 0.3);
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
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2)) !important;
        border-color: rgba(6, 182, 212, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2) !important;
    }
</style>

<script>
// Store course titles for tooltip functionality
window.courseTitles = new Map();

// Force sidebar button style consistency and add tooltip functionality
function ensureSidebarButtonConsistency() {
    const sidebar = document.querySelector('.stSidebar');
    if (sidebar) {
        const buttons = sidebar.querySelectorAll('button');
        buttons.forEach(button => {
            // Force re-application of our custom styles
            button.style.setProperty('background', 'linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(14, 165, 233, 0.1))', 'important');
            button.style.setProperty('color', '#e2e8f0', 'important');
            button.style.setProperty('border', '1px solid rgba(6, 182, 212, 0.3)', 'important');
            button.style.setProperty('border-radius', '12px', 'important');
            button.style.setProperty('font-weight', '500', 'important');
        });
    }
}

// Add custom tooltip functionality for course buttons
function addCourseTooltips() {
    window.courseTitles.forEach((fullTitle, buttonText) => {
        const buttons = document.querySelectorAll('.stSidebar button');
        buttons.forEach(button => {
            if (button.textContent.trim() === buttonText && buttonText.includes('...')) {
                // Remove any existing tooltip
                const existingTooltip = button.parentElement.querySelector('.custom-course-tooltip');
                if (existingTooltip) {
                    existingTooltip.remove();
                }
                
                // Create tooltip element
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-course-tooltip';
                tooltip.textContent = fullTitle;
                tooltip.style.cssText = `
                    position: absolute;
                    bottom: 110%;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.9);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 12px;
                    white-space: nowrap;
                    z-index: 9999;
                    opacity: 0;
                    visibility: hidden;
                    transition: opacity 0.3s ease, visibility 0.3s ease;
                    pointer-events: none;
                    max-width: 300px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                `;
                
                // Add arrow
                const arrow = document.createElement('div');
                arrow.style.cssText = `
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    border: 5px solid transparent;
                    border-top-color: rgba(0, 0, 0, 0.9);
                `;
                tooltip.appendChild(arrow);
                
                // Make button container relative positioned
                button.parentElement.style.position = 'relative';
                button.parentElement.appendChild(tooltip);
                
                // Add hover events
                button.addEventListener('mouseenter', () => {
                    tooltip.style.opacity = '1';
                    tooltip.style.visibility = 'visible';
                });
                
                button.addEventListener('mouseleave', () => {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                });
            }
        });
    });
}

// Combined function to run all enhancements
function enhanceSidebar() {
    ensureSidebarButtonConsistency();
    addCourseTooltips();
}

// Run immediately and on DOM changes
enhanceSidebar();
const observer = new MutationObserver(enhanceSidebar);
observer.observe(document.body, { childList: true, subtree: true });

// Also run when Streamlit finishes loading
window.addEventListener('load', enhanceSidebar);
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

# --- OAuth Callback Detection ---
# Check if this is a Google OAuth callback and handle it directly BEFORE navigation setup
query_params = st.query_params
if 'code' in query_params and 'state' in query_params and MONGO_AVAILABLE:
    # This is a Google OAuth callback, process it here
    try:
        from google_oauth_simple import handle_oauth_callback, is_google_oauth_configured
        
        if is_google_oauth_configured():
            google_user_info = handle_oauth_callback(query_params)
            if google_user_info:
                # Check if user exists with this Google ID
                existing_user = manager.find_user_by_google_id(google_user_info['google_id'])
                if existing_user:
                    # User exists, log them in
                    st.session_state['authentication_status'] = True
                    st.session_state['username'] = existing_user['username']
                    st.session_state['name'] = existing_user.get('name')
                    st.session_state['email'] = existing_user.get('email')
                    
                    # Update cookies
                    if cookies is not None:
                        try:
                            if cookies.ready():
                                cookies[AUTH_COOKIE_NAME] = existing_user['username']
                                cookies.save()
                        except (AttributeError, TypeError):
                            pass
                    
                    st.success("Logged in successfully with Google!")
                    st.rerun()
                else:
                    # User doesn't exist, store for signup and continue to show the current page
                    # The login page will handle the pending signup
                    st.session_state['pending_google_signup'] = google_user_info
                    st.warning("Google account not linked. Please link your account or create a new one.")
            else:
                # OAuth failed
                st.error("OAuth authentication failed. Please try again.")
        else:
            # OAuth not configured
            st.error("Google OAuth is not properly configured.")
    except ImportError:
        # Google OAuth not available
        st.error("Google OAuth is not available due to missing dependencies.")

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
                            truncated_title, is_truncated = truncate_course_name(course_title)
                            
                            # Register course title for tooltip if truncated
                            if is_truncated:
                                escaped_truncated = escape_for_javascript(truncated_title)
                                escaped_full = escape_for_javascript(course_title)
                                st.markdown(f"""
                                <script>
                                if (typeof window.courseTitles === 'undefined') {{
                                    window.courseTitles = new Map();
                                }}
                                window.courseTitles.set("{escaped_truncated}", "{escaped_full}");
                                </script>
                                """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([0.8, 0.2])
                            with col1:
                                if st.button(truncated_title, key=f"nav_{course_id}", use_container_width=True):
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
                        truncated_title, is_truncated = truncate_course_name(course_title)
                        
                        # Register course title for tooltip if truncated
                        if is_truncated:
                            escaped_truncated = escape_for_javascript(truncated_title)
                            escaped_full = escape_for_javascript(course_title)
                            st.markdown(f"""
                            <script>
                            if (typeof window.courseTitles === 'undefined') {{
                                window.courseTitles = new Map();
                            }}
                            window.courseTitles.set("{escaped_truncated}", "{escaped_full}");
                            </script>
                            """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([0.8, 0.2])
                        with col1:
                            if st.button(truncated_title, key=f"nav_{course_id}", use_container_width=True):
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
