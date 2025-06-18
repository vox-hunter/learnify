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
import re
import PyPDF2
import pdfplumber

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

# Optimized Pydantic models
class ArbitraryMapping(BaseModel):
    model_config = {"extra": "allow"}

class QuizItem(BaseModel):
    type: Literal[
        "multiple_choice", "multiple choice",
        "fill_in_the_blank", "fill in the blank",
        "match",
        "short_answer", "short answer",
        "true_false", "true false",
        "true or false"
    ]
    question: str
    options: Optional[List[str]] = Field(default=None, alias="choices")
    answer: Union[str, bool, List[str], ArbitraryMapping]

class Section(BaseModel):
    section_title: str = Field(alias="section")
    explanation: str
    quiz: List[QuizItem] = Field(alias="questions")
    subsections: Optional[List['Section']] = Field(default=None, alias="sub_sections", title="Sub Sections")

class Course(BaseModel):
    course_title: str
    sections: List[Section]

class ActualApiResponse(RootModel):
    root: List[Section]

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Optimized API key validation
api_key = None
if STREAMLIT_AVAILABLE:
    try:
        api_key = st.secrets.GEMINI_API_KEY
        logger.info("Successfully loaded API key from Streamlit secrets")
    except (KeyError, FileNotFoundError):
        logger.info("Streamlit secrets not available, trying environment variables")

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        logger.info("Successfully loaded API key from environment variables")

if not api_key:
    logger.error("GEMINI_API_KEY not found")
    raise ValueError("GEMINI_API_KEY is required")

try:
    client = genai.Client(api_key=api_key)
    logger.info("Gemini client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    raise

# Load prompt and system instructions
BASE_DIR = os.path.dirname(__file__)
PROMPT_PATH = os.path.join(BASE_DIR, "prompt.txt")
SYS_INS_PATH = os.path.join(BASE_DIR, "sys_ins.txt")

try:
    with open(PROMPT_PATH, "r", encoding='utf-8') as f:
        prompt = f.read()
    logger.debug(f"Loaded prompt.txt ({len(prompt)} characters)")
except FileNotFoundError:
    logger.error(f"prompt.txt not found at {PROMPT_PATH}")
    raise

try:
    with open(SYS_INS_PATH, "r", encoding='utf-8') as f:
        sys_ins = f.read()
    logger.debug(f"Loaded sys_ins.txt ({len(sys_ins)} characters)")
except FileNotFoundError:
    logger.error(f"sys_ins.txt not found at {SYS_INS_PATH}")
    raise

def validate_pdf_content(pdf_bytes):
    """Validate PDF content efficiently"""
    if not pdf_bytes or len(pdf_bytes) < 1024:
        return False
    return pdf_bytes.startswith(b'%PDF-')

def validate_short_answer_with_ai(question, user_answer, expected_answer):
    """Simplified AI validation for short answers"""
    try:
        validation_prompt = f"""
Question: {question}
Expected: {expected_answer}
Student: {user_answer}

Evaluate if the student's answer is correct. Respond with JSON:
{{"is_correct": true/false, "explanation": "brief explanation"}}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            ),
            contents=[validation_prompt]
        )
        
        if not response.text:
            return None, "AI validation failed"
        
        validation_result = json.loads(response.text)
        is_correct = validation_result.get("is_correct", False)
        explanation = validation_result.get("explanation", "No explanation provided")
        
        return is_correct, explanation
        
    except Exception as e:
        logger.error(f"Error in AI validation: {e}")
        return None, f"AI validation error: {str(e)}"

def generate_course(file_content=None, file_url=None, status_callback=None):
    """Optimized course generation"""
    import time
    start_time = time.time()
    
    def update_status(message, progress=None):
        if status_callback:
            status_callback(message, progress)
        logger.info(message)
    
    pdf_bytes = None
    update_status("🚀 Starting course generation...", 5)
    
    # Handle file content
    if file_content:
        update_status("📄 Validating PDF file...", 10)
        if not validate_pdf_content(file_content):
            return None, "Invalid PDF file"
        pdf_bytes = file_content
        update_status("✅ PDF validated", 20)
    
    # Handle file URL
    elif file_url:
        update_status("🌐 Downloading PDF...", 10)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(file_url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            if not validate_pdf_content(resp.content):
                return None, "Invalid PDF from URL"
            
            pdf_bytes = resp.content
            update_status(f"✅ PDF downloaded ({len(pdf_bytes)} bytes)", 20)
            
        except requests.exceptions.Timeout:
            return None, "Request timed out"
        except requests.exceptions.ConnectionError:
            return None, "Connection error"
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP error {e.response.status_code}"
        except Exception as e:
            return None, f"Error fetching PDF: {e}"
    
    if not pdf_bytes:
        return None, "No PDF content provided"
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if len(pdf_bytes) > max_size:
        return None, f"PDF too large ({len(pdf_bytes)} bytes). Max: {max_size} bytes"
    
    # Analyze content
    update_status("📊 Analyzing PDF content...", 30)
    pdf_analysis = analyze_pdf_content(pdf_bytes)
    word_count = pdf_analysis['word_count']
    estimated_time = pdf_analysis['estimated_time']
    
    if word_count == 0:
        return None, "Could not extract text from PDF"
    
    if word_count > 15000:
        return None, f"PDF too long ({word_count:,} words). Max: 15,000 words"
    
    update_status(f"🤖 AI processing content... (Est: {estimated_time})", 45)
    
    try:
        # Generate content
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

        update_status("🧠 Processing AI response...", 80)
        
        if not response.text:
            return None, "Empty AI response"
        
        update_status("✅ Validating course structure...", 90)
        
        try:
            parsed = ActualApiResponse.model_validate_json(response.text)
            update_status("🎉 Course generated successfully!", 100)
            
            actual_time = time.time() - start_time
            logger.info(f"Course generated in {actual_time:.1f}s (Words: {word_count})")
            
            return parsed.root, None
            
        except ValidationError:
            try:
                raw_data = json.loads(response.text)
                update_status("🎉 Course generated successfully!", 100)
                return raw_data, None
            except json.JSONDecodeError:
                return None, "Failed to parse AI response"
        
    except Exception as e:
        actual_time = time.time() - start_time
        logger.error(f"Error after {actual_time:.1f}s: {e}")
        
        error_message = str(e)
        if "quota" in error_message.lower():
            error_message = "API quota exceeded"
        elif "api_key" in error_message.lower():
            error_message = "Invalid API key"
        elif "timeout" in error_message.lower():
            error_message = "Request timed out"
        
        return None, f"Error: {error_message}"

def extract_text_from_pdf(pdf_bytes):
    """Optimized PDF text extraction"""
    text = ""
    
    # Try pdfplumber first
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception:
        pass
    
    # Fallback to PyPDF2
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception:
        pass
    
    return text

def count_words_in_text(text):
    """Optimized word counting"""
    if not text:
        return 0
    
    # Simple word count - split by whitespace and filter short words
    words = text.split()
    meaningful_words = [w for w in words if len(w) > 2 and re.search(r'[a-zA-Z]', w)]
    return len(meaningful_words)

def estimate_generation_time(word_count):
    """Simplified time estimation"""
    if word_count < 500:
        return "15-25 seconds"
    elif word_count < 1500:
        return "20-35 seconds"
    elif word_count < 3000:
        return "35-55 seconds"
    elif word_count < 5000:
        return "50-75 seconds"
    elif word_count < 8000:
        return "1:15-1:45 minutes"
    elif word_count < 12000:
        return "1:45-2:30 minutes"
    else:
        return "2:30-3:30 minutes"

def analyze_pdf_content(pdf_bytes):
    """Optimized PDF analysis"""
    try:
        text = extract_text_from_pdf(pdf_bytes)
        word_count = count_words_in_text(text)
        estimated_time = estimate_generation_time(word_count)
        
        return {
            'word_count': word_count,
            'estimated_time': estimated_time,
            'text_length': len(text),
            'has_content': bool(text.strip())
        }
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        return {
            'word_count': 0,
            'estimated_time': "Unknown",
            'text_length': 0,
            'has_content': False
        }