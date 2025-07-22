import requests
import json

def test_full_join_flow():
    """Test the complete join flow with authentication"""
    print("🎯 Testing Complete Join Flow")
    print("=" * 35)
    
    share_link = "gf2lqnGt"
    
    # Step 1: Get event info (no auth required)
    print("1️⃣ Getting event info...")
    get_response = requests.get(f"http://127.0.0.1:8000/api/events/join/{share_link}/")
    
    if get_response.status_code == 200:
        event_data = get_response.json()
        print(f"✅ Event: {event_data['data']['event']['name']}")
        
        # Step 2: Try to join without authentication
        print("\n2️⃣ Attempting to join without auth...")
        join_response = requests.post(f"http://127.0.0.1:8000/api/events/join/{share_link}/")
        print(f"📊 Status: {join_response.status_code}")
        
        if join_response.status_code == 400:
            join_data = join_response.json()
            print(f"🔒 Expected: {join_data['message']}")
            
            # Step 3: Register/Login and then join
            print("\n3️⃣ Testing join with registration...")
            
            # Try to join with new user data
            new_user_data = {
                "email": "testjoin@example.com",
                "password": "testpass123",
                "name": "Test Join User"
            }
            
            join_with_reg_response = requests.post(
                f"http://127.0.0.1:8000/api/events/join/{share_link}/",
                json=new_user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📊 Join with registration status: {join_with_reg_response.status_code}")
            
            if join_with_reg_response.status_code == 200:
                success_data = join_with_reg_response.json()
                print(f"✅ Success: {success_data.get('message')}")
                
                # Check if user got token
                if 'data' in success_data and 'token' in success_data['data']:
                    print(f"🔑 Token received: {success_data['data']['token'][:20]}...")
                else:
                    print("ℹ️  No token in response")
            else:
                error_data = join_with_reg_response.json()
                print(f"❌ Error: {error_data}")
        else:
            print(f"🤔 Unexpected status: {join_response.status_code}")
    else:
        print(f"❌ Could not get event info: {get_response.status_code}")

if __name__ == "__main__":
    test_full_join_flow()
