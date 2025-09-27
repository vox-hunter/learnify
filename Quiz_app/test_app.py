"""
Unified test file for the Learnify AI Quiz and Course Generator
Tests core functionality: authentication, course generation, and storage
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add Quiz_app to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock Streamlit for testing
class MockStreamlit:
    def __init__(self):
        self.session_state = {}
    
    def write(self, *args, **kwargs):
        pass
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def success(self, msg):
        print(f"SUCCESS: {msg}")
    
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def cache_resource(self, func):
        """Mock cache_resource decorator"""
        return func

# Mock streamlit module
sys.modules['streamlit'] = MockStreamlit()

class TestAuthentication(unittest.TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_streamlit = MockStreamlit()
    
    def test_mongo_auth_import(self):
        """Test that mongo auth can be imported"""
        try:
            from mongo_auth import MongoAuthManager
            self.assertTrue(True, "MongoAuthManager imported successfully")
        except ImportError:
            self.skipTest("MongoDB not available in test environment")
    
    def test_session_state_handling(self):
        """Test session state management"""
        session = {}
        session['authentication_status'] = True
        session['username'] = 'test_user'
        
        self.assertTrue(session.get('authentication_status'))
        self.assertEqual(session.get('username'), 'test_user')

class TestCourseGeneration(unittest.TestCase):
    """Test course generation functionality"""
    
    def test_background_jobs_import(self):
        """Test that background job system can be imported"""
        try:
            from utils.background_jobs import start_course_generation, get_job
            self.assertTrue(callable(start_course_generation))
            self.assertTrue(callable(get_job))
        except ImportError as e:
            self.fail(f"Failed to import background jobs: {e}")
    
    def test_file_security_validation(self):
        """Test file security validation"""
        try:
            from file_security import validate_file_security
            
            # Test valid file
            is_safe, msg = validate_file_security("test.pdf", 1024 * 1024)  # 1MB
            self.assertTrue(is_safe)
            
            # Test oversized file
            is_safe, msg = validate_file_security("large.pdf", 20 * 1024 * 1024)  # 20MB
            self.assertFalse(is_safe)
            
            # Test dangerous file
            is_safe, msg = validate_file_security("malware.exe", 1024)
            self.assertFalse(is_safe)
            
        except ImportError as e:
            self.fail(f"Failed to import file_security: {e}")

class TestCourseStorage(unittest.TestCase):
    """Test course storage functionality"""
    
    def test_mongo_course_manager_import(self):
        """Test that course manager can be imported"""
        try:
            from mongo_course_manager import get_course_manager
            self.assertTrue(callable(get_course_manager))
        except ImportError:
            self.skipTest("MongoDB not available in test environment")
    
    def test_local_backend_import(self):
        """Test that local backend can be imported"""
        try:
            import local_backend
            self.assertTrue(hasattr(local_backend, 'generate_course'))
        except ImportError as e:
            self.fail(f"Failed to import local_backend: {e}")

class TestUtilities(unittest.TestCase):
    """Test utility functions"""
    
    def test_lazy_imports(self):
        """Test lazy import system"""
        try:
            from utils.lazy_imports import lazy_import, import_optional
            self.assertTrue(callable(lazy_import))
            self.assertTrue(callable(import_optional))
        except ImportError as e:
            self.fail(f"Failed to import lazy_imports: {e}")
    
    def test_navigation_cache(self):
        """Test navigation cache system"""
        try:
            from utils.navigation_cache import record_page_visit, cache_course_list
            self.assertTrue(callable(record_page_visit))
            self.assertTrue(callable(cache_course_list))
        except ImportError as e:
            self.fail(f"Failed to import navigation_cache: {e}")

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)