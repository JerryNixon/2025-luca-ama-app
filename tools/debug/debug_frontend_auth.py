#!/usr/bin/env python3
"""
Debug frontend authentication issue
"""

import requests

print("=" * 60)
print("DEBUGGING FRONTEND AUTHENTICATION")
print("=" * 60)

# Test login with Jerry
login_data = {
    'email': 'jerry.nixon@microsoft.com',
    'password': 'test123'
}

print("Testing login for Jerry...")
response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
print(f"Login Status: {response.status_code}")

if response.status_code == 200:
    auth_data = response.json()
    user_data = auth_data.get('data', {}).get('user', {})
    
    print("✅ LOGIN SUCCESSFUL")
    print("User data returned by API:")
    print(f"  - ID: {user_data.get('id')}")
    print(f"  - Name: {user_data.get('name')}")
    print(f"  - Email: {user_data.get('email')}")
    print(f"  - Role: {user_data.get('role')}")
    print(f"  - Can create events: {user_data.get('can_create_events')}")
    print(f"  - Is admin: {user_data.get('is_admin')}")
    print(f"  - Is system admin: {user_data.get('is_system_admin')}")
    
    # Test the /me endpoint
    token = auth_data.get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("\nTesting /auth/me/ endpoint...")
    me_response = requests.get('http://localhost:8000/api/auth/me/', headers=headers)
    print(f"Me Status: {me_response.status_code}")
    
    if me_response.status_code == 200:
        me_data = me_response.json()
        me_user = me_data.get('data', {})
        print("✅ /auth/me/ SUCCESSFUL")
        print("User data from /me endpoint:")
        print(f"  - Name: {me_user.get('name')}")
        print(f"  - Email: {me_user.get('email')}")
        print(f"  - Role: {me_user.get('role')}")
        print(f"  - Can create events: {me_user.get('can_create_events')}")
    else:
        print(f"❌ /auth/me/ failed: {me_response.text}")
        
else:
    print(f"❌ LOGIN FAILED: {response.text}")

print("\n" + "=" * 60)
print("FRONTEND DEBUGGING COMPLETE")
print("=" * 60)
print("If login is successful but button doesn't show:")
print("1. Check browser console for JavaScript errors")
print("2. Restart the frontend server: npm run dev")
print("3. Clear browser cache and cookies")
print("4. Check if 'isAuthenticated' is true in browser dev tools")
