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
import PyPDF2
import pdfplumber

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")  # Load debug mode from environment

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
    
def generate_course(file_content=None, file_url=None, status_callback=None):
    """
    Generate a course structure from PDF content or a PDF URL.
    
    Args:
        file_content: The binary content of a PDF file
        file_url: URL to a PDF file
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
    
    pdf_bytes = None
    update_status("🚀 Starting course generation process...", 5)
    
    # Handle file content
    if file_content:
        update_status("📄 Validating uploaded PDF file...", 10)
        logger.info(f"Processing uploaded PDF file ({len(file_content)} bytes)")
        if not validate_pdf_content(file_content):
            return None, "Invalid PDF file. Please ensure you're uploading a valid PDF document."
        pdf_bytes = file_content
        update_status("✅ PDF file validated successfully", 20)
    
    # Handle file URL
    elif file_url:
        update_status("🌐 Connecting to PDF URL...", 10)
        logger.info(f"Fetching PDF from URL: {file_url}")
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            update_status("📥 Downloading PDF from URL...", 15)
            resp = requests.get(file_url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            # Check content type
            content_type = resp.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type and not file_url.lower().endswith('.pdf'):
                logger.warning(f"Content type '{content_type}' may not be a PDF")
            
            update_status("🔍 Validating downloaded PDF...", 18)
            if not validate_pdf_content(resp.content):
                return None, "The URL does not point to a valid PDF file."
            
            pdf_bytes = resp.content
            update_status(f"✅ PDF downloaded successfully ({len(pdf_bytes)} bytes)", 20)
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
    
    update_status("📏 Checking file size and content limits...", 25)
    # Check file size limits (reduced from 20MB to 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(pdf_bytes) > max_size:
        return None, f"PDF file is too large ({len(pdf_bytes)} bytes). Maximum size is {max_size} bytes (10MB)."      # Analyze PDF content for word count
    update_status("📊 Analyzing PDF content and word count...", 30)
    pdf_analysis = analyze_pdf_content(pdf_bytes)
    word_count = pdf_analysis['word_count']
    estimated_time = pdf_analysis['estimated_time']
    
    if word_count == 0:
        return None, "Could not extract readable text from this PDF. Please ensure the PDF contains text content."
    
    if word_count > 15000:
        return None, f"PDF contains too many words ({word_count:,}). Maximum allowed is 15,000 words. Please use a shorter document."
      # Update status with estimated time information
    update_status(f"📊 AI is analyzing PDF content (Est. time: {estimated_time})", 32)
    
    try:
        update_status("🤖 Connecting to Gemini AI...", 35)
        logger.info("Sending request to Gemini AI...")
        
        update_status(f"📤 Uploading PDF to AI for analysis... (Est. time: {estimated_time})", 45)
        # Generate content using Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            config=types.GenerateContentConfig(
                system_instruction=sys_ins,
                response_mime_type="application/json",
            ),
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
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
            logger.info(f"Course generation completed in {actual_time:.1f} seconds (Word count: {word_count}, Estimated: {estimated_time})")
            
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
                logger.info(f"Course generation completed in {actual_time:.1f} seconds (Word count: {word_count}, Estimated: {estimated_time})")
                
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
            error_message = "Request timed out. The PDF may be too complex or the service is busy."
        
        return None, f"Error generating course: {error_message}"

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes using multiple methods for reliability"""
    text = ""
    
    try:
        # Method 1: Try pdfplumber first (usually more accurate)
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        if text.strip():
            return text
            
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")
    
    try:
        # Method 2: Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed: {e}")
    
    return text

def count_words_in_text(text):
    """Count words in text, excluding very short words and numbers only"""
    if not text:
        return 0
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split into words and filter
    words = text.split()
    
    # Count meaningful words (length > 2 and not just numbers/symbols)
    meaningful_words = [
        word for word in words 
        if len(word) > 2 and re.search(r'[a-zA-Z]', word)
    ]
    
    return len(meaningful_words)

def estimate_generation_time(word_count):
    """
    Estimate course generation time based on word count and AI processing complexity.
    
    Factors considered:
    - PDF text extraction and processing
    - AI model processing time (scales with content complexity)
    - Course structure generation
    - Question generation complexity
    
    The AI model (Gemini 2.5 Flash) typically processes:
    - Simple documents: ~200-500 words per second
    - Complex documents: ~100-300 words per second
    
    Additional overhead:
    - PDF processing: 2-5 seconds
    - AI connection and setup: 3-8 seconds  
    - Response processing and validation: 2-5 seconds
    """
    # Base overhead time for PDF processing, AI setup, and response validation
    base_overhead = 10  # seconds
    
    # AI processing time varies by content complexity and word count
    # Gemini 2.5 Flash typically processes text fairly quickly, but generation is slower
    if word_count < 500:
        # Very short documents - minimal content, few questions
        ai_processing_time = 15  # seconds
        total_time = base_overhead + ai_processing_time
        return f"{total_time}-{total_time + 10} seconds"
    
    elif word_count < 1500:
        # Short documents - 1-3 sections, moderate questions
        ai_processing_time = 20  # seconds
        total_time = base_overhead + ai_processing_time
        return f"{total_time}-{total_time + 15} seconds"
    
    elif word_count < 3000:
        # Medium documents - 3-5 sections, good question variety
        ai_processing_time = 35  # seconds
        total_time = base_overhead + ai_processing_time
        return f"{total_time}-{total_time + 20} seconds"
    
    elif word_count < 5000:
        # Larger documents - 5-7 sections, complex structure
        ai_processing_time = 50  # seconds
        total_time = base_overhead + ai_processing_time
        minutes = total_time // 60
        remaining_seconds = total_time % 60
        upper_minutes = (total_time + 25) // 60
        upper_seconds = (total_time + 25) % 60
        
        if minutes == 0:
            return f"{total_time}-{total_time + 25} seconds"
        elif upper_minutes == minutes:
            return f"{minutes}:{remaining_seconds:02d}-{minutes}:{upper_seconds:02d} minutes"
        else:
            return f"{minutes}:{remaining_seconds:02d}-{upper_minutes}:{upper_seconds:02d} minutes"
    
    elif word_count < 8000:
        # Large documents - 7-10 sections, comprehensive content
        ai_processing_time = 75  # seconds
        total_time = base_overhead + ai_processing_time
        minutes = total_time // 60
        remaining_seconds = total_time % 60
        upper_time = total_time + 30
        upper_minutes = upper_time // 60
        upper_seconds = upper_time % 60
        return f"{minutes}:{remaining_seconds:02d}-{upper_minutes}:{upper_seconds:02d} minutes"
    
    elif word_count < 12000:
        # Very large documents - 10+ sections, extensive questions
        ai_processing_time = 105  # seconds
        total_time = base_overhead + ai_processing_time
        minutes = total_time // 60
        remaining_seconds = total_time % 60
        upper_time = total_time + 45
        upper_minutes = upper_time // 60
        upper_seconds = upper_time % 60
        return f"{minutes}:{remaining_seconds:02d}-{upper_minutes}:{upper_seconds:02d} minutes"
    
    else:
        # Maximum size documents - comprehensive courses
        ai_processing_time = 140  # seconds
        total_time = base_overhead + ai_processing_time
        minutes = total_time // 60
        remaining_seconds = total_time % 60
        upper_time = total_time + 60
        upper_minutes = upper_time // 60
        upper_seconds = upper_time % 60
        return f"{minutes}:{remaining_seconds:02d}-{upper_minutes}:{upper_seconds:02d} minutes"

def analyze_pdf_content(pdf_bytes):
    """Analyze PDF content and return word count and estimated time"""
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_bytes)
        
        # Count words
        word_count = count_words_in_text(text)
        
        # Estimate generation time
        estimated_time = estimate_generation_time(word_count)
        
        return {
            'word_count': word_count,
            'estimated_time': estimated_time,
            'text_length': len(text),
            'has_content': bool(text.strip())
        }
        
    except Exception as e:
        logger.error(f"Error analyzing PDF content: {e}")
        return {
            'word_count': 0,
            'estimated_time': "Unknown",
            'text_length': 0,
            'has_content': False
        }
