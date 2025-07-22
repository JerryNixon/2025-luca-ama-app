#!/usr/bin/env python3
"""
Test Supabase WebSocket Connection - Alternative Implementation
Since replication is not available, this tests the direct Supabase approach.
"""
import os
import sys
import django
import asyncio
import time

# Add the backend directory to the Python path
backend_path = os.path.abspath('./backend')
sys.path.insert(0, backend_path)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import User, Event, Question

def test_supabase_websocket_approach():
    """Test the WebSocket approach with current setup"""
    print("🧪 Testing Supabase WebSocket Approach")
    print("=" * 50)
    
    # 1. Check our event
    try:
        event = Event.objects.get(title="Tech Leadership AMA")
        print(f"✅ Event found: {event.title} (ID: {event.id})")
    except Event.DoesNotExist:
        print("❌ Event not found")
        return
    
    # 2. Check current questions
    questions = Question.objects.filter(event=event)
    print(f"📊 Current questions: {questions.count()}")
    
    # 3. Create a new test question
    try:
        author = User.objects.filter(role='user').first()
        if not author:
            print("⚠️  No user found, creating test user...")
            author = User.objects.create(
                name="WebSocket Test User",
                email="websocket@test.com",
                role="user"
            )
            print(f"✅ Created test user: {author.name}")
        
        # Create a test question
        test_question = Question.objects.create(
            event=event,
            author=author,
            text=f"🔥 WebSocket Test Question - {int(time.time())}",
            is_anonymous=False
        )
        
        print(f"✅ Created test question:")
        print(f"   ID: {test_question.id}")
        print(f"   Text: {test_question.text}")
        print(f"   Author: {test_question.author.name}")
        print(f"   Created: {test_question.created_at}")
        
        # 4. Verify it's in database
        db_question = Question.objects.get(id=test_question.id)
        print(f"✅ Verified in database: {db_question.text}")
        
        # 5. Show what the frontend should receive
        print(f"\n📡 Frontend should receive WebSocket update:")
        print(f"   Event Type: INSERT")
        print(f"   Table: api_question")
        print(f"   Record: {{")
        print(f"     id: '{db_question.id}'")
        print(f"     event_id: '{db_question.event.id}'")
        print(f"     text: '{db_question.text}'")
        print(f"     author_id: '{db_question.author.id}'")
        print(f"     created_at: '{db_question.created_at}'")
        print(f"   }}")
        
        print(f"\n🌐 Check your browser at http://localhost:3000/realtime-test")
        print(f"   The question should appear instantly if WebSocket is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test question: {e}")
        return False

def show_websocket_status():
    """Show current status for WebSocket testing"""
    print("\n📊 WebSocket Test Status")
    print("=" * 30)
    
    print("✅ RLS Policies Created:")
    print("   - api_question (authenticated users can read)")
    print("   - api_event (authenticated users can read)")
    
    print("\n❌ Replication Status:")
    print("   - Feature not available yet (Early Access)")
    print("   - Using JavaScript client approach instead")
    
    print("\n🔧 Current Approach:")
    print("   - Frontend: Supabase JavaScript client")
    print("   - Backend: Django continues to write to database")
    print("   - Real-time: Direct postgres_changes subscription")
    
    print("\n🧪 To Test:")
    print("   1. Open: http://localhost:3000/realtime-test")
    print("   2. Run this script to create test questions")
    print("   3. Watch for instant updates in browser")
    print("   4. Check browser console (F12) for connection logs")

if __name__ == "__main__":
    show_websocket_status()
    print()
    if test_supabase_websocket_approach():
        print(f"\n✅ Test completed! Check the frontend for real-time update.")
    else:
        print(f"\n❌ Test failed. Check the errors above.")
