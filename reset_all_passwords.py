#!/usr/bin/env python3
"""
Reset passwords for all test users to enable testing with different accounts
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("RESETTING ALL USER PASSWORDS FOR TESTING")
print("=" * 60)

# Get all users and set their password to 'test123'
users = User.objects.all()

for user in users:
    # Set password to test123 for all users
    user.set_password('test123')
    user.save()
    
    print(f"✅ Reset password for {user.email}")
    print(f"   Name: {user.name}")
    print(f"   Role: {user.role}")
    print(f"   Is admin: {user.is_admin}")
    print(f"   Microsoft ID: {user.microsoft_id}")
    
    # Test authentication
    auth_user = authenticate(email=user.email, password='test123')
    if auth_user:
        print(f"   ✅ Authentication test PASSED")
    else:
        print(f"   ❌ Authentication test FAILED")
    print()

print("=" * 60)
print("TESTING API LOGIN FOR ALL USERS")
print("=" * 60)

import requests

# Test login for each user
for user in users:
    print(f"\nTesting login for {user.email}...")
    
    login_data = {
        'email': user.email,
        'password': 'test123'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            user_data = auth_data.get('data', {}).get('user', {})
            print(f"  ✅ LOGIN SUCCESS")
            print(f"     User: {user_data.get('name', 'N/A')}")
            print(f"     Role: {user_data.get('role', 'N/A')}")
            print(f"     Can create events: {user_data.get('can_create_events', 'N/A')}")
            print(f"     Is admin: {user_data.get('is_admin', 'N/A')}")
        else:
            print(f"  ❌ LOGIN FAILED: {response.text}")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

print("\n" + "=" * 60)
print("PASSWORD RESET COMPLETE!")
print("=" * 60)
print("All users now have password: test123")
print()
print("You can now test with these accounts:")
for user in users:
    print(f"  📧 {user.email} (Role: {user.role})")
print()
print("Frontend login: http://localhost:3000")
print("Use any email above with password: test123")
