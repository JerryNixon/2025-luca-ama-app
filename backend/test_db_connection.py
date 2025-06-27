"""
Test script for Fabric SQL Database connection with certificate authentication.
Run this after placing the certificate file in the backend directory.
"""

import pyodbc
import os
from dotenv import load_dotenv

def test_certificate_connection():
    load_dotenv()
    
    server = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    cert_path = os.getenv('DB_CERT_PATH')
    
    print(f"Testing connection to: {server}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print(f"Certificate: {cert_path}")
    
    # Check if certificate file exists
    if not os.path.exists(cert_path):
        print(f"ERROR: Certificate file not found: {cert_path}")
        print("Please copy the .pfx file to the backend directory")
        return False
    
    # Test different authentication methods
    auth_methods = [
        # Method 1: ActiveDirectoryIntegrated (might work if cert is installed)
        {
            "name": "ActiveDirectoryIntegrated",
            "conn_str": f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},1433;DATABASE={database};Authentication=ActiveDirectoryIntegrated;Encrypt=yes;TrustServerCertificate=yes;"
        },
        # Method 2: ActiveDirectoryInteractive (might prompt for auth)
        {
            "name": "ActiveDirectoryInteractive", 
            "conn_str": f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},1433;DATABASE={database};Authentication=ActiveDirectoryInteractive;Encrypt=yes;TrustServerCertificate=yes;"
        },
        # Method 3: Try without explicit authentication (Windows auth)
        {
            "name": "Windows Authentication",
            "conn_str": f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},1433;DATABASE={database};Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;"
        }
    ]
    
    for method in auth_methods:
        try:
            print(f"\n🔄 Trying {method['name']}...")
            conn = pyodbc.connect(method['conn_str'])
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test, GETDATE() as current_time")
            result = cursor.fetchone()
            print(f"✅ {method['name']} successful! Result: {result}")
            
            # Test if we can see our tables
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables in database:")
            for table in tables[:5]:  # Show first 5 tables
                print(f"  - {table[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ {method['name']} failed: {e}")
            continue
    
    print(f"\n🔧 All authentication methods failed. Additional steps:")
    print("1. Install the certificate in Windows Certificate Store:")
    print(f"   Import-PfxCertificate -FilePath '{cert_path}' -CertStoreLocation Cert:\\CurrentUser\\My")
    print("2. Make sure you're connected to Microsoft internal network/VPN")
    print("3. The certificate might need a password - check with your admin")
    return False

if __name__ == "__main__":
    test_certificate_connection()
