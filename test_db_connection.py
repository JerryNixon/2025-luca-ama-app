#!/usr/bin/env python3
"""
Database connection test script for AMA backend
Tests both SQLite and Fabric SQL connections
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

def test_sqlite():
    """Test SQLite database connection"""
    print("🔍 Testing SQLite Database Connection...")
    
    # Set environment variable for SQLite
    os.environ['USE_SQLITE'] = 'True'
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ SQLite connection successful!")
            return True
        else:
            print("❌ SQLite connection failed - unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return False

def test_fabric_sql():
    """Test Fabric SQL database connection"""
    print("\n🔍 Testing Fabric SQL Database Connection...")
    
    # Set environment variable for Fabric SQL
    os.environ['USE_SQLITE'] = 'False'
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Fabric SQL connection successful!")
            return True
        else:
            print("❌ Fabric SQL connection failed - unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ Fabric SQL connection failed: {e}")
        print("   This might be due to:")
        print("   - ODBC driver compatibility issues")
        print("   - Network connectivity problems")
        print("   - Authentication configuration")
        return False

def main():
    """Main test function"""
    print("🚀 AMA Backend Database Connection Test")
    print("=" * 50)
    
    # Test SQLite first
    sqlite_ok = test_sqlite()
    
    # Test Fabric SQL
    fabric_ok = test_fabric_sql()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"SQLite:    {'✅ Working' if sqlite_ok else '❌ Failed'}")
    print(f"Fabric SQL: {'✅ Working' if fabric_ok else '❌ Failed'}")
    
    if sqlite_ok:
        print("\n💡 Recommendation:")
        print("   Use SQLite for development (USE_SQLITE=True)")
        print("   Switch to Fabric SQL for production (USE_SQLITE=False)")
    
    return sqlite_ok or fabric_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
