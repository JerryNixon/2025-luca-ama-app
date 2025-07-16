#!/usr/bin/env python3
"""
Azure SQL Database Connection Test

Tests connection to Azure SQL Database (Serverless) and provides
detailed connection information and basic performance metrics.

Usage:
    python test_azure_sql_connection.py
"""

import os
import sys
import time
import statistics
from datetime import datetime

# Add backend to path for Django imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Set Django settings for Azure SQL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azure_sql_settings')

try:
    import django
    django.setup()
    
    from django.db import connection
    from django.core.management import execute_from_command_line
    
except ImportError as e:
    print(f"❌ Django import error: {e}")
    print("💡 Make sure you're in the backend directory and Django is installed")
    sys.exit(1)

def test_basic_connection():
    """Test basic database connection"""
    print("🔍 Testing Basic Connection...")
    print("-" * 40)
    
    try:
        start_time = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
        end_time = time.perf_counter()
        
        connection_time = (end_time - start_time) * 1000
        
        print(f"✅ Connection successful!")
        print(f"📊 Connection time: {connection_time:.2f}ms")
        print(f"🔢 Test query result: {result[0]}")
        
        return True, connection_time
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, None

def get_database_info():
    """Get Azure SQL Database information"""
    print("\n🏢 Database Information...")
    print("-" * 40)
    
    try:
        with connection.cursor() as cursor:
            # Database version and edition
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            
            # Database name and server
            cursor.execute("SELECT DB_NAME(), @@SERVERNAME")
            db_info = cursor.fetchone()
            
            # Service objective (pricing tier)
            cursor.execute("""
                SELECT 
                    DATABASEPROPERTYEX(DB_NAME(), 'ServiceObjective') as service_objective,
                    DATABASEPROPERTYEX(DB_NAME(), 'Edition') as edition
            """)
            tier_info = cursor.fetchone()
            
            print(f"📊 Database: {db_info[0]}")
            print(f"🏢 Server: {db_info[1]}")
            print(f"💰 Edition: {tier_info[1]}")
            print(f"⚡ Service Tier: {tier_info[0]}")
            print(f"🔧 Version: {version.split(' - ')[0]}")
            
    except Exception as e:
        print(f"❌ Failed to get database info: {e}")

def test_crud_performance():
    """Test basic CRUD operation performance"""
    print("\n⚡ CRUD Performance Test...")
    print("-" * 40)
    
    times = {
        'select': [],
        'insert': [],
        'update': [],
        'delete': []
    }
    
    try:
        with connection.cursor() as cursor:
            # Create test table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='azure_sql_test' AND xtype='U')
                CREATE TABLE azure_sql_test (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    test_data NVARCHAR(100),
                    created_at DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            # Test INSERT operations
            for i in range(5):
                start_time = time.perf_counter()
                cursor.execute(
                    "INSERT INTO azure_sql_test (test_data) VALUES (?)",
                    [f"Test data {i}"]
                )
                end_time = time.perf_counter()
                times['insert'].append((end_time - start_time) * 1000)
            
            # Test SELECT operations
            for i in range(5):
                start_time = time.perf_counter()
                cursor.execute("SELECT TOP 10 * FROM azure_sql_test")
                results = cursor.fetchall()
                end_time = time.perf_counter()
                times['select'].append((end_time - start_time) * 1000)
            
            # Test UPDATE operations
            for i in range(5):
                start_time = time.perf_counter()
                cursor.execute(
                    "UPDATE azure_sql_test SET test_data = ? WHERE id = ?",
                    [f"Updated data {i}", i + 1]
                )
                end_time = time.perf_counter()
                times['update'].append((end_time - start_time) * 1000)
            
            # Test DELETE operations
            for i in range(5):
                start_time = time.perf_counter()
                cursor.execute("DELETE FROM azure_sql_test WHERE id = ?", [i + 1])
                end_time = time.perf_counter()
                times['delete'].append((end_time - start_time) * 1000)
            
            # Clean up
            cursor.execute("DROP TABLE azure_sql_test")
            
        # Display results
        print("📊 Performance Results (5 operations each):")
        for operation, operation_times in times.items():
            if operation_times:
                avg_time = statistics.mean(operation_times)
                min_time = min(operation_times)
                max_time = max(operation_times)
                print(f"   {operation.upper():6}: Avg {avg_time:6.2f}ms | Min {min_time:6.2f}ms | Max {max_time:6.2f}ms")
        
        return times
        
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        return None

def check_serverless_status():
    """Check if database is in serverless mode and its status"""
    print("\n🔄 Serverless Status Check...")
    print("-" * 40)
    
    try:
        with connection.cursor() as cursor:
            # Check database status
            cursor.execute("""
                SELECT 
                    name,
                    state_desc,
                    user_access_desc
                FROM sys.databases 
                WHERE name = DB_NAME()
            """)
            status = cursor.fetchone()
            
            if status:
                print(f"📊 Database Status: {status[1]}")
                print(f"👥 User Access: {status[2]}")
                
                if status[1] == 'ONLINE':
                    print("✅ Database is active and ready")
                elif status[1] == 'PAUSED':
                    print("⏸️  Database is paused (serverless auto-pause)")
                    print("💡 First query may have higher latency due to resume")
            
    except Exception as e:
        print(f"❌ Failed to check serverless status: {e}")

def main():
    """Main test function"""
    print("🔵 Azure SQL Database (Serverless) Connection Test")
    print("=" * 60)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: {os.environ.get('DATABASE_TYPE', 'Unknown')}")
    
    # Test basic connection
    connection_success, connection_time = test_basic_connection()
    
    if not connection_success:
        print("\n❌ Cannot proceed with further tests due to connection failure")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Verify Azure SQL Database is created and running")
        print("   2. Check firewall rules allow your IP address")
        print("   3. Verify connection string in .env.azure_sql")
        print("   4. Ensure database is not paused (serverless)")
        return
    
    # Get database information
    get_database_info()
    
    # Check serverless status
    check_serverless_status()
    
    # Test CRUD performance
    crud_times = test_crud_performance()
    
    # Summary
    print("\n📈 Test Summary")
    print("=" * 40)
    print(f"✅ Connection: Successful ({connection_time:.2f}ms)")
    
    if crud_times:
        all_times = []
        for times_list in crud_times.values():
            all_times.extend(times_list)
        
        if all_times:
            avg_crud = statistics.mean(all_times)
            print(f"⚡ Average CRUD: {avg_crud:.2f}ms")
            
            # Performance assessment
            if avg_crud < 50:
                print("🚀 Performance: Excellent")
            elif avg_crud < 100:
                print("✅ Performance: Good") 
            elif avg_crud < 200:
                print("⚠️  Performance: Moderate")
            else:
                print("🐌 Performance: Needs optimization")
    
    print(f"\n⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Next Steps:")
    print("   1. Run Django migrations: python manage.py migrate")
    print("   2. Create test data: python manage.py shell")
    print("   3. Run performance benchmarks")
    print("   4. Compare with Docker and Fabric results")

if __name__ == "__main__":
    main()
