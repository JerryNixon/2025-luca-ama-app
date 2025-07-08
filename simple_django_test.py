#!/usr/bin/env python3
"""
Simple Django Test - Check if Django is working
"""

import os
import sys

# Add the backend directory to path
sys.path.insert(0, 'backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

try:
    import django
    django.setup()
    
    from api.models import Event, User
    
    print("✅ Django setup successful")
    
    # Test database connection
    print(f"📊 Events in database: {Event.objects.count()}")
    print(f"👥 Users in database: {User.objects.count()}")
    
    # List events
    print("\n📝 Current events:")
    for event in Event.objects.all():
        print(f"  - {event.name} (ID: {event.id})")
    
    # List users
    print("\n👤 Current users:")
    for user in User.objects.all():
        print(f"  - {user.name} ({user.email}) - {user.role}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
