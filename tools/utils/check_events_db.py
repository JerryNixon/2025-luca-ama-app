"""
Check if events exist in the database and test the events API
"""
import requests
import json

def test_events_database():
    """Test if events exist and API is working"""
    print("🔍 Testing Events Database and API...")
    
    # Step 1: Login to get token
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    credentials = {
        "email": "moderator@microsoft.com",
        "password": "moderator123"
    }
    
    try:
        # Login
        response = requests.post(login_url, json=credentials, timeout=10)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        data = response.json()
        if not data.get('success'):
            print(f"❌ Login failed: {data}")
            return
        
        token = data['data']['token']
        print(f"✅ Login successful")
        
        # Step 2: Test events API
        events_url = "http://127.0.0.1:8000/api/events/"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        events_response = requests.get(events_url, headers=headers, timeout=10)
        print(f"📡 Events API Status: {events_response.status_code}")
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            print(f"✅ Events API Response: {json.dumps(events_data, indent=2)}")
            
            # Check if it's the expected format
            if 'success' in events_data and events_data['success']:
                events_list = events_data.get('data', [])
                print(f"📊 Number of events: {len(events_list)}")
                
                for i, event in enumerate(events_list):
                    print(f"Event {i+1}: {event.get('name', 'No name')} (ID: {event.get('id', 'No ID')})")
                    print(f"  Created by: {event.get('created_by', {}).get('name', 'Unknown')}")
                    print(f"  Active: {event.get('is_active', False)}")
                    print(f"  Share link: {event.get('share_link', 'None')}")
                    print()
                    
            else:
                print("❌ Unexpected API response format")
                
        else:
            print(f"❌ Events API failed: {events_response.status_code}")
            print(f"Error: {events_response.text}")
            
        # Step 3: Test event creation
        print("\n🔧 Testing Event Creation...")
        create_url = "http://127.0.0.1:8000/api/events/"
        test_event = {
            "name": "Test Event " + str(hash("test") % 1000),
            "open_date": None,
            "close_date": None
        }
        
        create_response = requests.post(create_url, json=test_event, headers=headers, timeout=10)
        print(f"📡 Create Event Status: {create_response.status_code}")
        
        if create_response.status_code in [200, 201]:
            create_data = create_response.json()
            print(f"✅ Event Created: {json.dumps(create_data, indent=2)}")
        else:
            print(f"❌ Event Creation Failed: {create_response.status_code}")
            print(f"Error: {create_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_events_database()
