"""
AI Quiz and Course Generator - Main Entry Point
This script handles navigation and session management for the Learnify app.
"""

import streamlit as st
import os
import sys
from utils.lazy_imports import import_optional, prefetch_modules
from utils.navigation_cache import record_page_visit, cache_course_list, get_cached_course_list, purge_stale_course_cache, warm_next_pages, remove_course_from_cache

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
    
    truncated_result = " ".join(words[:max_words]) + "..."
    return truncated_result, True

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
    
        /* Preserve original casing for course buttons in sidebar */
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebarContent"] .stButton > button { text-transform: none !important; }
    
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

MongoAuthManager = import_optional("mongo_auth:MongoAuthManager")
get_course_manager_fn = import_optional("mongo_course_manager:get_course_manager")
EncryptedCookieManagerClass = import_optional("streamlit_cookies_manager:EncryptedCookieManager")
MONGO_AVAILABLE = all([MongoAuthManager, get_course_manager_fn, EncryptedCookieManagerClass])

# Warm heavy modules in background (non-blocking)
prefetch_modules(["mongo_auth", "mongo_course_manager", "streamlit_cookies_manager"])  # warm-up

# --- Auth & Cookie Management (No UI Rendering) ---
def initialize_cookie_manager():
    """Initialize cookie manager with error handling for deployment environments"""
    try:
        # Use only Streamlit secrets
        cookie_key = st.secrets.get("COOKIE_ENCRYPTION_KEY", "learnify-secure-key-2024-change-for-production")
        if EncryptedCookieManagerClass is None:
            raise ImportError("EncryptedCookieManager dependency not available")
        cookie_manager = EncryptedCookieManagerClass(
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
    AUTH_VALID_COOKIE = "auth_valid"
    AUTH_SESSION_COOKIE = "auth_session_v"
    LOGOUT_SENTINEL = "logged_out"

    def get_auth_manager():
        if "auth_manager" not in st.session_state:
            try:
                if MongoAuthManager is None:
                    raise ImportError("MongoAuthManager not available")
                st.session_state.auth_manager = MongoAuthManager()
            except (ImportError, ConnectionError, ValueError):
                st.session_state.auth_manager = None
        return st.session_state.auth_manager

    manager = get_auth_manager()
    
    def auto_login_from_cookie():
        # Block if just logged out during this cycle
        if st.session_state.get('logout_just_occurred'):
            return
        if st.session_state.get('authentication_status'):
            return
        if not hasattr(st.session_state, 'cookies') or st.session_state.cookies is None:
            return
        try:
            if not st.session_state.cookies.ready():
                return
        except Exception:
            return
        u = st.session_state.cookies.get(AUTH_COOKIE_NAME)
        valid = st.session_state.cookies.get(AUTH_VALID_COOKIE)
        if not u or u in (LOGOUT_SENTINEL,) or valid != '1':
            return
        if manager:
            user_data = manager.find_user_by_username(u)
            if user_data:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = u
                st.session_state['name'] = user_data.get('name')
                st.session_state['email'] = user_data.get('email')

    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    auto_login_from_cookie()

    def logout_user():
        # Mark logout
        st.session_state['logout_just_occurred'] = True
        # Preserve infrastructure (cookie manager, auth manager)
        preserve = {
            'cookies': st.session_state.get('cookies'),
            'auth_manager': st.session_state.get('auth_manager'),
            'logout_just_occurred': True,
        }
        st.session_state.clear()
        for k, v in preserve.items():
            if v is not None:
                st.session_state[k] = v
        st.session_state['authentication_status'] = False
        st.session_state['username'] = None
        st.session_state['name'] = None
        st.session_state['email'] = None
        # Invalidate cookies
        if hasattr(st.session_state, 'cookies') and st.session_state.cookies is not None:
            try:
                if st.session_state.cookies.ready():
                    cm = st.session_state.cookies
                    # Collect candidate keys
                    key_getter = []
                    try:
                        if hasattr(cm, 'keys'):
                            key_getter = list(cm.keys())  # type: ignore
                    except Exception:
                        pass
                    # Fallback known keys
                    for k in [AUTH_COOKIE_NAME, AUTH_VALID_COOKIE, AUTH_SESSION_COOKIE, 'guest_courses_count']:
                        if k not in key_getter:
                            key_getter.append(k)
                    for k in key_getter:
                        try:
                            cm[k] = LOGOUT_SENTINEL if k != AUTH_VALID_COOKIE else '0'
                        except Exception:
                            pass
                    try:
                        cm.save()
                    except Exception:
                        pass
            except Exception:
                pass
        # Client-side expiry (best effort)
        st.markdown(
            """
            <script>
            (function(){
              try {
                const SENT='logged_out';
                const FAR='Fri, 01 Jan 9999 00:00:00 GMT';
                const targets=[];
                document.cookie.split(';').forEach(c=>{
                  const name=c.split('=')[0].trim();
                  if(/learnify|username|auth_valid|auth_session_v|guest_courses_count/i.test(name)){
                    targets.push(name);
                  }
                });
                // Ensure explicit known names
                ['username','auth_valid','auth_session_v','guest_courses_count','learnify/auth_username'].forEach(n=>{if(!targets.includes(n)) targets.push(n);});
                targets.forEach(n=>{
                  document.cookie = n+'='+SENT+'; expires='+FAR+'; path=/; SameSite=Lax;';
                });
              } catch(e) { console.warn('Logout cookie overwrite failed', e); }
            })();
            </script>
            """,
            unsafe_allow_html=True
        )
        st.query_params.clear()
        st.rerun()

    # Enforce logout sentinel early (in case previous reload happened before JS ran fully)
    def _enforce_logout_sentinel():
        if not st.session_state.get('logout_just_occurred'):
            return
        try:
            if st.session_state.cookies and st.session_state.cookies.ready():
                cm = st.session_state.cookies
                # If username still not sentinel, force it and save
                uname = cm.get(AUTH_COOKIE_NAME)
                if uname and uname != LOGOUT_SENTINEL:
                    for k in [AUTH_COOKIE_NAME, AUTH_VALID_COOKIE, AUTH_SESSION_COOKIE]:
                        try:
                            if k == AUTH_VALID_COOKIE:
                                cm[k] = '0'
                            else:
                                cm[k] = LOGOUT_SENTINEL
                        except Exception:
                            pass
                    try:
                        cm.save()
                    except Exception:
                        pass
        except Exception:
            pass

    _enforce_logout_sentinel()

    # Optional debug panel for auth cookie troubleshooting
    if st.query_params.get('auth_debug') == '1':
        with st.sidebar.expander("Auth Debug", expanded=True):
            try:
                if cookies is not None and cookies.ready():
                    st.write({
                        'username_cookie': cookies.get(AUTH_COOKIE_NAME),
                        'auth_valid_cookie': cookies.get(AUTH_VALID_COOKIE),
                        'auth_session_cookie': cookies.get(AUTH_SESSION_COOKIE),
                        'logout_flag_session_state': st.session_state.get('logout_just_occurred'),
                        'session_auth': st.session_state.get('authentication_status'),
                        'session_username': st.session_state.get('username'),
                    })
                else:
                    st.write('Cookies not ready')
            except Exception as _dbg_e:
                st.write(f'Debug error: {_dbg_e}')
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
            if google_user_info and manager:
                # Check if user exists with this Google ID
                existing_user = manager.find_user_by_google_id(google_user_info['google_id']) if manager else None
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
                                import time as _t
                                cookies[AUTH_COOKIE_NAME] = existing_user['username']
                                cookies[AUTH_VALID_COOKIE] = '1'
                                cookies[AUTH_SESSION_COOKIE] = str(int(_t.time()))
                                cookies.save()
                        except (AttributeError, TypeError):
                            pass
                    
                    st.success("Logged in successfully with Google!")
                    st.rerun()
                else:
                    # User doesn't exist, create a new account automatically using Google info
                    st.info("Creating new account with Google information...")
                    
                    # Generate a base username from email or name
                    email = google_user_info.get('email', '')
                    name = google_user_info.get('name', '')
                    base_username = email.split('@')[0] if email else name.lower().replace(' ', '')
                    
                    # Create the new Google user
                    user_id = error_msg = final_username = None
                    if manager:
                        user_id, error_msg, final_username = manager.create_google_user(
                        google_user_info, 
                        base_username,
                        marketing_consent=False  # Default to false, user can change later
                        )
                    
                    if user_id and final_username:
                        # Successfully created, now log them in
                        st.session_state['authentication_status'] = True
                        st.session_state['username'] = final_username
                        st.session_state['name'] = google_user_info.get('name')
                        st.session_state['email'] = google_user_info.get('email')
                        
                        # Update cookies
                        if cookies is not None:
                            try:
                                if cookies.ready():
                                    import time as _t
                                    cookies[AUTH_COOKIE_NAME] = final_username
                                    cookies[AUTH_VALID_COOKIE] = '1'
                                    cookies[AUTH_SESSION_COOKIE] = str(int(_t.time()))
                                    cookies.save()
                            except (AttributeError, TypeError):
                                pass
                        
                        st.success(f"Welcome! Account created successfully with username: {final_username}")
                        st.rerun()
                    else:
                        st.error(f"Failed to create account: {error_msg}")
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

# Build navigation list (always include login_page so switching works)
nav_pages = [home_page, login_page, course_page, privacy_page, terms_page]

# --- Navigation Control ---
pg = st.navigation(nav_pages)
current_page_title = getattr(pg, 'title', None) or getattr(pg, 'name', None)
if current_page_title:
    record_page_visit(current_page_title)

# Warm likely next pages (lightweight, no blocking UI)
def _prefetch(page_name: str):
    # For now just touch course manager for Course page prediction
    if page_name == 'Course' and get_course_manager_fn:
        try:
            _cm_local = get_course_manager_fn()
            if _cm_local and st.session_state.get('authentication_status'):
                _cached_courses = get_cached_course_list()
                if _cached_courses is None:
                    _courses, _err = _cm_local.get_user_courses(st.session_state['username'])
                    if not _err:
                        cache_course_list(_courses)
                        valid_ids = [str(c.get('_id') or c.get('id') or c.get('course_id')) for c in _courses]
                        purge_stale_course_cache(valid_ids)
        except (RuntimeError, ValueError):
            pass

warm_next_pages(_prefetch)

# Hide the Account/Login link when authenticated
if st.session_state.get('authentication_status'):
    st.markdown(
        """
        <style>
        /* Hide sidebar nav link pointing to /Login when user authenticated */
        [data-testid="stSidebarNav"] a[href*="/Login"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Streamlit-Native Multipage Routing ---
# This implementation works with hosting platforms like Render, Streamlit Cloud, etc.
# without requiring server-side configuration.

# Handle page routing via query parameters (works with all hosting platforms)
page_param = st.query_params.get('page')
if page_param:
    page_routes = {
        'privacy': privacy_page,
        'terms': terms_page,
        'course': course_page,
        'login': login_page
    }
    
    allowed_pages = set(page_routes.keys())
    page_param_lower = page_param.lower()
    if page_param_lower in allowed_pages:
        target_page = page_routes[page_param_lower]
        st.switch_page(target_page)

# Display helpful routing information for sharing links
if st.query_params.get('show_routing_info'):
    st.info("""
    🔧 **Multipage Routing Information**
    
    **✅ Working Routes** (use these for sharing):
    - Privacy Policy: `?page=privacy`
    - Terms & Conditions: `?page=terms`
    - Course Page: `?page=course`
    - Login: `?page=login`
    
    **🔧 Direct URL Support**: For `/privacy` style URLs, server configuration is required.
    See `DEPLOYMENT_GUIDE.md` for platform-specific instructions.
    
    **📱 Share URLs**: Use query parameter format for reliable cross-platform sharing.
    """)

# Add navigation helper links in development mode
if st.query_params.get('dev_mode'):
    st.write("**Quick Navigation Links (Development):**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Privacy Policy"):
            st.query_params.page = 'privacy'
            st.rerun()
    
    with col2:
        if st.button("Terms & Conditions"):
            st.query_params.page = 'terms'
            st.rerun()
    
    with col3:
        if st.button("Course Page"):
            st.query_params.page = 'course'
            st.rerun()
    
    with col4:
        if st.button("Login"):
            st.query_params.page = 'login'
            st.rerun()

# --- Sidebar UI (Renders after st.navigation) ---
with st.sidebar:
    # Show debug info if available
    if 'debug_last_click' in st.session_state:
        st.info(f"Debug: {st.session_state.debug_last_click}")
    
    if st.session_state.get('authentication_status') and MONGO_AVAILABLE:
        st.header("Courses")
        _cm_sidebar = get_course_manager_fn() if get_course_manager_fn else None
        if _cm_sidebar:
            try:
                # Try read from cache first
                _cached_courses_sidebar = get_cached_course_list()
                if _cached_courses_sidebar is not None:
                    _courses_list, _err_sidebar = _cached_courses_sidebar, None
                else:
                    _courses_list, _err_sidebar = _cm_sidebar.get_user_courses(st.session_state['username'])
                    if not _err_sidebar:
                        cache_course_list(_courses_list)
                if _err_sidebar:
                    st.error(_err_sidebar)
                elif _courses_list:
                    num = len(_courses_list)
                    h = max(60, min(num * 50 + 20, 400))
                    wrapper = st.container(height=h) if num > 6 else st.container()
                    with wrapper:
                        for _course_doc in _courses_list:
                            cid_raw = _course_doc.get('_id') or _course_doc.get('id') or _course_doc.get('course_id')
                            if not cid_raw:
                                continue
                            cid = str(cid_raw)
                            title = _course_doc.get('title', 'Untitled Course')
                            trunc, is_trunc = truncate_course_name(title)
                            if is_trunc:
                                st.markdown(f"""
                                <script>
                                if (typeof window.courseTitles === 'undefined') {{ window.courseTitles = new Map(); }}
                                window.courseTitles.set("{escape_for_javascript(trunc)}", "{escape_for_javascript(title)}");
                                </script>
                                """, unsafe_allow_html=True)
                            col1, col2 = st.columns([0.8, 0.2])
                            with col1:
                                if st.button(trunc, key=f"nav_{cid}", use_container_width=True):
                                    st.session_state.current_course_id = cid
                                    st.query_params.course_id = cid
                                    st.switch_page("pages/3_Course.py")
                            with col2:
                                with st.popover("⋮", use_container_width=True):
                                    if st.button("Delete", key=f"delete_{cid}", use_container_width=True):
                                        ok, msg = _cm_sidebar.delete_course(cid, st.session_state['username'])
                                        if ok:
                                            # Update caches immediately so UI reflects change without full reload
                                            remove_course_from_cache(cid)
                                            # Also mutate in-flight list so current loop reflects removal without rerun
                                            try:
                                                _courses_list[:] = [c for c in _courses_list if str(c.get('_id') or c.get('id') or c.get('course_id')) != cid]
                                            except Exception:
                                                pass
                                            # Invalidate list cache so next build re-fetches if needed
                                            try:
                                                from utils.navigation_cache import invalidate_course_list_cache
                                                invalidate_course_list_cache()
                                            except Exception:
                                                pass
                                            st.success("Course deleted successfully!")
                                            st.rerun()
                                        else:
                                            st.error(f"Failed: {msg}")
                                    is_public = _course_doc.get('is_public', False)
                                    label = "Make Private" if is_public else "Make Public"
                                    if st.button(label, key=f"share_{cid}", use_container_width=True):
                                        ok, msg = _cm_sidebar.update_course_privacy(cid, st.session_state['username'], not is_public)
                                        if ok:
                                            st.success("Privacy updated.")
                                        else:
                                            st.error(msg)
                                        st.rerun()
                else:
                    st.info("No courses yet.")
            except (RuntimeError, ValueError):
                st.info("Courses temporarily unavailable.")
    
    st.markdown('<div style="margin-top: auto;"></div>', unsafe_allow_html=True)
    with st.container():
        if st.session_state.get('authentication_status'):
            # Direct Account button (no dropdown) -> navigate to account page
            display_name = st.session_state.get('name', st.session_state.get('username'))
            if st.button(f"👤 {display_name}", use_container_width=True, key="account_button"):
                st.switch_page(login_page)
        else:
            if st.button("Sign up / Login", icon="🔐", use_container_width=True):
                st.switch_page(login_page)

# --- Run Page ---
pg.run()

# Mark app as fully loaded
st.session_state['app_fully_loaded'] = True
