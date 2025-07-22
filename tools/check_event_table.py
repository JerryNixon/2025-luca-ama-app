import os
import django
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)
os.chdir(backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from api.models import Event

def check_event_table_structure():
    """Check the actual Event table structure in the database"""
    print("🔍 Checking Event table structure...")
    
    # Get table structure using Django's connection
    with connection.cursor() as cursor:
        # Check if table exists and get its structure
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'api_event'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        
        print(f"📋 Event table columns ({len(columns)} total):")
        for column_name, data_type, is_nullable, default_value in columns:
            print(f"  - {column_name}: {data_type} (nullable: {is_nullable}, default: {default_value})")
    
    # Also check what Django thinks the model fields are
    print("\n🧩 Django model fields:")
    for field in Event._meta.get_fields():
        if hasattr(field, 'name'):
            print(f"  - {field.name}: {type(field).__name__}")

if __name__ == "__main__":
    check_event_table_structure()
