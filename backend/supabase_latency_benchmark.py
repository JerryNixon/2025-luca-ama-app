#!/usr/bin/env python3
"""
Supabase PostgreSQL Latency Benchmark
=====================================
Identical test to Fabric SQL for direct performance comparison
This measures the exact same operations we tested with Fabric.
"""

import os
import sys
import django
import time
import statistics
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question, Vote
from django.db import connection, transaction
from django.utils import timezone

# Test configuration - IDENTICAL to Fabric test
TEST_ITERATIONS = 50
TEST_DATA_SIZE = 100

@contextmanager
def measure_time():
    """Context manager to measure execution time"""
    start_time = time.time()
    yield
    end_time = time.time()
    return end_time - start_time

def setup_test_data():
    """Create test data identical to Fabric test"""
    print("🔧 Setting up test data...")
    
    # Create test user
    test_user, created = User.objects.get_or_create(
        email='latency_test_user@test.com',
        defaults={
            'username': 'latency_test_user',
            'name': 'Latency Test User',
            'role': 'user',
            'is_active': True,
            'auth_source': 'manual'
        }
    )
    
    # Create test event
    test_event, created = Event.objects.get_or_create(
        name='Latency Test Event',
        defaults={
            'created_by': test_user,
            'is_active': True,
            'is_public': True,
            'open_date': timezone.now(),
            'close_date': timezone.now()
        }
    )
    
    return test_user, test_event

def cleanup_test_data():
    """Clean up test data"""
    print("🧹 Cleaning up test data...")
    User.objects.filter(email='latency_test_user@test.com').delete()
    Event.objects.filter(name='Latency Test Event').delete()
    Question.objects.filter(text__startswith='Latency test question').delete()

def test_simple_queries():
    """Test 1: Simple SELECT queries - IDENTICAL to Fabric test"""
    print("\n📊 Test 1: Simple SELECT Queries (User count)")
    latencies = []
    
    for i in range(TEST_ITERATIONS):
        start_time = time.time()
        count = User.objects.count()
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # Convert to ms
        latencies.append(latency)
        
        if i < 3:  # Show first few results
            print(f"   Query {i+1}: {latency:.2f}ms (count: {count})")
    
    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    median_latency = statistics.median(latencies)
    
    print(f"\n📈 Simple Query Results ({TEST_ITERATIONS} iterations):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Median:  {median_latency:.2f}ms")
    print(f"   Min:     {min_latency:.2f}ms")
    print(f"   Max:     {max_latency:.2f}ms")
    
    return {
        'test': 'simple_queries',
        'avg': avg_latency,
        'median': median_latency,
        'min': min_latency,
        'max': max_latency
    }

def test_join_queries():
    """Test 2: JOIN queries - IDENTICAL to Fabric test"""
    print("\n📊 Test 2: JOIN Queries (Events with creators)")
    latencies = []
    
    for i in range(TEST_ITERATIONS):
        start_time = time.time()
        # Same query as Fabric test: Events with their creators
        events = list(Event.objects.select_related('created_by').all()[:10])
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # Convert to ms
        latencies.append(latency)
        
        if i < 3:  # Show first few results
            print(f"   Query {i+1}: {latency:.2f}ms (events: {len(events)})")
    
    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    median_latency = statistics.median(latencies)
    
    print(f"\n📈 JOIN Query Results ({TEST_ITERATIONS} iterations):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Median:  {median_latency:.2f}ms")
    print(f"   Min:     {min_latency:.2f}ms")
    print(f"   Max:     {max_latency:.2f}ms")
    
    return {
        'test': 'join_queries',
        'avg': avg_latency,
        'median': median_latency,
        'min': min_latency,
        'max': max_latency
    }

def test_insert_operations(test_user, test_event):
    """Test 3: INSERT operations - IDENTICAL to Fabric test"""
    print(f"\n📊 Test 3: INSERT Operations ({TEST_DATA_SIZE} questions)")
    latencies = []
    
    # Clean up any existing test questions
    Question.objects.filter(text__startswith='Latency test question').delete()
    
    for i in range(TEST_DATA_SIZE):
        start_time = time.time()
        
        question = Question.objects.create(
            event=test_event,
            author=test_user,
            text=f'Latency test question {i+1}',
            is_anonymous=False,
            upvotes=0,
            is_answered=False,
            is_starred=False,
            is_staged=False,
            tags='[]'
        )
        
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # Convert to ms
        latencies.append(latency)
        
        if i < 3:  # Show first few results
            print(f"   Insert {i+1}: {latency:.2f}ms")
    
    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    median_latency = statistics.median(latencies)
    
    print(f"\n📈 INSERT Results ({TEST_DATA_SIZE} operations):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Median:  {median_latency:.2f}ms")
    print(f"   Min:     {min_latency:.2f}ms")
    print(f"   Max:     {max_latency:.2f}ms")
    
    return {
        'test': 'insert_operations',
        'avg': avg_latency,
        'median': median_latency,
        'min': min_latency,
        'max': max_latency
    }

def test_complex_queries():
    """Test 4: Complex queries - IDENTICAL to Fabric test"""
    print("\n📊 Test 4: Complex Queries (Questions with votes and authors)")
    latencies = []
    
    for i in range(TEST_ITERATIONS):
        start_time = time.time()
        
        # Same complex query as Fabric test
        questions = list(
            Question.objects
            .select_related('author', 'event')
            .prefetch_related('vote_records')
            .filter(event__is_active=True)
            .order_by('-upvotes', '-created_at')[:10]
        )
        
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # Convert to ms
        latencies.append(latency)
        
        if i < 3:  # Show first few results
            print(f"   Query {i+1}: {latency:.2f}ms (questions: {len(questions)})")
    
    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    median_latency = statistics.median(latencies)
    
    print(f"\n📈 Complex Query Results ({TEST_ITERATIONS} iterations):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Median:  {median_latency:.2f}ms")
    print(f"   Min:     {min_latency:.2f}ms")
    print(f"   Max:     {max_latency:.2f}ms")
    
    return {
        'test': 'complex_queries',
        'avg': avg_latency,
        'median': median_latency,
        'min': min_latency,
        'max': max_latency
    }

def run_latency_benchmark():
    """Run complete latency benchmark - IDENTICAL to Fabric test"""
    print("🚀 Supabase PostgreSQL Latency Benchmark")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔢 Test Iterations: {TEST_ITERATIONS}")
    print(f"📊 Insert Operations: {TEST_DATA_SIZE}")
    print(f"🌍 Database: Supabase PostgreSQL")
    print(f"🏢 Host: db.zcbgzcoqrxkzkzfugoqk.supabase.co")
    print("=" * 60)
    
    # Setup test data
    test_user, test_event = setup_test_data()
    
    results = []
    
    try:
        # Run all tests in the same order as Fabric test
        results.append(test_simple_queries())
        results.append(test_join_queries())
        results.append(test_insert_operations(test_user, test_event))
        results.append(test_complex_queries())
        
        # Summary - IDENTICAL format to Fabric test
        print("\n" + "=" * 60)
        print("📊 SUPABASE POSTGRESQL BENCHMARK SUMMARY")
        print("=" * 60)
        
        for result in results:
            print(f"{result['test'].upper():<20} | Avg: {result['avg']:>7.2f}ms | "
                  f"Med: {result['median']:>7.2f}ms | Min: {result['min']:>7.2f}ms | "
                  f"Max: {result['max']:>7.2f}ms")
        
        # Overall average
        overall_avg = statistics.mean([r['avg'] for r in results])
        print("-" * 60)
        print(f"{'OVERALL AVERAGE':<20} | Avg: {overall_avg:>7.2f}ms")
        print("=" * 60)
        
        # Connection info
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            print(f"🔗 Database Version: {db_version}")
        
        print(f"📍 Platform: Supabase (PostgreSQL)")
        print(f"🌍 SSL Connection: Required")
        print(f"⚡ Connection Pooling: Enabled")
        
        return results
        
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    try:
        results = run_latency_benchmark()
        print(f"\n✅ Benchmark completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
