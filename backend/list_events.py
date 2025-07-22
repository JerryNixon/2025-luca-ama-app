#!/usr/bin/env python3
"""
List Events in Supabase
=======================
Find actual event IDs for real-time testing
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question

def list_events():
    """List all events with their IDs and questions"""
    
    print("📋 Events in Supabase Database:")
    print("=" * 50)
    
    events = Event.objects.all().order_by('created_at')
    
    for event in events:
        print(f"🎯 Event: {event.name}")
        print(f"   ID: {event.id}")
        print(f"   Active: {event.is_active}")
        print(f"   Created: {event.created_at}")
        
        # Count questions for this event
        question_count = Question.objects.filter(event=event).count()
        print(f"   Questions: {question_count}")
        
        if question_count > 0:
            print(f"   📝 Sample questions:")
            questions = Question.objects.filter(event=event)[:3]
            for q in questions:
                print(f"      - {q.text[:60]}...")
        
        print()
    
    if events.exists():
        first_event = events.first()
        print(f"🎯 Use this Event ID for real-time testing:")
        print(f"   {first_event.id}")
        return first_event.id
    else:
        print("❌ No events found!")
        return None

if __name__ == "__main__":
    event_id = list_events()
