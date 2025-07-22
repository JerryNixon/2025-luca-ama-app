#!/usr/bin/env python
"""
Azure SQL Comprehensive Performance Report
==========================================
Final performance test matching your Fabric report format with correct schema.
"""

import os
import sys
import time
from statistics import mean, median

# Add Django project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

# Configure Django
import django
django.setup()

from django.db import connection

def print_header():
    """Print formatted header matching Fabric report"""
    print("☁️ AZURE SQL DATABASE PERFORMANCE REPORT")
    print("=" * 70)
    print("🔵 Platform: Azure SQL Database (Serverless)")
    print("🏢 Server: luca-azure-ama.database.windows.net")
    print("📊 Database: luca_azure_ama")
    print("🌍 Connection: Encrypted SSL/TLS with Azure AD Auth")
    print("⚡ Test Type: Django ORM Performance Benchmark")
    print()

def test_database_info():
    """Get database information"""
    print("🔗 DATABASE CONFIGURATION")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # Get version
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        version_line = version.split('\n')[0].strip()
        print(f"Version: {version_line}")
        
        # Get current time and timezone
        cursor.execute("SELECT SYSDATETIME(), CURRENT_TIMEZONE()")
        dt_info = cursor.fetchone()
        print(f"Server Time: {dt_info[0]}")
        print(f"Timezone: {dt_info[1]}")
        
        # Get database name and collation
        cursor.execute("SELECT DB_NAME(), DATABASEPROPERTYEX(DB_NAME(), 'Collation')")
        db_info = cursor.fetchone()
        print(f"Database: {db_info[0]}")
        print(f"Collation: {db_info[1]}")
    
    print()

def test_connection_performance():
    """Test connection latency performance"""
    print("🔌 CONNECTION PERFORMANCE")
    print("-" * 40)
    
    times = []
    for i in range(10):  # More tests for better accuracy
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        times.append(latency_ms)
    
    avg_latency = mean(times)
    min_latency = min(times)
    max_latency = max(times)
    median_latency = median(times)
    
    print(f"📊 Connection Latency (10 tests):")
    print(f"   Average: {avg_latency:.2f} ms")
    print(f"   Median:  {median_latency:.2f} ms")
    print(f"   Range:   {min_latency:.2f} - {max_latency:.2f} ms")
    print()
    
    return times

def test_data_operations():
    """Test data retrieval operations"""
    print("📊 DATA OPERATIONS PERFORMANCE")
    print("-" * 40)
    
    results = {}
    
    # Test 1: User operations
    print("👥 User Operations:")
    
    # Count users
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_user")
        user_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    user_count_time = (end_time - start_time) * 1000
    results['user_count'] = user_count_time
    print(f"   Count users: {user_count_time:.2f} ms ({user_count} total)")
    
    # Find superuser
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 id, username FROM api_user WHERE is_superuser = 1")
        superuser = cursor.fetchone()
    end_time = time.perf_counter()
    superuser_time = (end_time - start_time) * 1000
    results['find_superuser'] = superuser_time
    print(f"   Find superuser: {superuser_time:.2f} ms")
    
    # Get user details
    if superuser:
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, email, name FROM api_user WHERE id = %s", [superuser[0]])
            user_details = cursor.fetchone()
        end_time = time.perf_counter()
        user_detail_time = (end_time - start_time) * 1000
        results['user_details'] = user_detail_time
        print(f"   Get user details: {user_detail_time:.2f} ms")
    
    print()
    
    # Test 2: Event operations
    print("📅 Event Operations:")
    
    # Count events
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_event")
        event_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    event_count_time = (end_time - start_time) * 1000
    results['event_count'] = event_count_time
    print(f"   Count events: {event_count_time:.2f} ms ({event_count} total)")
    
    # Get active events
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_event WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    active_time = (end_time - start_time) * 1000
    results['active_events'] = active_time
    print(f"   Active events: {active_time:.2f} ms ({active_count} active)")
    
    # Get recent events
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 10 id, name, created_at FROM api_event ORDER BY created_at DESC")
        recent_events = cursor.fetchall()
    end_time = time.perf_counter()
    recent_time = (end_time - start_time) * 1000
    results['recent_events'] = recent_time
    print(f"   Recent events: {recent_time:.2f} ms ({len(recent_events)} found)")
    
    print()
    
    # Test 3: Question operations
    print("❓ Question Operations:")
    
    # Count questions
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_question")
        question_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    question_count_time = (end_time - start_time) * 1000
    results['question_count'] = question_count_time
    print(f"   Count questions: {question_count_time:.2f} ms ({question_count} total)")
    
    # Get answered questions
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_question WHERE is_answered = 1")
        answered_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    answered_time = (end_time - start_time) * 1000
    results['answered_questions'] = answered_time
    print(f"   Answered questions: {answered_time:.2f} ms ({answered_count} answered)")
    
    # Get starred questions
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_question WHERE is_starred = 1")
        starred_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    starred_time = (end_time - start_time) * 1000
    results['starred_questions'] = starred_time
    print(f"   Starred questions: {starred_time:.2f} ms ({starred_count} starred)")
    
    print()
    
    # Test 4: Vote operations
    print("🗳️ Vote Operations:")
    
    # Count votes
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_vote")
        vote_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    vote_count_time = (end_time - start_time) * 1000
    results['vote_count'] = vote_count_time
    print(f"   Count votes: {vote_count_time:.2f} ms ({vote_count} total)")
    
    print()
    
    return results

def test_complex_queries():
    """Test complex multi-table queries"""
    print("🔄 COMPLEX QUERY PERFORMANCE")
    print("-" * 40)
    
    results = {}
    
    # Test 1: Questions with vote counts
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
    
    questions_votes_time = (end_time - start_time) * 1000
    results['questions_with_votes'] = questions_votes_time
    print(f"Questions with votes: {questions_votes_time:.2f} ms ({len(questions_with_votes)} questions)")
    
    # Test 2: Event participation summary
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.name, COUNT(ep.user_id) as participant_count
            FROM api_event e
            LEFT JOIN api_event_participants ep ON e.id = ep.event_id
            GROUP BY e.id, e.name
            ORDER BY participant_count DESC
        """)
        event_participation = cursor.fetchall()
    end_time = time.perf_counter()
    
    participation_time = (end_time - start_time) * 1000
    results['event_participation'] = participation_time
    print(f"Event participation: {participation_time:.2f} ms ({len(event_participation)} events)")
    
    # Test 3: User activity aggregation
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.username,
                   COUNT(DISTINCT q.id) as questions_asked,
                   COUNT(DISTINCT v.id) as votes_cast
            FROM api_user u
            LEFT JOIN api_question q ON u.id = q.author_id
            LEFT JOIN api_vote v ON u.id = v.user_id
            GROUP BY u.id, u.username
            HAVING COUNT(DISTINCT q.id) > 0 OR COUNT(DISTINCT v.id) > 0
        """)
        user_activity = cursor.fetchall()
    end_time = time.perf_counter()
    
    activity_time = (end_time - start_time) * 1000
    results['user_activity'] = activity_time
    print(f"User activity summary: {activity_time:.2f} ms ({len(user_activity)} active users)")
    
    print()
    return results

def print_performance_summary(connection_times, data_results, complex_results):
    """Print comprehensive performance summary"""
    print("📊 COMPREHENSIVE PERFORMANCE SUMMARY")
    print("=" * 70)
    
    # Connection statistics
    avg_connection = mean(connection_times)
    min_connection = min(connection_times)
    max_connection = max(connection_times)
    median_connection = median(connection_times)
    
    print("🔌 Connection Performance:")
    print(f"   Average Latency: {avg_connection:.2f} ms")
    print(f"   Median Latency:  {median_connection:.2f} ms")
    print(f"   Best Case:       {min_connection:.2f} ms")
    print(f"   Worst Case:      {max_connection:.2f} ms")
    print()
    
    # Data operation statistics
    print("📊 Data Operation Performance:")
    all_data_times = list(data_results.values())
    if all_data_times:
        avg_data = mean(all_data_times)
        min_data = min(all_data_times)
        max_data = max(all_data_times)
        median_data = median(all_data_times)
        
        print(f"   Average Query Time: {avg_data:.2f} ms")
        print(f"   Median Query Time:  {median_data:.2f} ms")
        print(f"   Fastest Query:      {min_data:.2f} ms")
        print(f"   Slowest Query:      {max_data:.2f} ms")
    print()
    
    # Complex query statistics
    print("🔄 Complex Query Performance:")
    all_complex_times = list(complex_results.values())
    if all_complex_times:
        avg_complex = mean(all_complex_times)
        min_complex = min(all_complex_times)
        max_complex = max(all_complex_times)
        
        print(f"   Average Complex Query: {avg_complex:.2f} ms")
        print(f"   Fastest Complex Query: {min_complex:.2f} ms")
        print(f"   Slowest Complex Query: {max_complex:.2f} ms")
    print()
    
    # Overall performance metrics
    all_times = connection_times + all_data_times + all_complex_times
    if all_times:
        overall_avg = mean(all_times)
        overall_median = median(all_times)
        overall_min = min(all_times)
        overall_max = max(all_times)
        
        print("⚡ Overall Performance Metrics:")
        print(f"   Overall Average:    {overall_avg:.2f} ms")
        print(f"   Overall Median:     {overall_median:.2f} ms")
        print(f"   Performance Range:  {overall_min:.2f} - {overall_max:.2f} ms")
        print()
    
    # Performance classification
    if avg_connection < 50:
        connection_grade = "Excellent"
    elif avg_connection < 100:
        connection_grade = "Good"
    elif avg_connection < 200:
        connection_grade = "Fair"
    else:
        connection_grade = "Poor"
    
    print("🎯 Performance Classification:")
    print(f"   Connection Grade: {connection_grade}")
    print(f"   Avg Response Time: {avg_connection:.2f} ms")
    print()
    
    print("✅ AZURE SQL DATABASE PERFORMANCE ANALYSIS COMPLETE")
    print("=" * 70)

def main():
    """Run comprehensive Azure SQL performance analysis"""
    print_header()
    
    try:
        # Database info
        test_database_info()
        
        # Run performance tests
        connection_times = test_connection_performance()
        data_results = test_data_operations()
        complex_results = test_complex_queries()
        
        # Print comprehensive summary
        print_performance_summary(connection_times, data_results, complex_results)
        
    except Exception as e:
        print(f"❌ Error during performance testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
