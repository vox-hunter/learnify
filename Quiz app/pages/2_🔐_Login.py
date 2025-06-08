"""
Login/Signup Page
"""
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load config functions
def load_config():
    """Load authentication config with fallback paths for cloud deployment"""
    potential_paths = [
        'authenticate.yaml',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authenticate.yaml'),
    ]
    
    for config_path in potential_paths:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.load(file, Loader=SafeLoader)
            return config
        except (FileNotFoundError, PermissionError):
            continue
    
    # Fallback to Streamlit secrets
    try:
        if hasattr(st, 'secrets') and 'authenticate' in st.secrets:
            return dict(st.secrets['authenticate'])
    except Exception:
        pass
    
    return None

def save_config(config):
    """Save config with error handling for cloud deployment"""
    potential_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authenticate.yaml'),
        'authenticate.yaml'
    ]
    
    for config_path in potential_paths:
        try:
            with open(config_path, 'w') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            return True
        except Exception:
            continue
    return False

# Set page config
st.set_page_config(
    page_title="Learnify - Login",
    page_icon="🔐",
    layout="centered"
)

# Apply modern CSS styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%);
    }
    
    /* Center container */
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        text-align: center;
    }
    
    /* Title styling */
    .login-title {
        font-size: 2.5rem;
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
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7a00cc, #5c0099);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 0, 255, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextInput > div > div > input[type="password"] {
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
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(26, 0, 51, 0.8);
        border-radius: 25px;
        padding: 10px 25px;
        border: 2px solid #9d00ff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
    }
      /* Back button */
    .back-btn {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 999;
    }
    
    /* Back button specific styling */
    .back-button-container .stButton > button {
        background: rgba(26, 0, 51, 0.9);
        color: white;
        border: 2px solid #9d00ff;
        border-radius: 25px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 14px;
        width: auto;
        min-width: 140px;
        white-space: nowrap;
        text-align: center;
    }
    
    .back-button-container .stButton > button:hover {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(157, 0, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Back button with better styling
    st.markdown('<div class="back-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 6])
    with col1:
        if st.button("← Back to Home", key="back_btn"):
            st.switch_page("pages/1_🏠_Home.py")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Title
    st.markdown('<h1 class="login-title">Welcome to Learnify</h1>', unsafe_allow_html=True)
    
    # Load authenticator
    authenticator, config = get_authenticator()
    
    if authenticator is None:
        st.error("🚫 Authentication system is temporarily unavailable")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Check if already authenticated
    if st.session_state.get('authentication_status'):
        st.success(f'✅ Welcome back, *{st.session_state.name}*!')
        st.info("🎓 You now have unlimited access to course generation.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Go to Home"):
                st.switch_page("pages/1_🏠_Home.py")
        with col2:
            if st.button("🚪 Logout"):
                try:
                    authenticator.logout()
                    st.rerun()
                except Exception as e:
                    st.error(f"Logout error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Authentication tabs
    login_tab, register_tab, forgot_tab = st.tabs(["🔐 Login", "📝 Register", "🔑 Reset Password"])
    
    with login_tab:
        st.markdown("### Sign in to your account")
        
        try:
            authenticator.login()
            
            if st.session_state.get('authentication_status'):
                st.success("✅ Login successful!")
                st.balloons()
                st.rerun()
            elif st.session_state.get('authentication_status') is False:
                st.error("❌ Username/password is incorrect")
        except Exception as e:
            st.error(f"Login error: {e}")
        
        # OAuth login section
        st.markdown("---")
        st.markdown("### Or sign in with")
        
        col1, col2 = st.columns(2)
        with col1:
            try:
                if config and 'oauth2' in config:
                    authenticator.experimental_guest_login(
                        'Login with Google',
                        provider='google',
                        oauth2=config['oauth2']
                    )
                else:
                    st.info("OAuth not configured")
            except Exception as e:
                st.error(f"Google login error: {e}")
        
        with col2:
            try:
                if config and 'oauth2' in config:
                    authenticator.experimental_guest_login(
                        'Login with Microsoft',
                        provider='microsoft',
                        oauth2=config['oauth2']
                    )
                else:
                    st.info("OAuth not configured")
            except Exception as e:
                st.error(f"Microsoft login error: {e}")
    
    with register_tab:
        st.markdown("### Create a new account")
        
        try:
            email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
                fields={
                    'Form name': '',
                    'Email': 'Email',
                    'Username': 'Username',
                    'Password': 'Password',
                    'Repeat password': 'Repeat password',
                    'Password hint': 'Password hint',
                    'Captcha': 'Captcha',
                    'Register': 'Create Account'
                },
                two_factor_auth=True
            )
            
            if email_of_registered_user:
                st.success('🎉 Account created successfully!')
                st.info("Please use your new credentials to login in the Login tab.")
                # Save the updated config
                config = load_config()
                save_config(config)
        except Exception as e:
            st.error(f"Registration error: {e}")
    
    with forgot_tab:
        st.markdown("### Reset your password")
        
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password(
                send_email=True
            )
            
            if username_of_forgotten_password:
                st.success('📧 New password sent to your email!')
                save_config(config)
            elif username_of_forgotten_password is False:
                st.error('❌ Username not found')
        except Exception as e:
            st.error(f"Password reset error: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_authenticator():
    """Create authenticator with robust error handling"""
    try:
        config = load_config()
        if not config:
            return None, None
            
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config.get('preauthorized', []),
            api_key=config.get('api_key')
        )
        return authenticator, config
    except Exception as e:
        st.error(f"Authentication system initialization failed: {e}")
        return None, None

if __name__ == "__main__":
    main()
