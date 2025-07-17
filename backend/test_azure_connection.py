#!/usr/bin/env python3
"""
Quick Azure SQL Connection Test
"""
import os
import django

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azure_sql_settings')
django.setup()

from django.db import connection

def test_connection():
    print("🔄 Testing Azure SQL Database connection...")
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✅ SUCCESS: Connected to Azure SQL Database")
            print(f"📊 Test query result: {result}")
            
        # Test database info
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"🗄️ Database version: {version[0][:100]}...")
            
        # Test if we can see existing tables (if any)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            print(f"📋 Existing tables: {len(tables)} found")
            for table in tables[:5]:  # Show first 5 tables
                print(f"   - {table[0]}")
            
        print("\n🎯 Azure SQL Database is fully accessible!")
        return True
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Check common issues
        if "Login failed" in str(e):
            print("💡 Issue: Invalid username or password")
        elif "cannot open server" in str(e) or "timeout" in str(e):
            print("💡 Issue: Network/firewall - check if your IP is allowed")
        elif "SSL" in str(e) or "certificate" in str(e):
            print("💡 Issue: SSL/TLS certificate problem")
        
        return False

if __name__ == "__main__":
    test_connection()
