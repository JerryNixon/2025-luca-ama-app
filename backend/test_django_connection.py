"""
Test Django connection to Fabric SQL database.
"""

import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

def test_django_connection():
    print("🔍 Testing Django Connection to Fabric SQL")
    print("=" * 50)
    
    try:
        from django.db import connection
        
        print("🔄 Testing Django database connection...")
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✅ Django connection successful: {result}")
            
            # Check tables Django can see
            cursor.execute("SELECT name FROM sys.tables WHERE type = 'U' ORDER BY name")
            tables = cursor.fetchall()
            print(f"✅ Django can see {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
                
        print("\n🎉 Django is successfully connected to Fabric SQL!")
        print("📋 Database configuration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Django connection failed: {e}")
        return False

if __name__ == "__main__":
    test_django_connection()
