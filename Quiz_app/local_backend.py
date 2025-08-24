import logging
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError
from typing import Union, Optional, List, Literal
from dotenv import load_dotenv
import json
import os
import requests
import io
import re
import mimetypes

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")  # Load debug mode from environment

# Define dangerous file extensions that should be blocked for security
DANGEROUS_EXTENSIONS = {
    # Executable files
    '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.app', '.deb', '.rpm', '.msi',
    # Scripts that could be harmful
    '.vbs', '.js', '.jar', '.ps1', '.sh', '.bash', '.csh', '.fish',
    # System files
    '.sys', '.dll', '.ini', '.reg',
    # Shortcuts that could be used maliciously
    '.lnk', '.url',
    # Other potentially dangerous files
    '.hta', '.wsf', '.wsh'
}

# Define a Pydantic model for arbitrary key-value mappings
class ArbitraryMapping(BaseModel):
    model_config = {"extra": "allow"}

# Define Pydantic Schemas
class QuizItem(BaseModel):
    type: Literal[
        "multiple_choice", "multiple choice",
        "fill_in_the_blank", "fill in the blank",
        "match",
        "short_answer", "short answer",
        "true_false", "true false",
        "true or false"  # Added 'true or false' to accepted literals
    ]  # accept both formats
    question: str
    options: Optional[List[str]] = Field(default=None, alias="choices")
    answer: Union[str, bool, List[str], ArbitraryMapping]

class Section(BaseModel):
    section_title: str = Field(alias="section")
    explanation: str
    quiz: List[QuizItem] = Field(alias="questions")
    # Allow sections to be nested. The alias "sub_sections" is provided as the AI might prefer it.
    # If the AI doesn't provide this field, it will default to None.
    subsections: Optional[List['Section']] = Field(default=None, alias="sub_sections", title="Sub Sections")

# Pydantic v2 automatically handles the self-reference 'Section' in List['Section']

class Course(BaseModel):
    course_title: str # This might not be provided by the AI with current prompts
    sections: List[Section]

# New model to match the ACTUAL API response structure (with course title)
class ActualApiResponse(BaseModel):
    course_title: str
    sections: List[Section]

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API key - try Streamlit secrets first, then environment variables
api_key = None

if STREAMLIT_AVAILABLE:
    try:
        api_key = st.secrets.GEMINI_API_KEY
        logger.info("Successfully loaded API key from Streamlit secrets")
    except (KeyError, FileNotFoundError):
        logger.info("Streamlit secrets not available or key not found, trying environment variables")

# Fallback to environment variables if Streamlit secrets not available
if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        logger.info("Successfully loaded API key from environment variables")

if not api_key:
    logger.error("GEMINI_API_KEY not found in Streamlit secrets or environment variables. Please check your configuration.")
    raise ValueError("GEMINI_API_KEY is required but not found in Streamlit secrets or environment variables")

try:
    client = genai.Client(api_key=api_key)
    logger.info("Gemini client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    raise

# Determine base directory for loading prompt and system instructions
BASE_DIR = os.path.dirname(__file__)
PROMPT_PATH = os.path.join(BASE_DIR, "prompt.txt")
SYS_INS_PATH = os.path.join(BASE_DIR, "sys_ins.txt")

# Load prompt and system instructions with error handling
try:
    with open(PROMPT_PATH, "r", encoding='utf-8') as f:
        prompt = f.read()
    logger.debug(f"Loaded prompt.txt ({len(prompt)} characters)")
except FileNotFoundError:
    logger.error(f"prompt.txt not found at {PROMPT_PATH}")
    raise
except Exception as e:
    logger.error(f"Error reading prompt.txt: {e}")
    raise

try:
    with open(SYS_INS_PATH, "r", encoding='utf-8') as f:
        sys_ins = f.read()
    logger.debug(f"Loaded sys_ins.txt ({len(sys_ins)} characters)")
except FileNotFoundError:
    logger.error(f"sys_ins.txt not found at {SYS_INS_PATH}")
    raise
except Exception as e:
    logger.error(f"Error reading sys_ins.txt: {e}")
    raise

def is_file_extension_safe(filename):
    """Check if a file extension is safe to upload"""
    if not filename:
        return False
    
    # Get file extension (case-insensitive)
    _, ext = os.path.splitext(filename.lower())
    
    # Block dangerous extensions
    if ext in DANGEROUS_EXTENSIONS:
        return False
    
    return True

def get_mime_type(filename, file_content=None):
    """Detect MIME type from filename and optionally file content"""
    if not filename:
        return "application/octet-stream"
    
    # Try to guess MIME type from filename
    mime_type, _ = mimetypes.guess_type(filename)
    
    # If we can't determine from filename, try from content
    if not mime_type and file_content:
        # Check for common file signatures
        if file_content.startswith(b'%PDF-'):
            mime_type = "application/pdf"
        elif file_content.startswith(b'\x89PNG'):
            mime_type = "image/png"
        elif file_content.startswith(b'\xff\xd8\xff'):
            mime_type = "image/jpeg"
        elif file_content.startswith(b'GIF8'):
            mime_type = "image/gif"
        elif file_content.startswith(b'PK\x03\x04'):
            # Could be various ZIP-based formats
            if filename.lower().endswith(('.docx', '.xlsx', '.pptx')):
                if 'word' in filename.lower():
                    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                elif 'excel' in filename.lower() or 'sheet' in filename.lower():
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                elif 'powerpoint' in filename.lower() or 'presentation' in filename.lower():
                    mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                mime_type = "application/zip"
    
    # Default fallback
    if not mime_type:
        mime_type = "application/octet-stream"
    
    return mime_type

def validate_file_content(file_content, filename):
    """Validate file content and check for security issues"""
    if not file_content:
        return False, "File is empty"
    
    if not filename:
        return False, "No filename provided"
    
    # Check file extension safety
    if not is_file_extension_safe(filename):
        _, ext = os.path.splitext(filename.lower())
        return False, f"File type '{ext}' is not allowed for security reasons. Executable files and scripts are blocked."
    
    # Check minimum size (should be at least a few bytes)
    if len(file_content) < 10:
        return False, "File is too small to contain meaningful content"
    
    return True, None

def estimate_processing_time_by_size(file_size_bytes):
    """
    Estimate processing time based on file size since we're not doing content analysis.
    This is a rough estimate for user expectations.
    """
    # Convert to MB for easier calculation
    size_mb = file_size_bytes / (1024 * 1024)
    
    # Base overhead time for AI setup and response processing
    base_overhead = 10  # seconds
    
    if size_mb < 1:
        # Small files
        total_time = base_overhead + 15
        return f"{total_time}-{total_time + 10} seconds"
    elif size_mb < 3:
        # Medium files
        total_time = base_overhead + 25
        return f"{total_time}-{total_time + 15} seconds"
    elif size_mb < 5:
        # Larger files
        total_time = base_overhead + 40
        minutes = total_time // 60
        seconds = total_time % 60
        upper_time = total_time + 20
        upper_minutes = upper_time // 60
        upper_seconds = upper_time % 60
        
        if minutes == 0:
            return f"{total_time}-{total_time + 20} seconds"
        else:
            return f"{minutes}:{seconds:02d}-{upper_minutes}:{upper_seconds:02d} minutes"
    else:
        # Large files
        total_time = base_overhead + 60
        minutes = total_time // 60
        seconds = total_time % 60
        upper_time = total_time + 30
        upper_minutes = upper_time // 60
        upper_seconds = upper_time % 60
        return f"{minutes}:{seconds:02d}-{upper_minutes}:{upper_seconds:02d} minutes"

def validate_short_answer_with_ai(question, user_answer, expected_answer):
    """
    Use AI to validate a short answer question and provide feedback.
    
    Args:
        question: The original question text
        user_answer: The user's submitted answer
        expected_answer: The expected/correct answer
        
    Returns:
        tuple: (is_correct, explanation)
            - is_correct: Boolean indicating if the answer is correct
            - explanation: String explanation of why the answer is correct/incorrect
    """
    try:
        validation_prompt = f"""
You are an expert teacher evaluating a student's short answer response. 

Question: {question}
Expected Answer: {expected_answer}
Student's Answer: {user_answer}

Please evaluate if the student's answer is correct or incorrect. Consider:
1. The core meaning and concepts should match
2. Minor spelling, grammar, or formatting differences should not matter
3. Synonyms and equivalent expressions should be accepted
4. The answer should demonstrate understanding of the key concepts

Respond with a JSON object in this exact format:
{{
    "is_correct": true/false,
    "explanation": "Brief explanation (1-2 sentences) of why the answer is correct or what's missing/wrong if incorrect"
}}

Be fair but accurate in your evaluation.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3  # Lower temperature for more consistent evaluation
            ),
            contents=[validation_prompt]
        )
        
        if not response.text:
            logger.warning("Empty response from AI validation")
            return None, "AI validation failed"
        
        # Parse the JSON response
        validation_result = json.loads(response.text)
        is_correct = validation_result.get("is_correct", False)
        explanation = validation_result.get("explanation", "No explanation provided")
        
        logger.info(f"AI validation result: {'Correct' if is_correct else 'Incorrect'}")
        return is_correct, explanation
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI validation response: {e}")
        return None, "AI validation response was invalid"
    except Exception as e:
        logger.error(f"Error in AI validation: {e}")
        return None, f"AI validation error: {str(e)}"
    
def generate_course(file_content=None, file_url=None, filename=None, status_callback=None):
    """
    Generate a course structure from file content or a file URL.
    
    Args:
        file_content: The binary content of a file
        file_url: URL to a file
        filename: Name of the uploaded file (used for MIME type detection and security validation)
        status_callback: Optional callback function to report progress status
        
    Returns:
        tuple: (course_data, error_message)
            - course_data: List of Section objects or None if an error occurred
            - error_message: Error message or None if successful
    """
    # Start timing for performance measurement
    import time
    start_time = time.time()
    
    def update_status(message, progress=None):
        """Helper function to update status via callback"""
        if status_callback:
            status_callback(message, progress)
        logger.info(message)
    
    file_bytes = None
    detected_mime_type = None
    update_status("🚀 Starting course generation process...", 5)
    
    # Handle file content
    if file_content:
        update_status("📄 Validating uploaded file...", 10)
        logger.info(f"Processing uploaded file ({len(file_content)} bytes)")
        
        # Validate file security and content
        is_valid, error_msg = validate_file_content(file_content, filename)
        if not is_valid:
            return None, error_msg
        
        # Detect MIME type
        detected_mime_type = get_mime_type(filename, file_content)
        file_bytes = file_content
        update_status("✅ File validated successfully", 20)
    
    # Handle file URL
    elif file_url:
        update_status("🌐 Connecting to file URL...", 10)
        logger.info(f"Fetching file from URL: {file_url}")
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            update_status("📥 Downloading file from URL...", 15)
            resp = requests.get(file_url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            # Extract filename from URL for validation
            url_filename = os.path.basename(file_url.split('?')[0])  # Remove query params
            if not url_filename:
                url_filename = "downloaded_file"
            
            update_status("🔍 Validating downloaded file...", 18)
            # Validate downloaded file
            is_valid, error_msg = validate_file_content(resp.content, url_filename)
            if not is_valid:
                return None, f"Downloaded file validation failed: {error_msg}"
            
            # Detect MIME type from URL and content
            detected_mime_type = get_mime_type(url_filename, resp.content)
            file_bytes = resp.content
            update_status(f"✅ File downloaded successfully ({len(file_bytes)} bytes)", 20)
            logger.info(f"Successfully fetched file ({len(file_bytes)} bytes)")
            
        except requests.exceptions.Timeout:
            return None, "Request timed out. The file may be too large or the server is slow."
        except requests.exceptions.ConnectionError:
            return None, "Connection error. Please check the URL and your internet connection."
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP error {e.response.status_code}: Unable to fetch file from URL"
        except Exception as e:
            logger.error(f"Error fetching file from URL: {e}")
            return None, f"Unable to fetch file from URL: {e}"
            
    # Check if we have file content
    if not file_bytes:
        return None, "No file content or file_url provided, or an error occurred processing the input."
    
    update_status("📏 Checking file size limits...", 25)
    # Check file size limits
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_bytes) > max_size:
        return None, f"File is too large ({len(file_bytes)} bytes). Maximum size is {max_size} bytes (10MB)."
    
    # Estimate processing time based on file size (since we can't analyze content beforehand)
    estimated_time = estimate_processing_time_by_size(len(file_bytes))
    
    # Update status with estimated time information
    update_status(f"📊 AI is analyzing file content (Est. time: {estimated_time})", 32)
    
    try:
        update_status("🤖 Connecting to Gemini AI...", 35)
        logger.info("Sending request to Gemini AI...")
        
        update_status(f"📤 Uploading file to AI for analysis... (Est. time: {estimated_time})", 45)
        # Generate content using Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            config=types.GenerateContentConfig(
                system_instruction=sys_ins,
                response_mime_type="application/json",
            ),
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=detected_mime_type),
                prompt,
            ],
        )

        update_status(f"🧠 AI is analyzing content... (Est. time: {estimated_time})", 65)
        if not response.text:
            logger.error("Received empty response from Gemini AI")
            return None, "Empty response from AI model. Please try again."
        
        update_status("📝 Generating course structure and questions...", 70)
        logger.info(f"Received response from Gemini AI ({len(response.text)} characters)")
        
        update_status("🔧 Processing AI response...", 80)
        try:
            # Try to parse with Pydantic validation first
            update_status("✅ Validating course content...", 90)
            parsed = ActualApiResponse.model_validate_json(response.text)
            logger.info("Successfully validated response with Pydantic schema")
            if DEBUG_MODE:
                logger.info(f"Parsed response: {parsed}")
            update_status("🎉 Course generated successfully!", 100)
            
            # Log actual generation time for performance tracking
            actual_time = time.time() - start_time
            logger.info(f"Course generation completed in {actual_time:.1f} seconds (File size: {len(file_bytes)} bytes, Estimated: {estimated_time})")
            
            return parsed, None
        except ValidationError as ve:
            logger.warning(f"Response schema validation failed: {ve}")
            try:
                update_status("🔄 Using fallback parsing method...", 85)
                # Fallback to raw JSON parsing
                raw_data = json.loads(response.text)
                logger.info("Successfully parsed as raw JSON (schema validation failed)")
                update_status("🎉 Course generated successfully!", 100)
                
                # Log actual generation time for performance tracking
                actual_time = time.time() - start_time
                logger.info(f"Course generation completed in {actual_time:.1f} seconds (File size: {len(file_bytes)} bytes, Estimated: {estimated_time})")
                
                return raw_data, None
            except json.JSONDecodeError as je:
                logger.error(f"JSON decode error: {je}")
                return None, f"Failed to parse AI response as valid JSON. Please try again."
        
    except Exception as e:
        # Log timing even for failed attempts
        actual_time = time.time() - start_time
        logger.error(f"Error generating course after {actual_time:.1f} seconds: {e}")
        
        error_message = str(e)
        
        # Provide more specific error messages for common issues
        if "quota" in error_message.lower():
            error_message = "API quota exceeded. Please check your Gemini API usage limits."
        elif "api_key" in error_message.lower():
            error_message = "Invalid API key. Please check your GEMINI_API_KEY in the .env file."
        elif "timeout" in error_message.lower():
            error_message = "Request timed out. The file may be too complex or the service is busy."
        
        return None, f"Error generating course: {error_message}"



