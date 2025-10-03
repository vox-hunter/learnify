"""
MongoDB Course Management System
Handles course storage, retrieval, and management with support for both authenticated and guest users.
"""
import os
import pymongo
import pymongo.errors
from bson.objectid import ObjectId
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import uuid
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
        _log_error(message)
    else:
        print(f"ERROR: {message}")

MONGODB_URI = None
DB_NAME = "learnify_courses"
COURSES_COLLECTION = "courses"
USER_COURSES_COLLECTION = "user_courses"

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

class MongoCourseManager:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGODB_URI)
            self.db = self.client[DB_NAME]
            self.courses_collection = self.db[COURSES_COLLECTION]
            self.user_courses_collection = self.db[USER_COURSES_COLLECTION]
            # Test connection
            self.client.admin.command('ping')
            # Create indexes for better performance
            self._create_indexes()
        except pymongo.errors.ConfigurationError as e:
            error_msg = f"MongoDB Configuration Error: {e}. Please check your MONGODB_URI."
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)
        except pymongo.errors.ConnectionFailure as e:
            error_msg = f"Failed to connect to MongoDB: {e}"
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred during MongoDB initialization: {e}"
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
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
            if self.courses_collection is not None:
                self.courses_collection.create_index("course_id", unique=True)
                self.courses_collection.create_index("creator")
                self.courses_collection.create_index("is_public")
            
            if self.user_courses_collection is not None:
                self.user_courses_collection.create_index([("user_identifier", 1), ("course_id", 1)], unique=True)
        except Exception:
            pass

    def generate_course_id(self) -> str:
        """Generate a unique course ID"""
        return str(ObjectId())

    def save_course(self, course_data: List[Dict], course_title: str, creator: str, 
                   is_guest: bool = False, session_id: Optional[str] = None, is_public: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Save a course to MongoDB"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        if course_data is None: # Add this check
            st.warning("Attempted to save a course with no data (course_data is None).")
            return None, "Course data was None."

        try:
            # Convert Pydantic models in course_data to dicts
            serializable_course_data = []
            if course_data: # Ensure course_data is not None before iterating
                for item in course_data:
                    # Check if it's a Pydantic model with model_dump (v2)
                    if hasattr(item, 'model_dump') and callable(getattr(item, 'model_dump', None)):
                        try:
                            # Type check to ensure we're calling model_dump on the right object
                            if not isinstance(item, dict):
                                serializable_course_data.append(item.model_dump(mode='json'))
                            else:
                                serializable_course_data.append(item)
                        except (AttributeError, TypeError):
                            # Fallback if model_dump fails
                            serializable_course_data.append(dict(item) if hasattr(item, '__dict__') else item)
                    # Check if it's a Pydantic model with dict method (v1)
                    elif hasattr(item, 'dict') and callable(getattr(item, 'dict', None)):
                        try:
                            # Type check to ensure we're calling dict on the right object
                            if not isinstance(item, dict):
                                serializable_course_data.append(item.dict())
                            else:
                                serializable_course_data.append(item)
                        except (AttributeError, TypeError):
                            # Fallback if dict fails
                            serializable_course_data.append(dict(item) if hasattr(item, '__dict__') else item)
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
                        serializable_course_data.append(processed_item)
                    else:
                        # If it's some other type that's not a dict or Pydantic model,
                        # it might cause issues, but we'll pass it through for now.
                        # Ideally, course_data should consistently be List[Union[Dict, PydanticModel]]
                        serializable_course_data.append(item)

            course_id = self.generate_course_id()
            course_document = {
                "course_id": course_id,
                "title": course_title,
                "content": serializable_course_data, # Use the serialized data
                "creator": creator,
                "is_guest": is_guest,
                "session_id": session_id if is_guest else None,
                "is_public": is_public,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "total_questions": self._count_questions(serializable_course_data), # Use robust _count_questions
                "total_sections": len(serializable_course_data) if serializable_course_data else 0 # Handle if serializable_course_data is empty
            }
            
            if self.courses_collection is not None:
                self.courses_collection.insert_one(course_document)
                user_identifier = session_id if is_guest else creator
                if user_identifier:
                    self._add_to_user_courses(user_identifier, course_id, is_guest)
                return course_id, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error saving course: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error saving course: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_course(self, course_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve a course by ID"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                course = self.courses_collection.find_one({"course_id": course_id})
                if course:
                    course.pop('_id', None)
                    # Transform MongoDB structure to API structure
                    if 'title' in course:
                        course['course_title'] = course.pop('title')
                    if 'content' in course:
                        course['sections'] = course.pop('content')
                    return course, None
                else:
                    return None, "Course not found."
            else:
                return None, "Database connection error."
                
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving course: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving course: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_user_courses(self, user_identifier: str, is_guest: bool = False, 
                        session_id: Optional[str] = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get all courses for a user"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                if is_guest and session_id:
                    query = {"session_id": session_id, "is_guest": True}
                else:
                    query = {"creator": user_identifier, "is_guest": False}
                
                courses = list(self.courses_collection.find(
                    query,
                    {"_id": 0}
                ).sort("created_at", -1))
                
                # Transform MongoDB structure to API structure for each course
                for course in courses:
                    if 'title' in course:
                        course['course_title'] = course.pop('title')
                    if 'content' in course:
                        course['sections'] = course.pop('content')
                
                return courses, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving user courses: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving user courses: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_course_stats(self, user_identifier: str, is_guest: bool = False, session_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Get course statistics for a user"""
        if not self._ensure_connection():
            return None, "Database connection error."

        try:
            if self.courses_collection is not None:
                if is_guest and session_id:
                    query = {"session_id": session_id, "is_guest": True}
                else:
                    query = {"creator": user_identifier, "is_guest": False}

                courses = list(self.courses_collection.find(query, {"_id": 0, "total_questions": 1, "total_sections": 1}))

                if not courses:
                    return {"total_courses": 0, "total_questions": 0, "average_questions_per_course": 0, "total_sections": 0}, None

                total_courses = len(courses)
                total_questions = sum(course.get("total_questions", 0) for course in courses)
                total_sections = sum(course.get("total_sections", 0) for course in courses)
                average_questions_per_course = total_questions / total_courses if total_courses > 0 else 0

                return {
                    "total_courses": total_courses,
                    "total_questions": total_questions,
                    "average_questions_per_course": round(average_questions_per_course, 2),
                    "total_sections": total_sections
                }, None
            else:
                return None, "Database connection error."

        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving course stats: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving course stats: {e}")
            return None, f"An unexpected error occurred: {e}"

    def transfer_guest_courses(self, session_id: str, new_user_identifier: str) -> Tuple[int, Optional[str]]:
        """Transfer guest courses to authenticated user when they log in"""
        if not self._ensure_connection():
            return 0, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                result = self.courses_collection.update_many(
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
                    transferred_courses = list(self.courses_collection.find(
                        {"creator": new_user_identifier, "is_guest": False},
                        {"course_id": 1, "_id": 0}
                    ))
                    
                    for course in transferred_courses:
                        self._add_to_user_courses(new_user_identifier, course["course_id"], False)
                
                return result.modified_count, None
            else:
                return 0, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error transferring courses: {e}")
            return 0, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error transferring courses: {e}")
            return 0, f"An unexpected error occurred: {e}"

    def delete_course(self, course_id: str, user_identifier: str, is_guest: bool = False) -> Tuple[bool, Optional[str]]:
        """Delete a course (only by its creator)"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            if self.courses_collection is not None and self.user_courses_collection is not None:
                if is_guest:
                    query = {"course_id": course_id, "session_id": user_identifier, "is_guest": True}
                else:
                    query = {"course_id": course_id, "creator": user_identifier, "is_guest": False}
                
                course = self.courses_collection.find_one(query)
                if not course:
                    return False, "Course not found or you don't have permission to delete it."
                
                result = self.courses_collection.delete_one(query)
                self.user_courses_collection.delete_one({
                    "user_identifier": user_identifier,
                    "course_id": course_id
                })
                
                return result.deleted_count > 0, None
            else:
                return False, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error deleting course: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error deleting course: {e}")
            return False, f"An unexpected error occurred: {e}"

    def update_course_privacy(self, course_id: str, user_identifier: str, is_public: bool) -> Tuple[bool, Optional[str]]:
        """Update course privacy setting"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                result = self.courses_collection.update_one(
                    {"course_id": course_id, "creator": user_identifier, "is_guest": False},
                    {
                        "$set": {
                            "is_public": is_public,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                if result.matched_count == 0:
                    return False, "Course not found or you don't have permission to modify it."
                
                return result.modified_count > 0, None
            else:
                return False, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error updating course privacy: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error updating course privacy: {e}")
            return False, f"An unexpected error occurred: {e}"

    def update_course_memory_strength(self, course_id: str, new_strength: int, time_spent: float) -> Tuple[bool, Optional[str]]:
        """Update the memory strength and last attempt timestamp for a course."""
        if not self._ensure_connection():
            return False, "Database connection error."

        try:
            if self.courses_collection is not None:
                result = self.courses_collection.update_one(
                    {"course_id": course_id},
                    {
                        "$set": {
                            "memory_strength": new_strength,
                            "last_attempt_timestamp": datetime.now(timezone.utc),
                            "time_spent": time_spent,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )

                if result.matched_count == 0:
                    return False, "Course not found."

                return result.modified_count > 0, None
            else:
                return False, "Database connection error."

        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error updating memory strength: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error updating memory strength: {e}")
            return False, f"An unexpected error occurred: {e}"

    def can_access_course(self, course_id: str, user_identifier: Optional[str] = None, 
                         session_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Check if a user can access a course"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                course = self.courses_collection.find_one({"course_id": course_id})
                if not course:
                    return False, "Course not found."
                
                if course.get("is_public", True):
                    return True, None
                
                if user_identifier and course.get("creator") == user_identifier:
                    return True, None
                
                if session_id and course.get("session_id") == session_id and course.get("is_guest"):
                    return True, None
                
                return False, "This course is private and you don't have access to it."
            else:
                return False, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error checking course access: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error checking course access: {e}")
            return False, f"An unexpected error occurred: {e}"

    def _add_to_user_courses(self, user_identifier: str, course_id: str, is_guest: bool):
        """Add course to user courses tracking"""
        try:
            if self.user_courses_collection is not None:
                self.user_courses_collection.update_one(
                    {"user_identifier": user_identifier, "course_id": course_id},
                    {
                        "$set": {
                            "user_identifier": user_identifier,
                            "course_id": course_id,
                            "is_guest": is_guest,
                            "added_at": datetime.now(timezone.utc)
                        }
                    },
                    upsert=True
                )
        except Exception:
            pass

    def save_progress(self, course_id: str, user_identifier: str, 
                     progress_data: Dict, is_guest: bool = False) -> Tuple[bool, Optional[str]]:
        """Save user progress for a course"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            if self.user_courses_collection is not None:
                # Upsert progress document
                self.user_courses_collection.update_one(
                    {
                        "course_id": course_id,
                        "user_identifier": user_identifier,
                        "is_guest": is_guest
                    },
                    {
                        "$set": {
                            "progress": progress_data,
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        },
                        "$setOnInsert": {
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    upsert=True
                )
                return True, None
            else:
                return False, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error saving progress: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error saving progress: {e}")
            return False, f"An unexpected error occurred: {e}"

    def get_progress(self, course_id: str, user_identifier: str, 
                    is_guest: bool = False) -> Tuple[Optional[Dict], Optional[str]]:
        """Get user progress for a course"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.user_courses_collection is not None:
                progress_doc = self.user_courses_collection.find_one(
                    {
                        "course_id": course_id,
                        "user_identifier": user_identifier,
                        "is_guest": is_guest
                    },
                    {"_id": 0, "progress": 1}
                )
                if progress_doc and "progress" in progress_doc:
                    return progress_doc["progress"], None
                else:
                    return None, None  # No progress found, not an error
            else:
                return None, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving progress: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving progress: {e}")
            return None, f"An unexpected error occurred: {e}"

    def _count_questions(self, course_data: Optional[List[Dict]]) -> int:
        """Count total questions in course data. Handles None and empty lists."""
        if not course_data:  # Handles None or empty list
            return 0
        
        total_questions_count = 0
        for section_dict in course_data:
            if isinstance(section_dict, dict):
                # Check 'quiz' field (previously also checked 'questions')
                quiz_list = section_dict.get('quiz') 
                if isinstance(quiz_list, list):
                    total_questions_count += len(quiz_list)
                
                # Recursively count questions in subsections
                subsections_list = section_dict.get('subsections')
                if isinstance(subsections_list, list): 
                    total_questions_count += self._count_questions(subsections_list) # Recursive call
        return total_questions_count

# Module-level instance
_course_manager = None

def get_course_manager() -> MongoCourseManager:
    """Get singleton course manager instance"""
    # Using module-level variable instead of global
    if '_course_manager' not in globals() or globals()['_course_manager'] is None:
        globals()['_course_manager'] = MongoCourseManager()
    return globals()['_course_manager']

def get_session_id() -> str:
    """Generate a new session ID for guest users"""
    # In FastAPI context, generate a new UUID each time
    # The frontend will manage session persistence via localStorage
    return str(uuid.uuid4())
