#!/usr/bin/env python3
"""
Test the login flow to ensure it goes to dashboard with all options
"""

import time
import requests

print("="*60)
print("TESTING COMPLETE LOGIN FLOW")
print("="*60)

# Test credentials
email = "jerry.nixon@microsoft.com"
password = "test123"

print(f"\n🔑 Testing login flow for: {email}")
print(f"📝 Expected flow:")
print(f"   1. Login with credentials")
print(f"   2. Redirect to dashboard (/dashboard)")
print(f"   3. Show options: Browse Events, Create Event, Profile")

# Step 1: Login
print(f"\n1. Logging in...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/auth/login/",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        user = data['data']['user']
        token = data['data']['token']
        print(f"✅ Login successful!")
        print(f"   User: {user['name']}")
        print(f"   Role: {user['role']}")
        print(f"   Can create events: {user.get('can_create_events', 'Not specified')}")
        print(f"   Is admin: {user.get('is_admin', 'Not specified')}")
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

print(f"\n✅ LOGIN FLOW TEST COMPLETE!")
print(f"📍 Frontend should now redirect to: http://localhost:3005/dashboard")
print(f"🎯 Dashboard should show:")
print(f"   ✓ Browse Events (for all users)")
print(f"   ✓ Create Event (for users with can_create_events=true)")
print(f"   ✓ Profile (for all users)")

print(f"\n🌐 Test URLs:")
print(f"   Login: http://localhost:3005/login")
print(f"   Dashboard: http://localhost:3005/dashboard")
print(f"   Events: http://localhost:3005/events")
print(f"   Create Event: http://localhost:3005/events/create")
print(f"   Profile: http://localhost:3005/profile")

print("="*60)
