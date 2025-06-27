"""
Simple test to verify Fabric SQL connection is working.
Run this to check your database connection.
"""

import pyodbc
import os
from dotenv import load_dotenv

def test_connection():
    # Load environment variables
    load_dotenv()
    
    print("🔍 Testing Fabric SQL Database Connection")
    print("=" * 50)
    
    # Get connection details from .env
    server = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    port = os.getenv('DB_PORT', '1433')
    
    print(f"📋 Connection Details:")
    print(f"   Server: {server}")
    print(f"   Database: {database}")
    print(f"   Username: {username}")
    print(f"   Port: {port}")
    print()
    
    try:
        # Build connection string
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};Authentication=ActiveDirectoryInteractive;Encrypt=yes;TrustServerCertificate=no"
        
        print("🔄 Attempting to connect...")
        print("   (You may see a login prompt - use your certificate credentials)")
        
        # Connect to database
        conn = pyodbc.connect(conn_str)
        print("✅ Successfully connected to Fabric SQL!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test, GETDATE() as timestamp")
        result = cursor.fetchone()
        print(f"✅ Test query successful: {result}")
        
        # Check what tables exist
        print("\n📋 Checking your tables...")
        cursor.execute("SELECT name FROM sys.tables WHERE type = 'U' ORDER BY name")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
                
            # Test a sample query from one of your tables
            if tables:
                sample_table = tables[0][0]
                print(f"\n📊 Sample data from '{sample_table}':")
                cursor.execute(f"SELECT TOP 3 * FROM [{sample_table}]")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"   {row}")
        else:
            print("ℹ️  No user tables found in database")
        
        # Close connection
        conn.close()
        print("\n🎉 Connection test successful! Your Fabric SQL database is ready.")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure you're connected to Microsoft VPN or corporate network")
        print("2. Verify the certificate is installed correctly")
        print("3. Check if you have permissions to access the Fabric SQL database")
        print("4. Try running this script as administrator")
        return False

if __name__ == "__main__":
    test_connection()
