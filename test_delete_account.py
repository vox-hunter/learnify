#!/usr/bin/env python3
"""
Test script for delete account functionality
"""
import sys
import os

# Add the Quiz_app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Quiz_app'))

try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import MongoCourseManager
    
    def test_delete_account():
        print("Testing delete account functionality...")
        
        # Initialize managers
        auth_manager = MongoAuthManager()
        course_manager = MongoCourseManager()
        
        # Test data
        test_username = "test_delete_user"
        test_email = "test_delete@example.com"
        test_password = "test123"
        
        print(f"1. Creating test user: {test_username}")
        
        # Create test user
        success, message = auth_manager.create_user(test_username, test_password, test_email, "Test User")
        if success:
            print(f"   ✅ User created successfully")
        else:
            print(f"   ❌ Failed to create user: {message}")
            return
        
        # Create a test course for the user
        print(f"2. Creating test course for user")
        test_course = {
            "course_id": "test_course_123",
            "title": "Test Course",
            "creator": test_username,
            "is_guest": False,
            "created_at": "2025-01-01",
            "sections": []
        }
        
        # Insert course directly
        try:
            course_manager.courses_collection.insert_one(test_course)
            print(f"   ✅ Test course created")
        except Exception as e:
            print(f"   ⚠️ Could not create test course: {e}")
        
        # Test deletion with wrong confirmation
        print(f"3. Testing deletion with wrong confirmation")
        success, message = auth_manager.delete_user_account(test_username, "wrong_username")
        if not success and "confirmation does not match" in message:
            print(f"   ✅ Correctly rejected wrong confirmation")
        else:
            print(f"   ❌ Should have rejected wrong confirmation")
        
        # Test deletion with correct confirmation
        print(f"4. Testing deletion with correct confirmation")
        success, message = auth_manager.delete_user_account(test_username, test_username)
        if success:
            print(f"   ✅ Account deleted successfully: {message}")
        else:
            print(f"   ❌ Failed to delete account: {message}")
        
        # Verify user is deleted
        print(f"5. Verifying user deletion")
        user = auth_manager.find_user_by_username(test_username)
        if user is None:
            print(f"   ✅ User successfully deleted from database")
        else:
            print(f"   ❌ User still exists in database")
        
        # Verify courses are deleted
        print(f"6. Verifying course deletion")
        courses, _ = course_manager.get_user_courses(test_username)
        if not courses or len(courses) == 0:
            print(f"   ✅ User courses successfully deleted")
        else:
            print(f"   ❌ User courses still exist: {len(courses)} courses found")
        
        print("Test completed!")

    if __name__ == "__main__":
        test_delete_account()
        
except ImportError as e:
    print(f"❌ Could not import required modules: {e}")
    print("Make sure you're running this from the learnify directory")
except Exception as e:
    print(f"❌ Error during testing: {e}")
