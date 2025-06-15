"""
Login/Signup Page
"""
import streamlit as st
import sys
import os
from streamlit_cookies_manager import EncryptedCookieManager

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from mongo_auth import MongoAuthManager
    MONGO_AVAILABLE = True
except ImportError as e:
    # It's okay to call st.error here after set_page_config
    st.error(f"Failed to import MongoAuthManager. Ensure mongo_auth.py is in the correct path: {e}")
    MONGO_AVAILABLE = False
    st.stop() # Stop if core auth module is missing

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

# --- Cookie Manager Initialization ---
# TODO: Replace "YOUR_STRONG_SECRET_PASSWORD_FOR_COOKIES" with a value from st.secrets
# For example: st.secrets.get("COOKIE_ENCRYPTION_KEY", "default_fallback_key")
# Ensure this key is strong and kept secret.
COOKIE_ENCRYPTION_KEY = st.secrets.get("COOKIE_ENCRYPTION_KEY", "YOUR_STRONG_SECRET_PASSWORD_FOR_COOKIES")
if COOKIE_ENCRYPTION_KEY == "YOUR_STRONG_SECRET_PASSWORD_FOR_COOKIES":
    st.warning("Using default cookie encryption key. Please set COOKIE_ENCRYPTION_KEY in st.secrets for production.")

cookies = EncryptedCookieManager(
    password=COOKIE_ENCRYPTION_KEY,
    prefix="learnify/auth", # Optional: prefix for cookie names
    # key="session_cookie" # Optional: if you want to name the cookie instance
)
# Initialize cookies if they haven't been, e.g. on first run
if not cookies.ready():
    st.stop() # Cookies are not ready, something is wrong.

AUTH_COOKIE_NAME = "username" # Name of the cookie storing the username

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
    # Set cookie for persistent login (e.g., expires in 7 days)
    cookies[AUTH_COOKIE_NAME] = username 
    cookies.save() # Save cookies to the browser

def logout_user():
    st.session_state['authentication_status'] = False
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.session_state['email'] = None
    st.session_state['logout_just_occurred'] = True # Flag to prevent immediate re-login
    # Clear cookie
    if AUTH_COOKIE_NAME in cookies:
        del cookies[AUTH_COOKIE_NAME]
        cookies.save()

# Initialize session state variables if they don't exist
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None

manager = get_auth_manager()

def auto_login_from_cookie():
    if not manager:
        return # Auth manager not available

    # Check if already authenticated or if a logout just happened
    if st.session_state.get('authentication_status') or st.session_state.get('logout_just_occurred_processed_auto_login', False):
        return

    cookie_username = cookies.get(AUTH_COOKIE_NAME)
    if cookie_username:
        user_data = manager.find_user_by_username(cookie_username)
        if user_data:
            # Verify critical fields, e.g., password hash if storing a session token
            # For username-only cookie, direct lookup is the main check
            st.write(f"Auto-logging in user: {cookie_username} from cookie.") # Debug
            login_user(cookie_username, user_data)
            # Do not rerun here, let the main script flow continue
        else:
            # User in cookie not found in DB, clear invalid cookie
            st.warning("Invalid authentication cookie detected. Clearing.") # Debug
            del cookies[AUTH_COOKIE_NAME]
            cookies.save()

# --- Process logout flag and attempt auto-login ---
just_logged_out = st.session_state.pop('logout_just_occurred', False)
if just_logged_out:
    st.session_state['logout_just_occurred_processed_auto_login'] = True # Mark that this specific reload after logout has been processed for auto-login
else:
    # If not just logged out, clear the processed flag
    st.session_state.pop('logout_just_occurred_processed_auto_login', None) 
    # Attempt auto-login only if not authenticated and not immediately after a logout action
    if not st.session_state.get('authentication_status'):
        auto_login_from_cookie()


# --- UI Rendering ---
if not manager:
    st.error("Authentication system could not be initialized. Please check the logs.")
    st.stop()

# Main container for login/registration
container = st.container()

if st.session_state.get('authentication_status'):
    with container:
        st.title(f"Welcome {st.session_state.get('name', st.session_state.get('username'))}!")
        st.write("You are logged in.")
        if st.button("Logout"):
            logout_user()
            st.rerun() # Rerun to reflect logout state
        
        st.subheader("Update Your Details")
        with st.form("update_details_form", clear_on_submit=True):
            new_name = st.text_input("New Name", value=st.session_state.get('name', ''))
            new_email = st.text_input("New Email", value=st.session_state.get('email', ''))
            submitted_update = st.form_submit_button("Update Details")

            if submitted_update:
                updates = {}
                if new_name and new_name != st.session_state.get('name'):
                    updates['name'] = new_name
                if new_email and new_email != st.session_state.get('email'):
                    updates['email'] = new_email
                
                if updates:
                    success, error_msg = manager.update_user_details(st.session_state['username'], updates)
                    if success:
                        st.success(f"Details updated successfully! {error_msg if error_msg else ''}")
                        # Update session state immediately
                        if 'name' in updates: st.session_state['name'] = updates['name']
                        if 'email' in updates: st.session_state['email'] = updates['email']
                        st.rerun()
                    else:
                        st.error(f"Failed to update details: {error_msg}")
                else:
                    st.info("No changes to update.")

        st.subheader("Change Password")
        with st.form("change_password_form", clear_on_submit=True):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            submitted_change_password = st.form_submit_button("Change Password")

            if submitted_change_password:
                if not all([current_password, new_password, confirm_new_password]):
                    st.warning("Please fill in all password fields.")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match.")
                else:
                    user = manager.find_user_by_username(st.session_state['username'])
                    if user and manager.verify_password(current_password, user.get('password')):
                        success, error_msg = manager.update_user_password(st.session_state['username'], new_password)
                        if success:
                            st.success("Password changed successfully!")
                        else:
                            st.error(f"Failed to change password: {error_msg}")
                    else:
                        st.error("Incorrect current password.")


else: # Not authenticated, show login or registration
    with container:
        login_tab, register_tab, forgot_password_tab = st.tabs(["Login", "Register", "Forgot Password"])

        with login_tab:
            st.subheader("Login to Your Account")
            with st.form("login_form", clear_on_submit=True):
                login_username = st.text_input("Username", key="login_uname")
                login_password = st.text_input("Password", type="password", key="login_pw")
                submitted_login = st.form_submit_button("Login")

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
            st.subheader("Create a New Account")
            with st.form("registration_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_username = st.text_input("Username", key="reg_uname")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_pw")
                reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_cpw")
                submitted_register = st.form_submit_button("Register")

                if submitted_register:
                    if not all([reg_name, reg_username, reg_email, reg_password, reg_confirm_password]):
                        st.warning("Please fill all fields.")
                    elif reg_password != reg_confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        user_id, error = manager.add_user(reg_username, reg_password, reg_email, reg_name)
                        if error:
                            st.error(f"Registration failed: {error}")
                        else:
                            st.success(f"Account created successfully for {reg_username}! You can now log in.")
                            # Optionally, log the user in directly after registration
                            # user_data = {"name": reg_name, "email": reg_email} # Create a basic user_data dict
                            # login_user(reg_username, user_data)
                            # st.rerun()

        with forgot_password_tab:
            st.subheader("Forgot Your Password?")
            st.write("Enter your username. If an account exists, we'll guide you (currently, this is a placeholder for a password reset flow).")
            with st.form("forgot_password_form", clear_on_submit=True):
                fp_username = st.text_input("Username", key="fp_uname")
                submitted_fp = st.form_submit_button("Request Password Reset")

                if submitted_fp:
                    if not fp_username:
                        st.warning("Please enter your username.")
                    else:
                        user = manager.find_user_by_username(fp_username)
                        if user:
                            # Basic: In a real app, you'd email a reset link or a temporary password.
                            # For now, we can simulate generating a new password and *telling* the user
                            # to contact admin, or if we had an email service, send it.
                            # This is a simplified version.
                            # For demonstration, let's assume we can't directly reset and show it here.
                            st.info(f"User '{fp_username}' found. Password reset functionality is not fully implemented in this demo. Imagine a new password was generated and would be sent to your registered email.")
                            # Example:
                            # temp_password = "newRandomPassword123" # Generate a random password
                            # success, err = manager.update_user_password(fp_username, temp_password)
                            # if success:
                            #     st.success(f"A temporary password has been set for {fp_username}. Please check your email (simulated).")
                            # else:
                            #     st.error(f"Could not reset password: {err}")
                        else:
                            st.error("Username not found.")

# --- Footer or other elements outside the main auth flow ---
st.markdown("---")
st.info("Learnify - Your AI Learning Companion")

# It's important to remove or adapt any leftover code that relied on the old authenticator's
# specific config structure (like YAML loading for credentials directly in this file).
# The MongoAuthManager now handles the direct interaction with the database for user data.
# If 'authenticate.yaml' was used for other settings, that logic would need to be preserved
# or migrated to MongoDB via manager.load_config/save_config if appropriate.
