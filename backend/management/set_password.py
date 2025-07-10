#!/usr/bin/env python3
"""
Set proper passwords for testing
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("SETTING UP TEST USER WITH PROPER PASSWORD")
print("=" * 60)

# Get the moderator user
try:
    user = User.objects.get(email='moderator@microsoft.com')
    user.set_password('testpass123')
    user.save()
    print(f"✅ Set password for {user.email}")
    
    # Test authentication
    auth_user = authenticate(email='moderator@microsoft.com', password='testpass123')
    if auth_user:
        print(f"✅ Authentication test successful")
        print(f"   User ID: {auth_user.id}")
        print(f"   Username: {auth_user.username}")
        print(f"   Email: {auth_user.email}")
        print(f"   Role: {auth_user.role}")
        print(f"   Is admin: {auth_user.is_admin}")
        print(f"   Microsoft ID: {auth_user.microsoft_id}")
    else:
        print(f"❌ Authentication test failed")
        
except User.DoesNotExist:
    print(f"❌ User moderator@microsoft.com not found")
    
# Test API login
print("\n" + "=" * 60)
print("TESTING API LOGIN")
print("=" * 60)

import requests

login_data = {
    'email': 'moderator@microsoft.com',
    'password': 'testpass123'
}

try:
    response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
    print(f"API login status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API login successful")
        print(f"Success: {data.get('success')}")
        
        user_data = data.get('data', {}).get('user', {})
        print(f"User from API: {user_data}")
        
        # Test events
        token = data.get('data', {}).get('token')
        headers = {'Authorization': f'Bearer {token}'}
        events_response = requests.get('http://localhost:8000/api/events/', headers=headers)
        print(f"Events status: {events_response.status_code}")
        
        if events_response.status_code == 200:
            events = events_response.json()
            print(f"Events count: {len(events)}")
            if events:
                print(f"First event permission fields:")
                first_event = events[0]
                print(f"   user_role_in_event: {first_event.get('user_role_in_event')}")
                print(f"   can_user_moderate: {first_event.get('can_user_moderate')}")
                print(f"   can_user_access: {first_event.get('can_user_access')}")
                print(f"   is_created_by_user: {first_event.get('is_created_by_user')}")
        
    else:
        print(f"❌ API login failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
