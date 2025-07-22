#!/usr/bin/env python3
"""
Create Superuser for Supabase AMA App
=====================================
Creates a superuser account to access Django admin panel
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User
from django.contrib.auth.hashers import make_password

def create_superuser():
    """Create a superuser for the AMA app"""
    
    print("🔑 Creating Superuser for Supabase AMA App...")
    print("-" * 50)
    
    try:
        # Check if superuser already exists
        existing_admin = User.objects.filter(is_superuser=True).first()
        if existing_admin:
            print(f"✅ Superuser already exists: {existing_admin.email}")
            print(f"   📧 Email: {existing_admin.email}")
            print(f"   👤 Username: {existing_admin.username}")
            print(f"   🎉 You can access Django Admin at: http://127.0.0.1:8000/admin/")
            return existing_admin
        
        # Create superuser manually
        superuser = User.objects.create(
            username='admin',
            email='admin@test.com',
            password=make_password('admin123'),
            name='Admin User',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_admin=True,
            auth_source='manual'
        )
        
        print(f"✅ Superuser created successfully!")
        print(f"   📧 Email: admin@test.com")
        print(f"   🔐 Password: admin123")
        print(f"   👤 Username: admin")
        print("-" * 50)
        print("🎉 You can now access Django Admin at: http://127.0.0.1:8000/admin/")
        
        return superuser
        
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_superuser()
