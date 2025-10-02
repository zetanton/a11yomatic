#!/usr/bin/env python3
"""Script to automatically create a user account"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
EMAIL = "zetanton@tamu.edu"
PASSWORD = "Vi$ion4ry"
FULL_NAME = "Zetanton"
ORGANIZATION = "TAMU"

def create_user():
    """Create a user account via the API"""
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running or not healthy")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # User registration data
    user_data = {
        "email": EMAIL,
        "password": PASSWORD,
        "full_name": FULL_NAME,
        "organization": ORGANIZATION
    }
    
    print(f"🔄 Creating user account for {EMAIL}...")
    
    try:
        # Register the user
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            user_info = response.json()
            print(f"✅ User created successfully!")
            print(f"   Email: {user_info['email']}")
            print(f"   Name: {user_info['full_name']}")
            print(f"   Organization: {user_info['organization']}")
            print(f"   User ID: {user_info['id']}")
            
            # Test login
            print(f"\n🔄 Testing login...")
            login_response = requests.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                data={
                    "username": EMAIL,
                    "password": PASSWORD
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                token_info = login_response.json()
                print(f"✅ Login successful!")
                print(f"   Token type: {token_info['token_type']}")
                print(f"   Access token: {token_info['access_token'][:20]}...")
                return True
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return False
                
        elif response.status_code == 422:
            print(f"❌ Validation error: {response.text}")
            return False
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 A11yomatic User Creation Script")
    print("=" * 40)
    
    success = create_user()
    
    if success:
        print("\n🎉 Setup complete! You can now:")
        print("   1. Go to http://localhost:3000")
        print("   2. Login with your credentials")
        print("   3. Start using the application")
        sys.exit(0)
    else:
        print("\n💥 Setup failed. Please check the errors above.")
        sys.exit(1)
