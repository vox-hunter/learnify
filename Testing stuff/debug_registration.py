#!/usr/bin/env python3
"""
Debug script to test user registration and login issues
"""

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml')
    with open(config_path, 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def save_config(config):
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'authenticate.yaml')
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

def check_user_in_config(username):
    config = load_config()
    users = config.get('credentials', {}).get('usernames', {})
    if username in users:
        user_data = users[username]
        print(f"✅ User '{username}' found in config:")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        print(f"   First Name: {user_data.get('first_name', 'N/A')}")
        print(f"   Last Name: {user_data.get('last_name', 'N/A')}")
        print(f"   Password Hash: {user_data.get('password', 'N/A')[:50]}...")
        print(f"   Password Hint: {user_data.get('password_hint', 'N/A')}")
        print(f"   Roles: {user_data.get('roles', 'N/A')}")
        return True
    else:
        print(f"❌ User '{username}' NOT found in config")
        print("Available users:", list(users.keys()))
        return False

def test_login(username, password):
    config = load_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Test password verification manually
    try:
        user_data = config['credentials']['usernames'].get(username)
        if user_data:
            stored_password = user_data['password']
            print(f"Testing password for user '{username}':")
            print(f"Stored hash: {stored_password}")
            
            # Test with bcrypt directly
            import bcrypt
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = stored_password.encode('utf-8')
            
            is_valid = bcrypt.checkpw(password_bytes, stored_hash_bytes)
            print(f"Direct bcrypt check: {'✅ PASS' if is_valid else '❌ FAIL'}")
            
            return is_valid
        else:
            print(f"User '{username}' not found in credentials")
            return False
    except Exception as e:
        print(f"Error testing login: {e}")
        return False

if __name__ == "__main__":
    print("=== Debug Registration Issue ===\n")
    
    # Check if the tester user exists
    print("1. Checking if 'tester' user exists in config:")
    check_user_in_config('tester')
    print()
    
    # Check the vox user for comparison
    print("2. Checking existing 'vox' user for comparison:")
    check_user_in_config('vox')
    print()
    
    # Test login for tester
    print("3. Testing login for 'tester' user:")
    tester_login_result = test_login('tester', 'Testing@123')
    print(f"Login test result: {'✅ SUCCESS' if tester_login_result else '❌ FAILED'}")
    print()
    
    # Test login for vox (assuming we know the password)
    print("4. Let's also check if we can identify the vox password issue:")
    check_user_in_config('vox')
