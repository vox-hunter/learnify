"""
Chat Session Manager for AI Loom
Handles multi-turn conversations using Google Gemini SDK's chat API
"""

import logging
import uuid
import json
import re
import time
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
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
                 quota_project_id: Optional[str] = None):
        """
        Initialize the chat session manager with Gemini client
        
        Args:
            user_credentials: Optional OAuth credentials dict for user quota
            username: Optional username for logging
            quota_project_id: Optional GCP project ID for quota billing
        """
        # Store user credentials for creating clients per-session
        self.user_credentials = user_credentials
        self.username = username
        self.quota_project_id = quota_project_id
        
        # Read model ID from environment with sensible default
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-exp")  # Default to stable model
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

        logger.info(f"ChatSessionManager initialized with model: {self.model_id}, user: {username or 'anonymous'}")

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

    def _create_course_generation_tool(self) -> dict:
        """
        Create a FunctionDeclaration describing the `generate_course` function.
        The JSON schema mirrors the `output_schema` in sys_ins.txt and the Pydantic models in local_backend.py.
        """
        schema = {
            "type": "object",
            "properties": {
                "course_title": {"type": "string", "description": "The title of the generated course"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section_title": {"type": "string"},
                            "explanation": {"type": "string"},
                            "quiz": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "description": "multiple_choice|true_false|short_answer|fill_in_the_blank"},
                                        "question": {"type": "string"},
                                        "options": {"type": ["array", "null"], "items": {"type": "string"}},
                                        "answer": {
                                            "oneOf": [
                                                {"type": "string"},
                                                {"type": "boolean"},
                                                {"type": "array", "items": {"type": "string"}},
                                                {"type": "object", "additionalProperties": {"type": "string"}}
                                            ]
                                        }
                                    },
                                    "required": ["type", "question", "answer"]
                                }
                            },
                            "subpoints": {
                                "type": ["array", "null"],
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "section_title": {"type": "string"},
                                        "explanation": {"type": "string"},
                                        "quiz": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"type": "string", "description": "multiple_choice|true_false|short_answer|fill_in_the_blank"},
                                                    "question": {"type": "string"},
                                                    "options": {"type": ["array", "null"], "items": {"type": "string"}},
                                                    "answer": {
                                                        "oneOf": [
                                                            {"type": "string"},
                                                            {"type": "boolean"},
                                                            {"type": "array", "items": {"type": "string"}},
                                                            {"type": "object", "additionalProperties": {"type": "string"}}
                                                        ]
                                                    }
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

        # Some SDKs accept a raw JSON schema dict as the arguments field; pass the schema directly for compatibility.
        # Return a plain dict declaration to maximize compatibility across SDK variations
        return {
            "name": "generate_course",
            "description": "Generate a structured course with title, sections, explanations, and quiz questions.",
            "arguments": schema
        }

    def create_session(self, system_instruction: Optional[str] = None) -> tuple[str, Any]:
        """
        Create a new chat session using Gemini SDK's chat.create()
        
        Args:
            system_instruction: Optional system instruction to guide the chat behavior
            
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
        
        # Configure chat with tools for URL context, Google Search and a function-calling tool for course generation
        # This enables the AI to fetch web content, search, and explicitly call the `generate_course` function
        try:
            course_tool_dict = self._create_course_generation_tool()
            # Build proper FunctionDeclaration and wrap in Tool
            course_func_decl = types.FunctionDeclaration(
                name=course_tool_dict["name"],
                description=course_tool_dict["description"],
                parameters=course_tool_dict["arguments"]
            )
            course_tool = types.Tool(function_declarations=[course_func_decl])
            
            # Use typed Tool entries for url_context and google_search
            tools_list = [
                types.Tool(url_context=types.UrlContext()),
                types.Tool(google_search=types.GoogleSearch()),
                course_tool
            ]
        except Exception as e:
            # If building the tool fails for any reason, fall back to existing tools
            logger.warning(f"Failed to create course generation tool: {e}; falling back to baseline tools")
            tools_list = [
                types.Tool(url_context=types.UrlContext()),
                types.Tool(google_search=types.GoogleSearch())
            ]

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
        ChatSessionManager._sessions[session_id] = {
            'chat': chat,
            'client': client,
            'quota_source': quota_source,
            'username': self.username
        }
        
        logger.info(f"Created new chat session: {session_id}")
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
    
    def send_message(
        self,
        session_id: Optional[str],
        message: str,
        file_data: Optional[bytes] = None,
        file_mime_type: Optional[str] = None,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the chat session with optional file or URL context
        
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
                                tool_start = time.time()
                                logger.info(f"[TOOL_CALL_START] function={name} session={session_id} user={self.username or 'guest'}")
                                
                                try:
                                    final_resp, extracted_course = self._handle_function_call(chat, response, function_call)
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

                                # Validate extracted_course using Pydantic models
                                is_json = False
                                course_data = None
                                validation_start = time.time()
                                
                                try:
                                    # Deep validation using Pydantic models
                                    from local_backend import ActualApiResponse
                                    validated_course = ActualApiResponse.model_validate(extracted_course)
                                    is_json = True
                                    course_data = extracted_course
                                    validation_time = time.time() - validation_start
                                    logger.info(f"✓ Deep validation passed for function-call course: {extracted_course.get('course_title')} (took {validation_time:.2f}s)")
                                except Exception as validation_error:
                                    validation_time = time.time() - validation_start
                                    logger.warning(f"Function call validation failed (took {validation_time:.2f}s): {validation_error}; falling back to legacy parsing")
                                    # Don't return early - let it fall through to legacy JSON parsing
                                    
                                if is_json:
                                    # Return early with function-calling result
                                    return {
                                        'success': True,
                                        'reply': reply_text,
                                        'session_id': session_id,
                                        'is_course': is_json,
                                        'course_data': course_data,
                                        'course_detection_source': 'function_call',
                                        'activity_info': activity_info
                                    }
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

            # Try to extract JSON course payload from the reply (search anywhere)
            is_json = False
            course_data = None
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
                    else:
                        logger.info("JSON parsed but missing course structure keys")
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
                'activity_info': activity_info
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
