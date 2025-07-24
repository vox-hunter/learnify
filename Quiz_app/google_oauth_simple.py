"""
Streamlit-compatible Google OAuth implementation.
This module provides a more robust Google OAuth integration that works with Streamlit's
session-based architecture and deployment constraints.
"""

import streamlit as st
import urllib.parse
import webbrowser
import uuid
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth.exceptions


def get_google_oauth_url():
    """
    Generate a Google OAuth URL for manual authentication.
    This is a fallback method for environments where direct OAuth flow is challenging.
    
    Returns:
        str: Google OAuth URL for manual authentication
    """
    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        
        # Check if we have placeholder values
        if (client_id == "your-google-client-id.apps.googleusercontent.com" or 
            client_secret == "your-google-client-secret"):
            return None
            
        # For development/demo purposes, we'll use a simpler approach
        # In production, you'd set up proper redirect URLs
        
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            'client_id': client_id,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',  # For manual code copying
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"
        
    except KeyError:
        return None


def create_google_oauth_flow():
    """Create a Google OAuth flow for handling authentication."""
    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        
        if (client_id == "your-google-client-id.apps.googleusercontent.com" or 
            client_secret == "your-google-client-secret"):
            return None
            
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=['openid', 'email', 'profile']
        )
        
        # Use the 'out of band' redirect URI for manual code entry
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        return flow
        
    except KeyError:
        return None


def exchange_code_for_user_info(auth_code):
    """
    Exchange authorization code for user information.
    
    Args:
        auth_code: Authorization code from Google OAuth
        
    Returns:
        dict: User information or None if failed
    """
    try:
        flow = create_google_oauth_flow()
        if not flow:
            return None
        
        # Exchange code for token
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Get user info
        import requests
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        
        if response.status_code == 200:
            user_info = response.json()
            return {
                'google_id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'given_name': user_info.get('given_name'),
                'family_name': user_info.get('family_name'),
                'picture': user_info.get('picture'),
                'verified_email': user_info.get('verified_email', False)
            }
        else:
            st.error(f"Failed to get user info: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error exchanging code for user info: {e}")
        return None


def show_google_oauth_interface():
    """
    Show a user-friendly Google OAuth interface.
    Returns user info if authentication is successful.
    """
    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        
        # Check if OAuth is configured
        if (client_id == "your-google-client-id.apps.googleusercontent.com" or 
            client_secret == "your-google-client-secret"):
            st.info("🔧 Google OAuth is not configured. Please set up your Google Cloud credentials.")
            with st.expander("📖 How to set up Google OAuth"):
                st.markdown("""
                **Steps to configure Google OAuth:**
                
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create a new project or select an existing one
                3. Enable the Google+ API or Google Identity API
                4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
                5. Choose "Web application" as the application type
                6. Add your domain to "Authorized origins"
                7. Add authorized redirect URIs (for development: `http://localhost:8501`)
                8. Copy the Client ID and Client Secret to your secrets.toml file
                
                **Update your secrets.toml:**
                ```toml
                GOOGLE_CLIENT_ID = "your-actual-client-id.apps.googleusercontent.com"
                GOOGLE_CLIENT_SECRET = "your-actual-client-secret"
                ```
                """)
            return None
        
        oauth_url = get_google_oauth_url()
        if not oauth_url:
            st.error("Failed to generate OAuth URL")
            return None
        
        st.info("🔵 **Google OAuth Authentication**")
        st.write("Click the button below to authenticate with Google:")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🔵 Open Google Auth", use_container_width=True):
                st.markdown(f"[🔗 **Click here to authenticate with Google**]({oauth_url})")
                st.info("👆 Click the link above to open Google authentication in a new tab")
        
        with col2:
            st.markdown(f"[🔗 **Direct Link to Google Auth**]({oauth_url})")
        
        st.markdown("---")
        st.write("After authenticating, copy the authorization code and paste it below:")
        
        auth_code = st.text_input(
            "📋 Authorization Code", 
            placeholder="Paste the code from Google here...",
            help="Complete the authentication in the link above, then copy the code and paste it here"
        )
        
        if auth_code and st.button("✅ Verify Code", use_container_width=True):
            with st.spinner("Verifying with Google..."):
                user_info = exchange_code_for_user_info(auth_code.strip())
                if user_info:
                    st.success("✅ Google authentication successful!")
                    return user_info
                else:
                    st.error("❌ Authentication failed. Please try again.")
        
        return None
        
    except KeyError as e:
        st.error(f"Missing Google OAuth configuration: {e}")
        return None
    except Exception as e:
        st.error(f"OAuth error: {e}")
        return None


def is_google_oauth_configured():
    """Check if Google OAuth is properly configured."""
    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        
        return not (client_id == "your-google-client-id.apps.googleusercontent.com" or 
                   client_secret == "your-google-client-secret")
    except KeyError:
        return False