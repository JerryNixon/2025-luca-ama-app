#!/usr/bin/env python3
"""
Azure SQL Performance Benchmark - Django ORM
Matches the exact same tests we ran on Docker and Fabric for fair comparison
"""

import os
import sys
import django
import time
import statistics
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings for Azure SQL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azure_sql_settings')

# Setup Django
django.setup()

from django.db import connection
from django.contrib.auth.models import User as DjangoUser
from api.models import User, Event, Question, Vote


def benchmark_azure_sql_performance(iterations=100):
    """
    Run the EXACT same Django ORM performance tests we used for Docker/Fabric
    """
    print("🚀 Azure SQL Django ORM Performance Benchmark")
    print("=" * 60)
    print(f"📊 Running {iterations} iterations of each test")
    print(f"🔗 Database: {connection.settings_dict['NAME']}")
    print(f"🏢 Server: {connection.settings_dict['HOST']}")
    print(f"🔧 Engine: {connection.settings_dict['ENGINE']}")
    print()

    results = {}

    # Test 1: Simple Database Connection (SELECT 1)
    print("📋 Test 1: Database Connection Latency")
    latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        
        if i % 20 == 0:
            print(f"  Progress: {i}/{iterations} - Current: {latency_ms:.2f}ms")
    
    results['connection'] = {
        'avg': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0
    }
    
    print(f"✅ Connection Results: Avg={results['connection']['avg']:.2f}ms, "
          f"Min={results['connection']['min']:.2f}ms, Max={results['connection']['max']:.2f}ms")
    print()

    # Test 2: Information Schema Query (Database-agnostic)
    print("📋 Test 2: Information Schema Query Latency")
    model_latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        model_latencies.append(latency_ms)
        
        if i % 20 == 0:
            print(f"  Progress: {i}/{iterations} - Current: {latency_ms:.2f}ms")
    
    results['model_query'] = {
        'avg': statistics.mean(model_latencies),
        'median': statistics.median(model_latencies),
        'min': min(model_latencies),
        'max': max(model_latencies),
        'std_dev': statistics.stdev(model_latencies) if len(model_latencies) > 1 else 0
    }
    
    print(f"✅ Model Query Results: Avg={results['model_query']['avg']:.2f}ms, "
          f"Min={results['model_query']['min']:.2f}ms, Max={results['model_query']['max']:.2f}ms")
    print()

    # Test 3: System Database Query
    print("📋 Test 3: System Database Query Latency")
    complex_latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.name AS schema_name,
                    t.name AS table_name,
                    c.name AS column_name
                FROM sys.schemas s
                INNER JOIN sys.tables t ON s.schema_id = t.schema_id
                INNER JOIN sys.columns c ON t.object_id = c.object_id
                WHERE s.name = 'dbo'
                ORDER BY t.name, c.column_id
            """)
            query_results = cursor.fetchmany(10)  # Get first 10 rows
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        complex_latencies.append(latency_ms)
        
        if i % 20 == 0:
            print(f"  Progress: {i}/{iterations} - Current: {latency_ms:.2f}ms")
    
    results['complex_query'] = {
        'avg': statistics.mean(complex_latencies),
        'median': statistics.median(complex_latencies),
        'min': min(complex_latencies),
        'max': max(complex_latencies),
        'std_dev': statistics.stdev(complex_latencies) if len(complex_latencies) > 1 else 0
    }
    
    print(f"✅ Complex Query Results: Avg={results['complex_query']['avg']:.2f}ms, "
          f"Min={results['complex_query']['min']:.2f}ms, Max={results['complex_query']['max']:.2f}ms")
    print()

    return results


def save_benchmark_results(results):
    """Save results for comparison with Docker and Fabric"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"azure_sql_django_benchmark_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("Azure SQL Django ORM Performance Benchmark Results\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Database: Azure SQL Database (Serverless)\n")
        f.write(f"Connection: Django ORM with azure_mssql_backend\n")
        f.write(f"Authentication: ActiveDirectoryInteractive\n\n")
        
        for test_name, metrics in results.items():
            f.write(f"{test_name.replace('_', ' ').title()} Results:\n")
            for metric, value in metrics.items():
                f.write(f"  {metric}: {value:.2f}ms\n")
            f.write("\n")
    
    print(f"💾 Results saved to: {filename}")
    return filename


def print_comparison_summary(results):
    """Print summary for easy comparison with Docker/Fabric results"""
    print("\n🎯 AZURE SQL PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"Connection Latency:    {results['connection']['avg']:.2f}ms (avg)")
    print(f"Model Query Latency:   {results['model_query']['avg']:.2f}ms (avg)")
    print(f"Complex Query Latency: {results['complex_query']['avg']:.2f}ms (avg)")
    print()
    print("📊 Compare these results with your Docker and Fabric benchmarks!")
    print("🔍 Look for the platform with the HIGHEST latency as requested.")


if __name__ == "__main__":
    try:
        print("🔄 Starting Azure SQL Django ORM benchmark...")
        results = benchmark_azure_sql_performance(100)
        
        filename = save_benchmark_results(results)
        print_comparison_summary(results)
        
        print(f"\n🎉 Azure SQL benchmark completed!")
        print(f"📁 Results saved to: {filename}")
        print("\nNow you can compare latency across all three platforms:")
        print("  • Docker SQL Server")
        print("  • Microsoft Fabric SQL") 
        print("  • Azure SQL Database (Serverless)")
        
    except Exception as e:
        print(f"❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
