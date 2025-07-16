#!/usr/bin/env python3
"""
Azure SQL Database Performance Benchmark

Comprehensive performance testing for Azure SQL Database (Serverless)
comparing against Docker and Fabric SQL performance results.

Features:
- Django ORM operation benchmarks
- Raw SQL query performance
- Concurrent operation testing
- Cold start vs warm performance
- Statistical analysis and comparison

Usage:
    python azure_sql_performance_test.py
"""

import os
import sys
import time
import statistics
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add backend to path for Django imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Set Django settings for Azure SQL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azure_sql_settings')

try:
    import django
    django.setup()
    
    from django.db import connection, transaction
    from api.models import User, Event, Question
    
except ImportError as e:
    print(f"❌ Django import error: {e}")
    print("💡 Make sure Django is properly configured for Azure SQL")
    sys.exit(1)

class AzureSQLPerformanceTester:
    def __init__(self):
        self.results = {
            'test_info': {
                'database_type': 'Azure SQL Database (Serverless)',
                'test_time': datetime.now().isoformat(),
                'environment': os.environ.get('DATABASE_TYPE', 'azure_sql_serverless')
            },
            'connection_tests': {},
            'orm_operations': {},
            'raw_sql_operations': {},
            'concurrent_operations': {},
            'cold_vs_warm': {}
        }
    
    def test_cold_start_performance(self):
        """Test performance after potential auto-pause"""
        print("🧊 Testing Cold Start Performance...")
        print("-" * 50)
        
        try:
            # Force a pause check by waiting a moment
            print("⏳ Waiting to simulate potential pause...")
            time.sleep(2)
            
            # First query (potential cold start)
            start_time = time.perf_counter()
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM api_user")
                result = cursor.fetchone()
            cold_time = (time.perf_counter() - start_time) * 1000
            
            # Second query (warm)
            start_time = time.perf_counter()
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM api_user")
                result = cursor.fetchone()
            warm_time = (time.perf_counter() - start_time) * 1000
            
            # Third query (warm)
            start_time = time.perf_counter()
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM api_user")
                result = cursor.fetchone()
            warm_time_2 = (time.perf_counter() - start_time) * 1000
            
            self.results['cold_vs_warm'] = {
                'cold_start_ms': cold_time,
                'warm_query_1_ms': warm_time,
                'warm_query_2_ms': warm_time_2,
                'performance_difference': cold_time - warm_time
            }
            
            print(f"❄️  Cold start query: {cold_time:.2f}ms")
            print(f"🔥 Warm query 1: {warm_time:.2f}ms")
            print(f"🔥 Warm query 2: {warm_time_2:.2f}ms")
            print(f"📊 Difference: {cold_time - warm_time:.2f}ms")
            
            if cold_time > warm_time * 2:
                print("⚠️  Significant cold start penalty detected")
            else:
                print("✅ Minimal cold start impact")
                
        except Exception as e:
            print(f"❌ Cold start test failed: {e}")
    
    def test_connection_performance(self):
        """Test database connection performance"""
        print("🔗 Testing Connection Performance...")
        print("-" * 50)
        
        connection_times = []
        
        for i in range(10):
            try:
                start_time = time.perf_counter()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                end_time = time.perf_counter()
                
                conn_time = (end_time - start_time) * 1000
                connection_times.append(conn_time)
                print(f"   Connection {i+1}: {conn_time:.2f}ms")
                
            except Exception as e:
                print(f"❌ Connection test {i+1} failed: {e}")
        
        if connection_times:
            self.results['connection_tests'] = {
                'avg_ms': statistics.mean(connection_times),
                'min_ms': min(connection_times),
                'max_ms': max(connection_times),
                'median_ms': statistics.median(connection_times),
                'std_dev': statistics.stdev(connection_times) if len(connection_times) > 1 else 0
            }
            
            avg_time = statistics.mean(connection_times)
            print(f"\n📊 Connection Summary:")
            print(f"   Average: {avg_time:.2f}ms")
            print(f"   Range: {min(connection_times):.2f}ms - {max(connection_times):.2f}ms")
    
    def test_orm_operations(self):
        """Test Django ORM performance"""
        print("\n🔧 Testing Django ORM Operations...")
        print("-" * 50)
        
        operations = {
            'user_count': [],
            'user_list': [],
            'user_create': [],
            'user_filter': [],
            'event_count': [],
            'event_list': [],
            'question_count': []
        }
        
        # Test each operation multiple times
        for i in range(5):
            try:
                # User count
                start_time = time.perf_counter()
                count = User.objects.count()
                operations['user_count'].append((time.perf_counter() - start_time) * 1000)
                
                # User list (first 10)
                start_time = time.perf_counter()
                users = list(User.objects.all()[:10])
                operations['user_list'].append((time.perf_counter() - start_time) * 1000)
                
                # User filter
                start_time = time.perf_counter()
                active_users = list(User.objects.filter(is_active=True)[:5])
                operations['user_filter'].append((time.perf_counter() - start_time) * 1000)
                
                # Event count
                start_time = time.perf_counter()
                event_count = Event.objects.count()
                operations['event_count'].append((time.perf_counter() - start_time) * 1000)
                
                # Event list
                start_time = time.perf_counter()
                events = list(Event.objects.all()[:10])
                operations['event_list'].append((time.perf_counter() - start_time) * 1000)
                
                # Question count
                start_time = time.perf_counter()
                question_count = Question.objects.count()
                operations['question_count'].append((time.perf_counter() - start_time) * 1000)
                
                print(f"   Iteration {i+1} completed")
                
            except Exception as e:
                print(f"❌ ORM test iteration {i+1} failed: {e}")
        
        # Calculate statistics
        self.results['orm_operations'] = {}
        for operation, times in operations.items():
            if times:
                self.results['orm_operations'][operation] = {
                    'avg_ms': statistics.mean(times),
                    'min_ms': min(times),
                    'max_ms': max(times),
                    'median_ms': statistics.median(times)
                }
        
        # Display results
        print(f"\n📊 ORM Performance Results:")
        for operation, stats in self.results['orm_operations'].items():
            print(f"   {operation:15}: {stats['avg_ms']:6.2f}ms avg")
    
    def test_raw_sql_performance(self):
        """Test raw SQL query performance"""
        print("\n⚡ Testing Raw SQL Performance...")
        print("-" * 50)
        
        queries = {
            'simple_select': "SELECT COUNT(*) FROM api_user",
            'join_query': """
                SELECT u.name, COUNT(e.id) as event_count 
                FROM api_user u 
                LEFT JOIN api_event e ON u.id = e.created_by_id 
                GROUP BY u.id, u.name
            """,
            'complex_filter': """
                SELECT e.*, u.name as creator_name 
                FROM api_event e 
                JOIN api_user u ON e.created_by_id = u.id 
                WHERE e.is_public = 1 
                ORDER BY e.created_at DESC
            """,
            'aggregate_query': """
                SELECT 
                    COUNT(*) as total_questions,
                    AVG(CAST(upvote_count as FLOAT)) as avg_upvotes
                FROM api_question 
                WHERE is_answered = 0
            """
        }
        
        self.results['raw_sql_operations'] = {}
        
        for query_name, sql in queries.items():
            times = []
            
            for i in range(5):
                try:
                    start_time = time.perf_counter()
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                        results = cursor.fetchall()
                    end_time = time.perf_counter()
                    
                    query_time = (end_time - start_time) * 1000
                    times.append(query_time)
                    
                except Exception as e:
                    print(f"❌ Query {query_name} iteration {i+1} failed: {e}")
            
            if times:
                self.results['raw_sql_operations'][query_name] = {
                    'avg_ms': statistics.mean(times),
                    'min_ms': min(times),
                    'max_ms': max(times),
                    'median_ms': statistics.median(times)
                }
        
        # Display results
        print(f"\n📊 Raw SQL Performance Results:")
        for query_name, stats in self.results['raw_sql_operations'].items():
            print(f"   {query_name:20}: {stats['avg_ms']:6.2f}ms avg")
    
    def test_concurrent_operations(self):
        """Test concurrent database operations"""
        print("\n🔄 Testing Concurrent Operations...")
        print("-" * 50)
        
        def run_concurrent_query():
            """Single concurrent query operation"""
            try:
                start_time = time.perf_counter()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM api_user")
                    result = cursor.fetchone()
                return (time.perf_counter() - start_time) * 1000
            except Exception as e:
                print(f"❌ Concurrent query failed: {e}")
                return None
        
        # Test with different concurrency levels
        concurrency_levels = [1, 2, 5, 10]
        
        self.results['concurrent_operations'] = {}
        
        for level in concurrency_levels:
            print(f"   Testing {level} concurrent operations...")
            
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=level) as executor:
                futures = [executor.submit(run_concurrent_query) for _ in range(level)]
                times = []
                
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        times.append(result)
            
            total_time = (time.perf_counter() - start_time) * 1000
            
            if times:
                self.results['concurrent_operations'][f'concurrency_{level}'] = {
                    'total_time_ms': total_time,
                    'avg_query_time_ms': statistics.mean(times),
                    'max_query_time_ms': max(times),
                    'queries_completed': len(times),
                    'throughput_qps': len(times) / (total_time / 1000)
                }
                
                print(f"      Total time: {total_time:.2f}ms")
                print(f"      Avg query: {statistics.mean(times):.2f}ms")
                print(f"      Throughput: {len(times) / (total_time / 1000):.2f} queries/sec")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"azure_sql_performance_{timestamp}.json"
        filepath = os.path.join(os.path.dirname(__file__), '..', 'results', filename)
        
        # Ensure results directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filepath
    
    def display_summary(self):
        """Display test summary"""
        print("\n" + "="*60)
        print("📈 AZURE SQL DATABASE PERFORMANCE SUMMARY")
        print("="*60)
        
        # Connection performance
        if 'connection_tests' in self.results and self.results['connection_tests']:
            conn = self.results['connection_tests']
            print(f"🔗 Connection: {conn['avg_ms']:.2f}ms avg ({conn['min_ms']:.1f}-{conn['max_ms']:.1f}ms)")
        
        # Cold vs Warm
        if 'cold_vs_warm' in self.results and self.results['cold_vs_warm']:
            cold_warm = self.results['cold_vs_warm']
            print(f"❄️  Cold Start: {cold_warm['cold_start_ms']:.2f}ms vs {cold_warm['warm_query_1_ms']:.2f}ms warm")
        
        # ORM performance
        if self.results.get('orm_operations'):
            orm_times = [stats['avg_ms'] for stats in self.results['orm_operations'].values()]
            if orm_times:
                avg_orm = statistics.mean(orm_times)
                print(f"🔧 ORM Average: {avg_orm:.2f}ms")
        
        # Raw SQL performance
        if self.results.get('raw_sql_operations'):
            sql_times = [stats['avg_ms'] for stats in self.results['raw_sql_operations'].values()]
            if sql_times:
                avg_sql = statistics.mean(sql_times)
                print(f"⚡ SQL Average: {avg_sql:.2f}ms")
        
        # Performance assessment
        all_times = []
        for category in ['orm_operations', 'raw_sql_operations']:
            if self.results.get(category):
                for stats in self.results[category].values():
                    all_times.append(stats['avg_ms'])
        
        if all_times:
            overall_avg = statistics.mean(all_times)
            print(f"\n🎯 Overall Average: {overall_avg:.2f}ms")
            
            if overall_avg < 50:
                assessment = "🚀 Excellent"
            elif overall_avg < 100:
                assessment = "✅ Good"
            elif overall_avg < 200:
                assessment = "⚠️  Moderate"
            else:
                assessment = "🐌 Needs Optimization"
            
            print(f"📊 Performance: {assessment}")
    
    def run_all_tests(self):
        """Run complete performance test suite"""
        print("🔵 Azure SQL Database (Serverless) Performance Test")
        print("=" * 60)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_connection_performance()
        self.test_cold_start_performance()
        self.test_orm_operations()
        self.test_raw_sql_performance()
        self.test_concurrent_operations()
        
        # Display summary and save results
        self.display_summary()
        self.save_results()
        
        print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎯 Next Steps:")
        print("   1. Compare with Docker SQL results")
        print("   2. Compare with Fabric SQL results")
        print("   3. Analyze performance differences")
        print("   4. Consider optimization strategies")

def main():
    """Main test execution"""
    try:
        tester = AzureSQLPerformanceTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
