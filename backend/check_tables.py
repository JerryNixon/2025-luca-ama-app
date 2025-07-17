#!/usr/bin/env python3
"""
Check tables in Azure SQL database
"""
import os
import sys
import django

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection

def check_tables():
    """Check what tables exist in the database"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            ORDER BY TABLE_NAME
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print("📋 Tables in Azure SQL database:")
        for table in tables:
            print(f"  ✅ {table}")
            
        # Check specifically for missing tables
        required_tables = [
            'django_session',
            'django_migrations',
            'api_user',
            'api_event',
            'api_question',
            'api_vote'
        ]
        
        print(f"\n🔍 Required tables status:")
        for table in required_tables:
            if table in tables:
                print(f"  ✅ {table} - EXISTS")
            else:
                print(f"  ❌ {table} - MISSING")
                
        return tables
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []

def create_sessions_table():
    """Create the django_session table manually"""
    try:
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'django_session'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("✅ django_session table already exists")
            return True
            
        # Create the sessions table
        cursor.execute("""
            CREATE TABLE [django_session] (
                [session_key] nvarchar(40) NOT NULL PRIMARY KEY,
                [session_data] nvarchar(max) NOT NULL,
                [expire_date] datetimeoffset NOT NULL
            )
        """)
        
        # Create index on expire_date
        cursor.execute("""
            CREATE INDEX [django_session_expire_date_a5c62663] 
            ON [django_session] ([expire_date])
        """)
        
        print("✅ Created django_session table")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sessions table: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Checking Azure SQL database tables...")
    
    tables = check_tables()
    
    if 'django_session' not in tables:
        print(f"\n🛠️  Creating missing django_session table...")
        if create_sessions_table():
            print(f"\n✅ Database setup complete!")
        else:
            print(f"\n❌ Failed to create sessions table")
    else:
        print(f"\n✅ All required tables exist!")
        
    print(f"\n🌐 You can now access the Django admin at: http://localhost:8000/admin/")
    print(f"   Login: admin@test.com / admin123")
