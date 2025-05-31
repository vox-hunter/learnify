#!/usr/bin/env python3
"""
Standalone debug script for authentication issues.
This script tests the authentication components without requiring Streamlit.
"""

import yaml
import bcrypt
import sys
import os

def load_config():
    """Load the authentication config file."""
    # Try different possible locations
    config_paths = [
        'authenticate.yaml',
        '../authenticate.yaml',
        '../../authenticate.yaml'
    ]
    
    for config_path in config_paths:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                print(f"✅ Loaded config from: {config_path}")
                return config
        except Exception as e:
            print(f"❌ Error loading config from {config_path}: {e}")
    
    print("❌ Could not find authenticate.yaml in any expected location")
    return None

def test_bcrypt_verification():
    """Test direct bcrypt password verification."""
    print("\n🔍 Testing bcrypt password verification...")
    
    config = load_config()
    if not config:
        return False
    
    # Get user credentials from config
    credentials = config.get('credentials', {})
    users = credentials.get('usernames', {})
    
    print(f"Found {len(users)} users in config: {list(users.keys())}")
    
    for username, user_data in users.items():
        print(f"\n👤 Testing user: {username}")
        password_hash = user_data.get('password')
        
        if not password_hash:
            print(f"❌ No password hash found for {username}")
            continue
        
        print(f"Password hash: {password_hash}")
          # Test with a few possible passwords including the hint
        test_passwords = ['Testing@123', 'test123', 'password', 'tester', username]
        
        for test_password in test_passwords:
            try:
                # Convert hash to bytes if it's a string
                if isinstance(password_hash, str):
                    hash_bytes = password_hash.encode('utf-8')
                else:
                    hash_bytes = password_hash
                
                is_valid = bcrypt.checkpw(test_password.encode('utf-8'), hash_bytes)
                if is_valid:
                    print(f"✅ Password '{test_password}' is valid for {username}")
                    return True
                else:
                    print(f"❌ Password '{test_password}' is invalid for {username}")
            except Exception as e:
                print(f"❌ Error checking password '{test_password}': {e}")
    
    return False

def test_streamlit_authenticator_import():
    """Test if streamlit-authenticator can be imported and initialized."""
    print("\n🔍 Testing streamlit-authenticator import...")
    
    try:
        import streamlit_authenticator as stauth
        print("✅ streamlit-authenticator imported successfully")
        
        config = load_config()
        if not config:
            return False
          # Try to create authenticator object
        try:
            # Handle the preauthorized config format issue
            preauthorized = config.get('preauthorized') or config.get('pre-authorized', {}).get('emails', [])
            
            authenticator = stauth.Authenticate(
                config['credentials'],
                config['cookie']['name'],
                config['cookie']['key'],
                config['cookie']['expiry_days'],
                preauthorized
            )
            print("✅ Authenticator object created successfully")
            
            # Try to access internal methods for debugging
            print("\n🔍 Testing authenticator internals...")
            print(f"Authenticator type: {type(authenticator)}")
            print(f"Available methods: {[method for method in dir(authenticator) if not method.startswith('_')]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating authenticator: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import streamlit-authenticator: {e}")
        return False

def check_config_structure():
    """Check the structure of the authentication config."""
    print("\n🔍 Checking config structure...")
    
    config = load_config()
    if not config:
        return False
    
    print("Config structure:")
    print(f"- credentials: {type(config.get('credentials'))}")
    if 'credentials' in config:
        creds = config['credentials']
        print(f"  - usernames: {type(creds.get('usernames'))}")
        if 'usernames' in creds:
            for username, user_data in creds['usernames'].items():
                print(f"    - {username}: {list(user_data.keys())}")
    
    print(f"- cookie: {type(config.get('cookie'))}")
    if 'cookie' in config:
        cookie = config['cookie']
        for key in ['name', 'key', 'expiry_days']:
            print(f"  - {key}: {cookie.get(key)}")
    
    print(f"- preauthorized: {config.get('preauthorized')}")
    
    return True

def main():
    """Run all debug tests."""
    print("🔧 Standalone Authentication Debug Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    config_paths = [
        'authenticate.yaml',
        '../authenticate.yaml',
        '../../authenticate.yaml'
    ]
    
    found_config = False
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"✅ Found authenticate.yaml at: {config_path}")
            found_config = True
            break
    
    if not found_config:
        print("❌ authenticate.yaml not found in any expected location")
        print(f"Current directory: {os.getcwd()}")
        print("Searched in:")
        for path in config_paths:
            print(f"  - {path}")
        return
    
    # Run tests
    check_config_structure()
    test_bcrypt_verification()
    test_streamlit_authenticator_import()
    
    print("\n" + "=" * 50)
    print("🔧 Debug tests completed")

if __name__ == "__main__":
    main()
