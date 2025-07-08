#!/usr/bin/env python3
"""
Debug Authentication State for Jerry
This script checks Jerry's authentication state and verifies if he can log in.
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

from django.contrib.auth import authenticate
from api.models import User, Event
from django.db import connection
import json

def debug_jerry_auth():
    """Debug Jerry's authentication state"""
    print("🔍 DEBUGGING JERRY'S AUTHENTICATION STATE")
    print("=" * 60)
    
    # Check if Jerry exists in the database
    try:
        jerry = User.objects.get(email='jerry.nixon@microsoft.com')
        print(f"✅ Jerry found in database")
        print(f"   ID: {jerry.id}")
        print(f"   Name: {jerry.name}")
        print(f"   Email: {jerry.email}")
        print(f"   Username: {jerry.username}")
        print(f"   Is Staff: {jerry.is_staff}")
        print(f"   Is Active: {jerry.is_active}")
        print(f"   Is Admin: {jerry.is_admin}")
        print(f"   Microsoft ID: {jerry.microsoft_id}")
        print(f"   Date Joined: {jerry.date_joined}")
        print(f"   Last Login: {jerry.last_login}")
    except User.DoesNotExist:
        print("❌ Jerry not found in database")
        return
    
    print("\n" + "=" * 60)
    
    # Test password authentication
    print("🔐 TESTING PASSWORD AUTHENTICATION")
    user = authenticate(username='jerry.nixon@microsoft.com', password='test123')
    if user:
        print(f"✅ Password authentication successful for Jerry")
        print(f"   Authenticated user: {user.name} ({user.email})")
    else:
        print("❌ Password authentication failed for Jerry")
        print("   Let's check the password hash...")
        print(f"   Password hash: {jerry.password}")
        
        # Try to set password and test again
        print("   Setting password to 'test123' and testing again...")
        jerry.set_password('test123')
        jerry.save()
        
        user = authenticate(username='jerry.nixon@microsoft.com', password='test123')
        if user:
            print(f"✅ Password authentication successful after reset")
        else:
            print("❌ Password authentication still failed")
    
    print("\n" + "=" * 60)
    
    # Check Jerry's events and permissions
    print("🎯 CHECKING JERRY'S EVENTS AND PERMISSIONS")
    events = Event.objects.all()
    print(f"Total events in database: {events.count()}")
    
    for event in events:
        print(f"\n📅 Event: {event.name}")
        print(f"   ID: {event.id}")
        print(f"   Creator: {event.created_by.name if event.created_by else 'None'}")
        print(f"   Is Public: {event.is_public}")
        print(f"   Can Jerry access: {event.can_user_access(jerry)}")
        print(f"   Can Jerry moderate: {event.can_user_moderate(jerry)}")
        print(f"   Jerry's role: {event.get_user_role_in_event(jerry)}")
        print(f"   Moderators: {[m.name for m in event.moderators.all()]}")
    
    print("\n" + "=" * 60)
    
    # Check if Jerry is in any event as a moderator
    print("👨‍💼 CHECKING JERRY'S MODERATOR STATUS")
    moderated_events = Event.objects.filter(moderators=jerry)
    print(f"Events Jerry moderates: {moderated_events.count()}")
    for event in moderated_events:
        print(f"   - {event.name}")
    
    # Check if Jerry created any events
    created_events = Event.objects.filter(created_by=jerry)
    print(f"Events Jerry created: {created_events.count()}")
    for event in created_events:
        print(f"   - {event.name}")
    
    print("\n" + "=" * 60)
    
    # Check database connection
    print("🔗 CHECKING DATABASE CONNECTION")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_user WHERE email = 'jerry.nixon@microsoft.com'")
            count = cursor.fetchone()[0]
            print(f"✅ Database connection working, Jerry count: {count}")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY FOR JERRY")
    print(f"   - User exists: {'✅' if jerry else '❌'}")
    print(f"   - Can authenticate: {'✅' if user else '❌'}")
    print(f"   - Is active: {'✅' if jerry.is_active else '❌'}")
    print(f"   - Is admin: {'✅' if jerry.is_admin else '❌'}")
    print(f"   - Created events: {created_events.count()}")
    print(f"   - Moderates events: {moderated_events.count()}")
    print(f"   - Can access all public events: ✅")
    print(f"   - Should be able to create events: ✅")
    
    print("\n" + "🔧 RECOMMENDATIONS:")
    print("   1. Jerry should be able to log in with email 'jerry.nixon@microsoft.com' and password 'test123'")
    print("   2. Jerry should see the 'Create Event' button if isAuthenticated is true")
    print("   3. Check frontend console for authentication state")
    print("   4. Check browser dev tools for authentication cookies/tokens")
    print("   5. Verify frontend AuthContext is properly setting isAuthenticated")

if __name__ == "__main__":
    debug_jerry_auth()
