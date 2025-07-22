#!/usr/bin/env python3
"""
Azure SQL - Create SQL Authentication User
This script uses our working Azure AD connection to create a SQL user for Django
"""

import pyodbc
import secrets
import string

def create_sql_user():
    """Create a SQL authentication user in Azure SQL"""
    
    # Use our working Azure AD connection
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=luca-azure-ama.database.windows.net,1433;'
        'DATABASE=luca_azure_ama;'
        'Authentication=ActiveDirectoryInteractive;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
    
    # Generate a secure password
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    sql_password = ''.join(secrets.choice(characters) for _ in range(16))
    sql_username = 'django_user'
    
    try:
        print("🔄 Connecting to Azure SQL with Azure AD...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Check if user already exists
        cursor.execute("""
            SELECT name FROM sys.database_principals 
            WHERE name = ? AND type = 'S'
        """, sql_username)
        
        if cursor.fetchone():
            print(f"⚠️ User '{sql_username}' already exists")
            
            # Drop existing user
            cursor.execute(f"DROP USER [{sql_username}]")
            print(f"🗑️ Dropped existing user '{sql_username}'")
        
        # Create SQL authentication user
        create_user_sql = f"""
            CREATE USER [{sql_username}] 
            WITH PASSWORD = '{sql_password}'
        """
        
        cursor.execute(create_user_sql)
        print(f"👤 Created SQL user: {sql_username}")
        
        # Grant necessary permissions for Django
        permissions = [
            f"ALTER ROLE db_datareader ADD MEMBER [{sql_username}]",
            f"ALTER ROLE db_datawriter ADD MEMBER [{sql_username}]",
            f"ALTER ROLE db_ddladmin ADD MEMBER [{sql_username}]",  # For migrations
        ]
        
        for permission in permissions:
            cursor.execute(permission)
            print(f"🔑 Granted permission: {permission.split('ADD')[0].split('db_')[1]}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎯 SUCCESS! SQL Authentication User Created")
        print("=" * 50)
        print(f"👤 Username: {sql_username}")
        print(f"🔐 Password: {sql_password}")
        print("\n📋 Django Configuration:")
        print("DATABASES = {")
        print("    'default': {")
        print("        'ENGINE': 'mssql',")
        print("        'NAME': 'luca_azure_ama',")
        print(f"        'USER': '{sql_username}',")
        print(f"        'PASSWORD': '{sql_password}',")
        print("        'HOST': 'luca-azure-ama.database.windows.net',")
        print("        'PORT': '1433',")
        print("        'OPTIONS': {")
        print("            'driver': 'ODBC Driver 17 for SQL Server',")
        print("            'extra_params': 'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'")
        print("        },")
        print("    }")
        print("}")
        
        return sql_username, sql_password
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None

if __name__ == "__main__":
    print("🔧 Azure SQL - SQL Authentication User Creator")
    print("=" * 50)
    
    username, password = create_sql_user()
    
    if username and password:
        print(f"\n🎉 Ready for Django testing!")
        print("Next steps:")
        print("1. Update your Django settings with the credentials above")
        print("2. Test Django connection")
        print("3. Run performance benchmarks")
    else:
        print("\n❌ Failed to create SQL user")
        print("You may need to check Azure SQL authentication settings")
