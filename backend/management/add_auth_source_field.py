#!/usr/bin/env python3
"""
Add auth_source field to User model and update existing users
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from api.models import User

def add_auth_source_field():
    """Add auth_source field to User model"""
    print("🔧 ADDING AUTH_SOURCE FIELD TO USER MODEL")
    print("=" * 60)
    
    try:
        with connection.cursor() as cursor:
            # Check if auth_source field exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'api_user' 
                AND COLUMN_NAME = 'auth_source'
            """)
            
            field_exists = cursor.fetchone()[0] > 0
            
            if not field_exists:
                print("Adding auth_source field to api_user table...")
                cursor.execute("""
                    ALTER TABLE api_user 
                    ADD auth_source NVARCHAR(20) NOT NULL DEFAULT 'manual'
                """)
                print("✅ auth_source field added successfully")
            else:
                print("✅ auth_source field already exists")
        
        # Update existing users based on their microsoft_id
        print("\n📋 UPDATING EXISTING USERS...")
        
        # Users with microsoft_id should have auth_source = 'microsoft'
        microsoft_users = User.objects.filter(
            microsoft_id__isnull=False
        ).exclude(microsoft_id='')
        
        for user in microsoft_users:
            user.auth_source = 'microsoft'
            user.save()
            print(f"✅ Updated {user.email} to microsoft auth source")
        
        # Users without microsoft_id should have auth_source = 'manual'
        manual_users = User.objects.filter(
            microsoft_id__isnull=True
        ).union(User.objects.filter(microsoft_id=''))
        
        for user in manual_users:
            user.auth_source = 'manual'
            user.save()
            print(f"✅ Updated {user.email} to manual auth source")
        
        print(f"\n📊 SUMMARY:")
        print(f"Microsoft users: {microsoft_users.count()}")
        print(f"Manual users: {manual_users.count()}")
        print(f"Total users: {User.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_auth_source_field()
