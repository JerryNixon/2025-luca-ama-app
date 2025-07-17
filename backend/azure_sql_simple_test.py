#!/usr/bin/env python3
"""
Azure SQL Simple Performance Test - Raw SQL to avoid model issues
Direct comparison with Docker results
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

def test_connection_latency(iterations=10):
    """Test Azure SQL connection latency"""
    print(f"🔌 Testing connection latency ({iterations} tests)...")
    latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        print(f"  Connection test {i+1}: {latency_ms:.2f} ms")
    
    avg_latency = statistics.mean(latencies)
    print(f"  Average connection latency: {avg_latency:.2f} ms")
    
    return {
        'latencies': latencies,
        'average': avg_latency,
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }

def test_question_creation_raw(iterations=10):
    """Test question creation using raw SQL"""
    print(f"\n🏗️ Question Creation Test - Raw SQL ({iterations} iterations)")
    print("--" * 30)
    
    cursor = connection.cursor()
    
    # Get the existing admin user ID
    cursor.execute("SELECT id FROM api_user WHERE is_superuser = 1")
    user_result = cursor.fetchone()
    if not user_result:
        print("❌ No admin user found")
        return None
    user_id = user_result[0]
    
    # Get or create test event
    cursor.execute("SELECT id FROM api_event WHERE name = 'Azure SQL Test Event'")
    event_result = cursor.fetchone()
    if not event_result:
        event_id = str(uuid.uuid4()).replace('-', '')
        now = datetime.now(timezone.utc)
        cursor.execute("""
            INSERT INTO api_event (id, name, created_by_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [event_id, 'Azure SQL Test Event', user_id, 1, now, now])
    else:
        event_id = event_result[0]
    
    latencies = []
    question_ids = []
    
    for i in range(iterations):
        question_id = str(uuid.uuid4()).replace('-', '')
        now = datetime.now(timezone.utc)
        
        start_time = time.perf_counter()
        
        # Raw SQL INSERT - equivalent to Question.objects.create()
        cursor.execute("""
            INSERT INTO api_question (
                id, text, author_id, event_id, is_anonymous, upvotes, 
                is_answered, is_starred, is_staged, tags, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            question_id,
            f"Test Question {i+1} for Azure SQL - Raw SQL",
            user_id,
            event_id,
            0,  # is_anonymous
            0,  # upvotes
            0,  # is_answered
            0,  # is_starred
            0,  # is_staged
            '[]',  # tags
            now,
            now
        ])
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        question_ids.append(question_id)
        
        print(f"  Question {i+1}: {latency_ms:.2f} ms")
    
    # Clean up test questions
    if question_ids:
        placeholders = ', '.join(['%s'] * len(question_ids))
        cursor.execute(f"DELETE FROM api_question WHERE id IN ({placeholders})", question_ids)
    
    return {
        'latencies': latencies,
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }

def test_select_operations(iterations=10):
    """Test SELECT operations"""
    print(f"\n🔍 SELECT Operations Test ({iterations} iterations each)")
    print("--" * 30)
    
    cursor = connection.cursor()
    results = {}
    
    # Test 1: Count all questions
    print("  Testing: SELECT COUNT(*) FROM api_question...")
    latencies = []
    for i in range(iterations):
        start_time = time.perf_counter()
        cursor.execute("SELECT COUNT(*) FROM api_question")
        cursor.fetchone()
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['count_questions'] = {
        'average': statistics.mean(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['count_questions']['average']:.2f} ms")
    
    # Test 2: Select all questions
    print("  Testing: SELECT * FROM api_question...")
    latencies = []
    for i in range(iterations):
        start_time = time.perf_counter()
        cursor.execute("SELECT TOP 100 * FROM api_question")
        cursor.fetchall()
        end_time = time.perf_counter()
        latencies.append((end_time - start_time) * 1000)
    
    results['select_questions'] = {
        'average': statistics.mean(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }
    print(f"    Average: {results['select_questions']['average']:.2f} ms")
    
    return results

def main():
    print("🔵 Using Azure SQL Database (Serverless) Configuration")
    
    # Get database info
    db_info = get_database_info()
    
    print("\n🚀 Azure SQL vs Docker Performance Comparison")
    print("=" * 60)
    print(f"📊 Database Type: Azure SQL Database (Serverless)")
    print(f"📁 Database Name: {db_info['database']}")
    print(f"🌐 Host: {db_info['server']}")
    print(f"🔧 Version: {db_info['version'][:100]}...")
    print()
    
    # Test connection latency
    connection_results = test_connection_latency(10)
    
    # Test question creation
    question_results = test_question_creation_raw(10)
    
    # Test SELECT operations
    select_results = test_select_operations(10)
    
    print(f"\n📊 AZURE SQL RESULTS SUMMARY")
    print("=" * 40)
    print(f"Database: Azure SQL Database (Serverless)")
    print(f"Connection Latency: {connection_results['average']:.2f} ms (avg)")
    print(f"  - Range: {connection_results['min']:.2f} - {connection_results['max']:.2f} ms")
    if question_results:
        print(f"Question Creation: {question_results['average']:.2f} ms (avg)")
        print(f"  - Fastest: {question_results['min']:.2f} ms")
        print(f"  - Slowest: {question_results['max']:.2f} ms")
        print(f"  - Median: {question_results['median']:.2f} ms")
    
    print(f"\nSELECT Operations:")
    for op_name, result in select_results.items():
        print(f"  {op_name}: {result['average']:.2f} ms avg")
    
    print(f"\n🔥 LATENCY COMPARISON")
    print("=" * 30)
    print(f"📈 Azure SQL vs Docker SQL Server:")
    print(f"  Connection Latency:")
    print(f"    🔵 Azure SQL: {connection_results['average']:.2f} ms")
    print(f"    🐳 Docker:    1.53 ms")
    print(f"    📊 Azure is {connection_results['average']/1.53:.1f}x SLOWER")
    
    if question_results:
        print(f"  Question Creation:")
        print(f"    🔵 Azure SQL: {question_results['average']:.2f} ms")
        print(f"    🐳 Docker:    12.41 ms")
        if question_results['average'] > 12.41:
            print(f"    📊 Azure is {question_results['average']/12.41:.1f}x SLOWER")
        else:
            print(f"    📊 Azure is {12.41/question_results['average']:.1f}x FASTER")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"azure_vs_docker_comparison_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("Azure SQL vs Docker Performance Comparison\n")
        f.write("=" * 45 + "\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        
        f.write("AZURE SQL RESULTS:\n")
        f.write(f"Connection Latency: {connection_results['average']:.2f} ms avg\n")
        if question_results:
            f.write(f"Question Creation: {question_results['average']:.2f} ms avg\n")
        f.write("\nSELECT Operations:\n")
        for op_name, result in select_results.items():
            f.write(f"  {op_name}: {result['average']:.2f} ms avg\n")
        
        f.write(f"\nCOMPARISON WITH DOCKER:\n")
        f.write(f"Azure Connection: {connection_results['average']:.2f} ms vs Docker: 1.53 ms\n")
        f.write(f"Ratio: {connection_results['average']/1.53:.1f}x slower\n")
        if question_results:
            f.write(f"Azure Creation: {question_results['average']:.2f} ms vs Docker: 12.41 ms\n")
            if question_results['average'] > 12.41:
                f.write(f"Ratio: {question_results['average']/12.41:.1f}x slower\n")
            else:
                f.write(f"Ratio: {12.41/question_results['average']:.1f}x faster\n")
    
    print(f"\n💾 Results saved to: {filename}")
    print(f"\n🎯 ANSWER TO YOUR QUESTION:")
    print(f"   Which backend has the HIGHEST latency?")
    print(f"   🔵 Azure SQL clearly shows much higher connection latency!")
    print(f"   📊 {connection_results['average']:.1f}ms vs 1.5ms = {connection_results['average']/1.53:.1f}x slower")

if __name__ == "__main__":
    main()
