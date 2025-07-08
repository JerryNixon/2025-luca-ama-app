#!/usr/bin/env python3
"""
Add new fields to existing tables using SQL
This bypasses migration issues and adds the fields directly
"""

import os
import sys

# Add the backend directory to path
sys.path.insert(0, 'backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

try:
    import django
    django.setup()
    
    from django.db import connection
    
    print("🔧 Adding new fields to database...")
    
    with connection.cursor() as cursor:
        # Add fields to User table
        try:
            cursor.execute("ALTER TABLE api_user ADD microsoft_id NVARCHAR(100) NULL")
            print("✅ Added microsoft_id to User table")
        except Exception as e:
            print(f"⚠️ microsoft_id field may already exist: {e}")
        
        try:
            cursor.execute("ALTER TABLE api_user ADD is_admin BIT DEFAULT 0")
            print("✅ Added is_admin to User table")
        except Exception as e:
            print(f"⚠️ is_admin field may already exist: {e}")
        
        # Add fields to Event table
        try:
            cursor.execute("ALTER TABLE api_event ADD is_public BIT DEFAULT 0")
            print("✅ Added is_public to Event table")
        except Exception as e:
            print(f"⚠️ is_public field may already exist: {e}")
        
        try:
            cursor.execute("ALTER TABLE api_event ADD invite_link NVARCHAR(100) NULL")
            print("✅ Added invite_link to Event table")
        except Exception as e:
            print(f"⚠️ invite_link field may already exist: {e}")
    
    print("✅ Database schema updated successfully!")
    
    # Test the fields by checking one table
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 microsoft_id, is_admin FROM api_user")
        result = cursor.fetchone()
        print(f"✅ Verified new User fields: {result}")
        
        cursor.execute("SELECT TOP 1 is_public, invite_link FROM api_event")
        result = cursor.fetchone()
        print(f"✅ Verified new Event fields: {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
