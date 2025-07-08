#!/usr/bin/env python3
"""
Initialize new user fields and test the permission system
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
print("INITIALIZING NEW USER FIELDS")
print("=" * 60)

# Initialize new fields for all users
users = User.objects.all()

for user in users:
    # Set default values for new fields
    user.is_admin = False  # Default to false
    user.microsoft_id = f'ms-{user.email.split("@")[0]}'  # Generate a sample Microsoft ID
    
    # Set admin for specific user
    if user.email == 't-lucahadife@microsoft.com':
        user.is_admin = True
    
    user.save()
    print(f"✅ Updated {user.email}:")
    print(f"   Microsoft ID: {user.microsoft_id}")
    print(f"   Is admin: {user.is_admin}")
    print(f"   Role: {user.role}")

print("\n" + "=" * 60)
print("TESTING API WITH NEW FIELDS")
print("=" * 60)

import requests

# Test login
login_data = {
    'email': 'moderator@microsoft.com',
    'password': 'testpass123'
}

try:
    response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200:
        auth_data = response.json()
        print("✅ Login successful")
        
        # Check user data in response
        user_data = auth_data.get('data', {}).get('user', {})
        print(f"User data from API:")
        print(f"   Name: {user_data.get('name', 'N/A')}")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        print(f"   Role: {user_data.get('role', 'N/A')}")
        print(f"   Microsoft ID: {user_data.get('microsoft_id', 'N/A')}")
        print(f"   Is admin: {user_data.get('is_admin', 'N/A')}")
        print(f"   Can create events: {user_data.get('can_create_events', 'N/A')}")
        print(f"   Is system admin: {user_data.get('is_system_admin', 'N/A')}")
        
        # Test events endpoint
        token = auth_data.get('data', {}).get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        events_response = requests.get('http://localhost:8000/api/events/', headers=headers)
        print(f"\nEvents response status: {events_response.status_code}")
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            print(f"✅ Retrieved {len(events_data)} events")
            
            # Show first event with new permission fields
            if events_data:
                event = events_data[0]
                print(f"\nFirst event details:")
                print(f"   Name: {event.get('name', 'N/A')}")
                print(f"   User role in event: {event.get('user_role_in_event', 'N/A')}")
                print(f"   Can moderate: {event.get('can_user_moderate', False)}")
                print(f"   Can access: {event.get('can_user_access', False)}")
                print(f"   Is creator: {event.get('is_created_by_user', False)}")
                print(f"   Is public: {event.get('is_public', 'N/A')}")
                print(f"   Moderators: {len(event.get('moderators', []))}")
                print(f"   Participants: {len(event.get('participants', []))}")
        else:
            print(f"❌ Events request failed: {events_response.text}")
            
    else:
        print(f"❌ Login failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
