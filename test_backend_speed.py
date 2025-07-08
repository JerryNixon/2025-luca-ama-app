#!/usr/bin/env python3
"""
Test Backend Response Time
Check if the backend is responding quickly enough
"""

import requests
import time
import json

def test_backend_speed():
    print("🔍 Testing Backend Response Speed...")
    
    # Test basic API endpoint
    try:
        start_time = time.time()
        response = requests.get('http://127.0.0.1:8000/api/', timeout=5)
        end_time = time.time()
        
        print(f"✅ Basic API response time: {end_time - start_time:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Basic API test failed: {e}")
        return False
    
    # Test login endpoint
    try:
        start_time = time.time()
        login_response = requests.post('http://127.0.0.1:8000/api/login/', json={
            'email': 'moderator@microsoft.com',
            'password': 'testpass123'
        }, timeout=10)
        end_time = time.time()
        
        print(f"✅ Login response time: {end_time - start_time:.2f}s")
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['token']
            
            # Test events endpoint
            start_time = time.time()
            events_response = requests.get('http://127.0.0.1:8000/api/events/', 
                                         headers={'Authorization': f'Bearer {token}'}, 
                                         timeout=20)
            end_time = time.time()
            
            print(f"✅ Events response time: {end_time - start_time:.2f}s")
            print(f"📊 Events count: {len(events_response.json()) if events_response.status_code == 200 else 'Error'}")
            
            if end_time - start_time > 10:
                print("⚠️  WARNING: Events endpoint is taking more than 10 seconds!")
                print("   This suggests a database connection issue.")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login/Events test failed: {e}")
        return False
    
    print("✅ All tests passed - Backend is responding normally")
    return True

if __name__ == "__main__":
    test_backend_speed()
