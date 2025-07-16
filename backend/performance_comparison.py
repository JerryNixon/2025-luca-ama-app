#!/usr/bin/env python
"""
Database Performance Comparison Script

This script allows you to easily switch between local Docker SQL Server and Microsoft Fabric
to compare performance. Simply set the USE_LOCAL_DB environment variable.

Usage:
    # Test local Docker SQL Server
    set USE_LOCAL_DB=true && python performance_comparison.py
    
    # Test Microsoft Fabric
    set USE_LOCAL_DB=false && python performance_comparison.py
"""

import os
import sys
import django
import time
import statistics
from datetime import datetime, timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection
from api.models import User, Event, Question


def get_database_info():
    """Get current database configuration and info"""
    from django.conf import settings
    
    db_config = settings.DATABASES['default']
    use_local = os.getenv('USE_LOCAL_DB', 'false').lower() == 'true'
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DB_NAME(), @@VERSION")
            result = cursor.fetchone()
            db_name = result[0]
            db_version = result[1][:100] + "..." if len(result[1]) > 100 else result[1]
        
        return {
            'type': 'Docker SQL Server' if use_local else 'Microsoft Fabric',
            'name': db_name,
            'host': db_config.get('HOST', 'N/A'),
            'port': db_config.get('PORT', 'N/A'),
            'version': db_version,
            'use_local': use_local
        }
    except Exception as e:
        return {'error': str(e)}


def run_quick_create_test(iterations=10):
    """Run a quick question creation test"""
    print(f"🏗️ Quick Question Creation Test ({iterations} iterations)")
    print("-" * 50)
    
    # Setup test data
    user, _ = User.objects.get_or_create(
        email="perf_test@example.com",
        defaults={
            'name': 'Performance Test User',
            'username': 'perf_test_user',
            'role': 'user'
        }
    )
    
    event, _ = Event.objects.get_or_create(
        name="Performance Test Event",
        defaults={
            'created_by': user,
            'is_active': True,
            'is_public': True
        }
    )
    
    times = []
    created_questions = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        
        question = Question.objects.create(
            text=f"Performance test question {i+1} - {datetime.now().isoformat()}",
            event=event,
            author=user,
            is_anonymous=False
        )
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        times.append(duration_ms)
        created_questions.append(question)
        
        print(f"  Question {i+1}: {duration_ms:.2f} ms")
    
    # Clean up
    for question in created_questions:
        question.delete()
    
    return {
        'operation': 'CREATE',
        'iterations': len(times),
        'average_ms': statistics.mean(times),
        'median_ms': statistics.median(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'times': times
    }


def main():
    print("🚀 Database Performance Comparison")
    print("=" * 60)
    
    # Get database info
    db_info = get_database_info()
    
    if 'error' in db_info:
        print(f"❌ Database connection failed: {db_info['error']}")
        return
    
    print(f"📊 Database Type: {db_info['type']}")
    print(f"📁 Database Name: {db_info['name']}")
    print(f"🌐 Host: {db_info['host']}:{db_info['port']}")
    print(f"🔧 Version: {db_info['version']}")
    print()
    
    # Test connection latency
    print("🔌 Testing connection latency...")
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
    print(f"  Average connection latency: {avg_connection:.2f} ms\n")
    
    # Run question creation test
    create_results = run_quick_create_test(10)
    
    # Print summary
    print("\n📊 SUMMARY")
    print("=" * 30)
    print(f"Database: {db_info['type']}")
    print(f"Connection Latency: {avg_connection:.2f} ms (avg)")
    print(f"Question Creation: {create_results['average_ms']:.2f} ms (avg)")
    print(f"  - Fastest: {create_results['min_ms']:.2f} ms")
    print(f"  - Slowest: {create_results['max_ms']:.2f} ms")
    print(f"  - Median: {create_results['median_ms']:.2f} ms")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_type = "local" if db_info['use_local'] else "fabric"
    filename = f"performance_results_{db_type}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Database Performance Test Results\n")
        f.write(f"================================\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Database Type: {db_info['type']}\n")
        f.write(f"Database Name: {db_info['name']}\n")
        f.write(f"Host: {db_info['host']}:{db_info['port']}\n\n")
        f.write(f"Connection Latency (5 tests):\n")
        for i, time_ms in enumerate(connection_times, 1):
            f.write(f"  Test {i}: {time_ms:.2f} ms\n")
        f.write(f"  Average: {avg_connection:.2f} ms\n\n")
        f.write(f"Question Creation Latency ({create_results['iterations']} tests):\n")
        for i, time_ms in enumerate(create_results['times'], 1):
            f.write(f"  Test {i}: {time_ms:.2f} ms\n")
        f.write(f"  Average: {create_results['average_ms']:.2f} ms\n")
        f.write(f"  Median: {create_results['median_ms']:.2f} ms\n")
        f.write(f"  Min: {create_results['min_ms']:.2f} ms\n")
        f.write(f"  Max: {create_results['max_ms']:.2f} ms\n")
    
    print(f"\n📝 Results saved to: {filename}")


if __name__ == "__main__":
    main()
