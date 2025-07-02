"""
Test script for NEW Fabric SQL connection (jnixon-luca-workspace)
Using: t-lucahadife@microsoft.com with Azure AD Interactive authentication
Database: SQL-ama-b4e17cae-52ca-4187-8fa3-1c76c5beb29a
"""

import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_new_fabric_connection():
    """Test connection to new Fabric SQL workspace (jnixon-luca-workspace)"""
    
    print("🔧 Testing NEW Fabric SQL Connection...")
    print("=" * 60)
    
    # Connection parameters from .env
    server = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    port = os.getenv('DB_PORT', '1433')
    username = os.getenv('DB_USER')
    
    print(f"🏢 Server: {server}")
    print(f"🗄️  Database: {database}")
    print(f"🚪 Port: {port}")
    print(f"👤 User: {username}")
    print(f"🔐 Auth: Azure AD Interactive")
    print("-" * 60)
    
    try:
        # Build connection string for Azure AD Interactive
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"Authentication=ActiveDirectoryInteractive;"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"ConnectTimeout=30;"
            f"MultipleActiveResultSets=False"
        )
        
        print("🔌 Attempting connection...")
        print(f"📝 Connection string: {connection_string}")
        print()
        
        # This will open Azure AD login popup
        print("🪟 Azure AD login popup should appear...")
        print("   Please login with: t-lucahadife@microsoft.com")
        print()
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("✅ CONNECTION SUCCESSFUL!")
        print()
        
        # Test basic query
        print("🧪 Testing basic query...")
        cursor.execute("SELECT @@VERSION as Version, DB_NAME() as DatabaseName")
        result = cursor.fetchone()
        
        print(f"📊 Database Version: {result.Version}")
        print(f"🗄️  Current Database: {result.DatabaseName}")
        print()
        
        # List all tables
        print("📋 Listing all tables in database...")
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
            FROM INFORMATION_SCHEMA.TABLES 
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"   📊 {table.TABLE_SCHEMA}.{table.TABLE_NAME} ({table.TABLE_TYPE})")
        else:
            print("   ℹ️  No tables found (database is empty)")
        
        print()
        print("🎉 NEW FABRIC CONNECTION TEST COMPLETED SUCCESSFULLY!")
        print("🚀 Your Django app can now connect to the new workspace!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except pyodbc.Error as e:
        print(f"❌ Database connection failed!")
        print(f"🔍 Error details: {str(e)}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Make sure you're logged into Azure with t-lucahadife@microsoft.com")
        print("   2. Check if you have access to jnixon-luca-workspace")
        print("   3. Verify the connection string details")
        print("   4. Try running: az login")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_new_fabric_connection()
