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
    initial_sidebar_state="expanded"
)

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
if MONGO_AVAILABLE:
    COOKIE_ENCRYPTION_KEY = st.secrets.get("COOKIE_ENCRYPTION_KEY", "YOUR_STRONG_SECRET_PASSWORD_FOR_COOKIES")
    cookies = EncryptedCookieManager(
        password=COOKIE_ENCRYPTION_KEY,
        prefix="learnify/auth",
    )
    st.session_state.cookies = cookies # Store cookies in session state

    if not cookies.ready():
        st.warning("Cookies are not ready. This may cause issues with authentication.")

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
        if not cookies.ready(): return
        cookie_username = cookies.get(AUTH_COOKIE_NAME)
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
        if cookies.ready():
            cookies[AUTH_COOKIE_NAME] = "logged_out"
            cookies.save()
        st.query_params.clear()
        st.rerun()
else:
    st.session_state['authentication_status'] = False
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

# --- Navigation Control ---
pg = st.navigation([home_page, login_page, course_page])

# --- Sidebar UI (Renders after st.navigation) ---
with st.sidebar:
    st.markdown("---")

    if st.session_state.get('authentication_status') and MONGO_AVAILABLE:
        st.header("Courses")
        course_manager = get_course_manager()
        if course_manager:
            courses, error = course_manager.get_user_courses(st.session_state['username'])
            if error:
                st.error(error)
            
            if courses:
                with st.container(height=400):
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
