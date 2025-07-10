#!/usr/bin/env python3
"""
Debug Current Events - Check what events are in the database
"""

import django
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import Event, User

def debug_events():
    print("🔍 Checking current events in database...")
    
    # Get all events
    events = Event.objects.all()
    print(f"📊 Total events in database: {events.count()}")
    
    for event in events:
        print(f"📝 Event ID: {event.id}")
        print(f"   Name: {event.name}")
        print(f"   Created by: {event.created_by.name if event.created_by else 'None'}")
        print(f"   Open date: {event.open_date}")
        print(f"   Created at: {event.created_at}")
        print()
    
    # Check users
    users = User.objects.all()
    print(f"👥 Total users: {users.count()}")
    
    for user in users:
        print(f"👤 User: {user.name} ({user.email}) - Role: {user.role}")

if __name__ == "__main__":
    debug_events()
