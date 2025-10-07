# Gemini OAuth Quick Reference

## For Developers

### Using the Client Factory

```python
from gemini_client_factory import create_gemini_client

# With user OAuth credentials
client, metadata = create_gemini_client(
    user_credentials={
        'token': '...',
        'refresh_token': '...',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': '...',
        'client_secret': '...',
        'expiry': '2024-01-01T00:00:00Z'
    },
    quota_project_id='my-gcp-project',
    username='alice'
)

# metadata = {'quota_source': 'oauth', 'username': 'alice', 'project_id': 'my-gcp-project'}

# Without credentials (fallback to API key)
client, metadata = create_gemini_client()
# metadata = {'quota_source': 'api_key', 'username': None, 'project_id': None}

# Use client normally
response = client.models.generate_content(model='gemini-2.0-flash-exp', contents='Hello')
```

### Getting User OAuth Data

```python
from mongo_auth import MongoAuthManager

auth_manager = MongoAuthManager()

# Retrieve user's Gemini OAuth credentials
oauth_data = auth_manager.get_gemini_oauth('alice')
# Returns: {'access_token': '...', 'refresh_token': '...', 'quota_project_id': '...', ...}

# Store OAuth data (after OAuth flow)
auth_manager.store_gemini_oauth('alice', {
    'access_token': '...',
    'refresh_token': '...',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': '...',
    'client_secret': '...',
    'expiry': '2024-01-01T00:00:00Z',
    'quota_project_id': 'my-gcp-project'
})

# Update tokens after refresh
auth_manager.update_gemini_oauth_tokens(
    'alice',
    access_token='new_token',
    expiry='2024-01-02T00:00:00Z',
    refresh_token='new_refresh_token'  # Optional
)

# Remove credentials (disconnect)
auth_manager.remove_gemini_oauth('alice')
```

### API Endpoint Pattern

```python
from fastapi import Form, HTTPException
from typing import Optional

@app.post("/your-gemini-endpoint")
async def your_endpoint(
    param: str = Form(...),
    username: Optional[str] = Form(None)  # Add this
):
    # Retrieve OAuth credentials
    user_credentials = None
    quota_project_id = None
    if username and auth_manager:
        oauth_data = auth_manager.get_gemini_oauth(username)
        if oauth_data:
            user_credentials = {
                'token': oauth_data.get('access_token'),
                'refresh_token': oauth_data.get('refresh_token'),
                'token_uri': oauth_data.get('token_uri'),
                'client_id': oauth_data.get('client_id'),
                'client_secret': oauth_data.get('client_secret'),
                'expiry': oauth_data.get('expiry')
            }
            quota_project_id = oauth_data.get('quota_project_id')
    
    # Call backend with credentials
    result = your_backend_function(
        param=param,
        user_credentials=user_credentials,
        username=username,
        quota_project_id=quota_project_id
    )
    
    return result
```

### Backend Function Pattern

```python
from typing import Optional, Dict, Any
from gemini_client_factory import create_gemini_client
import logging

logger = logging.getLogger(__name__)

def your_backend_function(
    param: str,
    user_credentials: Optional[Dict[str, Any]] = None,
    username: Optional[str] = None,
    quota_project_id: Optional[str] = None
):
    # Create client with OAuth or fallback
    client, quota_metadata = create_gemini_client(
        user_credentials=user_credentials,
        quota_project_id=quota_project_id,
        username=username
    )
    
    # Log quota source
    quota_source = quota_metadata.get('quota_source', 'unknown')
    logger.info(f"Processing request using quota_source={quota_source}, user={username or 'anonymous'}")
    
    # Use client
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=param
    )
    
    return response.text
```

## For Frontend Developers

### Calling Endpoints with Username

```javascript
// In your API service
async generateCourse(file, username) {
  const formData = new FormData();
  formData.append('file', file);
  if (username) {
    formData.append('username', username); // Add username param
  }
  
  const response = await axios.post('/course/generate/upload', formData);
  return response.data;
}

// In chat
async sendChatMessage(message, sessionId, username) {
  const formData = new FormData();
  formData.append('message', message);
  if (sessionId) formData.append('session_id', sessionId);
  if (username) formData.append('username', username); // Add username param
  
  const response = await axios.post('/chat/message', formData);
  return response.data;
}
```

### OAuth Connection Flow (TODO - Not Implemented Yet)

```javascript
// 1. Initiate OAuth
async connectGeminiOAuth() {
  // Call backend to get OAuth URL
  const { auth_url } = await axios.post('/auth/gemini/connect', {
    username: this.username,
    quota_project_id: this.selectedProject  // User's GCP project choice
  });
  
  // Redirect to Google OAuth
  window.location.href = auth_url;
}

// 2. Handle callback (in AuthCallback component)
async mounted() {
  const code = this.$route.query.code;
  if (code) {
    // Exchange code for tokens and store in MongoDB
    await axios.post('/auth/gemini/callback', {
      code: code,
      username: this.username
    });
    
    // Show success message
    this.$router.push('/settings');
  }
}

// 3. Disconnect OAuth
async disconnectGeminiOAuth() {
  await axios.delete(`/auth/gemini/disconnect?username=${this.username}`);
  this.oauthConnected = false;
}

// 4. Check OAuth status
async checkOAuthStatus() {
  const { connected, quota_project_id } = await axios.get(
    `/auth/gemini/status?username=${this.username}`
  );
  this.oauthConnected = connected;
  this.quotaProject = quota_project_id;
}
```

## Quota Sources

| Source | Description | When Used |
|--------|-------------|-----------|
| `oauth` | User's personal GCP quota | User has connected OAuth + valid credentials |
| `api_key` | Shared AI Loom API key | Anonymous user OR OAuth not connected OR OAuth invalid |
| `unknown` | Error state | Should not occur in normal operation |

## Environment Setup

### Backend .env

```bash
GEMINI_API_KEY=your_fallback_api_key_here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
```

### Frontend .env (for future OAuth UI)

```bash
VITE_GOOGLE_CLIENT_ID=your_oauth_client_id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_SECRET=your_oauth_client_secret
VITE_OAUTH_REDIRECT_URI=https://app.ailoom.me/auth/callback
```

## Troubleshooting

### "Quota source is api_key for authenticated user"

**Cause**: User doesn't have OAuth connected or credentials are invalid

**Solution**: 
1. Check if user has `gemini_oauth` field in MongoDB
2. Verify OAuth tokens haven't expired beyond refresh capability
3. User needs to reconnect OAuth in frontend

### "Invalid OAuth credentials"

**Cause**: Credentials expired and refresh_token is invalid

**Solution**: User must reconnect OAuth (automatic fallback to API key occurs)

### "Quota project access denied"

**Cause**: User doesn't have `serviceusage.services.use` permission on quota_project_id

**Solution**: 
1. User needs to grant permission in GCP Console
2. Or select different project with permission
3. Automatic fallback to API key occurs

### Token refresh failures

**Cause**: Refresh token expired or revoked

**Solution**: 
1. Automatic fallback to API key
2. User should reconnect OAuth for personal quota

## Monitoring

Check logs for quota attribution:

```bash
# Successful OAuth usage
INFO - Generating course using quota_source=oauth, user=alice

# Fallback to API key
INFO - Generating course using quota_source=api_key, user=anonymous

# Token refresh
INFO - Refreshed expired OAuth token for user: alice
```

## Security Notes

- ✅ OAuth credentials stored in MongoDB (encrypted connection)
- ✅ Automatic fallback prevents service disruption
- ✅ Tokens refreshed automatically when expired
- ⚠️ Consider encrypting refresh_token at rest (future)
- ⚠️ Frontend must validate quota_project_id access before storing
