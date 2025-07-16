#!/usr/bin/env python
"""
Fabric Database Performance Test

This script specifically tests Microsoft Fabric SQL performance by forcing
the USE_LOCAL_DB setting to False.
"""

import os
import sys
import django
import time
from datetime import datetime

# Force Fabric database usage
os.environ['USE_LOCAL_DB'] = 'false'

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from api.models import User, Event, Question


def test_fabric_performance():
    """Test Microsoft Fabric database performance"""
    
    print("☁️ Microsoft Fabric Performance Test")
    print("=" * 60)
    
    # Verify we're using Fabric
    from django.conf import settings
    db_config = settings.DATABASES['default']
    
    print(f"🔍 Database Configuration:")
    print(f"   Host: {db_config.get('HOST', 'N/A')}")
    print(f"   Database: {db_config.get('NAME', 'N/A')}")
    print(f"   USE_LOCAL_DB: {os.getenv('USE_LOCAL_DB', 'not set')}")
    print()
    
    # Test database connection
    print("🔌 Testing Fabric connection...")
    connection_times = []
    
    for i in range(5):
        start_time = time.perf_counter()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DB_NAME(), @@VERSION")
                result = cursor.fetchone()
                db_name = result[0]
                if i == 0:  # Only show version once
                    db_version = result[1][:100] + "..." if len(result[1]) > 100 else result[1]
                    print(f"✅ Connected to: {db_name}")
                    print(f"🔧 Version: {db_version}")
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            connection_times.append(duration_ms)
            print(f"  Connection test {i+1}: {duration_ms:.2f} ms")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return
    
    avg_connection = sum(connection_times) / len(connection_times)
    print(f"  📊 Average connection latency: {avg_connection:.2f} ms\n")
    
    # Test Question creation (reuse existing test users/events if available)
    print("🏗️ Testing Question Creation...")
    print("-" * 40)
    
    try:
        # Get or create test user
        user, _ = User.objects.get_or_create(
            email="fabric_test@example.com",
            defaults={
                'name': 'Fabric Test User',
                'username': 'fabric_test',
                'role': 'user'
            }
        )
        
        # Get or create test event  
        event, _ = Event.objects.get_or_create(
            name="Fabric Performance Test Event",
            defaults={
                'created_by': user,
                'is_active': True,
                'is_public': True
            }
        )
        
        # Test question creation
        creation_times = []
        created_questions = []
        
        for i in range(10):
            start_time = time.perf_counter()
            
            question = Question.objects.create(
                text=f"Fabric test question {i+1} - {datetime.now().isoformat()}",
                event=event,
                author=user,
                is_anonymous=False
            )
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            creation_times.append(duration_ms)
            created_questions.append(question)
            
            print(f"  Question {i+1}: {duration_ms:.2f} ms")
        
        # Calculate stats
        avg_create = sum(creation_times) / len(creation_times)
        min_create = min(creation_times)
        max_create = max(creation_times)
        
        print(f"\n📊 FABRIC PERFORMANCE RESULTS:")
        print("=" * 50)
        print(f"Connection Latency:")
        print(f"  Average: {avg_connection:.2f} ms")
        print(f"  Range: {min(connection_times):.2f} - {max(connection_times):.2f} ms")
        print()
        print(f"Question Creation:")
        print(f"  Average: {avg_create:.2f} ms")
        print(f"  Fastest: {min_create:.2f} ms")
        print(f"  Slowest: {max_create:.2f} ms")
        print(f"  Total questions: {len(creation_times)}")
        
        # Clean up
        print(f"\n🧹 Cleaning up...")
        for question in created_questions:
            question.delete()
        print(f"✅ Deleted {len(created_questions)} test questions")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fabric_performance_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Microsoft Fabric Performance Test\n")
            f.write(f"================================\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Database: {db_name}\n\n")
            f.write(f"Connection Latency (5 tests):\n")
            for i, time_ms in enumerate(connection_times, 1):
                f.write(f"  Test {i}: {time_ms:.2f} ms\n")
            f.write(f"  Average: {avg_connection:.2f} ms\n\n")
            f.write(f"Question Creation (10 tests):\n")
            for i, time_ms in enumerate(creation_times, 1):
                f.write(f"  Test {i}: {time_ms:.2f} ms\n")
            f.write(f"  Average: {avg_create:.2f} ms\n")
            f.write(f"  Fastest: {min_create:.2f} ms\n")
            f.write(f"  Slowest: {max_create:.2f} ms\n")
        
        print(f"📝 Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Question creation test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fabric_performance()
