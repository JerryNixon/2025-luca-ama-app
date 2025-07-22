#!/usr/bin/env python3
"""
Azure SQL Quick Question Test - Equivalent to quick_question_test.py
Tests your exact request: Question.objects.create() operations
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
    
    # Get server name from connection string
    server_name = connection.settings_dict.get('HOST', 'unknown')
    
    return {
        'version': version,
        'database': db_name,
        'server': server_name,
        'engine': connection.settings_dict.get('ENGINE', 'unknown')
    }

def test_connection_latency(iterations=5):
    """Test Azure SQL connection latency"""
    print("🔌 Testing connection latency...")
    latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        
        # Simple connection test
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
        'min': min(latencies),
        'max': max(latencies)
    }

def setup_test_data():
    """Set up test user and event"""
    # Get or create test user
    try:
        user = User.objects.filter(email='test@example.com').first()
        if not user:
            user = User.objects.create(
                id=str(uuid.uuid4()).replace('-', ''),
                email='test@example.com',
                name='Test User',
                role='participant',
                is_active=True,
                is_anonymous=False,
                date_joined=datetime.now(timezone.utc)
            )
    except Exception as e:
        print(f"Using existing superuser for test data: {e}")
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            raise Exception("No user available for testing")
    
    # Get or create test event
    event = Event.objects.filter(name='Azure SQL Test Event').first()
    if not event:
        event = Event.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            name='Azure SQL Test Event',
            created_by=user,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    return user, event

def test_question_creation(user, event, iterations=10):
    """Test Question.objects.create() performance - your exact request"""
    print(f"🏗️ Quick Question Creation Test ({iterations} iterations)")
    print("--" * 25)
    
    latencies = []
    question_ids = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        
        # Your exact request: Question.objects.create()
        question = Question.objects.create(
            id=str(uuid.uuid4()).replace('-', ''),
            text=f"Test Question {i+1} for Azure SQL",
            author=user,
            event=event,
            is_anonymous=False,
            upvotes=0,
            is_answered=False,
            is_starred=False,
            is_staged=False,
            tags='[]',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        question_ids.append(question.id)
        
        print(f"  Question {i+1}: {latency_ms:.2f} ms")
    
    # Clean up test questions
    Question.objects.filter(id__in=question_ids).delete()
    
    return {
        'latencies': latencies,
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }

def main():
    print("🔵 Using Azure SQL Database (Serverless) Configuration")
    
    # Get database info
    db_info = get_database_info()
    
    print("🚀 Azure SQL Performance Comparison")
    print("=" * 60)
    print(f"📊 Database Type: Azure SQL Database (Serverless)")
    print(f"📁 Database Name: {db_info['database']}")
    print(f"🌐 Host: {db_info['server']}")
    print(f"🔧 Version: {db_info['version'][:100]}...")  # Truncate long version string
    print()
    
    # Test connection latency
    connection_results = test_connection_latency(5)
    print()
    
    # Setup test data
    user, event = setup_test_data()
    
    # Test question creation
    question_results = test_question_creation(user, event, 10)
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 30)
    print(f"Database: Azure SQL Database (Serverless)")
    print(f"Connection Latency: {connection_results['average']:.2f} ms (avg)")
    print(f"Question Creation: {question_results['average']:.2f} ms (avg)")
    print(f"  - Fastest: {question_results['min']:.2f} ms")
    print(f"  - Slowest: {question_results['max']:.2f} ms")
    print(f"  - Median: {question_results['median']:.2f} ms")
    print()
    
    # Save results for comparison
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = {
        'timestamp': timestamp,
        'database_type': 'Azure SQL Database (Serverless)',
        'database_name': db_info['database'],
        'server': db_info['server'],
        'connection_latency': connection_results,
        'question_creation': question_results
    }
    
    filename = f"azure_sql_quick_test_results_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write("Azure SQL Quick Question Test Results\n")
        f.write("=" * 40 + "\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Database: {db_info['database']}\n")
        f.write(f"Server: {db_info['server']}\n\n")
        f.write("Connection Latency Results:\n")
        f.write(f"  Average: {connection_results['average']:.2f} ms\n")
        f.write(f"  Min: {connection_results['min']:.2f} ms\n")
        f.write(f"  Max: {connection_results['max']:.2f} ms\n\n")
        f.write("Question Creation Results:\n")
        f.write(f"  Average: {question_results['average']:.2f} ms\n")
        f.write(f"  Median: {question_results['median']:.2f} ms\n")
        f.write(f"  Min: {question_results['min']:.2f} ms\n")
        f.write(f"  Max: {question_results['max']:.2f} ms\n")
    
    print(f"💾 Results saved to: {filename}")
    print()
    print("🔍 Compare these results with your Docker (1.53ms connection, 12.41ms creation)")
    print("    and Fabric SQL results to find the highest latency platform!")

if __name__ == "__main__":
    main()
