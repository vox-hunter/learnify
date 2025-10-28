"""
Chat Session Manager for AI Loom
Handles multi-turn conversations using Google Gemini SDK's chat API
"""

import logging
import uuid
import json
import re
import time
import hashlib
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from datetime import datetime, date
from gemini_client_factory import create_gemini_client

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ChatSessionManager:
    """
    Manages chat sessions using Gemini SDK's multi-turn chat functionality.
    No manual conversation history tracking needed - SDK handles it internally.
    
    Sessions are stored in a class-level store so they persist across manager instances.
    """
    
    # Class-level session store shared across all instances
    # session_id -> {'chat': chat_obj, 'client': client_obj, 'quota_source': str, 'username': str}
    _sessions: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, user_credentials: Optional[Dict[str, Any]] = None, 
                 username: Optional[str] = None,
                 quota_project_id: Optional[str] = None,
                 user_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize the chat session manager with Gemini client
        
        Args:
            user_credentials: Optional OAuth credentials dict for user quota
            username: Optional username for logging
            quota_project_id: Optional GCP project ID for quota billing
            user_profile: Optional user onboarding profile dict for personalization
        """
        # Store user credentials for creating clients per-session
        self.user_credentials = user_credentials
        self.username = username
        self.quota_project_id = quota_project_id
        self.user_profile = user_profile
        
        # Read model ID from environment with sensible default
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")  # Default to stable model
        logger.info(f"Using Gemini model: {self.model_id}")

        # Load system instruction from sys_ins.txt file (robust, non-fatal)
        sys_ins_path = os.path.join(os.path.dirname(__file__), 'sys_ins.txt')
        self.system_instruction = None
        try:
            if os.path.exists(sys_ins_path):
                with open(sys_ins_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Strip wrapping fenced code blocks if present (```...```) and any leading language tag
                content_str = content.strip()
                if content_str.startswith('```') and content_str.endswith('```'):
                    # remove the first fence line (may include a language tag) and the trailing fence
                    first_newline = content_str.find('\n')
                    if first_newline != -1:
                        inner = content_str[first_newline+1:-3].strip()
                    else:
                        inner = content_str[3:-3].strip()
                    self.system_instruction = inner
                else:
                    self.system_instruction = content_str

                logger.info("Loaded system instruction from sys_ins.txt")
            else:
                logger.warning(f"sys_ins.txt not found at {sys_ins_path}; using fallback instruction")
                self.system_instruction = "You are AI Loom, an educational AI assistant."
        except Exception as e:
            # Never allow failure to load the sys_ins file to crash the server
            logger.exception(f"Failed to load sys_ins.txt at {sys_ins_path}; using fallback. Error: {e}")
            self.system_instruction = "You are AI Loom, an educational AI assistant."

        # Inject user context if profile is provided
        if user_profile:
            self._inject_user_context()

        logger.info(f"ChatSessionManager initialized with model: {self.model_id}, user: {username or 'anonymous'}")

    def _sanitize_context_string(self, text: str, max_length: int = 200) -> str:
        """
        Sanitize user-provided context strings to prevent injection attacks.
        
        Args:
            text: Raw text from user profile
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string with limited length and no control characters
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Strip control characters and newlines
        sanitized = ''.join(char for char in text if char.isprintable() and char not in ['\n', '\r', '\t'])
        
        # Escape brackets to prevent prompt injection
        sanitized = sanitized.replace('[', '').replace(']', '')
        
        # Trim to max length
        sanitized = sanitized[:max_length].strip()
        
        return sanitized

    def _format_user_context(self) -> str:
        """
        Format user profile data into a readable context string for system instruction.
        
        Returns:
            Formatted context string or empty string if profile not available
        """
        if not self.user_profile:
            return ""
        
        try:
            context_parts = []
            profile = self.user_profile
            
            # Calculate age if date_of_birth is provided
            age_str = ""
            if profile.get('date_of_birth'):
                try:
                    dob_value = profile['date_of_birth']
                    dob_date = None
                    
                    # Handle different date_of_birth types from MongoDB
                    if isinstance(dob_value, datetime):
                        # datetime.datetime object - extract date component
                        dob_date = dob_value.date()
                    elif isinstance(dob_value, date):
                        # datetime.date object - use directly
                        dob_date = dob_value
                    elif isinstance(dob_value, str):
                        # String in ISO format - parse it
                        parsed_datetime = datetime.fromisoformat(dob_value)
                        dob_date = parsed_datetime.date()
                    
                    # Calculate age if we successfully obtained a date
                    if dob_date:
                        today = datetime.now().date()
                        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                        age_str = f"{age}-year-old "
                except (ValueError, TypeError, AttributeError):
                    logger.warning(f"Could not parse date_of_birth: {profile.get('date_of_birth')}")
            
            user_type = self._sanitize_context_string(profile.get('user_type', ''), max_length=20).lower()
            
            # Format based on user type
            if user_type == 'student':
                student_profile = profile.get('student_profile', {})
                year_level = self._sanitize_context_string(student_profile.get('year_level', ''), max_length=50)
                study_stage = self._sanitize_context_string(student_profile.get('study_stage', ''), max_length=50)
                exam_board = self._sanitize_context_string(student_profile.get('exam_board', ''), max_length=100)
                subjects = student_profile.get('subjects', [])
                learning_goals = student_profile.get('learning_goals', [])
                learning_style = self._sanitize_context_string(student_profile.get('learning_style', ''), max_length=50)
                course_name = self._sanitize_context_string(student_profile.get('course_name', ''), max_length=100)
                institution_name = self._sanitize_context_string(student_profile.get('institution_name', ''), max_length=150)
                
                context_parts.append(f"The user is a {age_str}student")
                
                if year_level:
                    context_parts.append(f"in {year_level}")
                if study_stage:
                    context_parts.append(f"studying {study_stage}")
                if exam_board:
                    context_parts.append(f"with {exam_board} exam board")
                    
                base_context = " ".join(context_parts) + "."
                context_parts = [base_context]
                
                if subjects and isinstance(subjects, list) and len(subjects) > 0:
                    # Sanitize and limit subjects
                    sanitized_subjects = [self._sanitize_context_string(s, max_length=50) for s in subjects[:10]]
                    subjects_str = ", ".join(filter(None, sanitized_subjects))
                    if subjects_str:
                        context_parts.append(f"They are taking {subjects_str}.")
                
                if learning_goals and isinstance(learning_goals, list) and len(learning_goals) > 0:
                    sanitized_goals = [self._sanitize_context_string(g, max_length=50) for g in learning_goals[:5]]
                    goals_str = ", ".join(filter(None, sanitized_goals))
                    if goals_str:
                        context_parts.append(f"Their learning goals include {goals_str}.")
                
                if learning_style:
                    context_parts.append(f"They prefer {learning_style} learning style.")
                
                if course_name or institution_name:
                    details = []
                    if course_name:
                        details.append(f"course: {course_name}")
                    if institution_name:
                        details.append(f"institution: {institution_name}")
                    context_parts.append(f"Additional details: {', '.join(details)}.")
                    
            elif user_type == 'educator':
                educator_profile = profile.get('educator_profile', {})
                subjects_taught = educator_profile.get('subjects_taught', [])
                stages_covered = educator_profile.get('stages_covered', [])
                exam_boards_covered = educator_profile.get('exam_boards_covered', [])
                use_cases = educator_profile.get('use_cases', [])
                institution_name = self._sanitize_context_string(educator_profile.get('institution_name', ''), max_length=150)
                class_size = educator_profile.get('class_size')
                
                context_parts.append("The user is an educator")
                
                if subjects_taught and isinstance(subjects_taught, list) and len(subjects_taught) > 0:
                    sanitized_subjects = [self._sanitize_context_string(s, max_length=50) for s in subjects_taught[:10]]
                    subjects_str = ", ".join(filter(None, sanitized_subjects))
                    if subjects_str:
                        context_parts.append(f"teaching {subjects_str}")
                
                if stages_covered and isinstance(stages_covered, list) and len(stages_covered) > 0:
                    sanitized_stages = [self._sanitize_context_string(s, max_length=30) for s in stages_covered[:10]]
                    stages_str = ", ".join(filter(None, sanitized_stages))
                    if stages_str:
                        context_parts.append(f"across {stages_str} stages")
                
                base_context = " ".join(context_parts) + "."
                context_parts = [base_context]
                
                if exam_boards_covered and isinstance(exam_boards_covered, list) and len(exam_boards_covered) > 0:
                    sanitized_boards = [self._sanitize_context_string(b, max_length=50) for b in exam_boards_covered[:10]]
                    boards_str = ", ".join(filter(None, sanitized_boards))
                    if boards_str:
                        context_parts.append(f"They cover {boards_str} exam boards.")
                
                if use_cases and isinstance(use_cases, list) and len(use_cases) > 0:
                    sanitized_use_cases = [self._sanitize_context_string(u, max_length=50) for u in use_cases[:10]]
                    use_cases_str = ", ".join(filter(None, sanitized_use_cases))
                    if use_cases_str:
                        context_parts.append(f"They use this system for {use_cases_str}.")
                
                if institution_name or class_size:
                    details = []
                    if institution_name:
                        details.append(f"institution: {institution_name}")
                    if class_size:
                        # Sanitize class_size (should be int or string)
                        safe_size = self._sanitize_context_string(str(class_size), max_length=20)
                        details.append(f"average class size: {safe_size}")
                    context_parts.append(f"Additional details: {', '.join(details)}.")
            else:
                context_parts.append(f"The user is a {age_str}user of the AI Loom platform.")
            
            # Add optional common fields (sanitized)
            if profile.get('user_intent'):
                intent = self._sanitize_context_string(profile['user_intent'], max_length=150)
                if intent:
                    context_parts.append(f"User intent: {intent}")
            if profile.get('tech_comfort_level'):
                level = self._sanitize_context_string(profile['tech_comfort_level'], max_length=30)
                if level:
                    context_parts.append(f"Technology comfort level: {level}.")
            if profile.get('ai_familiarity'):
                familiarity = self._sanitize_context_string(profile['ai_familiarity'], max_length=30)
                if familiarity:
                    context_parts.append(f"AI familiarity: {familiarity}.")
            
            # Add timezone and language preference if available (sanitized)
            context_parts.append("")
            details = []
            if profile.get('timezone'):
                tz = self._sanitize_context_string(profile['timezone'], max_length=50)
                if tz:
                    details.append(f"Timezone: {tz}")
            if profile.get('language_preference'):
                lang = self._sanitize_context_string(profile['language_preference'], max_length=20)
                if lang:
                    details.append(f"Language: {lang}")
            if details:
                context_parts.append(", ".join(details) + ".")
            
            formatted_context = " ".join(context_parts).strip()
            
            # Comment 21: Cap total context length to 1000 chars
            if len(formatted_context) > 1000:
                formatted_context = formatted_context[:1000]
                logger.warning(f"User context truncated to 1000 chars for {self.username}")
            
            return formatted_context
            
        except Exception as e:
            logger.warning(f"Error formatting user context: {e}")
            return ""
            
            # Format based on user type
            if user_type == 'student':
                student_profile = profile.get('student_profile', {})
                year_level = student_profile.get('year_level')
                study_stage = student_profile.get('study_stage')
                exam_board = student_profile.get('exam_board')
                subjects = student_profile.get('subjects', [])
                learning_goals = student_profile.get('learning_goals', [])
                learning_style = student_profile.get('learning_style')
                course_name = student_profile.get('course_name')
                institution_name = student_profile.get('institution_name')
                
                context_parts.append(f"The user is a {age_str}student")
                
                if year_level:
                    context_parts.append(f"in {year_level}")
                if study_stage:
                    context_parts.append(f"studying {study_stage}")
                if exam_board:
                    context_parts.append(f"with {exam_board} exam board")
                    
                base_context = " ".join(context_parts) + "."
                context_parts = [base_context]
                
                if subjects:
                    subjects_str = ", ".join(subjects) if isinstance(subjects, list) else subjects
                    context_parts.append(f"They are taking {subjects_str}.")
                
                if learning_goals:
                    goals_str = ", ".join(learning_goals) if isinstance(learning_goals, list) else learning_goals
                    context_parts.append(f"Their learning goals include {goals_str}.")
                
                if learning_style:
                    context_parts.append(f"They prefer {learning_style} learning style.")
                
                if course_name or institution_name:
                    details = []
                    if course_name:
                        details.append(f"course: {course_name}")
                    if institution_name:
                        details.append(f"institution: {institution_name}")
                    context_parts.append(f"Additional details: {', '.join(details)}.")
                    
            elif user_type == 'educator':
                educator_profile = profile.get('educator_profile', {})
                subjects_taught = educator_profile.get('subjects_taught', [])
                stages_covered = educator_profile.get('stages_covered', [])
                exam_boards_covered = educator_profile.get('exam_boards_covered', [])
                use_cases = educator_profile.get('use_cases', [])
                institution_name = educator_profile.get('institution_name')
                class_size = educator_profile.get('class_size')
                
                context_parts.append("The user is an educator")
                
                if subjects_taught:
                    subjects_str = ", ".join(subjects_taught) if isinstance(subjects_taught, list) else subjects_taught
                    context_parts.append(f"teaching {subjects_str}")
                
                if stages_covered:
                    stages_str = ", ".join(stages_covered) if isinstance(stages_covered, list) else stages_covered
                    context_parts.append(f"across {stages_str} stages")
                
                base_context = " ".join(context_parts) + "."
                context_parts = [base_context]
                
                if exam_boards_covered:
                    boards_str = ", ".join(exam_boards_covered) if isinstance(exam_boards_covered, list) else exam_boards_covered
                    context_parts.append(f"They cover {boards_str} exam boards.")
                
                if use_cases:
                    use_cases_str = ", ".join(use_cases) if isinstance(use_cases, list) else use_cases
                    context_parts.append(f"They use this system for {use_cases_str}.")
                
                if institution_name or class_size:
                    details = []
                    if institution_name:
                        details.append(f"institution: {institution_name}")
                    if class_size:
                        details.append(f"average class size: {class_size}")
                    context_parts.append(f"Additional details: {', '.join(details)}.")
            else:
                context_parts.append(f"The user is a {age_str}user of the AI Loom platform.")
            
            # Add optional common fields
            if profile.get('user_intent'):
                context_parts.append(f"User intent: {profile['user_intent']}")
            if profile.get('tech_comfort_level'):
                context_parts.append(f"Technology comfort level: {profile['tech_comfort_level']}.")
            if profile.get('ai_familiarity'):
                context_parts.append(f"AI familiarity: {profile['ai_familiarity']}.")
            
            # Add timezone and language preference if available
            context_parts.append("")
            details = []
            if profile.get('timezone'):
                details.append(f"Timezone: {profile['timezone']}")
            if profile.get('language_preference'):
                details.append(f"Language: {profile['language_preference']}")
            if details:
                context_parts.append(", ".join(details) + ".")
            
            formatted_context = " ".join(context_parts).strip()
            return formatted_context
            
        except Exception as e:
            logger.warning(f"Error formatting user context: {e}")
            return ""

    def _inject_user_context(self) -> None:
        """
        Inject formatted user context into system instruction.
        Appends personalization context to the base system instruction.
        """
        try:
            formatted_context = self._format_user_context()
            if formatted_context:
                separator = "\n\n---\n\nUSER CONTEXT:\n"
                usage_instruction = "\n\nUse this information to personalize your responses, adjust difficulty level, use relevant examples from their subjects, and align with their learning goals and style. Maintain an appropriate tone based on their age and educational level."
                self.system_instruction += separator + formatted_context + usage_instruction
                logger.info(f"User context injected for username: {self.username}")
            else:
                logger.info("No user context available for injection")
        except Exception as e:
            logger.warning(f"Failed to inject user context: {e}")


    def _determine_activity_type(self, message: str, file_data: Optional[bytes], url: Optional[str]) -> Dict[str, Any]:
        """
        Determine the type of AI activity based on the input
        
        Returns:
            Dict with activity type and message for frontend display
        """
        if file_data:
            if message and any(keyword in message.lower() for keyword in ['course', 'generate', 'create']):
                return {
                    'type': 'generating_course',
                    'message': '🎓 Generating course from uploaded file...',
                    'action': 'course_generation'
                }
            return {
                'type': 'processing_file',
                'message': '📄 Processing uploaded file...',
                'action': 'file_processing'
            }
        
        if url:
            return {
                'type': 'searching_web',
                'message': '🌐 Analyzing web content...',
                'action': 'web_search'
            }
        
        if message:
            lower_msg = message.lower()
            if any(keyword in lower_msg for keyword in ['flashcard', 'flash card', 'study cards', 'memorize']):
                return {
                    'type': 'generating_flashcard',
                    'message': '🃏 Generating flashcards...',
                    'action': 'flashcard_generation'
                }
            if any(keyword in lower_msg for keyword in ['course', 'generate', 'create', 'make']):
                return {
                    'type': 'generating_course',
                    'message': '🎓 Generating course content...',
                    'action': 'course_generation'
                }
            if any(keyword in lower_msg for keyword in ['search', 'find', 'look up']):
                return {
                    'type': 'searching_web',
                    'message': '🔍 Searching for information...',
                    'action': 'web_search'
                }
        
        return {
            'type': 'thinking',
            'message': '🧠 Thinking...',
            'action': 'general_processing'
        }

    def _create_search_required_tool(self) -> dict:
        """
        Create a function tool that returns whether web search is required.
        This allows the model to make a decision before committing to using built-in tools.
        """
        schema = {
            "type": "OBJECT",
            "properties": {
                "search_needed": {
                    "type": "BOOLEAN",
                    "description": "True if the query requires real-time web search or external URL context, False otherwise"
                },
                "reason": {
                    "type": "STRING",
                    "description": "Brief explanation of why search is or is not needed"
                }
            },
            "required": ["search_needed"]
        }
        return {
            "name": "search_required",
            "description": "Determines if the current query requires web search or URL context to answer properly. Returns true if search is needed, false if the knowledge base can handle it.",
            "arguments": types.Schema(type="OBJECT", properties=schema.get("properties"), required=schema.get("required"))
        }

    def _create_course_generation_tool(self) -> dict:
        """
        Create a FunctionDeclaration describing the `generate_course` function.
        The JSON schema uses Gemini's type system for compatibility with FunctionDeclaration validation.
        Note: Removed additionalProperties as Gemini SDK doesn't support it in function declarations.
        """
        schema = {
            "type": "OBJECT",
            "properties": {
                "course_title": {"type": "STRING", "description": "The title of the generated course"},
                "sections": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "section_title": {"type": "STRING"},
                            "explanation": {"type": "STRING"},
                            "quiz": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "type": {"type": "STRING", "description": "multiple_choice|true_false|short_answer|fill_in_the_blank|match"},
                                        "question": {"type": "STRING"},
                                        "options": {"type": "ARRAY", "items": {"type": "STRING"}},
                                        "answer": {"type": "STRING", "description": "The correct answer (can be a string, boolean, or JSON-formatted answer)"}
                                    },
                                    "required": ["type", "question", "answer"]
                                }
                            },
                            "subpoints": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "section_title": {"type": "STRING"},
                                        "explanation": {"type": "STRING"},
                                        "quiz": {
                                            "type": "ARRAY",
                                            "items": {
                                                "type": "OBJECT",
                                                "properties": {
                                                    "type": {"type": "STRING", "description": "multiple_choice|true_false|short_answer|fill_in_the_blank|match"},
                                                    "question": {"type": "STRING"},
                                                    "options": {"type": "ARRAY", "items": {"type": "STRING"}},
                                                    "answer": {"type": "STRING", "description": "The correct answer (can be a string, boolean, or JSON-formatted answer)"}
                                                },
                                                "required": ["type", "question", "answer"]
                                            }
                                        }
                                    },
                                    "required": ["section_title", "explanation", "quiz"]
                                }
                            }
                        },
                        "required": ["section_title", "explanation", "quiz"]
                    }
                }
            },
            "required": ["course_title", "sections"]
        }

        # Return plain dict declaration for compatibility with Gemini's FunctionDeclaration
        return {
            "name": "generate_course",
            "description": "Generate a structured course with title, sections, explanations, and quiz questions.",
            "arguments": schema
        }

    def _create_flashcard_generation_tool(self) -> dict:
        """
        Create a FunctionDeclaration describing the `generate_flashcard` function.
        The JSON schema uses Gemini's type system for compatibility with FunctionDeclaration validation.
        """
        schema = {
            "type": "OBJECT",
            "properties": {
                "flashcard_title": {
                    "type": "STRING",
                    "description": "The title of the flashcard set"
                },
                "cards": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "front": {
                                "type": "STRING",
                                "description": "Question or term (1-2 sentences)"
                            },
                            "back": {
                                "type": "STRING",
                                "description": "Answer or definition (2-4 sentences)"
                            },
                            "hint": {
                                "type": "STRING",
                                "description": "Optional hint to help learner recall"
                            },
                            "difficulty": {
                                "type": "STRING",
                                "description": "Optional difficulty level: easy|medium|hard"
                            },
                            "mastery_level": {
                                "type": "NUMBER",
                                "description": "Optional mastery level 0-5 for spaced repetition tracking"
                            }
                        },
                        "required": ["front", "back"]
                    }
                },
                "source_course_id": {
                    "type": "STRING",
                    "description": "Optional link to course ID if flashcards are generated from a course"
                }
            },
            "required": ["flashcard_title", "cards"]
        }

        return {
            "name": "generate_flashcard",
            "description": "Generate a structured flashcard set with title and cards for spaced repetition learning. Optionally link to source course.",
            "arguments": schema
        }

    def _process_function_call_result(self, chat, response, function_call, model_cls, type_label: str, session_id: str, activity_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Helper to process function call results (course or flashcard generation).
        
        Args:
            chat: Chat session object
            response: Initial AI response with function call
            function_call: The function call object
            model_cls: Pydantic model class for validation (ActualApiResponse or Flashcard)
            type_label: Label for logging ('course' or 'flashcard')
            session_id: Current session ID
            activity_info: Activity metadata for frontend
            
        Returns:
            Response dict if validation succeeds, None if it fails (falls back to legacy parsing)
        """
        tool_start = time.time()
        name = getattr(function_call, 'name', None) or (function_call.get('name') if isinstance(function_call, dict) else None)
        logger.info(f"[TOOL_CALL_START] function={name} session={session_id} user={self.username or 'guest'}")
        
        try:
            final_resp, extracted_data = self._handle_function_call(chat, response, function_call)
            tool_duration = time.time() - tool_start
            logger.info(f"[TOOL_CALL_SUCCESS] function={name} duration={tool_duration:.2f}s session={session_id}")
        except Exception as tool_error:
            tool_duration = time.time() - tool_start
            logger.error(f"[TOOL_CALL_FAILED] function={name} duration={tool_duration:.2f}s error={tool_error} session={session_id}")
            raise
        
        # Build reply_text from final_resp
        reply_text = ''
        if final_resp and hasattr(final_resp, 'text') and final_resp.text is not None:
            reply_text = final_resp.text
        elif final_resp and hasattr(final_resp, 'candidates') and final_resp.candidates:
            for p in getattr(final_resp.candidates[0].content, 'parts', []):
                if hasattr(p, 'text') and p.text is not None:
                    reply_text += p.text

        # Validate extracted data using Pydantic model
        is_valid = False
        validated_data = None
        validation_start = time.time()
        
        try:
            # Deep validation using Pydantic models
            validated_obj = model_cls.model_validate(extracted_data)
            is_valid = True
            validated_data = extracted_data
            validation_time = time.time() - validation_start
            title_key = 'course_title' if type_label == 'course' else 'flashcard_title'
            logger.info(f"✓ Deep validation passed for function-call {type_label}: {extracted_data.get(title_key)} (took {validation_time:.2f}s)")
        except Exception as validation_error:
            validation_time = time.time() - validation_start
            logger.warning(f"Function call {type_label} validation failed (took {validation_time:.2f}s): {validation_error}; falling back to legacy parsing")
            return None  # Signal to fall through to legacy parsing
            
        if is_valid:
            # Build response dict based on type
            # For structured data (course/flashcard), provide clean reply instead of raw JSON
            if type_label == 'course':
                clean_reply = f"I've generated a course titled \"{validated_data.get('course_title', 'Untitled Course')}\" with {len(validated_data.get('sections', []))} sections."
                return {
                    'success': True,
                    'reply': clean_reply,
                    'session_id': session_id,
                    'is_course': True,
                    'course_data': validated_data,
                    'course_detection_source': 'function_call',
                    'activity_info': activity_info
                }
            else:  # flashcard
                card_count = len(validated_data.get('cards', []))
                clean_reply = f"I've generated {card_count} flashcard{'' if card_count == 1 else 's'} titled \"{validated_data.get('flashcard_title', 'Untitled Flashcard Set')}\"."
                return {
                    'success': True,
                    'reply': clean_reply,
                    'session_id': session_id,
                    'is_flashcard': True,
                    'flashcard_data': validated_data,
                    'flashcard_detection_source': 'function_call',
                    'activity_info': activity_info
                }
        
        return None

    def _build_function_only_tools(self) -> list:
        """
        Build only function tools (search_required, course, flashcard).
        No built-in tools (Google Search, URL Context) are included.
        """
        try:
            search_tool_dict = self._create_search_required_tool()
            course_tool_dict = self._create_course_generation_tool()
            flashcard_tool_dict = self._create_flashcard_generation_tool()
            
            # Build FunctionDeclarations
            search_func_decl = types.FunctionDeclaration(
                name=search_tool_dict["name"],
                description=search_tool_dict["description"],
                parameters=search_tool_dict["arguments"]
            )
            
            course_func_decl = types.FunctionDeclaration(
                name=course_tool_dict["name"],
                description=course_tool_dict["description"],
                parameters=course_tool_dict["arguments"]
            )
            
            flashcard_func_decl = types.FunctionDeclaration(
                name=flashcard_tool_dict["name"],
                description=flashcard_tool_dict["description"],
                parameters=flashcard_tool_dict["arguments"]
            )
            
            # Wrap all in single Tool with multiple function declarations
            function_tool = types.Tool(function_declarations=[
                search_func_decl,
                course_func_decl,
                flashcard_func_decl
            ])
            
            logger.info("Built function-only tools: search_required, course generation, flashcard generation")
            return [function_tool]
        except Exception as e:
            logger.warning(f"Failed to create function-only tools: {e}")
            return []
    
    def _build_builtin_only_tools(self) -> list:
        """
        Build only built-in tools (Google Search, URL Context).
        No function tools are included.
        """
        try:
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            url_context_tool = types.Tool(url_context=types.UrlContext())
            
            logger.info("Built built-in-only tools: Google Search, URL Context")
            return [google_search_tool, url_context_tool]
        except Exception as e:
            logger.warning(f"Failed to create built-in-only tools: {e}")
            return []

    def create_session(self, system_instruction: Optional[str] = None, use_builtin_tools: bool = False) -> tuple[str, Any]:
        """
        Create a new chat session using Gemini SDK's chat.create()
        
        Args:
            system_instruction: Optional system instruction to guide the chat behavior
            use_builtin_tools: If True, use built-in tools (search, URL context). If False, use function tools only.
            
        Returns:
            tuple: (session_id, chat_object)
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create Gemini client using factory (OAuth with user quota or API key fallback)
        client, quota_metadata = create_gemini_client(
            user_credentials=self.user_credentials,
            quota_project_id=self.quota_project_id,
            username=self.username
        )
        
        quota_source = quota_metadata.get('quota_source', 'unknown')
        logger.info(f"Created chat session {session_id} using quota_source={quota_source}, user={self.username or 'anonymous'}")
        
        # Configure chat with appropriate tools
        # Dual-mode strategy: Start with function tools, switch to built-in tools if search is needed
        try:
            if use_builtin_tools:
                tools_list = self._build_builtin_only_tools()
                logger.info("Initialized chat session with built-in tools only (Google Search, URL Context)")
            else:
                tools_list = self._build_function_only_tools()
                logger.info("Initialized chat session with function tools only (search_required, course generation, flashcard generation)")
        except Exception as e:
            # If building the tools fails for any reason, use no tools (rely on JSON parsing)
            logger.warning(f"Failed to create tools: {e}; falling back to no tools (JSON parsing only)")
            tools_list = []

        config = types.GenerateContentConfig(
            system_instruction=system_instruction or self.system_instruction,
            tools=tools_list,
            temperature=1,  # Balanced creativity and consistency
        )
        
        # Create chat session using Gemini SDK
        # The SDK manages conversation history automatically
        chat = client.chats.create(
            model=self.model_id,
            config=config
        )
        
        # Store chat object, client, and quota metadata in session store
        # Also track whether this session uses built-in tools
        ChatSessionManager._sessions[session_id] = {
            'chat': chat,
            'client': client,
            'quota_source': quota_source,
            'username': self.username,
            'use_builtin_tools': use_builtin_tools
        }
        
        logger.info(f"Created new chat session: {session_id} (builtin_tools={use_builtin_tools})")
        return session_id, chat
    
    def get_session(self, session_id: str) -> Optional[Any]:
        """
        Retrieve an existing chat session
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            Chat object if found, None otherwise
        """
        session_data = ChatSessionManager._sessions.get(session_id)
        if session_data:
            return session_data.get('chat')
        return None
    
    def _extract_grounding_metadata(self, response) -> Dict[str, Any]:
        """
        Extract grounding metadata (Google Search results and URL context) from response.
        
        Args:
            response: The Gemini API response object
            
        Returns:
            Dict with grounding metadata or empty dict if not present
        """
        grounding_info = {}
        
        try:
            # Check for grounding metadata from Google Search
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Extract grounding metadata (Google Search results with citations)
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    gm = candidate.grounding_metadata
                    grounding_info['search_queries'] = getattr(gm, 'web_search_queries', [])
                    grounding_info['grounding_chunks'] = []
                    
                    # Extract source chunks (URLs and titles)
                    if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                        for chunk in gm.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                grounding_info['grounding_chunks'].append({
                                    'uri': getattr(chunk.web, 'uri', ''),
                                    'title': getattr(chunk.web, 'title', '')
                                })
                    
                    grounding_info['grounding_supports'] = []
                    # Extract support segments linking text to sources
                    if hasattr(gm, 'grounding_supports') and gm.grounding_supports:
                        for support in gm.grounding_supports:
                            support_info = {}
                            if hasattr(support, 'segment'):
                                support_info['text'] = getattr(support.segment, 'text', '')
                                support_info['start_index'] = getattr(support.segment, 'start_index', 0)
                                support_info['end_index'] = getattr(support.segment, 'end_index', 0)
                            support_info['chunk_indices'] = getattr(support, 'grounding_chunk_indices', [])
                            grounding_info['grounding_supports'].append(support_info)
                    
                    logger.info(f"Extracted grounding metadata: {len(grounding_info.get('grounding_chunks', []))} sources found")
                
                # Extract URL context metadata
                if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
                    ucm = candidate.url_context_metadata
                    grounding_info['url_context'] = []
                    
                    if hasattr(ucm, 'url_metadata') and ucm.url_metadata:
                        for url_info in ucm.url_metadata:
                            grounding_info['url_context'].append({
                                'url': getattr(url_info, 'retrieved_url', ''),
                                'status': getattr(url_info, 'url_retrieval_status', 'UNKNOWN')
                            })
                    
                    logger.info(f"Extracted URL context metadata: {len(grounding_info.get('url_context', []))} URLs retrieved")
        
        except Exception as e:
            logger.warning(f"Error extracting grounding metadata: {e}")
        
        return grounding_info
    
    def send_message(
        self,
        session_id: Optional[str],
        message: str,
        file_data: Optional[bytes] = None,
        file_mime_type: Optional[str] = None,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the chat session with optional file or URL context.
        
        This is the non-streaming (blocking) method that returns a complete response.
        For streaming responses, use send_message_stream() instead.
        
        Args:
            session_id: Existing session ID or None to create new session
            message: User's text message
            file_data: Optional file content as bytes
            file_mime_type: MIME type of the file (required if file_data provided)
            url: Optional URL for the AI to fetch context from
            
        Returns:
            dict: {
                'success': bool,
                'reply': str,
                'session_id': str,
                'error': Optional[str]
            }
        """
        # Determine activity type for frontend indicators
        activity_info = self._determine_activity_type(message, file_data, url)
        logger.info(f"[ACTIVITY_START] type={activity_info['type']} action={activity_info['action']} session={session_id}")
        
        try:
            # Get or create chat session
            if session_id:
                chat = self.get_session(session_id)
                if not chat:
                    logger.warning(f"Session {session_id} not found, creating new session")
                    session_id, chat = self.create_session()
            else:
                session_id, chat = self.create_session()
            
            # Prepare message content
            # The Gemini SDK accepts a list of parts that can include text, files, and URLs
            content_parts = []
            
            # Add text message
            if message:
                content_parts.append(message)
            elif file_data:
                # Add simple context when only file is provided
                content_parts.append("User uploaded a file")
            
            # Add file if provided
            # Files are sent as bytes to the Gemini API
            if file_data and file_mime_type:
                logger.info(f"Including file in message (MIME: {file_mime_type}, size: {len(file_data)} bytes)")
                # Upload file to Gemini File API for processing
                file_part = types.Part.from_bytes(
                    data=file_data,
                    mime_type=file_mime_type
                )
                content_parts.append(file_part)
                
                # Add guard for file uploads without explicit course generation request
                if message and not any(keyword in message.lower() for keyword in ['generate', 'create', 'course', 'make']):
                    content_parts.append("\n\nNote: If you want a course generated from this file, please confirm or ask explicitly.")
            
            # Add URL if provided
            # The URL context tool will automatically fetch the content
            if url:
                logger.info(f"Including URL in message: {url}")
                # Simply mention the URL in the message - the url_context tool handles fetching
                content_parts.append(f"\n\nPlease analyze this URL: {url}")
            
            # Send message to chat using SDK's send_message()
            # The SDK handles conversation history automatically
            logger.info(f"Sending message to session {session_id}")
            response = chat.send_message(content_parts)

            # --- Function calling support: detect if model requested a function call ---
            try:
                if hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                    for part in getattr(response.candidates[0].content, 'parts', []):
                        function_call = getattr(part, 'function_call', None)
                        # Some SDKs represent function_call as dict
                        if not function_call and isinstance(part, dict):
                            function_call = part.get('function_call')
                        if function_call:
                            name = getattr(function_call, 'name', None) or (function_call.get('name') if isinstance(function_call, dict) else None)
                            if name == 'generate_course':
                                from local_backend import ActualApiResponse
                                result = self._process_function_call_result(
                                    chat, response, function_call, 
                                    ActualApiResponse, 'course', 
                                    session_id, activity_info
                                )
                                if result:
                                    return result
                                # If None returned, fall through to legacy parsing
                            elif name == 'generate_flashcard':
                                from local_backend import Flashcard
                                result = self._process_function_call_result(
                                    chat, response, function_call, 
                                    Flashcard, 'flashcard', 
                                    session_id, activity_info
                                )
                                if result:
                                    logger.info(f"[DEBUG] Returning flashcard result: is_flashcard={result.get('is_flashcard')}, has_data={bool(result.get('flashcard_data'))}")
                                    return result
                                # If None returned, fall through to legacy parsing
            except Exception:
                # If function-call handling fails, continue to legacy parsing below
                logger.exception("Function-call handling failed; falling back to legacy parsing")
            
            # Extract reply text from response

            reply_text = ""
            if hasattr(response, 'text') and response.text is not None:
                reply_text = response.text
            elif hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                for part in getattr(response.candidates[0].content, 'parts', []):
                    if hasattr(part, 'text') and part.text is not None:
                        reply_text += part.text

            # Ensure reply_text is a string
            if not isinstance(reply_text, str) or not reply_text:
                logger.error("AI response did not return any text. reply_text is None or empty.")
                reply_text = ""
            
            # Extract grounding metadata (Google Search and URL context)
            grounding_metadata = self._extract_grounding_metadata(response)

            # Try to extract JSON course or flashcard payload from the reply (search anywhere)
            is_json = False
            course_data = None
            is_flashcard = False
            flashcard_data = None
            json_text = None

            # 1) Look for fenced code blocks anywhere: ```json ... ``` or ``` ... ```
            m = re.search(r"```(?:json)?\s*(.*?)\s*```", reply_text or "", re.DOTALL | re.IGNORECASE)
            if m:
                json_text = m.group(1).strip()
                logger.info("Found fenced code block candidate for JSON")

            # 2) If none, look for HTML <pre> or <code> blocks
            if not json_text:
                m = re.search(r"<pre[^>]*>(.*?)</pre>", reply_text or "", re.DOTALL | re.IGNORECASE)
                if m:
                    json_text = m.group(1).strip()
                    logger.info("Found <pre> block candidate for JSON")
            if not json_text:
                m = re.search(r"<code[^>]*>(.*?)</code>", reply_text or "", re.DOTALL | re.IGNORECASE)
                if m:
                    json_text = m.group(1).strip()
                    logger.info("Found <code> block candidate for JSON")

            # 3) If still none, attempt to extract the first balanced-brace JSON substring
            if not json_text and reply_text:
                start = reply_text.find('{')
                if start != -1:
                    depth = 0
                    i = start
                    while i < len(reply_text):
                        ch = reply_text[i]
                        if ch == '{':
                            depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                json_text = reply_text[start:i+1].strip()
                                logger.info("Found balanced-brace candidate for JSON")
                                break
                        i += 1

            # Debug: log preview
            logger.info(f"Response preview: {(reply_text or '')[:200]}...")

            # If we have a candidate json_text, try to clean common issues and parse
            if json_text:
                # Remove leading/trailing fences or language markers (e.g., 'json') already stripped above
                # Fix common JSON issues from AI responses: remove trailing commas before ] or }
                cleaned = re.sub(r',(\s*[}\]])', r'\1', json_text)
                # Remove any Markdown code ticks inside
                cleaned = cleaned.replace('`', '')
                try:
                    parsed_json = json.loads(cleaned)
                    if isinstance(parsed_json, dict) and 'course_title' in parsed_json and 'sections' in parsed_json:
                        is_json = True
                        course_data = parsed_json
                        logger.info(f"✓ Detected course JSON response: {parsed_json.get('course_title')}")
                        # Add detection source for logging
                        course_detection_source = 'json_parse'
                        
                        # Print the entire course JSON for debugging
                        logger.info("=" * 80)
                        logger.info("FULL COURSE JSON:")
                        logger.info("=" * 80)
                        formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                        logger.info(formatted_json)
                        logger.info("=" * 80)
                    elif isinstance(parsed_json, dict) and 'flashcard_title' in parsed_json and 'cards' in parsed_json:
                        # Flashcard JSON detected
                        is_flashcard = True
                        flashcard_data = parsed_json
                        logger.info(f"✓ Detected flashcard JSON response: {parsed_json.get('flashcard_title')}")
                        # Add detection source for logging
                        flashcard_detection_source = 'json_parse'
                        
                        # Print the entire flashcard JSON for debugging
                        logger.info("=" * 80)
                        logger.info("FULL FLASHCARD JSON:")
                        logger.info("=" * 80)
                        formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                        logger.info(formatted_json)
                        logger.info("=" * 80)
                    else:
                        logger.info("JSON parsed but missing course or flashcard structure keys")
                except Exception as e:
                    logger.info(f"Candidate JSON parse failed: {str(e)[:200]}")

            # If no valid JSON was found, run redaction to avoid leaking system prompts
            if not is_json:
                try:
                    preview_lower = (reply_text or '').lower()
                    leaked = False

                    # If the model echoed an explicit request to show system instructions
                    if 'here are my full system instructions' in preview_lower or 'okay, here are my full system instructions' in preview_lower:
                        leaked = True

                    # If the reply contains a large substring of the system instruction, treat as leak
                    if not leaked and self.system_instruction:
                        si = self.system_instruction.strip()
                        if len(si) > 100 and si[:100].lower() in preview_lower:
                            leaked = True
                    
                    # Comment 13: Check for USER CONTEXT block leak
                    if not leaked and 'user context:' in preview_lower:
                        # Check if the banner or section is exposed
                        if '---' in reply_text and 'user context' in preview_lower:
                            leaked = True

                    if leaked:
                        logger.warning(f"Detected potential system-instruction leak from session {session_id}; redacting reply")
                        reply_text = "I'm sorry — I can't share internal system instructions or tool definitions. How can I help instead?"
                except Exception:
                    # Don't let redaction errors break flow
                    pass
            
            return {
                'success': True,
                'reply': reply_text,
                'session_id': session_id,
                'is_course': is_json,
                'course_data': course_data,
                'course_detection_source': locals().get('course_detection_source', 'none'),
                'is_flashcard': is_flashcard,
                'flashcard_data': flashcard_data,
                'flashcard_detection_source': locals().get('flashcard_detection_source', 'none'),
                'activity_info': activity_info,
                'grounding_metadata': grounding_metadata  # Include search results and URL context
            }
            
        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'reply': '',
                'session_id': session_id or '',
                'error': str(e),
                'activity_info': locals().get('activity_info', {'type': 'error', 'message': 'Error occurred', 'action': 'error'})
            }
    
    def send_message_stream(
        self,
        session_id: Optional[str],
        message: str,
        file_data: Optional[bytes] = None,
        file_mime_type: Optional[str] = None,
        url: Optional[str] = None
    ):
        """
        Stream a message to the chat session with optional file or URL context.
        
        This method yields events incrementally as the AI generates the response,
        enabling real-time streaming to the frontend via Server-Sent Events (SSE).
        
        Args:
            session_id: Existing session ID or None to create new session
            message: User's text message
            file_data: Optional file content as bytes
            file_mime_type: MIME type of the file (required if file_data provided)
            url: Optional URL for the AI to fetch context from
            
        Yields:
            Dict events with the following types:
            - {'type': 'status', 'activity_type': str, 'message': str, 'action': str}
            - {'type': 'chunk', 'text': str, 'session_id': str}
            - {'type': 'course', 'data': dict}
            - {'type': 'flashcard', 'data': dict}
            - {'type': 'complete', 'session_id': str}
            - {'type': 'error', 'error': str, 'session_id': str}
        """
        from typing import Generator
        
        # Determine activity type for frontend indicators
        activity_info = self._determine_activity_type(message, file_data, url)
        logger.info(f"[ACTIVITY_START_STREAM] type={activity_info['type']} action={activity_info['action']} session={session_id}")
        
        # Yield initial status event
        yield {
            'type': 'status',
            'activity_type': activity_info['type'],
            'message': activity_info['message'],
            'action': activity_info['action']
        }
        
        try:
            # Get or create chat session with validation logging
            if session_id:
                logger.info(f"Attempting to retrieve existing session: {session_id}")
                chat = self.get_session(session_id)
                if not chat:
                    logger.warning(f"Session {session_id} not found in store (keys: {list(self._sessions.keys())}), creating new session")
                    session_id, chat = self.create_session()
                else:
                    logger.info(f"Successfully retrieved session {session_id}")
            else:
                logger.info("No session_id provided, creating new session")
                session_id, chat = self.create_session()
            
            # Prepare message content (same as send_message)
            content_parts = []
            
            # Add text message
            if message:
                content_parts.append(message)
            elif file_data:
                content_parts.append("User uploaded a file")
            
            # Add file if provided
            if file_data and file_mime_type:
                logger.info(f"Including file in streaming message (MIME: {file_mime_type}, size: {len(file_data)} bytes)")
                file_part = types.Part.from_bytes(
                    data=file_data,
                    mime_type=file_mime_type
                )
                content_parts.append(file_part)
                
                if message and not any(keyword in message.lower() for keyword in ['generate', 'create', 'course', 'make']):
                    content_parts.append("\n\nNote: If you want a course generated from this file, please confirm or ask explicitly.")
            
            # Add URL if provided
            if url:
                logger.info(f"Including URL in streaming message: {url}")
                content_parts.append(f"\n\nPlease analyze this URL: {url}")
            
            # Stream the response using Gemini SDK's send_message_stream
            logger.info(f"Starting streaming for session {session_id}")
            
            # Accumulate response text for post-processing
            accumulated_text = ""
            final_chunk = None
            chunk_count = 0
            sequence_number = 0
            
            # Iterate over streaming chunks
            for chunk in chat.send_message_stream(content_parts):
                chunk_count += 1
                if chunk_count % 10 == 0:
                    logger.debug(f"Streamed {chunk_count} chunks for session {session_id}")
                    
                final_chunk = chunk  # Keep reference to final chunk for function call detection
                
                # Extract text from chunk
                chunk_text = ""
                if hasattr(chunk, 'text') and chunk.text is not None:
                    chunk_text = chunk.text
                elif hasattr(chunk, 'candidates') and chunk.candidates and len(chunk.candidates) > 0:
                    for part in getattr(chunk.candidates[0].content, 'parts', []):
                        if hasattr(part, 'text') and part.text is not None:
                            chunk_text += part.text
                
                # Accumulate text for later processing
                if chunk_text:
                    accumulated_text += chunk_text
                    sequence_number += 1
                    
                    # Yield text chunk event with sequence number for deduplication
                    yield {
                        'type': 'chunk',
                        'text': chunk_text,
                        'seq': sequence_number,
                        'session_id': session_id
                    }
            
            # After streaming completes, check for function calls in the final chunk
            function_call_handled = False
            search_required_result = False
            
            if final_chunk and hasattr(final_chunk, 'candidates') and final_chunk.candidates and len(final_chunk.candidates) > 0:
                for part in getattr(final_chunk.candidates[0].content, 'parts', []):
                    function_call = getattr(part, 'function_call', None)
                    if not function_call and isinstance(part, dict):
                        function_call = part.get('function_call')
                    
                    if function_call:
                        name = getattr(function_call, 'name', None) or (function_call.get('name') if isinstance(function_call, dict) else None)
                        
                        # PRIORITY 1: Check if search_required returned True
                        if name == 'search_required':
                            try:
                                # Extract the search_needed argument
                                raw_args = getattr(function_call, 'args', None) or getattr(function_call, 'arguments', None)
                                if isinstance(raw_args, str):
                                    args_obj = json.loads(raw_args)
                                else:
                                    args_obj = raw_args or {}
                                
                                search_required_result = args_obj.get('search_needed', False)
                                logger.info(f"[SEARCH_DETECTION] search_required returned: {search_required_result}")
                                
                                if search_required_result:
                                    logger.info(f"[SEARCH_SWITCH] Switching to built-in tools mode for session {session_id}")
                                    # Mark that we need to regenerate with built-in tools
                                    # Store the current session state to switch modes
                                    ChatSessionManager._sessions[session_id]['use_builtin_tools'] = True
                            except Exception as e:
                                logger.warning(f"Error parsing search_required result: {e}")
                        
                        # PRIORITY 2: Handle course generation
                        elif name == 'generate_course':
                            try:
                                from local_backend import ActualApiResponse
                                
                                # Handle function call
                                final_resp, extracted_data = self._handle_function_call(chat, final_chunk, function_call)
                                
                                # Validate using Pydantic
                                try:
                                    validated_obj = ActualApiResponse.model_validate(extracted_data)
                                    
                                    # Generate idempotency ID for function call result
                                    idempotency_id = hashlib.sha256(
                                        json.dumps({
                                            'type': 'course',
                                            'title': extracted_data.get('course_title'),
                                            'section_count': len(extracted_data.get('sections', []))
                                        }, sort_keys=True).encode()
                                    ).hexdigest()[:12]
                                    
                                    # Yield course data event with idempotency ID
                                    yield {
                                        'type': 'course',
                                        'data': extracted_data,
                                        'idempotency_id': idempotency_id
                                    }
                                    
                                    # Yield model's final response text if available
                                    if final_resp and hasattr(final_resp, 'text') and final_resp.text:
                                        yield {
                                            'type': 'chunk',
                                            'text': final_resp.text,
                                            'session_id': session_id
                                        }
                                    
                                    function_call_handled = True
                                    logger.info(f"✓ Streamed course data: {extracted_data.get('course_title')}")
                                except Exception as validation_error:
                                    logger.warning(f"Course validation failed during streaming: {validation_error}")
                            except Exception as e:
                                logger.error(f"Error handling course function call in stream: {e}", exc_info=True)
                        
                        # PRIORITY 3: Handle flashcard generation
                        elif name == 'generate_flashcard':
                            try:
                                from local_backend import Flashcard
                                
                                # Handle function call
                                final_resp, extracted_data = self._handle_function_call(chat, final_chunk, function_call)
                                
                                # Validate using Pydantic
                                try:
                                    validated_obj = Flashcard.model_validate(extracted_data)
                                    
                                    # Generate idempotency ID for function call result
                                    idempotency_id = hashlib.sha256(
                                        json.dumps({
                                            'type': 'flashcard',
                                            'title': extracted_data.get('flashcard_title'),
                                            'card_count': len(extracted_data.get('cards', []))
                                        }, sort_keys=True).encode()
                                    ).hexdigest()[:12]
                                    
                                    # Yield flashcard data event with idempotency ID
                                    yield {
                                        'type': 'flashcard',
                                        'data': extracted_data,
                                        'idempotency_id': idempotency_id
                                    }
                                    
                                    # Yield model's final response text if available
                                    if final_resp and hasattr(final_resp, 'text') and final_resp.text:
                                        yield {
                                            'type': 'chunk',
                                            'text': final_resp.text,
                                            'session_id': session_id
                                        }
                                    
                                    function_call_handled = True
                                    logger.info(f"✓ Streamed flashcard data: {extracted_data.get('flashcard_title')}")
                                except Exception as validation_error:
                                    logger.warning(f"Flashcard validation failed during streaming: {validation_error}")
                            except Exception as e:
                                logger.error(f"Error handling flashcard function call in stream: {e}", exc_info=True)
            
            # REGENERATION LOGIC: If search_required returned True, regenerate with built-in tools
            if search_required_result and not function_call_handled:
                logger.info(f"[REGENERATE_WITH_SEARCH] Regenerating response with built-in tools for session {session_id}")
                yield {
                    'type': 'status',
                    'activity_type': 'searching_web',
                    'message': '🌐 Searching for information...',
                    'action': 'web_search'
                }
                
                try:
                    # Get the existing chat session and switch it to use built-in tools
                    session_data = ChatSessionManager._sessions.get(session_id)
                    if session_data:
                        old_chat = session_data['chat']
                        
                        # Create a new chat session with built-in tools enabled
                        new_session_id, new_chat = self.create_session(system_instruction=self.system_instruction, use_builtin_tools=True)
                        
                        # Copy conversation history from old chat to new chat
                        # Send the same content_parts through the new chat with built-in tools
                        logger.info(f"[SEARCH_REGENERATE] Streaming response with built-in tools")
                        
                        chunk_count_search = 0
                        search_accumulated_text = ""
                        
                        for search_chunk in new_chat.send_message_stream(content_parts):
                            chunk_count_search += 1
                            
                            # Extract text from chunk
                            chunk_text = ""
                            if hasattr(search_chunk, 'text') and search_chunk.text is not None:
                                chunk_text = search_chunk.text
                            elif hasattr(search_chunk, 'candidates') and search_chunk.candidates and len(search_chunk.candidates) > 0:
                                for part in getattr(search_chunk.candidates[0].content, 'parts', []):
                                    if hasattr(part, 'text') and part.text is not None:
                                        chunk_text += part.text
                            
                            # Yield text chunks from search-enabled response
                            if chunk_text:
                                search_accumulated_text += chunk_text
                                yield {
                                    'type': 'chunk',
                                    'text': chunk_text,
                                    'session_id': session_id  # Keep original session ID for frontend
                                }
                        
                        # Extract grounding metadata from search response
                        grounding_metadata_search = self._extract_grounding_metadata(search_chunk) if 'search_chunk' in locals() else {}
                        
                        # Update session to use the new built-in-tools-enabled chat
                        ChatSessionManager._sessions[session_id]['chat'] = new_chat
                        
                        logger.info(f"[REGENERATE_COMPLETE] Regenerated with search, {chunk_count_search} chunks streamed")
                except Exception as e:
                    logger.error(f"Error during search regeneration: {e}", exc_info=True)
                    yield {
                        'type': 'error',
                        'error': f'Failed to regenerate with search: {str(e)}',
                        'session_id': session_id
                    }
            
            # Legacy JSON parsing is DISABLED - only use proper function calls
            # (Previously tried to parse JSON from streamed text, but this was causing
            # false positives when AI discussed course/flashcard structures)
            
            # Apply redaction check (same as send_message)
            if accumulated_text:
                try:
                    preview_lower = accumulated_text.lower()
                    leaked = False
                    
                    if 'here are my full system instructions' in preview_lower or 'okay, here are my full system instructions' in preview_lower:
                        leaked = True
                    
                    if not leaked and self.system_instruction:
                        si = self.system_instruction.strip()
                        if len(si) > 100 and si[:100].lower() in preview_lower:
                            leaked = True
                    
                    if leaked:
                        logger.warning(f"Detected potential system-instruction leak in streaming session {session_id}; redacting")
                        # Note: In streaming mode, text was already sent. Log warning for monitoring.
                
                except Exception:
                    pass
            
            # Yield completion event
            # Extract grounding metadata from the final chunk
            grounding_metadata = self._extract_grounding_metadata(final_chunk)
            
            yield {
                'type': 'complete',
                'session_id': session_id,
                'grounding_metadata': grounding_metadata  # Include search results and URL context
            }
            
            logger.info(f"[ACTIVITY_COMPLETE_STREAM] session={session_id}, chunks_sent={chunk_count}")
        
        except Exception as e:
            # Classify error type
            error_str = str(e)
            error_type = "internal_error"
            retriable = True
            
            # Classify specific error types
            if "quota" in error_str.lower() or "rate limit" in error_str.lower():
                error_type = "quota_exceeded"
                retriable = False
            elif "authentication" in error_str.lower() or "credentials" in error_str.lower():
                error_type = "auth_error"
                retriable = False
            elif "timeout" in error_str.lower():
                error_type = "timeout"
                retriable = True
            
            logger.error(f"Error in send_message_stream (type={error_type}, retriable={retriable}, session={session_id}): {error_str}", exc_info=True)
            yield {
                'type': 'error',
                'error': error_str,
                'error_type': error_type,
                'retriable': retriable,
                'session_id': session_id or ''
            }
    
    def get_history(self, session_id: str) -> Optional[list]:
        """
        Get conversation history for a session
        
        Args:
            session_id: The session identifier
            
        Returns:
            List of messages if session exists, None otherwise
        """
        chat = self.get_session(session_id)
        if not chat:
            return None
        
        try:
            # Get history using SDK's get_history() method
            history = chat.get_history()
            return history
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in ChatSessionManager._sessions:
            del ChatSessionManager._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def _handle_function_call(self, chat, initial_response, function_call) -> tuple:
        """
        Handle a function_call emitted by the model.

        Steps:
        - Extract arguments from the function_call
        - Construct a FunctionResponse and send it back as tool output
        - Return the final model response and the extracted course dict
        """
        try:
            # Extract function name and args robustly
            name = getattr(function_call, 'name', None) or (function_call.get('name') if isinstance(function_call, dict) else None)
            raw_args = None
            if hasattr(function_call, 'args'):
                raw_args = getattr(function_call, 'args')
            elif hasattr(function_call, 'arguments'):
                raw_args = getattr(function_call, 'arguments')
            elif isinstance(function_call, dict):
                raw_args = function_call.get('args') or function_call.get('arguments')

            args_obj = None
            if isinstance(raw_args, str):
                try:
                    args_obj = json.loads(raw_args)
                except Exception:
                    # If not JSON, keep as raw string in wrapper
                    args_obj = {"_raw": raw_args}
            else:
                args_obj = raw_args

            if args_obj is None:
                args_obj = {}

            # Execute actual tool logic instead of echoing args
            try:
                if name == 'generate_course':
                    # For now, use the model's structured output as the course data
                    # Real execution would call _build_course_from_file() with context
                    tool_result = args_obj
                    logger.info(f"Function call generated course: {args_obj.get('course_title', 'Unknown')}")
                elif name == 'generate_flashcard':
                    # Use the model's structured output as the flashcard data
                    tool_result = args_obj
                    logger.info(f"Function call generated flashcard: {args_obj.get('flashcard_title', 'Unknown')}")
                else:
                    tool_result = {"status": "executed", "function": name}
                
                # Use proper function_response part for tool-call roundtrip
                function_response = types.FunctionResponse(name=name, response=tool_result)
                fr_part = types.Part(function_response=function_response)

                # Send function response with Content wrapper, fallback to direct part
                try:
                    tool_content = types.Content(role='tool', parts=[fr_part])
                    final_response = chat.send_message([tool_content])
                except Exception as wrapper_error:
                    logger.warning(f"Content wrapper failed, trying direct part: {wrapper_error}")
                    final_response = chat.send_message([fr_part])
                return final_response, args_obj
            except Exception as e:
                logger.exception(f"Failed to build/send FunctionResponse for {name}: {e}")
                # As a graceful fallback, return initial_response and the parsed args
                return initial_response, args_obj
        except Exception as e:
            logger.exception(f"Error handling function call: {e}")
            return None, None
