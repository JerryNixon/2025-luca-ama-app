#!/usr/bin/env python
"""
Quick Question Creation Latency Test for Microsoft Fabric

This script specifically tests Question.objects.create() latency on Fabric.
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from api.models import User, Event, Question


def test_fabric_question_creation():
    """Test Question.objects.create() latency on Microsoft Fabric"""
    
    print("☁️ Microsoft Fabric - Quick Question Creation Test")
    print("=" * 60)
    
    # Test database connection first
    print("🔌 Testing Fabric database connection...")
    start_time = time.perf_counter()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DB_NAME(), @@VERSION")
            result = cursor.fetchone()
            db_name = result[0]
            db_version = result[1][:80] + "..." if len(result[1]) > 80 else result[1]
        
        end_time = time.perf_counter()
        connection_time = (end_time - start_time) * 1000
        
        print(f"✅ Connected to: {db_name}")
        print(f"🔧 Version: {db_version}")
        print(f"⚡ Connection time: {connection_time:.2f} ms\n")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Get or create test user
    print("👤 Setting up test user...")
    start_time = time.perf_counter()
    
    try:
        user, created = User.objects.get_or_create(
            email="fabric_quick_test@example.com",
            defaults={
                'name': 'Fabric Quick Test User',
                'username': 'fabric_quick_test',
                'role': 'user'
            }
        )
        end_time = time.perf_counter()
        user_time = (end_time - start_time) * 1000
        
        action = "Created" if created else "Found existing"
        print(f"✅ {action} user: {user.name} ({user.id})")
        print(f"⚡ User setup time: {user_time:.2f} ms\n")
        
    except Exception as e:
        print(f"❌ User setup failed: {e}")
        return
    
    # Get or create test event
    print("📅 Setting up test event...")
    start_time = time.perf_counter()
    
    try:
        event, created = Event.objects.get_or_create(
            name="Fabric Quick Test Event",
            defaults={
                'created_by': user,
                'is_active': True,
                'is_public': True
            }
        )
        end_time = time.perf_counter()
        event_time = (end_time - start_time) * 1000
        
        action = "Created" if created else "Found existing"
        print(f"✅ {action} event: {event.name} ({event.id})")
        print(f"⚡ Event setup time: {event_time:.2f} ms\n")
        
    except Exception as e:
        print(f"❌ Event setup failed: {e}")
        return
    
    # Now test Question creation
    print("❓ Testing Question.objects.create() on Microsoft Fabric...")
    print("-" * 50)
    
    times = []
    created_questions = []
    
    # Test 10 question creations
    for i in range(10):
        question_text = f"Fabric Test Question {i+1} - {datetime.now().isoformat()}"
        
        start_time = time.perf_counter()
        
        try:
            question = Question.objects.create(
                text=question_text,
                event=event,
                author=user,
                is_anonymous=False
            )
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            times.append(duration_ms)
            created_questions.append(question)
            
            print(f"✅ Question {i+1}: {duration_ms:.2f} ms")
            
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print(f"❌ Question {i+1} FAILED: {duration_ms:.2f} ms - {e}")
    
    # Print results
    if times:
        print("\n📊 MICROSOFT FABRIC RESULTS:")
        print("=" * 40)
        print(f"Total questions created: {len(times)}")
        print(f"Average time: {sum(times)/len(times):.2f} ms")
        print(f"Fastest: {min(times):.2f} ms")
        print(f"Slowest: {max(times):.2f} ms")
        
        # Compare with Docker baseline
        docker_avg = 8.58  # From previous Docker test
        fabric_avg = sum(times)/len(times)
        difference = fabric_avg - docker_avg
        
        print(f"\n🔄 COMPARISON WITH DOCKER:")
        print(f"Docker average: {docker_avg:.2f} ms")
        print(f"Fabric average: {fabric_avg:.2f} ms")
        print(f"Difference: {difference:+.2f} ms ({((fabric_avg/docker_avg - 1) * 100):+.1f}%)")
        
        # Write to log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"fabric_quick_test_{timestamp}.txt", "w") as f:
            f.write(f"Microsoft Fabric Question Creation Test - {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n")
            f.write(f"Database: {db_name}\n")
            f.write(f"Connection time: {connection_time:.2f} ms\n")
            f.write(f"User setup time: {user_time:.2f} ms\n")
            f.write(f"Event setup time: {event_time:.2f} ms\n\n")
            f.write("Question Creation Times:\n")
            for i, time_ms in enumerate(times, 1):
                f.write(f"  Question {i}: {time_ms:.2f} ms\n")
            f.write(f"\nFabric Average: {fabric_avg:.2f} ms\n")
            f.write(f"Docker Average: {docker_avg:.2f} ms\n")
            f.write(f"Difference: {difference:+.2f} ms ({((fabric_avg/docker_avg - 1) * 100):+.1f}%)\n")
        
        print(f"📝 Results saved to: fabric_quick_test_{timestamp}.txt")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    try:
        for question in created_questions:
            question.delete()
        print(f"✅ Deleted {len(created_questions)} test questions")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")


if __name__ == "__main__":
    test_fabric_question_creation()
