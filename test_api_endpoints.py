#!/usr/bin/env python3
"""
Test API Endpoints
"""

import requests
import json

def test_api():
    print("🔍 Testing API endpoints...")
    
    # Test login
    print("\n1. Testing login...")
    login_response = requests.post('http://localhost:8000/api/login/', json={
        'email': 'moderator@microsoft.com',
        'password': 'testpass123'
    })
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        token = login_response.json()['data']['token']
        
        # Test events endpoint
        print("\n2. Testing events endpoint...")
        headers = {'Authorization': f'Bearer {token}'}
        events_response = requests.get('http://localhost:8000/api/events/', headers=headers)
        
        if events_response.status_code == 200:
            print("✅ Events endpoint working")
            events_data = events_response.json()
            print(f"📊 Events response: {json.dumps(events_data, indent=2)}")
            
            # Test creating an event
            print("\n3. Testing event creation...")
            event_data = {
                'name': 'Test Event API',
                'open_date': '2025-07-10T10:00:00Z'
            }
            
            create_response = requests.post('http://localhost:8000/api/events/', 
                                          json=event_data, headers=headers)
            
            if create_response.status_code == 201:
                print("✅ Event creation successful")
                created_event = create_response.json()
                print(f"📝 Created event: {json.dumps(created_event, indent=2)}")
                
                # Test getting events again
                print("\n4. Testing events after creation...")
                new_events_response = requests.get('http://localhost:8000/api/events/', headers=headers)
                if new_events_response.status_code == 200:
                    new_events_data = new_events_response.json()
                    print(f"📊 New events count: {len(new_events_data)}")
                    print(f"📊 New events: {json.dumps(new_events_data, indent=2)}")
                else:
                    print(f"❌ Failed to get events after creation: {new_events_response.status_code}")
            else:
                print(f"❌ Event creation failed: {create_response.status_code}")
                print(f"Response: {create_response.text}")
        else:
            print(f"❌ Events endpoint failed: {events_response.status_code}")
            print(f"Response: {events_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"❌ Error: {e}")
