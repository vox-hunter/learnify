import streamlit as st
import os
import sys
from streamlit_cookies_manager import EncryptedCookieManager

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import get_course_manager, get_session_id
    from email_verification import send_verification_email, generate_verification_code, verify_email_code
    MONGO_AVAILABLE = True
except ImportError as e:
    # It's okay to call st.error here after set_page_config
    st.error(f"Failed to import required modules: {e}")
    MONGO_AVAILABLE = False
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
except Exception:
    cookies_ready = False

if not cookies_ready:
    st.warning("Cookies are initializing... Authentication features may be limited.")
    # Don't stop - allow the page to continue with limited functionality

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
        except Exception as e:
            st.warning(f"⚠️ Error transferring guest courses: {e}")    # Update cookies in a single operation
    if cookies is not None:
        try:
            if cookies.ready():
                cookies["guest_courses_count"] = "0"  # Reset guest course count
                cookies[AUTH_COOKIE_NAME] = username  # Set auth cookie
                cookies.save() # Save all cookie changes at once
        except Exception:
            pass  # Ignore cookie errors during login
    st.rerun()

def logout_user():
    st.session_state['authentication_status'] = False
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.session_state['email'] = None    # Flagging is handled by main.py now
    if cookies is not None:
        try:
            if cookies.ready():
                # Set cookie to "logged_out" instead of deleting (more reliable)
                cookies[AUTH_COOKIE_NAME] = "logged_out"
                cookies.save()
        except Exception:
            pass  # Ignore cookie errors during logout
    st.rerun()

# Initialize session state variables if they don't exist
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None

manager = get_auth_manager()

# Auto-login is now handled by main.py

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
                    st.info("No changes detected.")
        
        # Delete Account Section
        st.subheader("🗑️ Delete Account")
        st.warning("⚠️ **Warning**: This action cannot be undone! This will permanently delete your account and all associated courses.")
        
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
                    📋 [**Terms & Conditions**](https://voxhunter.dev/terms) | 🔒 [**Privacy Policy**](https://voxhunter.dev/privacy)
                    """)
                    
                    # Add optional checkbox for marketing emails (default ticked)
                    marketing_emails = st.checkbox(
                        "I agree to receive marketing emails (optional)",
                        key="marketing_checkbox",
                        value=True,
                        help="Uncheck if you don't want to receive marketing emails"
                    )
                    
                    submitted_register = st.form_submit_button("Send Verification Email")

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
                                if success:
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
                
                with st.form("verify_registration_form", clear_on_submit=False):
                    entered_code = st.text_input("Enter 6-digit verification code")
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted_verify = st.form_submit_button("Verify & Complete Registration")
                    with col2:
                        resend_code = st.form_submit_button("Resend Code")
                    
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
                            else:
                                st.error(f"Failed to resend email: {email_message}")
                        else:
                            st.error(f"Failed to generate new code: {error}")
                
                # Option to go back and change details
                if st.button("← Change Registration Details"):
                    st.session_state.registration_step = 'details'
                    st.rerun()
        
        with forgot_password_tab:
            st.subheader("Reset Your Password")
            
            # Password reset flow state management
            if 'reset_step' not in st.session_state:
                st.session_state.reset_step = 'email'
            if 'reset_email' not in st.session_state:
                st.session_state.reset_email = None
            if 'reset_verification_code' not in st.session_state:
                st.session_state.reset_verification_code = None
            
            if st.session_state.reset_step == 'email':
                # Step 1: Enter email address
                st.write("Enter your email address to receive a password reset code.")
                with st.form("forgot_password_form", clear_on_submit=False):
                    fp_email = st.text_input("Email Address", key="fp_email", value=st.session_state.reset_email or "")
                    submitted_fp = st.form_submit_button("Send Reset Code")

                    if submitted_fp:
                        if not fp_email:
                            st.warning("Please enter your email address.")
                        else:
                            user = manager.find_user_by_email(fp_email)
                            if user:
                                # Generate and send verification code
                                reset_code = generate_verification_code()
                                st.session_state.reset_verification_code = reset_code
                                st.session_state.reset_email = fp_email
                                
                                # Store verification code in database
                                success, error = manager.store_verification_code(fp_email, reset_code, "password_reset")
                                if success:
                                    # Send email
                                    email_success, email_message = send_verification_email(fp_email, reset_code, "password_reset")
                                    if email_success:
                                        st.success(f"Password reset code sent to {fp_email}! Please check your inbox.")
                                        st.session_state.reset_step = 'verify'
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to send reset email: {email_message}")
                                else:
                                    st.error(f"Failed to generate reset code: {error}")
                            else:
                                st.error("No account found with that email address.")
            
            elif st.session_state.reset_step == 'verify':
                # Step 2: Verify code and set new password
                st.info(f"Please enter the reset code sent to {st.session_state.reset_email}")
                
                with st.form("verify_reset_form", clear_on_submit=False):
                    entered_code = st.text_input("Enter 6-digit reset code")
                    new_password = st.text_input("New Password", type="password")
                    confirm_new_password = st.text_input("Confirm New Password", type="password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted_reset = st.form_submit_button("Reset Password")
                    with col2:
                        resend_reset_code = st.form_submit_button("Resend Code")
                    
                    if submitted_reset:
                        if not all([entered_code, new_password, confirm_new_password]):
                            st.warning("Please fill all fields.")
                        elif new_password != confirm_new_password:
                            st.error("Passwords do not match.")
                        else:
                            # Verify the code
                            success, error = manager.verify_code(
                                st.session_state.reset_email, 
                                entered_code, 
                                "password_reset"
                            )
                            
                            if success:
                                # Find user and update password
                                user = manager.find_user_by_email(st.session_state.reset_email)
                                if user:
                                    success, error = manager.update_user_password(user['username'], new_password)
                                    if success:
                                        st.success("Password reset successfully! You can now log in with your new password.")
                                        
                                        # Reset state
                                        st.session_state.reset_step = 'email'
                                        st.session_state.reset_email = None
                                        st.session_state.reset_verification_code = None
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to update password: {error}")
                                else:
                                    st.error("User account not found.")
                            else:
                                st.error(f"Verification failed: {error}")
                    
                    if resend_reset_code:
                        # Generate new code and resend
                        new_code = generate_verification_code()
                        st.session_state.reset_verification_code = new_code
                        
                        success, error = manager.store_verification_code(
                            st.session_state.reset_email, 
                            new_code, 
                            "password_reset"
                        )
                        
                        if success:
                            email_success, email_message = send_verification_email(
                                st.session_state.reset_email, 
                                new_code, 
                                "password_reset"
                            )
                            if email_success:
                                st.success("New reset code sent!")
                            else:
                                st.error(f"Failed to resend email: {email_message}")
                        else:
                            st.error(f"Failed to generate new code: {error}")
                
                # Option to go back and change email
                if st.button("← Use Different Email"):
                    st.session_state.reset_step = 'email'
                    st.rerun()

# --- Footer or other elements outside the main auth flow ---
st.markdown("---")
# It's important to remove or adapt any leftover code that relied on the old authenticator's
# specific config structure (like YAML loading for credentials directly in this file).
# The MongoAuthManager now handles the direct interaction with the database for user data.
# If 'authenticate.yaml' was used for other settings, that logic would need to be preserved
# or migrated to MongoDB via manager.load_config/save_config if appropriate.
