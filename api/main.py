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
import time
import uuid
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
from local_backend import validate_short_answer_with_ai, FlashcardItem
from mongo_auth import MongoAuthManager
from mongo_course_manager import MongoCourseManager, get_session_id
from mongo_flashcard_manager import MongoFlashcardManager
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
        "https://g157jfrt-3000.asse.devtunnels.ms",
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
flashcard_manager = None
# Note: chat_manager is NOT initialized globally - created per-request with user credentials

# In-memory store for pending Google signups (short-lived)
# signup_token -> { 'token_response': {...}, 'user_info': {...}, 'ts': epoch_seconds }
_PENDING_GOOGLE_SIGNUPS = {}

def _cleanup_pending_signups(max_age_seconds: int = 600):
    """Remove expired pending signups to avoid memory leaks."""
    try:
        now = time.time()
        to_delete = [k for k, v in _PENDING_GOOGLE_SIGNUPS.items() if now - v.get('ts', 0) > max_age_seconds]
        for k in to_delete:
            _PENDING_GOOGLE_SIGNUPS.pop(k, None)
    except Exception:
        pass

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global auth_manager, course_manager, flashcard_manager
    try:
        auth_manager = MongoAuthManager()
        course_manager = MongoCourseManager()
        flashcard_manager = MongoFlashcardManager()
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

class SaveFlashcardRequest(BaseModel):
    flashcard_data: List[FlashcardItem]  # Use Pydantic validation for flashcard items
    flashcard_title: str
    source_course_id: Optional[str] = None

class UpdateFlashcardProgressRequest(BaseModel):
    studied_cards: List[int]  # List of card indices that have been studied
    mastery_levels: Dict[str, int]  # Dictionary mapping card index (as string) to mastery level (0-5)
    last_studied: str  # ISO timestamp of last study session
    accuracy_rate: Optional[float] = None  # Optional accuracy rate (0.0-1.0)

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

class GenerateFlashcardsRequest(BaseModel):
    card_count: Optional[int] = 10
    difficulty: Optional[str] = None
    focus_areas: Optional[List[str]] = None

class MatchModeStatsRequest(BaseModel):
    completion_time: float  # seconds
    moves_count: int  # number of card flips
    card_count: int  # number of pairs played
    timestamp: str  # ISO timestamp

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
        "course_manager_available": course_manager is not None,
        "flashcard_manager_available": flashcard_manager is not None
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
async def get_oauth_url(fastapi_request: Request, request: Optional[GoogleAuthUrlRequest] = None):
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
async def google_oauth_callback(fastapi_request: Request, request: Optional[GoogleOAuthCallbackRequest] = None):
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
            
            print(f"[OAuth Callback] Existing user: {existing_user.get('username')}, google_id before: {google_id}")
            print(f"[OAuth Callback] Validated user google_id: {validated_user.get('google_id')}")
            
            # Link Google account if not already linked
            if not google_id:
                try:
                    # Update user details with google_id and picture
                    success, error = auth_manager.update_user_details(
                        existing_user["username"],
                        {
                            "google_id": validated_user.get("google_id"),
                            "picture": validated_user.get("picture"),
                            "google_linked": True
                        }
                    )
                    if success:
                        google_id = validated_user.get("google_id")
                        print(f"[OAuth Callback] Linked Google account, google_id after: {google_id}")
                    else:
                        print(f"Warning: Failed to link Google account: {error}")
                except Exception as e:
                    print(f"Warning: Failed to link Google account: {e}")
            
            # Update profile picture if available
            if validated_user.get("picture") and not existing_user.get("picture"):
                try:
                    auth_manager.update_user_details(
                        existing_user["username"],
                        {"picture": validated_user["picture"]}
                    )
                except Exception as e:
                    print(f"Warning: Failed to update profile picture: {e}")
            
            # Check if user is admin
            is_admin = existing_user.get("email") == "vidyutsanthosh4@gmail.com"
            
            print(f"[OAuth Callback] Returning isGoogleUser: {bool(google_id)} (google_id={google_id})")
            
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
            # New user - stash token_response temporarily and return token + user info for username selection
            try:
                signup_token = str(uuid.uuid4())
                _cleanup_pending_signups()
                _PENDING_GOOGLE_SIGNUPS[signup_token] = {
                    'token_response': token_response,
                    'user_info': {
                        'email': validated_user["email"],
                        'name': validated_user["name"],
                        'google_id': validated_user.get("google_id"),
                        'picture': validated_user.get("picture")
                    },
                    'ts': time.time()
                }
            except Exception as e:
                print(f"Warning: Failed to store pending signup: {e}")
                raise HTTPException(status_code=500, detail="Failed to initialize signup session")

            return {
                "success": True,
                "needs_username": True,
                "signup_token": signup_token,
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
async def google_oauth_status(fastapi_request: Request):
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
    # New flow: use signup_token from /auth/google/callback
    signup_token: Optional[str] = None
    # Legacy fallback: accept code/redirect_uri/state
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    state: Optional[str] = None
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
        # Prefer new flow using signup_token to avoid reusing auth code
        validated_user = None
        if request.signup_token:
            _cleanup_pending_signups()
            pending = _PENDING_GOOGLE_SIGNUPS.pop(request.signup_token, None)
            if not pending:
                raise HTTPException(status_code=400, detail="Signup session expired or invalid")
            token_response = pending.get('token_response')
            user_info = pending.get('user_info')
            if not token_response or not user_info:
                raise HTTPException(status_code=400, detail="Invalid signup session data")
            # validated_user already structured in callback
            validated_user = user_info
        else:
            # Legacy fallback: Exchange code for token (may fail if code already used)
            if not request.code or not request.redirect_uri:
                raise HTTPException(status_code=400, detail="Missing authorization data")
            token_response = exchange_code_for_token(
                code=request.code,
                redirect_uri=request.redirect_uri
            )
            if not token_response or "access_token" not in token_response:
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
            user_info = get_user_info(token_response["access_token"])
            if not user_info:
                raise HTTPException(status_code=400, detail="Failed to get user information from Google")
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
        success, error = auth_manager.unlink_google_account(request.username)
        
        if not success:
            raise HTTPException(status_code=400, detail=error or "Failed to unlink Google account")
        
        return {
            "success": True,
            "message": "Google account unlinked successfully"
        }
    except HTTPException:
        raise
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

# Generate flashcards from course content
@app.post("/course/{course_id}/generate-flashcards")
async def generate_flashcards_from_course(
    course_id: str,
    request: GenerateFlashcardsRequest = GenerateFlashcardsRequest(),
    username: Optional[str] = None
):
    """Generate flashcards from course content using AI
    
    Loads the course, formats content into a prompt, and uses the chat manager
    to generate flashcards via Gemini AI. Automatically links flashcards to the
    source course via source_course_id.
    """
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    logger.info(f"Generating flashcards from course {course_id} for user {username or 'guest'}")
    
    try:
        # Load the course
        course, error = course_manager.get_course(course_id=course_id)
        
        if error or not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if course has content
        if not course.get('sections') or len(course['sections']) == 0:
            raise HTTPException(status_code=400, detail="Course has no content to generate flashcards from")
        
        # Format course content into a structured prompt
        course_title = course.get('course_title', 'Untitled Course')
        sections = course.get('sections', [])
        
        # Build prompt with course content
        prompt_parts = [
            f"Generate {request.card_count} flashcards from this course content:",
            f"Course Title: {course_title}",
            "",
            "Key concepts and topics:"
        ]
        
        # Extract key concepts from each section
        for i, section in enumerate(sections[:10]):  # Limit to first 10 sections to avoid token limits
            section_title = section.get('section_title', f'Section {i+1}')
            explanation = section.get('explanation', '')
            
            # Truncate long explanations
            if len(explanation) > 500:
                explanation = explanation[:500] + "..."
            
            prompt_parts.append(f"\n{section_title}:")
            # Comment 4: Skip empty explanation line if missing
            if explanation and explanation.strip():
                prompt_parts.append(explanation)
            
            # Include sample quiz questions if available
            quiz = section.get('quiz', [])
            # Comment 4: Trim sample questions when explanation is empty to reduce prompt bloat
            max_questions = 3 if explanation and explanation.strip() else 2
            if quiz and len(quiz) > 0:
                if explanation and explanation.strip():
                    prompt_parts.append("Sample questions:")
                for q in quiz[:max_questions]:
                    question_text = q.get('question', '')
                    if question_text:
                        prompt_parts.append(f"- {question_text}")
            
            # Include subsections if available
            subsections = section.get('subsections') or section.get('subpoints', [])
            if subsections:
                for sub in subsections[:3]:  # Limit subsections
                    sub_title = sub.get('section_title', sub.get('title', ''))
                    if sub_title:
                        prompt_parts.append(f"  • {sub_title}")
        
        # Add explicit instructions for flashcard generation
        prompt_parts.extend([
            "",
            f"Create {request.card_count} flashcards with concise front (question/term) and back (answer/definition) pairs.",
            "Include hints where helpful. Vary difficulty levels (easy, medium, hard).",
            "Focus on key concepts, definitions, and important facts from the course."
        ])
        
        if request.difficulty:
            prompt_parts.append(f"Focus on {request.difficulty} difficulty questions.")
        
        if request.focus_areas:
            prompt_parts.append(f"Focus on these topics: {', '.join(request.focus_areas)}")
        
        formatted_prompt = "\n".join(prompt_parts)
        
        logger.info(f"Formatted prompt length: {len(formatted_prompt)} characters")
        
        # Get user credentials for chat manager if available
        user_credentials = None
        if username and auth_manager:
            try:
                user = auth_manager.get_user_by_username(username)
                if user and user.get('oauth_credentials'):
                    user_credentials = user['oauth_credentials']
            except Exception as e:
                logger.warning(f"Could not load user credentials for chat manager: {e}")
        
        # Initialize chat manager with user credentials
        chat_manager = ChatSessionManager(
            user_credentials=user_credentials,
            username=username or (user_identifier if is_guest else username)
        )
        
        # Send message to AI for flashcard generation
        response = chat_manager.send_message(
            session_id=None,
            message=formatted_prompt,
            file_data=None,
            file_mime_type=None,
            url=None
        )
        
        # Check if flashcards were generated
        if response.get('is_flashcard') and response.get('flashcard_data'):
            flashcard_data = response['flashcard_data']
            
            # Add source_course_id to link flashcards to this course
            flashcard_data['source_course_id'] = course_id
            
            logger.info(f"Successfully generated {len(flashcard_data.get('cards', []))} flashcards from course {course_id}")
            
            return {
                "success": True,
                "flashcard_data": flashcard_data,
                "source_course_id": course_id,
                "reply": response.get('reply', '')
            }
        else:
            logger.warning(f"AI did not generate flashcards for course {course_id}")
            return {
                "success": False,
                "error": "Failed to generate flashcards from course content. The AI may have determined the content is not suitable for flashcard generation."
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating flashcards from course: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")

# Flashcard management endpoints
@app.post("/flashcard/save")
async def save_flashcard(request: SaveFlashcardRequest, username: Optional[str] = None, session_id: Optional[str] = None):
    """Save a flashcard set to the database
    
    For guest users: frontend must persist and send session_id for session continuity.
    If session_id is not provided for guests, a new one will be generated.
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    is_guest = username is None
    # Use provided session_id for guests, or generate new one if not provided
    if is_guest and not session_id:
        session_id = get_session_id()
    
    # Serialize Pydantic FlashcardItem objects to dicts
    flashcard_data_dicts = [item.model_dump(mode='json') for item in request.flashcard_data]
    
    flashcard_id, error = flashcard_manager.save_flashcard(
        flashcard_data=flashcard_data_dicts,
        flashcard_title=request.flashcard_title,
        creator=username or session_id,
        is_guest=is_guest,
        session_id=session_id if is_guest else None,
        source_course_id=request.source_course_id
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {
        "success": True,
        "flashcard_id": flashcard_id,
        "session_id": session_id if is_guest else None  # Return session_id for frontend persistence
    }

@app.get("/flashcard/{flashcard_id}")
async def get_flashcard(flashcard_id: str):
    """Get a flashcard set by ID"""
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    flashcard, error = flashcard_manager.get_flashcard(flashcard_id)
    if error:
        raise HTTPException(status_code=500, detail=error)
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Convert ObjectId to string
    if '_id' in flashcard:
        flashcard['_id'] = str(flashcard['_id'])
    if 'flashcard_id' in flashcard:
        flashcard['flashcard_id'] = str(flashcard['flashcard_id'])
    
    return flashcard

@app.get("/flashcards")
async def list_flashcards(username: Optional[str] = None, session_id: Optional[str] = None):
    """List all flashcards for a user
    
    For guest users: frontend must persist and send session_id for session continuity.
    If session_id is not provided for guests, a new one will be generated (resulting in empty list).
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    if username:
        flashcards, error = flashcard_manager.get_user_flashcards(username, is_guest=False)
    else:
        # Use provided session_id or generate new one
        if not session_id:
            session_id = get_session_id()
        flashcards, error = flashcard_manager.get_user_flashcards(session_id, is_guest=True, session_id=session_id)
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # Ensure flashcards is a list and convert ObjectId to string
    if flashcards is None:
        flashcards = []
    
    for flashcard in flashcards:
        if '_id' in flashcard:
            flashcard['_id'] = str(flashcard['_id'])
        if 'flashcard_id' in flashcard:
            flashcard['flashcard_id'] = str(flashcard['flashcard_id'])
    
    return {"flashcards": flashcards}

@app.get("/flashcards/by-course/{course_id}")
async def get_flashcards_by_course(course_id: str, username: Optional[str] = None, session_id: Optional[str] = None):
    """Get flashcards linked to a specific course
    
    For guest users: frontend must persist and send session_id for session continuity.
    If session_id is not provided for guests, a new one will be generated (resulting in empty list).
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    is_guest = username is None
    # Use provided session_id for guests, or generate new one if not provided
    if is_guest and not session_id:
        session_id = get_session_id()
    user_identifier = username or session_id
    
    flashcards, error = flashcard_manager.get_flashcards_by_course(
        course_id=course_id,
        user_identifier=user_identifier,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # Ensure flashcards is a list and convert ObjectId to string
    if flashcards is None:
        flashcards = []
    
    for flashcard in flashcards:
        if '_id' in flashcard:
            flashcard['_id'] = str(flashcard['_id'])
        if 'flashcard_id' in flashcard:
            flashcard['flashcard_id'] = str(flashcard['flashcard_id'])
    
    return {"flashcards": flashcards}

@app.post("/flashcard/{flashcard_id}/progress")
async def update_flashcard_progress(flashcard_id: str, request: UpdateFlashcardProgressRequest, username: Optional[str] = None, session_id: Optional[str] = None):
    """Update user progress on a flashcard set
    
    For guest users: frontend must persist and send session_id for session continuity.
    If session_id is not provided for guests, a new one will be generated.
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    is_guest = username is None
    # Use provided session_id for guests, or generate new one if not provided
    if is_guest and not session_id:
        session_id = get_session_id()
    user_identifier = username or session_id
    
    # Validate mastery_levels values are within 0-5 range
    for card_idx, level in request.mastery_levels.items():
        if level < 0 or level > 5:
            raise HTTPException(
                status_code=400,
                detail=f"Mastery level for card {card_idx} must be between 0 and 5 (got {level})"
            )
    
    # Build progress data structure from request
    progress_data = {
        "studied_cards": request.studied_cards,
        "mastery_levels": request.mastery_levels,  # Already has string keys from request model
        "last_studied": request.last_studied,
        "accuracy_rate": request.accuracy_rate
    }
    
    success, error = flashcard_manager.save_flashcard_progress(
        flashcard_id=flashcard_id,
        user_identifier=user_identifier,
        progress_data=progress_data,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {"success": success}

@app.get("/flashcard/{flashcard_id}/progress")
async def get_flashcard_progress(flashcard_id: str, username: Optional[str] = None, session_id: Optional[str] = None):
    """Get user progress on a flashcard set
    
    For guest users: frontend must persist and send session_id for session continuity.
    If session_id is not provided for guests, a new one will be generated (resulting in no progress).
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    is_guest = username is None
    # Use provided session_id for guests, or generate new one if not provided
    if is_guest and not session_id:
        session_id = get_session_id()
    user_identifier = username or session_id
    
    progress, error = flashcard_manager.get_flashcard_progress(
        flashcard_id=flashcard_id,
        user_identifier=user_identifier,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return progress or {
        "studied_cards": [],
        "mastery_levels": {},
        "last_studied": None,
        "accuracy_rate": None
    }

@app.delete("/flashcard/{flashcard_id}")
async def delete_flashcard(flashcard_id: str, username: Optional[str] = None, session_id: Optional[str] = None):
    """Delete a flashcard set owned by the user
    
    For guest users: frontend must persist and send session_id for session continuity.
    If session_id is not provided for guests, a new one will be generated.
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")

    is_guest = username is None
    # Use provided session_id for guests, or generate new one if not provided
    if is_guest and not session_id:
        session_id = get_session_id()
    user_identifier = username or session_id

    success, error = flashcard_manager.delete_flashcard(
        flashcard_id=flashcard_id,
        user_identifier=user_identifier,
        is_guest=is_guest
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    return {"success": success}

# Match mode statistics endpoints
@app.post("/flashcard/{flashcard_id}/match-stats")
async def save_match_stats(
    flashcard_id: str, 
    request: MatchModeStatsRequest,
    username: Optional[str] = None, 
    session_id: Optional[str] = None
):
    """Save match mode game statistics for a flashcard set
    
    Tracks completion time, moves count, and updates personal bests.
    For guest users: stats are saved to session_id, for authenticated users to username.
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    is_guest = username is None
    if is_guest and not session_id:
        session_id = get_session_id()
    user_identifier = username or session_id
    
    # Get existing progress to update match stats
    progress, error = flashcard_manager.get_flashcard_progress(
        flashcard_id=flashcard_id,
        user_identifier=user_identifier,
        is_guest=is_guest
    )
    
    if error and error != "Database connection error.":
        # If error is connection error, we should fail
        if "connection" in error.lower():
            raise HTTPException(status_code=500, detail=error)
        # Otherwise, start with empty progress
        progress = {}
    
    if not progress:
        progress = {}
    
    # Initialize match_mode_stats if it doesn't exist
    if 'match_mode_stats' not in progress:
        progress['match_mode_stats'] = {
            'personal_best_time': None,
            'games_played': 0,
            'total_time': 0,
            'best_moves': None,
            'total_moves': 0,
            'last_played': None
        }
    
    match_stats = progress['match_mode_stats']
    
    # Update statistics
    match_stats['games_played'] = match_stats.get('games_played', 0) + 1
    match_stats['total_time'] = match_stats.get('total_time', 0) + request.completion_time
    match_stats['total_moves'] = match_stats.get('total_moves', 0) + request.moves_count
    match_stats['last_played'] = request.timestamp
    
    # Update personal bests
    if match_stats['personal_best_time'] is None or request.completion_time < match_stats['personal_best_time']:
        match_stats['personal_best_time'] = request.completion_time
    
    if match_stats['best_moves'] is None or request.moves_count < match_stats['best_moves']:
        match_stats['best_moves'] = request.moves_count
    
    # Calculate averages
    match_stats['average_time'] = match_stats['total_time'] / match_stats['games_played']
    match_stats['average_moves'] = match_stats['total_moves'] / match_stats['games_played']
    
    # Save updated progress
    success, error = flashcard_manager.save_flashcard_progress(
        flashcard_id=flashcard_id,
        user_identifier=user_identifier,
        progress_data=progress,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {
        "success": True,
        "stats": match_stats
    }

@app.get("/flashcard/{flashcard_id}/match-stats")
async def get_match_stats(
    flashcard_id: str,
    username: Optional[str] = None,
    session_id: Optional[str] = None
):
    """Get match mode statistics for a flashcard set
    
    Returns personal bests and aggregate statistics.
    """
    if not flashcard_manager:
        raise HTTPException(status_code=503, detail="Flashcard manager unavailable")
    
    is_guest = username is None
    if is_guest and not session_id:
        session_id = get_session_id()
    user_identifier = username or session_id
    
    progress, error = flashcard_manager.get_flashcard_progress(
        flashcard_id=flashcard_id,
        user_identifier=user_identifier,
        is_guest=is_guest
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # Return match stats or empty default
    if progress and 'match_mode_stats' in progress:
        return progress['match_mode_stats']
    else:
        return {
            'personal_best_time': None,
            'games_played': 0,
            'average_time': None,
            'best_moves': None,
            'average_moves': None,
            'last_played': None
        }

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
                "is_course": False,
                "is_flashcard": False
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
                        "is_course": False,
                        "is_flashcard": False
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
            is_safe, error_message = validate_file_security(
                filename=file.filename,
                file_size=len(file_data)
            )
            validation_result = {"valid": is_safe, "error": error_message}
            
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
        
        # Optional debug log when a course was detected
        if result.get('is_course'):
            logger.info(f"Course detected for user={username or 'guest'} session={result.get('session_id')} (source={result.get('course_detection_source','function_or_json')})")

        # Optional debug log when a flashcard set was detected
        if result.get('is_flashcard'):
            logger.info(f"Flashcard set detected for user={username or 'guest'} session={result.get('session_id')}")

        # Return enhanced response with course and flashcard detection
        return {
            "success": True,
            "reply": result['reply'],
            "session_id": result['session_id'],
            "is_course": result.get('is_course', False),
            "course_data": result.get('course_data'),
            "is_flashcard": result.get('is_flashcard', False),
            "flashcard_data": result.get('flashcard_data'),
            "course_detection_source": result.get('course_detection_source'),
            "flashcard_detection_source": result.get('flashcard_detection_source'),
            "activity_info": result.get('activity_info')
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
