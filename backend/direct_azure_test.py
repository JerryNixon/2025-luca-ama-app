#!/usr/bin/env python3
"""
Direct Azure SQL Connection Test
Uses pyodbc directly without Django to test the connection
"""

import pyodbc

def test_direct_connection():
    """Test direct connection to Azure SQL using pyodbc"""
    
    # Connection parameters from your ADO.NET string
    server = 'luca-azure-ama.database.windows.net'
    database = 'luca_azure_ama'
    username = 'CloudSA397da94b'
    password = 'SummerHadouf2004*'
    
    # Try different drivers
    drivers_to_test = [
        'ODBC Driver 17 for SQL Server',
        'SQL Server'
    ]
    
    for driver in drivers_to_test:
        print(f"\n🔍 Testing with driver: {driver}")
        
        # Build connection string exactly like Azure's ADO.NET format
        connection_string = (
            f'DRIVER={{{driver}}};'
            f'SERVER={server},1433;'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            f'Encrypt=yes;'
            f'TrustServerCertificate=no;'
            f'Connection Timeout=30;'
            f'MultipleActiveResultSets=False;'
            f'Persist Security Info=False;'
        )
        
        try:
            print(f"🔄 Connecting to Azure SQL...")
            conn = pyodbc.connect(connection_string)
            
            print(f"✅ SUCCESS: Connected with {driver}")
            
            # Test a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test, @@VERSION as version")
            row = cursor.fetchone()
            
            print(f"📊 Test query result: {row[0]}")
            print(f"🗄️ SQL Server version: {row[1][:100]}...")
            
            cursor.close()
            conn.close()
            
            print(f"🎯 SOLUTION FOUND: Use driver '{driver}' in Django")
            return driver
            
        except Exception as e:
            print(f"❌ FAILED with {driver}: {str(e)}")
            
            # Parse common error types
            error_str = str(e)
            if "Login failed" in error_str:
                print("💡 Issue: Invalid username or password")
            elif "timeout" in error_str.lower():
                print("💡 Issue: Connection timeout - check firewall")
            elif "certificate" in error_str.lower():
                print("💡 Issue: SSL certificate problem")
            elif "network" in error_str.lower():
                print("💡 Issue: Network connectivity problem")
    
    return None

if __name__ == "__main__":
    print("🔗 Direct Azure SQL Connection Test")
    print("=" * 40)
    
    working_driver = test_direct_connection()
    
    print("\n" + "=" * 40)
    if working_driver:
        print(f"✅ SUCCESS: Connection works with '{working_driver}'")
        print("\n🎯 Next steps:")
        print("1. Update Django settings to use this driver")
        print("2. Test Django connection")
        print("3. Run migrations")
    else:
        print("❌ No working connection found")
        print("\n🔧 Troubleshooting needed:")
        print("1. Check Azure SQL firewall settings")
        print("2. Verify username/password")
        print("3. Check if database is paused (serverless)")
