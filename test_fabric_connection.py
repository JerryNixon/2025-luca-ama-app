#!/usr/bin/env python3
"""
Quick test to verify Fabric SQL connection is working
"""
import os
import sys
import django
from pathlib import Path

# Set up Django environment
project_root = Path(__file__).parent / 'backend'
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    
    if result:
        print("✅ Fabric SQL connection successful!")
        print(f"🗄️  Connected to database: {connection.settings_dict['NAME']}")
        print(f"🖥️  Host: {connection.settings_dict['HOST']}")
        
        # Test basic ORM functionality
        from api.models import User
        user_count = User.objects.count()
        print(f"👥 Users in database: {user_count}")
        
    else:
        print("❌ Database connection failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
