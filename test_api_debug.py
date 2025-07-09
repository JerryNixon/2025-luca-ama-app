#!/usr/bin/env python3
"""
Quick test to debug the 400 error when saving moderator notes.
"""

import requests
import json

# Test the API directly to see the exact error
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
QUESTIONS_URL = f"{BASE_URL}/questions/"

def test_moderator_note_save():
    print("🔍 Testing Moderator Note Save API")
    print("=" * 50)
    
    # Try to login as a user first (we'll test with any available user)
    print("1. Attempting login...")
    
    # We know from earlier that users need Microsoft auth, but let's try anyway to see the error
    headers = {'Content-Type': 'application/json'}
    login_data = {'email': 'amapatil@microsoft.com', 'password': 'test123'}
    
    try:
        response = requests.post(LOGIN_URL, json=login_data, headers=headers)
        print(f"   Login response status: {response.status_code}")
        print(f"   Login response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Login failed - cannot test note saving")
            print("💡 This is expected since users need Microsoft authentication")
            return
            
        # If login works, continue with the test
        data = response.json()
        token = data.get('data', {}).get('token')  # Extract token from nested structure
        
        if not token:
            print("❌ No token in response")
            print(f"   Response structure: {json.dumps(data, indent=2)}")
            return
        
        # Test updating a question with moderator notes
        print("\n2. Testing question update...")
        question_id = "7a3efba9-ab04-412b-bf1d-5423dd4fdf43"  # From the error message
        
        update_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        update_data = {
            'presenter_notes': 'Test note from API debug script'
        }
        
        update_response = requests.patch(
            f"{QUESTIONS_URL}{question_id}/", 
            json=update_data, 
            headers=update_headers
        )
        
        print(f"   Update response status: {update_response.status_code}")
        print(f"   Update response: {update_response.text}")
        
        if update_response.status_code != 200:
            print("❌ Update failed")
            try:
                error_detail = update_response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Raw error: {update_response.text}")
        else:
            print("✅ Update successful!")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_question_structure():
    """Check what fields the question API expects"""
    print("\n🔍 Checking Question API Structure")
    print("=" * 50)
    
    try:
        # Try to get questions list to see the structure
        response = requests.get(f"{BASE_URL}/events/")
        print(f"Events API status: {response.status_code}")
        
        # Also try to access a question without auth to see the error structure
        question_id = "7a3efba9-ab04-412b-bf1d-5423dd4fdf43"
        response = requests.get(f"{QUESTIONS_URL}{question_id}/")
        print(f"Question GET status (no auth): {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try updating without auth to see validation errors
        update_data = {'presenter_notes': 'test'}
        response = requests.put(f"{QUESTIONS_URL}{question_id}/", json=update_data)
        print(f"Question PUT status (no auth): {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Structure check error: {e}")

if __name__ == "__main__":
    test_moderator_note_save()
    test_question_structure()
