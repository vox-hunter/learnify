"""
MongoDB Chat Management System
Handles persistent chat storage, retrieval, and management with course linking support.
"""
import os
import pymongo
import pymongo.errors
from bson.objectid import ObjectId
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid
from dotenv import load_dotenv
import logging

# Load environment variables
api_env_path = os.path.join(os.path.dirname(__file__), '..', 'api', '.env')
if os.path.exists(api_env_path):
    load_dotenv(api_env_path)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME_COURSES", "learnify_courses")
CHATS_COLLECTION = "chats"

if not MONGODB_URI:
    raise ValueError("Missing MONGODB_URI environment variable")

class MongoChatManager:
    """
    Manages persistent chat sessions with MongoDB storage.
    Supports user-owned chats and optional course linkage.
    """
    
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGODB_URI)
            self.db = self.client[DB_NAME]
            self.chats_collection = self.db[CHATS_COLLECTION]
            # Test connection
            self.client.admin.command('ping')
            # Create indexes for better performance
            self._create_indexes()
            logger.info(f"MongoChatManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoChatManager: {e}")
            self.client = None
            self.db = None
            self.chats_collection = None
            raise RuntimeError(f"MongoDB initialization failed: {e}")
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index for user's chats
            self.chats_collection.create_index([("user_id", 1), ("created_at", -1)])
            # Index for course-linked chats
            self.chats_collection.create_index([("course_id", 1)])
            # Index for chat_id lookups
            self.chats_collection.create_index([("chat_id", 1)], unique=True)
            logger.info("Chat collection indexes created")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def create_chat(
        self,
        user_id: str,
        title: Optional[str] = None,
        course_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare a new chat session object (not saved until first message is added)
        """
        chat_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        # Auto-generate title if not provided
        if not title:
            if course_id:
                title = f"Course Chat - {now.strftime('%Y-%m-%d %H:%M')}"
            else:
                title = f"Chat - {now.strftime('%Y-%m-%d %H:%M')}"
        chat_doc = {
            "chat_id": chat_id,
            "user_id": user_id,
            "course_id": course_id,
            "title": title,
            "messages": [],
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
            "is_active": True
        }
        # Do not insert into DB yet
        return chat_doc
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat by ID
        
        Args:
            chat_id: The chat identifier
            
        Returns:
            Chat document or None if not found
        """
        if self.chats_collection is None:
            return None
        
        try:
            chat = self.chats_collection.find_one({"chat_id": chat_id})
            if chat:
                # Convert ObjectId to string for JSON serialization
                chat["_id"] = str(chat["_id"])
            return chat
        except Exception as e:
            logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    def get_user_chats(
        self,
        user_id: str,
        include_inactive: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all chats for a user
        
        Args:
            user_id: Username
            include_inactive: Whether to include inactive chats
            limit: Maximum number of chats to return
            
        Returns:
            List of chat documents
        """
        if self.chats_collection is None:
            return []
        
        try:
            query = {"user_id": user_id}
            if not include_inactive:
                query["is_active"] = True
            
            chats = list(
                self.chats_collection
                .find(query)
                .sort("updated_at", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for chat in chats:
                chat["_id"] = str(chat["_id"])
            
            return chats
            
        except Exception as e:
            logger.error(f"Error getting chats for user {user_id}: {e}")
            return []
    
    def get_course_chat(
        self,
        user_id: str,
        course_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the chat linked to a specific course for a user
        
        Args:
            user_id: Username
            course_id: Course identifier
            
        Returns:
            Chat document or None if not found
        """
        if self.chats_collection is None:
            return None
        
        try:
            chat = self.chats_collection.find_one({
                "user_id": user_id,
                "course_id": course_id,
                "is_active": True
            })
            
            if chat:
                chat["_id"] = str(chat["_id"])
            
            return chat
            
        except Exception as e:
            logger.error(f"Error getting course chat for {user_id}/{course_id}: {e}")
            return None
    
    def add_message(
        self,
        chat_id: str,
        role: str,
        text: str,
        attachment: Optional[Dict[str, Any]] = None,
        chat_doc: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to a chat. If chat does not exist, create and save it now.
        Args:
            chat_id: The chat identifier
            role: Message role ('user' or 'assistant')
            text: Message text
            attachment: Optional attachment metadata
            chat_doc: Optional chat document to create if chat does not exist
        Returns:
            True if successful, False otherwise
        """
        if self.chats_collection is None:
            return False
        try:
            message = {
                "role": role,
                "text": text,
                "timestamp": datetime.now(timezone.utc)
            }
            if attachment:
                message["attachment"] = attachment
            chat = self.chats_collection.find_one({"chat_id": chat_id})
            if not chat:
                # Create chat now if not exists
                if chat_doc:
                    chat_doc["messages"] = [message]
                    chat_doc["updated_at"] = datetime.now(timezone.utc)
                    result = self.chats_collection.insert_one(chat_doc)
                    logger.info(f"Created chat {chat_id} on first message")
                    return result.inserted_id is not None
                else:
                    logger.error(f"Chat {chat_id} does not exist and no chat_doc provided")
                    return False
            else:
                result = self.chats_collection.update_one(
                    {"chat_id": chat_id},
                    {
                        "$push": {"messages": message},
                        "$set": {"updated_at": datetime.now(timezone.utc)}
                    }
                )
                return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message to chat {chat_id}: {e}")
            return False
    
    def update_session_id(self, chat_id: str, session_id: str) -> bool:
        """
        Update the Gemini session ID for a chat
        
        Args:
            chat_id: The chat identifier
            session_id: New Gemini session ID
            
        Returns:
            True if successful, False otherwise
        """
        if self.chats_collection is None:
            return False
        
        try:
            result = self.chats_collection.update_one(
                {"chat_id": chat_id},
                {
                    "$set": {
                        "session_id": session_id,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating session_id for chat {chat_id}: {e}")
            return False
    
    def update_title(self, chat_id: str, title: str) -> bool:
        """
        Update chat title
        
        Args:
            chat_id: The chat identifier
            title: New title
            
        Returns:
            True if successful, False otherwise
        """
        if self.chats_collection is None:
            return False
        
        try:
            result = self.chats_collection.update_one(
                {"chat_id": chat_id},
                {
                    "$set": {
                        "title": title,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating title for chat {chat_id}: {e}")
            return False
    
    def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """
        Soft delete a chat (mark as inactive)
        
        Args:
            chat_id: The chat identifier
            user_id: Username (for verification)
            
        Returns:
            True if successful, False otherwise
        """
        if self.chats_collection is None:
            return False
        
        try:
            result = self.chats_collection.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Deleted chat {chat_id} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            return False
    
    def hard_delete_chat(self, chat_id: str, user_id: str) -> bool:
        """
        Permanently delete a chat
        
        Args:
            chat_id: The chat identifier
            user_id: Username (for verification)
            
        Returns:
            True if successful, False otherwise
        """
        if self.chats_collection is None:
            return False
        
        try:
            result = self.chats_collection.delete_one({
                "chat_id": chat_id,
                "user_id": user_id
            })
            
            if result.deleted_count > 0:
                logger.info(f"Hard deleted chat {chat_id} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error hard deleting chat {chat_id}: {e}")
            return False
