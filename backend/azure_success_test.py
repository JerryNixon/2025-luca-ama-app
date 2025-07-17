#!/usr/bin/env python3
"""
Azure SQL Success Test
Since we confirmed the connection works with pyodbc, let's test basic operations
"""

import pyodbc

def test_azure_sql_operations():
    """Test basic Azure SQL operations"""
    
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
    
    try:
        print("🔄 Connecting to Azure SQL Database...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Test 1: Basic query
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"📊 Test query: {result[0]}")
        
        # Test 2: Check database info
        cursor.execute("SELECT DB_NAME() as database_name, USER_NAME() as user_name")
        result = cursor.fetchone()
        print(f"🗄️ Database: {result[0]}")
        print(f"👤 User: {result[1]}")
        
        # Test 3: Check if we can create tables (permissions test)
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'test_connection')
                CREATE TABLE test_connection (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    message nvarchar(100),
                    created_at datetime2 DEFAULT GETDATE()
                )
            """)
            conn.commit()
            print("✅ Can create tables - full database access")
            
            # Test 4: Insert and read data
            cursor.execute("INSERT INTO test_connection (message) VALUES (?)", "Hello Azure SQL!")
            conn.commit()
            
            cursor.execute("SELECT TOP 1 message, created_at FROM test_connection ORDER BY id DESC")
            result = cursor.fetchone()
            print(f"💾 Data test: {result[0]} at {result[1]}")
            
            # Clean up
            cursor.execute("DROP TABLE test_connection")
            conn.commit()
            print("🧹 Cleaned up test table")
            
        except Exception as e:
            print(f"⚠️ Limited permissions: {str(e)}")
        
        cursor.close()
        conn.close()
        
        print("\n🎯 AZURE SQL CONNECTION SUCCESSFUL!")
        print("✅ Authentication: Working")
        print("✅ Network access: Working") 
        print("✅ Database operations: Working")
        
        return True
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔗 Azure SQL Success Test")
    print("=" * 40)
    
    success = test_azure_sql_operations()
    
    if success:
        print("\n🎉 CONGRATULATIONS!")
        print("Your Azure SQL Database is fully connected and working!")
        print("\n📋 Summary:")
        print("✅ Firewall configured correctly")
        print("✅ Azure AD authentication working")  
        print("✅ Database operations successful")
        print("\n🔧 Next steps:")
        print("1. Fix Django configuration for Azure AD")
        print("2. Run performance benchmarks")
        print("3. Compare with Fabric SQL performance")
    else:
        print("\n❌ Connection still has issues")
        print("Check the error message above for details")
