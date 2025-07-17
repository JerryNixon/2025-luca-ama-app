#!/usr/bin/env python3
"""
Azure AD Authentication Test for Azure SQL
"""

import pyodbc

def test_azure_ad_connection():
    """Test Azure AD authentication methods"""
    
    server = 'luca-azure-ama.database.windows.net'
    database = 'luca_azure_ama'
    
    # Test different Azure AD authentication methods
    auth_methods = [
        {
            'name': 'Active Directory Interactive',
            'connection_string': (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={server},1433;'
                f'DATABASE={database};'
                f'Encrypt=yes;'
                f'TrustServerCertificate=no;'
                f'Connection Timeout=30;'
                f'Authentication=ActiveDirectoryInteractive;'
            )
        },
        {
            'name': 'Active Directory Default',
            'connection_string': (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={server},1433;'
                f'DATABASE={database};'
                f'Encrypt=yes;'
                f'TrustServerCertificate=no;'
                f'Connection Timeout=30;'
                f'Authentication=ActiveDirectoryDefault;'
            )
        }
    ]
    
    for method in auth_methods:
        print(f"\n🔍 Testing: {method['name']}")
        print(f"🔄 This may open a browser window for authentication...")
        
        try:
            conn = pyodbc.connect(method['connection_string'])
            
            print(f"✅ SUCCESS: Connected with {method['name']}")
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test, USER_NAME() as current_user")
            row = cursor.fetchone()
            
            print(f"📊 Test result: {row[0]}")
            print(f"👤 Current user: {row[1]}")
            
            cursor.close()
            conn.close()
            
            return method['name']
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("🔐 Azure AD Authentication Test")
    print("=" * 40)
    print("💡 This will test Azure AD authentication")
    print("💡 You may need to sign in to your Microsoft account")
    
    working_method = test_azure_ad_connection()
    
    print("\n" + "=" * 40)
    if working_method:
        print(f"✅ SUCCESS: {working_method} works!")
        print("\n🎯 Next steps:")
        print("1. Update Django settings for Azure AD auth")
        print("2. Configure environment variables")
    else:
        print("❌ Azure AD authentication failed")
        print("💡 You may need to configure Azure SQL to allow your account")
