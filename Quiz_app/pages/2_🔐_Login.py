"""
Login Page - Simplified authentication interface
"""
import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Minimal CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton > button {
        background-color: #0066cc !important;
        color: white !important;
        border-radius: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# Import auth modules
try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import get_course_manager, get_session_id
    from google_oauth_simple import show_google_oauth_interface, is_google_oauth_configured
    MONGO_AVAILABLE = True
except ImportError as e:
    st.error(f"Authentication not available: {e}")
    MONGO_AVAILABLE = False

def main():
    st.title("🔐 Login")
    
    if not MONGO_AVAILABLE:
        st.error("Authentication system not available")
        return
    
    # Check if already logged in
    if st.session_state.get('authentication_status'):
        st.success(f"Welcome back, {st.session_state.get('name', 'User')}!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Home", type="primary"):
                st.switch_page("pages/1_🏠_Home.py")
        with col2:
            if st.button("Logout"):
                logout_user()
        return
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        login_form()
    
    with tab2:
        register_form()

def login_form():
    """Display login form"""
    with st.form("login"):
        st.subheader("Login to Your Account")
        
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login", type="primary"):
            if username and password:
                try:
                    manager = MongoAuthManager()
                    user_data = manager.authenticate_user(username, password)
                    
                    if user_data:
                        st.session_state['authentication_status'] = True
                        st.session_state['username'] = user_data.get('username')
                        st.session_state['name'] = user_data.get('name', username)
                        st.session_state['email'] = user_data.get('email')
                        
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                except Exception as e:
                    st.error(f"Login error: {str(e)}")
            else:
                st.error("Please enter both username and password")

def register_form():
    """Display registration form"""
    with st.form("register"):
        st.subheader("Create New Account")
        
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Register", type="primary"):
            if not all([name, username, email, password, password_confirm]):
                st.error("Please fill in all fields")
                return
            
            if password != password_confirm:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
            
            try:
                manager = MongoAuthManager()
                success, message = manager.register_user(
                    username=username,
                    password=password,
                    email=email,
                    name=name
                )
                
                if success:
                    st.success("Registration successful! Please login.")
                else:
                    st.error(f"Registration failed: {message}")
                    
            except Exception as e:
                st.error(f"Registration error: {str(e)}")

def logout_user():
    """Logout user and clear session"""
    # Clear session state
    for key in list(st.session_state.keys()):
        if key.startswith(('authentication', 'username', 'name', 'email')):
            del st.session_state[key]
    
    st.success("Logged out successfully!")
    st.rerun()

if __name__ == "__main__":
    main()