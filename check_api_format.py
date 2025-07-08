"""
Quick test to see the exact API response format
"""
import requests

def test_api_format():
    """Test the exact API response format"""
    print("🔍 Testing API Response Format...")
    
    # Login first
    login_response = requests.post(
        "http://127.0.0.1:8000/api/auth/login/",
        json={"email": "moderator@microsoft.com", "password": "moderator123"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['data']['token']
        
        # Test events API
        events_response = requests.get(
            "http://127.0.0.1:8000/api/events/",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"Status: {events_response.status_code}")
        print(f"Headers: {dict(events_response.headers)}")
        print(f"Raw Response: {events_response.text}")
        
        if events_response.status_code == 200:
            try:
                data = events_response.json()
                print(f"JSON Type: {type(data)}")
                if isinstance(data, list):
                    print(f"List length: {len(data)}")
                elif isinstance(data, dict):
                    print(f"Dict keys: {list(data.keys())}")
            except Exception as e:
                print(f"JSON parse error: {e}")

if __name__ == "__main__":
    test_api_format()
