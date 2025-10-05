"""
Test actual API response structure
"""
import requests
import json

def test_api_response():
    """Test what the actual API returns"""
    print("=" * 60)
    print("Testing API Response Structure")
    print("=" * 60)
    
    # Prepare request
    url = "http://localhost:8000/chat/message"
    data = {
        "message": "create a very short course about Python lists with just one section"
    }
    
    print(f"\n📤 POST {url}")
    print(f"   Data: {data}")
    print("-" * 60)
    
    response = requests.post(url, data=data)
    
    print(f"\n📥 Response Status: {response.status_code}")
    print("-" * 60)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Response Fields:")
        for key in result.keys():
            value = result[key]
            if isinstance(value, str):
                print(f"   {key}: {value[:100]}..." if len(value) > 100 else f"   {key}: {value}")
            elif isinstance(value, dict):
                print(f"   {key}: <dict with {len(value)} keys>")
                if key == 'course_data' and value:
                    print(f"      course_title: {value.get('course_title')}")
                    print(f"      sections: {len(value.get('sections', []))} section(s)")
            else:
                print(f"   {key}: {value}")
        
        # Pretty print full JSON
        print(f"\n📋 Full Response JSON:")
        print("-" * 60)
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {response.text}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_api_response()
