#!/usr/bin/env python3
"""
Create a superuser for the Azure SQL database directly
"""
import os
import sys
import django
from datetime import datetime, timezone
import uuid

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User
from django.contrib.auth.hashers import make_password

def create_superuser():
    """Create a superuser directly in Azure SQL"""
    
    # Check if a superuser already exists
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"✅ Superuser already exists: {admin_user.email}")
            print(f"   Name: {admin_user.name}")
            print(f"   Role: {admin_user.role}")
            return admin_user
    except Exception as e:
        print(f"⚠️  Could not check for existing users: {e}")
    
    # Create a new superuser
    try:
        superuser = User.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            email='admin@test.com',
            name='Admin User',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_anonymous=False,
            is_admin=True,
            password=make_password('admin123'),  # Hash the password
            date_joined=datetime.now(timezone.utc)
        )
        
        print(f"✅ Superuser created successfully!")
        print(f"   Email: {superuser.email}")
        print(f"   Password: admin123")
        print(f"   Name: {superuser.name}")
        print(f"   Role: {superuser.role}")
        print(f"   ID: {superuser.id}")
        
        return superuser
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return None

def create_test_event():
    """Create a test event"""
    try:
        # Get the admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No admin user found to create event")
            return None
            
        # Check if test event already exists
        from api.models import Event
        test_event = Event.objects.filter(name='Test Event').first()
        if test_event:
            print(f"✅ Test event already exists: {test_event.name}")
            return test_event
            
        # Create a test event
        event = Event.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            name='Test Event',
            created_by=admin_user,
            is_active=True,
            is_public=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        print(f"✅ Test event created: {event.name}")
        print(f"   ID: {event.id}")
        print(f"   Created by: {event.created_by.name}")
        
        return event
        
    except Exception as e:
        print(f"❌ Error creating test event: {e}")
        return None

if __name__ == '__main__':
    print("🔧 Creating superuser for Azure SQL...")
    
    superuser = create_superuser()
    if superuser:
        event = create_test_event()
        
        print(f"\n🎉 Setup complete! You can now:")
        print(f"   1. Access Django admin at: http://localhost:8000/admin/")
        print(f"   2. Login with: admin@test.com / admin123")
        print(f"   3. Access the frontend at: http://localhost:3000/")
        
        if event:
            print(f"   4. Test the event: {event.name}")
    else:
        print("❌ Failed to create superuser")
