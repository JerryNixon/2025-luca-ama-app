#!/usr/bin/env python3
"""
Test Frontend-Backend Integration
This script tests the exact same flow as the frontend
"""

import requests
import json
import time

def test_frontend_backend_integration():
    print("🔍 Testing Frontend-Backend Integration...")
    
    # Test 1: Basic API health
    try:
        response = requests.get('http://127.0.0.1:8000/api/', timeout=5)
        print(f"✅ API Health: {response.status_code}")
    except Exception as e:
        print(f"❌ API Health failed: {e}")
        return False
    
    # Test 2: Login with correct endpoint
    try:
        print("\n🔐 Testing Login...")
        start_time = time.time()
        
        login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                                     json={
                                         'email': 'moderator@microsoft.com',
                                         'password': 'testpass123'
                                     }, 
                                     timeout=10)
        
        end_time = time.time()
        print(f"📊 Login response time: {end_time - start_time:.2f}s")
        print(f"📊 Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            data = login_response.json()
            token = data['data']['token']
            print(f"📊 Token received: {token[:20]}...")
            
            # Test 3: Get Events
            print("\n📋 Testing Events API...")
            start_time = time.time()
            
            events_response = requests.get('http://127.0.0.1:8000/api/events/', 
                                         headers={'Authorization': f'Bearer {token}'},
                                         timeout=20)
            
            end_time = time.time()
            print(f"📊 Events response time: {end_time - start_time:.2f}s")
            print(f"📊 Events status: {events_response.status_code}")
            
            if events_response.status_code == 200:
                events_data = events_response.json()
                print(f"✅ Events API working! Found {len(events_data)} events")
                
                if len(events_data) > 0:
                    print("📝 Sample event:")
                    print(json.dumps(events_data[0], indent=2))
                
                return True
            else:
                print(f"❌ Events API failed: {events_response.text}")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_backend_integration()
    if success:
        print("\n🎉 All tests passed! The backend is working correctly.")
        print("💡 The timeout issue is likely on the frontend side.")
    else:
        print("\n❌ Tests failed. There's an issue with the backend.")
