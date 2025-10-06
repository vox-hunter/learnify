"""
Test script to verify chat course generation detection
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from api/.env
env_path = os.path.join(os.path.dirname(__file__), 'api', '.env')
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from chat_manager import ChatSessionManager

def test_course_generation():
    """Test if course generation is properly detected"""
    print("=" * 60)
    print("Testing Chat Course Generation")
    print("=" * 60)
    
    # Initialize chat manager
    manager = ChatSessionManager()
    print(f"✓ ChatSessionManager initialized")
    
    # Create a session
    session_id, chat = manager.create_session()
    print(f"✓ Session created: {session_id}")
    
    # Send course generation request
    test_message = "create a short course about Python variables"
    print(f"\n📤 Sending: '{test_message}'")
    print("-" * 60)
    
    result = manager.send_message(
        message=test_message,
        session_id=session_id
    )
    
    print("\n📥 Response:")
    print("-" * 60)
    print(f"Success: {result['success']}")
    print(f"Is Course: {result.get('is_course', False)}")
    print(f"Has Course Data: {result.get('course_data') is not None}")
    
    if result.get('is_course'):
        print(f"\n✓ COURSE DETECTED!")
        print(f"   Title: {result['course_data'].get('course_title')}")
        print(f"   Sections: {len(result['course_data'].get('sections', []))}")
    else:
        print(f"\n✗ NOT DETECTED AS COURSE")
        print(f"   Reply length: {len(result.get('reply', ''))} chars")
        print(f"   Reply preview: {result.get('reply', '')[:200]}...")
    
    print("=" * 60)

if __name__ == "__main__":
    test_course_generation()
