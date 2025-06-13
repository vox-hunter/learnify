"""
Login/Signup Page
"""
import streamlit as st
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from mongo_auth import MongoAuthManager
    MONGO_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import MongoAuthManager. Ensure mongo_auth.py is in the correct path: {e}")
    MONGO_AVAILABLE = False
    st.stop() # Stop if core auth module is missing

# Set page config FIRST - must be the very first Streamlit command
st.set_page_config(
    page_title="Learnify - Login",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    # Potentially add other user details you want in session state

def logout_user():
    st.session_state['authentication_status'] = False
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.session_state['email'] = None
    # Clear other session state variables related to the user

# Initialize session state variables if they don't exist
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None


# --- UI Rendering ---
manager = get_auth_manager()

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
                            login_user(login_username, user)
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
