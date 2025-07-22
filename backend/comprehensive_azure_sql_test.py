#!/usr/bin/env python3
"""
Comprehensive Azure SQL Performance Test
Matching the exact format of the Fabric test for direct comparison
"""
import os
import sys
import django
import time
import statistics
import uuid
from datetime import datetime, timezone

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question
from django.db import connection

def get_database_info():
    """Get Azure SQL database information"""
    cursor = connection.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    
    cursor.execute("SELECT DB_NAME()")
    db_name = cursor.fetchone()[0]
    
    return {
        'version': version,
        'database': db_name,
        'server': connection.settings_dict.get('HOST', 'unknown')
    }

def test_connection_latency():
    """Test 1: Connection Latency - Raw database connection time (SELECT 1)"""
    print("🔌 TEST 1: CONNECTION LATENCY")
    print("-" * 40)
    
    latencies = []
    for i in range(5):
        # High-precision timing using Python's perf_counter()
        start_time = time.perf_counter()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        latencies.append(duration_ms)
        print(f"  Connection test {i+1}: {duration_ms:.2f} ms")
    
    avg_latency = statistics.mean(latencies)
    print(f"  📊 Average: {avg_latency:.2f} ms")
    print()
    
    return {
        'latencies': latencies,
        'average': avg_latency
    }

def test_user_event_setup():
    """Test 2: User/Event Setup Performance"""
    print("👥 TEST 2: USER/EVENT SETUP")
    print("-" * 40)
    
    # User setup
    start_time = time.perf_counter()
    try:
        # Try to get existing admin user first
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # Create new user if none exists
            user = User.objects.create(
                id=str(uuid.uuid4()).replace('-', ''),
                email='azure_test@example.com',
                name='Azure Test User',
                role='admin',
                is_active=True,
                is_superuser=True,
                is_anonymous=False,
                date_joined=datetime.now(timezone.utc)
            )
    except Exception:
        # Fallback: use raw SQL to get existing user
        cursor = connection.cursor()
        cursor.execute("SELECT TOP 1 id FROM api_user WHERE is_superuser = 1")
        result = cursor.fetchone()
        if result:
            user = User.objects.get(id=result[0])
        else:
            raise Exception("No admin user available")
    
    user_setup_ms = (time.perf_counter() - start_time) * 1000
    print(f"  User setup: {user_setup_ms:.2f} ms")
    
    # Event setup
    start_time = time.perf_counter()
    try:
        event = Event.objects.filter(name='Azure Comprehensive Test Event').first()
        if not event:
            event = Event.objects.create(
                id=str(uuid.uuid4()).replace('-', ''),
                name='Azure Comprehensive Test Event',
                created_by=user,
                is_active=True,
                is_public=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
    except Exception:
        # Fallback: use raw SQL
        cursor = connection.cursor()
        cursor.execute("SELECT TOP 1 id FROM api_event WHERE name LIKE '%Test%'")
        result = cursor.fetchone()
        if result:
            event = Event.objects.get(id=result[0])
        else:
            # Create with raw SQL
            event_id = str(uuid.uuid4()).replace('-', '')
            now = datetime.now(timezone.utc)
            cursor.execute("""
                INSERT INTO api_event (id, name, created_by_id, is_active, is_public, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [event_id, 'Azure Comprehensive Test Event', user.id, 1, 1, now, now])
            event = Event.objects.get(id=event_id)
    
    event_setup_ms = (time.perf_counter() - start_time) * 1000
    print(f"  Event setup: {event_setup_ms:.2f} ms")
    print()
    
    return user, event, {
        'user_setup': user_setup_ms,
        'event_setup': event_setup_ms
    }

def test_question_creation(user, event):
    """Test 3: Question Creation Performance - Full Django ORM create operation"""
    print("🏗️ TEST 3: QUESTION CREATION PERFORMANCE")
    print("-" * 40)
    
    all_latencies = []
    question_ids = []
    
    print("  Round 1: Creating 10 questions...")
    
    for i in range(10):
        # High-precision timing using Python's perf_counter()
        start_time = time.perf_counter()
        
        question = Question.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            text=f"Azure Test Question {i+1} - Comprehensive Performance Test",
            author=user,
            event=event,
            is_anonymous=False,
            upvotes=i,
            is_answered=i % 3 == 0,
            is_starred=i % 5 == 0,
            is_staged=False,
            tags='["azure", "performance", "test"]',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        all_latencies.append(duration_ms)
        question_ids.append(question.id)
        
        # Print only odd-numbered questions to match format
        if i % 2 == 0:
            print(f"    Question {i+1}: {duration_ms:.2f} ms")
    
    round1_avg = statistics.mean(all_latencies)
    print(f"  Round 1 Average: {round1_avg:.2f} ms")
    print()
    
    return question_ids, {
        'latencies': all_latencies,
        'average': round1_avg,
        'min': min(all_latencies),
        'max': max(all_latencies)
    }

def test_query_performance(event, user):
    """Test 4: Query Performance - Various SELECT operations"""
    print("🔍 TEST 4: QUERY PERFORMANCE")
    print("-" * 40)
    
    results = {}
    
    # Count all questions
    start_time = time.perf_counter()
    Question.objects.count()
    count_ms = (time.perf_counter() - start_time) * 1000
    print(f"  Count all questions: {count_ms:.2f} ms")
    results['count'] = count_ms
    
    # Get questions by event
    start_time = time.perf_counter()
    list(Question.objects.filter(event=event))
    event_filter_ms = (time.perf_counter() - start_time) * 1000
    print(f"  Get questions by event: {event_filter_ms:.2f} ms")
    results['event_filter'] = event_filter_ms
    
    # Get questions by author
    start_time = time.perf_counter()
    list(Question.objects.filter(author=user))
    author_filter_ms = (time.perf_counter() - start_time) * 1000
    print(f"  Get questions by author: {author_filter_ms:.2f} ms")
    results['author_filter'] = author_filter_ms
    
    # Get single question
    question = Question.objects.filter(event=event).first()
    if question:
        start_time = time.perf_counter()
        Question.objects.get(id=question.id)
        single_ms = (time.perf_counter() - start_time) * 1000
        print(f"  Get single question: {single_ms:.2f} ms")
        results['single'] = single_ms
    
    print()
    return results

def test_update_performance(question_ids):
    """Test 5: Update Performance - Model field changes and saves"""
    print("✏️ TEST 5: UPDATE PERFORMANCE")
    print("-" * 40)
    
    update_latencies = []
    
    # Test 5 updates
    for i in range(min(5, len(question_ids))):
        question = Question.objects.get(id=question_ids[i])
        
        # High-precision timing using Python's perf_counter()
        start_time = time.perf_counter()
        
        question.text = f"Updated Azure Test Question {i+1} - Performance Update"
        question.upvotes = i + 100
        question.is_starred = True
        question.updated_at = datetime.now(timezone.utc)
        question.save()
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        update_latencies.append(duration_ms)
        print(f"  Update {i+1}: {duration_ms:.2f} ms")
    
    avg_update = statistics.mean(update_latencies)
    print(f"  Average update: {avg_update:.2f} ms")
    print()
    
    return {
        'latencies': update_latencies,
        'average': avg_update
    }

def test_delete_performance(question_ids):
    """Test 6: Delete Performance - Individual and bulk deletions"""
    print("🗑️ TEST 6: DELETE PERFORMANCE")
    print("-" * 40)
    
    delete_latencies = []
    deleted_count = 0
    
    # Individual deletes (first 3)
    for i in range(min(3, len(question_ids))):
        question_id = question_ids[i]
        
        # High-precision timing using Python's perf_counter()
        start_time = time.perf_counter()
        Question.objects.filter(id=question_id).delete()
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        delete_latencies.append(duration_ms)
        deleted_count += 1
        print(f"  Delete {i+1}: {duration_ms:.2f} ms")
    
    # Bulk delete remaining
    remaining_ids = question_ids[deleted_count:]
    if remaining_ids:
        start_time = time.perf_counter()
        Question.objects.filter(id__in=remaining_ids).delete()
        bulk_delete_ms = (time.perf_counter() - start_time) * 1000
        print(f"  Bulk delete {len(remaining_ids)} questions: {bulk_delete_ms:.2f} ms")
    
    print()
    return {
        'individual_latencies': delete_latencies,
        'bulk_latency': bulk_delete_ms if remaining_ids else 0,
        'bulk_count': len(remaining_ids) if remaining_ids else 0
    }

def save_detailed_results(db_info, all_results):
    """Save detailed results to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comprehensive_azure_sql_test_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("☁️ COMPREHENSIVE AZURE SQL DATABASE PERFORMANCE TEST\n")
        f.write("=" * 70 + "\n")
        f.write(f"📊 Database: {db_info['database']}\n")
        f.write(f"🔧 Version: {db_info['version'][:100]}...\n")
        f.write(f"🌐 Server: {db_info['server']}\n")
        f.write(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("🔌 CONNECTION LATENCY RESULTS:\n")
        f.write(f"  Average: {all_results['connection']['average']:.2f} ms\n")
        f.write(f"  Individual tests: {[f'{x:.2f}' for x in all_results['connection']['latencies']]}\n\n")
        
        f.write("👥 USER/EVENT SETUP RESULTS:\n")
        f.write(f"  User setup: {all_results['setup']['user_setup']:.2f} ms\n")
        f.write(f"  Event setup: {all_results['setup']['event_setup']:.2f} ms\n\n")
        
        f.write("🏗️ QUESTION CREATION RESULTS:\n")
        f.write(f"  Average: {all_results['creation']['average']:.2f} ms\n")
        f.write(f"  Min: {all_results['creation']['min']:.2f} ms\n")
        f.write(f"  Max: {all_results['creation']['max']:.2f} ms\n\n")
        
        f.write("🔍 QUERY PERFORMANCE RESULTS:\n")
        for op, latency in all_results['queries'].items():
            f.write(f"  {op}: {latency:.2f} ms\n")
        f.write("\n")
        
        f.write("✏️ UPDATE PERFORMANCE RESULTS:\n")
        f.write(f"  Average: {all_results['updates']['average']:.2f} ms\n\n")
        
        f.write("🗑️ DELETE PERFORMANCE RESULTS:\n")
        f.write(f"  Individual deletes: {[f'{x:.2f}' for x in all_results['deletes']['individual_latencies']]}\n")
        if all_results['deletes']['bulk_count'] > 0:
            f.write(f"  Bulk delete ({all_results['deletes']['bulk_count']} items): {all_results['deletes']['bulk_latency']:.2f} ms\n")
    
    print(f"📝 Detailed results saved to: {filename}")
    return filename

def main():
    print("☁️ COMPREHENSIVE AZURE SQL DATABASE PERFORMANCE TEST")
    print("=" * 70)
    
    # Get database info
    db_info = get_database_info()
    print(f"📊 Database: {db_info['database']}")
    print(f"🔧 Version: {db_info['version'][:100]}...")
    print(f"        {db_info['version'][100:200]}...")  # Second line like in Fabric
    print()
    
    all_results = {}
    
    # Run all tests
    all_results['connection'] = test_connection_latency()
    
    user, event, setup_results = test_user_event_setup()
    all_results['setup'] = setup_results
    
    question_ids, creation_results = test_question_creation(user, event)
    all_results['creation'] = creation_results
    
    query_results = test_query_performance(event, user)
    all_results['queries'] = query_results
    
    update_results = test_update_performance(question_ids)
    all_results['updates'] = update_results
    
    delete_results = test_delete_performance(question_ids)
    all_results['deletes'] = delete_results
    
    # Save detailed results
    filename = save_detailed_results(db_info, all_results)
    
    print()
    print("🎯 AZURE SQL PERFORMANCE SUMMARY:")
    print("=" * 40)
    print(f"Connection Latency: {all_results['connection']['average']:.2f} ms")
    print(f"Question Creation: {all_results['creation']['average']:.2f} ms")
    print(f"Query Performance: {statistics.mean(all_results['queries'].values()):.2f} ms avg")
    print(f"Update Performance: {all_results['updates']['average']:.2f} ms")
    print(f"Delete Performance: {statistics.mean(all_results['deletes']['individual_latencies']):.2f} ms avg")

if __name__ == "__main__":
    main()
