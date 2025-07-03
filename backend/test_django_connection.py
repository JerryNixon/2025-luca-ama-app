#!/usr/bin/env python
"""
Test Django ORM connection to Fabric SQL Database
"""
import os
import django
from django.conf import settings
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

def test_database_connection():
    """Test the database connection using Django ORM."""
    try:
        print("Testing Django database connection...")
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
            print(f"✅ Database connection successful: {result}")
            
            # Test getting database info
            cursor.execute("SELECT @@VERSION as version")
            version = cursor.fetchone()
            print(f"✅ Database version: {version[0]}")
            
            # List existing tables
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            print(f"✅ Found {len(tables)} existing tables:")
            for table in tables:
                print(f"   - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
