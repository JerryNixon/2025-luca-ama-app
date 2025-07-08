#!/usr/bin/env python3
"""
Admin User Management Script
This script allows admins to manually add users to the database
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User
from django.contrib.auth.hashers import make_password
import uuid

def add_user_to_database():
    """Interactive script to add users to the database"""
    print("👨‍💼 ADMIN USER MANAGEMENT")
    print("=" * 60)
    print("This script allows you to manually add users to the database")
    print("These users will be able to log in with email/password")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Add new user")
        print("2. List all users")
        print("3. Update user password")
        print("4. Delete user")
        print("5. Exit")
        
        choice = input("\nChoose an option (1-5): ").strip()
        
        if choice == '1':
            add_new_user()
        elif choice == '2':
            list_all_users()
        elif choice == '3':
            update_user_password()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")

def add_new_user():
    """Add a new user to the database"""
    print("\n📝 ADD NEW USER")
    print("-" * 30)
    
    # Get user information
    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"❌ User with email {email} already exists")
        return
    
    name = input("Full Name: ").strip()
    if not name:
        print("❌ Name is required")
        return
    
    password = input("Password: ").strip()
    if not password:
        print("❌ Password is required")
        return
    
    # Role selection
    print("\nRole options:")
    print("1. user (regular user)")
    print("2. moderator (can moderate events)")
    print("3. admin (system administrator)")
    
    role_choice = input("Choose role (1-3): ").strip()
    role_map = {'1': 'user', '2': 'moderator', '3': 'admin'}
    role = role_map.get(role_choice, 'user')
    
    # Create user
    try:
        user = User.objects.create(
            email=email,
            name=name,
            username=email,  # Use email as username
            role=role,
            is_active=True,
            is_admin=(role == 'admin'),
            is_staff=(role in ['admin', 'moderator']),
            is_superuser=(role == 'admin')
        )
        
        # Set password
        user.set_password(password)
        user.save()
        
        print(f"✅ User {name} ({email}) created successfully!")
        print(f"   Role: {role}")
        print(f"   Can log in with: {email} / {password}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")

def list_all_users():
    """List all users in the database"""
    print("\n📋 ALL USERS")
    print("-" * 50)
    
    users = User.objects.all().order_by('email')
    
    if not users:
        print("No users found.")
        return
    
    print(f"Found {users.count()} users:")
    print()
    
    for user in users:
        print(f"👤 {user.name} ({user.email})")
        print(f"   Role: {user.role}")
        print(f"   Is Admin: {'Yes' if user.is_admin else 'No'}")
        print(f"   Is Active: {'Yes' if user.is_active else 'No'}")
        print(f"   Microsoft ID: {user.microsoft_id or 'None'}")
        print(f"   Last Login: {user.last_login or 'Never'}")
        print()

def update_user_password():
    """Update a user's password"""
    print("\n🔑 UPDATE USER PASSWORD")
    print("-" * 30)
    
    email = input("User email: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.name} ({user.email})")
        
        new_password = input("New password: ").strip()
        if not new_password:
            print("❌ Password is required")
            return
        
        user.set_password(new_password)
        user.save()
        
        print(f"✅ Password updated for {user.name}")
        print(f"   Can now log in with: {email} / {new_password}")
        
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found")
    except Exception as e:
        print(f"❌ Error updating password: {e}")

def delete_user():
    """Delete a user from the database"""
    print("\n🗑️ DELETE USER")
    print("-" * 30)
    
    email = input("User email: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.name} ({user.email})")
        
        confirm = input("Are you sure you want to delete this user? (yes/no): ").strip().lower()
        if confirm == 'yes':
            user.delete()
            print(f"✅ User {user.name} deleted successfully")
        else:
            print("❌ Deletion cancelled")
            
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found")
    except Exception as e:
        print(f"❌ Error deleting user: {e}")

if __name__ == "__main__":
    add_user_to_database()
