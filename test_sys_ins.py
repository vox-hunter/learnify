"""
Test the new sys_ins.txt system instruction
"""
import sys
import os
from dotenv import load_dotenv

# Load environment
env_path = os.path.join(os.path.dirname(__file__), 'api', '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from chat_manager import ChatSessionManager

def test_explicit_course():
    """Test with explicit course request (from sys_ins.txt example)"""
    print("=" * 60)
    print("Test 1: Explicit Course Request")
    print("=" * 60)
    
    mgr = ChatSessionManager()
    sid, _ = mgr.create_session()
    
    result = mgr.send_message(sid, "create a very short course about the states of matter")
    
    print(f"Is Course: {result['is_course']}")
    if result['is_course']:
        print(f"✓ Course Title: {result['course_data']['course_title']}")
        print(f"✓ Sections: {len(result['course_data']['sections'])}")
    else:
        print(f"✗ Reply: {result['reply'][:200]}")
    print()

def test_ambiguous():
    """Test with ambiguous request"""
    print("=" * 60)
    print("Test 2: Ambiguous Request (should ask for clarification)")
    print("=" * 60)
    
    mgr = ChatSessionManager()
    sid, _ = mgr.create_session()
    
    result = mgr.send_message(sid, "Tell me about photosynthesis")
    
    print(f"Is Course: {result['is_course']}")
    print(f"Reply: {result['reply'][:300]}")
    print()

if __name__ == "__main__":
    test_explicit_course()
    test_ambiguous()
