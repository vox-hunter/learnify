import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConfigurationError, ConnectionFailure, DuplicateKeyError
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Literal

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

load_dotenv()


def _log_error(message: str) -> None:
    """Log errors with or without Streamlit support."""
    if HAS_STREAMLIT:
        st.error(message)
    else:
        print(f"ERROR: {message}")


def _deep_merge_dicts(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge updates into base dict, preserving nested structures."""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


MONGODB_URI = None
DATABASE_NAME = "learnify_courses"

if HAS_STREAMLIT:
    try:
        MONGODB_URI = st.secrets["MONGODB_URI"]
        DATABASE_NAME = st.secrets.get("DATABASE_NAME", "learnify_courses")
    except (KeyError, AttributeError):
        MONGODB_URI = os.getenv("MONGODB_URI")
        DATABASE_NAME = os.getenv("DATABASE_NAME", "learnify_courses")
else:
    MONGODB_URI = os.getenv("MONGODB_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "learnify_courses")


CourseState = Literal["initialized", "decomposed", "sections_approved", "generating", "completed"]
SectionState = Literal["proposed", "approved", "generating", "generated", "refined"]


class AILoomLesson(BaseModel):
    lesson_id: str
    lesson_title: str
    content: str
    order: int
    estimated_duration_minutes: Optional[int] = None
    learning_objectives: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AILoomSection(BaseModel):
    section_id: str
    course_id: str
    section_title: str
    description: str
    order: int
    state: SectionState
    key_learning_goals: List[str] = Field(default_factory=list)
    main_concepts: List[str] = Field(default_factory=list)
    lesson_count: int = 0
    has_quiz: bool = False
    has_exercises: bool = False
    created_at: datetime
    updated_at: datetime


class AILoomCourse(BaseModel):
    course_id: str
    topic: str
    description: str
    state: CourseState
    creator: str
    is_guest: bool
    session_id: Optional[str] = None
    section_count: int = 0
    total_lessons: int = 0
    difficulty_level: Optional[str] = None
    estimated_duration_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AILoomCourseManager:
    """MongoDB manager for AI Loom's hierarchical course structure."""

    def __init__(self) -> None:
        """Initialize MongoDB connection and create collections/indexes."""
        if not MONGODB_URI:
            raise ConfigurationError("MONGODB_URI environment variable not set")

        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DATABASE_NAME]

            # Test connection
            self.client.admin.command("ping")

            # Get collection references
            self.ai_loom_courses = self.db["ai_loom_courses"]
            self.ai_loom_sections = self.db["ai_loom_sections"]
            self.ai_loom_lessons = self.db["ai_loom_lessons"]
            self.ai_loom_user_courses = self.db["ai_loom_user_courses"]

            self._create_indexes()

        except ConfigurationError as e:
            _log_error(f"MongoDB Configuration Error: {str(e)}")
            raise
        except ConnectionFailure as e:
            _log_error(f"MongoDB Connection Error: {str(e)}")
            raise
        except Exception as e:
            _log_error(f"Unexpected error initializing MongoDB: {str(e)}")
            raise

    def _create_indexes(self) -> None:
        """Create indexes for all collections."""
        try:
            # ai_loom_courses indexes
            self.ai_loom_courses.create_index("course_id", unique=True)
            self.ai_loom_courses.create_index("creator")
            self.ai_loom_courses.create_index("session_id")
            self.ai_loom_courses.create_index("state")
            self.ai_loom_courses.create_index("created_at")
            self.ai_loom_courses.create_index([("creator", ASCENDING), ("state", ASCENDING)])

            # ai_loom_sections indexes
            self.ai_loom_sections.create_index("section_id", unique=True)
            self.ai_loom_sections.create_index("course_id")
            self.ai_loom_sections.create_index("state")
            self.ai_loom_sections.create_index("order")
            self.ai_loom_sections.create_index([("course_id", ASCENDING), ("order", ASCENDING)])

            # ai_loom_lessons indexes
            self.ai_loom_lessons.create_index("lesson_id", unique=True)
            self.ai_loom_lessons.create_index("section_id")
            self.ai_loom_lessons.create_index("order")
            self.ai_loom_lessons.create_index([("section_id", ASCENDING), ("order", ASCENDING)])

            # ai_loom_user_courses indexes
            self.ai_loom_user_courses.create_index(
                [("user_identifier", ASCENDING), ("course_id", ASCENDING)], unique=True
            )

        except Exception as e:
            _log_error(f"Error creating indexes: {str(e)}")

    def _ensure_connection(self) -> bool:
        """Verify MongoDB connection is active."""
        try:
            if self.client is None or self.db is None:
                return False
            self.client.admin.command("ping")
            return True
        except Exception as e:
            _log_error(f"Connection check failed: {str(e)}")
            return False

    def generate_course_id(self) -> str:
        """Generate a unique course ID."""
        return str(ObjectId())

    def generate_section_id(self) -> str:
        """Generate a unique section ID."""
        return str(ObjectId())

    def generate_lesson_id(self) -> str:
        """Generate a unique lesson ID."""
        return str(ObjectId())

    def create_course(
        self,
        topic: str,
        description: str,
        creator: str,
        is_guest: bool = False,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Create a new course."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            course_id = self.generate_course_id()
            now = datetime.utcnow()

            # Handle metadata serialization
            if metadata is None:
                metadata = {}
            else:
                try:
                    metadata_copy = {}
                    for key, value in metadata.items():
                        if hasattr(value, "model_dump"):
                            metadata_copy[key] = value.model_dump()
                        elif hasattr(value, "dict"):
                            metadata_copy[key] = value.dict()
                        else:
                            metadata_copy[key] = value
                    metadata = metadata_copy
                except Exception as e:
                    _log_error(f"Error serializing metadata: {str(e)}")
                    metadata = {}

            # For guest users, use session_id; for authenticated users, set session_id to None
            tracking_identifier = session_id if is_guest else creator
            stored_session_id = session_id if is_guest else None

            course_doc = {
                "course_id": course_id,
                "topic": topic,
                "description": description,
                "state": "initialized",
                "creator": creator,
                "is_guest": is_guest,
                "session_id": stored_session_id,
                "section_count": 0,
                "total_lessons": 0,
                "difficulty_level": None,
                "estimated_duration_hours": None,
                "created_at": now,
                "updated_at": now,
                "metadata": metadata,
            }

            self.ai_loom_courses.insert_one(course_doc)
            self._add_to_user_courses(tracking_identifier, course_id, is_guest)

            return course_id, None

        except DuplicateKeyError as e:
            return None, f"Course already exists: {str(e)}"
        except Exception as e:
            _log_error(f"Error creating course: {str(e)}")
            return None, str(e)

    def get_course(self, course_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve a course by ID."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            course = self.ai_loom_courses.find_one({"course_id": course_id})
            if not course:
                return None, "Course not found"

            course.pop("_id", None)
            return course, None

        except Exception as e:
            _log_error(f"Error retrieving course: {str(e)}")
            return None, str(e)

    def get_user_courses(
        self,
        user_identifier: str,
        is_guest: bool = False,
        session_id: Optional[str] = None,
    ) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Retrieve all courses for a user."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            if is_guest:
                query = {"session_id": session_id, "is_guest": True}
            else:
                query = {"creator": user_identifier, "is_guest": False}

            courses = list(
                self.ai_loom_courses.find(query).sort("created_at", pymongo.DESCENDING)
            )

            for course in courses:
                course.pop("_id", None)

            return courses, None

        except Exception as e:
            _log_error(f"Error retrieving user courses: {str(e)}")
            return None, str(e)

    def update_course_state(
        self,
        course_id: str,
        new_state: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Update course state with ownership verification and transition validation."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Verify ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return False, "Course not found or access denied"

            # Validate state
            valid_states: List[str] = [
                "initialized",
                "decomposed",
                "sections_approved",
                "generating",
                "completed",
            ]
            if new_state not in valid_states:
                return False, f"Invalid state: {new_state}"

            # Enforce state transition rules
            current_state = course.get("state")
            if not self.can_transition_course_state(current_state, new_state):
                return False, f"Cannot transition from {current_state} to {new_state}"

            self.ai_loom_courses.update_one(
                {"course_id": course_id},
                {
                    "$set": {
                        "state": new_state,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            return True, None

        except Exception as e:
            _log_error(f"Error updating course state: {str(e)}")
            return False, str(e)

    def delete_course(
        self, course_id: str, user_identifier: str, is_guest: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Delete a course and all associated sections and lessons."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Verify ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return False, "Course not found or access denied"

            # Collect all section IDs
            sections = list(self.ai_loom_sections.find({"course_id": course_id}))
            section_ids = [section["section_id"] for section in sections]

            # Delete all lessons with set-based delete
            if section_ids:
                self.ai_loom_lessons.delete_many({"section_id": {"$in": section_ids}})

            # Delete all sections
            self.ai_loom_sections.delete_many({"course_id": course_id})

            # Delete course
            self.ai_loom_courses.delete_one({"course_id": course_id})

            # Delete from user tracking
            self.ai_loom_user_courses.delete_one(
                {"user_identifier": user_identifier, "course_id": course_id}
            )

            return True, None

        except Exception as e:
            _log_error(f"Error deleting course: {str(e)}")
            return False, str(e)

    def create_section(
        self,
        course_id: str,
        section_title: str,
        description: str,
        order: int,
        key_learning_goals: List[str],
        main_concepts: List[str],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Create a new section in a course."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return None, "Course not found or access denied"

            section_id = self.generate_section_id()
            now = datetime.utcnow()

            section_doc = {
                "section_id": section_id,
                "course_id": course_id,
                "section_title": section_title,
                "description": description,
                "order": order,
                "state": "proposed",
                "key_learning_goals": key_learning_goals,
                "main_concepts": main_concepts,
                "lesson_count": 0,
                "has_quiz": False,
                "has_exercises": False,
                "created_at": now,
                "updated_at": now,
            }

            self.ai_loom_sections.insert_one(section_doc)

            # Increment course section count
            self.ai_loom_courses.update_one(
                {"course_id": course_id}, {"$inc": {"section_count": 1}}
            )

            return section_id, None

        except Exception as e:
            _log_error(f"Error creating section: {str(e)}")
            return None, str(e)

    def get_section(self, section_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve a section by ID."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return None, "Section not found"

            section.pop("_id", None)
            return section, None

        except Exception as e:
            _log_error(f"Error retrieving section: {str(e)}")
            return None, str(e)

    def get_course_sections(
        self,
        course_id: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Retrieve all sections for a course."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Verify course access
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return None, "Course not found or access denied"

            sections = list(
                self.ai_loom_sections.find({"course_id": course_id}).sort("order", ASCENDING)
            )

            for section in sections:
                section.pop("_id", None)

            return sections, None

        except Exception as e:
            _log_error(f"Error retrieving course sections: {str(e)}")
            return None, str(e)

    def update_section_state(
        self,
        section_id: str,
        new_state: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Update section state with ownership verification and transition validation."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return False, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return False, "Access denied"

            # Validate state
            valid_states: List[str] = ["proposed", "approved", "generating", "generated", "refined"]
            if new_state not in valid_states:
                return False, f"Invalid state: {new_state}"

            # Enforce state transition rules
            current_state = section.get("state")
            if not self.can_transition_section_state(current_state, new_state):
                return False, f"Cannot transition from {current_state} to {new_state}"

            self.ai_loom_sections.update_one(
                {"section_id": section_id},
                {
                    "$set": {
                        "state": new_state,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            return True, None

        except Exception as e:
            _log_error(f"Error updating section state: {str(e)}")
            return False, str(e)

    def update_section_content(
        self,
        section_id: str,
        updates: Dict[str, Any],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Update section content with ownership verification."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return False, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return False, "Access denied"

            # Filter allowed fields
            allowed_fields = {
                "section_title",
                "description",
                "key_learning_goals",
                "main_concepts",
                "has_quiz",
                "has_exercises",
            }
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

            # Return early if no allowed fields present
            if not filtered_updates:
                return True, None

            filtered_updates["updated_at"] = datetime.utcnow()

            self.ai_loom_sections.update_one(
                {"section_id": section_id}, {"$set": filtered_updates}
            )

            return True, None

        except Exception as e:
            _log_error(f"Error updating section content: {str(e)}")
            return False, str(e)

    def delete_section(
        self, section_id: str, user_identifier: str, is_guest: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Delete a section and all associated lessons."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return False, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return False, "Access denied"

            # Delete all lessons in section
            self.ai_loom_lessons.delete_many({"section_id": section_id})

            # Delete section
            self.ai_loom_sections.delete_one({"section_id": section_id})

            # Decrement course counts
            self.ai_loom_courses.update_one(
                {"course_id": section["course_id"]},
                {
                    "$inc": {
                        "section_count": -1,
                        "total_lessons": -section.get("lesson_count", 0),
                    }
                },
            )

            return True, None

        except Exception as e:
            _log_error(f"Error deleting section: {str(e)}")
            return False, str(e)

    def bulk_create_sections(
        self,
        course_id: str,
        sections_data: List[Dict],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[List[str]], Optional[str]]:
        """Bulk create sections for a course."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return None, "Course not found or access denied"

            now = datetime.utcnow()
            section_ids = []
            section_docs = []

            for idx, section_data in enumerate(sections_data):
                section_id = self.generate_section_id()
                section_ids.append(section_id)

                section_doc = {
                    "section_id": section_id,
                    "course_id": course_id,
                    "section_title": section_data.get("section_title", ""),
                    "description": section_data.get("description", ""),
                    "order": section_data.get("order", idx),
                    "state": "proposed",
                    "key_learning_goals": section_data.get("key_learning_goals", []),
                    "main_concepts": section_data.get("main_concepts", []),
                    "lesson_count": 0,
                    "has_quiz": False,
                    "has_exercises": False,
                    "created_at": now,
                    "updated_at": now,
                }
                section_docs.append(section_doc)

            if section_docs:
                self.ai_loom_sections.insert_many(section_docs)

            # Update course section count
            self.ai_loom_courses.update_one(
                {"course_id": course_id}, {"$inc": {"section_count": len(section_ids)}}
            )

            return section_ids, None

        except Exception as e:
            _log_error(f"Error bulk creating sections: {str(e)}")
            return None, str(e)

    def approve_sections(
        self,
        course_id: str,
        section_ids: List[str],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Approve multiple sections and update course state."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return False, "Course not found or access denied"

            # Update sections state with course_id constraint
            self.ai_loom_sections.update_many(
                {"course_id": course_id, "section_id": {"$in": section_ids}},
                {
                    "$set": {
                        "state": "approved",
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            # Update course state
            self.ai_loom_courses.update_one(
                {"course_id": course_id},
                {
                    "$set": {
                        "state": "sections_approved",
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            return True, None

        except Exception as e:
            _log_error(f"Error approving sections: {str(e)}")
            return False, str(e)

    def create_lesson(
        self,
        section_id: str,
        lesson_title: str,
        content: str,
        order: int,
        learning_objectives: List[str],
        estimated_duration_minutes: Optional[int],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Create a new lesson in a section."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return None, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return None, "Access denied"

            lesson_id = self.generate_lesson_id()
            now = datetime.utcnow()

            lesson_doc = {
                "lesson_id": lesson_id,
                "section_id": section_id,
                "lesson_title": lesson_title,
                "content": content,
                "order": order,
                "estimated_duration_minutes": estimated_duration_minutes,
                "learning_objectives": learning_objectives,
                "created_at": now,
                "updated_at": now,
            }

            self.ai_loom_lessons.insert_one(lesson_doc)

            # Increment section lesson count and course total lessons
            self.ai_loom_sections.update_one(
                {"section_id": section_id}, {"$inc": {"lesson_count": 1}}
            )
            self.ai_loom_courses.update_one(
                {"course_id": section["course_id"]}, {"$inc": {"total_lessons": 1}}
            )

            return lesson_id, None

        except Exception as e:
            _log_error(f"Error creating lesson: {str(e)}")
            return None, str(e)

    def get_lesson(self, lesson_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve a lesson by ID."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            lesson = self.ai_loom_lessons.find_one({"lesson_id": lesson_id})
            if not lesson:
                return None, "Lesson not found"

            lesson.pop("_id", None)
            return lesson, None

        except Exception as e:
            _log_error(f"Error retrieving lesson: {str(e)}")
            return None, str(e)

    def get_section_lessons(
        self,
        section_id: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Retrieve all lessons for a section."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return None, "Section not found"

            # Verify course access
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return None, "Access denied"

            lessons = list(
                self.ai_loom_lessons.find({"section_id": section_id}).sort("order", ASCENDING)
            )

            for lesson in lessons:
                lesson.pop("_id", None)

            return lessons, None

        except Exception as e:
            _log_error(f"Error retrieving section lessons: {str(e)}")
            return None, str(e)

    def update_lesson_content(
        self,
        lesson_id: str,
        updates: Dict[str, Any],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Update lesson content with ownership verification."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Get lesson
            lesson = self.ai_loom_lessons.find_one({"lesson_id": lesson_id})
            if not lesson:
                return False, "Lesson not found"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": lesson["section_id"]})
            if not section:
                return False, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return False, "Access denied"

            # Filter allowed fields
            allowed_fields = {
                "lesson_title",
                "content",
                "learning_objectives",
                "estimated_duration_minutes",
            }
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

            # Return early if no allowed fields present
            if not filtered_updates:
                return True, None

            filtered_updates["updated_at"] = datetime.utcnow()

            self.ai_loom_lessons.update_one(
                {"lesson_id": lesson_id}, {"$set": filtered_updates}
            )

            return True, None

        except Exception as e:
            _log_error(f"Error updating lesson content: {str(e)}")
            return False, str(e)

    def delete_lesson(
        self, lesson_id: str, user_identifier: str, is_guest: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Delete a lesson."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Get lesson
            lesson = self.ai_loom_lessons.find_one({"lesson_id": lesson_id})
            if not lesson:
                return False, "Lesson not found"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": lesson["section_id"]})
            if not section:
                return False, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return False, "Access denied"

            # Delete lesson
            self.ai_loom_lessons.delete_one({"lesson_id": lesson_id})

            # Decrement section lesson count and course total lessons
            self.ai_loom_sections.update_one(
                {"section_id": lesson["section_id"]}, {"$inc": {"lesson_count": -1}}
            )
            self.ai_loom_courses.update_one(
                {"course_id": section["course_id"]}, {"$inc": {"total_lessons": -1}}
            )

            return True, None

        except Exception as e:
            _log_error(f"Error deleting lesson: {str(e)}")
            return False, str(e)

    def bulk_create_lessons(
        self,
        section_id: str,
        lessons_data: List[Dict],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[List[str]], Optional[str]]:
        """Bulk create lessons for a section."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Get section
            section = self.ai_loom_sections.find_one({"section_id": section_id})
            if not section:
                return None, "Section not found"

            # Verify course ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": section["course_id"], "creator": user_identifier}
                )

            if not course:
                return None, "Access denied"

            now = datetime.utcnow()
            lesson_ids = []
            lesson_docs = []

            for idx, lesson_data in enumerate(lessons_data):
                lesson_id = self.generate_lesson_id()
                lesson_ids.append(lesson_id)

                lesson_doc = {
                    "lesson_id": lesson_id,
                    "section_id": section_id,
                    "lesson_title": lesson_data.get("lesson_title", ""),
                    "content": lesson_data.get("content", ""),
                    "order": lesson_data.get("order", idx),
                    "estimated_duration_minutes": lesson_data.get(
                        "estimated_duration_minutes"
                    ),
                    "learning_objectives": lesson_data.get("learning_objectives", []),
                    "created_at": now,
                    "updated_at": now,
                }
                lesson_docs.append(lesson_doc)

            if lesson_docs:
                self.ai_loom_lessons.insert_many(lesson_docs)

            # Update section lesson count and course total lessons
            self.ai_loom_sections.update_one(
                {"section_id": section_id}, {"$inc": {"lesson_count": len(lesson_ids)}}
            )
            self.ai_loom_courses.update_one(
                {"course_id": section["course_id"]}, {"$inc": {"total_lessons": len(lesson_ids)}}
            )

            return lesson_ids, None

        except Exception as e:
            _log_error(f"Error bulk creating lessons: {str(e)}")
            return None, str(e)

    def get_course_hierarchy(
        self,
        course_id: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve full course hierarchy with sections and lessons."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Get course
            course_result, error = self.get_course(course_id)
            if error:
                return None, error

            # Verify access
            if is_guest:
                if course_result["session_id"] != user_identifier or not course_result["is_guest"]:
                    return None, "Access denied"
            else:
                if course_result["creator"] != user_identifier or course_result["is_guest"]:
                    return None, "Access denied"

            # Get sections
            sections_result, error = self.get_course_sections(course_id, user_identifier, is_guest)
            if error:
                return None, error

            # Get lessons for each section
            sections_with_lessons = []
            for section in sections_result:
                lessons_result, error = self.get_section_lessons(
                    section["section_id"], user_identifier, is_guest
                )
                if error:
                    return None, error

                section_data = section.copy()
                section_data["lessons"] = lessons_result
                sections_with_lessons.append(section_data)

            hierarchy = {"course": course_result, "sections": sections_with_lessons}

            return hierarchy, None

        except Exception as e:
            _log_error(f"Error retrieving course hierarchy: {str(e)}")
            return None, str(e)

    def get_course_with_sections(
        self,
        course_id: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve course with sections (without lessons)."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Get course
            course_result, error = self.get_course(course_id)
            if error:
                return None, error

            # Verify access
            if is_guest:
                if course_result["session_id"] != user_identifier or not course_result["is_guest"]:
                    return None, "Access denied"
            else:
                if course_result["creator"] != user_identifier or course_result["is_guest"]:
                    return None, "Access denied"

            # Get sections
            sections_result, error = self.get_course_sections(course_id, user_identifier, is_guest)
            if error:
                return None, error

            hierarchy = {"course": course_result, "sections": sections_result}

            return hierarchy, None

        except Exception as e:
            _log_error(f"Error retrieving course with sections: {str(e)}")
            return None, str(e)

    def _add_to_user_courses(
        self, user_identifier: str, course_id: str, is_guest: bool
    ) -> None:
        """Internal method to track course in user tracking collection."""
        try:
            self.ai_loom_user_courses.update_one(
                {"user_identifier": user_identifier, "course_id": course_id},
                {
                    "$set": {
                        "user_identifier": user_identifier,
                        "course_id": course_id,
                        "is_guest": is_guest,
                        "added_at": datetime.utcnow(),
                    }
                },
                upsert=True,
            )
        except Exception as e:
            _log_error(f"Error adding course to user tracking: {str(e)}")

    def transfer_guest_courses(
        self, session_id: str, new_user_identifier: str
    ) -> Tuple[int, Optional[str]]:
        """Transfer all guest courses to an authenticated user."""
        try:
            if not self._ensure_connection():
                return 0, "Database connection failed"

            # Update courses
            result = self.ai_loom_courses.update_many(
                {"session_id": session_id, "is_guest": True},
                {
                    "$set": {
                        "creator": new_user_identifier,
                        "is_guest": False,
                        "updated_at": datetime.utcnow(),
                    },
                    "$unset": {"session_id": ""},
                },
            )

            count_transferred = result.modified_count

            # Migrate user tracking entries instead of deleting
            self.ai_loom_user_courses.update_many(
                {"user_identifier": session_id, "is_guest": True},
                {
                    "$set": {
                        "user_identifier": new_user_identifier,
                        "is_guest": False,
                    }
                },
            )

            return count_transferred, None

        except Exception as e:
            _log_error(f"Error transferring guest courses: {str(e)}")
            return 0, str(e)

    def get_course_state(self, course_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Retrieve just the state field of a course."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            course = self.ai_loom_courses.find_one(
                {"course_id": course_id}, {"state": 1}
            )
            if not course:
                return None, "Course not found"

            return course.get("state"), None

        except Exception as e:
            _log_error(f"Error retrieving course state: {str(e)}")
            return None, str(e)

    def can_transition_course_state(self, from_state: str, to_state: str) -> bool:
        """Validate course state transitions."""
        valid_transitions = {
            "initialized": ["decomposed"],
            "decomposed": ["sections_approved"],
            "sections_approved": ["generating"],
            "generating": ["completed"],
            "completed": [],
        }

        return to_state in valid_transitions.get(from_state, [])

    def can_transition_section_state(self, from_state: str, to_state: str) -> bool:
        """Validate section state transitions."""
        valid_transitions = {
            "proposed": ["approved"],
            "approved": ["generating"],
            "generating": ["generated"],
            "generated": ["refined"],
            "refined": [],
        }

        return to_state in valid_transitions.get(from_state, [])

    def update_course_metadata(
        self,
        course_id: str,
        metadata: Dict[str, Any],
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Update course metadata with deep merging."""
        try:
            if not self._ensure_connection():
                return False, "Database connection failed"

            # Verify ownership
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return False, "Course not found or access denied"

            # Deep merge metadata
            existing_metadata = course.get("metadata", {})
            updated_metadata = _deep_merge_dicts(existing_metadata, metadata)

            self.ai_loom_courses.update_one(
                {"course_id": course_id},
                {
                    "$set": {
                        "metadata": updated_metadata,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            return True, None

        except Exception as e:
            _log_error(f"Error updating course metadata: {str(e)}")
            return False, str(e)

    def get_course_metadata(
        self,
        course_id: str,
        user_identifier: str,
        is_guest: bool = False,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve course metadata with access verification."""
        try:
            if not self._ensure_connection():
                return None, "Database connection failed"

            # Verify access
            if is_guest:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "session_id": user_identifier}
                )
            else:
                course = self.ai_loom_courses.find_one(
                    {"course_id": course_id, "creator": user_identifier}
                )

            if not course:
                return None, "Course not found or access denied"

            return course.get("metadata", {}), None

        except Exception as e:
            _log_error(f"Error retrieving course metadata: {str(e)}")
            return None, str(e)


_ai_loom_manager = None


def get_ai_loom_manager() -> AILoomCourseManager:
    """Get or create singleton instance of AILoomCourseManager."""
    global _ai_loom_manager
    if _ai_loom_manager is None:
        _ai_loom_manager = AILoomCourseManager()
    return _ai_loom_manager
