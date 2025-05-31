#!/usr/bin/env python3
"""
Test script to verify authentication functionality without running the full app
"""

import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import os

def test_config_loading():
    """Test loading the authentication config"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml')
        print(f"Looking for config at: {config_path}")
        
        with open(config_path, 'r') as file:
            config = yaml.load(file, Loader=SafeLoader)
        
        print("✅ Config loaded successfully!")
        print(f"Found credentials for {len(config['credentials']['usernames'])} users")
        print(f"OAuth providers: {list(config['oauth2'].keys())}")
        return config
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return None

def test_authenticator_creation(config):
    """Test creating the authenticator object"""
    try:
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        print("✅ Authenticator created successfully!")
        return authenticator
    except Exception as e:
        print(f"❌ Authenticator creation failed: {e}")
        return None

def test_course_limit_logic():
    """Test the course generation limit logic"""
    print("\n--- Testing Course Limit Logic ---")
    
    # Simulate different scenarios
    scenarios = [
        {"authenticated": False, "courses_generated": 0, "expected": True},
        {"authenticated": False, "courses_generated": 2, "expected": True},
        {"authenticated": False, "courses_generated": 3, "expected": False},
        {"authenticated": True, "courses_generated": 5, "expected": True},
    ]
    
    for i, scenario in enumerate(scenarios):
        # Simulate check_course_limit function
        if scenario["authenticated"]:
            can_generate = True
        else:
            can_generate = scenario["courses_generated"] < 3
        
        status = "✅" if can_generate == scenario["expected"] else "❌"
        print(f"{status} Scenario {i+1}: Auth={scenario['authenticated']}, Courses={scenario['courses_generated']}, Can Generate={can_generate}")

if __name__ == "__main__":
    print("🧪 Testing Authentication Implementation\n")
    
    # Test config loading
    config = test_config_loading()
    
    if config:
        # Test authenticator creation
        authenticator = test_authenticator_creation(config)
        
        if authenticator:
            print("✅ All authentication components are working!")
        else:
            print("❌ Authenticator creation failed")
    else:
        print("❌ Config loading failed")
    
    # Test course limit logic
    test_course_limit_logic()
    
    print("\n🎉 Authentication test completed!")
