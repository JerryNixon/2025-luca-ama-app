#!/usr/bin/env python3
"""
Test Event Creation and Retrieval
This script tests event creation and retrieval through the API to ensure
the frontend and backend integration is working correctly.
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Test credentials
TEST_USER = {
    "email": "moderator@microsoft.com",
    "password": "testpass123"
}

def test_event_creation():
    """Test creating an event and retrieving it"""
    print("🔍 Testing Event Creation and Retrieval...")
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_response = requests.post(f"{BASE_URL}/login/", json=TEST_USER)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data["data"]["token"]
    user_info = login_data["data"]["user"]
    print(f"✅ Login successful for: {user_info['name']} ({user_info['role']})")
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get current events (before creation)
    print("\n2. Getting current events...")
    events_response = requests.get(f"{BASE_URL}/events/", headers=headers)
    
    if events_response.status_code != 200:
        print(f"❌ Failed to get events: {events_response.status_code}")
        print(f"Response: {events_response.text}")
        return
    
    events_data = events_response.json()
    print(f"✅ Current events retrieved")
    print(f"📊 Response format: {type(events_data)}")
    print(f"📊 Response data: {json.dumps(events_data, indent=2)}")
    
    current_event_count = len(events_data) if isinstance(events_data, list) else 0
    print(f"📊 Current event count: {current_event_count}")
    
    # Step 3: Create a new event
    print("\n3. Creating new event...")
    future_date = datetime.now() + timedelta(days=1)
    event_data = {
        "name": f"Test Event {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "open_date": future_date.isoformat(),
        "close_date": None
    }
    
    create_response = requests.post(f"{BASE_URL}/events/", json=event_data, headers=headers)
    
    if create_response.status_code != 201:
        print(f"❌ Failed to create event: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    created_event = create_response.json()
    print(f"✅ Event created successfully")
    print(f"📊 Created event data: {json.dumps(created_event, indent=2)}")
    
    # Step 4: Get events again (after creation)
    print("\n4. Getting events after creation...")
    new_events_response = requests.get(f"{BASE_URL}/events/", headers=headers)
    
    if new_events_response.status_code != 200:
        print(f"❌ Failed to get events after creation: {new_events_response.status_code}")
        print(f"Response: {new_events_response.text}")
        return
    
    new_events_data = new_events_response.json()
    print(f"✅ Events retrieved after creation")
    print(f"📊 Response format: {type(new_events_data)}")
    print(f"📊 Response data: {json.dumps(new_events_data, indent=2)}")
    
    new_event_count = len(new_events_data) if isinstance(new_events_data, list) else 0
    print(f"📊 New event count: {new_event_count}")
    
    # Step 5: Verify event was added
    if new_event_count > current_event_count:
        print(f"✅ Event count increased from {current_event_count} to {new_event_count}")
        print("✅ Event creation and retrieval working correctly!")
    else:
        print(f"❌ Event count did not increase (was {current_event_count}, now {new_event_count})")
        print("❌ There might be an issue with event creation or retrieval")

if __name__ == "__main__":
    test_event_creation()
