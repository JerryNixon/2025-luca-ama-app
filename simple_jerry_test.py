#!/usr/bin/env python3
"""
Simple Jerry Test - Test Jerry's access with proper API calls
"""

import requests
import json

def test_jerry_simple():
    """Simple test for Jerry's access"""
    print("Testing Jerry's access...")
    
    # Test 1: Login
    print("1. Testing Jerry's login...")
    login_response = requests.post("http://localhost:8000/api/auth/login/", json={
        "email": "jerry.nixon@microsoft.com",
        "password": "test123"
    })
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data['data']['token']
        user_data = login_data['data']['user']
        
        print(f"   Login successful!")
        print(f"   Name: {user_data['name']}")
        print(f"   Can create events: {user_data['can_create_events']}")
        
        # Test 2: Get events
        print("\n2. Testing Jerry's event access...")
        headers = {"Authorization": f"Bearer {token}"}
        events_response = requests.get("http://localhost:8000/api/events/", headers=headers)
        
        if events_response.status_code == 200:
            events = events_response.json()
            print(f"   Jerry can access {len(events)} events")
            
            for event in events:
                print(f"   - {event['name']}: {event['user_role_in_event']}")
        else:
            print("   Failed to get events")
            
        print("\nJerry should now be able to:")
        print("- Log in with jerry.nixon@microsoft.com / test123")
        print("- See the Create Event button (isAuthenticated = true)")
        print("- Create new events")
        print("- See events he has access to")
        
    else:
        print("   Login failed")
        print(f"   Status: {login_response.status_code}")
        print(f"   Response: {login_response.text}")

if __name__ == "__main__":
    test_jerry_simple()
