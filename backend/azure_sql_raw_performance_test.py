#!/usr/bin/env python
"""
Azure SQL Performance Test - Raw SQL Version
============================================
This script uses raw SQL to avoid Django ORM schema issues and provide
a direct comparison with your Fabric SQL performance test.
"""

import os
import sys
import time
import pyodbc
from statistics import mean, median

# Add Django project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

# Configure Django
import django
django.setup()

from django.db import connection

def print_header():
    """Print formatted test header matching Fabric test format"""
    print("☁️ COMPREHENSIVE AZURE SQL DATABASE PERFORMANCE TEST")
    print("=" * 70)
    print("🔵 Using Azure SQL Database (Serverless) Configuration")
    print("📍 Database: Azure SQL Database")
    print("🏢 Server: Azure SQL (Serverless)")
    print("⚡ Performance: Testing against Fabric SQL")
    print("🌍 Connection: Encrypted (SSL/TLS)")
    print()

def test_connection_info():
    """Test database connection and get info"""
    print("🔗 DATABASE CONNECTION INFO")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # Get database name
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]
        print(f"📊 Database: {db_name}")
        
        # Get version
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"🔧 Version: {version[:80]}...")
        
        # Get current time
        cursor.execute("SELECT SYSDATETIME()")
        current_time = cursor.fetchone()[0]
        print(f"🕒 Current Time: {current_time}")
        print()

def test_connection_latency():
    """Test basic connection latency"""
    print("🔌 TEST 1: CONNECTION LATENCY")
    print("-" * 40)
    
    times = []
    for i in range(5):
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        times.append(latency_ms)
        print(f"  Connection test {i+1}: {latency_ms:.2f} ms")
    
    avg_latency = mean(times)
    print(f"  📊 Average: {avg_latency:.2f} ms")
    print()
    return times

def test_user_operations():
    """Test user table operations with raw SQL"""
    print("👥 TEST 2: USER OPERATIONS")
    print("-" * 40)
    
    results = {}
    
    # Test 1: Count users
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_user")
        user_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    
    count_time = (end_time - start_time) * 1000
    results['count_users'] = count_time
    print(f"  User count query: {count_time:.2f} ms ({user_count} users)")
    
    # Test 2: Find superuser
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 id, username FROM api_user WHERE is_superuser = 1")
        superuser = cursor.fetchone()
    end_time = time.perf_counter()
    
    superuser_time = (end_time - start_time) * 1000
    results['find_superuser'] = superuser_time
    if superuser:
        print(f"  Find superuser: {superuser_time:.2f} ms (found: {superuser[1]})")
    else:
        print(f"  Find superuser: {superuser_time:.2f} ms (no superuser found)")
    
    # Test 3: Get user by ID (if superuser exists)
    if superuser:
        user_id = superuser[0]
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, email FROM api_user WHERE id = %s", [user_id])
            user_details = cursor.fetchone()
        end_time = time.perf_counter()
        
        get_user_time = (end_time - start_time) * 1000
        results['get_user_by_id'] = get_user_time
        print(f"  Get user by ID: {get_user_time:.2f} ms")
    
    print()
    return results

def test_event_operations():
    """Test event table operations"""
    print("📅 TEST 3: EVENT OPERATIONS")
    print("-" * 40)
    
    results = {}
    
    # Test 1: Count events
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_event")
        event_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    
    count_time = (end_time - start_time) * 1000
    results['count_events'] = count_time
    print(f"  Event count query: {count_time:.2f} ms ({event_count} events)")
    
    # Test 2: Get recent events
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TOP 10 id, title, created_at 
            FROM api_event 
            ORDER BY created_at DESC
        """)
        recent_events = cursor.fetchall()
    end_time = time.perf_counter()
    
    recent_time = (end_time - start_time) * 1000
    results['get_recent_events'] = recent_time
    print(f"  Get recent events: {recent_time:.2f} ms ({len(recent_events)} found)")
    
    # Test 3: Get active events
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_event WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    
    active_time = (end_time - start_time) * 1000
    results['get_active_events'] = active_time
    print(f"  Get active events: {active_time:.2f} ms ({active_count} active)")
    
    print()
    return results

def test_question_operations():
    """Test question table operations"""
    print("❓ TEST 4: QUESTION OPERATIONS")
    print("-" * 40)
    
    results = {}
    
    # Test 1: Count questions
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_question")
        question_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    
    count_time = (end_time - start_time) * 1000
    results['count_questions'] = count_time
    print(f"  Question count query: {count_time:.2f} ms ({question_count} questions)")
    
    # Test 2: Get questions with votes
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT q.id, q.text, COUNT(v.id) as vote_count
            FROM api_question q
            LEFT JOIN api_vote v ON q.id = v.question_id
            GROUP BY q.id, q.text
            ORDER BY vote_count DESC
        """)
        questions_with_votes = cursor.fetchall()
    end_time = time.perf_counter()
    
    vote_query_time = (end_time - start_time) * 1000
    results['questions_with_votes'] = vote_query_time
    print(f"  Questions with votes: {vote_query_time:.2f} ms ({len(questions_with_votes)} found)")
    
    # Test 3: Get recent questions
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TOP 5 id, text, created_at 
            FROM api_question 
            ORDER BY created_at DESC
        """)
        recent_questions = cursor.fetchall()
    end_time = time.perf_counter()
    
    recent_time = (end_time - start_time) * 1000
    results['get_recent_questions'] = recent_time
    print(f"  Get recent questions: {recent_time:.2f} ms ({len(recent_questions)} found)")
    
    print()
    return results

def test_complex_operations():
    """Test complex multi-table operations"""
    print("🔄 TEST 5: COMPLEX OPERATIONS")
    print("-" * 40)
    
    results = {}
    
    # Test 1: Event with question count
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.title, COUNT(q.id) as question_count
            FROM api_event e
            LEFT JOIN api_question q ON e.id = q.event_id
            GROUP BY e.id, e.title
            ORDER BY question_count DESC
        """)
        events_with_questions = cursor.fetchall()
    end_time = time.perf_counter()
    
    event_question_time = (end_time - start_time) * 1000
    results['events_with_questions'] = event_question_time
    print(f"  Events with questions: {event_question_time:.2f} ms ({len(events_with_questions)} found)")
    
    # Test 2: User activity summary
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.username, 
                   COUNT(DISTINCT e.id) as events_created,
                   COUNT(DISTINCT q.id) as questions_asked,
                   COUNT(DISTINCT v.id) as votes_cast
            FROM api_user u
            LEFT JOIN api_event e ON u.id = e.host_id
            LEFT JOIN api_question q ON u.id = q.author_id
            LEFT JOIN api_vote v ON u.id = v.user_id
            GROUP BY u.id, u.username
            HAVING COUNT(DISTINCT e.id) > 0 OR COUNT(DISTINCT q.id) > 0 OR COUNT(DISTINCT v.id) > 0
        """)
        user_activity = cursor.fetchall()
    end_time = time.perf_counter()
    
    activity_time = (end_time - start_time) * 1000
    results['user_activity'] = activity_time
    print(f"  User activity summary: {activity_time:.2f} ms ({len(user_activity)} active users)")
    
    print()
    return results

def print_summary(connection_times, user_results, event_results, question_results, complex_results):
    """Print formatted summary matching Fabric test format"""
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 70)
    
    # Connection stats
    avg_connection = mean(connection_times)
    min_connection = min(connection_times)
    max_connection = max(connection_times)
    
    print(f"🔌 Connection Latency:")
    print(f"   Average: {avg_connection:.2f} ms")
    print(f"   Range: {min_connection:.2f} - {max_connection:.2f} ms")
    print()
    
    # Operation stats
    all_times = []
    
    print(f"👥 User Operations:")
    for op, time_ms in user_results.items():
        print(f"   {op.replace('_', ' ').title()}: {time_ms:.2f} ms")
        all_times.append(time_ms)
    print()
    
    print(f"📅 Event Operations:")
    for op, time_ms in event_results.items():
        print(f"   {op.replace('_', ' ').title()}: {time_ms:.2f} ms")
        all_times.append(time_ms)
    print()
    
    print(f"❓ Question Operations:")
    for op, time_ms in question_results.items():
        print(f"   {op.replace('_', ' ').title()}: {time_ms:.2f} ms")
        all_times.append(time_ms)
    print()
    
    print(f"🔄 Complex Operations:")
    for op, time_ms in complex_results.items():
        print(f"   {op.replace('_', ' ').title()}: {time_ms:.2f} ms")
        all_times.append(time_ms)
    print()
    
    # Overall stats
    if all_times:
        avg_operation = mean(all_times)
        median_operation = median(all_times)
        min_operation = min(all_times)
        max_operation = max(all_times)
        
        print(f"📈 Overall Operation Performance:")
        print(f"   Average: {avg_operation:.2f} ms")
        print(f"   Median: {median_operation:.2f} ms")
        print(f"   Range: {min_operation:.2f} - {max_operation:.2f} ms")
        print()
    
    print("✅ AZURE SQL DATABASE PERFORMANCE TEST COMPLETE")
    print("=" * 70)

def main():
    """Run comprehensive Azure SQL performance test"""
    print_header()
    
    try:
        # Test database connection
        test_connection_info()
        
        # Run performance tests
        connection_times = test_connection_latency()
        user_results = test_user_operations()
        event_results = test_event_operations()
        question_results = test_question_operations()
        complex_results = test_complex_operations()
        
        # Print summary
        print_summary(connection_times, user_results, event_results, question_results, complex_results)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
