#!/usr/bin/env python3
"""
Real-time Test Script
====================
Adds questions to Supabase database to test real-time subscriptions

Keep your browser open on http://localhost:3000/realtime-test 
and run this script to see questions appear instantly!
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question

def add_realtime_test_question():
    """Add a test question to see real-time updates"""
    
    # Get the test event (Tech Leadership AMA)
    try:
        event = Event.objects.get(id='daf3690d-784e-49bb-8ec0-547cc4cc2d8b')
        print(f"✅ Found test event: {event.name}")
    except Event.DoesNotExist:
        print("❌ Test event not found! Make sure sample data is created.")
        return
    
    # Get a test user
    try:
        user = User.objects.filter(role='user').first()
        if not user:
            user = User.objects.first()
        print(f"✅ Using user: {user.name}")
    except:
        print("❌ No users found! Make sure sample data is created.")
        return
    
    # Create a test question with timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    question_text = f"🔄 Real-time test question added at {timestamp} - This should appear instantly in your browser!"
    
    question = Question.objects.create(
        event=event,
        author=user,
        text=question_text,
        is_anonymous=False,
        upvotes=0
    )
    
    print(f"🎉 Created question: {question.text}")
    print(f"📝 Question ID: {question.id}")
    print(f"⏰ Created at: {question.created_at}")
    print("")
    print("👀 Check your browser - the question should appear instantly!")
    print("🔄 Run this script again to add more questions")

if __name__ == "__main__":
    print("🚀 Real-time Test - Adding Question to Database")
    print("=" * 50)
    add_realtime_test_question()
