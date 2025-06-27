"""
Script to populate the database with sample data for testing.
Run this after the database is set up.
"""

import os
import django
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question

def create_sample_data():
    print("Creating sample data...")
    
    # Create sample users
    users_data = [
        {
            'id': 'user1',
            'email': 'john.doe@microsoft.com',
            'name': 'John Doe',
            'role': 'user'
        },
        {
            'id': 'user2',
            'email': 'jane.smith@microsoft.com',
            'name': 'Jane Smith',
            'role': 'presenter'
        },
        {
            'id': 'user3',
            'email': 'mike.wilson@microsoft.com',
            'name': 'Mike Wilson',
            'role': 'moderator'
        }
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            id=user_data['id'],
            defaults=user_data
        )
        users.append(user)
        if created:
            print(f"✅ Created user: {user.name}")
        else:
            print(f"ℹ️  User already exists: {user.name}")
    
    # Create sample events
    host = users[1]  # Jane Smith as presenter
    events_data = [
        {
            'id': 'event1',
            'name': 'Microsoft AI and Machine Learning AMA',
            'created_by': host,
            'open_date': datetime.now() + timedelta(days=1),
            'close_date': datetime.now() + timedelta(days=1, hours=2),
            'is_active': True,
            'share_link': 'https://teams.microsoft.com/event1'
        },
        {
            'id': 'event2',
            'name': 'Cloud Computing Best Practices',
            'created_by': host,
            'open_date': datetime.now() + timedelta(days=7),
            'close_date': datetime.now() + timedelta(days=7, hours=1, minutes=30),
            'is_active': True,
            'share_link': 'https://teams.microsoft.com/event2'
        }
    ]
    
    events = []
    for event_data in events_data:
        event, created = Event.objects.get_or_create(
            id=event_data['id'],
            defaults=event_data
        )
        events.append(event)
        if created:
            print(f"✅ Created event: {event.name}")
        else:
            print(f"ℹ️  Event already exists: {event.name}")
    
    # Create sample questions
    author = users[0]  # John Doe as question author
    questions_data = [
        {
            'id': 'q1',
            'text': 'What are the latest developments in GPT models and how can we integrate them into our enterprise applications?',
            'author': author,
            'event': events[0],
            'upvotes': 15,
            'is_answered': False,
            'is_starred': True,
            'is_anonymous': False
        },
        {
            'id': 'q2',
            'text': 'How do we ensure AI model fairness and prevent bias in our machine learning algorithms?',
            'author': author,
            'event': events[0],
            'upvotes': 12,
            'is_answered': True,
            'is_starred': False,
            'is_anonymous': False
        },
        {
            'id': 'q3',
            'text': 'What are the cost optimization strategies for Azure Cognitive Services at scale?',
            'author': users[2],
            'event': events[1],
            'upvotes': 8,
            'is_answered': False,
            'is_starred': False,
            'is_anonymous': True
        }
    ]
    
    for question_data in questions_data:
        question, created = Question.objects.get_or_create(
            id=question_data['id'],
            defaults=question_data
        )
        if created:
            print(f"✅ Created question: {question.text[:50]}...")
        else:
            print(f"ℹ️  Question already exists: {question.text[:50]}...")
    
    print(f"\n🎉 Sample data creation complete!")
    print(f"📊 Database summary:")
    print(f"   - Users: {User.objects.count()}")
    print(f"   - Events: {Event.objects.count()}")
    print(f"   - Questions: {Question.objects.count()}")

if __name__ == "__main__":
    create_sample_data()
