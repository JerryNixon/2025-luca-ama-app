#!/usr/bin/env python
"""
Fix Azure SQL Django Migrations Issue
=====================================
Recreate django_migrations table with compatible data types
"""

import pyodbc

def fix_migrations_table():
    """Fix the django_migrations table ODBC compatibility issue"""
    
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=luca-azure-ama.database.windows.net,1433;"
        "DATABASE=luca_azure_ama;"
        "Authentication=ActiveDirectoryInteractive;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30"
    )
    
    try:
        print("🔗 Connecting to Azure SQL...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("🗑️ Dropping existing django_migrations table...")
        cursor.execute("DROP TABLE IF EXISTS django_migrations")
        conn.commit()
        
        print("✨ Creating new compatible django_migrations table...")
        cursor.execute("""
            CREATE TABLE django_migrations (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                app NVARCHAR(255) NOT NULL,
                name NVARCHAR(255) NOT NULL,
                applied DATETIME2 DEFAULT GETDATE()
            )
        """)
        conn.commit()
        
        print("📥 Adding essential migration records...")
        # Add the core Django migrations
        essential_migrations = [
            ('contenttypes', '0001_initial'),
            ('auth', '0001_initial'),
            ('admin', '0001_initial'),
            ('api', '0001_initial'),
            ('sessions', '0001_initial'),
        ]
        
        for app, migration in essential_migrations:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES (?, ?, GETDATE())
            """, app, migration)
        
        conn.commit()
        print(f"✅ Added {len(essential_migrations)} essential migration records")
        
        cursor.close()
        conn.close()
        print("🎉 Django migrations table fixed and ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_migrations_table()
