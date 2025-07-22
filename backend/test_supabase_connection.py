#!/usr/bin/env python3
"""
Supabase ORM Connection Test
===========================
Quick test to verify Django ORM is working with Supabase PostgreSQL
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

from api.models import User, Event

def test_supabase_orm():
    """Test basic ORM operations with Supabase"""
    
    print("🔗 Testing Supabase PostgreSQL ORM Connection...")
    print("-" * 50)
    
    try:
        # Test 1: Count existing users
        user_count = User.objects.count()
        print(f"✅ User count query successful: {user_count} users")
        
        # Test 2: Count existing events  
        event_count = Event.objects.count()
        print(f"✅ Event count query successful: {event_count} events")
        
        # Test 3: Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            print(f"✅ Database version: {db_version}")
        
        print("-" * 50)
        print("🎉 Supabase ORM Connection Test: SUCCESS!")
        print("💡 Django ORM is successfully connected to Supabase PostgreSQL")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_orm()
