#!/usr/bin/env python3
"""
Debug script to test streamlit-authenticator login issue
This script tests the exact authentication flow to identify the root cause
"""
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import bcrypt
import os

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml')
    with open(config_path, 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def test_bcrypt_verification():
    """Test bcrypt password verification directly"""
    config = load_config()
    
    st.write("## Direct bcrypt verification test")
    
    username = "tester"
    password = "Testing@123"
    
    if username in config['credentials']['usernames']:
        stored_hash = config['credentials']['usernames'][username]['password']
        
        st.write(f"**Username:** {username}")
        st.write(f"**Password:** {password}")
        st.write(f"**Stored hash:** `{stored_hash}`")
        
        # Test bcrypt verification
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            st.write(f"**Direct bcrypt verification:** {'✅ PASS' if is_valid else '❌ FAIL'}")
        except Exception as e:
            st.write(f"**Direct bcrypt verification:** ❌ ERROR - {e}")
    else:
        st.write(f"❌ Username '{username}' not found in config")

def test_authenticator_components():
    """Test authenticator initialization and components"""
    st.write("## Authenticator component test")
    
    try:
        config = load_config()
        st.write("✅ Config loaded successfully")
        
        # Check config structure
        required_keys = ['credentials', 'cookie']
        for key in required_keys:
            if key in config:
                st.write(f"✅ Config has '{key}' key")
            else:
                st.write(f"❌ Config missing '{key}' key")
        
        # Check credentials structure
        if 'usernames' in config.get('credentials', {}):
            usernames = list(config['credentials']['usernames'].keys())
            st.write(f"✅ Found usernames: {usernames}")
        else:
            st.write("❌ No usernames found in credentials")
        
        # Initialize authenticator
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        st.write("✅ Authenticator initialized successfully")
        
        return authenticator, config
        
    except Exception as e:
        st.write(f"❌ Authenticator initialization failed: {e}")
        return None, None

def test_login_function():
    """Test the login function specifically"""
    st.write("## Login function test")
    
    authenticator, config = test_authenticator_components()
    if not authenticator:
        st.write("❌ Cannot test login - authenticator failed to initialize")
        return
    
    # Manually test authentication methods
    username = "tester"
    password = "Testing@123"
    
    st.write(f"Testing login for username: **{username}** with password: **{password}**")
    
    # Check if we can access the internal authentication method
    try:
        # Access the credentials from the authenticator
        credentials = authenticator.credentials
        if username in credentials['usernames']:
            stored_password = credentials['usernames'][username]['password']
            
            # Test password verification using authenticator's method
            try:
                # This mimics what streamlit-authenticator does internally
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
                st.write(f"**Internal password check:** {'✅ PASS' if is_valid else '❌ FAIL'}")
                
                # Check user data structure
                user_data = credentials['usernames'][username]
                st.write("**User data structure:**")
                for key, value in user_data.items():
                    if key == 'password':
                        st.write(f"  - {key}: [HIDDEN]")
                    else:
                        st.write(f"  - {key}: {value}")
                        
            except Exception as e:
                st.write(f"❌ Internal password check failed: {e}")
        else:
            st.write(f"❌ Username '{username}' not found in authenticator credentials")
    except Exception as e:
        st.write(f"❌ Error accessing authenticator credentials: {e}")

def test_streamlit_login_widget():
    """Test the actual streamlit-authenticator login widget"""
    st.write("## Streamlit-Authenticator Login Widget Test")
    
    authenticator, config = test_authenticator_components()
    if not authenticator:
        st.write("❌ Cannot test login widget - authenticator failed to initialize")
        return
    
    st.write("**Note:** Use the login widget below with:")
    st.write("- Username: `tester`")
    st.write("- Password: `Testing@123`")
    
    try:
        # Test the actual login widget
        name, authentication_status, username = authenticator.login()
        
        st.write("### Login Results:")
        st.write(f"- **Name:** {name}")
        st.write(f"- **Authentication Status:** {authentication_status}")
        st.write(f"- **Username:** {username}")
        
        if authentication_status is True:
            st.success("🎉 Login successful!")
        elif authentication_status is False:
            st.error("❌ Login failed - Username/password incorrect")
        elif authentication_status is None:
            st.info("ℹ️ Please enter your credentials")
            
    except Exception as e:
        st.error(f"❌ Login widget error: {e}")

def main():
    st.title("🔍 Streamlit-Authenticator Debug Tool")
    st.write("This tool helps debug authentication issues.")
    
    # Run all tests
    test_bcrypt_verification()
    st.markdown("---")
    test_streamlit_login_widget()

if __name__ == "__main__":
    main()
