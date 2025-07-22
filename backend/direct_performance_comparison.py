#!/usr/bin/env python3
"""
Direct Database Performance Comparison
Fabric SQL vs Azure SQL - Raw Connection Benchmarking
"""

import time
import statistics
import pyodbc
from datetime import datetime

# Connection configurations
FABRIC_SQL = {
    'name': 'Microsoft Fabric SQL',
    'connection_string': (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=x6eps4xrq2xudenlfv6naeo3i4-kb437xihomeu7pnyhpdwqylphe.msit-database.fabric.microsoft.com,1433;'
        'DATABASE=SQL-ama-b4e17cae-52ca-4187-8fa3-1c76c5beb29a;'
        'Authentication=ActiveDirectoryInteractive;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
}

AZURE_SQL = {
    'name': 'Azure SQL Database (Serverless)',
    'connection_string': (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=luca-azure-ama.database.windows.net,1433;'
        'DATABASE=luca_azure_ama;'
        'Authentication=ActiveDirectoryInteractive;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
}

def benchmark_database(db_config, test_name="Performance Test"):
    """Benchmark a specific database configuration"""
    
    print(f"\n🔍 Testing: {db_config['name']}")
    print("-" * 40)
    
    results = {
        'connection_times': [],
        'query_times': [],
        'total_time': 0,
        'errors': []
    }
    
    # Test connection time
    try:
        start_time = time.time()
        conn = pyodbc.connect(db_config['connection_string'])
        connection_time = time.time() - start_time
        results['connection_times'].append(connection_time)
        
        print(f"✅ Connection: {connection_time:.3f}s")
        
        cursor = conn.cursor()
        
        # Test basic queries
        test_queries = [
            ("Simple SELECT", "SELECT 1 as test"),
            ("Database info", "SELECT DB_NAME(), USER_NAME()"),
            ("System time", "SELECT GETDATE()"),
            ("Math operation", "SELECT 1+1, 2*3, 10/2"),
            ("String operation", "SELECT 'Hello' + ' ' + 'World'")
        ]
        
        for query_name, query in test_queries:
            try:
                start_time = time.time()
                cursor.execute(query)
                results_data = cursor.fetchall()
                query_time = time.time() - start_time
                
                results['query_times'].append(query_time)
                print(f"  {query_name}: {query_time:.3f}s")
                
            except Exception as e:
                results['errors'].append(f"{query_name}: {str(e)}")
                print(f"  ❌ {query_name}: {str(e)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        results['errors'].append(f"Connection: {str(e)}")
        print(f"❌ Connection failed: {str(e)}")
    
    return results

def compare_performance():
    """Compare performance between Fabric and Azure SQL"""
    
    print("🚀 Database Performance Comparison")
    print("=" * 50)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both databases
    fabric_results = benchmark_database(FABRIC_SQL, "Fabric SQL")
    azure_results = benchmark_database(AZURE_SQL, "Azure SQL")
    
    # Compare results
    print("\n📊 PERFORMANCE COMPARISON")
    print("=" * 50)
    
    # Connection time comparison
    if fabric_results['connection_times'] and azure_results['connection_times']:
        fabric_conn = fabric_results['connection_times'][0]
        azure_conn = azure_results['connection_times'][0]
        
        print(f"🔗 Connection Time:")
        print(f"  Fabric SQL:  {fabric_conn:.3f}s")
        print(f"  Azure SQL:   {azure_conn:.3f}s")
        
        if fabric_conn < azure_conn:
            diff = ((azure_conn - fabric_conn) / fabric_conn) * 100
            print(f"  🏆 Fabric SQL is {diff:.1f}% faster")
        else:
            diff = ((fabric_conn - azure_conn) / azure_conn) * 100
            print(f"  🏆 Azure SQL is {diff:.1f}% faster")
    
    # Query time comparison
    if fabric_results['query_times'] and azure_results['query_times']:
        fabric_avg = statistics.mean(fabric_results['query_times'])
        azure_avg = statistics.mean(azure_results['query_times'])
        
        print(f"\n⚡ Average Query Time:")
        print(f"  Fabric SQL:  {fabric_avg:.3f}s")
        print(f"  Azure SQL:   {azure_avg:.3f}s")
        
        if fabric_avg < azure_avg:
            diff = ((azure_avg - fabric_avg) / fabric_avg) * 100
            print(f"  🏆 Fabric SQL is {diff:.1f}% faster")
        else:
            diff = ((fabric_avg - azure_avg) / azure_avg) * 100
            print(f"  🏆 Azure SQL is {diff:.1f}% faster")
    
    # Error summary
    total_errors = len(fabric_results['errors']) + len(azure_results['errors'])
    if total_errors > 0:
        print(f"\n⚠️ Errors encountered: {total_errors}")
        for error in fabric_results['errors']:
            print(f"  Fabric: {error}")
        for error in azure_results['errors']:
            print(f"  Azure: {error}")
    else:
        print(f"\n✅ No errors - both databases working perfectly!")
    
    return fabric_results, azure_results

if __name__ == "__main__":
    fabric_results, azure_results = compare_performance()
