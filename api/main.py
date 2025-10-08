"""
FastAPI Main Application
This is the entry point for the FastAPI backend that replaces the Streamlit backend.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import backend modules
from local_backend import generate_course, validate_short_answer_with_ai
from mongo_auth import MongoAuthManager
from mongo_course_manager import MongoCourseManager, get_session_id
from file_security import validate_file_security
from chat_manager import ChatSessionManager
from google_oauth_fastapi import (
    get_google_auth_url,
    exchange_code_for_token,
    get_user_info,
    validate_google_oauth_user,
    verify_oauth_config
)

# Create FastAPI app
app = FastAPI(
    title="AI Loom API",
    description="AI-powered course and quiz generation API",
    version="1.0.0"
)

# Configure CORS
# Allow configuring CORS origins from an environment variable for deployed environments.
# Set ALLOWED_ORIGINS as a comma-separated list (example: https://alpha-ai-loom-frontend.onrender.com,https://app.ailoom.me)
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if _allowed_origins_env:
    # support '*' as a special value to allow all origins
    if _allowed_origins_env.strip() == "*":
        _allowed_origins = ["*"]
    else:
        _allowed_origins = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]
else:
    _allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:5173",
        "https://ailoom-alpha.pages.dev",
        "https://app.ailoom.me",
        "https://alpha-ai-loom-frontend.onrender.com",
        "https://ai-loom-frontend.onrender.com",
        "https://ailoom.me",
    ]

print(f"CORS allowed origins: {_allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
auth_manager = None
course_manager = None
# Note: chat_manager is NOT initialized globally - created per-request with user credentials

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global auth_manager, course_manager
    try:
        auth_manager = MongoAuthManager()
        course_manager = MongoCourseManager()
        # chat_manager is created per-request with user OAuth credentials
    except Exception as e:
        print(f"Warning: Could not initialize managers: {e}")

# Pydantic models for request/response
class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    name: str
    marketing_consent: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class CourseGenerationRequest(BaseModel):
    file_url: Optional[str] = None

class ValidateAnswerRequest(BaseModel):
    question: str
    user_answer: str
    expected_answer: str

class SaveCourseRequest(BaseModel):
    course_data: List[Dict[str, Any]]
    course_title: str
    is_public: bool = True

class UpdateProgressRequest(BaseModel):
    answered_questions: List[str]  # List of question keys like "0-main-0"
    score: int
    current_section_index: int
    answer_data: Optional[dict] = {}  # Dictionary mapping question keys to answer data

class SendVerificationRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class GoogleOAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: str
    state: str

class GoogleAuthUrlRequest(BaseModel):
    redirect_uri: str
    state: str

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Loom API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "auth_available": auth_manager is not None,
        "course_manager_available": course_manager is not None
    }

# Authentication endpoints
@app.post("/auth/register")
async def register(user: UserRegister):
    """Register a new user"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    user_id, error = auth_manager.add_user(
        username=user.username,
        password=user.password,
        email=user.email,
        name=user.name,
        marketing_consent=user.marketing_consent
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user_id": str(user_id)
    }

@app.post("/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    user = auth_manager.find_user_by_username(credentials.username)
    if not user or not auth_manager.verify_password(credentials.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Check if user is admin (specific email)
    is_admin = user.get("email") == "vidyutsanthosh4@gmail.com"
    
    # Check Google account status
    is_google_user = bool(user.get("google_id"))
    has_password = bool(user.get("password"))
    
    return {
        "success": True,
        "username": user["username"],
        "name": user.get("name"),
        "email": user.get("email"),
        "picture": user.get("picture"),
        "isAdmin": is_admin,
        "isGoogleUser": is_google_user,
        "hasPassword": has_password
    }

# Email verification endpoints
@app.post("/auth/send-verification")
async def send_verification(request: SendVerificationRequest):
    """Send verification code to email"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Import email_verification module
    try:
        from email_verification import send_verification_email, generate_verification_code
    except Exception as e:
        print(f"Error importing email_verification: {e}")
        raise HTTPException(status_code=500, detail=f"Email service initialization failed: {str(e)}")
    
    # Generate code
    code = generate_verification_code()
    
    # Store code in database
    success, error = auth_manager.store_verification_code(
        email=request.email,
        code=code,
        purpose="registration"
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "Failed to store verification code")
    
    # Send email
    try:
        email_sent, email_message = send_verification_email(
            email=request.email,
            code=code,
            purpose="registration"
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    if not email_sent:
        raise HTTPException(status_code=500, detail=email_message)
    
    return {
        "success": True,
        "message": "Verification code sent to your email"
    }

@app.post("/auth/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """Verify email with code"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Verify code
    success, error = auth_manager.verify_code(
        email=request.email,
        entered_code=request.code,
        purpose="registration"
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Invalid verification code")
    
    # Mark email as verified
    marked, mark_error = auth_manager.mark_email_verified(request.email)
    if not marked:
        # Code was valid but marking failed - still return success
        # since the code was consumed
        pass
    
    return {
        "success": True,
        "message": "Email verified successfully"
    }

# Forgot password endpoints
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

@app.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset code to email"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Check if user exists with this email
    user = auth_manager.find_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not for security
        # Return success anyway to prevent email enumeration
        return {
            "success": True,
            "message": "If an account exists with this email, a reset code has been sent"
        }
    
    # Import email_verification module
    try:
        from email_verification import send_verification_email, generate_verification_code
    except Exception as e:
        print(f"Error importing email_verification: {e}")
        raise HTTPException(status_code=500, detail=f"Email service initialization failed: {str(e)}")
    
    # Generate code
    code = generate_verification_code()
    
    # Store code in database with password_reset purpose
    success, error = auth_manager.store_verification_code(
        email=request.email,
        code=code,
        purpose="password_reset"
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "Failed to store verification code")
    
    # Send email with password_reset purpose
    try:
        email_sent, email_message = send_verification_email(
            email=request.email,
            code=code,
            purpose="password_reset"
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    if not email_sent:
        raise HTTPException(status_code=500, detail=email_message)
    
    return {
        "success": True,
        "message": "If an account exists with this email, a reset code has been sent"
    }

@app.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with verification code"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Verify code
    success, error = auth_manager.verify_code(
        email=request.email,
        entered_code=request.code,
        purpose="password_reset"
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Invalid or expired verification code")
    
    # Find user by email
    user = auth_manager.find_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password using the auth manager method
    success, error = auth_manager.update_user_password_by_email(
        email=request.email,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "Failed to update password")
    
    # Delete the used verification code
    try:
        auth_manager.verification_codes.delete_many({
            "email": request.email,
            "purpose": "password_reset"
        })
    except Exception as e:
        # Log but don't fail if code cleanup fails
        print(f"Warning: Failed to delete verification code: {e}")
    
    return {
        "success": True,
        "message": "Password has been reset successfully"
    }

# Google OAuth endpoints
from fastapi import Request

@app.post("/auth/google/url")
@app.options("/auth/google/url")
async def get_oauth_url(request: Optional[GoogleAuthUrlRequest] = None, fastapi_request: Request = None):
    """Get Google OAuth authorization URL"""
    # Handle OPTIONS preflight
    if request is None:
        origin = fastapi_request.headers.get("origin") if fastapi_request else None
        allowed_origin = origin if origin in _allowed_origins or "*" in _allowed_origins else None
        return JSONResponse(
            content={"message": "OK"},
            headers={
                "Access-Control-Allow-Origin": allowed_origin or "null",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    if not verify_oauth_config():
        raise HTTPException(
            status_code=503, 
            detail="Google OAuth is not configured. Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to environment variables."
        )
    
    try:
        auth_url = get_google_auth_url(
            redirect_uri=request.redirect_uri,
            state=request.state
        )
        
        if not auth_url:
            raise HTTPException(status_code=500, detail="Failed to generate OAuth URL")
        
        return {
            "success": True,
            "auth_url": auth_url
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating OAuth URL: {str(e)}")


@app.post("/auth/google/callback")
@app.options("/auth/google/callback")
async def google_oauth_callback(request: Optional[GoogleOAuthCallbackRequest] = None, fastapi_request: Request = None):
    """Handle Google OAuth callback and create/login user"""
    # Handle OPTIONS preflight
    if request is None:
        origin = fastapi_request.headers.get("origin") if fastapi_request else None
        allowed_origin = origin if origin in _allowed_origins or "*" in _allowed_origins else None
        return JSONResponse(
            content={"message": "OK"},
            headers={
                "Access-Control-Allow-Origin": allowed_origin or "null",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    if not verify_oauth_config():
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    try:
        # Exchange code for token
        token_response = exchange_code_for_token(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        
        if not token_response or "access_token" not in token_response:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
        
        # Get user info from Google
        user_info = get_user_info(token_response["access_token"])
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user information from Google")
        
        # Validate and extract user data
        validated_user = validate_google_oauth_user(user_info)
        
        # Check if user exists by email
        existing_user = auth_manager.find_user_by_email(validated_user["email"])
        
        if existing_user:
            # Existing user - check if they need to link Google account
            google_id = existing_user.get("google_id")
            has_password = bool(existing_user.get("password"))
            
            # Link Google account if not already linked
            if not google_id:
                try:
                    auth_manager.users.update_one(
                        {"email": validated_user["email"]},
                        {"$set": {
                            "google_id": validated_user.get("google_id"),
                            "picture": validated_user.get("picture")
                        }}
                    )
                    google_id = validated_user.get("google_id")
                except Exception as e:
                    print(f"Warning: Failed to link Google account: {e}")
            
            # Update profile picture if available
            if validated_user.get("picture") and not existing_user.get("picture"):
                try:
                    auth_manager.users.update_one(
                        {"email": validated_user["email"]},
                        {"$set": {"picture": validated_user["picture"]}}
                    )
                except Exception as e:
                    print(f"Warning: Failed to update profile picture: {e}")
            
            # Check if user is admin
            is_admin = existing_user.get("email") == "vidyutsanthosh4@gmail.com"
            
            return {
                "success": True,
                "username": existing_user["username"],
                "name": existing_user.get("name", validated_user["name"]),
                "email": existing_user["email"],
                "picture": existing_user.get("picture", validated_user.get("picture")),
                "isAdmin": is_admin,
                "is_new_user": False,
                "isGoogleUser": bool(google_id),
                "hasPassword": has_password
            }
        else:
            # New user - return user info for username selection
            return {
                "success": True,
                "needs_username": True,
                "user_info": {
                    "email": validated_user["email"],
                    "name": validated_user["name"],
                    "google_id": validated_user.get("google_id"),
                    "picture": validated_user.get("picture")
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in Google OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth authentication failed: {str(e)}")


@app.get("/auth/google/status")
@app.options("/auth/google/status")
async def google_oauth_status(fastapi_request: Request = None):
    """Check if Google OAuth is configured"""
    try:
        configured = verify_oauth_config()
        origin = fastapi_request.headers.get("origin") if fastapi_request else None
        allowed_origin = origin if origin in _allowed_origins or "*" in _allowed_origins else None
        return JSONResponse(
            content={
                "configured": configured,
                "message": "Google OAuth is ready" if configured else "Google OAuth not configured"
            },
            headers={
                "Access-Control-Allow-Origin": allowed_origin or "null",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        origin = fastapi_request.headers.get("origin") if fastapi_request else None
        allowed_origin = origin if origin in _allowed_origins or "*" in _allowed_origins else None
        return JSONResponse(
            content={"configured": False, "message": f"Error checking OAuth config: {str(e)}"},
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": allowed_origin or "null",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )


@app.get("/auth/check-username")
async def check_username(username: str):
    """Check if username is available"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    if len(username) < 3:
        return {"available": False, "message": "Username must be at least 3 characters"}
    
    existing_user = auth_manager.find_user_by_username(username)
    return {"available": existing_user is None}


class GoogleCompleteRequest(BaseModel):
    code: str
    redirect_uri: str
    state: str
    username: str

class RateCourseRequest(BaseModel):
    rating: int

class CloneCourseRequest(BaseModel):
    course_id: str

@app.post("/auth/google/complete")
async def complete_google_signup(request: GoogleCompleteRequest):
    """Complete Google OAuth signup with chosen username"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    if not verify_oauth_config():
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    try:
        # Exchange code for token
        token_response = exchange_code_for_token(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        
        if not token_response or "access_token" not in token_response:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
        
        # Get user info from Google
        user_info = get_user_info(token_response["access_token"])
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user information from Google")
        
        # Validate and extract user data
        validated_user = validate_google_oauth_user(user_info)
        
        # Check if username is available
        existing_user = auth_manager.find_user_by_username(request.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username is already taken")
        
        # Check if user already exists by email (shouldn't happen, but safety check)
        existing_email = auth_manager.find_user_by_email(validated_user["email"])
        if existing_email:
            raise HTTPException(status_code=400, detail="An account with this email already exists")
        
        # Prepare Google user info for create_google_user method
        google_user_info = {
            "email": validated_user["email"],
            "name": validated_user["name"],
            "google_id": validated_user.get("google_id"),
            "picture": validated_user.get("picture")
        }
        
        # Create user with chosen username
        user_id, error, final_username = auth_manager.create_google_user(
            google_user_info=google_user_info,
            base_username=request.username,
            marketing_consent=False
        )
        
        if error:
            raise HTTPException(status_code=500, detail=f"Failed to create user: {error}")
        
        # Check if user is admin
        is_admin = validated_user["email"] == "vidyutsanthosh4@gmail.com"
        
        return {
            "success": True,
            "username": final_username,
            "name": validated_user["name"],
            "email": validated_user["email"],
            "picture": validated_user.get("picture"),
            "isAdmin": is_admin,
            "is_new_user": True,
            "isGoogleUser": True,
            "hasPassword": False
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing Google signup: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


# Account management endpoints
class UpdateProfileRequest(BaseModel):
    username: str
    name: str
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    username: str
    current_password: str
    new_password: str

class DeleteAccountRequest(BaseModel):
    username: str

@app.put("/account/profile")
async def update_profile(request: UpdateProfileRequest):
    """Update user profile information"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Verify username exists
    user = auth_manager.find_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare updates
    updates = {"name": request.name}
    
    # Only allow email change if user is not a Google user
    if user.get("google_id"):
        # Google user - don't allow email change
        if request.email != user.get("email"):
            raise HTTPException(
                status_code=400, 
                detail="Cannot change email for Google accounts. Please unlink your Google account first if you have a password."
            )
    else:
        # Traditional user - allow email change
        updates["email"] = request.email
    
    # Update user details
    success, error = auth_manager.update_user_details(
        username=request.username,
        updates=updates
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Failed to update profile")
    
    return {
        "success": True,
        "message": "Profile updated successfully"
    }

@app.put("/account/password")
async def change_password(request: ChangePasswordRequest):
    """Change user password"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Verify current password
    user = auth_manager.find_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not auth_manager.verify_password(request.current_password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Update password
    success, error = auth_manager.update_user_password(
        username=request.username,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Failed to change password")
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }

class UnlinkGoogleRequest(BaseModel):
    username: str

@app.post("/account/unlink-google")
async def unlink_google_account(request: UnlinkGoogleRequest):
    """Unlink Google account from user"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Find user
    user = auth_manager.find_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has a password (can't unlink if it's the only auth method)
    if not user.get("password"):
        raise HTTPException(
            status_code=400, 
            detail="Cannot unlink Google account. This is your only login method. Please set a password first."
        )
    
    # Remove Google ID and picture
    try:
        auth_manager.users.update_one(
            {"username": request.username},
            {"$unset": {"google_id": "", "picture": ""}}
        )
        
        return {
            "success": True,
            "message": "Google account unlinked successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlink Google account: {str(e)}")

@app.delete("/account")
async def delete_account(request: DeleteAccountRequest):
    """Delete user account"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    # Delete account (passes username twice for confirmation)
    success, error = auth_manager.delete_user_account(
        username=request.username,
        confirm_username=request.username
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error or "Failed to delete account")
    
    return {
        "success": True,
        "message": "Account deleted successfully"
    }

# Course generation endpoints
@app.post("/course/generate/upload")
async def generate_course_from_upload(
    file: UploadFile = File(...),
    username: Optional[str] = None
):
    """Generate a course from an uploaded file"""
    # Validate file
    file_size = 0
    file_content = bytearray()
    
    # Read file in chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        file_content.extend(chunk)
    
    file_bytes = bytes(file_content)
    
    # Validate file security
    is_safe, error_message = validate_file_security(file.filename, file_size)
    if not is_safe:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Retrieve user's Gemini OAuth credentials if authenticated
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
            logger.info(f"Retrieved Gemini OAuth credentials for user: {username}")
    
    # Generate course with user credentials
    course_data, error = generate_course(
        file_content=file_bytes,
        filename=file.filename,
        user_credentials=user_credentials,
        username=username,
        quota_project_id=quota_project_id
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # Convert course_data to dict if it's a Pydantic model
    if hasattr(course_data, 'model_dump'):
        course_dict = course_data.model_dump()
    elif hasattr(course_data, 'dict'):
        course_dict = course_data.dict()
    else:
        course_dict = course_data
    
    return {
        "success": True,
        "course_data": course_dict
    }

@app.post("/course/generate/url")
async def generate_course_from_url(
    request: CourseGenerationRequest,
    username: Optional[str] = None
):
    """Generate a course from a URL"""
    if not request.file_url:
        raise HTTPException(status_code=400, detail="file_url is required")
    
    # Retrieve user's Gemini OAuth credentials if authenticated
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
            logger.info(f"Retrieved Gemini OAuth credentials for user: {username}")
    
    # Generate course with user credentials
    course_data, error = generate_course(
        file_url=request.file_url,
        user_credentials=user_credentials,
        username=username,
        quota_project_id=quota_project_id
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # Convert course_data to dict if it's a Pydantic model
    if hasattr(course_data, 'model_dump'):
        course_dict = course_data.model_dump()
    elif hasattr(course_data, 'dict'):
        course_dict = course_data.dict()
    else:
        course_dict = course_data
    
    return {
        "success": True,
        "course_data": course_dict
    }

# Quiz validation endpoints
@app.post("/quiz/validate-answer")
async def validate_answer(
    request: ValidateAnswerRequest,
    username: Optional[str] = None
):
    """Validate a short answer using AI"""
    # Retrieve user's Gemini OAuth credentials if authenticated
    user_credentials = None
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
            logger.info(f"Retrieved Gemini OAuth credentials for user: {username}")
    
    is_correct, explanation = validate_short_answer_with_ai(
        question=request.question,
        user_answer=request.user_answer,
        expected_answer=request.expected_answer,
        user_credentials=user_credentials,
        username=username
    )
    
    if is_correct is None:
        raise HTTPException(status_code=500, detail=explanation)
    
    return {
        "is_correct": is_correct,
        "explanation": explanation
    }

# Course management endpoints
@app.post("/course/save")
async def save_course(request: SaveCourseRequest, username: Optional[str] = None):
    """Save a course to the database"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    is_guest = username is None
    # Only generate session_id for guest users
    session_id = get_session_id() if is_guest else None
    
    course_id, error = course_manager.save_course(
        course_data=request.course_data,
        course_title=request.course_title,
        creator=username or session_id,
        is_guest=is_guest,
        session_id=session_id if is_guest else None,
        is_public=request.is_public
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {
        "success": True,
        "course_id": course_id
    }

@app.get("/course/{course_id}")
async def get_course(course_id: str):
    """Get a course by ID"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    course, error = course_manager.get_course(course_id)
    if error:
        raise HTTPException(status_code=500, detail=error)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Convert ObjectId to string
    if '_id' in course:
        course['_id'] = str(course['_id'])
    if 'course_id' in course:
        course['course_id'] = str(course['course_id'])
    
    return course

@app.get("/courses")
async def list_courses(username: Optional[str] = None):
    """List all courses for a user"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    if username:
        courses, error = course_manager.get_user_courses(username, is_guest=False)
    else:
        session_id = get_session_id()
        courses, error = course_manager.get_user_courses(session_id, is_guest=True, session_id=session_id)
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # Ensure courses is a list and convert ObjectId to string
    if courses is None:
        courses = []
    
    for course in courses:
        if '_id' in course:
            course['_id'] = str(course['_id'])
        if 'course_id' in course:
            course['course_id'] = str(course['course_id'])
    
    return {"courses": courses}

@app.post("/course/{course_id}/progress")
async def update_progress(course_id: str, request: UpdateProgressRequest, username: Optional[str] = None):
    """Update user progress on a course"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    user_identifier = username or get_session_id()
    is_guest = username is None
    
    # Build progress data structure from request
    progress_data = {
        "answered_questions": request.answered_questions,
        "score": request.score,
        "current_section_index": request.current_section_index,
        "answer_data": request.answer_data or {}
    }
    
    success, error = course_manager.save_progress(
        course_id=course_id,
        user_identifier=user_identifier,
        progress_data=progress_data,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {"success": success}

@app.get("/course/{course_id}/progress")
async def get_progress(course_id: str, username: Optional[str] = None):
    """Get user progress on a course"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    user_identifier = username or get_session_id()
    is_guest = username is None
    
    progress, error = course_manager.get_progress(
        course_id=course_id,
        user_identifier=user_identifier,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return progress or {"answered_questions": [], "score": 0, "current_section_index": 0, "answer_data": {}}


# Public Course Library endpoints
@app.get("/library/courses")
async def get_public_courses(
    page: int = 0,
    limit: int = 20,
    sort_by: str = 'created_at',
    sort_order: int = -1
):
    """Get paginated list of public courses"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    courses, error = course_manager.get_public_courses(page, limit, sort_by, sort_order)
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {"courses": courses or []}


@app.get("/library/search")
async def search_public_courses(
    q: str,
    page: int = 0,
    limit: int = 20
):
    """Search public courses by text query"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    courses, error = course_manager.search_public_courses(q, page, limit)
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {"courses": courses or []}


@app.get("/library/subject/{subject}")
async def get_courses_by_subject(
    subject: str,
    page: int = 0,
    limit: int = 20
):
    """Get public courses by subject/tag"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    courses, error = course_manager.get_courses_by_subject(subject, page, limit)
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {"courses": courses or []}


@app.post("/library/course/{course_id}/rate")
async def rate_course(course_id: str, request: RateCourseRequest, username: Optional[str] = None):
    """Rate a public course (1-5 stars)"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    # Use session ID for guests, username for authenticated users
    user_identifier = username or get_session_id()
    
    success, error = course_manager.rate_course(course_id, user_identifier, request.rating)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {"success": success}


@app.post("/library/course/{course_id}/clone")
async def clone_course(course_id: str, username: Optional[str] = None):
    """Clone a public course to user's account"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    is_guest = username is None
    user_identifier = username or get_session_id()
    session_id = get_session_id() if is_guest else None
    
    new_course_id, error = course_manager.clone_course(
        course_id=course_id,
        new_creator=user_identifier,
        is_guest=is_guest,
        session_id=session_id
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "success": True,
        "course_id": new_course_id,
        "message": "Course cloned successfully"
    }


# Delete a course
@app.delete("/course/{course_id}")
async def delete_course(course_id: str, username: Optional[str] = None):
    """Delete a course owned by the user
    For authenticated users, `username` parameter should be provided (axios interceptor attaches it).
    Guest deletions are handled client-side (localStorage) and won't call this endpoint.
    """
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")

    user_identifier = username or get_session_id()
    is_guest = username is None

    success, error = course_manager.delete_course(course_id=course_id, user_identifier=user_identifier, is_guest=is_guest)

    if error:
        # If deletion failed due to permissions or not found, return 400
        raise HTTPException(status_code=400, detail=error)

    return {"success": success}

# Chat endpoints
@app.post("/chat/message")
async def chat_message(
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    username: Optional[str] = Form(None)
):
    """
    Send a message to the AI chat with optional file or URL context.
    Uses Gemini SDK's multi-turn chat API for conversation management.
    
    Args:
        message: User's text message
        session_id: Optional existing session ID to continue conversation
        file: Optional file upload for context
        url: Optional URL for AI to fetch and analyze
        username: Optional username for OAuth credentials
        
    Returns:
        {
            "success": bool,
            "reply": str,
            "session_id": str,
            "error": Optional[str]
        }
    """
    try:
        # --- Access control rules ---
        # If user is not logged in (guest), do not forward to AI. Return a polite assistant-style reply.
        GUEST_FAKE_REPLY = "You need to be logged in to use AI features, if you want to try AI Generated course, checkout \"library\" for community generated courses."

        # Counters for logged-in users without Gemini OAuth (in-memory)
        # username -> count
        # Use a module-level dict to track non-OAuth usage; initialize if missing
        if '_NON_OAUTH_CHAT_USAGE' not in globals():
            _NON_OAUTH_CHAT_USAGE = {}

        # If no username provided -> guest behavior
        if not username:
            # Return a fake AI reply so frontend can render it naturally
            return {
                "success": True,
                "reply": GUEST_FAKE_REPLY,
                "session_id": "",
                "is_course": False
            }

        # Retrieve user's Gemini OAuth credentials if authenticated
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
                logger.info(f"Retrieved Gemini OAuth credentials for chat user: {username}")
            else:
                # User is logged in but does not have Gemini/Google OAuth linked.
                # Enforce 10-request free limit.
                current = globals().get('_NON_OAUTH_CHAT_USAGE', {}).get(username, 0)
                if current >= 10:
                    # Return polite assistant-style reply forcing Google login
                    return {
                        "success": True,
                        "reply": "You've reached the 10 free chat requests. Please login with Google to continue using AI features.",
                        "session_id": "",
                        "is_course": False
                    }
                # Increment usage and allow request to proceed
                # Update the module-level counter safely
                usage = globals().get('_NON_OAUTH_CHAT_USAGE', {})
                usage[username] = current + 1
                globals()['_NON_OAUTH_CHAT_USAGE'] = usage
                logger.info(f"Non-OAuth chat usage for {username}: {usage[username]}")
        
        # Create chat manager with user credentials
        chat_manager = ChatSessionManager(
            user_credentials=user_credentials,
            username=username,
            quota_project_id=quota_project_id
        )
        
        file_data = None
        file_mime_type = None
        
        # Process uploaded file if provided
        if file:
            # Read file content as bytes for Gemini API
            file_data = await file.read()
            file_mime_type = file.content_type or "application/octet-stream"
            
            logger.info(f"Processing uploaded file: {file.filename} ({file_mime_type}, {len(file_data)} bytes)")
            
            # Validate file security (reuse existing validation)
            validation_result = validate_file_security(
                file_data=file_data,
                filename=file.filename
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"File validation failed: {validation_result['error']}"
                )
        
        # Send message to chat session using Gemini SDK
        # The ChatSessionManager handles:
        # - Creating/retrieving chat sessions
        # - Sending messages with file/URL context
        # - Managing conversation history automatically via SDK
        result = chat_manager.send_message(
            session_id=session_id,
            message=message,
            file_data=file_data,
            file_mime_type=file_mime_type,
            url=url
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Chat processing failed'))
        
        # Return enhanced response with course detection
        return {
            "success": True,
            "reply": result['reply'],
            "session_id": result['session_id'],
            "is_course": result.get('is_course', False),
            "course_data": result.get('course_data')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    username: Optional[str] = None
):
    """
    Get conversation history for a chat session.
    
    Args:
        session_id: The chat session identifier
        username: Optional username for creating manager instance
        
    Returns:
        List of messages in the conversation
    """
    # Create chat manager instance (sessions are stored at class level)
    chat_manager = ChatSessionManager(username=username)
    
    history = chat_manager.get_history(session_id)
    
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "session_id": session_id,
        "history": history
    }

@app.delete("/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    username: Optional[str] = None
):
    """
    Delete a chat session and its history.
    
    Args:
        session_id: The chat session identifier
        username: Optional username for creating manager instance
        
    Returns:
        Success confirmation
    """
    # Create chat manager instance (sessions are stored at class level)
    chat_manager = ChatSessionManager(username=username)
    
    deleted = chat_manager.delete_session(session_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "message": "Session deleted successfully"
    }

# Analytics endpoints
@app.get("/analytics/courses")
async def get_course_analytics(username: Optional[str] = None):
    """Get analytics for user's courses"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    user_identifier = username or get_session_id()
    courses = course_manager.get_user_courses(user_identifier)
    
    total_courses = len(courses)
    completed_courses = sum(1 for c in courses if c.get("completed", False))
    
    return {
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "in_progress": total_courses - completed_courses
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["../api", "../backend"]  # Watch both api and backend directories
    )
