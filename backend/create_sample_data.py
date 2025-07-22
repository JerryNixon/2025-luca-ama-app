#!/usr/bin/env python3
"""
Create Sample Data for Supabase AMA App
=======================================
Creates sample events, users, and questions for testing
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question
from django.contrib.auth.hashers import make_password
from django.utils import timezone

def create_sample_data():
    """Create sample users, events, and questions"""
    
    print("🎭 Creating Sample Data for AMA App...")
    print("-" * 50)
    
    try:
        # Create sample users
        print("👥 Creating sample users...")
        
        # Regular users
        users = []
        user_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'name': 'John Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'name': 'Jane Smith'},
            {'username': 'presenter1', 'email': 'presenter@example.com', 'name': 'Alex Presenter'},
            {'username': 'participant1', 'email': 'participant@example.com', 'name': 'Sam Participant'},
        ]
        
        for user_info in user_data:
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info['username'],
                    'password': make_password('password123'),
                    'name': user_info['name'],
                    'role': 'user',
                    'is_active': True,
                    'auth_source': 'manual'
                }
            )
            if created:
                print(f"   ✅ Created user: {user.name} ({user.email})")
            else:
                print(f"   ℹ️ User exists: {user.name} ({user.email})")
            users.append(user)
        
        # Create sample events
        print("\n🎪 Creating sample events...")
        
        admin = User.objects.filter(is_superuser=True).first()
        presenter = users[2]  # Alex Presenter
        
        events_data = [
            {
                'name': 'Tech Leadership AMA',
                'open_date': timezone.now() - timedelta(hours=1),
                'close_date': timezone.now() + timedelta(hours=2),
                'created_by': admin,
                'is_public': True,
                'is_active': True
            },
            {
                'name': 'Supabase vs Traditional Databases',
                'open_date': timezone.now() - timedelta(minutes=30),
                'close_date': timezone.now() + timedelta(hours=1),
                'created_by': presenter,
                'is_public': False,
                'is_active': True
            },
            {
                'name': 'Career Development Q&A',
                'open_date': timezone.now() + timedelta(hours=1),
                'close_date': timezone.now() + timedelta(hours=3),
                'created_by': admin,
                'is_public': True,
                'is_active': True
            }
        ]
        
        events = []
        for event_info in events_data:
            event, created = Event.objects.get_or_create(
                name=event_info['name'],
                defaults=event_info
            )
            if created:
                print(f"   ✅ Created event: {event.name}")
                # Generate share link
                event.generate_share_link()
                event.save()
                print(f"      🔗 Share link: {event.share_link}")
            else:
                print(f"   ℹ️ Event exists: {event.name}")
            events.append(event)
        
        # Add participants and moderators
        print("\n👨‍💼 Adding participants and moderators...")
        for event in events:
            # Add some users as participants
            event.participants.add(users[0], users[1], users[3])
            # Add presenter as moderator for some events
            if event.created_by != presenter:
                event.moderators.add(presenter)
            print(f"   ✅ Added participants to: {event.name}")
        
        # Create sample questions
        print("\n❓ Creating sample questions...")
        
        questions_data = [
            {
                'text': 'How do you handle technical debt while maintaining feature velocity?',
                'author': users[0],
                'event': events[0],
                'is_anonymous': False,
                'upvotes': 5
            },
            {
                'text': 'What are the main advantages of using Supabase over traditional PostgreSQL?',
                'author': users[1],
                'event': events[1],
                'is_anonymous': False,
                'upvotes': 3
            },
            {
                'text': 'How should I prepare for senior developer interviews?',
                'author': users[3],
                'event': events[2],
                'is_anonymous': True,
                'upvotes': 8
            },
            {
                'text': 'Can you explain the difference between scaling up vs scaling out?',
                'author': users[1],
                'event': events[0],
                'is_anonymous': False,
                'upvotes': 2
            }
        ]
        
        for question_info in questions_data:
            question, created = Question.objects.get_or_create(
                text=question_info['text'],
                defaults=question_info
            )
            if created:
                print(f"   ✅ Created question: {question.text[:50]}...")
            else:
                print(f"   ℹ️ Question exists: {question.text[:50]}...")
        
        print("\n" + "-" * 50)
        print("🎉 Sample Data Creation Complete!")
        print("\n📊 Summary:")
        print(f"   👥 Users: {User.objects.count()}")
        print(f"   🎪 Events: {Event.objects.count()}")
        print(f"   ❓ Questions: {Question.objects.count()}")
        
        print("\n🔗 Admin Access:")
        print("   URL: http://127.0.0.1:8000/admin/")
        print("   Email: admin@test.com")
        print("   Password: admin123")
        
        print("\n🎪 Sample Events:")
        for event in events:
            print(f"   • {event.name} (Share: {event.share_link})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_sample_data()
