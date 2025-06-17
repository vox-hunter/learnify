"""
MongoDB Course Management System
Handles course storage, retrieval, and management with support for both authenticated and guest users.
"""
import streamlit as st
import pymongo
import pymongo.errors
from bson.objectid import ObjectId
from datetime import datetime, timezone
import json
from typing import Dict, List, Optional, Tuple, Any, Union
import uuid

try:
    MONGODB_URI = st.secrets["MONGODB_URI"]
    DB_NAME = "learnify_courses"
    COURSES_COLLECTION = "courses"
    USER_COURSES_COLLECTION = "user_courses"
except KeyError as e:
    st.error(f"Missing secret: {e}. Please ensure MONGODB_URI is set in your Streamlit secrets.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while loading secrets: {e}")
    st.stop()

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
            st.error(f"MongoDB Configuration Error: {e}. Please check your MONGODB_URI.")
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
            st.stop()
        except pymongo.errors.ConnectionFailure as e:
            st.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred during MongoDB initialization: {e}")
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
            st.stop()

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

    def save_course(self, course_data: List[Any], course_title: str, creator: str, 
                   is_guest: bool = False, session_id: Optional[str] = None, is_public: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Save a course to MongoDB"""
        if self.db is None:
            return None, "Database connection error."
        
        if course_data is None: # Add this check
            st.warning("Attempted to save a course with no data (course_data is None).")
            return None, "Course data was None."

        try:
            # Convert Pydantic models in course_data to dicts
            serializable_course_data = []
            if course_data: # Ensure course_data is not None before iterating
                for item in course_data:
                    if hasattr(item, 'model_dump'):  # Pydantic v2
                        serializable_course_data.append(item.model_dump(mode='json'))
                    elif hasattr(item, 'dict'):  # Pydantic v1
                        serializable_course_data.append(item.dict())
                    elif isinstance(item, dict):
                        # If it's already a dict, ensure nested Pydantic models are also converted
                        processed_item = {}
                        for key, value in item.items():
                            if hasattr(value, 'model_dump'):
                                processed_item[key] = value.model_dump(mode='json')
                            elif isinstance(value, list) and value and hasattr(value[0], 'model_dump'):
                                processed_item[key] = [v.model_dump(mode='json') for v in value]
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
                result = self.courses_collection.insert_one(course_document)
                user_identifier = session_id if is_guest else creator
                if user_identifier:
                    self._add_to_user_courses(user_identifier, course_id, is_guest)
                return course_id, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            st.error(f"MongoDB error saving course: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error saving course: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_course(self, course_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve a course by ID"""
        if self.db is None:
            return None, "Database connection error."
        
        try:
            if self.courses_collection is not None:
                course = self.courses_collection.find_one({"course_id": course_id})
                if course:
                    course.pop('_id', None)
                    return course, None
                else:
                    return None, "Course not found."
            else:
                return None, "Database connection error."
                
        except pymongo.errors.PyMongoError as e:
            st.error(f"MongoDB error retrieving course: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error retrieving course: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_user_courses(self, user_identifier: str, is_guest: bool = False, 
                        session_id: Optional[str] = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get all courses for a user"""
        if self.db is None:
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
                
                return courses, None
            else:
                return None, "Database connection error."
            
        except pymongo.errors.PyMongoError as e:
            st.error(f"MongoDB error retrieving user courses: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error retrieving user courses: {e}")
            return None, f"An unexpected error occurred: {e}"

    def get_course_stats(self, user_identifier: str, is_guest: bool = False, session_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Get course statistics for a user"""
        if self.db is None:
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
            st.error(f"MongoDB error retrieving course stats: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error retrieving course stats: {e}")
            return None, f"An unexpected error occurred: {e}"

    def transfer_guest_courses(self, session_id: str, new_user_identifier: str) -> Tuple[int, Optional[str]]:
        """Transfer guest courses to authenticated user when they log in"""
        if self.db is None:
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
            st.error(f"MongoDB error transferring courses: {e}")
            return 0, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error transferring courses: {e}")
            return 0, f"An unexpected error occurred: {e}"

    def delete_course(self, course_id: str, user_identifier: str, is_guest: bool = False) -> Tuple[bool, Optional[str]]:
        """Delete a course (only by its creator)"""
        if self.db is None:
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
            st.error(f"MongoDB error deleting course: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error deleting course: {e}")
            return False, f"An unexpected error occurred: {e}"

    def update_course_privacy(self, course_id: str, user_identifier: str, is_public: bool) -> Tuple[bool, Optional[str]]:
        """Update course privacy setting"""
        if self.db is None:
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
            st.error(f"MongoDB error updating course privacy: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error updating course privacy: {e}")
            return False, f"An unexpected error occurred: {e}"

    def can_access_course(self, course_id: str, user_identifier: Optional[str] = None, 
                         session_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Check if a user can access a course"""
        if self.db is None:
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
            st.error(f"MongoDB error checking course access: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            st.error(f"Unexpected error checking course access: {e}")
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

@st.cache_resource
def get_course_manager() -> MongoCourseManager:
    """Get singleton course manager instance"""
    return MongoCourseManager()

def get_session_id() -> str:
    """Get or create session ID for guest users"""
    if 'guest_session_id' not in st.session_state:
        st.session_state.guest_session_id = str(uuid.uuid4())
    return st.session_state.guest_session_id
