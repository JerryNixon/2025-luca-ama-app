#!/usr/bin/env python
"""
Create Sample Event and Questions for Testing
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample event and questions for testing"""
    
    print("📅 Creating Sample AMA Event and Questions")
    print("=" * 50)
    
    # Get admin user
    admin = User.objects.get(email='admin@test.com')
    user = User.objects.get(email='user@test.com')
    
    # Create sample event
    event, created = Event.objects.get_or_create(
        name="Docker Performance Test AMA",
        defaults={
            'created_by': admin,
            'is_active': True,
            'is_public': True,
            'open_date': datetime.now(),
            'close_date': datetime.now() + timedelta(days=7)
        }
    )
    
    status = "Created" if created else "Found existing"
    print(f"✅ {status} event: {event.name}")
    print(f"   - ID: {event.id}")
    print(f"   - Created by: {event.created_by.name}")
    
    # Add some sample questions
    sample_questions = [
        "How does the Docker SQL Server performance compare to Microsoft Fabric?",
        "What are the best practices for Django ORM optimization?",
        "How can we monitor database query performance in production?",
        "What factors affect latency in cloud vs local databases?",
        "How do connection pools impact database performance?"
    ]
    
    questions_created = 0
    for i, question_text in enumerate(sample_questions):
        question, created = Question.objects.get_or_create(
            text=question_text,
            event=event,
            defaults={
                'author': user if i % 2 == 0 else admin,
                'is_anonymous': i % 3 == 0,
                'upvotes': i * 2  # Give some initial votes
            }
        )
        
        if created:
            questions_created += 1
            print(f"✅ Created question: {question_text[:50]}...")
    
    print(f"\n🎉 Sample data ready!")
    print(f"   - Event: {event.name}")
    print(f"   - Questions created: {questions_created}")
    print(f"   - Total questions: {event.questions.count()}")
    
    print(f"\n🌐 Test the event at: http://localhost:3000")
    print(f"📋 Event ID: {event.id}")

if __name__ == "__main__":
    create_sample_data()
