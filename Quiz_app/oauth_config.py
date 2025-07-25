"""
Google OAuth Configuration for Learnify
========================================

IMPORTANT: Update the OAUTH_REDIRECT_URI below to match your deployment URL.

This URL must also be configured in your Google Cloud Console:
1. Go to Google Cloud Console > APIs & Services > Credentials
2. Select your OAuth 2.0 Client ID
3. Add this URL to "Authorized redirect URIs"

The URL should:
- Use HTTPS in production
- NOT have a trailing slash
- Match exactly what's configured in Google Cloud Console

Examples:
- Development: "http://localhost:8501"
- Render: "https://your-app-name.onrender.com"
- Streamlit Cloud: "https://your-app.streamlit.app"
"""

# ===== UPDATE THIS URL FOR YOUR DEPLOYMENT =====
OAUTH_REDIRECT_URI = "https://learnify-pr-17.onrender.com"
# ==============================================

# Don't modify below this line unless you know what you're doing
def get_oauth_redirect_uri():
    """Get the configured OAuth redirect URI."""
    return OAUTH_REDIRECT_URI
