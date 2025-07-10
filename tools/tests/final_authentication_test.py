#!/usr/bin/env python3
"""
Test script to confirm Jerry can login and all endpoints work correctly
"""

import requests
import json

print("="*60)
print("FINAL AUTHENTICATION TEST")
print("="*60)

# Test Jerry's login credentials
email = "jerry.nixon@microsoft.com"
password = "test123"

print(f"\nTesting login for: {email}")
print(f"Password: {password}")

# Step 1: Test check-user endpoint
print("\n1. Testing check-user endpoint...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/auth/check-user/",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        exists = data.get("data", {}).get("exists", False)
        print(f"✅ User exists: {exists}")
    else:
        print(f"❌ Check user failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Check user error: {e}")
    exit(1)

# Step 2: Test login endpoint
print("\n2. Testing login endpoint...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/auth/login/",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"User: {data['data']['user']['name']}")
        print(f"Role: {data['data']['user']['role']}")
        token = data['data']['token']
        print(f"Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 3: Test me endpoint with token
print("\n3. Testing me endpoint with token...")
try:
    response = requests.get(
        "http://127.0.0.1:8000/api/auth/me/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Token validation successful!")
        print(f"User: {data['data']['name']}")
        print(f"Email: {data['data']['email']}")
    else:
        print(f"❌ Token validation failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Token validation error: {e}")
    exit(1)

print("\n" + "="*60)
print("🎉 ALL TESTS PASSED! JERRY CAN LOGIN SUCCESSFULLY!")
print("="*60)
print(f"Email: {email}")
print(f"Password: {password}")
print("Frontend URL: http://localhost:3005/login")
print("Backend URL: http://127.0.0.1:8000/api/auth/login/")
print("="*60)
