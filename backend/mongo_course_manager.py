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
COURSE_RATINGS_COLLECTION = "course_ratings"

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
            self.course_ratings_collection = self.db[COURSE_RATINGS_COLLECTION]
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
            self.course_ratings_collection = None
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
            self.course_ratings_collection = None
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
            self.course_ratings_collection = None
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
                self.courses_collection.create_index("title")
                self.courses_collection.create_index("tags")
                self.courses_collection.create_index("subject")
                self.courses_collection.create_index("created_at")
                # Text search index for title and content
                self.courses_collection.create_index([
                    ("title", "text"),
                    ("description", "text"),
                    ("tags", "text"),
                    ("subject", "text")
                ])
            
            if self.user_courses_collection is not None:
                self.user_courses_collection.create_index([("user_identifier", 1), ("course_id", 1)], unique=True)
            
            if self.course_ratings_collection is not None:
                self.course_ratings_collection.create_index([("course_id", 1), ("user_identifier", 1)], unique=True)
                self.course_ratings_collection.create_index("course_id")
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
            
            # Extract metadata for public courses
            metadata = self._extract_course_metadata(serializable_course_data, course_title)
            
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
                "total_sections": len(serializable_course_data) if serializable_course_data else 0, # Handle if serializable_course_data is empty
                "description": metadata['description'],
                "subject": ', '.join(metadata['subjects']) if metadata['subjects'] else '',
                "tags": metadata['tags'],
                "rating": 0.0,
                "total_ratings": 0,
                "popularity_score": 0.0
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
        """Remove a course from user's account (but keep public courses accessible to others)"""
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
                
                # If course is public, only remove from user's account but keep it public
                if course.get('is_public', False):
                    # Just remove from user_courses_collection
                    self.user_courses_collection.delete_one({
                        "user_identifier": user_identifier,
                        "course_id": course_id
                    })
                    
                    # Mark course as "orphaned" (no longer owned by original creator)
                    # but keep it public and accessible
                    self.courses_collection.update_one(
                        {"course_id": course_id},
                        {
                            "$set": {
                                "creator": "[deleted user]",
                                "is_guest": False,
                                "updated_at": datetime.now(timezone.utc)
                            },
                            "$unset": {"session_id": ""}
                        }
                    )
                    
                    return True, None
                else:
                    # Private course - delete completely
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

    def _extract_course_metadata(self, course_data: List[Dict], course_title: str) -> Dict:
        """Extract metadata from course content for search and organization"""
        # Extract subjects/topics from course content
        subjects = set()
        tags = set()
        
        # Look for subject indicators in title and content
        title_lower = course_title.lower()
        
        # Common academic subjects
        subject_keywords = {
            'mathematics': ['math', 'algebra', 'geometry', 'calculus', 'statistics'],
            'science': ['physics', 'chemistry', 'biology', 'science'],
            'history': ['history', 'historical'],
            'literature': ['literature', 'english', 'writing'],
            'computer_science': ['programming', 'coding', 'software', 'computer'],
            'business': ['business', 'economics', 'finance', 'marketing'],
            'language': ['spanish', 'french', 'german', 'chinese', 'japanese'],
            'art': ['art', 'design', 'music', 'drawing'],
            'medicine': ['medical', 'health', 'medicine', 'anatomy'],
            'engineering': ['engineering', 'mechanical', 'electrical']
        }
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                subjects.add(subject)
                tags.update(keywords)
        
        # Extract from course content
        for section in course_data:
            if isinstance(section, dict):
                section_title = section.get('section_title', '').lower()
                explanation = section.get('explanation', '').lower()
                
                for subject, keywords in subject_keywords.items():
                    if any(keyword in section_title or keyword in explanation for keyword in keywords):
                        subjects.add(subject)
                        tags.update([kw for kw in keywords if kw in section_title or kw in explanation])
        
        # Generate description from first section
        description = ""
        if course_data and len(course_data) > 0:
            first_section = course_data[0]
            if isinstance(first_section, dict):
                explanation = first_section.get('explanation', '')
                if explanation:
                    # Get first 200 characters for description
                    description = explanation[:200] + ("..." if len(explanation) > 200 else "")
        
        return {
            'subjects': list(subjects),
            'tags': list(tags),
            'description': description
        }

    def _annotate_flashcard_availability(self, courses: List[Dict]):
        """Mark courses that have public flashcards linked to them"""
        if not courses:
            return

        try:
            course_ids = [course.get('course_id') for course in courses if course.get('course_id')]
            if not course_ids:
                for course in courses:
                    course['has_flashcards'] = False
                    course['linked_flashcard_count'] = 0
                return

            flashcards_collection = self.db.get_collection('flashcards') if self.db is not None else None
            if flashcards_collection is None:
                for course in courses:
                    course['has_flashcards'] = False
                    course['linked_flashcard_count'] = 0
                return

            pipeline = [
                {"$match": {"source_course_id": {"$in": course_ids}, "is_public": True}},
                {"$group": {"_id": "$source_course_id", "total": {"$sum": 1}}}
            ]
            results = list(flashcards_collection.aggregate(pipeline))
            availability = {result['_id']: result.get('total', 0) for result in results if result.get('_id')}

            for course in courses:
                course_id = course.get('course_id')
                linked_total = availability.get(course_id, 0)
                course['has_flashcards'] = linked_total > 0
                course['linked_flashcard_count'] = linked_total
        except Exception:
            for course in courses:
                course['has_flashcards'] = False
                course['linked_flashcard_count'] = 0

    def get_public_courses(self, page: int = 0, limit: int = 20, sort_by: str = 'created_at', 
                          sort_order: int = -1) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get paginated list of public courses"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                skip = page * limit
                
                courses = list(self.courses_collection.find(
                    {"is_public": True},
                    {"_id": 0, "content": 0}  # Exclude content for performance
                ).sort(sort_by, sort_order).skip(skip).limit(limit))
                
                # Transform MongoDB structure to API structure
                for course in courses:
                    if 'title' in course:
                        course['course_title'] = course.pop('title')
                self._annotate_flashcard_availability(courses)

                return courses, None
            else:
                return None, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving public courses: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving public courses: {e}")
            return None, f"An unexpected error occurred: {e}"

    def search_public_courses(self, query: str, page: int = 0, limit: int = 20) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Search public courses by text query"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                skip = page * limit
                
                # Use MongoDB text search
                search_filter = {
                    "is_public": True,
                    "$text": {"$search": query}
                }
                
                courses = list(self.courses_collection.find(
                    search_filter,
                    {"_id": 0, "content": 0, "score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit))
                
                # Transform MongoDB structure to API structure
                for course in courses:
                    if 'title' in course:
                        course['course_title'] = course.pop('title')
                self._annotate_flashcard_availability(courses)

                return courses, None
            else:
                return None, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error searching public courses: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error searching public courses: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_courses_by_subject(self, subject: str, page: int = 0, limit: int = 20) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get public courses by subject/tag"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                skip = page * limit
                
                courses = list(self.courses_collection.find(
                    {
                        "is_public": True,
                        "$or": [
                            {"subject": {"$regex": subject, "$options": "i"}},
                            {"tags": {"$regex": subject, "$options": "i"}}
                        ]
                    },
                    {"_id": 0, "content": 0}
                ).sort("created_at", -1).skip(skip).limit(limit))
                
                # Transform MongoDB structure to API structure
                for course in courses:
                    if 'title' in course:
                        course['course_title'] = course.pop('title')
                self._annotate_flashcard_availability(courses)

                return courses, None
            else:
                return None, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error retrieving courses by subject: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error retrieving courses by subject: {e}")
            return None, f"An unexpected error occurred: {e}"

    def rate_course(self, course_id: str, user_identifier: str, rating: int) -> Tuple[bool, Optional[str]]:
        """Rate a course (1-5 stars)"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        if rating < 1 or rating > 5:
            return False, "Rating must be between 1 and 5"
        
        try:
            if self.course_ratings_collection is not None and self.courses_collection is not None:
                # Upsert rating
                self.course_ratings_collection.update_one(
                    {"course_id": course_id, "user_identifier": user_identifier},
                    {
                        "$set": {
                            "course_id": course_id,
                            "user_identifier": user_identifier,
                            "rating": rating,
                            "created_at": datetime.now(timezone.utc)
                        }
                    },
                    upsert=True
                )
                
                # Update course average rating
                self._update_course_rating(course_id)
                
                return True, None
            else:
                return False, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error rating course: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error rating course: {e}")
            return False, f"An unexpected error occurred: {e}"

    def _update_course_rating(self, course_id: str):
        """Update average rating for a course"""
        try:
            if self.course_ratings_collection is not None and self.courses_collection is not None:
                # Calculate average rating
                pipeline = [
                    {"$match": {"course_id": course_id}},
                    {"$group": {
                        "_id": "$course_id",
                        "avg_rating": {"$avg": "$rating"},
                        "total_ratings": {"$sum": 1}
                    }}
                ]
                
                result = list(self.course_ratings_collection.aggregate(pipeline))
                
                if result:
                    avg_rating = round(result[0]['avg_rating'], 2)
                    total_ratings = result[0]['total_ratings']
                    
                    # Update course document
                    self.courses_collection.update_one(
                        {"course_id": course_id},
                        {
                            "$set": {
                                "rating": avg_rating,
                                "total_ratings": total_ratings,
                                "popularity_score": avg_rating * total_ratings  # Simple popularity metric
                            }
                        }
                    )
        except Exception:
            pass  # Fail silently to not break the main operation

    def clone_course(self, course_id: str, new_creator: str, is_guest: bool = False, 
                    session_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Clone a public course for a user to modify"""
        if not self._ensure_connection():
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                # Get original course
                original_course = self.courses_collection.find_one({"course_id": course_id, "is_public": True})
                
                if not original_course:
                    return None, "Course not found or not public"
                
                # Create new course ID
                new_course_id = self.generate_course_id()
                
                # Clone course document
                cloned_course = {
                    "course_id": new_course_id,
                    "title": f"Copy of {original_course.get('title', 'Untitled Course')}",
                    "content": original_course.get('content', []),
                    "creator": new_creator,
                    "is_guest": is_guest,
                    "session_id": session_id if is_guest else None,
                    "is_public": False,  # Cloned courses are private by default
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "total_questions": original_course.get('total_questions', 0),
                    "total_sections": original_course.get('total_sections', 0),
                    "cloned_from": course_id  # Track original course
                }
                
                # Insert cloned course
                self.courses_collection.insert_one(cloned_course)
                
                # Add to user courses
                user_identifier = session_id if is_guest else new_creator
                if user_identifier:
                    self._add_to_user_courses(user_identifier, new_course_id, is_guest)
                
                return new_course_id, None
            else:
                return None, "Database connection error."
        except pymongo.errors.PyMongoError as e:
            _log_error(f"MongoDB error cloning course: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error cloning course: {e}")
            return None, f"An unexpected error occurred: {e}"

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
