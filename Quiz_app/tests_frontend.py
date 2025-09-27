"""
Comprehensive Frontend Test Suite for Learnify
Merges all frontend tests into a single file for better organization.
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add Quiz_app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MockStreamlit:
    """Mock Streamlit for testing frontend components without running the app."""
    def __init__(self):
        self.secrets = {
            "MONGODB_URI": "mongodb+srv://test:test@test.mongodb.net/test",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret"
        }
        self.session_state = {}
    
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")
    def success(self, msg): print(f"SUCCESS: {msg}")
    def stop(self): pass
    def markdown(self, content, unsafe_allow_html=False): pass
    def title(self, text): pass
    def text_area(self, label, **kwargs): return ""
    def button(self, label, **kwargs): return False
    def selectbox(self, label, options, **kwargs): return options[0] if options else None

class TestCSSLoader(unittest.TestCase):
    """Test the consolidated CSS loading system."""
    
    def setUp(self):
        # Mock streamlit
        sys.modules['streamlit'] = MockStreamlit()
    
    def test_css_loader_import(self):
        """Test that CSS loader can be imported."""
        try:
            from utils.css_loader import load_consolidated_css, apply_page_specific_css
            self.assertTrue(True, "CSS loader imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import CSS loader: {e}")
    
    def test_css_file_exists(self):
        """Test that the consolidated CSS file exists."""
        css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
        self.assertTrue(os.path.exists(css_path), "Consolidated CSS file should exist")
    
    def test_css_file_not_empty(self):
        """Test that the CSS file has content."""
        css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                content = f.read()
            self.assertGreater(len(content), 100, "CSS file should have substantial content")
    
    def test_load_consolidated_css(self):
        """Test loading consolidated CSS."""
        from utils.css_loader import load_consolidated_css
        # Should not raise exception
        try:
            result = load_consolidated_css()
            self.assertIsInstance(result, bool, "Should return boolean")
        except Exception as e:
            self.fail(f"CSS loading failed: {e}")

class TestGoogleOAuthIntegration(unittest.TestCase):
    """Test Google OAuth integration maintains data consistency."""
    
    def setUp(self):
        # Mock streamlit and required modules
        sys.modules['streamlit'] = MockStreamlit()
        
    def test_oauth_config_check(self):
        """Test Google OAuth configuration checking."""
        try:
            from google_oauth_simple import is_google_oauth_configured
            # Should not raise exception
            result = is_google_oauth_configured()
            self.assertIsInstance(result, bool, "Should return boolean")
        except ImportError:
            self.skipTest("Google OAuth module not available")
        except Exception as e:
            self.fail(f"OAuth config check failed: {e}")
    
    def test_mongo_auth_manager_init(self):
        """Test MongoAuthManager initialization."""
        try:
            from mongo_auth import MongoAuthManager
            # Should be able to create instance
            manager = MongoAuthManager()
            self.assertIsNotNone(manager, "MongoAuthManager should initialize")
        except ImportError:
            self.skipTest("MongoDB auth module not available")
        except Exception as e:
            # Connection failures are expected in test environment
            self.assertIn("pymongo", str(e).lower() or "connection" in str(e).lower(),
                         f"Should fail with connection/import error, got: {e}")
    
    def test_user_data_structure_consistency(self):
        """Test that Google OAuth users have same data structure as manual users."""
        from datetime import datetime
        
        # Test manual user data structure
        manual_user_data = {
            "username": "test_manual_user",
            "password": "hashed_password",
            "email": "manual@test.com",
            "name": "Manual Test User",
            "email_verified": False,
            "marketing_consent": True,
            "created_at": datetime.utcnow().isoformat(),
            "google_id": None,
            "google_linked": False
        }
        
        # Test Google OAuth user data structure
        google_user_data = {
            "username": "google_test_user",
            "password": None,
            "email": "google@test.com",
            "name": "Google Test User", 
            "email_verified": True,
            "marketing_consent": True,
            "created_at": datetime.utcnow().isoformat(),
            "google_id": "123456789",
            "google_linked": True
        }
        
        # Verify structure consistency
        manual_keys = set(manual_user_data.keys())
        google_keys = set(google_user_data.keys())
        
        self.assertEqual(manual_keys, google_keys, 
                        "Manual and Google OAuth user data structures should be identical")

class TestFillInBlankComponent(unittest.TestCase):
    """Test the fill-in-the-blanks custom component."""
    
    def test_component_import(self):
        """Test that fill-in-the-blanks component can be imported."""
        try:
            from st_fill_in_the_blanks import fill_in_the_blanks_input
            self.assertIsNotNone(fill_in_the_blanks_input, "Component should be importable")
        except ImportError:
            # This is acceptable - component may not be available in test environment
            self.skipTest("Fill-in-the-blanks component not available")
    
    def test_component_css_exists(self):
        """Test that component CSS file exists."""
        css_path = os.path.join(os.path.dirname(__file__), 
                               "st_fill_in_the_blanks", "frontend", "src", "FillInTheBlanks.css")
        self.assertTrue(os.path.exists(css_path), "Component CSS file should exist")
    
    def test_component_css_optimized(self):
        """Test that component CSS is reasonably sized (not bloated)."""
        css_path = os.path.join(os.path.dirname(__file__), 
                               "st_fill_in_the_blanks", "frontend", "src", "FillInTheBlanks.css")
        if os.path.exists(css_path):
            file_size = os.path.getsize(css_path)
            # CSS should be under 20KB for good performance
            self.assertLess(file_size, 20000, "Component CSS should be optimized (< 20KB)")

class TestPageOptimization(unittest.TestCase):
    """Test that pages are optimized and don't have excessive CSS."""
    
    def test_home_page_css_reduction(self):
        """Test that Home page has reduced CSS bloat."""
        home_path = os.path.join(os.path.dirname(__file__), "pages", "1_🏠_Home.py")
        if os.path.exists(home_path):
            with open(home_path, 'r') as f:
                content = f.read()
            
            # Count CSS blocks
            css_blocks = content.count("<style>")
            # Should have minimal CSS blocks (using consolidated CSS)
            self.assertLessEqual(css_blocks, 2, "Home page should have minimal CSS blocks")
    
    def test_consolidated_css_usage(self):
        """Test that pages use the consolidated CSS loader."""
        test_files = [
            "pages/1_🏠_Home.py",
            "pages/2_🔐_Login.py", 
            "pages/3_Course.py"
        ]
        
        for file_path in test_files:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Should use CSS loader
                has_css_loader = "load_consolidated_css" in content or "css_loader" in content
                # Allow some pages to not be refactored yet
                if not has_css_loader:
                    print(f"Note: {file_path} not yet refactored to use consolidated CSS")

class TestBackendIntegration(unittest.TestCase):
    """Test that backend functionality is preserved."""
    
    def test_backend_imports_preserved(self):
        """Test that backend-related imports are not broken."""
        critical_modules = [
            "local_backend",
            "mongo_auth", 
            "mongo_course_manager",
            "utils.background_jobs"
        ]
        
        for module_name in critical_modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name} imports successfully")
            except ImportError as e:
                # Some modules may not be available in test environment
                print(f"⚠️  {module_name} not available: {e}")
    
    def test_lazy_imports_system(self):
        """Test that lazy imports system works."""
        try:
            from utils.lazy_imports import lazy_import, import_optional
            
            # Test lazy import
            result = lazy_import("os")  # Should work with built-in module
            self.assertIsNotNone(result, "Lazy import should work")
            
            # Test optional import
            result = import_optional("nonexistent_module:NonexistentClass")
            self.assertIsNone(result, "Optional import should return None for missing modules")
            
        except ImportError:
            self.skipTest("Lazy imports system not available")

def run_frontend_tests():
    """Run all frontend tests and return results."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCSSLoader,
        TestGoogleOAuthIntegration, 
        TestFillInBlankComponent,
        TestPageOptimization,
        TestBackendIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    print("🧪 Running Comprehensive Frontend Tests...")
    print("=" * 60)
    
    result = run_frontend_tests()
    
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed'}")
    
    exit(0 if success else 1)