"""
Chat Session Manager for AI Loom
Handles multi-turn conversations using Google Gemini SDK's chat API
"""

import logging
import uuid
import json
import re
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
        
        self.model_id = "gemini-2.5-flash-preview-09-2025"  # Using latest model with URL context support

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
        
        # Configure chat with tools for URL context and Google Search
        # This enables the AI to automatically fetch URLs and search the web
        config = types.GenerateContentConfig(
            system_instruction=system_instruction or self.system_instruction,
            tools=[
                {"url_context": {}},  # Enable URL context tool for fetching web content
                {"google_search": {}}  # Enable Google Search for up-to-date information
            ],
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
            
            # Extract reply text from response
            reply_text = ""
            if hasattr(response, 'text'):
                reply_text = response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text'):
                        reply_text += part.text

            # Try to extract JSON course payload from the reply (search anywhere)
            is_json = False
            course_data = None
            json_text = None

            # 1) Look for fenced code blocks anywhere: ```json ... ``` or ``` ... ```
            m = re.search(r"```(?:json)?\s*(.*?)\s*```", reply_text, re.DOTALL | re.IGNORECASE)
            if m:
                json_text = m.group(1).strip()
                logger.info("Found fenced code block candidate for JSON")

            # 2) If none, look for HTML <pre> or <code> blocks
            if not json_text:
                m = re.search(r"<pre[^>]*>(.*?)</pre>", reply_text, re.DOTALL | re.IGNORECASE)
                if m:
                    json_text = m.group(1).strip()
                    logger.info("Found <pre> block candidate for JSON")
            if not json_text:
                m = re.search(r"<code[^>]*>(.*?)</code>", reply_text, re.DOTALL | re.IGNORECASE)
                if m:
                    json_text = m.group(1).strip()
                    logger.info("Found <code> block candidate for JSON")

            # 3) If still none, attempt to extract the first balanced-brace JSON substring
            if not json_text:
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
                'course_data': course_data
            }
            
        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'reply': '',
                'session_id': session_id or '',
                'error': str(e)
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
