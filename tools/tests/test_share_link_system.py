#!/usr/bin/env python3
"""
Event Share Link System Test

Tests the complete share link functionality including:
- Share link generation
- Join endpoint (GET/POST)
- User registration via share link
- User login via share link
- Event access after joining
- Error handling for invalid links
"""

import requests
import json
import sys
import os

# Add the backend directory to Python path for model imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Base URL for the API
BASE_URL = 'http://localhost:8000'

def test_share_link_system():
    """Test the complete share link system functionality"""
    print("🔗 Testing Event Share Link System")
    print("=" * 50)
    
    # Step 1: Login as an existing user to create an event
    print("\n1. Logging in as test user...")
    login_response = requests.post(f'{BASE_URL}/api/auth/login/', json={
        'email': 'jerry@test.com',
        'password': 'password123'
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed. Cannot proceed with test.")
        print(f"Response: {login_response.text}")
        return False
    
    login_data = login_response.json()
    auth_token = login_data['data']['token']
    headers = {'Authorization': f'Bearer {auth_token}'}
    print("✅ Login successful")
    
    # Step 2: Create a new event
    print("\n2. Creating a new event...")
    event_data = {
        'name': 'Share Link Test Event',
        'open_date': '2025-07-15T10:00:00Z'
    }
    
    create_response = requests.post(f'{BASE_URL}/api/events/', 
                                  json=event_data, 
                                  headers=headers)
    
    if create_response.status_code != 201:
        print("❌ Event creation failed")
        print(f"Response: {create_response.text}")
        return False
    
    event = create_response.json()['data']
    event_id = event['id']
    share_url = event.get('share_url')
    
    if not share_url:
        print("❌ Share URL was not generated")
        return False
    
    # Extract share link from URL
    share_link = share_url.split('/join/')[-1]
    print(f"✅ Event created successfully")
    print(f"   Event ID: {event_id}")
    print(f"   Share Link: {share_link}")
    print(f"   Share URL: {share_url}")
    
    # Step 3: Test GET request to join endpoint (event info)
    print("\n3. Testing share link info retrieval...")
    info_response = requests.get(f'{BASE_URL}/api/events/join/{share_link}/')
    
    if info_response.status_code != 200:
        print("❌ Failed to get share link info")
        print(f"Response: {info_response.text}")
        return False
    
    info_data = info_response.json()
    print("✅ Share link info retrieved successfully")
    print(f"   Event Name: {info_data['data']['event']['name']}")
    print(f"   Created By: {info_data['data']['event']['created_by']}")
    
    # Step 4: Test new user registration via share link
    print("\n4. Testing new user registration via share link...")
    register_data = {
        'action': 'register',
        'email': 'sharelink_test@example.com',
        'password': 'testpass123',
        'name': 'Share Link Test User'
    }
    
    register_response = requests.post(f'{BASE_URL}/api/events/join/{share_link}/', 
                                    json=register_data)
    
    if register_response.status_code != 200:
        print("❌ User registration via share link failed")
        print(f"Response: {register_response.text}")
        return False
    
    register_result = register_response.json()
    new_user_token = register_result['data']['token']
    new_user_headers = {'Authorization': f'Bearer {new_user_token}'}
    
    print("✅ User registration successful")
    print(f"   User: {register_result['data']['user']['name']}")
    print(f"   Message: {register_result['message']}")
    
    # Step 5: Verify new user has access to the event
    print("\n5. Verifying new user event access...")
    event_access_response = requests.get(f'{BASE_URL}/api/events/{event_id}/', 
                                       headers=new_user_headers)
    
    if event_access_response.status_code != 200:
        print("❌ New user cannot access event")
        return False
    
    print("✅ New user has access to event")
    
    # Step 6: Test existing user login via share link
    print("\n6. Testing existing user login via share link...")
    
    # For this test, we'll create a user manually in the database or skip
    # Since we don't have a register endpoint, we'll test with an existing user
    print("   Note: Using existing user for login test")
    
    # Now test login via share link with the first registered user
    login_data = {
        'action': 'login',
        'email': 'sharelink_test@example.com',
        'password': 'testpass123'
    }
    
    login_via_share_response = requests.post(f'{BASE_URL}/api/events/join/{share_link}/', 
                                           json=login_data)
    
    if login_via_share_response.status_code != 200:
        print("❌ User login via share link failed")
        print(f"Response: {login_via_share_response.text}")
        return False
    
    login_result = login_via_share_response.json()
    another_user_token = login_result['data']['token']
    another_user_headers = {'Authorization': f'Bearer {another_user_token}'}
    
    print("✅ User login via share link successful")
    print(f"   User: {login_result['data']['user']['name']}")
    print(f"   Message: {login_result['message']}")
    
    # Step 7: Verify second user has access to the event
    print("\n7. Verifying second user event access...")
    second_user_access = requests.get(f'{BASE_URL}/api/events/{event_id}/', 
                                    headers=another_user_headers)
    
    if second_user_access.status_code != 200:
        print("❌ Second user cannot access event")
        return False
    
    print("✅ Second user has access to event")
    
    # Step 8: Test invalid share link
    print("\n8. Testing invalid share link...")
    invalid_response = requests.get(f'{BASE_URL}/api/events/join/invalid_link_123/')
    
    if invalid_response.status_code == 404:
        print("✅ Invalid share link properly rejected")
    else:
        print("❌ Invalid share link should return 404")
        return False
    
    # Step 9: Test authenticated user joining (should add to event)
    print("\n9. Testing authenticated user joining event...")
    
    # Use the original user token to join the event again
    auth_join_response = requests.post(f'{BASE_URL}/api/events/join/{share_link}/', 
                                     headers=headers)
    
    if auth_join_response.status_code != 200:
        print("❌ Authenticated user join failed")
        print(f"Response: {auth_join_response.text}")
        return False
    
    auth_join_result = auth_join_response.json()
    print("✅ Authenticated user join successful")
    print(f"   Message: {auth_join_result['message']}")
    
    print("\n" + "=" * 50)
    print("🎉 All share link system tests passed!")
    print("\nShare Link System is working correctly:")
    print("✅ Share links are generated for new events")
    print("✅ Share link info can be retrieved")
    print("✅ New users can register via share links")
    print("✅ Existing users can login via share links")
    print("✅ Users are automatically added to events")
    print("✅ Invalid share links are properly handled")
    print("✅ Authenticated users can join events")
    
    return True

def test_frontend_integration():
    """Test that frontend pages are accessible"""
    print("\n🌐 Testing Frontend Integration")
    print("=" * 30)
    
    # Test that frontend is running
    try:
        frontend_response = requests.get('http://localhost:3000')
        if frontend_response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print("❌ Frontend not accessible")
            return False
    except requests.ConnectionError:
        print("❌ Frontend not running on localhost:3000")
        return False
    
    print("✅ Frontend integration test passed")
    return True

if __name__ == '__main__':
    print("🚀 Starting Event Share Link System Tests")
    print("Make sure both backend (port 8000) and frontend (port 3000) are running")
    
    # Test backend connectivity
    try:
        # Use the events endpoint to check if backend is running
        health_check = requests.get(f'{BASE_URL}/api/events/', timeout=5)
        print("✅ Backend is accessible")
    except requests.ConnectionError:
        print("❌ Backend not running. Please start the Django backend on port 8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Backend connectivity error: {e}")
        sys.exit(1)
    
    # Run tests
    backend_success = test_share_link_system()
    frontend_success = test_frontend_integration()
    
    if backend_success and frontend_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("The Event Share Link System is fully functional!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)
