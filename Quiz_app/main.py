"""
AI Quiz and Course Generator - Main Entry Point
This script handles navigation and session management for the Learnify app.
"""

import streamlit as st
import os
import sys

# --- Page Config ---
st.set_page_config(
    page_title="AI Loom",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"  # Set to expanded - we'll handle collapse via CSS
)

# --- Start Loading Animation ---
from streamlit_loading import start_background_loading, complete_loading, ensure_loading_cleanup

# Check if loading was already completed (for page refreshes/navigation)
if not st.session_state.get('app_loading_complete', False):
    # Start loading animation in background
    start_background_loading()
else:
    # Ensure loading UI is cleaned up on all pages
    ensure_loading_cleanup()

# --- Custom CSS to hide navigation links ---
st.markdown("""
<style>
    /* Hide the 'Course' link in the sidebar */
    a[data-testid="stSidebarNavLink"][href$="/Course"] {
        display: none;
    }
</style>
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
    except Exception as e:
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
        except Exception:
            cookies_ready = False
    
    if not cookies_ready:
        st.warning("Cookies are initializing... Authentication features may be limited.")

    AUTH_COOKIE_NAME = "username"

    def get_auth_manager():
        if "auth_manager" not in st.session_state:
            try:
                st.session_state.auth_manager = MongoAuthManager()
            except Exception:
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
        except Exception:
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
            except Exception:
                pass  # Ignore cookie errors during logout
                
        st.query_params.clear()
        st.rerun()
else:
    st.session_state['authentication_status'] = False
    st.session_state.cookies = None  # Ensure cookies is available even when MONGO is not available
    def logout_user(): # Define for non-mongo case
        st.session_state['authentication_status'] = False
        st.rerun()
        st.rerun()

# --- Pages Definition ---
home_page = st.Page("pages/1_🏠_Home.py", title="New Course", icon="➕", default=True)

if st.session_state.get('authentication_status'):
    login_page = st.Page("pages/2_🔐_Login.py", title="Account", icon="👤")
else:
    login_page = st.Page("pages/2_🔐_Login.py", title="Login", icon="🔐")
    
course_page = st.Page("pages/3_Course.py", title="Course")

# --- Navigation Control ---
pg = st.navigation([home_page, login_page, course_page])

# --- Sidebar UI (Renders after st.navigation) ---
with st.sidebar:
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
                                    st.session_state.current_course_id = course_id  # Store in session state
                                    st.query_params.course_id = course_id
                                    st.switch_page("pages/3_Course.py")
                            with col2:
                                with st.popover("⋮", use_container_width=True):
                                    if st.button("Delete", key=f"delete_{course_id}", use_container_width=True):
                                        success, msg = course_manager.delete_course(course_id, st.session_state['username'])
                                        if success:
                                            st.success("Course deleted.")
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                    
                                    is_public = course.get('is_public', False)
                                    share_label = "Make Private" if is_public else "Make Public"
                                    if st.button(share_label, key=f"share_{course_id}", use_container_width=True):
                                        success, msg = course_manager.update_course_privacy(course_id, st.session_state['username'], not is_public)
                                        if success:
                                            st.success("Privacy updated.")
                                            st.rerun()
                                        else:
                                            st.error(msg)
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
                                st.session_state.current_course_id = course_id  # Store in session state
                                st.query_params.course_id = course_id
                                st.switch_page("pages/3_Course.py")
                        with col2:
                            with st.popover("⋮", use_container_width=True):
                                if st.button("Delete", key=f"delete_{course_id}", use_container_width=True):
                                    success, msg = course_manager.delete_course(course_id, st.session_state['username'])
                                    if success:
                                        st.success("Course deleted.")
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                
                                is_public = course.get('is_public', False)
                                share_label = "Make Private" if is_public else "Make Public"
                                if st.button(share_label, key=f"share_{course_id}", use_container_width=True):
                                    success, msg = course_manager.update_course_privacy(course_id, st.session_state['username'], not is_public)
                                    if success:
                                        st.success("Privacy updated.")
                                        st.rerun()
                                    else:
                                        st.error(msg)
            else:
                st.info("No courses yet.")
    
    st.markdown('<div style="margin-top: auto;"></div>', unsafe_allow_html=True)
    with st.container():
        if st.session_state.get('authentication_status'):
            with st.popover(f"👤 {st.session_state.get('name', st.session_state.get('username'))}", use_container_width=True):
                if st.button("Logout", use_container_width=True):
                    logout_user()
                if st.button("Reset Password", use_container_width=True, key="sidebar_reset_password"):
                    st.switch_page("pages/2_🔐_Login.py")
        else:
            if st.button("Sign up / Login", icon="🔐", use_container_width=True):
                st.switch_page("pages/2_🔐_Login.py")

# --- Run Page ---
pg.run()

# Complete loading after everything is initialized
if not st.session_state.get('app_loading_complete', False):
    complete_loading()

# Mark loading as complete
st.session_state['app_fully_loaded'] = True
