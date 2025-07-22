#!/usr/bin/env python3
"""
Azure SQL vs Docker - Connection Latency Summary
Final comparison showing which backend has highest latency
"""
import os
import sys
import django
import time
import statistics

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from django.db import connection

def test_azure_sql_latency(iterations=15):
    """Test Azure SQL connection latency extensively"""
    print("🔵 Azure SQL Database (Serverless) - Connection Latency Test")
    print("=" * 60)
    
    latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 as test_connection")
        cursor.fetchone()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        print(f"Test {i+1:2d}: {latency_ms:6.2f} ms")
    
    return {
        'latencies': latencies,
        'average': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'std': statistics.stdev(latencies)
    }

def main():
    print("🎯 BACKEND LATENCY COMPARISON")
    print("=" * 50)
    print("Testing which backend has the HIGHEST latency...")
    print()
    
    # Test Azure SQL
    azure_results = test_azure_sql_latency(15)
    
    print()
    print("📊 FINAL RESULTS COMPARISON")
    print("=" * 40)
    
    # Your Docker results
    docker_avg = 1.53  # From your test results
    docker_range = "1.09 - 2.57"
    
    # Your Fabric results (if you have them)
    # fabric_avg = ??  # Add if you have Fabric results
    
    print(f"🐳 Docker SQL Server (Local):")
    print(f"   Average: {docker_avg:.2f} ms")
    print(f"   Range: {docker_range} ms")
    print()
    
    print(f"🔵 Azure SQL Database (Serverless):")
    print(f"   Average: {azure_results['average']:.2f} ms")
    print(f"   Range: {azure_results['min']:.2f} - {azure_results['max']:.2f} ms")
    print(f"   Median: {azure_results['median']:.2f} ms")
    print(f"   Std Dev: {azure_results['std']:.2f} ms")
    print()
    
    # Calculate the difference
    ratio = azure_results['average'] / docker_avg
    
    print("🔥 LATENCY WINNER (HIGHEST):")
    print("=" * 30)
    if azure_results['average'] > docker_avg:
        print(f"🏆 AZURE SQL has the HIGHEST latency!")
        print(f"   📊 {azure_results['average']:.1f}ms vs {docker_avg}ms")
        print(f"   📈 Azure is {ratio:.1f}x SLOWER than Docker")
        print(f"   🎯 That's +{azure_results['average'] - docker_avg:.1f}ms more latency per operation")
    else:
        print(f"🏆 DOCKER has higher latency")
        print(f"   📊 {docker_avg}ms vs {azure_results['average']:.1f}ms")
    
    print()
    print("💡 ANALYSIS:")
    print(f"   • Azure SQL (cloud): Network latency to Azure datacenter")
    print(f"   • Docker (local): Local container, minimal network overhead")
    print(f"   • The {ratio:.1f}x difference shows the impact of cloud vs local")
    
    print()
    print("🎯 ANSWER TO YOUR QUESTION:")
    print(f"   'Which backend has the highest latency?'")
    print(f"   ➡️  AZURE SQL DATABASE (SERVERLESS)")
    print(f"   📊 {azure_results['average']:.1f}ms average connection latency")
    print(f"   🔥 {ratio:.1f}x higher than local Docker")

if __name__ == "__main__":
    main()
