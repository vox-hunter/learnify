import requests
import json

# Test the new library API endpoints
base_url = "http://localhost:8000"

def test_api_endpoint(endpoint, method="GET", data=None):
    url = f"{base_url}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"\nError testing {endpoint}: {e}")
        return False

if __name__ == "__main__":
    print("Testing new Library API endpoints...")
    
    # Test public courses endpoint
    test_api_endpoint("/library/courses")
    
    # Test search endpoint
    test_api_endpoint("/library/search?q=math")
    
    # Test health check
    test_api_endpoint("/health")
    
    print("\nAPI tests completed!")