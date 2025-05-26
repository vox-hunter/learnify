import logging
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
import os
import requests

from pydantic import BaseModel, Field, RootModel, ValidationError
from typing import Union, Optional, List, Dict, Any, Literal

DEBUG_MODE = True  # Set to True to enable debug logging

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

# Wrapper for response_model using Pydantic V2 RootModel
class SectionListWrapper(RootModel[List[Section]]):
    root: List[Section] # Explicitly define root for clarity, matches ActualApiResponse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Determine base directory for loading prompt and system instructions
BASE_DIR = os.path.dirname(__file__)
PROMPT_PATH = os.path.join(BASE_DIR, "prompt.txt")
SYS_INS_PATH = os.path.join(BASE_DIR, "sys_ins.txt")
with open(PROMPT_PATH, "r") as f:
    prompt = f.read()
with open(SYS_INS_PATH, "r") as f:
    sys_ins = f.read()
logger.debug(f"Loaded prompt.txt ({len(prompt)} characters)")
logger.debug(f"Loaded sys_ins.txt ({len(sys_ins)} characters)")

@app.post("/generate-course", response_model=SectionListWrapper)
async def generate_course(request: Request, file: UploadFile = File(None)):
    """Generate a course structure from an uploaded PDF or a PDF URL."""  # Updated docstring
    payload = {}
    file_url = None
    pdf_bytes = None

    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        if file:
            pdf_bytes = await file.read()
    elif "application/json" in content_type:
        try:
            payload = await request.json()
            file_url = payload.get("file_url")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if not pdf_bytes:
        if file_url:
            try:
                resp = requests.get(file_url)
                resp.raise_for_status()
                pdf_bytes = resp.content
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Unable to fetch PDF from URL: {e}")

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="No file or file_url provided, or an error occurred processing the input.")  # Updated error message

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
        raise HTTPException(status_code=500, detail="Empty response from model")
    try:
        parsed = ActualApiResponse.model_validate_json(response.text)
        return SectionListWrapper(parsed.root)
    except ValidationError as ve:
        logger.warning(f"Response schema validation failed: {ve}")
        return JSONResponse(content=json.loads(response.text))
    except json.JSONDecodeError:
        logger.error(f"Failed to parse AI response as JSON: {response.text[:200]}")
        raise HTTPException(status_code=500, detail="AI model did not return valid JSON.")