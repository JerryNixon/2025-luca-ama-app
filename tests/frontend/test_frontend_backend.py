import requests

def test_frontend_backend_connection():
    """Test if frontend can properly communicate with backend"""
    print("🔗 Testing Frontend-Backend Connection")
    print("=" * 45)
    
    # Test the same endpoint that frontend would call
    share_link = "gf2lqnGt"
    frontend_api_url = f"http://127.0.0.1:8000/api/events/join/{share_link}/"
    
    print(f"📡 Testing: {frontend_api_url}")
    
    try:
        # Test GET request (what frontend does first)
        response = requests.get(frontend_api_url, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        print(f"📊 GET Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                event_data = data.get('data', {}).get('event', {})
                print(f"✅ Event found: {event_data.get('name')}")
                print(f"   Created by: {event_data.get('created_by')}")
                print(f"   Event ID: {event_data.get('id')}")
                
                # Test what happens when user tries to join
                print(f"\n📡 Testing POST (join attempt)...")
                post_response = requests.post(frontend_api_url, 
                    json={},
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                )
                
                print(f"📊 POST Status: {post_response.status_code}")
                
                if post_response.status_code == 401:
                    print("🔒 Authentication required (expected for unauthenticated user)")
                elif post_response.status_code == 200:
                    join_data = post_response.json()
                    print(f"✅ Join response: {join_data}")
                else:
                    print(f"⚠️  Unexpected POST status: {post_response.status_code}")
                    try:
                        error_data = post_response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Raw response: {post_response.text}")
            else:
                print(f"❌ API returned success=false: {data}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_frontend_backend_connection()
