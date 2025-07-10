#!/usr/bin/env python3
"""
Test Jerry's login specifically
"""
import requests
import json

print("=" * 60)
print("TESTING JERRY'S LOGIN SPECIFICALLY")
print("=" * 60)

# Test login API endpoint
API_URL = "http://127.0.0.1:8000/api/auth/login/"

# Test Jerry's credentials
credentials = {
    "email": "jerry.nixon@microsoft.com",
    "password": "test123"
}

try:
    response = requests.post(API_URL, json=credentials, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ JERRY LOGIN SUCCESS!")
        data = response.json()
        print(f"User: {data['data']['user']['name']}")
        print(f"Email: {data['data']['user']['email']}")
        print(f"Role: {data['data']['user']['role']}")
        print(f"Token: {data['data']['token'][:50]}...")
    else:
        print("❌ JERRY LOGIN FAILED")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Also test with check-user endpoint
print("\n" + "=" * 60)
print("TESTING CHECK-USER ENDPOINT")
print("=" * 60)

try:
    check_url = "http://127.0.0.1:8000/api/auth/check-user/"
    response = requests.post(check_url, json={"email": "jerry.nixon@microsoft.com"}, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"User exists: {data['data']['exists']}")
        if data['data']['exists']:
            print("✅ User exists in database")
        else:
            print("❌ User not found in database")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
