import streamlit as st
import os
import sys
# from streamlit_cookies_manager import EncryptedCookieManager  # Commented out as it's unused

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
    
    /* Sidebar styling delegated to main.py */
    
    /* Ensure all text is light colored */
    .stMarkdown, .stText, p, div, span {
        color: #e2e8f0 !important;
    }
    
    /* Dark theme for Streamlit elements */
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
    }
    
    /* Main content container */
    .main-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 600px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Modern card styling */
    .auth-card {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(6, 182, 212, 0.1);
        border-radius: 10px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #06b6d4;
        font-weight: 500;
        padding: 8px 16px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        color: white !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    /* Form styling */
    .stForm {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(6, 182, 212, 0.2);
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
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #06b6d4;
        box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }
    
    /* Form submit button styling */
    .stForm .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        border-radius: 8px;
    }
    
    .stError {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
        border-radius: 8px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        border-radius: 8px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #2196F3, #1976D2);
        color: white;
        border-radius: 8px;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        margin: 0.5rem 0;
    }
    
    /* Title styling */
    h1, h2, h3 {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    /* Welcome section styling */
    .welcome-section {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #e2e8f0;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Danger zone styling */
    .danger-zone {
        background: linear-gradient(135deg, #ff4757, #ff3838);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 71, 87, 0.1);
        border-radius: 8px;
        color: #ff4757;
        font-weight: 500;
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
</style>
""", unsafe_allow_html=True)

try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import get_course_manager, get_session_id
    from email_verification import send_verification_email, generate_verification_code
    from google_oauth_simple import show_google_oauth_interface, is_google_oauth_configured
    # verify_email_code is not used in this file
    MONGO_AVAILABLE = True
except ImportError as e:
    # It's okay to call st.error here after set_page_config
    st.error(f"Failed to import required modules: {e}")
    MONGO_AVAILABLE = False
    
    # Define fallback functions to prevent NameError
    def is_google_oauth_configured():
        return False
    
    def show_google_oauth_interface():
        st.error("Google OAuth is not available due to import errors.")
        return None
    
    st.stop() # Stop if core auth module is missing

# --- Get Cookie Manager from Session State ---
cookies = st.session_state.get('cookies')
if cookies is None:
    # Try fallback initialization
    try:
        from cookie_fallback import ensure_cookie_manager
        if ensure_cookie_manager():
            cookies = st.session_state.get('cookies')
        else:
            st.error("Cookie manager not found in session state. Please run the app from the main entry point.")
            st.markdown("Please go back to the [Home page](/) to start the application properly.")
            st.stop()
    except ImportError:
        st.error("Cookie manager not found in session state. Please run the app from the main entry point.")
        st.markdown("Please go back to the [Home page](/) to start the application properly.")
        st.stop()

# Initialize cookies if they haven't been, e.g. on first run
# Note: On some deployment platforms, cookies might take time to initialize
try:
    cookies_ready = cookies is not None and cookies.ready()
except (AttributeError, TypeError):
    cookies_ready = False

AUTH_COOKIE_NAME = "username" # Name of the cookie storing the username
AUTH_VALID_COOKIE = "auth_valid"
AUTH_SESSION_COOKIE = "auth_session_v"

# --- Authentication State Management ---
def get_auth_manager():
    if "auth_manager" not in st.session_state:
        if MONGO_AVAILABLE:
            st.session_state.auth_manager = MongoAuthManager()
        else:
            st.error("MongoAuthManager is not available. Cannot proceed with authentication.")
            return None
    return st.session_state.auth_manager

def login_user(username, user_data):
    st.session_state['authentication_status'] = True
    st.session_state['username'] = username
    st.session_state['name'] = user_data.get('name')
    st.session_state['email'] = user_data.get('email')
    
    # Transfer guest courses to logged-in user if MongoDB is available
    if MONGO_AVAILABLE:
        try:
            session_id = get_session_id()
            course_manager = get_course_manager()
            transferred_count, transfer_error = course_manager.transfer_guest_courses(session_id, username)
            if transferred_count > 0:
                st.success(f"✅ {transferred_count} guest course{'s' if transferred_count != 1 else ''} transferred to your account!")
            elif transfer_error:
                st.warning(f"⚠️ Could not transfer guest courses: {transfer_error}")
        except (AttributeError, ImportError, ConnectionError, TypeError) as e:
            st.warning(f"⚠️ Error transferring guest courses: {e}")    # Update cookies in a single operation
    if cookies is not None:
        try:
            if cookies.ready():
                import time as _t
                cookies["guest_courses_count"] = "0"  # Reset guest course count
                cookies[AUTH_COOKIE_NAME] = username  # Set auth cookie
                cookies[AUTH_VALID_COOKIE] = '1'
                cookies[AUTH_SESSION_COOKIE] = str(int(_t.time()))
                cookies.save() # Persist all
        except (AttributeError, TypeError):
            pass  # Ignore cookie errors during login
    st.rerun()

def logout_user():
    # Set logout flag FIRST to prevent immediate re-login
    st.session_state['logout_just_occurred'] = True
    
    # List of keys to preserve during logout
    preserve_keys = [
        'cookies', 'selected_tab',  # UI state
        'auth_manager',  # Auth infrastructure 
        'app_loading_complete', 'app_fully_loaded',  # App state
        'logout_just_occurred'  # Logout flag - preserve this!
    ]

    # Create a new dictionary with only the preserved keys
    preserved_state = {key: st.session_state[key] for key in preserve_keys if key in st.session_state}

    # Clear the entire session state
    st.session_state.clear()

    # Restore the preserved keys
    for key, value in preserved_state.items():
        st.session_state[key] = value

    # Set authentication status to False explicitly
    st.session_state['authentication_status'] = False
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.session_state['email'] = None
    
    # Update / invalidate cookies (mirror main.py logic)
    if cookies is not None:
        try:
            if cookies.ready():
                cm = cookies
                try:
                    keys = list(cm.keys()) if hasattr(cm, 'keys') else []  # type: ignore
                except Exception:
                    keys = []
                for k in [AUTH_COOKIE_NAME, 'auth_valid', 'auth_session_v', 'guest_courses_count', 'learnify/auth_username']:
                    if k not in keys:
                        keys.append(k)
                for k in keys:
                    try:
                        if 'auth' in k.lower() or 'user' in k.lower() or k in ('guest_courses_count',):
                            cm[k] = 'logged_out' if k != 'auth_valid' else '0'
                    except Exception:
                        pass
                try:
                    cm.save()
                except Exception:
                    pass
        except (AttributeError, TypeError):
            pass  # Ignore cookie errors during logout
    
    # Clear any OAuth related query params
    st.query_params.clear()
    
    st.rerun()

# Initialize session state variables if they don't exist
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None

manager = get_auth_manager()

# Get query parameters for OAuth callback handling
query_params = st.query_params

# Auto-login is now handled by main.py

# --- UI Rendering ---
if not manager:
    st.error("Authentication system could not be initialized. Please check the logs.")
    st.stop()

if st.session_state.get('authentication_status'):
    # Welcome section for logged-in users
    st.markdown("""
    <div class="welcome-section">
        <h1>🎉 Welcome Back!</h1>
        <h3>{}</h3>
        <p>You are successfully logged in to AI Loom</p>
    </div>
    """.format(st.session_state.get('name', st.session_state.get('username', 'User'))), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    with col2:
        # Only show Reset Password for non-Google users
        current_user = manager.find_user_by_username(st.session_state['username'])
        is_google_user = current_user and current_user.get('google_linked', False)
        
        if not is_google_user:
            if st.button("🔑 Reset Password", use_container_width=True):
                st.session_state['selected_tab'] = "Forgot Password"
                logout_user()
        else:
            # Show a placeholder or different button for Google users
            st.info("🔗 Google Account - Password managed by Google")
    
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.subheader("📝 Update Your Details")
    
    # Check if current user is a Google user
    current_user = manager.find_user_by_username(st.session_state['username'])
    is_google_user = current_user and current_user.get('google_linked', False)
    
    with st.form("update_details_form", clear_on_submit=True):
        # Name field (always editable)
        new_name = st.text_input("Display Name", value=st.session_state.get('name', ''), 
                                help="Your display name shown to others")
        
        # Username field (always editable)
        new_username = st.text_input("Username", value=st.session_state.get('username', ''),
                                   help="Your unique username for login")
        
        # Email field (disabled for Google users)
        if is_google_user:
            st.text_input("Email", value=st.session_state.get('email', ''), 
                         disabled=True, help="Email cannot be changed for Google accounts")
            new_email = st.session_state.get('email', '')  # Keep current email
        else:
            new_email = st.text_input("Email", value=st.session_state.get('email', ''))
        
        submitted_update = st.form_submit_button("✅ Update Details")

        if submitted_update:
            updates = {}
            if new_name and new_name != st.session_state.get('name'):
                updates['name'] = new_name
            if new_username and new_username != st.session_state.get('username'):
                # Check if new username is available
                if not manager.find_user_by_username(new_username):
                    updates['username'] = new_username
                else:
                    st.error("Username already taken. Please choose a different one.")
                    st.stop()
            if not is_google_user and new_email and new_email != st.session_state.get('email'):
                updates['email'] = new_email
            
            if updates:
                success, error_msg = manager.update_user_details(st.session_state['username'], updates)
                if success:
                    st.success(f"Details updated successfully! {error_msg if error_msg else ''}")
                    # Update session state immediately
                    if 'name' in updates: st.session_state['name'] = updates['name']
                    if 'username' in updates: st.session_state['username'] = updates['username']
                    if 'email' in updates: st.session_state['email'] = updates['email']
                    st.rerun()
                else:
                    st.error(f"Failed to update details: {error_msg}")
            else:
                st.info("No changes detected.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Google Account Management Section
    current_user = manager.find_user_by_username(st.session_state['username'])
    if current_user:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("🔵 Google Account")
        
        if current_user.get('google_linked', False):
            st.success("✅ Your account is linked to Google")
            if st.button("🔓 Unlink Google Account", use_container_width=True):
                success, error = manager.unlink_google_account(st.session_state['username'])
                if success:
                    st.success("Google account unlinked successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to unlink Google account: {error}")
        else:
            st.info("🔗 Link your Google account for easier login")
            
            # Initialize Google linking mode
            if 'google_link_mode' not in st.session_state:
                st.session_state.google_link_mode = False
            
            if is_google_oauth_configured():
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔵 Link Google Account", use_container_width=True):
                        st.session_state.google_link_mode = True
                        st.rerun()
                with col2:
                    if st.session_state.google_link_mode and st.button("❌ Cancel Linking", use_container_width=True):
                        st.session_state.google_link_mode = False
                        st.rerun()
                
                if st.session_state.google_link_mode:
                    google_user_info = show_google_oauth_interface()
                    if google_user_info:
                        # Check if this Google account is already linked to another user
                        existing_google_user = manager.find_user_by_google_id(google_user_info['google_id'])
                        if existing_google_user:
                            st.error("This Google account is already linked to another user.")
                        else:
                            # Link the account
                            success, error = manager.link_google_account(
                                st.session_state['username'], 
                                google_user_info['google_id']
                            )
                            if success:
                                st.success("Google account linked successfully!")
                                st.session_state.google_link_mode = False
                                st.rerun()
                            else:
                                st.error(f"Failed to link Google account: {error}")
            else:
                st.info("Google OAuth is not configured.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Delete Account Section
    st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
    st.subheader("🗑️ Delete Account")
    st.warning("⚠️ **Warning**: This action cannot be undone! This will permanently delete your account and all associated courses.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("🔴 Delete My Account"):
        st.markdown("""
        **What will be deleted:**
        - Your user account and profile
        - All courses you've created
        - All course progress and data
        - All associated preferences and settings
        
        **This action is permanent and cannot be recovered.**
        """)
        
        with st.form("delete_account_form", clear_on_submit=False):
            st.write("To confirm account deletion, please type your username below:")
            confirm_username = st.text_input(
                f"Type '{st.session_state['username']}' to confirm:",
                placeholder="Enter your username to confirm deletion"
            )
            
            delete_checkbox = st.checkbox(
                "I understand this action is permanent and cannot be undone",
                key="delete_confirm_checkbox"
            )
            
            submitted_delete = st.form_submit_button(
                "🗑️ DELETE MY ACCOUNT PERMANENTLY",
                type="secondary",
                help="This will permanently delete your account"
            )

            if submitted_delete:
                if not delete_checkbox:
                    st.error("❌ You must check the confirmation checkbox to proceed.")
                elif not confirm_username:
                    st.error("❌ Please enter your username to confirm deletion.")
                elif confirm_username != st.session_state['username']:
                    st.error(f"❌ Username confirmation does not match. You entered '{confirm_username}' but expected '{st.session_state['username']}'.")
                else:                        # Perform account deletion
                    with st.spinner("Deleting account..."):
                        try:
                            # Delete user courses from course manager
                            course_mgr = get_course_manager()
                            courses, _ = course_mgr.get_user_courses(st.session_state['username'])
                            
                            courses_deleted = 0
                            if courses:
                                # Delete each course
                                for course in courses:
                                    try:
                                        if hasattr(course_mgr, 'courses_collection') and course_mgr.courses_collection is not None:
                                            delete_result = course_mgr.courses_collection.delete_one({
                                                "course_id": course.get("course_id"),
                                                "creator": st.session_state['username']
                                            })
                                            if delete_result.deleted_count > 0:
                                                courses_deleted += 1
                                    except (AttributeError, TypeError):
                                        continue  # Skip if course deletion fails
                            
                            # Delete user account
                            try:
                                if hasattr(manager, 'users_collection') and manager.users_collection is not None:
                                    user_delete_result = manager.users_collection.delete_one({
                                        "username": st.session_state['username']
                                    })
                                    
                                    if user_delete_result.deleted_count > 0:
                                        st.success(f"✅ Account deleted successfully! Removed {courses_deleted} courses.")
                                        st.balloons()
                                    
                                    # Clear session and redirect
                                    st.session_state.clear()
                                    if cookies is not None and cookies.ready():
                                        try:
                                            cookies.clear()
                                            cookies.save()
                                        except (AttributeError, TypeError):
                                            pass
                                    
                                    st.info("Redirecting to home page...")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete account. Please try again or contact support.")
                            except (AttributeError, TypeError):
                                st.error("❌ Database connection error. Please try again.")
                                
                        except (ConnectionError, ValueError) as e:
                            st.error(f"❌ Error deleting account: {str(e)}")
                            st.error("Please try again or contact support if the problem persists.")
                        except Exception as e:  # pylint: disable=broad-except
                            st.error(f"❌ Unexpected error: {str(e)}")
                            st.error("Please contact support for assistance.")
else: # Not authenticated, show login or registration
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    tab_names = ["Login", "Register", "Forgot Password"]
    
    # Determine the default index for the tabs
    default_index = 0
    if 'selected_tab' in st.session_state:
        try:
            default_index = tab_names.index(st.session_state.selected_tab)
            # Clear the state after using it so it doesn't persist
            del st.session_state['selected_tab']
        except (ValueError, KeyError):
            default_index = 0 # Default to login if tab name is invalid

    login_tab, register_tab, forgot_password_tab = st.tabs(tab_names)

    with login_tab:
        st.subheader("🔐 Login to Your Account")
        
        # Handle OAuth callback for login (DEBUG MODE - NO AUTO-REDIRECT)
        if 'code' in query_params and 'state' in query_params and is_google_oauth_configured():
            st.warning("🔍 DEBUG MODE: OAuth callback detected - processing without auto-redirect")
            st.write("**Query Parameters:**", dict(query_params))
            
            google_user_info = show_google_oauth_interface()
            
            if google_user_info:
                st.success("✅ Google user info received successfully!")
                st.json(google_user_info)
                
                # Check if user exists with this Google ID
                existing_google_user = manager.find_user_by_google_id(google_user_info['google_id'])
                if existing_google_user:
                    st.success(f"✅ Found existing Google user: {existing_google_user.get('name', existing_google_user['username'])}")
                    if st.button("Login as this user"):
                        login_user(existing_google_user['username'], existing_google_user)
                        st.rerun()
                else:
                    # Check if user exists with same email for account linking
                    existing_email_user = manager.find_user_by_email(google_user_info['email'])
                    if existing_email_user:
                        st.info(f"📧 Found existing account with email: {existing_email_user['username']}")
                        if st.button("Link Google account to existing account"):
                            st.session_state['pending_google_link'] = {
                                'google_info': google_user_info,
                                'existing_user': existing_email_user
                            }
                            st.rerun()
                    else:
                        st.error("❌ No account found with this Google account. Please sign up first or use the signup tab.")
                        st.info("💡 Tip: You can create an account with the same email address in the signup tab, then link your Google account.")
            else:
                st.error("❌ Failed to get Google user info")
            
            # Add clear button to reset OAuth state
            if st.button("🧹 Clear OAuth State and Continue"):
                st.query_params.clear()
                if 'oauth_state' in st.session_state:
                    del st.session_state['oauth_state']
                st.rerun()
        
        # Handle pending Google signup from main.py OAuth callback
        if 'pending_google_signup' in st.session_state:
            google_user_info = st.session_state['pending_google_signup']
            del st.session_state['pending_google_signup']
            
            # Check if user exists with same email for account linking
            existing_email_user = manager.find_user_by_email(google_user_info['email'])
            if existing_email_user:
                # Ask user if they want to link accounts
                st.session_state['pending_google_link'] = {
                    'google_info': google_user_info,
                    'existing_user': existing_email_user
                }
                st.rerun()
            else:
                st.error("No account found with this Google account. Please sign up first or create an account with the same email first.")
        
        # Handle pending Google account linking
        if 'pending_google_link' in st.session_state:
            st.info("🔗 Link your Google account to your existing account")
            pending_info = st.session_state['pending_google_link']
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Link Google Account", use_container_width=True):
                    success, error = manager.link_google_account(
                        pending_info['existing_user']['username'], 
                        pending_info['google_info']['google_id']
                    )
                    if success:
                        login_user(pending_info['existing_user']['username'], pending_info['existing_user'])
                        del st.session_state['pending_google_link']
                        st.success("Google account linked successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to link account: {error}")
            
            with col2:
                if st.button("❌ Use Different Account", use_container_width=True):
                    del st.session_state['pending_google_link']
                    st.rerun()
            
            st.markdown("---")
        
        # Google OAuth Login (only show if not handling callback)
        if 'google_login_mode' not in st.session_state:
            st.session_state.google_login_mode = False
        
        if is_google_oauth_configured() and not ('code' in query_params and 'state' in query_params):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔵 Login with Google", use_container_width=True):
                    st.session_state.google_login_mode = True
                    st.rerun()
            with col2:
                if st.session_state.google_login_mode and st.button("❌ Cancel Google Login", use_container_width=True):
                    st.session_state.google_login_mode = False
                    st.rerun()
            
            if st.session_state.google_login_mode:
                google_user_info = show_google_oauth_interface()
                # Note: During normal flow (not callback), this will return None
                # The actual processing happens when user returns from Google
                
                st.markdown("---")
        
        if not st.session_state.google_login_mode:
            st.markdown("**OR use username/password:**")
            
            with st.form("login_form", clear_on_submit=True):
                login_username = st.text_input("Username", key="login_uname")
                login_password = st.text_input("Password", type="password", key="login_pw")
                submitted_login = st.form_submit_button("🚀 Login")

                if submitted_login:
                    if not login_username or not login_password:
                        st.warning("Please enter username and password.")
                    else:
                        user = manager.find_user_by_username(login_username)
                        if user and manager.verify_password(login_password, user.get("password")):
                            login_user(login_username, user) # This will now also set the cookie
                            st.success("Logged in successfully!")
                            st.rerun() # Rerun to show logged-in view
                        else:
                            st.error("Invalid username or password.")
    
    with register_tab:
        st.subheader("✨ Create a New Account")
        
        # Handle pending Google signup from main.py OAuth callback
        if 'pending_google_signup' in st.session_state:
            google_user_info = st.session_state['pending_google_signup']
            del st.session_state['pending_google_signup']
            
            # Check if user exists with this email
            existing_email_user = manager.find_user_by_email(google_user_info['email'])
            if existing_email_user:
                st.error("An account with this email already exists. Please use the login tab to link your Google account.")
            else:
                # Check if Google ID already exists
                existing_google_user = manager.find_user_by_google_id(google_user_info['google_id'])
                if existing_google_user:
                    st.error("This Google account is already registered. Please use the login tab.")
                else:
                    # Store Google info for signup completion
                    st.session_state['google_signup_info'] = google_user_info
                    st.rerun()
        
        # Handle OAuth callback first, regardless of signup mode (DEBUG MODE - NO AUTO-REDIRECT)
        if 'code' in query_params and 'state' in query_params and is_google_oauth_configured():
            st.warning("🔍 DEBUG MODE: OAuth callback detected in signup tab - processing without auto-redirect")
            st.write("**Query Parameters:**", dict(query_params))
            
            google_user_info = show_google_oauth_interface()
            
            if google_user_info:
                st.success("✅ Google user info received successfully!")
                st.json(google_user_info)
                
                # Check if Google ID already exists (existing Google user - auto login)
                existing_google_user = manager.find_user_by_google_id(google_user_info['google_id'])
                if existing_google_user:
                    st.success(f"✅ Found existing Google user: {existing_google_user.get('name', existing_google_user['username'])}")
                    if st.button("Login as existing user"):
                        login_user(existing_google_user['username'], existing_google_user)
                        st.rerun()
                else:
                    # Check if user exists with this email (potential account linking)
                    existing_email_user = manager.find_user_by_email(google_user_info['email'])
                    if existing_email_user:
                        st.info(f"📧 Found existing account with email: {existing_email_user['username']}")
                        if st.button("Link to existing account (switch to login tab)"):
                            st.session_state['pending_google_link'] = {
                                'google_info': google_user_info,
                                'existing_user': existing_email_user
                            }
                            st.session_state['selected_tab'] = "Login"
                            st.rerun()
                        if st.button("Continue with new account signup"):
                            st.session_state['google_signup_info'] = google_user_info
                            st.rerun()
                    else:
                        st.info("✅ New user - ready for signup completion")
                        if st.button("Continue with account creation"):
                            st.session_state['google_signup_info'] = google_user_info
                            st.rerun()
            else:
                st.error("❌ Failed to get Google user info")
            
            # Add clear button to reset OAuth state
            if st.button("🧹 Clear OAuth State and Continue", key="signup_clear"):
                st.query_params.clear()
                if 'oauth_state' in st.session_state:
                    del st.session_state['oauth_state']
                st.rerun()
        
        # Handle Google signup completion
        if 'google_signup_info' in st.session_state:
            st.info("🎉 Complete your Google account setup")
            google_info = st.session_state['google_signup_info']
            
            # Generate a suggested username
            email = google_info.get('email', '')
            suggested_username = email.split('@')[0] if '@' in email else 'user'
            # Clean the username
            import re
            suggested_username = re.sub(r'[^a-zA-Z0-9_]', '', suggested_username) or 'googleuser'
            
            with st.form("complete_google_signup", clear_on_submit=False):
                st.text_input("Email (from Google)", value=google_info.get('email', ''), disabled=True)
                google_name = st.text_input("Full Name", value=google_info.get('name', ''), key="google_name")
                google_username = st.text_input("Username", value=suggested_username, key="google_username")
                
                st.markdown("---")
                
                # Terms and conditions checkbox
                st.markdown("**Legal Agreement Required:**")
                google_terms_agreed = st.checkbox(
                    "I agree to the Terms & Conditions and Privacy Policy",
                    key="google_terms_checkbox",
                    value=False
                )
                
                st.markdown("📋 [**Terms & Conditions**](https://ailoom.me/Terms) | 🔒 [**Privacy Policy**](https://ailoom.me/Privacy)")
                
                google_marketing_emails = st.checkbox(
                    "I agree to receive marketing emails (optional)",
                    key="google_marketing_checkbox",
                    value=True
                )
                
                submitted_google_signup = st.form_submit_button("✅ Complete Google Account Setup")
                
                if submitted_google_signup:
                    if not google_terms_agreed:
                        st.error("You must agree to the Terms & Conditions and Privacy Policy.")
                    elif not google_name or not google_username:
                        st.warning("Please fill in all required fields.")
                    else:
                        # Create the Google user
                        user_id, error, final_username = manager.create_google_user(
                            google_info, 
                            google_username, 
                            google_marketing_emails
                        )
                        
                        if error:
                            st.error(f"Account creation failed: {error}")
                        else:
                            # Update the name if it was changed
                            if google_name != google_info.get('name'):
                                manager.update_user_details(final_username, {'name': google_name})
                            
                            st.success(f"Google account created successfully! Username: {final_username}")
                            
                            # Log the user in
                            user_data = manager.find_user_by_username(final_username)
                            if user_data:
                                login_user(final_username, user_data)
                                del st.session_state['google_signup_info']
                                st.rerun()
            
            if st.button("❌ Cancel Google Signup"):
                del st.session_state['google_signup_info']
                st.rerun()
            
            st.markdown("---")
        
        # Google OAuth Signup (only show if not handling callback and not completing signup)
        if 'google_signup_mode' not in st.session_state:
            st.session_state.google_signup_mode = False
        
        if (is_google_oauth_configured() and 'google_signup_info' not in st.session_state and 
            not ('code' in query_params and 'state' in query_params)):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔵 Sign up with Google", use_container_width=True):
                    st.session_state.google_signup_mode = True
                    st.rerun()
            with col2:
                if st.session_state.google_signup_mode and st.button("❌ Cancel Google Signup", use_container_width=True):
                    st.session_state.google_signup_mode = False
                    st.rerun()
            
            if st.session_state.google_signup_mode:
                google_user_info = show_google_oauth_interface()
                # Note: During normal flow (not callback), this will return None
                # The actual processing happens when user returns from Google
                
                st.markdown("---")
        
        if not st.session_state.google_signup_mode and 'google_signup_info' not in st.session_state:
            st.markdown("**OR create account with email:**")
        
        # Registration flow state management
        if 'registration_step' not in st.session_state:
            st.session_state.registration_step = 'details'
        if 'registration_data' not in st.session_state:
            st.session_state.registration_data = {}
        if 'verification_code' not in st.session_state:
            st.session_state.verification_code = None
        
        if st.session_state.registration_step == 'details':
            # Step 1: Collect user details
            with st.form("registration_form", clear_on_submit=False):
                reg_name = st.text_input("Full Name", key="reg_name", value=st.session_state.registration_data.get('name', ''))
                reg_username = st.text_input("Username", key="reg_uname", value=st.session_state.registration_data.get('username', ''))
                reg_email = st.text_input("Email", key="reg_email", value=st.session_state.registration_data.get('email', ''))
                reg_password = st.text_input("Password", type="password", key="reg_pw")
                reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_cpw")
                  # Add mandatory checkbox for Terms & Conditions and Privacy Policy
                st.markdown("---")
                
                # Create the checkbox text with embedded links
                st.markdown("""
                **Legal Agreement Required:**
                """)
                terms_agreed = st.checkbox(
                    "I agree to the Terms & Conditions and Privacy Policy",
                    key="terms_checkbox",
                    value=False,
                    help="You must agree to our terms to create an account"
                )
                
                # Add clickable links below the checkbox
                st.markdown("""
                📋 [**Terms & Conditions**](https://ailoom.me/Terms) | 🔒 [**Privacy Policy**](https://ailoom.me/Privacy)
                """)
                
                # Add optional checkbox for marketing emails (default ticked)
                marketing_emails = st.checkbox(
                    "I agree to receive marketing emails (optional)",
                    key="marketing_checkbox",
                    value=True,
                    help="Uncheck if you don't want to receive marketing emails"
                )
                
                submitted_register = st.form_submit_button("📧 Send Verification Email")

                if submitted_register:
                    if not all([reg_name, reg_username, reg_email, reg_password, reg_confirm_password]):
                        st.warning("Please fill all fields.")
                    elif not terms_agreed:
                        st.error("You must agree to the Terms & Conditions and Privacy Policy to create an account.")
                    elif reg_password != reg_confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        # Check if username or email already exists
                        if manager.find_user_by_username(reg_username):
                            st.error("Username already exists.")
                        elif manager.find_user_by_email(reg_email):
                            st.error("Email already registered.")
                        else:                                # Store registration data temporarily
                            st.session_state.registration_data = {
                                'name': reg_name,
                                'username': reg_username,
                                'email': reg_email,
                                'password': reg_password,
                                'marketing_consent': marketing_emails
                            }
                            
                            # Generate and send verification code
                            verification_code = generate_verification_code()
                            st.session_state.verification_code = verification_code
                            
                            # Store verification code in database
                            success, error = manager.store_verification_code(reg_email, verification_code, "registration")
                            if success and reg_email:
                                # Send email
                                email_success, email_message = send_verification_email(reg_email, verification_code, "registration")
                                if email_success:
                                    st.success(f"Verification email sent to {reg_email}! Please check your inbox.")
                                    st.session_state.registration_step = 'verify'
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send verification email: {email_message}")
                            else:
                                st.error(f"Failed to generate verification code: {error}")
        
        elif st.session_state.registration_step == 'verify':
            # Step 2: Verify email
            st.info(f"Please enter the verification code sent to {st.session_state.registration_data.get('email', '')}")
            st.info("Please check your spam folder if you don't see it in your inbox.")
            with st.form("verify_registration_form", clear_on_submit=False):
                entered_code = st.text_input("Enter 6-digit verification code")
                col1, col2 = st.columns(2)
                with col1:
                    submitted_verify = st.form_submit_button("✅ Verify & Complete Registration")
                with col2:
                    resend_code = st.form_submit_button("🔄 Resend Code")
                
                if submitted_verify:
                    if not entered_code:
                        st.warning("Please enter the verification code.")
                    else:
                        # Verify the code
                        success, error = manager.verify_code(
                            st.session_state.registration_data['email'], 
                            entered_code, 
                            "registration"
                        )
                        
                        if success:                                # Create the user account
                            user_id, reg_error = manager.add_user(
                                st.session_state.registration_data['username'],
                                st.session_state.registration_data['password'],
                                st.session_state.registration_data['email'],
                                st.session_state.registration_data['name'],
                                st.session_state.registration_data['marketing_consent']
                            )
                            
                            if reg_error:
                                st.error(f"Registration failed: {reg_error}")
                            else:
                                # Mark email as verified
                                manager.mark_email_verified(st.session_state.registration_data['email'])
                                
                                st.success(f"Account created successfully for {st.session_state.registration_data['username']}! You can now log in.")
                                
                                # Reset registration state
                                st.session_state.registration_step = 'details'
                                st.session_state.registration_data = {}
                                st.session_state.verification_code = None
                                st.rerun()
                        else:
                            st.error(f"Verification failed: {error}")
                
                if resend_code:
                    # Generate new code and resend
                    new_code = generate_verification_code()
                    st.session_state.verification_code = new_code
                    
                    success, error = manager.store_verification_code(
                        st.session_state.registration_data['email'], 
                        new_code, 
                        "registration"
                    )
                    
                    if success:
                        email_success, email_message = send_verification_email(
                            st.session_state.registration_data['email'], 
                            new_code, 
                            "registration"
                        )
                        if email_success:
                            st.success("New verification code sent!")
                            st.info("Please check your spam folder if you don't see it in your inbox.")
                        else:
                            st.error(f"Failed to resend email: {email_message}")
                    else:
                        st.error(f"Failed to generate new code: {error}")
            
            # Option to go back and change details
            if st.button("← Change Registration Details"):
                st.session_state.registration_step = 'details'
                st.rerun()
    
    with forgot_password_tab:
        st.subheader("🔑 Reset Your Password")

        # Password reset flow state management
        if 'reset_step' not in st.session_state:
            st.session_state.reset_step = 'email'

        if st.session_state.reset_step == 'email':
            # Step 1: Enter email address
            st.write("Enter your email address to receive a password reset code.")
            with st.form("forgot_password_form"):
                fp_email = st.text_input("Email Address", key="fp_email_input")
                submitted_fp = st.form_submit_button("📧 Send Reset Code")

                if submitted_fp:
                    if not fp_email:
                        st.warning("Please enter your email address.")
                    else:
                        user = manager.find_user_by_email(fp_email)
                        if user:
                            # Check if this is a Google account
                            if user.get('google_linked', False):
                                st.error("🔗 This email is associated with a Google account. Password reset is not available for Google accounts. Please use Google's password recovery if needed.")
                            else:
                                # Generate and send verification code
                                reset_code = generate_verification_code()
                                
                                # Store verification code in database
                                success, error = manager.store_verification_code(fp_email, reset_code, "password_reset")
                                if success:
                                    # Send email
                                    email_success, email_message = send_verification_email(fp_email, reset_code, "password_reset")
                                    if email_success:
                                        st.session_state.reset_email = fp_email
                                        st.session_state.reset_step = 'verify'
                                        st.success(f"Password reset code sent to {fp_email}! Please check your inbox.")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to send reset email: {email_message}")
                                else:
                                    st.error(f"Failed to generate reset code: {error}")
                        else:
                            st.error("No account found with that email address.")
        
        elif st.session_state.reset_step == 'verify':
            # Step 2: Verify code and set new password
            st.info(f"Please enter the reset code sent to {st.session_state.get('reset_email')}")
            
            with st.form("verify_reset_form"):
                entered_code = st.text_input("Enter 6-digit reset code")
                new_password = st.text_input("New Password", type="password")
                confirm_new_password = st.text_input("Confirm New Password", type="password")
                
                submitted_reset = st.form_submit_button("🔑 Reset Password")

                if submitted_reset:
                    if not all([entered_code, new_password, confirm_new_password]):
                        st.warning("Please fill all fields.")
                    elif new_password != confirm_new_password:
                        st.error("Passwords do not match.")
                    else:
                        # Verify the code
                        email_to_verify = st.session_state.get('reset_email')
                        if email_to_verify:
                            success, error = manager.verify_code(
                                email_to_verify, 
                                entered_code, 
                                "password_reset"
                            )
                            
                            if success:
                                # Find user and update password
                                user = manager.find_user_by_email(email_to_verify)
                                if user:
                                    update_success, update_error = manager.update_user_password(user['username'], new_password)
                                    if update_success:
                                        st.success("Password reset successfully! You can now log in with your new password.")
                                        
                                        # Reset state
                                        st.session_state.reset_step = 'email'
                                        del st.session_state['reset_email']
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to update password: {update_error}")
                                else:
                                    st.error("User account not found.")
                            else:
                                st.error(f"Verification failed: {error}")
                        else:
                            st.error("Session expired. Please start the password reset process again.")

            if st.button("← Use Different Email"):
                st.session_state.reset_step = 'email'
                if 'reset_email' in st.session_state:
                    del st.session_state['reset_email']
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
