#!/usr/bin/env python
"""
Create test users for AMA platform authentication
"""
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User

def create_test_users():
    """Create test users for authentication testing"""
    
    # Create moderator user
    moderator, created = User.objects.get_or_create(
        email='moderator@microsoft.com',
        defaults={
            'name': 'AMA Moderator',
            'role': 'moderator',
            'is_staff': True,
            'is_active': True,
        }
    )
    if created:
        moderator.set_password('moderator123')
        moderator.save()
        print(f"✅ Created moderator: {moderator.email}")
    else:
        # Update password for existing user
        moderator.set_password('moderator123')
        moderator.save()
        print(f"✅ Updated moderator: {moderator.email}")
    
    # Create regular user
    user, created = User.objects.get_or_create(
        email='user@microsoft.com',
        defaults={
            'name': 'AMA User',
            'role': 'user',
            'is_active': True,
        }
    )
    if created:
        user.set_password('user123')
        user.save()
        print(f"✅ Created user: {user.email}")
    else:
        # Update password for existing user
        user.set_password('user123')
        user.save()
        print(f"✅ Updated user: {user.email}")
    
    # Create presenter user
    presenter, created = User.objects.get_or_create(
        email='presenter@microsoft.com',
        defaults={
            'name': 'AMA Presenter',
            'role': 'presenter',
            'is_active': True,
        }
    )
    if created:
        presenter.set_password('presenter123')
        presenter.save()
        print(f"✅ Created presenter: {presenter.email}")
    else:
        # Update password for existing user
        presenter.set_password('presenter123')
        presenter.save()
        print(f"✅ Updated presenter: {presenter.email}")
    
    print("\n🔑 Test Users Created:")
    print("=" * 50)
    print(f"Moderator: moderator@microsoft.com / moderator123")
    print(f"User:      user@microsoft.com / user123")
    print(f"Presenter: presenter@microsoft.com / presenter123")
    print("=" * 50)

if __name__ == "__main__":
    create_test_users()
