"""
Test the events API to see what data structure is being returned
"""
import requests
import json

# Test the events API with authentication
def test_events_api():
    """Test the events API with authentication"""
    print("🔍 Testing Events API...")
    
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
        print(f"✅ Login successful, token: {token[:20]}...")
        
        # Step 2: Test events API
        events_url = "http://127.0.0.1:8000/api/events/"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        events_response = requests.get(events_url, headers=headers, timeout=10)
        print(f"Events API status: {events_response.status_code}")
        print(f"Events API response: {events_response.text}")
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            print(f"✅ Events API successful!")
            print(f"Response structure: {type(events_data)}")
            
            if isinstance(events_data, dict):
                print(f"Response keys: {list(events_data.keys())}")
                if 'data' in events_data:
                    print(f"Data type: {type(events_data['data'])}")
                    if isinstance(events_data['data'], list):
                        print(f"Number of events: {len(events_data['data'])}")
                        if events_data['data']:
                            print(f"First event keys: {list(events_data['data'][0].keys())}")
            
            return events_data
        else:
            print(f"❌ Events API failed: {events_response.status_code}")
            print(f"Error: {events_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_events_api()
