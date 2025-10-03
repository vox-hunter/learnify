# Google OAuth Setup Instructions

## Overview
Google OAuth has been fully implemented for both frontend and backend. This allows users to sign in using their Google account.

## Production URLs
- **Custom Domain:** https://app.ailoom.me
- **Frontend (Render):** https://alpha-ai-loom-frontend.onrender.com
- **Backend (Render):** https://ai-loom-backend.onrender.com OR https://ai-loom-backend-f5do.onrender.com

## Google Cloud Console Setup

### 1. Create OAuth 2.0 Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click **Create Credentials** > **OAuth 2.0 Client ID**
4. Select **Web application** as application type

### 2. Configure Authorized Redirect URIs
Add ALL of the following redirect URIs:

```
https://app.ailoom.me/auth/google/callback
https://alpha-ai-loom-frontend.onrender.com/auth/google/callback
http://localhost:3000/auth/google/callback
```

### 3. Configure Authorized JavaScript Origins
Add the following origins:

```
https://app.ailoom.me
https://alpha-ai-loom-frontend.onrender.com
http://localhost:3000
```

### 4. Get Credentials
After creating, you'll receive:
- **Client ID** (e.g., `xxxxx.apps.googleusercontent.com`)
- **Client Secret** (keep this confidential!)

## Backend Environment Variables

### Local Development (`api/.env`)
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
MONGODB_URI=your-mongodb-uri
GEMINI_API_KEY=your-gemini-key
```

### Render Backend Deployment
Add the following environment variables in Render dashboard:

1. Go to your backend web service
2. Navigate to **Environment** tab
3. Add:
   - `GOOGLE_CLIENT_ID` = your-client-id.apps.googleusercontent.com
   - `GOOGLE_CLIENT_SECRET` = your-client-secret

## Frontend Configuration

No additional environment variables needed! The frontend automatically:
- Determines the correct redirect URI based on `window.location.origin`
- Uses the existing `VITE_API_URL` to communicate with backend

## How It Works

### Authentication Flow
1. **User clicks "Continue with Google"** on login/register page
2. **Frontend generates CSRF state token** and stores in localStorage
3. **Frontend calls backend** `/auth/google/url` endpoint with redirect_uri
4. **Backend validates redirect_uri** (must be in ALLOWED_REDIRECT_URIS)
5. **Backend returns Google OAuth URL** with state parameter
6. **Frontend redirects to Google** for authentication
7. **User authorizes app on Google**
8. **Google redirects back** to `/auth/google/callback` with authorization code
9. **Frontend extracts code and state** from URL
10. **Frontend verifies state** matches stored value (CSRF protection)
11. **Frontend sends code to backend** `/auth/google/callback` endpoint
12. **Backend exchanges code for access token** using CLIENT_SECRET
13. **Backend fetches user info** from Google
14. **Backend creates/finds user** using `create_google_user()` method
15. **Backend returns user data** to frontend
16. **Frontend updates auth store** and redirects to home

### Security Features
- **CSRF Protection:** Random state parameter generated and verified
- **Secure Token Exchange:** Authorization code exchanged server-side with CLIENT_SECRET
- **Redirect URI Validation:** Only whitelisted URIs allowed
- **Session Storage:** User data stored in localStorage/sessionStorage based on "remember me"

## Files Modified

### Backend
- ✅ `backend/google_oauth_fastapi.py` (NEW) - OAuth helper functions
- ✅ `api/main.py` - Added 3 OAuth endpoints
- ✅ `backend/mongo_auth.py` - Already had `create_google_user()` method

### Frontend
- ✅ `src/components/GoogleLoginButton.vue` (NEW) - Login button component
- ✅ `src/views/GoogleCallbackView.vue` (NEW) - Callback handler
- ✅ `src/views/LoginView.vue` - Integrated Google login button
- ✅ `src/router/index.js` - Added `/auth/google/callback` route

## Testing

### Cannot Test Locally
OAuth requires HTTPS in production. Testing locally is not recommended because:
- Google requires exact redirect URI match
- Mixing localhost with production creates configuration complexity

### Production Testing Steps
1. **Deploy to Render** with environment variables set
2. **Verify configuration** by visiting: `https://ai-loom-backend.onrender.com/auth/google/status`
   - Should return: `{"configured": true}`
3. **Test OAuth flow:**
   - Go to https://app.ailoom.me/login
   - Click "Continue with Google"
   - Authorize with your Google account
   - Should redirect back and create/login user

### Debugging
Check browser console and network tab for:
- State token generation and storage
- API calls to `/auth/google/url` and `/auth/google/callback`
- Redirect URL construction
- Error messages from backend

Check backend logs for:
- OAuth URL generation
- Code exchange with Google
- User creation/login
- Any validation errors

## Common Issues

### "redirect_uri_mismatch" Error
- **Cause:** Redirect URI not configured in Google Cloud Console
- **Fix:** Add exact URI to authorized redirect URIs

### "invalid_client" Error
- **Cause:** CLIENT_ID or CLIENT_SECRET incorrect
- **Fix:** Verify environment variables match Google Cloud Console

### "Invalid state parameter" Error
- **Cause:** State token mismatch (possible CSRF)
- **Fix:** Clear localStorage and try again. Check for browser extensions blocking cookies.

### Backend Returns "OAuth not configured"
- **Cause:** Environment variables not set
- **Fix:** Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to Render

### User Created but Login Fails
- **Cause:** Auth store not updated or session not saved
- **Fix:** Check frontend callback handler is storing username in localStorage

## Next Steps After Deployment

1. ✅ Set environment variables in Render
2. ✅ Configure Google Cloud Console redirect URIs
3. ✅ Deploy frontend and backend
4. ✅ Test OAuth flow end-to-end
5. 🔄 Monitor user signups via Google OAuth
6. 🔄 Consider adding Google Analytics event tracking
7. 🔄 Add email verification requirement (if needed)

## Support

If OAuth isn't working:
1. Check `/auth/google/status` endpoint returns `configured: true`
2. Verify all redirect URIs match exactly (including http/https)
3. Check browser console for JavaScript errors
4. Review backend logs in Render dashboard
5. Ensure CORS is configured for your frontend domain
