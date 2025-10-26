"""
MongoDB Flashcard Management System
Handles flashcard storage, retrieval, and management with support for both authenticated and guest users.
Mirrors the architecture of MongoCourseManager for consistency.
"""
import os
import pymongo
import pymongo.errors
from bson.objectid import ObjectId
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv

# Try to import streamlit, but make it optional
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Load environment variables from multiple possible locations
api_env_path = os.path.join(os.path.dirname(__file__), '..', 'api', '.env')
if os.path.exists(api_env_path):
    load_dotenv(api_env_path)
else:
    load_dotenv()

def _log_error(message):
    """Log error using Streamlit if available, otherwise use print/logging"""
    if STREAMLIT_AVAILABLE:
        st.error(message)
    else:
        print(f"ERROR: {message}")

MONGODB_URI = None
DB_NAME = "learnify_courses"
FLASHCARDS_COLLECTION = "flashcards"
USER_FLASHCARDS_COLLECTION = "user_flashcards"

# Try Streamlit secrets first
if STREAMLIT_AVAILABLE:
    try:
        MONGODB_URI = st.secrets["MONGODB_URI"]
        DB_NAME = st.secrets.get("DB_NAME_COURSES", "learnify_courses")
    except (KeyError, AttributeError, FileNotFoundError, Exception):
        pass  # Fall through to environment variables

# Fallback to environment variables
if not MONGODB_URI:
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("DB_NAME_COURSES", "learnify_courses")

if not MONGODB_URI:
    error_msg = "Missing MONGODB_URI. Please ensure MONGODB_URI is set in your environment variables or Streamlit secrets."
    if STREAMLIT_AVAILABLE:
        _log_error(error_msg)
        st.stop()
    else:
        raise ValueError(error_msg)

class MongoFlashcardManager:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGODB_URI)
            self.db = self.client[DB_NAME]
            self.flashcards_collection = self.db[FLASHCARDS_COLLECTION]
            self.user_flashcards_collection = self.db[USER_FLASHCARDS_COLLECTION]
            # Test connection
            self.client.admin.command('ping')
            # Create indexes for better performance
            self._create_indexes()
        except pymongo.errors.ConfigurationError as e:
            error_msg = f"MongoDB Configuration Error: {e}. Please check your MONGODB_URI."
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.flashcards_collection = None
            self.user_flashcards_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)
        except pymongo.errors.ConnectionFailure as e:
            error_msg = f"Failed to connect to MongoDB: {e}"
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.flashcards_collection = None
            self.user_flashcards_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred during MongoDB initialization: {e}"
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.flashcards_collection = None
            self.user_flashcards_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)

    def _ensure_connection(self):
        """Ensure MongoDB connection is active"""
        if self.client is None or self.db is None:
            _log_error("MongoDB connection is not available.")
            return False
        try:
            self.client.admin.command('ping')
            return True
        except pymongo.errors.ConnectionFailure:
            _log_error("MongoDB connection lost. Please try again later.")
            return False

    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            if self.flashcards_collection is not None:
                self.flashcards_collection.create_index("flashcard_id", unique=True)
                self.flashcards_collection.create_index("creator")
                self.flashcards_collection.create_index("session_id")
                self.flashcards_collection.create_index("source_course_id")
                self.flashcards_collection.create_index("created_at")
            
            if self.user_flashcards_collection is not None:
                self.user_flashcards_collection.create_index([("user_identifier", 1), ("flashcard_id", 1)], unique=True)
        except Exception:
            pass

    def generate_flashcard_id(self) -> str:
        """Generate a unique flashcard ID"""
        return str(ObjectId())

    def save_flashcard(self, flashcard_data: List[Dict], flashcard_title: str, creator: str, 
                      is_guest: bool = False, session_id: Optional[str] = None, 
                      source_course_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Save a flashcard set to MongoDB"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        if flashcard_data is None:
            return None, "Flashcard data was None."

        try:
            # Convert Pydantic models in flashcard_data to dicts
            serializable_flashcard_data = []
            if flashcard_data:
                for item in flashcard_data:
                    # Check if it's a Pydantic model with model_dump (v2)
                    if hasattr(item, 'model_dump') and callable(getattr(item, 'model_dump', None)):
                        try:
                            if not isinstance(item, dict):
                                serializable_flashcard_data.append(item.model_dump(mode='json'))
                            else:
                                serializable_flashcard_data.append(item)
                        except (AttributeError, TypeError):
                            serializable_flashcard_data.append(dict(item) if hasattr(item, '__dict__') else item)
                    # Check if it's a Pydantic model with dict method (v1)
                    elif hasattr(item, 'dict') and callable(getattr(item, 'dict', None)):
                        try:
                            if not isinstance(item, dict):
                                serializable_flashcard_data.append(item.dict())
                            else:
                                serializable_flashcard_data.append(item)
                        except (AttributeError, TypeError):
                            serializable_flashcard_data.append(dict(item) if hasattr(item, '__dict__') else item)
                    elif isinstance(item, dict):
                        # If it's already a dict, ensure nested Pydantic models are also converted
                        processed_item = {}
                        for key, value in item.items():
                            if hasattr(value, 'model_dump') and callable(getattr(value, 'model_dump', None)) and not isinstance(value, dict):
                                try:
                                    processed_item[key] = value.model_dump(mode='json')
                                except (AttributeError, TypeError):
                                    processed_item[key] = value
                            elif isinstance(value, list) and value and hasattr(value[0], 'model_dump') and not isinstance(value[0], dict):
                                try:
                                    processed_item[key] = [v.model_dump(mode='json') for v in value if hasattr(v, 'model_dump')]
                                except (AttributeError, TypeError):
                                    processed_item[key] = value
                            else:
                                processed_item[key] = value
                        serializable_flashcard_data.append(processed_item)
                    else:
                        serializable_flashcard_data.append(item)

            flashcard_id = self.generate_flashcard_id()
            
            flashcard_document = {
                "flashcard_id": flashcard_id,
                "title": flashcard_title,
                "cards": serializable_flashcard_data,
                "creator": creator,
                "is_guest": is_guest,
                "session_id": session_id if is_guest else None,
                "source_course_id": source_course_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "total_cards": self._count_cards(serializable_flashcard_data)
            }
            
            if self.flashcards_collection is not None:
                self.flashcards_collection.insert_one(flashcard_document)
                user_identifier = session_id if is_guest else creator
                if user_identifier:
                    self._add_to_user_flashcards(user_identifier, flashcard_id, is_guest)
                return flashcard_id, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error saving flashcard: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error saving flashcard: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_flashcard(self, flashcard_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve a flashcard set by ID"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.flashcards_collection is not None:
                flashcard = self.flashcards_collection.find_one({"flashcard_id": flashcard_id})
                if flashcard:
                    flashcard.pop('_id', None)
                    # Transform MongoDB structure to API structure
                    if 'title' in flashcard:
                        flashcard['flashcard_title'] = flashcard.pop('title')
                    return flashcard, None
                else:
                    return None, "Flashcard not found."
            else:
                return None, "Database connection error."
                
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving flashcard: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving flashcard: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_user_flashcards(self, user_identifier: str, is_guest: bool = False, 
                           session_id: Optional[str] = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get all flashcards for a user"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.flashcards_collection is not None:
                if is_guest and session_id:
                    query = {"session_id": session_id, "is_guest": True}
                else:
                    query = {"creator": user_identifier, "is_guest": False}
                
                flashcards = list(self.flashcards_collection.find(
                    query,
                    {"_id": 0}
                ).sort("created_at", -1))
                
                # Transform MongoDB structure to API structure for each flashcard
                for flashcard in flashcards:
                    if 'title' in flashcard:
                        flashcard['flashcard_title'] = flashcard.pop('title')
                
                return flashcards, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving user flashcards: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving user flashcards: {e}")
            return None, f"An unexpected error occurred: {e}"

    def delete_flashcard(self, flashcard_id: str, user_identifier: str, is_guest: bool = False) -> Tuple[bool, Optional[str]]:
        """Remove a flashcard set from user's account"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            if self.flashcards_collection is not None:
                # Verify ownership
                if is_guest:
                    query = {"flashcard_id": flashcard_id, "session_id": user_identifier, "is_guest": True}
                else:
                    query = {"flashcard_id": flashcard_id, "creator": user_identifier, "is_guest": False}
                
                flashcard = self.flashcards_collection.find_one(query)
                if not flashcard:
                    return False, "Flashcard not found or you don't have permission to delete it."
                
                # Delete the flashcard
                self.flashcards_collection.delete_one(query)
                
                # Remove from user_flashcards collection
                self.user_flashcards_collection.delete_one({
                    "user_identifier": user_identifier,
                    "flashcard_id": flashcard_id
                })
                
                return True, None
            else:
                return False, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error deleting flashcard: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error deleting flashcard: {e}")
            return False, f"An unexpected error occurred: {e}"

    def save_flashcard_progress(self, flashcard_id: str, user_identifier: str, 
                                progress_data: Dict, is_guest: bool = False) -> Tuple[bool, Optional[str]]:
        """Save user progress for a flashcard set (spaced repetition tracking)"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            if self.user_flashcards_collection is not None:
                # Normalize mastery_levels keys to strings for MongoDB compatibility
                # MongoDB does not allow dots or leading $ in keys
                if 'mastery_levels' in progress_data and progress_data['mastery_levels']:
                    normalized_mastery = {}
                    for key, value in progress_data['mastery_levels'].items():
                        # Convert key to string and validate
                        str_key = str(key)
                        # Guard rails: no dots or leading $ (MongoDB restrictions)
                        if '.' in str_key or str_key.startswith('$'):
                            return False, f"Invalid mastery level key: {str_key}. Keys cannot contain dots or start with $."
                        normalized_mastery[str_key] = value
                    progress_data['mastery_levels'] = normalized_mastery
                
                progress_data['last_updated'] = datetime.now(timezone.utc)
                
                result = self.user_flashcards_collection.update_one(
                    {
                        "user_identifier": user_identifier,
                        "flashcard_id": flashcard_id
                    },
                    {
                        "$set": {
                            "progress": progress_data,
                            "is_guest": is_guest
                        }
                    },
                    upsert=True
                )
                
                return True, None
            else:
                return False, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error saving flashcard progress: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error saving flashcard progress: {e}")
            return False, f"An unexpected error occurred: {e}"

    def get_flashcard_progress(self, flashcard_id: str, user_identifier: str, 
                               is_guest: bool = False) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve user progress for a flashcard set"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.user_flashcards_collection is not None:
                user_flashcard = self.user_flashcards_collection.find_one({
                    "user_identifier": user_identifier,
                    "flashcard_id": flashcard_id
                })
                
                if user_flashcard and 'progress' in user_flashcard:
                    progress = user_flashcard['progress']
                    # Convert mastery_levels keys back to integers for client compatibility
                    if 'mastery_levels' in progress and progress['mastery_levels']:
                        int_mastery = {}
                        for key, value in progress['mastery_levels'].items():
                            try:
                                int_mastery[int(key)] = value
                            except (ValueError, TypeError):
                                # If conversion fails, keep as string
                                int_mastery[key] = value
                        progress['mastery_levels'] = int_mastery
                    return progress, None
                else:
                    return None, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving flashcard progress: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving flashcard progress: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_flashcards_by_course(self, course_id: str, user_identifier: str, 
                                is_guest: bool = False) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get all flashcards linked to a specific course"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.flashcards_collection is not None:
                # Query for flashcards with matching source_course_id
                # Only return flashcards owned by the user
                if is_guest:
                    query = {
                        "source_course_id": course_id,
                        "session_id": user_identifier,
                        "is_guest": True
                    }
                else:
                    query = {
                        "source_course_id": course_id,
                        "creator": user_identifier,
                        "is_guest": False
                    }
                
                flashcards = list(self.flashcards_collection.find(
                    query,
                    {"_id": 0}
                ).sort("created_at", -1))
                
                # Transform MongoDB structure to API structure
                for flashcard in flashcards:
                    if 'title' in flashcard:
                        flashcard['flashcard_title'] = flashcard.pop('title')
                
                return flashcards, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving flashcards by course: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving flashcards by course: {e}")
            return None, f"An unexpected error occurred: {e}"

    def transfer_guest_flashcards(self, session_id: str, new_user_identifier: str) -> Tuple[int, Optional[str]]:
        """Transfer guest flashcards to authenticated user when they log in"""
        if not self._ensure_connection():
            return 0, "Database connection error."
        
        try:
            if self.flashcards_collection is not None:
                result = self.flashcards_collection.update_many(
                    {"session_id": session_id, "is_guest": True},
                    {
                        "$set": {
                            "creator": new_user_identifier,
                            "is_guest": False,
                            "updated_at": datetime.now(timezone.utc)
                        },
                        "$unset": {"session_id": ""}
                    }
                )
                
                if result.modified_count > 0:
                    transferred_flashcards = list(self.flashcards_collection.find(
                        {"creator": new_user_identifier, "is_guest": False},
                        {"flashcard_id": 1, "_id": 0}
                    ))
                    
                    for flashcard in transferred_flashcards:
                        self._add_to_user_flashcards(new_user_identifier, flashcard["flashcard_id"], False)
                
                return result.modified_count, None
            else:
                return 0, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error transferring flashcards: {e}")
            return 0, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error transferring flashcards: {e}")
            return 0, f"An unexpected error occurred: {e}"

    def _add_to_user_flashcards(self, user_identifier: str, flashcard_id: str, is_guest: bool):
        """Add flashcard to user's flashcard collection"""
        try:
            if self.user_flashcards_collection is not None:
                self.user_flashcards_collection.update_one(
                    {
                        "user_identifier": user_identifier,
                        "flashcard_id": flashcard_id
                    },
                    {
                        "$set": {
                            "is_guest": is_guest,
                            "added_at": datetime.now(timezone.utc)
                        }
                    },
                    upsert=True
                )
        except Exception:
            pass

    def _count_cards(self, flashcard_data: List[Dict]) -> int:
        """Count total cards in flashcard set"""
        if not flashcard_data:
            return 0
        return len(flashcard_data)

# Module-level singleton
_flashcard_manager = None

def get_flashcard_manager() -> MongoFlashcardManager:
    """Get or create singleton instance of MongoFlashcardManager"""
    global _flashcard_manager
    if _flashcard_manager is None:
        _flashcard_manager = MongoFlashcardManager()
    return _flashcard_manager
