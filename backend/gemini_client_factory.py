"""
Gemini Client Factory with OAuth Support
========================================
Provides a factory for creating Gemini clients with user OAuth credentials
and automatic fallback to shared API key. Implements quota project billing
and token refresh handling.
"""

import logging
import os
from typing import Optional, Tuple
from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Shared API key fallback
SHARED_API_KEY = os.getenv("GEMINI_API_KEY")

# OAuth scopes required for Gemini API
GEMINI_OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/generative-language.retriever'
]


def create_gemini_client(
    user_credentials: Optional[dict] = None,
    quota_project_id: Optional[str] = None,
    username: Optional[str] = None
) -> Tuple[genai.Client, dict]:
    """
    Create a Gemini client with user OAuth credentials or fallback to shared API key.
    
    Args:
        user_credentials: Dictionary containing OAuth tokens:
            - access_token: Current access token
            - refresh_token: Refresh token for getting new access tokens
            - token_uri: OAuth token endpoint URI
            - client_id: OAuth client ID
            - client_secret: OAuth client secret
            - expiry: Token expiration timestamp (ISO format string)
            - quota_project_id: Project ID for quota billing
        quota_project_id: Override quota project ID (optional)
        username: Username for logging purposes (optional)
    
    Returns:
        Tuple of (client, metadata):
            - client: Configured genai.Client instance
            - metadata: Dict with quota_source, username, project_id
    """
    metadata = {
        "quota_source": None,
        "username": username,
        "project_id": None
    }
    
    # Try to use user OAuth credentials first
    if user_credentials and _validate_user_credentials(user_credentials):
        try:
            client, project_id = _create_oauth_client(user_credentials, quota_project_id)
            metadata["quota_source"] = "user_oauth"
            metadata["project_id"] = project_id
            logger.info(f"✓ Created Gemini client with user OAuth credentials (user={username}, project={project_id})")
            return client, metadata
        except Exception as e:
            logger.warning(f"⚠ Failed to create OAuth client for {username}: {e}. Falling back to shared API key.")
    
    # Fallback to shared API key
    if not SHARED_API_KEY:
        raise ValueError("No user credentials provided and GEMINI_API_KEY not configured")
    
    try:
        client = genai.Client(api_key=SHARED_API_KEY)
        metadata["quota_source"] = "shared_api_key"
        logger.info(f"✓ Created Gemini client with shared API key (user={username or 'guest'})")
        return client, metadata
    except Exception as e:
        logger.error(f"✗ Failed to create Gemini client with shared API key: {e}")
        raise


def _validate_user_credentials(creds: dict) -> bool:
    """Validate that user credentials dict has required fields"""
    required_fields = ['refresh_token', 'token_uri', 'client_id', 'client_secret']
    return all(creds.get(field) for field in required_fields)


def _create_oauth_client(
    user_creds: dict,
    quota_project_override: Optional[str] = None
) -> Tuple[genai.Client, str]:
    """
    Create a Gemini client using user OAuth credentials with quota project billing.
    
    Args:
        user_creds: User OAuth credentials dictionary
        quota_project_override: Optional project ID to override stored quota_project_id
    
    Returns:
        Tuple of (client, quota_project_id)
    """
    # Extract quota project ID (use override if provided, else from creds)
    quota_project_id = quota_project_override or user_creds.get('quota_project_id')
    
    if not quota_project_id:
        raise ValueError("quota_project_id is required for OAuth-based Gemini usage")
    
    # Create OAuth2 credentials object
    creds = Credentials(
        token=user_creds.get('access_token'),  # May be None - will refresh if needed
        refresh_token=user_creds.get('refresh_token'),
        token_uri=user_creds.get('token_uri'),
        client_id=user_creds.get('client_id'),
        client_secret=user_creds.get('client_secret'),
        scopes=GEMINI_OAUTH_SCOPES,
        quota_project_id=quota_project_id
    )
    
    # Refresh credentials if expired or missing access token
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            logger.info("Refreshing expired OAuth credentials...")
            creds.refresh(Request())
            logger.info("✓ OAuth credentials refreshed successfully")
        elif not creds.token:
            logger.info("No access token present, refreshing...")
            creds.refresh(Request())
            logger.info("✓ OAuth credentials refreshed successfully")
    
    # Create HttpOptions with quota project header
    # The x-goog-user-project header tells Google to bill quota to the user's project
    http_options = types.HttpOptions(
        headers={
            'x-goog-user-project': quota_project_id
        }
    )
    
    # Create Gemini client with OAuth credentials and quota headers
    client = genai.Client(
        credentials=creds,
        http_options=http_options
    )
    
    return client, quota_project_id


def get_refreshed_tokens(user_creds: dict) -> Optional[dict]:
    """
    Refresh OAuth tokens and return updated token data for storage.
    
    Args:
        user_creds: User OAuth credentials dictionary
    
    Returns:
        Dictionary with updated tokens (access_token, expiry) or None if refresh failed
    """
    if not _validate_user_credentials(user_creds):
        logger.warning("Cannot refresh: invalid credentials structure")
        return None
    
    try:
        creds = Credentials(
            token=user_creds.get('access_token'),
            refresh_token=user_creds.get('refresh_token'),
            token_uri=user_creds.get('token_uri'),
            client_id=user_creds.get('client_id'),
            client_secret=user_creds.get('client_secret'),
            scopes=GEMINI_OAUTH_SCOPES,
            quota_project_id=user_creds.get('quota_project_id')
        )
        
        creds.refresh(Request())
        
        return {
            'access_token': creds.token,
            'expiry': creds.expiry.isoformat() if creds.expiry else None,
            'refresh_token': creds.refresh_token  # May be rotated
        }
    except Exception as e:
        logger.error(f"Failed to refresh OAuth tokens: {e}")
        return None


# For backward compatibility - default client with shared API key
def get_default_client() -> genai.Client:
    """Get a default Gemini client using shared API key (backward compatibility)"""
    if not SHARED_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    return genai.Client(api_key=SHARED_API_KEY)
