#!/usr/bin/env python
"""
Quick Test User Creation Script

Creates test users for the AMA app so you can log in and test functionality.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User

def create_test_users():
    """Create essential test users"""
    
    print("👥 Creating Test Users for AMA App")
    print("=" * 50)
    
    users_to_create = [
        {
            'email': 'admin@test.com',
            'name': 'Test Admin',
            'username': 'admin',
            'role': 'admin',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True,
            'is_admin': True
        },
        {
            'email': 'moderator@test.com', 
            'name': 'Test Moderator',
            'username': 'moderator',
            'role': 'moderator',
            'password': 'mod123',
            'is_staff': True,
            'is_admin': False
        },
        {
            'email': 'user@test.com',
            'name': 'Test User',
            'username': 'user',
            'role': 'user', 
            'password': 'user123',
            'is_staff': False,
            'is_admin': False
        },
        {
            'email': 'jerry@test.com',
            'name': 'Jerry Test',
            'username': 'jerry',
            'role': 'admin',
            'password': 'jerry123',
            'is_staff': True,
            'is_superuser': True,
            'is_admin': True
        }
    ]
    
    for user_data in users_to_create:
        email = user_data['email']
        password = user_data.pop('password')
        
        # Create or update user
        user, created = User.objects.get_or_create(
            email=email,
            defaults=user_data
        )
        
        # Set password
        user.set_password(password)
        user.save()
        
        status = "Created" if created else "Updated"
        print(f"✅ {status}: {user.name} ({user.email})")
        print(f"   - Role: {user.role}")
        print(f"   - Password: {password}")
        print(f"   - Staff: {user.is_staff}")
        print()
    
    print("🎉 Test users ready!")
    print("\n📝 Login Credentials:")
    print("-" * 30)
    print("Admin:     admin@test.com / admin123")
    print("Moderator: moderator@test.com / mod123") 
    print("User:      user@test.com / user123")
    print("Jerry:     jerry@test.com / jerry123")
    print("\n🌐 Go to: http://localhost:3000")

if __name__ == "__main__":
    create_test_users()
