"""
Optimized MongoDB Course Management System
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
    st.error(f"Missing secret: {e}")
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
            self._create_indexes()
        except Exception as e:
            st.error(f"MongoDB initialization error: {e}")
            self.client = None
            self.db = None
            self.courses_collection = None
            self.user_courses_collection = None
            st.stop()

    def _ensure_connection(self):
        """Lightweight connection check"""
        if self.client is None:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False

    def _create_indexes(self):
        """Create optimized indexes"""
        try:
            if self.courses_collection is not None:
                self.courses_collection.create_index("course_id", unique=True)
                self.courses_collection.create_index([("creator", 1), ("is_guest", 1)])
                self.courses_collection.create_index("is_public")
            
            if self.user_courses_collection is not None:
                self.user_courses_collection.create_index([("user_identifier", 1), ("course_id", 1)], unique=True)
        except:
            pass

    def generate_course_id(self) -> str:
        """Generate unique course ID"""
        return str(ObjectId())

    def save_course(self, course_data: List[Dict], course_title: str, creator: str, 
                   is_guest: bool = False, session_id: Optional[str] = None, is_public: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Optimized course saving"""
        if not self._ensure_connection() or course_data is None:
            return None, "Database connection error or no data"

        try:
            # Efficient serialization
            serializable_course_data = []
            if course_data:
                for item in course_data:
                    if hasattr(item, 'model_dump'):
                        serializable_course_data.append(item.model_dump(mode='json'))
                    elif hasattr(item, 'dict'):
                        serializable_course_data.append(item.dict())
                    elif isinstance(item, dict):
                        serializable_course_data.append(self._process_dict_item(item))
                    else:
                        serializable_course_data.append(item)

            course_id = self.generate_course_id()
            course_document = {
                "course_id": course_id,
                "title": course_title,
                "content": serializable_course_data,
                "creator": creator,
                "is_guest": is_guest,
                "session_id": session_id if is_guest else None,
                "is_public": is_public,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "total_questions": self._count_questions(serializable_course_data),
                "total_sections": len(serializable_course_data) if serializable_course_data else 0
            }
            
            if self.courses_collection is not None:
                self.courses_collection.insert_one(course_document)
                user_identifier = session_id if is_guest else creator
                if user_identifier:
                    self._add_to_user_courses(user_identifier, course_id, is_guest)
                return course_id, None
            else:
                return None, "Database connection error"
            
        except Exception as e:
            return None, f"Database error: {e}"

    def _process_dict_item(self, item):
        """Process dictionary items efficiently"""
        processed_item = {}
        for key, value in item.items():
            if hasattr(value, 'model_dump'):
                processed_item[key] = value.model_dump(mode='json')
            elif isinstance(value, list) and value and hasattr(value[0], 'model_dump'):
                processed_item[key] = [v.model_dump(mode='json') for v in value]
            else:
                processed_item[key] = value
        return processed_item

    def get_course(self, course_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Optimized course retrieval"""
        if not self._ensure_connection():
            return None, "Database connection error"
        
        try:
            if self.courses_collection is not None:
                course = self.courses_collection.find_one({"course_id": course_id})
                if course:
                    course.pop('_id', None)
                    return course, None
                else:
                    return None, "Course not found"
            else:
                return None, "Database connection error"
        except Exception as e:
            return None, f"Database error: {e}"

    def get_user_courses(self, user_identifier: str, is_guest: bool = False, 
                        session_id: Optional[str] = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Optimized user courses retrieval"""
        if not self._ensure_connection():
            return None, "Database connection error"
        
        try:
            if self.courses_collection is not None:
                if is_guest and session_id:
                    query = {"session_id": session_id, "is_guest": True}
                else:
                    query = {"creator": user_identifier, "is_guest": False}
                
                # Optimized projection - only get necessary fields
                projection = {
                    "_id": 0,
                    "course_id": 1,
                    "title": 1,
                    "created_at": 1,
                    "total_questions": 1,
                    "total_sections": 1,
                    "is_public": 1
                }
                
                courses = list(self.courses_collection.find(
                    query, projection
                ).sort("created_at", -1).limit(20))  # Limit results
                
                return courses, None
            else:
                return None, "Database connection error"
            
        except Exception as e:
            return None, f"Database error: {e}"

    def get_course_stats(self, user_identifier: str, is_guest: bool = False, session_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Optimized course statistics"""
        if not self._ensure_connection():
            return None, "Database connection error"

        try:
            if self.courses_collection is not None:
                if is_guest and session_id:
                    query = {"session_id": session_id, "is_guest": True}
                else:
                    query = {"creator": user_identifier, "is_guest": False}

                # Use aggregation for better performance
                pipeline = [
                    {"$match": query},
                    {"$group": {
                        "_id": None,
                        "total_courses": {"$sum": 1},
                        "total_questions": {"$sum": "$total_questions"},
                        "total_sections": {"$sum": "$total_sections"},
                        "public_courses": {"$sum": {"$cond": ["$is_public", 1, 0]}},
                        "private_courses": {"$sum": {"$cond": ["$is_public", 0, 1]}}
                    }}
                ]
                
                result = list(self.courses_collection.aggregate(pipeline))
                
                if result:
                    stats = result[0]
                    stats.pop('_id', None)
                    total_courses = stats.get('total_courses', 0)
                    total_questions = stats.get('total_questions', 0)
                    stats['average_questions_per_course'] = round(
                        total_questions / total_courses if total_courses > 0 else 0, 2
                    )
                    return stats, None
                else:
                    return {
                        "total_courses": 0,
                        "total_questions": 0,
                        "average_questions_per_course": 0,
                        "total_sections": 0,
                        "public_courses": 0,
                        "private_courses": 0
                    }, None
            else:
                return None, "Database connection error"

        except Exception as e:
            return None, f"Database error: {e}"

    def transfer_guest_courses(self, session_id: str, new_user_identifier: str) -> Tuple[int, Optional[str]]:
        """Optimized course transfer"""
        if not self._ensure_connection():
            return 0, "Database connection error"
        
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
                    # Update user courses tracking
                    transferred_courses = self.courses_collection.find(
                        {"creator": new_user_identifier, "is_guest": False},
                        {"course_id": 1, "_id": 0}
                    )
                    
                    for course in transferred_courses:
                        self._add_to_user_courses(new_user_identifier, course["course_id"], False)
                
                return result.modified_count, None
            else:
                return 0, "Database connection error"
            
        except Exception as e:
            return 0, f"Database error: {e}"

    def delete_course(self, course_id: str, user_identifier: str, is_guest: bool = False) -> Tuple[bool, Optional[str]]:
        """Optimized course deletion"""
        if not self._ensure_connection():
            return False, "Database connection error"
        
        try:
            if self.courses_collection is not None and self.user_courses_collection is not None:
                if is_guest:
                    query = {"course_id": course_id, "session_id": user_identifier, "is_guest": True}
                else:
                    query = {"course_id": course_id, "creator": user_identifier, "is_guest": False}
                
                course = self.courses_collection.find_one(query, {"_id": 1})
                if not course:
                    return False, "Course not found or no permission"
                
                result = self.courses_collection.delete_one(query)
                self.user_courses_collection.delete_one({
                    "user_identifier": user_identifier,
                    "course_id": course_id
                })
                
                return result.deleted_count > 0, None
            else:
                return False, "Database connection error"
            
        except Exception as e:
            return False, f"Database error: {e}"

    def can_access_course(self, course_id: str, user_identifier: Optional[str] = None, 
                         session_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Optimized access check"""
        if not self._ensure_connection():
            return False, "Database connection error"
        
        try:
            if self.courses_collection is not None:
                # Only get necessary fields
                course = self.courses_collection.find_one(
                    {"course_id": course_id},
                    {"is_public": 1, "creator": 1, "session_id": 1, "is_guest": 1}
                )
                
                if not course:
                    return False, "Course not found"
                
                if course.get("is_public", True):
                    return True, None
                
                if user_identifier and course.get("creator") == user_identifier:
                    return True, None
                
                if session_id and course.get("session_id") == session_id and course.get("is_guest"):
                    return True, None
                
                return False, "Private course - no access"
            else:
                return False, "Database connection error"
            
        except Exception as e:
            return False, f"Database error: {e}"

    def _add_to_user_courses(self, user_identifier: str, course_id: str, is_guest: bool):
        """Optimized user course tracking"""
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
        except:
            pass

    def _count_questions(self, course_data: Optional[List[Dict]]) -> int:
        """Optimized question counting"""
        if not course_data:
            return 0
        
        total = 0
        for section_dict in course_data:
            if isinstance(section_dict, dict):
                # Count main section questions
                quiz_list = section_dict.get('quiz')
                if isinstance(quiz_list, list):
                    total += len(quiz_list)
                
                # Count subsection questions
                subsections_list = section_dict.get('subsections')
                if isinstance(subsections_list, list):
                    total += self._count_questions(subsections_list)
        return total

# Singleton pattern for better performance
_course_manager = None

def get_course_manager() -> MongoCourseManager:
    """Get singleton course manager instance"""
    global _course_manager
    if _course_manager is None:
        _course_manager = MongoCourseManager()
    return _course_manager

def get_session_id() -> str:
    """Get or create session ID for guest users"""
    if 'guest_session_id' not in st.session_state:
        st.session_state.guest_session_id = str(uuid.uuid4())
    return st.session_state.guest_session_id