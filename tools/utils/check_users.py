#!/usr/bin/env python3
"""
Check what users exist in the database
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

print("=" * 60)
print("CHECKING EXISTING USERS IN DATABASE")
print("=" * 60)

users = User.objects.all()
print(f"Found {users.count()} users in database:")

for user in users:
    print(f"  - {user.username} ({user.email})")
    print(f"    Role: {user.role}")
    print(f"    Is admin: {getattr(user, 'is_admin', 'N/A')}")
    print(f"    Microsoft ID: {getattr(user, 'microsoft_id', 'N/A')}")
    print(f"    Is active: {user.is_active}")
    print(f"    Last login: {user.last_login}")
    print()

if users.count() == 0:
    print("No users found. Creating a test user...")
    
    # Create a test user
    test_user = User.objects.create_user(
        username='testuser@microsoft.com',
        email='testuser@microsoft.com',
        password='testpass123',
        role='moderator'
    )
    # Set new fields
    test_user.is_admin = False
    test_user.microsoft_id = 'test-ms-id-12345'
    test_user.save()
    
    print(f"✅ Created test user: {test_user.username}")
    print(f"   Email: {test_user.email}")
    print(f"   Password: testpass123")
    print(f"   Role: {test_user.role}")
