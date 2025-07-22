#!/usr/bin/env python
"""
Test connection to Microsoft Fabric SQL Database
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from django.core.management.color import make_style

style = make_style()

def test_fabric_connection():
    """Test connection to Microsoft Fabric SQL Database"""
    
    print(style.HTTP_INFO("🔗 Testing Microsoft Fabric SQL Database Connection..."))
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@VERSION, DB_NAME(), SYSTEM_USER")
            result = cursor.fetchone()
            
            print(style.SUCCESS("✅ Successfully connected to Microsoft Fabric SQL Database!"))
            print(f"📊 Database: {result[1]}")
            print(f"👤 User: {result[2]}")
            print(f"🔧 SQL Server Version: {result[0][:50]}...")
            
        # Test if we can list tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"📋 Found {len(tables)} existing tables:")
                for table in tables[:10]:  # Show first 10 tables
                    print(f"  - {table[0]}")
                if len(tables) > 10:
                    print(f"  ... and {len(tables) - 10} more tables")
            else:
                print("📋 No existing tables found (fresh database)")
            
        return True
        
    except Exception as e:
        print(style.ERROR(f"❌ Connection failed: {e}"))
        return False

if __name__ == "__main__":
    success = test_fabric_connection()
    sys.exit(0 if success else 1)
