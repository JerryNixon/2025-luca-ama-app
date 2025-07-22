#!/usr/bin/env python3
"""
Azure SQL Latency Benchmark - Equivalent to latency_benchmark.py
Comprehensive testing of CREATE, SELECT, UPDATE, DELETE operations
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

def setup_test_data():
    """Set up test user and event"""
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create(
                id=str(uuid.uuid4()).replace('-', ''),
                email='benchmark@test.com',
                name='Benchmark User',
                role='admin',
                is_active=True,
                is_superuser=True,
                is_anonymous=False,
                date_joined=datetime.now(timezone.utc)
            )
    except Exception:
        user = User.objects.filter(is_superuser=True).first()
    
    event = Event.objects.filter(name='Azure SQL Benchmark Event').first()
    if not event:
        event = Event.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            name='Azure SQL Benchmark Event',
            created_by=user,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    return user, event

def test_create_operations(user, event, iterations=20):
    """Test CREATE operations with statistics"""
    print(f"📝 Testing CREATE Operations ({iterations} iterations)")
    print("-" * 50)
    
    latencies = []
    question_ids = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        
        question = Question.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            text=f"Benchmark Question {i+1} - Azure SQL Performance Test",
            author=user,
            event=event,
            is_anonymous=False,
            upvotes=i % 10,  # Vary upvotes
            is_answered=i % 3 == 0,  # Every 3rd question is answered
            is_starred=i % 5 == 0,   # Every 5th question is starred
            is_staged=False,
            tags='["performance", "benchmark", "azure"]',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        question_ids.append(question.id)
        
        if (i + 1) % 5 == 0:
            print(f"  Created {i+1}/{iterations} questions - Latest: {latency_ms:.2f}ms")
    
    return {
        'latencies': latencies,
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'question_ids': question_ids
    }

def test_select_operations(event, iterations=20):
    """Test various SELECT query patterns"""
    print(f"🔍 Testing SELECT Operations ({iterations} iterations each)")
    print("-" * 50)
    
    results = {}
    
    # Test 1: Select all questions
    print("  Testing: Question.objects.all()...")
    latencies = []
    for i in range(iterations):
        start_time = time.perf_counter()
        list(Question.objects.all())  # Force evaluation
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['select_all'] = {
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['select_all']['average']:.2f}ms")
    
    # Test 2: Select by event
    print("  Testing: Question.objects.filter(event=event)...")
    latencies = []
    for i in range(iterations):
        start_time = time.perf_counter()
        list(Question.objects.filter(event=event))
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['select_by_event'] = {
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['select_by_event']['average']:.2f}ms")
    
    # Test 3: Count queries
    print("  Testing: Question.objects.count()...")
    latencies = []
    for i in range(iterations):
        start_time = time.perf_counter()
        Question.objects.count()
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['count'] = {
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['count']['average']:.2f}ms")
    
    # Test 4: Single object get
    question = Question.objects.filter(event=event).first()
    if question:
        print("  Testing: Question.objects.get(id=...)...")
        latencies = []
        for i in range(iterations):
            start_time = time.perf_counter()
            Question.objects.get(id=question.id)
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000)
        
        results['get_single'] = {
            'average': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'min': min(latencies),
            'max': max(latencies)
        }
        print(f"    Average: {results['get_single']['average']:.2f}ms")
    
    return results

def test_update_operations(question_ids, iterations=10):
    """Test UPDATE operations"""
    print(f"✏️ Testing UPDATE Operations ({iterations} iterations)")
    print("-" * 50)
    
    results = {}
    
    # Test 1: Update text field
    print("  Testing: question.text update...")
    latencies = []
    for i in range(min(iterations, len(question_ids))):
        question = Question.objects.get(id=question_ids[i])
        start_time = time.perf_counter()
        question.text = f"Updated text {i+1} - Azure SQL benchmark"
        question.save()
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['update_text'] = {
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['update_text']['average']:.2f}ms")
    
    # Test 2: Update multiple fields
    print("  Testing: multiple field update...")
    latencies = []
    for i in range(min(iterations, len(question_ids))):
        question = Question.objects.get(id=question_ids[i])
        start_time = time.perf_counter()
        question.upvotes = i + 100
        question.is_starred = True
        question.updated_at = datetime.now(timezone.utc)
        question.save()
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['update_multiple'] = {
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['update_multiple']['average']:.2f}ms")
    
    return results

def test_delete_operations(question_ids, iterations=10):
    """Test DELETE operations"""
    print(f"🗑️ Testing DELETE Operations ({iterations} iterations)")
    print("-" * 50)
    
    results = {}
    
    # Test 1: Individual deletes
    print("  Testing: individual question.delete()...")
    latencies = []
    deleted_ids = []
    
    for i in range(min(iterations, len(question_ids))):
        question_id = question_ids[i]
        start_time = time.perf_counter()
        Question.objects.filter(id=question_id).delete()
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
        deleted_ids.append(question_id)
    
    results['delete_individual'] = {
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['delete_individual']['average']:.2f}ms")
    
    # Test 2: Bulk delete remaining questions
    remaining_ids = [qid for qid in question_ids if qid not in deleted_ids]
    if remaining_ids:
        print("  Testing: bulk delete...")
        start_time = time.perf_counter()
        Question.objects.filter(id__in=remaining_ids).delete()
        end_time = time.perf_counter()
        bulk_latency = (end_time - start_time) * 1000
        
        results['delete_bulk'] = {
            'latency': bulk_latency,
            'count': len(remaining_ids)
        }
        print(f"    Bulk delete of {len(remaining_ids)} questions: {bulk_latency:.2f}ms")
    
    return results

def main():
    print("🔵 Using Azure SQL Database (Serverless) Configuration")
    print("🚀 Azure SQL Comprehensive Latency Benchmark")
    print("=" * 60)
    
    # Setup
    user, event = setup_test_data()
    
    # Run tests
    create_results = test_create_operations(user, event, 20)
    print()
    
    select_results = test_select_operations(event, 20)
    print()
    
    update_results = test_update_operations(create_results['question_ids'], 10)
    print()
    
    delete_results = test_delete_operations(create_results['question_ids'], 10)
    print()
    
    # Summary
    print("📊 COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 40)
    print(f"Database: Azure SQL Database (Serverless)")
    print()
    print("CREATE Operations:")
    print(f"  Average: {create_results['average']:.2f} ms")
    print(f"  Range: {create_results['min']:.2f} - {create_results['max']:.2f} ms")
    print()
    print("SELECT Operations:")
    for op_name, result in select_results.items():
        print(f"  {op_name}: {result['average']:.2f} ms avg")
    print()
    print("UPDATE Operations:")
    for op_name, result in update_results.items():
        print(f"  {op_name}: {result['average']:.2f} ms avg")
    print()
    print("DELETE Operations:")
    for op_name, result in delete_results.items():
        if 'average' in result:
            print(f"  {op_name}: {result['average']:.2f} ms avg")
        else:
            print(f"  {op_name}: {result['latency']:.2f} ms (bulk)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"azure_sql_comprehensive_results_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("Azure SQL Comprehensive Benchmark Results\n")
        f.write("=" * 45 + "\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        
        f.write("CREATE Operations:\n")
        f.write(f"  Average: {create_results['average']:.2f} ms\n")
        f.write(f"  Median: {create_results['median']:.2f} ms\n")
        f.write(f"  Min: {create_results['min']:.2f} ms\n")
        f.write(f"  Max: {create_results['max']:.2f} ms\n\n")
        
        f.write("SELECT Operations:\n")
        for op_name, result in select_results.items():
            f.write(f"  {op_name}: {result['average']:.2f} ms avg\n")
        f.write("\n")
        
        f.write("UPDATE Operations:\n")
        for op_name, result in update_results.items():
            f.write(f"  {op_name}: {result['average']:.2f} ms avg\n")
        f.write("\n")
        
        f.write("DELETE Operations:\n")
        for op_name, result in delete_results.items():
            if 'average' in result:
                f.write(f"  {op_name}: {result['average']:.2f} ms avg\n")
            else:
                f.write(f"  {op_name}: {result['latency']:.2f} ms (bulk)\n")
    
    print(f"\n💾 Results saved to: {filename}")
    print("\n🔍 Compare with your Docker results:")
    print("    CREATE: 8.58-12.41 ms average")
    print("    SELECT: 2.16-7.04 ms average") 
    print("    UPDATE: 7.76-28.77 ms average")
    print("    DELETE: 17.89-30.50 ms average")

if __name__ == "__main__":
    main()
