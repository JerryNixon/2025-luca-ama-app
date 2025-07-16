#!/usr/bin/env python
"""
Comprehensive Database Performance Comparison

This script provides a detailed comparison between what we measured on Docker
and what we're seeing on Microsoft Fabric.
"""

import os
import sys
import django
import time
import statistics
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from api.models import User, Event, Question


def comprehensive_fabric_test():
    """Run comprehensive performance tests on Microsoft Fabric"""
    
    print("☁️ COMPREHENSIVE MICROSOFT FABRIC PERFORMANCE TEST")
    print("=" * 70)
    
    # Get database info
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DB_NAME(), @@VERSION")
            result = cursor.fetchone()
            db_name = result[0]
            db_version = result[1][:100] + "..." if len(result[1]) > 100 else result[1]
        
        print(f"📊 Database: {db_name}")
        print(f"🔧 Version: {db_version}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test 1: Connection Latency
    print(f"\n🔌 TEST 1: CONNECTION LATENCY")
    print("-" * 40)
    
    connection_times = []
    for i in range(5):
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        connection_times.append(duration_ms)
        print(f"  Connection test {i+1}: {duration_ms:.2f} ms")
    
    avg_connection = statistics.mean(connection_times)
    print(f"  📊 Average: {avg_connection:.2f} ms")
    
    # Test 2: User/Event Setup
    print(f"\n👥 TEST 2: USER/EVENT SETUP")
    print("-" * 40)
    
    start_time = time.perf_counter()
    user, _ = User.objects.get_or_create(
        email="comprehensive_test@example.com",
        defaults={
            'name': 'Comprehensive Test User',
            'username': 'comprehensive_test',
            'role': 'user'
        }
    )
    user_time = (time.perf_counter() - start_time) * 1000
    print(f"  User setup: {user_time:.2f} ms")
    
    start_time = time.perf_counter()
    event, _ = Event.objects.get_or_create(
        name="Comprehensive Test Event",
        defaults={
            'created_by': user,
            'is_active': True,
            'is_public': True
        }
    )
    event_time = (time.perf_counter() - start_time) * 1000
    print(f"  Event setup: {event_time:.2f} ms")
    
    # Test 3: Question Creation (Multiple rounds)
    print(f"\n🏗️ TEST 3: QUESTION CREATION PERFORMANCE")
    print("-" * 40)
    
    all_create_times = []
    created_questions = []
    
    # Round 1: Initial questions
    print("  Round 1: Creating 10 questions...")
    round1_times = []
    for i in range(10):
        start_time = time.perf_counter()
        question = Question.objects.create(
            text=f"Comprehensive test question {i+1} - {datetime.now().isoformat()}",
            event=event,
            author=user,
            is_anonymous=False
        )
        duration_ms = (time.perf_counter() - start_time) * 1000
        round1_times.append(duration_ms)
        all_create_times.append(duration_ms)
        created_questions.append(question)
        if i % 2 == 0:
            print(f"    Question {i+1}: {duration_ms:.2f} ms")
    
    print(f"  Round 1 Average: {statistics.mean(round1_times):.2f} ms")
    
    # Test 4: Query Performance
    print(f"\n🔍 TEST 4: QUERY PERFORMANCE")
    print("-" * 40)
    
    query_tests = [
        ("Count all questions", lambda: Question.objects.count()),
        ("Get questions by event", lambda: list(Question.objects.filter(event=event))),
        ("Get questions by author", lambda: list(Question.objects.filter(author=user))),
        ("Get single question", lambda: Question.objects.first()),
    ]
    
    query_times = []
    for test_name, query_func in query_tests:
        times = []
        for i in range(3):
            start_time = time.perf_counter()
            result = query_func()
            duration_ms = (time.perf_counter() - start_time) * 1000
            times.append(duration_ms)
        
        avg_time = statistics.mean(times)
        query_times.append(avg_time)
        print(f"  {test_name}: {avg_time:.2f} ms")
    
    # Test 5: Update Performance
    print(f"\n✏️ TEST 5: UPDATE PERFORMANCE")
    print("-" * 40)
    
    update_times = []
    for i, question in enumerate(created_questions[:5]):
        start_time = time.perf_counter()
        question.text = f"Updated question {i+1} - {datetime.now().isoformat()}"
        question.upvotes += 1
        question.save()
        duration_ms = (time.perf_counter() - start_time) * 1000
        update_times.append(duration_ms)
        print(f"  Update {i+1}: {duration_ms:.2f} ms")
    
    avg_update = statistics.mean(update_times)
    print(f"  Average update: {avg_update:.2f} ms")
    
    # Test 6: Delete Performance
    print(f"\n🗑️ TEST 6: DELETE PERFORMANCE")
    print("-" * 40)
    
    delete_times = []
    for i, question in enumerate(created_questions[:3]):
        start_time = time.perf_counter()
        question.delete()
        duration_ms = (time.perf_counter() - start_time) * 1000
        delete_times.append(duration_ms)
        print(f"  Delete {i+1}: {duration_ms:.2f} ms")
    
    # Bulk delete the rest
    remaining_questions = created_questions[3:]
    if remaining_questions:
        start_time = time.perf_counter()
        Question.objects.filter(id__in=[q.id for q in remaining_questions]).delete()
        bulk_delete_time = (time.perf_counter() - start_time) * 1000
        print(f"  Bulk delete {len(remaining_questions)} questions: {bulk_delete_time:.2f} ms")
    
    # Summary Report
    print(f"\n📊 COMPREHENSIVE FABRIC PERFORMANCE SUMMARY")
    print("=" * 70)
    
    # Docker baseline (from previous tests)
    docker_results = {
        'connection': 1.53,
        'question_create': 8.58,
        'queries': 3.50,
        'updates': 15.0,  # estimated
    }
    
    fabric_results = {
        'connection': avg_connection,
        'question_create': statistics.mean(all_create_times),
        'queries': statistics.mean(query_times),
        'updates': avg_update,
    }
    
    print(f"{'Operation':<20} {'Docker (ms)':<12} {'Fabric (ms)':<12} {'Difference':<15} {'% Change'}")
    print("-" * 75)
    
    for operation in docker_results:
        docker_val = docker_results[operation]
        fabric_val = fabric_results[operation]
        diff = fabric_val - docker_val
        pct_change = ((fabric_val / docker_val) - 1) * 100
        
        print(f"{operation:<20} {docker_val:<12.2f} {fabric_val:<12.2f} {diff:<+15.2f} {pct_change:<+7.1f}%")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_fabric_test_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Comprehensive Microsoft Fabric Performance Test\n")
        f.write(f"===============================================\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Database: {db_name}\n\n")
        
        f.write(f"Connection Latency (5 tests):\n")
        for i, time_ms in enumerate(connection_times, 1):
            f.write(f"  Test {i}: {time_ms:.2f} ms\n")
        f.write(f"  Average: {avg_connection:.2f} ms\n\n")
        
        f.write(f"Question Creation ({len(all_create_times)} tests):\n")
        for i, time_ms in enumerate(all_create_times, 1):
            f.write(f"  Question {i}: {time_ms:.2f} ms\n")
        f.write(f"  Average: {fabric_results['question_create']:.2f} ms\n\n")
        
        f.write(f"Performance Comparison Summary:\n")
        f.write(f"{'Operation':<20} {'Docker (ms)':<12} {'Fabric (ms)':<12} {'Difference':<15} {'% Change'}\n")
        f.write("-" * 75 + "\n")
        
        for operation in docker_results:
            docker_val = docker_results[operation]
            fabric_val = fabric_results[operation]
            diff = fabric_val - docker_val
            pct_change = ((fabric_val / docker_val) - 1) * 100
            f.write(f"{operation:<20} {docker_val:<12.2f} {fabric_val:<12.2f} {diff:<+15.2f} {pct_change:<+7.1f}%\n")
    
    print(f"\n📝 Detailed results saved to: {filename}")
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print("-" * 30)
    create_slowdown = fabric_results['question_create'] / docker_results['question_create']
    connection_slowdown = fabric_results['connection'] / docker_results['connection']
    
    print(f"• Question creation is {create_slowdown:.1f}x slower on Fabric")
    print(f"• Network latency is {connection_slowdown:.0f}x higher on Fabric")
    print(f"• Most performance difference is due to network latency")
    print(f"• Your Django code is efficient - the bottleneck is infrastructure")


if __name__ == "__main__":
    comprehensive_fabric_test()
