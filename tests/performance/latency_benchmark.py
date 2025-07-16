#!/usr/bin/env python
"""
Django ORM Latency Benchmark Script

This script tests the performance of key Django ORM operations on your Question model
to help identify whether performance issues are caused by Fabric SQL or your code.

Usage:
    python latency_benchmark.py

Results are printed to console and optionally saved to latency_log.txt
"""

import os
import sys
import django
import time
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import transaction, connection
from api.models import User, Event, Question


class LatencyBenchmark:
    """Benchmark Django ORM operations for latency testing"""
    
    def __init__(self, log_file: str = "latency_log.txt"):
        self.log_file = log_file
        self.results = []
        self.test_data = {}
        
    def log(self, message: str):
        """Log message to console and file"""
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    
    def measure_time(self, operation_name: str, func, *args, **kwargs) -> float:
        """Measure execution time of a function in milliseconds"""
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            self.log(f"✅ {operation_name}: {duration_ms:.2f} ms")
            return duration_ms, result
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            self.log(f"❌ {operation_name} FAILED: {duration_ms:.2f} ms - {str(e)}")
            return duration_ms, None
    
    def setup_test_data(self):
        """Create necessary test data (user and event)"""
        self.log("\n📋 Setting up test data...")
        
        # Create or get test user
        duration_ms, user = self.measure_time(
            "Create/Get Test User",
            User.objects.get_or_create,
            email="test_user@example.com",
            defaults={
                'name': 'Test User',
                'username': 'test_user_benchmark',
                'role': 'user'
            }
        )
        self.test_data['user'] = user[0] if user else None
        
        # Create or get test event
        duration_ms, event = self.measure_time(
            "Create/Get Test Event",
            Event.objects.get_or_create,
            name="Benchmark Test Event",
            defaults={
                'created_by': self.test_data['user'],
                'is_active': True,
                'is_public': True
            }
        )
        self.test_data['event'] = event[0] if event else None
        
        if not self.test_data['user'] or not self.test_data['event']:
            raise Exception("Failed to create test data")
            
        self.log(f"✅ Test data ready - User: {self.test_data['user'].id}, Event: {self.test_data['event'].id}")
    
    def benchmark_create_operations(self, count: int = 10):
        """Benchmark Question creation operations"""
        self.log(f"\n🏗️ Testing Question Creation ({count} iterations)...")
        
        times = []
        created_questions = []
        
        for i in range(count):
            duration_ms, question = self.measure_time(
                f"Create Question {i+1}",
                Question.objects.create,
                text=f"Test Question {i+1} - {datetime.now().isoformat()}",
                event=self.test_data['event'],
                author=self.test_data['user'],
                is_anonymous=False
            )
            
            if question:
                times.append(duration_ms)
                created_questions.append(question)
        
        self.test_data['created_questions'] = created_questions
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            median_time = statistics.median(times)
            
            self.log(f"\n📊 CREATE OPERATION STATS:")
            self.log(f"   Average: {avg_time:.2f} ms")
            self.log(f"   Median:  {median_time:.2f} ms")
            self.log(f"   Min:     {min_time:.2f} ms")
            self.log(f"   Max:     {max_time:.2f} ms")
            
            self.results.append({
                'operation': 'CREATE',
                'count': len(times),
                'avg_ms': avg_time,
                'median_ms': median_time,
                'min_ms': min_time,
                'max_ms': max_time
            })
    
    def benchmark_select_operations(self, count: int = 10):
        """Benchmark Question selection operations"""
        self.log(f"\n🔍 Testing Question Selection ({count} iterations)...")
        
        if not self.test_data.get('created_questions'):
            self.log("⚠️ No questions available for selection test")
            return
        
        times = []
        
        # Test various select operations
        operations = [
            ("Select All Questions", lambda: list(Question.objects.all())),
            ("Select Questions by Event", lambda: list(Question.objects.filter(event=self.test_data['event']))),
            ("Select Questions by Author", lambda: list(Question.objects.filter(author=self.test_data['user']))),
            ("Count Questions", lambda: Question.objects.count()),
            ("Get Single Question by ID", lambda: Question.objects.get(id=self.test_data['created_questions'][0].id)),
        ]
        
        for op_name, op_func in operations:
            op_times = []
            for i in range(count):
                duration_ms, result = self.measure_time(f"{op_name} {i+1}", op_func)
                if result is not None:
                    op_times.append(duration_ms)
            
            if op_times:
                avg_time = statistics.mean(op_times)
                self.log(f"   {op_name} - Average: {avg_time:.2f} ms")
                times.extend(op_times)
        
        if times:
            avg_time = statistics.mean(times)
            self.results.append({
                'operation': 'SELECT',
                'count': len(times),
                'avg_ms': avg_time,
                'min_ms': min(times),
                'max_ms': max(times)
            })
    
    def benchmark_update_operations(self, count: int = 10):
        """Benchmark Question update operations"""
        self.log(f"\n✏️ Testing Question Updates ({count} iterations)...")
        
        if not self.test_data.get('created_questions'):
            self.log("⚠️ No questions available for update test")
            return
        
        times = []
        questions = self.test_data['created_questions']
        
        for i in range(min(count, len(questions))):
            question = questions[i]
            duration_ms, result = self.measure_time(
                f"Update Question {i+1}",
                self._update_question,
                question,
                f"Updated text {i+1} - {datetime.now().isoformat()}"
            )
            
            if result:
                times.append(duration_ms)
        
        if times:
            avg_time = statistics.mean(times)
            self.log(f"\n📊 UPDATE OPERATION STATS:")
            self.log(f"   Average: {avg_time:.2f} ms")
            
            self.results.append({
                'operation': 'UPDATE',
                'count': len(times),
                'avg_ms': avg_time,
                'min_ms': min(times),
                'max_ms': max(times)
            })
    
    def _update_question(self, question: Question, new_text: str):
        """Helper method to update a question"""
        question.text = new_text
        question.upvotes += 1
        question.save()
        return question
    
    def benchmark_delete_operations(self):
        """Benchmark Question deletion operations"""
        self.log(f"\n🗑️ Testing Question Deletion...")
        
        if not self.test_data.get('created_questions'):
            self.log("⚠️ No questions available for delete test")
            return
        
        times = []
        questions = self.test_data['created_questions'].copy()
        
        # Delete half of the questions individually
        delete_count = len(questions) // 2
        for i in range(delete_count):
            question = questions[i]
            duration_ms, result = self.measure_time(
                f"Delete Question {i+1}",
                question.delete
            )
            times.append(duration_ms)
        
        # Bulk delete the rest
        remaining_questions = questions[delete_count:]
        if remaining_questions:
            question_ids = [q.id for q in remaining_questions]
            duration_ms, result = self.measure_time(
                f"Bulk Delete {len(remaining_questions)} Questions",
                Question.objects.filter(id__in=question_ids).delete
            )
            times.append(duration_ms)
        
        if times:
            avg_time = statistics.mean(times)
            self.log(f"\n📊 DELETE OPERATION STATS:")
            self.log(f"   Average: {avg_time:.2f} ms")
            
            self.results.append({
                'operation': 'DELETE',
                'count': len(times),
                'avg_ms': avg_time,
                'min_ms': min(times),
                'max_ms': max(times)
            })
    
    def test_database_connection(self):
        """Test basic database connectivity and info"""
        self.log("\n🔌 Testing Database Connection...")
        
        # Get database info
        duration_ms, result = self.measure_time(
            "Database Connection Test",
            self._get_db_info
        )
        
        return result
    
    def _get_db_info(self):
        """Get database connection information"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            
            return {'version': version, 'db_name': db_name}
    
    def run_benchmark(self):
        """Run the complete benchmark suite"""
        # Initialize log file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"Django ORM Latency Benchmark - {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
        
        self.log(f"🚀 Django ORM Latency Benchmark Started")
        self.log(f"📅 Timestamp: {datetime.now().isoformat()}")
        
        # Test database connection
        db_info = self.test_database_connection()
        if db_info:
            self.log(f"📊 Database: {db_info['db_name']}")
            self.log(f"🔧 Version: {db_info['version'][:100]}...")  # Truncate long version string
        
        try:
            # Setup test data
            self.setup_test_data()
            
            # Run benchmarks
            self.benchmark_create_operations(count=10)
            self.benchmark_select_operations(count=5)
            self.benchmark_update_operations(count=5)
            self.benchmark_delete_operations()
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            self.log(f"❌ Benchmark failed: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        
        finally:
            # Cleanup any remaining test data
            self.cleanup()
    
    def print_summary(self):
        """Print benchmark summary"""
        self.log("\n" + "=" * 60)
        self.log("📊 BENCHMARK SUMMARY")
        self.log("=" * 60)
        
        if not self.results:
            self.log("No results to display")
            return
        
        for result in self.results:
            self.log(f"\n{result['operation']} Operations:")
            self.log(f"  Iterations: {result['count']}")
            self.log(f"  Average:    {result['avg_ms']:.2f} ms")
            if 'median_ms' in result:
                self.log(f"  Median:     {result['median_ms']:.2f} ms")
            self.log(f"  Min:        {result['min_ms']:.2f} ms")
            self.log(f"  Max:        {result['max_ms']:.2f} ms")
        
        # Overall stats
        all_times = []
        for result in self.results:
            all_times.extend([result['avg_ms']] * result['count'])
        
        if all_times:
            self.log(f"\n🎯 OVERALL PERFORMANCE:")
            self.log(f"   Average across all operations: {statistics.mean(all_times):.2f} ms")
            self.log(f"   Total operations tested: {sum(r['count'] for r in self.results)}")
    
    def cleanup(self):
        """Clean up test data"""
        self.log("\n🧹 Cleaning up test data...")
        
        try:
            # Delete test questions (if any remain)
            deleted_questions = Question.objects.filter(
                event__name="Benchmark Test Event"
            ).delete()
            if deleted_questions[0] > 0:
                self.log(f"   Deleted {deleted_questions[0]} test questions")
            
            # Delete test event
            deleted_events = Event.objects.filter(name="Benchmark Test Event").delete()
            if deleted_events[0] > 0:
                self.log(f"   Deleted {deleted_events[0]} test events")
            
            # Note: Not deleting test user as it might be reused
            
        except Exception as e:
            self.log(f"⚠️ Cleanup warning: {str(e)}")


if __name__ == "__main__":
    benchmark = LatencyBenchmark()
    benchmark.run_benchmark()
