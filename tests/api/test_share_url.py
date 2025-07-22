import requests
import json

# Test if share URLs are now pointing to frontend
def test_share_url():
    """Test that share URLs point to frontend (port 3001)"""
    print("🔗 Testing Share URL Generation")
    print("=" * 40)
    
    # Login first
    login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
        json={
            'email': 'test@microsoft.com',
            'password': 'testpass123'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get events to check their share URLs
        events_response = requests.get('http://127.0.0.1:8000/api/events/', headers=headers)
        
        if events_response.status_code == 200:
            events = events_response.json()
            
            print(f"📋 Found {len(events)} events")
            for event in events[:3]:  # Check first 3 events
                share_url = event.get('share_url')
                if share_url:
                    print(f"  📎 {event['name'][:30]}...")
                    print(f"     Share URL: {share_url}")
                    
                    # Check if URL points to frontend (port 3001)
                    if 'localhost:3001' in share_url or '127.0.0.1:3001' in share_url:
                        print(f"     ✅ Correctly points to frontend")
                    else:
                        print(f"     ❌ Still pointing to wrong URL")
                else:
                    print(f"  📎 {event['name'][:30]}... - No share URL")
                print()
        else:
            print(f"❌ Failed to get events: {events_response.status_code}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_share_url()
