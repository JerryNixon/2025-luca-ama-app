"""
Debug the events API by creating a test event and then fetching all events
"""
import requests
import json

def debug_events_workflow():
    """Test the complete events workflow"""
    print("🔧 Debugging Events API Workflow...")
    
    # Step 1: Login
    print("\n1. 🔐 Login...")
    login_response = requests.post(
        "http://127.0.0.1:8000/api/auth/login/",
        json={"email": "moderator@microsoft.com", "password": "moderator123"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    if not login_data.get('success'):
        print(f"❌ Login failed: {login_data}")
        return
    
    token = login_data['data']['token']
    user = login_data['data']['user']
    print(f"✅ Login successful for {user['name']} ({user['role']})")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Step 2: Check existing events
    print("\n2. 📋 Checking existing events...")
    events_response = requests.get(
        "http://127.0.0.1:8000/api/events/",
        headers=headers,
        timeout=10
    )
    
    print(f"Events API Status: {events_response.status_code}")
    print(f"Events API Raw Response: {events_response.text}")
    
    if events_response.status_code == 200:
        try:
            events_data = events_response.json()
            print(f"Events Data Type: {type(events_data)}")
            
            if isinstance(events_data, list):
                print(f"✅ Found {len(events_data)} events (array format)")
                for i, event in enumerate(events_data):
                    print(f"  Event {i+1}: {event.get('name', 'No name')} (ID: {event.get('id', 'No ID')})")
            elif isinstance(events_data, dict):
                if 'success' in events_data and 'data' in events_data:
                    events_list = events_data['data']
                    print(f"✅ Found {len(events_list)} events (wrapped format)")
                    for i, event in enumerate(events_list):
                        print(f"  Event {i+1}: {event.get('name', 'No name')} (ID: {event.get('id', 'No ID')})")
                else:
                    print(f"❓ Unexpected dict format: {list(events_data.keys())}")
        except Exception as e:
            print(f"❌ Error parsing events response: {e}")
    else:
        print(f"❌ Events API failed: {events_response.status_code}")
        print(f"Error: {events_response.text}")
    
    # Step 3: Create a test event
    print("\n3. 🆕 Creating a test event...")
    test_event = {
        "name": f"Test Event {hash('test') % 1000}",
        "open_date": None,
        "close_date": None
    }
    
    create_response = requests.post(
        "http://127.0.0.1:8000/api/events/",
        json=test_event,
        headers=headers,
        timeout=10
    )
    
    print(f"Create Event Status: {create_response.status_code}")
    print(f"Create Event Response: {create_response.text}")
    
    if create_response.status_code in [200, 201]:
        try:
            create_data = create_response.json()
            print(f"✅ Event created successfully!")
            print(f"Created Event: {json.dumps(create_data, indent=2)}")
        except Exception as e:
            print(f"❌ Error parsing create response: {e}")
    else:
        print(f"❌ Event creation failed: {create_response.status_code}")
        print(f"Error: {create_response.text}")
    
    # Step 4: Check events again
    print("\n4. 🔄 Checking events after creation...")
    events_response2 = requests.get(
        "http://127.0.0.1:8000/api/events/",
        headers=headers,
        timeout=10
    )
    
    if events_response2.status_code == 200:
        try:
            events_data2 = events_response2.json()
            if isinstance(events_data2, list):
                print(f"✅ Now found {len(events_data2)} events")
            elif isinstance(events_data2, dict) and 'data' in events_data2:
                print(f"✅ Now found {len(events_data2['data'])} events")
        except Exception as e:
            print(f"❌ Error parsing second events response: {e}")

if __name__ == "__main__":
    debug_events_workflow()
