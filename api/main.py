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
    title="Learnify API",
    description="AI-powered course and quiz generation API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"],  # Vue dev servers
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Learnify API",
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
@app.post("/api/auth/register")
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

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    user = auth_manager.find_user_by_username(credentials.username)
    if not user or not auth_manager.verify_password(credentials.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {
        "success": True,
        "username": user["username"],
        "name": user.get("name"),
        "email": user.get("email")
    }

# Course generation endpoints
@app.post("/api/course/generate/upload")
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

@app.post("/api/course/generate/url")
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
@app.post("/api/quiz/validate-answer")
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
@app.post("/api/course/save")
async def save_course(request: SaveCourseRequest, username: Optional[str] = None):
    """Save a course to the database"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    session_id = get_session_id()
    is_guest = username is None
    
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

@app.get("/api/course/{course_id}")
async def get_course(course_id: str):
    """Get a course by ID"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    course = course_manager.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course

@app.get("/api/courses")
async def list_courses(username: Optional[str] = None):
    """List all courses for a user"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    if username:
        courses = course_manager.get_user_courses(username)
    else:
        session_id = get_session_id()
        courses = course_manager.get_guest_courses(session_id)
    
    return {"courses": courses}

@app.post("/api/course/{course_id}/progress")
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

@app.get("/api/course/{course_id}/progress")
async def get_progress(course_id: str, username: Optional[str] = None):
    """Get user progress on a course"""
    if not course_manager:
        raise HTTPException(status_code=503, detail="Course manager unavailable")
    
    user_identifier = username or get_session_id()
    progress = course_manager.get_progress(user_identifier, course_id)
    
    return progress or {"progress": {}}

# Analytics endpoints
@app.get("/api/analytics/courses")
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
