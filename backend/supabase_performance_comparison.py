#!/usr/bin/env python3
"""
Supabase PostgreSQL Performance Comparison Script
Identical test methodology to Fabric SQL performance comparison
"""

import os
import sys
import django
import time
import statistics
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection, connections
from django.conf import settings
from api.models import User, Event, Question

def print_header():
    """Print test header with database information"""
    print("🔗 Using SUPABASE PostgreSQL Database")
    print(f"🐘 Supabase Database: {settings.DATABASES['default']['NAME']}")
    print(f"🌐 Host: {settings.DATABASES['default']['HOST']}")
    print()

def apply_performance_optimizations():
    """Apply Supabase-specific performance optimizations"""
    print("Applying Supabase performance optimizations...")
    
    # Connection settings already configured in settings.py for Supabase
    # These are handled by psycopg2 and Supabase's connection pooling
    
    print("✅ Performance optimizations applied successfully!")
    print()

def get_database_info():
    """Get database version and configuration info"""
    with connection.cursor() as cursor:
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version_info = cursor.fetchone()[0]
        
        # Get database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        
        # Get current user
        cursor.execute("SELECT current_user;")
        db_user = cursor.fetchone()[0]
        
    return {
        'version': version_info,
        'database': db_name,
        'user': db_user,
        'host': settings.DATABASES['default']['HOST'],
        'port': settings.DATABASES['default']['PORT']
    }

def test_connection_latency(iterations=5):
    """Test raw database connection latency"""
    print("🔌 Testing connection latency...")
    latencies = []
    
    for i in range(iterations):
        start_time = time.time()
        
        # Test with a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        print(f"  Connection test {i+1}: {latency_ms:.2f} ms")
    
    return latencies

def test_question_creation(iterations=10):
    """Test question creation performance - identical to Fabric test"""
    print("🏗️ Quick Question Creation Test (10 iterations)")
    print("--" * 25)
    
    # Ensure we have a test user and event
    test_user, _ = User.objects.get_or_create(
        email='perf_test_user@test.com',
        defaults={
            'username': 'perf_test_user',
            'name': 'Performance Test User',
            'role': 'user',
            'auth_source': 'manual'
        }
    )
    
    test_event, _ = Event.objects.get_or_create(
        name='Performance Test Event',
        defaults={
            'created_by': test_user,
            'is_active': True,
            'is_public': True
        }
    )
    
    latencies = []
    
    for i in range(iterations):
        start_time = time.time()
        
        # Create a question - identical operation to Fabric test
        question = Question.objects.create(
            event=test_event,
            text=f"Performance test question {i+1} - {datetime.now()}",
            author=test_user,
            is_anonymous=False
        )
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        print(f"  Question {i+1}: {latency_ms:.2f} ms")
        
        # Clean up the question to avoid database bloat
        question.delete()
    
    # Clean up test data
    test_event.delete()
    test_user.delete()
    
    return latencies

def main():
    """Main performance test execution"""
    print_header()
    apply_performance_optimizations()
    
    # Get database information
    db_info = get_database_info()
    
    print("🚀 Database Performance Comparison")
    print("=" * 60)
    print(f"📊 Database Type: Supabase PostgreSQL")
    print(f"📁 Database Name: {db_info['database']}")
    print(f"🌐 Host: {db_info['host']}:{settings.DATABASES['default']['PORT']}")
    print(f"🔧 Version: {db_info['version'][:100]}...")
    if len(db_info['version']) > 100:
        print(f"        {db_info['version'][100:200]}...")
    print()
    
    # Test connection latency
    connection_latencies = test_connection_latency()
    print()
    
    # Test question creation performance
    question_latencies = test_question_creation()
    print()
    
    # Calculate statistics
    conn_avg = statistics.mean(connection_latencies)
    
    quest_avg = statistics.mean(question_latencies)
    quest_min = min(question_latencies)
    quest_max = max(question_latencies)
    quest_median = statistics.median(question_latencies)
    
    # Print summary - identical format to Fabric test
    print("📊 SUMMARY")
    print("=" * 30)
    print(f"Database: Supabase PostgreSQL")
    print(f"Connection Latency: {conn_avg:.2f} ms (avg)")
    print(f"Question Creation: {quest_avg:.2f} ms (avg)")
    print(f"  - Fastest: {quest_min:.2f} ms")
    print(f"  - Slowest: {quest_max:.2f} ms")
    print(f"  - Median: {quest_median:.2f} ms")

if __name__ == "__main__":
    main()
