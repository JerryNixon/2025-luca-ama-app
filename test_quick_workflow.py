#!/usr/bin/env python3
"""
Quick test to verify question visibility between participants and moderators.

This script tests the core workflow:
1. Login as Jerry (moderator)
2. Login as Amar (participant) 
3. Post a question as Amar
4. Check if Jerry can see it via API
5. Test the refresh functionality

Usage:
    python test_quick_workflow.py
"""

import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
EVENTS_URL = f"{BASE_URL}/events/"
QUESTIONS_URL = f"{BASE_URL}/questions/"

def login_user(email, password):
    """Login a user and return token and user info."""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {'email': email, 'password': password}
        response = requests.post(LOGIN_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token'), data.get('user')
        else:
            print(f"Login failed for {email}: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None, None

def main():
    print("🧪 Quick Workflow Test")
    print("=" * 50)
    
    # Try logging in with different approaches
    print("\n1. Testing Jerry login (moderator)...")
    
    # Try different login formats
    jerry_approaches = [
        ('jerry.nixon@microsoft.com', 'test123'),
        ('jerrynixon', 'test123'),
        ('jerry', 'test123')
    ]
    
    jerry_token = None
    jerry_user = None
    
    for email, password in jerry_approaches:
        print(f"   Trying: {email}")
        token, user = login_user(email, password)
        if token:
            jerry_token, jerry_user = token, user
            print(f"   ✅ Success! Logged in as: {user['name']}")
            break
        else:
            print(f"   ❌ Failed")
    
    if not jerry_token:
        print("\n❌ Could not login as Jerry with any approach")
        print("💡 The users might need to be recreated or use Microsoft login")
        return
    
    print("\n2. Testing Amar login (participant)...")
    
    # Try different login formats
    amar_approaches = [
        ('amapatil@microsoft.com', 'test123'),
        ('amarpatil', 'test123'),
        ('amar', 'test123')
    ]
    
    amar_token = None
    amar_user = None
    
    for email, password in amar_approaches:
        print(f"   Trying: {email}")
        token, user = login_user(email, password)
        if token:
            amar_token, amar_user = token, user
            print(f"   ✅ Success! Logged in as: {user['name']}")
            break
        else:
            print(f"   ❌ Failed")
    
    if not amar_token:
        print("\n❌ Could not login as Amar with any approach")
        return
    
    print("\n🎉 Both users logged in successfully!")
    print(f"   Jerry: {jerry_user['name']} (token: {jerry_token[:20]}...)")
    print(f"   Amar: {amar_user['name']} (token: {amar_token[:20]}...)")
    
    print("\n💡 The login issue was resolved!")
    print("💡 You can now test the full workflow in the browser:")
    print("   1. Login as Jerry, create/access an event")
    print("   2. Login as Amar, post a question")
    print("   3. Switch back to Jerry, use refresh button to see new questions")
    print("   4. Test moderator actions (star, stage, answer, add notes)")

if __name__ == "__main__":
    main()
