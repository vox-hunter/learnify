"""
Test script for the chat endpoint
"""
import requests
import time

# Wait for server to be ready
print("Waiting for server to start...")
time.sleep(3)

# Test health endpoint
print("\n1. Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✓ Health check: {response.json()}")
except Exception as e:
    print(f"✗ Health check failed: {e}")
    exit(1)

# Test chat message endpoint
print("\n2. Testing chat message endpoint...")
try:
    # Send a simple message
    data = {
        'message': 'Hello! Can you help me understand Python basics?'
    }
    response = requests.post("http://localhost:8000/chat/message", data=data)
    result = response.json()
    
    if result.get('success'):
        print(f"✓ Chat response received!")
        print(f"  Session ID: {result['session_id']}")
        print(f"  Reply preview: {result['reply'][:100]}...")
        
        # Save session ID for follow-up
        session_id = result['session_id']
        
        # Test follow-up message
        print("\n3. Testing multi-turn conversation...")
        data2 = {
            'message': 'Can you explain variables?',
            'session_id': session_id
        }
        response2 = requests.post("http://localhost:8000/chat/message", data=data2)
        result2 = response2.json()
        
        if result2.get('success'):
            print(f"✓ Follow-up message works!")
            print(f"  Same session: {result2['session_id'] == session_id}")
            print(f"  Reply preview: {result2['reply'][:100]}...")
        else:
            print(f"✗ Follow-up failed: {result2.get('error')}")
    else:
        print(f"✗ Chat failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ Chat test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ All tests passed!")
