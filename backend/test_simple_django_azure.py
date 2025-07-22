#!/usr/bin/env python3
"""
Simple Django ORM Test for Azure SQL
Let's see if Django can connect with the standard mssql backend
"""

import os
import sys
import django

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azure_sql_settings')

# Setup Django
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def test_django_connection():
    """Test if Django can connect to Azure SQL"""
    
    print("🔄 Testing Django ORM connection to Azure SQL...")
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
            print(f"✅ Basic connection successful: {result}")
        
        # Test Django migrations table (realistic test)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'django_migrations'
            """)
            result = cursor.fetchone()
            print(f"✅ Django migrations table check: {result[0]} tables found")
        
        print("\n🎉 Django ORM connection to Azure SQL is working!")
        print("We can proceed with performance benchmarking using standard Django ORM")
        return True
        
    except Exception as e:
        print(f"❌ Django ORM connection failed: {e}")
        print("\nDebugging info:")
        print(f"  Host: {connection.settings_dict['HOST']}")
        print(f"  Database: {connection.settings_dict['NAME']}")
        print(f"  Engine: {connection.settings_dict['ENGINE']}")
        print(f"  Options: {connection.settings_dict.get('OPTIONS', {})}")
        return False

if __name__ == "__main__":
    test_django_connection()
