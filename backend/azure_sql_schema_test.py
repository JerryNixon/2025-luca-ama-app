#!/usr/bin/env python
"""
Azure SQL Schema Check and Simple Performance Test
==================================================
Check what tables and columns exist, then run basic tests.
"""

import os
import sys
import time
from statistics import mean

# Add Django project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

# Configure Django
import django
django.setup()

from django.db import connection

def check_tables_and_columns():
    """Check what tables and columns exist"""
    print("🔍 AZURE SQL SCHEMA INSPECTION")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Get columns for each table
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, [table_name])
            columns = cursor.fetchall()
            
            if table_name.startswith('api_'):
                print(f"    Columns ({len(columns)}):")
                for col_name, col_type in columns:
                    print(f"      {col_name}: {col_type}")
                print()
    print()

def test_basic_operations():
    """Test basic operations with existing schema"""
    print("⚡ BASIC PERFORMANCE TESTS")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Connection latency
    print("🔌 Connection Latency:")
    times = []
    for i in range(5):
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        times.append(latency_ms)
        print(f"  Test {i+1}: {latency_ms:.2f} ms")
    
    avg_latency = mean(times)
    results['connection_avg'] = avg_latency
    print(f"  📊 Average: {avg_latency:.2f} ms")
    print()
    
    # Test 2: User table operations
    print("👥 User Operations:")
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_user")
        user_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    
    user_count_time = (end_time - start_time) * 1000
    results['user_count'] = user_count_time
    print(f"  Count users: {user_count_time:.2f} ms ({user_count} users)")
    
    # Test superuser lookup
    start_time = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_user WHERE is_superuser = 1")
        superuser_count = cursor.fetchone()[0]
    end_time = time.perf_counter()
    
    superuser_time = (end_time - start_time) * 1000
    results['superuser_lookup'] = superuser_time
    print(f"  Find superusers: {superuser_time:.2f} ms ({superuser_count} found)")
    print()
    
    # Test 3: Event table operations (if it exists and has data)
    print("📅 Event Operations:")
    try:
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_event")
            event_count = cursor.fetchone()[0]
        end_time = time.perf_counter()
        
        event_count_time = (end_time - start_time) * 1000
        results['event_count'] = event_count_time
        print(f"  Count events: {event_count_time:.2f} ms ({event_count} events)")
        
        # Check if events have a name column instead of title
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT TOP 5 id FROM api_event")
            recent_events = cursor.fetchall()
        end_time = time.perf_counter()
        
        recent_time = (end_time - start_time) * 1000
        results['recent_events'] = recent_time
        print(f"  Get recent events: {recent_time:.2f} ms ({len(recent_events)} found)")
        
    except Exception as e:
        print(f"  Event operations failed: {e}")
    print()
    
    # Test 4: Question table operations (if it exists)
    print("❓ Question Operations:")
    try:
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_question")
            question_count = cursor.fetchone()[0]
        end_time = time.perf_counter()
        
        question_count_time = (end_time - start_time) * 1000
        results['question_count'] = question_count_time
        print(f"  Count questions: {question_count_time:.2f} ms ({question_count} questions)")
        
    except Exception as e:
        print(f"  Question operations failed: {e}")
    print()
    
    # Test 5: Simple join if both tables exist
    print("🔄 Join Operations:")
    try:
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, COUNT(e.id) as event_count
                FROM api_user u
                LEFT JOIN api_event e ON u.id = e.host_id
                GROUP BY u.id, u.username
            """)
            user_events = cursor.fetchall()
        end_time = time.perf_counter()
        
        join_time = (end_time - start_time) * 1000
        results['user_event_join'] = join_time
        print(f"  User-Event join: {join_time:.2f} ms ({len(user_events)} users)")
        
    except Exception as e:
        print(f"  Join operations failed: {e}")
    print()
    
    return results

def print_summary(results):
    """Print performance summary"""
    print("📊 AZURE SQL PERFORMANCE SUMMARY")
    print("=" * 50)
    
    # Overall stats
    all_times = list(results.values())
    if all_times:
        avg_time = mean(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        
        print(f"🎯 Key Metrics:")
        for operation, time_ms in results.items():
            op_name = operation.replace('_', ' ').title()
            print(f"   {op_name}: {time_ms:.2f} ms")
        
        print(f"\n📈 Summary:")
        print(f"   Average Operation: {avg_time:.2f} ms")
        print(f"   Fastest Operation: {min_time:.2f} ms")
        print(f"   Slowest Operation: {max_time:.2f} ms")
    
    print(f"\n✅ AZURE SQL TEST COMPLETE")
    print("=" * 50)

def main():
    """Run Azure SQL schema check and performance test"""
    print("☁️ AZURE SQL DATABASE ANALYSIS")
    print("=" * 70)
    print("🔵 Database: Azure SQL Database (Serverless)")
    print("🌍 Connection: Encrypted (SSL/TLS)")
    print()
    
    try:
        # Check schema
        check_tables_and_columns()
        
        # Run performance tests
        results = test_basic_operations()
        
        # Print summary
        print_summary(results)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
