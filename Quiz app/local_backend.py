import logging
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, RootModel, ValidationError
from typing import Union, Optional, List, Dict, Any, Literal
from dotenv import load_dotenv
import json
import os
import requests
import io

DEBUG_MODE = False  # Set to True to enable debug logging

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
    answer: Union[str, bool, ArbitraryMapping]

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

# New model to match the ACTUAL API response structure (a list of sections)
class ActualApiResponse(RootModel):
    root: List[Section] # The API response is a list of top-level sections

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
    raise ValueError("GEMINI_API_KEY is required but not found in environment variables")

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

def validate_pdf_content(pdf_bytes):
    """Validate that the content is actually a PDF"""
    if not pdf_bytes:
        return False
    
    # Check PDF header
    if not pdf_bytes.startswith(b'%PDF-'):
        return False
    
    # Check minimum size (a valid PDF should be at least a few KB)
    if len(pdf_bytes) < 1024:
        return False
    
    return True

def generate_course(file_content=None, file_url=None):
    """
    Generate a course structure from PDF content or a PDF URL.
    
    Args:
        file_content: The binary content of a PDF file
        file_url: URL to a PDF file
        
    Returns:
        tuple: (course_data, error_message)
            - course_data: List of Section objects or None if an error occurred
            - error_message: Error message or None if successful
    """
    pdf_bytes = None
    
    # Handle file content
    if file_content:
        logger.info(f"Processing uploaded PDF file ({len(file_content)} bytes)")
        if not validate_pdf_content(file_content):
            return None, "Invalid PDF file. Please ensure you're uploading a valid PDF document."
        pdf_bytes = file_content
    
    # Handle file URL
    elif file_url:
        logger.info(f"Fetching PDF from URL: {file_url}")
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            resp = requests.get(file_url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            # Check content type
            content_type = resp.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type and not file_url.lower().endswith('.pdf'):
                logger.warning(f"Content type '{content_type}' may not be a PDF")
            
            if not validate_pdf_content(resp.content):
                return None, "The URL does not point to a valid PDF file."
            
            pdf_bytes = resp.content
            logger.info(f"Successfully fetched PDF ({len(pdf_bytes)} bytes)")
            
        except requests.exceptions.Timeout:
            return None, "Request timed out. The PDF file may be too large or the server is slow."
        except requests.exceptions.ConnectionError:
            return None, "Connection error. Please check the URL and your internet connection."
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP error {e.response.status_code}: Unable to fetch PDF from URL"
        except Exception as e:
            logger.error(f"Error fetching PDF from URL: {e}")
            return None, f"Unable to fetch PDF from URL: {e}"
    
    # Check if we have PDF content
    if not pdf_bytes:
        return None, "No file content or file_url provided, or an error occurred processing the input."
    
    # Check file size limits
    max_size = 20 * 1024 * 1024  # 20MB
    if len(pdf_bytes) > max_size:
        return None, f"PDF file is too large ({len(pdf_bytes)} bytes). Maximum size is {max_size} bytes (20MB)."
    
    try:
        logger.info("Sending request to Gemini AI...")
        # Generate content using Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=sys_ins,
                response_mime_type="application/json",
            ),
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                prompt,
            ],
        )
        
        if not response.text:
            logger.error("Received empty response from Gemini AI")
            return None, "Empty response from AI model. Please try again."
        
        logger.info(f"Received response from Gemini AI ({len(response.text)} characters)")
        
        try:
            # Try to parse with Pydantic validation first
            parsed = ActualApiResponse.model_validate_json(response.text)
            logger.info("Successfully validated response with Pydantic schema")
            return parsed.root, None
        except ValidationError as ve:
            logger.warning(f"Response schema validation failed: {ve}")
            try:
                # Fallback to raw JSON parsing
                raw_data = json.loads(response.text)
                logger.info("Successfully parsed as raw JSON (schema validation failed)")
                return raw_data, None
            except json.JSONDecodeError as je:
                logger.error(f"JSON decode error: {je}")
                return None, f"Failed to parse AI response as valid JSON. Please try again."
        
    except Exception as e:
        logger.error(f"Error generating course: {e}")
        error_message = str(e)
        
        # Provide more specific error messages for common issues
        if "quota" in error_message.lower():
            error_message = "API quota exceeded. Please check your Gemini API usage limits."
        elif "api_key" in error_message.lower():
            error_message = "Invalid API key. Please check your GEMINI_API_KEY in the .env file."
        elif "timeout" in error_message.lower():
            error_message = "Request timed out. The PDF may be too complex or the service is busy."
        
        return None, f"Error generating course: {error_message}"
