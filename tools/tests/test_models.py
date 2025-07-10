#!/usr/bin/env python3
"""
Test the updated models with new fields
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
    
    from api.models import User, Event
    
    print("🔍 Testing updated models...")
    
    # Test User model with new fields
    print("\n👤 Testing User model:")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"- {user.name} ({user.email})")
        print(f"  Role: {user.role}")
        print(f"  Microsoft ID: {user.microsoft_id}")
        print(f"  Is Admin: {user.is_admin}")
        print(f"  Can create events: {user.can_create_events()}")
        print(f"  Is system admin: {user.is_system_admin()}")
        print()
    
    # Test Event model with new fields
    print("📅 Testing Event model:")
    events = Event.objects.all()
    print(f"Total events: {events.count()}")
    
    for event in events:
        print(f"- {event.name}")
        print(f"  Created by: {event.created_by.name}")
        print(f"  Is public: {event.is_public}")
        print(f"  Invite link: {event.invite_link}")
        print(f"  Share link: {event.share_link}")
        
        # Test permission methods
        creator = event.created_by
        print(f"  Creator can moderate: {event.can_user_moderate(creator)}")
        print(f"  Creator can access: {event.can_user_access(creator)}")
        print(f"  Creator role in event: {event.get_user_role_in_event(creator)}")
        print()
    
    print("✅ Model testing completed successfully!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
