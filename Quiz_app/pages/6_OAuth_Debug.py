"""
OAuth Debug Helper
This page helps debug Google OAuth issues by showing detailed information
about the OAuth flow and current session state.
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from google_oauth_simple import is_google_oauth_configured, get_app_redirect_uri
    from oauth_config import get_oauth_redirect_uri
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

st.set_page_config(page_title="OAuth Debug", page_icon="🔍")

st.title("🔍 OAuth Debug Helper")

st.markdown("---")

# Configuration Info
st.subheader("Configuration")
col1, col2 = st.columns(2)

with col1:
    st.write("**OAuth Configured:**", is_google_oauth_configured())
    st.write("**Redirect URI:**", get_oauth_redirect_uri())
    st.write("**App Redirect URI:**", get_app_redirect_uri())

with col2:
    try:
        st.write("**Client ID:**", st.secrets["GOOGLE_CLIENT_ID"][:20] + "..." if len(st.secrets["GOOGLE_CLIENT_ID"]) > 20 else st.secrets["GOOGLE_CLIENT_ID"])
        st.write("**Client Secret:**", "***" + st.secrets["GOOGLE_CLIENT_SECRET"][-4:] if st.secrets["GOOGLE_CLIENT_SECRET"] else "Not set")
    except KeyError as e:
        st.error(f"Missing secret: {e}")

st.markdown("---")

# Current Request Info
st.subheader("Current Request")
query_params = st.query_params
st.write("**Query Parameters:**", dict(query_params))
st.write("**Has 'code':**", 'code' in query_params)
st.write("**Has 'state':**", 'state' in query_params)

if 'code' in query_params:
    st.write("**Authorization Code:**", query_params['code'][:20] + "..." if len(query_params['code']) > 20 else query_params['code'])

if 'state' in query_params:
    st.write("**Received State:**", query_params['state'])

st.markdown("---")

# Session State Info
st.subheader("Session State")
st.write("**OAuth State in Session:**", st.session_state.get('oauth_state', 'Not set'))
st.write("**Google Login Mode:**", st.session_state.get('google_login_mode', False))
st.write("**Authentication Status:**", st.session_state.get('authentication_status', 'Not set'))

# Show relevant session state keys
oauth_keys = [key for key in st.session_state.keys() if 'oauth' in key.lower() or 'google' in key.lower()]
if oauth_keys:
    st.write("**OAuth-related session keys:**")
    for key in oauth_keys:
        value = st.session_state[key]
        if isinstance(value, dict) and 'email' in value:
            # Don't show sensitive user info
            st.write(f"- {key}: User info (email: {value.get('email', 'N/A')})")
        else:
            st.write(f"- {key}: {value}")

st.markdown("---")

# Actions
st.subheader("Debug Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Clear Query Params"):
        st.query_params.clear()
        st.rerun()

with col2:
    if st.button("Clear OAuth Session"):
        keys_to_remove = [key for key in st.session_state.keys() if 'oauth' in key.lower() or 'google' in key.lower()]
        for key in keys_to_remove:
            del st.session_state[key]
        st.success(f"Cleared {len(keys_to_remove)} OAuth-related session keys")
        st.rerun()

with col3:
    if st.button("Test OAuth Flow"):
        from google_oauth_simple import get_google_oauth_url
        oauth_url, state = get_google_oauth_url()
        if oauth_url:
            st.success("OAuth URL generated successfully!")
            st.write("**OAuth URL:**", oauth_url[:100] + "..." if len(oauth_url) > 100 else oauth_url)
            st.write("**Generated State:**", state)
        else:
            st.error("Failed to generate OAuth URL")

st.markdown("---")

# Instructions
st.subheader("How to Use This Debug Page")
st.markdown("""
1. **Check Configuration**: Ensure OAuth is configured and redirect URI is correct
2. **Test OAuth Flow**: Click "Test OAuth Flow" to generate an OAuth URL
3. **Examine Callback**: After OAuth redirect, check the query parameters and session state
4. **Clear State**: Use the clear buttons to reset OAuth state if needed

**Common Issues:**
- **OAuth state mismatch**: Session state is cleared during redirect
- **Redirect URI mismatch**: Google Cloud Console settings don't match configuration
- **Missing secrets**: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set
""")
