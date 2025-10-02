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
from pathlib import Path
from dotenv import load_dotenv

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

# Create FastAPI app
app = FastAPI(
    title="AI Loom API",
    description="AI-powered course and quiz generation API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8080", 
        "http://localhost:5173",
        "https://ai-loom-frontend.onrender.com",  # Production frontend
        "https://learnify-geih.onrender.com"  # Old Streamlit app
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
auth_manager = None
course_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global auth_manager, course_manager
    try:
        auth_manager = MongoAuthManager()
        course_manager = MongoCourseManager()
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
    course_id: str
    section_index: int
    subsection_index: Optional[int] = None
    question_index: int
    is_correct: bool

class SendVerificationRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

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
    
    return {
        "success": True,
        "username": user["username"],
        "name": user.get("name"),
        "email": user.get("email"),
        "isAdmin": is_admin
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
    
    # Update password
    from bcrypt import hashpw, gensalt
    hashed_password = hashpw(request.new_password.encode('utf-8'), gensalt()).decode('utf-8')
    
    # Update password in database
    try:
        auth_manager.users.update_one(
            {"email": request.email},
            {"$set": {"password": hashed_password}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update password")
    
    return {
        "success": True,
        "message": "Password has been reset successfully"
    }

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
    
    # Update user details
    success, error = auth_manager.update_user_details(
        username=request.username,
        updates={
            "name": request.name,
            "email": request.email
        }
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
    
    # Generate course
    course_data, error = generate_course(
        file_content=file_bytes,
        filename=file.filename
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
async def generate_course_from_url(request: CourseGenerationRequest):
    """Generate a course from a URL"""
    if not request.file_url:
        raise HTTPException(status_code=400, detail="file_url is required")
    
    # Generate course
    course_data, error = generate_course(
        file_url=request.file_url
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
async def validate_answer(request: ValidateAnswerRequest):
    """Validate a short answer using AI"""
    is_correct, explanation = validate_short_answer_with_ai(
        question=request.question,
        user_answer=request.user_answer,
        expected_answer=request.expected_answer
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
    
    success, error = course_manager.update_progress(
        user_identifier=user_identifier,
        course_id=course_id,
        section_index=request.section_index,
        subsection_index=request.subsection_index,
        question_index=request.question_index,
        is_correct=request.is_correct
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
    progress = course_manager.get_progress(user_identifier, course_id)
    
    return progress or {"progress": {}}

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
