#!/usr/bin/env python
"""
Test script for the new moderator assignment and permission system.
Tests the updated backend views and serializers.
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question
from api.serializers import EventSerializer
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import json

def test_moderator_assignment():
    """Test moderator assignment during event creation and updates"""
    print("=" * 60)
    print("TESTING MODERATOR ASSIGNMENT SYSTEM")
    print("=" * 60)
    
    User = get_user_model()
    
    # Create test users
    creator = User.objects.create_user(
        username='creator',
        email='creator@example.com',
        password='testpass123'
    )
    
    moderator1 = User.objects.create_user(
        username='moderator1',
        email='moderator1@example.com',
        password='testpass123'
    )
    
    moderator2 = User.objects.create_user(
        username='moderator2',
        email='moderator2@example.com',
        password='testpass123'
    )
    
    participant = User.objects.create_user(
        username='participant',
        email='participant@example.com',
        password='testpass123'
    )
    
    print(f"✓ Created test users: {creator.username}, {moderator1.username}, {moderator2.username}, {participant.username}")
    
    # Test 1: Create event with moderator assignment
    print("\n1. Testing event creation with moderator assignment...")
    
    factory = APIRequestFactory()
    request = factory.post('/api/events/', {
        'name': 'Test Event with Moderators',
        'open_date': datetime.now().isoformat(),
        'close_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'moderator_emails': ['moderator1@example.com', 'moderator2@example.com'],
        'is_public': True
    })
    request.user = creator
    
    serializer = EventSerializer(data={
        'name': 'Test Event with Moderators',
        'open_date': datetime.now(),
        'close_date': datetime.now() + timedelta(days=1),
        'moderator_emails': ['moderator1@example.com', 'moderator2@example.com'],
        'is_public': True
    }, context={'request': request})
    
    if serializer.is_valid():
        event = serializer.save(created_by=creator)
        print(f"✓ Event created: {event.name}")
        print(f"  - Creator: {event.created_by.username}")
        print(f"  - Moderators: {[m.username for m in event.moderators.all()]}")
        print(f"  - Expected: creator, moderator1, moderator2")
        
        # Test permissions
        print("\n2. Testing permission methods...")
        test_users = [creator, moderator1, moderator2, participant]
        
        for user in test_users:
            role = event.get_user_role_in_event(user)
            can_moderate = event.can_user_moderate(user)
            can_access = event.can_user_access(user)
            print(f"  - {user.username}: role={role}, can_moderate={can_moderate}, can_access={can_access}")
        
        # Test 3: Update event moderators
        print("\n3. Testing moderator update...")
        
        update_request = factory.patch('/api/events/', {
            'moderator_emails': ['moderator1@example.com']  # Remove moderator2
        })
        update_request.user = creator
        
        update_serializer = EventSerializer(
            event, 
            data={'moderator_emails': ['moderator1@example.com']},
            context={'request': update_request},
            partial=True
        )
        
        if update_serializer.is_valid():
            updated_event = update_serializer.save()
            print(f"✓ Event updated")
            print(f"  - Moderators after update: {[m.username for m in updated_event.moderators.all()]}")
        else:
            print(f"✗ Update failed: {update_serializer.errors}")
    else:
        print(f"✗ Event creation failed: {serializer.errors}")
    
    # Test 4: Test non-existent moderator email
    print("\n4. Testing non-existent moderator email...")
    
    test_request = factory.post('/api/events/', {
        'name': 'Test Event 2',
        'open_date': datetime.now().isoformat(),
        'close_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'moderator_emails': ['nonexistent@example.com', 'moderator1@example.com'],
        'is_public': True
    })
    test_request.user = creator
    
    test_serializer = EventSerializer(data={
        'name': 'Test Event 2',
        'open_date': datetime.now(),
        'close_date': datetime.now() + timedelta(days=1),
        'moderator_emails': ['nonexistent@example.com', 'moderator1@example.com'],
        'is_public': True
    }, context={'request': test_request})
    
    if test_serializer.is_valid():
        test_event = test_serializer.save(created_by=creator)
        print(f"✓ Event created despite non-existent email")
        print(f"  - Moderators: {[m.username for m in test_event.moderators.all()]}")
        print(f"  - Should only have creator and moderator1")
    else:
        print(f"✗ Event creation failed: {test_serializer.errors}")

def test_permission_edge_cases():
    """Test edge cases for the permission system"""
    print("\n" + "=" * 60)
    print("TESTING PERMISSION EDGE CASES")
    print("=" * 60)
    
    User = get_user_model()
    
    # Create admin user
    admin = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123',
        is_admin=True
    )
    
    # Create regular user
    regular_user = User.objects.create_user(
        username='regular',
        email='regular@example.com',
        password='testpass123'
    )
    
    # Create event
    event = Event.objects.create(
        name='Test Event',
        created_by=regular_user,
        open_date=datetime.now(),
        close_date=datetime.now() + timedelta(days=1),
        is_public=False
    )
    
    print(f"✓ Created private event by {regular_user.username}")
    
    # Test admin permissions
    print("\n1. Testing admin permissions...")
    admin_role = event.get_user_role_in_event(admin)
    admin_can_moderate = event.can_user_moderate(admin)
    admin_can_access = event.can_user_access(admin)
    
    print(f"  - Admin role: {admin_role}")
    print(f"  - Admin can moderate: {admin_can_moderate}")
    print(f"  - Admin can access: {admin_can_access}")
    print(f"  - Expected: admin should have access to all events")
    
    # Test public vs private events
    print("\n2. Testing public vs private event access...")
    
    # Create public event
    public_event = Event.objects.create(
        name='Public Event',
        created_by=regular_user,
        open_date=datetime.now(),
        close_date=datetime.now() + timedelta(days=1),
        is_public=True
    )
    
    # Create another user
    visitor = User.objects.create_user(
        username='visitor',
        email='visitor@example.com',
        password='testpass123'
    )
    
    # Test visitor access to public event
    visitor_public_access = public_event.can_user_access(visitor)
    visitor_public_role = public_event.get_user_role_in_event(visitor)
    
    print(f"  - Visitor access to public event: {visitor_public_access}")
    print(f"  - Visitor role in public event: {visitor_public_role}")
    
    # Test visitor access to private event
    visitor_private_access = event.can_user_access(visitor)
    visitor_private_role = event.get_user_role_in_event(visitor)
    
    print(f"  - Visitor access to private event: {visitor_private_access}")
    print(f"  - Visitor role in private event: {visitor_private_role}")
    
    print("\n3. Testing participant vs moderator permissions...")
    
    # Add visitor as participant to private event
    event.participants.add(visitor)
    
    visitor_participant_access = event.can_user_access(visitor)
    visitor_participant_role = event.get_user_role_in_event(visitor)
    visitor_participant_moderate = event.can_user_moderate(visitor)
    
    print(f"  - Visitor as participant - access: {visitor_participant_access}, role: {visitor_participant_role}, moderate: {visitor_participant_moderate}")
    
    # Add visitor as moderator
    event.moderators.add(visitor)
    
    visitor_moderator_access = event.can_user_access(visitor)
    visitor_moderator_role = event.get_user_role_in_event(visitor)
    visitor_moderator_moderate = event.can_user_moderate(visitor)
    
    print(f"  - Visitor as moderator - access: {visitor_moderator_access}, role: {visitor_moderator_role}, moderate: {visitor_moderator_moderate}")

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 60)
    print("CLEANING UP TEST DATA")
    print("=" * 60)
    
    User = get_user_model()
    
    # Delete test users
    test_usernames = ['creator', 'moderator1', 'moderator2', 'participant', 'admin', 'regular', 'visitor']
    deleted_count = 0
    
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            user.delete()
            deleted_count += 1
            print(f"✓ Deleted user: {username}")
        except User.DoesNotExist:
            pass
    
    # Delete test events
    test_events = Event.objects.filter(name__startswith='Test Event')
    event_count = test_events.count()
    test_events.delete()
    
    print(f"✓ Deleted {event_count} test events")
    print(f"✓ Cleaned up {deleted_count} test users")

if __name__ == '__main__':
    try:
        test_moderator_assignment()
        test_permission_edge_cases()
        cleanup_test_data()
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
