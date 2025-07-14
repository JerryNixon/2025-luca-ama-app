import requests
import json

def test_frontend_api_call():
    """Test the exact API call that frontend makes"""
    print("🔗 Testing Share URL with Frontend Headers")
    print("=" * 45)
    
    # Simulate the exact request the frontend makes when logged in
    # First, let's get a token using a known working method
    
    # Use your working credentials
    login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
        json={
            'email': 'amar@microsoft.com',  # Use your actual email
            'password': 'amarpass123'       # Use your actual password
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['data']['token']
        print(f"✅ Login successful")
        
        # Now simulate frontend API call from localhost:3002
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3002',          # Frontend origin
            'Referer': 'http://localhost:3002/events',  # Coming from events page
        }
        
        print(f"📡 Making API call with Origin: http://localhost:3002")
        
        # Get events (this will trigger share URL generation)
        events_response = requests.get('http://127.0.0.1:8000/api/events/', headers=headers)
        
        if events_response.status_code == 200:
            events = events_response.json()
            print(f"✅ Got {len(events)} events")
            
            if events:
                first_event = events[0]
                share_url = first_event.get('share_url')
                
                print(f"\n📋 Event: {first_event['name']}")
                print(f"🔗 Generated Share URL: {share_url}")
                
                # Check if it uses the correct frontend URL
                if share_url:
                    if 'localhost:3002' in share_url:
                        print(f"✅ SUCCESS: Share URL correctly uses localhost:3002")
                    elif 'localhost:3001' in share_url:
                        print(f"⚠️  Still using localhost:3001 (old hardcoded)")
                    elif 'localhost:3000' in share_url:
                        print(f"📍 Using localhost:3000 (fallback)")
                    else:
                        print(f"❓ Using different URL: {share_url}")
                else:
                    print(f"❌ No share URL generated")
            else:
                print("ℹ️  No events found")
        else:
            print(f"❌ Failed to get events: {events_response.status_code}")
            print(f"   Response: {events_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")

if __name__ == "__main__":
    test_frontend_api_call()
