import requests
import json

def test_dynamic_share_url():
    """Test if share URLs now use the correct frontend URL"""
    print("🔗 Testing Dynamic Share URL Generation")
    print("=" * 45)
    
    # Test different origins
    origins_to_test = [
        'http://localhost:3000',
        'http://localhost:3001', 
        'http://localhost:3002'
    ]
    
    for origin in origins_to_test:
        print(f"\n📡 Testing with Origin: {origin}")
        
        # Login first
        login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
            json={
                'email': 'test@microsoft.com',
                'password': 'testpass123'
            },
            headers={
                'Content-Type': 'application/json',
                'Origin': origin,  # Simulate request from this frontend
                'Referer': f'{origin}/events'  # Simulate coming from events page
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['token']
            headers = {
                'Authorization': f'Bearer {token}',
                'Origin': origin,
                'Referer': f'{origin}/events'
            }
            
            # Get events to check their share URLs
            events_response = requests.get('http://127.0.0.1:8000/api/events/', headers=headers)
            
            if events_response.status_code == 200:
                events = events_response.json()
                
                if events:
                    first_event = events[0]
                    share_url = first_event.get('share_url')
                    
                    print(f"   📎 Event: {first_event['name'][:30]}...")
                    print(f"   🔗 Share URL: {share_url}")
                    
                    # Check if URL matches the origin
                    if share_url and origin in share_url:
                        print(f"   ✅ Share URL correctly uses {origin}")
                    elif share_url:
                        print(f"   ⚠️  Share URL uses different origin: {share_url}")
                    else:
                        print(f"   ❌ No share URL generated")
                else:
                    print(f"   ℹ️  No events found")
            else:
                print(f"   ❌ Failed to get events: {events_response.status_code}")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_dynamic_share_url()
