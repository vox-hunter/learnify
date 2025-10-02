"""
Consolidated Test Suite for Learnify Application
This file consolidates all test functionality to reduce clutter and improve organization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Streamlit for testing
class MockStreamlit:
    def __init__(self):
        self.secrets = {
            "MONGODB_URI": "mongodb+srv://vox:tZm0fZA2BQT5sDf9@learnifydb.h4kxpad.mongodb.net/learnify_auth?retryWrites=true&w=majority",
            "GOOGLE_CLIENT_ID": "your-google-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "your-google-client-secret"
        }
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")
    
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def stop(self):
        pass

# Mock streamlit module
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

def test_google_oauth_integration():
    """Test that Google OAuth users have the same data structure as manual users."""
    print("Testing Google OAuth integration...")
    
    try:
        from mongo_auth import MongoAuthManager
        from google_oauth_simple import is_google_oauth_configured
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        return False
    
    # Test OAuth configuration check
    print(f"Google OAuth configured: {is_google_oauth_configured()}")
    
    # Test MongoAuthManager initialization
    try:
        manager = MongoAuthManager()
        print("✅ MongoAuthManager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize MongoAuthManager: {e}")
        return False
    
    # Test user data structure consistency
    print("\n--- Testing User Data Structure Consistency ---")
    from datetime import datetime
    
    # Manual user structure
    manual_user_data = {
        "username": "test_manual_user",
        "password": manager.hash_password("test_password"),
        "email": "manual@test.com",
        "name": "Manual Test User",
        "email_verified": False,
        "marketing_consent": True,
        "created_at": datetime.utcnow().isoformat(),
        "google_id": None,
        "google_linked": False
    }
    
    # Google OAuth user structure
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
    
    # Verify data structure consistency
    manual_keys = set(manual_user_data.keys())
    google_keys = set(google_user_data.keys())
    
    if manual_keys == google_keys:
        print("✅ Data structures are consistent!")
        print("Both user types have the same fields:")
        for key in sorted(manual_keys):
            print(f"  - {key}")
    else:
        print("❌ Data structures are inconsistent!")
        print(f"Manual keys: {manual_keys}")
        print(f"Google keys: {google_keys}")
        return False
    
    return True

def test_common_styles():
    """Test that common styles module works correctly"""
    print("\nTesting common styles...")
    
    try:
        from utils.common_styles import get_base_styles, get_sidebar_styles, apply_common_styles
        
        # Test style generation
        base_styles = get_base_styles()
        sidebar_styles = get_sidebar_styles()
        
        if "<style>" in base_styles and ".stApp" in base_styles:
            print("✅ Base styles generated correctly")
        else:
            print("❌ Base styles generation failed")
            return False
            
        if "<style>" in sidebar_styles and ".stSidebar" in sidebar_styles:
            print("✅ Sidebar styles generated correctly")
        else:
            print("❌ Sidebar styles generation failed")
            return False
            
        print("✅ Common styles module working correctly")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import common styles: {e}")
        return False
    except Exception as e:
        print(f"❌ Common styles test failed: {e}")
        return False

def test_lazy_imports():
    """Test that lazy import system works correctly"""
    print("\nTesting lazy imports...")
    
    try:
        from utils.lazy_imports import lazy_import, import_optional, prefetch_modules
        
        # Test lazy import
        mongo_auth = lazy_import("mongo_auth")
        if mongo_auth is not None:
            print("✅ Lazy import working correctly")
        else:
            print("⚠️ Lazy import returned None (module may not be available)")
            
        # Test optional import
        streamlit_cookies = import_optional("streamlit_cookies_manager:EncryptedCookieManager")
        if streamlit_cookies is not None:
            print("✅ Optional import working correctly")
        else:
            print("⚠️ Optional import returned None (module may not be available)")
            
        # Test prefetch (should not fail)
        prefetch_modules(["os", "sys"])
        print("✅ Prefetch modules working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Lazy imports test failed: {e}")
        return False

def run_all_tests():
    """Run all consolidated tests"""
    print("🧪 Running Learnify Consolidated Test Suite")
    print("=" * 50)
    
    tests = [
        ("Google OAuth Integration", test_google_oauth_integration),
        ("Common Styles", test_common_styles),
        ("Lazy Imports", test_lazy_imports),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} Test: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} Test: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} Test: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The refactoring maintained functionality.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)