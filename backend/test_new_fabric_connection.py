"""
Test connection to NEW Fabric SQL workspace (jnixon-luca-workspace)
This script tests the connection to the SQL-ama database using Azure AD authentication.
"""
import os
import sys
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_new_fabric_connection():
    """Test connection to the new Fabric SQL workspace"""
    
    print("🔗 Testing NEW Fabric SQL Connection (jnixon-luca-workspace)")
    print("=" * 60)
    
    # Connection parameters from .env
    server = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME') 
    username = os.getenv('DB_USER')
    
    print(f"Server: {server}")
    print(f"Database: {database}")
    print(f"User: {username}")
    print()
    
    # Build connection string for Azure AD Interactive authentication
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"Authentication=ActiveDirectoryInteractive;"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"ConnectTimeout=30"
    )
    
    try:
        print("🔐 Attempting Azure AD Interactive authentication...")
        print("   (A browser window may open for Microsoft login)")
        
        # Connect to database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("✅ Connected successfully to NEW Fabric SQL workspace!")
        print()
        
        # Test basic query
        print("📊 Testing basic query...")
        cursor.execute("SELECT @@VERSION as version, DB_NAME() as database_name")
        result = cursor.fetchone()
        
        print(f"   Database: {result.database_name}")
        print(f"   Version: {result.version[:50]}...")
        print()
        
        # List existing tables
        print("📋 Checking existing tables...")
        cursor.execute("""
            SELECT TABLE_NAME, TABLE_TYPE 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("   Existing tables:")
            for table in tables:
                print(f"   - {table.TABLE_NAME}")
        else:
            print("   No tables found (this is normal for a new database)")
        
        print()
        print("🎉 NEW Fabric SQL connection test SUCCESSFUL!")
        print("   Your Django app can now connect to this workspace.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except pyodbc.Error as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("🔧 Troubleshooting tips:")
        print("   1. Make sure you're logged into Microsoft with t-lucahadife@microsoft.com")
        print("   2. Check that you have access to jnixon-luca-workspace")
        print("   3. Verify the server name in your Fabric workspace")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_new_fabric_connection()
