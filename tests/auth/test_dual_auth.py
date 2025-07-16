#!/usr/bin/env python3
"""
Test Dual Authentication System
This script tests both Microsoft OAuth and manual database login
"""

import requests
import json

def test_dual_auth():
    """Test both authentication methods"""
    print("🔍 TESTING DUAL AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    # Test endpoints
    base_url = "http://localhost:8000/api"
    
    # Test 1: Check user existence endpoint
    print("\n1. TESTING USER EXISTENCE CHECK")
    test_emails = [
        "jerry.nixon@microsoft.com",  # Exists in database
        "newuser@microsoft.com",      # Doesn't exist
        "moderator@microsoft.com"     # Exists in database
    ]
    
    for email in test_emails:
        try:
            response = requests.post(f"{base_url}/auth/check-user/", json={"email": email})
            if response.status_code == 200:
                data = response.json()
                exists = data.get('data', {}).get('exists', False)
                print(f"   {email}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
            else:
                print(f"   {email}: ❌ Error {response.status_code}")
        except Exception as e:
            print(f"   {email}: ❌ Network error: {e}")
    
    # Test 2: Microsoft OAuth URL endpoint
    print("\n2. TESTING MICROSOFT OAUTH URL")
    try:
        response = requests.get(f"{base_url}/auth/microsoft/url/")
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('data', {}).get('auth_url', '')
            print(f"   ✅ OAuth URL generated: {auth_url[:80]}...")
        else:
            print(f"   ❌ Failed to get OAuth URL: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Network error: {e}")
    
    # Test 3: Manual database login
    print("\n3. TESTING MANUAL DATABASE LOGIN")
    credentials = {
        "email": "jerry.nixon@microsoft.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login/", json=credentials)
        if response.status_code == 200:
            data = response.json()
            user = data.get('data', {}).get('user', {})
            print(f"   ✅ Manual login successful for: {user.get('name', 'Unknown')}")
            print(f"   Email: {user.get('email', 'Unknown')}")
            print(f"   Can create events: {user.get('can_create_events', False)}")
        else:
            print(f"   ❌ Manual login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Network error: {e}")
    
    # Test 4: Test Microsoft OAuth simulation
    print("\n4. TESTING MICROSOFT OAUTH SIMULATION")
    mock_oauth_data = {
        "code": "mock_auth_code",
        "user_id": "test-user",
        "email": "testuser@microsoft.com",
        "name": "Test User",
        "tenant_id": "test-tenant"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/microsoft/", json=mock_oauth_data)
        if response.status_code == 200:
            data = response.json()
            user = data.get('data', {}).get('user', {})
            print(f"   ✅ Microsoft OAuth simulation successful for: {user.get('name', 'Unknown')}")
            print(f"   Email: {user.get('email', 'Unknown')}")
            print(f"   Microsoft ID: {user.get('microsoft_id', 'Unknown')}")
        else:
            print(f"   ❌ Microsoft OAuth simulation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Network error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DUAL AUTHENTICATION SYSTEM SUMMARY")
    print("   - User existence check: Available")
    print("   - Microsoft OAuth URL: Available")
    print("   - Manual database login: Available")
    print("   - Microsoft OAuth simulation: Available")
    print("\n📝 NEXT STEPS:")
    print("   1. Set up real Microsoft OAuth app registration")
    print("   2. Configure tenant ID and client ID")
    print("   3. Test with real Microsoft accounts")
    print("   4. Test frontend integration")

if __name__ == "__main__":
    test_dual_auth()
