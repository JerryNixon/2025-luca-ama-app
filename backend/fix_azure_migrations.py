#!/usr/bin/env python
"""
Fix Azure SQL ODBC Type Issue
=============================
This script fixes the ODBC SQL type -155 issue by recreating the django_migrations table
with compatible data types.
"""

import os
import sys
import pyodbc

# Add Django project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

def fix_migrations_table():
    """Fix the django_migrations table ODBC compatibility issue"""
    
    # Direct connection to Azure SQL
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
        
        # Check if django_migrations table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'django_migrations'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            print("📋 Backing up existing django_migrations data...")
            # Get existing data
            cursor.execute("SELECT id, app, name, applied FROM django_migrations")
            existing_data = cursor.fetchall()
            
            print("🗑️ Dropping problematic django_migrations table...")
            cursor.execute("DROP TABLE django_migrations")
            conn.commit()
        else:
            existing_data = []
        
        print("✨ Creating new compatible django_migrations table...")
        cursor.execute("""
            CREATE TABLE django_migrations (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                app NVARCHAR(255) NOT NULL,
                name NVARCHAR(255) NOT NULL,
                applied DATETIME2 NOT NULL
            )
        """)
        conn.commit()
        
        # Restore data if we had any
        if existing_data:
            print("📥 Restoring migration data...")
            for row in existing_data:
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES (?, ?, ?)
                """, row[1], row[2], row[3])
            conn.commit()
            print(f"✅ Restored {len(existing_data)} migration records")
        
        print("🎉 Django migrations table fixed!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing migrations table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_migrations_table()
