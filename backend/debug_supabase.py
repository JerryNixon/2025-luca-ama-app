#!/usr/bin/env python3
"""
Debug Supabase Connection
========================
Test if we can connect to Supabase from the backend
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

from django.db import connection
from api.models import User, Event, Question

def test_supabase_connection():
    """Test database connection and basic queries"""
    
    print("🔍 Testing Supabase Connection...")
    print("=" * 40)
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Database connected: {version}")
    
        # Test our tables exist
        try:
            user_count = User.objects.count()
            event_count = Event.objects.count()
            question_count = Question.objects.count()
            
            print(f"📊 Database Contents:")
            print(f"   Users: {user_count}")
            print(f"   Events: {event_count}")
            print(f"   Questions: {question_count}")
            
            # Check if our test event exists
            try:
                test_event = Event.objects.get(id='06c61a8b-2763-4b04-871b-3ff7ad60f1f5')
                print(f"✅ Test event found: {test_event.name}")
                
                # Get questions for this event
                event_questions = Question.objects.filter(event=test_event)
                print(f"📝 Questions in test event: {event_questions.count()}")
                
                for q in event_questions[:3]:
                    print(f"   - {q.text[:50]}...")
                    
            except Event.DoesNotExist:
                print("❌ Test event not found!")
                
        except Exception as e:
            print(f"❌ Error querying tables: {e}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
        
    return True

def test_direct_supabase():
    """Test direct connection to Supabase using supabase-py"""
    
    print("\n🔗 Testing Direct Supabase Connection...")
    print("=" * 40)
    
    try:
        # Try importing supabase
        from supabase import create_client, Client
        
        # Connection details
        url = "https://eysipjwmfgtvmjqgfojn.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5c2lwandtZmd0dm1qcWdmb2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwNDc3NzQsImV4cCI6MjA1MjYyMzc3NH0.1r8vNJIlEG5dTTJGf_LCuA_vQOJILnK8ZM5HryUMUGM"
        
        supabase: Client = create_client(url, key)
        
        # Test query
        result = supabase.table("api_question").select("*").limit(1).execute()
        
        print(f"✅ Direct Supabase connection successful")
        print(f"📊 Sample query result: {len(result.data)} records")
        
        return True
        
    except ImportError:
        print("❌ supabase-py not installed")
        print("   Run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Direct Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Supabase Connection Diagnosis")
    print("=" * 50)
    
    # Test Django connection
    django_ok = test_supabase_connection()
    
    # Test direct Supabase connection
    supabase_ok = test_direct_supabase()
    
    print("\n📋 Summary:")
    print("=" * 20)
    print(f"Django to Supabase: {'✅' if django_ok else '❌'}")
    print(f"Direct Supabase: {'✅' if supabase_ok else '❌'}")
    
    if not django_ok:
        print("\n🔧 Troubleshooting Django Connection:")
        print("1. Check .env.supabase file exists")
        print("2. Verify Supabase credentials are correct")
        print("3. Run: python switch_to_supabase.py supabase")
        
    if not supabase_ok:
        print("\n🔧 Troubleshooting Direct Connection:")
        print("1. Install: pip install supabase")
        print("2. Check Supabase project is active")
        print("3. Verify API keys are correct")
