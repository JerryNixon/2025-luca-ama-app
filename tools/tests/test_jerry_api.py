#!/usr/bin/env python3
"""
Test Frontend Authentication API for Jerry
This script tests the login API endpoint to verify Jerry can authenticate
"""

import requests
import json

def test_jerry_login():
    """Test Jerry's login via API"""
    print("🔍 TESTING JERRY'S LOGIN VIA API")
    print("=" * 60)
    
    # API endpoint
    login_url = "http://localhost:8000/api/auth/login/"
    
    # Jerry's credentials
    credentials = {
        "email": "jerry.nixon@microsoft.com",
        "password": "test123"
    }
    
    print(f"Testing login for: {credentials['email']}")
    print(f"API endpoint: {login_url}")
    
    try:
        response = requests.post(login_url, json=credentials)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"User data: {json.dumps(data.get('data', {}).get('user', {}), indent=2)}")
            
            # Check if user has the token
            token = data.get('data', {}).get('token')
            if token:
                print(f"✅ Token received: {token[:50]}...")
                
                # Test the /me endpoint with the token
                me_url = "http://localhost:8000/api/auth/me/"
                headers = {"Authorization": f"Bearer {token}"}
                
                me_response = requests.get(me_url, headers=headers)
                print(f"\n🔍 Testing /me endpoint...")
                print(f"Status code: {me_response.status_code}")
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ /me endpoint successful!")
                    print(f"User data: {json.dumps(me_data.get('data', {}), indent=2)}")
                else:
                    print(f"❌ /me endpoint failed: {me_response.text}")
                    
            else:
                print("❌ No token received")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_events_api():
    """Test events API endpoint"""
    print("\n" + "=" * 60)
    print("🔍 TESTING EVENTS API")
    
    # Login first to get token
    login_url = "http://localhost:8000/api/auth/login/"
    credentials = {
        "email": "jerry.nixon@microsoft.com",
        "password": "test123"
    }
    
    try:
        login_response = requests.post(login_url, json=credentials)
        if login_response.status_code != 200:
            print("❌ Login failed, cannot test events API")
            return
            
        token = login_response.json().get('data', {}).get('token')
        if not token:
            print("❌ No token received, cannot test events API")
            return
        
        # Test events endpoint
        events_url = "http://localhost:8000/api/events/"
        headers = {"Authorization": f"Bearer {token}"}
        
        events_response = requests.get(events_url, headers=headers)
        print(f"Events API status: {events_response.status_code}")
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            print("✅ Events API successful!")
            
            # Check if it's a DRF response with 'data' key or direct array
            if 'data' in events_data:
                events = events_data['data']
            else:
                events = events_data
                
            print(f"Number of events: {len(events)}")
            
            for event in events[:3]:  # Show first 3 events
                print(f"  - {event.get('name', 'Unknown')}")
                print(f"    Can create: {event.get('can_user_create', 'Unknown')}")
                print(f"    Can moderate: {event.get('can_user_moderate', 'Unknown')}")
                print(f"    User role: {event.get('user_role', 'Unknown')}")
                
        else:
            print(f"❌ Events API failed: {events_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing events API: {e}")

if __name__ == "__main__":
    test_jerry_login()
    test_events_api()
