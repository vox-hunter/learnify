# Google OAuth Setup Guide for Learnify

This guide explains how to configure Google OAuth authentication for the Learnify application.

## Overview

Learnify now supports Google OAuth as an optional authentication method alongside the existing email/password system. Users can:

- Sign up using their Google account
- Log in with Google OAuth
- Link their existing account to Google
- Maintain all existing functionality with Google-authenticated accounts

## Prerequisites

1. A Google Cloud Console account
2. Access to your Learnify deployment configuration
3. Admin access to update the `secrets.toml` file

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID for reference

## Step 2: Enable Required APIs

1. In the Google Cloud Console, navigate to "APIs & Services" → "Library"
2. Search for and enable the following APIs:
   - **Google+ API** (for basic profile information)
   - **Google Identity Services API** (for OAuth)

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace domain)
3. Fill in the required information:
   - **App name**: Learnify
   - **User support email**: Your support email
   - **App logo**: Upload the Learnify logo if desired
   - **App domain**: Your deployment domain (e.g., `https://yourdomain.com`)
   - **Developer contact information**: Your email

4. Add the following scopes:
   - `openid`
   - `email`
   - `profile`

5. Add test users (in development mode) or publish the app (for production)

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Configure the settings:

   **Name**: Learnify OAuth Client

   **Authorized JavaScript origins**:
   - `https://learnify-pr-17.onrender.com` (for current deployment)

   **Authorized redirect URIs**:
   - `https://learnify-pr-17.onrender.com` (for current deployment)
   
   **Note**: Remove any `urn:ietf:wg:oauth:2.0:oob` entries as they are not needed for web applications.

5. Click "Create"
6. **Important**: Copy the Client ID and Client Secret immediately

## Step 5: Configure Learnify

### Update secrets.toml

Replace the placeholder values in your `secrets.toml` files:

**File**: `.streamlit/secrets.toml` and `Quiz_app/.streamlit/secrets.toml`

```toml
# Google OAuth Configuration
GOOGLE_CLIENT_ID = "your-actual-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-actual-client-secret"
```

### Example Configuration

```toml
# Complete secrets.toml example
GEMINI_API_KEY = "your-gemini-api-key"
MONGODB_URI = "your-mongodb-connection-string"
COOKIE_ENCRYPTION_KEY = "your-cookie-encryption-key"
RESEND_API_KEY = "your-resend-api-key"

# Google OAuth Configuration
GOOGLE_CLIENT_ID = "123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnopqrstuvwxyz123456"
```

## Step 6: Deployment Configuration

### For Local Development

No additional configuration needed. The OAuth will work with `localhost:8501`.

### For Production Deployment

1. **Update redirect URIs** in Google Cloud Console to match your production domain
2. **Use HTTPS** - Google OAuth requires secure connections in production
3. **Domain verification** - Verify your domain in Google Cloud Console if required

### For Streamlit Cloud

1. Add your Streamlit Cloud URL as an authorized origin and redirect URI:
   - `https://your-app-name.streamlit.app`

2. Ensure your secrets are properly configured in Streamlit Cloud's secrets management

## Step 7: Test the Integration

1. Start your Learnify application
2. Navigate to the Login page
3. You should see "Login with Google" and "Sign up with Google" buttons
4. Test the OAuth flow:
   - Click the Google button
   - You will be redirected to Google for authentication
   - Authorize the application
   - You will be automatically redirected back to Learnify
   - Verify successful authentication

## User Experience

### For New Users

1. Click "Sign up with Google"
2. Authenticate with Google
3. Complete account setup (choose username, agree to terms)
4. Start using Learnify with Google authentication

### For Existing Users

1. Log in normally
2. Go to Account settings
3. Click "Link Google Account"
4. Authenticate with Google
5. Account is now linked - can use either method to log in

## Data Consistency

The Google OAuth integration maintains the same data structure as manual accounts:

- **Username**: User-chosen (can be modified after Google signup)
- **Email**: From Google account
- **Name**: From Google account (can be modified)
- **Email verification**: Automatically verified for Google accounts
- **Password**: None initially (users can set one if desired)
- **Google linking**: Tracked in database

## Security Features

- **State parameter validation** prevents CSRF attacks
- **Email verification** is automatic for Google accounts  
- **Account linking** prevents duplicate accounts with same email
- **Secure token handling** using Google's official libraries
- **Cookie management** maintains session consistency

## Troubleshooting

### Common Issues

1. **"OAuth not configured" message**
   - Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly
   - Ensure they don't contain placeholder values

2. **"Invalid redirect URI" error**
   - Verify redirect URIs in Google Cloud Console match your domain exactly
   - For development: Use `http://localhost:8501` 
   - For production: Use your actual HTTPS domain
   - Remove any `urn:ietf:wg:oauth:2.0:oob` entries (not needed for web apps)
   - Check for typos in URLs
   - Ensure protocol (http/https) matches

3. **"Access blocked" error**
   - Check OAuth consent screen configuration
   - Ensure required scopes are added
   - Verify app publication status

4. **"Invalid client" error**
   - Verify Client ID and Secret are correct
   - Check that APIs are enabled
   - Ensure credentials are for "Web application" type

### Development vs Production

- **Development**: Use `http://localhost:8501`
- **Production**: Must use HTTPS and verified domain
- **Testing**: Add test users in OAuth consent screen during development

## Support

For additional help:

1. Check Google's [OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
2. Review the [Streamlit deployment guide](https://docs.streamlit.io/streamlit-community-cloud)
3. Contact the Learnify development team

## Security Notes

- Never commit client secrets to version control
- Use environment variables or secure secret management
- Regularly rotate OAuth credentials
- Monitor OAuth usage in Google Cloud Console
- Keep redirect URIs minimal and specific