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

# Import centralized OAuth configuration
try:
    from oauth_config import get_oauth_redirect_uri
except ImportError:
    # Fallback if oauth_config.py is not available
    def get_oauth_redirect_uri():
        return "https://learnify-pr-17.onrender.com"


def get_google_oauth_url():
    """
    Generate a Google OAuth URL for web application authentication.
    Uses proper redirect URI that points back to the Streamlit app.
    
    Returns:
        tuple: (oauth_url, state) or (None, None) if configuration is invalid
    """
    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        
        # Check if we have placeholder values
        if (client_id == "your-google-client-id.apps.googleusercontent.com" or 
            client_secret == "your-google-client-secret"):
            return None, None
            
        # Generate a state parameter for security
        state = str(uuid.uuid4())
        
        # Determine the redirect URI based on the current app URL
        # For development, use localhost:8501
        # For production, this should be the actual domain
        redirect_uri = get_app_redirect_uri()
        
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        
        query_string = urllib.parse.urlencode(params)
        oauth_url = f"{base_url}?{query_string}"
        
        # Store state in session for validation
        st.session_state['oauth_state'] = state
        
        return oauth_url, state
        
    except KeyError:
        return None, None


def get_app_redirect_uri():
    """
    Get the appropriate redirect URI for the current app environment.
    
    Returns:
        str: The redirect URI to use for OAuth
    """
    # Use the configured redirect URI from oauth_config.py
    return get_oauth_redirect_uri()
    
    # Original logic kept as comments for future reference:
    # # Try to detect the current app URL
    # try:
    #     # Check if we're running on Streamlit Cloud
    #     if hasattr(st, 'get_option') and st.get_option('server.baseUrlPath'):
    #         # Running on Streamlit Cloud or similar
    #         base_url = st.get_option('server.baseUrlPath')
    #         if not base_url.startswith('http'):
    #             base_url = f"https://{base_url}"
    #         return base_url
    # except:
    #     pass
    # 
    # # Check session state for custom redirect URI (can be set by admin)
    # if 'custom_oauth_redirect_uri' in st.session_state:
    #     return st.session_state['custom_oauth_redirect_uri']
    # 
    # # Default to localhost for development
    # return "http://localhost:8501"


def create_google_oauth_flow():
    """Create a Google OAuth flow for handling web application authentication."""
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
        
        # Use the app's redirect URI for web application flow
        flow.redirect_uri = get_app_redirect_uri()
        
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
            st.error("Failed to create OAuth flow")
            return None
        
        # Exchange code for token
        try:
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
        except Exception as token_error:
            st.error(f"Failed to exchange authorization code: {token_error}")
            return None
        
        # Get user info
        import requests
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {credentials.token}'},
                timeout=10  # Add timeout
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
                st.error(f"Failed to get user info from Google: HTTP {response.status_code}")
                return None
        except requests.RequestException as req_error:
            st.error(f"Network error while getting user info: {req_error}")
            return None
            
    except Exception as e:
        st.error(f"Error exchanging code for user info: {e}")
        return None


def show_google_oauth_interface():
    """
    Show a user-friendly Google OAuth interface for web applications.
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
                6. Add your domain to "Authorized origins": `https://learnify-pr-17.onrender.com`
                7. Add redirect URIs: `https://learnify-pr-17.onrender.com`
                8. Copy the Client ID and Client Secret to your secrets.toml file
                
                **Update your secrets.toml:**
                ```toml
                GOOGLE_CLIENT_ID = "your-actual-client-id.apps.googleusercontent.com"
                GOOGLE_CLIENT_SECRET = "your-actual-client-secret"
                ```
                """)
            return None
        
        # Check if we're returning from OAuth callback
        query_params = st.query_params
        if 'code' in query_params and 'state' in query_params:
            return handle_oauth_callback(query_params)
        
        # Generate OAuth URL
        oauth_url, state = get_google_oauth_url()
        if not oauth_url:
            st.error("Failed to generate OAuth URL")
            return None
        
        st.info("🔵 **Google OAuth Authentication**")
        st.write("Click the button below to authenticate with Google:")
        
        # Create a styled button that opens Google auth in the same tab
        if st.button("🔵 Continue with Google", use_container_width=True, type="primary"):
            # Use JavaScript to redirect to OAuth URL
            st.markdown(f"""
            <script>
                window.location.href = "{oauth_url}";
            </script>
            """, unsafe_allow_html=True)
            
            # Also provide a manual link as fallback
            st.markdown(f"If the redirect doesn't work, [click here to authenticate with Google]({oauth_url})")
            st.info("You will be redirected to Google for authentication, then back to this app.")
        
        return None
        
    except KeyError as e:
        st.error(f"Missing Google OAuth configuration: {e}")
        return None
    except Exception as e:
        st.error(f"OAuth error: {e}")
        return None


def handle_oauth_callback(query_params):
    """
    Handle the OAuth callback from Google.
    
    Args:
        query_params: Query parameters from the callback URL
        
    Returns:
        dict: User information or None if failed
    """
    try:
        # Verify state parameter to prevent CSRF attacks
        received_state = query_params.get('state')
        expected_state = st.session_state.get('oauth_state')
        
        if not expected_state or received_state != expected_state:
            st.error("OAuth state mismatch. Please try again.")
            # Clear the query params and state
            st.query_params.clear()
            if 'oauth_state' in st.session_state:
                del st.session_state['oauth_state']
            return None
        
        # Get authorization code
        auth_code = query_params.get('code')
        if not auth_code:
            st.error("No authorization code received from Google.")
            return None
        
        # Exchange code for user info
        with st.spinner("Verifying with Google..."):
            user_info = exchange_code_for_user_info(auth_code)
            
            # Clear the query params and state after successful authentication
            st.query_params.clear()
            if 'oauth_state' in st.session_state:
                del st.session_state['oauth_state']
            
            if user_info:
                st.success("✅ Google authentication successful!")
                return user_info
            else:
                st.error("❌ Authentication failed. Please try again.")
                return None
                
    except Exception as e:
        st.error(f"Error handling OAuth callback: {e}")
        # Clear state on error
        st.query_params.clear()
        if 'oauth_state' in st.session_state:
            del st.session_state['oauth_state']
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