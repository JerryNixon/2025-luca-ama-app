#!/usr/bin/env python3
"""
Azure SQL Direct Performance Benchmark
Uses the same pyodbc connection that we confirmed works, bypassing Django ORM
This ensures fair performance comparison with Docker and Fabric
"""

import pyodbc
import time
import statistics
import os
from datetime import datetime

def get_azure_connection():
    """Get Azure SQL connection using the method we confirmed works"""
    server = 'luca-azure-ama.database.windows.net'
    database = 'luca_azure_ama'
    
    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server},1433;'
        f'DATABASE={database};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
        f'Connection Timeout=30;'
        f'Authentication=ActiveDirectoryInteractive;'
    )
    
    return pyodbc.connect(connection_string)

def benchmark_simple_queries(iterations=100):
    """Benchmark simple queries that match our Django tests"""
    print("🔄 Starting Azure SQL Direct Benchmark...")
    
    conn = get_azure_connection()
    cursor = conn.cursor()
    
    # Test 1: Simple SELECT 1 (connection latency)
    print("\n📊 Test 1: Simple SELECT 1 (Connection Latency)")
    latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        cursor.execute("SELECT 1 as test_value")
        result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        
        if i % 20 == 0:
            print(f"  Progress: {i}/{iterations} - Current: {latency_ms:.2f}ms")
    
    print(f"\n✅ SELECT 1 Results ({iterations} iterations):")
    print(f"  Average: {statistics.mean(latencies):.2f}ms")
    print(f"  Median: {statistics.median(latencies):.2f}ms")
    print(f"  Min: {min(latencies):.2f}ms")
    print(f"  Max: {max(latencies):.2f}ms")
    print(f"  Std Dev: {statistics.stdev(latencies):.2f}ms")
    
    # Test 2: Table existence check (realistic Django query)
    print("\n📊 Test 2: Table Existence Check")
    table_latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'django_migrations'
        """)
        result = cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        table_latencies.append(latency_ms)
        
        if i % 20 == 0:
            print(f"  Progress: {i}/{iterations} - Current: {latency_ms:.2f}ms")
    
    print(f"\n✅ Table Check Results ({iterations} iterations):")
    print(f"  Average: {statistics.mean(table_latencies):.2f}ms")
    print(f"  Median: {statistics.median(table_latencies):.2f}ms")
    print(f"  Min: {min(table_latencies):.2f}ms")
    print(f"  Max: {max(table_latencies):.2f}ms")
    print(f"  Std Dev: {statistics.stdev(table_latencies):.2f}ms")
    
    conn.close()
    
    return {
        'select_1': {
            'avg': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'min': min(latencies),
            'max': max(latencies),
            'std_dev': statistics.stdev(latencies)
        },
        'table_check': {
            'avg': statistics.mean(table_latencies),
            'median': statistics.median(table_latencies),
            'min': min(table_latencies),
            'max': max(table_latencies),
            'std_dev': statistics.stdev(table_latencies)
        }
    }

def save_results(results):
    """Save results to file for comparison"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"azure_sql_benchmark_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("Azure SQL Direct Performance Benchmark Results\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Database: Azure SQL (Serverless)\n")
        f.write(f"Connection: Direct pyodbc with ActiveDirectoryInteractive\n\n")
        
        f.write("SELECT 1 Results:\n")
        for key, value in results['select_1'].items():
            f.write(f"  {key}: {value:.2f}ms\n")
        
        f.write("\nTable Check Results:\n")
        for key, value in results['table_check'].items():
            f.write(f"  {key}: {value:.2f}ms\n")
    
    print(f"\n💾 Results saved to: {filename}")

if __name__ == "__main__":
    try:
        results = benchmark_simple_queries(100)
        save_results(results)
        print("\n🎉 Azure SQL benchmark completed successfully!")
        print("\nThis can be directly compared with Docker and Fabric results")
        print("since it uses the same raw SQL queries without Django ORM overhead")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you're authenticated with Azure CLI:")
        print("az login")
