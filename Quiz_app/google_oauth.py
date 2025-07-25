"""
Google OAuth integration for Learnify authentication system.
Provides Google OAuth login/signup functionality while maintaining compatibility
with the existing MongoDB-based authentication system.
"""

import streamlit as st
import urllib.parse
import uuid
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth.exceptions


class GoogleOAuthManager:
    def __init__(self):
        """Initialize Google OAuth manager with Streamlit secrets."""
        try:
            self.client_id = st.secrets["GOOGLE_CLIENT_ID"]
            self.client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
            
            # Check if we have placeholder values
            if (self.client_id == "your-google-client-id.apps.googleusercontent.com" or 
                self.client_secret == "your-google-client-secret"):
                self.oauth_enabled = False
                st.warning("Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in secrets.toml")
            else:
                self.oauth_enabled = True
                
        except KeyError as e:
            st.error(f"Missing Google OAuth configuration in secrets: {e}")
            self.oauth_enabled = False
            self.client_id = None
            self.client_secret = None
    
    def get_authorization_url(self, redirect_uri):
        """
        Generate Google OAuth authorization URL.
        
        Args:
            redirect_uri: The URI to redirect to after authorization
            
        Returns:
            tuple: (authorization_url, state) or (None, None) if OAuth not enabled
        """
        if not self.oauth_enabled:
            return None, None
            
        try:
            # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=['openid', 'email', 'profile']
            )
            
            flow.redirect_uri = redirect_uri
            
            # Generate a state parameter for security
            state = str(uuid.uuid4())
            
            # Get authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            # Store flow and state in session state for later use
            st.session_state['oauth_flow'] = flow
            st.session_state['oauth_state'] = state
            
            return authorization_url, state
            
        except Exception as e:
            st.error(f"Error generating OAuth URL: {e}")
            return None, None
    
    def handle_oauth_callback(self, authorization_response_url):
        """
        Handle the OAuth callback and extract user information.
        
        Args:
            authorization_response_url: The full URL of the authorization response
            
        Returns:
            dict: User information or None if authentication failed
        """
        if not self.oauth_enabled:
            return None
            
        try:
            # Retrieve the flow from session state
            flow = st.session_state.get('oauth_flow')
            if not flow:
                st.error("OAuth flow not found in session state")
                return None
            
            # Fetch token
            flow.fetch_token(authorization_response=authorization_response_url)
            
            # Get user info from Google
            credentials = flow.credentials
            
            # Use the credentials to get user information
            from google.auth.transport.requests import Request
            import requests
            
            # Make request to Google's userinfo endpoint
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {credentials.token}'}
            )
            
            if response.status_code == 200:
                user_info = response.json()
                
                # Clean up session state
                if 'oauth_flow' in st.session_state:
                    del st.session_state['oauth_flow']
                if 'oauth_state' in st.session_state:
                    del st.session_state['oauth_state']
                
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
                st.error(f"Failed to get user info from Google: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error handling OAuth callback: {e}")
            return None
    
    def generate_username_from_google_info(self, google_user_info):
        """
        Generate a username from Google user information.
        
        Args:
            google_user_info: Dictionary containing Google user information
            
        Returns:
            str: Generated username
        """
        email = google_user_info.get('email', '')
        name = google_user_info.get('name', '')
        given_name = google_user_info.get('given_name', '')
        
        # Try to use the part before @ in email as username base
        if email and '@' in email:
            username_base = email.split('@')[0]
        elif given_name:
            username_base = given_name.lower().replace(' ', '')
        elif name:
            username_base = name.lower().replace(' ', '')
        else:
            username_base = 'user'
        
        # Remove any non-alphanumeric characters except underscores
        import re
        username_base = re.sub(r'[^a-zA-Z0-9_]', '', username_base)
        
        return username_base or 'googleuser'


def get_app_redirect_uri():
    """
    Get the appropriate redirect URI for the current app environment.
    
    Returns:
        str: The redirect URI to use for OAuth
    """
    # Try to detect the current app URL
    try:
        # Check if we're running on Streamlit Cloud
        if hasattr(st, 'get_option') and st.get_option('server.baseUrlPath'):
            # Running on Streamlit Cloud or similar
            base_url = st.get_option('server.baseUrlPath')
            if not base_url.startswith('http'):
                base_url = f"https://{base_url}"
            return base_url
    except:
        pass
    
    # Check session state for custom redirect URI (can be set by admin)
    if 'custom_oauth_redirect_uri' in st.session_state:
        return st.session_state['custom_oauth_redirect_uri']
    
    # Default to localhost for development
    return "http://localhost:8501"


def get_oauth_manager():
    """Get or create Google OAuth manager instance."""
    if 'google_oauth_manager' not in st.session_state:
        st.session_state.google_oauth_manager = GoogleOAuthManager()
    return st.session_state.google_oauth_manager


def create_google_oauth_button(button_text="Continue with Google", key="google_oauth_btn"):
    """
    Create a Google OAuth button that initiates the OAuth flow.
    
    Args:
        button_text: Text to display on the button
        key: Unique key for the button
        
    Returns:
        bool: True if button was clicked and OAuth can proceed
    """
    oauth_manager = get_oauth_manager()
    
    if not oauth_manager.oauth_enabled:
        st.info("🔧 Google OAuth is not configured. Please configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
        return False
    
    # Create a stylized Google OAuth button
    button_html = f"""
    <style>
    .google-oauth-btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 10px 16px;
        background-color: #ffffff;
        color: #757575;
        border: 1px solid #dadce0;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        transition: background-color 0.2s, box-shadow 0.2s;
        width: 100%;
        box-sizing: border-box;
    }}
    .google-oauth-btn:hover {{
        background-color: #f8f9fa;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }}
    .google-oauth-btn:active {{
        background-color: #f1f3f4;
    }}
    .google-icon {{
        width: 18px;
        height: 18px;
        margin-right: 8px;
    }}
    </style>
    <div class="google-oauth-btn" id="{key}">
        <svg class="google-icon" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        {button_text}
    </div>
    """
    
    # Display the button HTML
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Use Streamlit button for interaction
    return st.button(button_text, key=key, use_container_width=True)


def handle_google_oauth_redirect():
    """
    Handle Google OAuth redirect in Streamlit.
    This should be called on pages that handle OAuth callbacks.
    
    Returns:
        dict: User information if OAuth was successful, None otherwise
    """
    oauth_manager = get_oauth_manager()
    
    if not oauth_manager.oauth_enabled:
        return None
    
    # Check if we have OAuth parameters in the URL
    query_params = st.query_params
    
    if 'code' in query_params and 'state' in query_params:
        # Verify state parameter
        expected_state = st.session_state.get('oauth_state')
        received_state = query_params.get('state')
        
        if expected_state != received_state:
            st.error("OAuth state mismatch. Possible security issue.")
            return None
        
        # Construct the full authorization response URL
        # Get the current page URL from Streamlit
        redirect_uri = get_app_redirect_uri()
        
        auth_response_url = f"{redirect_uri}?code={query_params['code']}&state={query_params['state']}"
        if 'scope' in query_params:
            auth_response_url += f"&scope={query_params['scope']}"
        
        # Handle the callback
        user_info = oauth_manager.handle_oauth_callback(auth_response_url)
        
        # Clear the query parameters to avoid repeated processing
        st.query_params.clear()
        
        return user_info
    
    return None