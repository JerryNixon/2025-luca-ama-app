#!/usr/bin/env python3
"""
Test script to diagnose event access issues
"""

import requests
import json

# Test configuration
BASE_URL = 'http://127.0.0.1:8000/api'
TEST_USER_EMAIL = 't-lucahadife@microsoft.com'
TEST_USER_PASSWORD = 'test123'

def test_event_access():
    print("🔧 Testing Event Access Issues")
    print("=" * 50)
    
    # Step 1: Login
    print("1. Testing login...")
    login_response = requests.post(f'{BASE_URL}/auth/login/', json={
        'email': TEST_USER_EMAIL,
        'password': TEST_USER_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    access_token = login_data.get('data', {}).get('token') or login_data.get('access_token')
    if not access_token:
        print(f"❌ No access token in response: {login_data}")
        return
    
    print(f"✅ Login successful, token: {access_token[:20]}...")
    
    # Headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Step 2: Get current user info
    print("\n2. Getting user info...")
    me_response = requests.get(f'{BASE_URL}/auth/me/', headers=headers)
    if me_response.status_code != 200:
        print(f"❌ Get user info failed: {me_response.status_code}")
        return
    
    user_data = me_response.json()
    print(f"✅ User: {user_data.get('name')} ({user_data.get('email')})")
    
    # Step 3: Create an event
    print("\n3. Creating test event...")
    event_data = {
        'name': 'Test Event for Debugging',
        'open_date': '2025-07-12T10:00:00Z'
    }
    
    create_response = requests.post(f'{BASE_URL}/events/', json=event_data, headers=headers)
    if create_response.status_code not in [200, 201]:
        print(f"❌ Event creation failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    event = create_response.json()
    event_id = event.get('id')
    print(f"✅ Event created: {event.get('name')} (ID: {event_id})")
    
    # Step 4: Try to access the event
    print("\n4. Accessing created event...")
    detail_response = requests.get(f'{BASE_URL}/events/{event_id}/', headers=headers)
    
    if detail_response.status_code != 200:
        print(f"❌ Event access failed: {detail_response.status_code}")
        print(f"Response: {detail_response.text}")
        return
    
    event_detail = detail_response.json()
    print(f"✅ Event access successful: {event_detail.get('name')}")
    print(f"   User role: {event_detail.get('user_role_in_event')}")
    print(f"   Can access: {event_detail.get('can_user_access')}")
    print(f"   Can moderate: {event_detail.get('can_user_moderate')}")
    
    # Step 5: List all events
    print("\n5. Listing all accessible events...")
    list_response = requests.get(f'{BASE_URL}/events/', headers=headers)
    if list_response.status_code != 200:
        print(f"❌ Events list failed: {list_response.status_code}")
        return
    
    events = list_response.json()
    print(f"✅ Found {len(events)} accessible events")
    for event in events:
        print(f"   - {event.get('name')} (ID: {event.get('id')})")
    
    print("\n🎉 All tests completed successfully!")

if __name__ == '__main__':
    test_event_access()
