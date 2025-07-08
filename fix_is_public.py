#!/usr/bin/env python3
"""
Fix is_public field for all events
Some events have is_public=None which can cause issues
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import Event

def fix_is_public_field():
    """Fix is_public field for all events"""
    print("🔧 FIXING IS_PUBLIC FIELD FOR ALL EVENTS")
    print("=" * 60)
    
    events = Event.objects.all()
    print(f"Total events: {events.count()}")
    
    for event in events:
        print(f"\n📅 Event: {event.name}")
        print(f"   ID: {event.id}")
        print(f"   Current is_public: {event.is_public}")
        
        if event.is_public is None:
            # Set to True by default for universal access
            event.is_public = True
            event.save()
            print(f"   ✅ Updated is_public to: {event.is_public}")
        else:
            print(f"   ✅ is_public already set: {event.is_public}")
    
    print("\n" + "=" * 60)
    print("✅ All events now have is_public field set properly")

if __name__ == "__main__":
    fix_is_public_field()
