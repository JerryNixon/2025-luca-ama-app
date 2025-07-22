#!/usr/bin/env python3
"""
Check table structure and create superuser for Azure SQL
"""
import os
import sys
import django
from datetime import datetime, timezone
import uuid

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from django.contrib.auth.hashers import make_password

def check_table_structure():
    """Check what columns exist in api_user table"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'api_user' 
            ORDER BY ORDINAL_POSITION
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print("Available columns in api_user:")
        for col in columns:
            print(f"  - {col}")
        return columns
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return []

def create_superuser_raw():
    """Create superuser using raw SQL to avoid model field issues"""
    try:
        # Check existing columns
        columns = check_table_structure()
        if not columns:
            return None
            
        cursor = connection.cursor()
        
        # Check if a superuser already exists
        cursor.execute("SELECT COUNT(*) FROM api_user WHERE is_superuser = 1")
        if cursor.fetchone()[0] > 0:
            print("✅ Superuser already exists")
            cursor.execute("SELECT email, name FROM api_user WHERE is_superuser = 1")
            result = cursor.fetchone()
            print(f"   Email: {result[0]}")
            print(f"   Name: {result[1]}")
            return True
        
        # Create superuser with available fields
        user_id = str(uuid.uuid4()).replace('-', '')
        password_hash = make_password('admin123')
        now = datetime.now(timezone.utc)
        
        # Build insert SQL with only available fields
        base_fields = {
            'id': user_id,
            'email': 'admin@test.com',
            'name': 'Admin User',
            'role': 'admin',
            'is_staff': 1,
            'is_superuser': 1,
            'is_active': 1,
            'is_anonymous': 0,
            'password': password_hash,
            'date_joined': now,
            'username': '',
            'first_name': '',
            'last_name': '',
            'last_login': None
        }
        
        # Add optional fields if they exist
        if 'is_admin' in columns:
            base_fields['is_admin'] = 1
        if 'microsoft_id' in columns:
            base_fields['microsoft_id'] = None
        if 'auth_source' in columns:
            base_fields['auth_source'] = 'manual'
            
        # Create the insert statement
        field_names = list(base_fields.keys())
        placeholders = ', '.join(['%s'] * len(field_names))
        field_names_str = ', '.join([f'[{name}]' for name in field_names])
        
        sql = f"INSERT INTO [api_user] ({field_names_str}) VALUES ({placeholders})"
        values = list(base_fields.values())
        
        print(f"Creating superuser with SQL: {sql}")
        cursor.execute(sql, values)
        
        print("✅ Superuser created successfully!")
        print("   Email: admin@test.com")
        print("   Password: admin123")
        print("   Name: Admin User")
        print(f"   ID: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Setting up superuser for Azure SQL...")
    success = create_superuser_raw()
    
    if success:
        print(f"\n🎉 Setup complete! You can now:")
        print(f"   1. Access Django admin at: http://localhost:8000/admin/")
        print(f"   2. Login with: admin@test.com / admin123")
        print(f"   3. Access the frontend at: http://localhost:3000/")
    else:
        print("❌ Failed to create superuser")
