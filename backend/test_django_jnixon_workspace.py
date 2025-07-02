"""
Django test script for NEW Fabric SQL connection (jnixon-luca-workspace)
This tests if Django can connect to the new workspace database
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from django.core.management.color import color_style

def test_django_new_fabric_connection():
    """Test Django ORM connection to new Fabric workspace"""
    
    style = color_style()
    print("🔧 Testing Django Connection to NEW Fabric Workspace...")
    print("=" * 60)
    
    # Print current database configuration
    db_config = settings.DATABASES['default']
    print(f"🏢 Host: {db_config.get('HOST', 'Not set')}")
    print(f"🗄️  Database: {db_config.get('NAME', 'Not set')}")
    print(f"🚪 Port: {db_config.get('PORT', 'Not set')}")
    print(f"👤 User: {db_config.get('USER', 'Not set')}")
    print(f"🔐 Engine: {db_config.get('ENGINE', 'Not set')}")
    print("-" * 60)
    
    try:
        # Test basic connection
        print("🔌 Testing Django database connection...")
        
        with connection.cursor() as cursor:
            # Test basic query
            cursor.execute("SELECT @@VERSION as Version, DB_NAME() as DatabaseName, USER_NAME() as CurrentUser")
            result = cursor.fetchone()
            
            print("✅ DJANGO CONNECTION SUCCESSFUL!")
            print()
            print(f"📊 Database Version: {result[0]}")
            print(f"🗄️  Current Database: {result[1]}")
            print(f"👤 Connected as: {result[2]}")
            print()
            
            # Check if our Django tables exist
            print("📋 Checking for Django tables...")
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'dbo' 
                AND TABLE_NAME LIKE 'api_%' OR TABLE_NAME LIKE 'auth_%' OR TABLE_NAME LIKE 'django_%'
                ORDER BY TABLE_NAME
            """)
            
            django_tables = cursor.fetchall()
            
            if django_tables:
                print(f"Found {len(django_tables)} Django-related tables:")
                for table in django_tables:
                    print(f"   📊 {table[0]}")
                print()
                print("🎉 Your Django models are already in the database!")
            else:
                print("   ℹ️  No Django tables found")
                print("   📝 You'll need to run: python manage.py migrate")
            
            print()
            print("🚀 Django is ready to work with the new Fabric workspace!")
            
        return True
        
    except Exception as e:
        print(f"❌ Django connection failed!")
        print(f"🔍 Error details: {str(e)}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check your .env file configuration")
        print("   2. Make sure you're logged into Azure")
        print("   3. Verify settings.py DATABASE configuration")
        print("   4. Try: python manage.py dbshell")
        
        return False

if __name__ == "__main__":
    test_django_new_fabric_connection()
