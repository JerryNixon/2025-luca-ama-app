#!/usr/bin/env python3
"""
Database Switching Script for Performance Testing
Easily switch between Docker, Fabric, and Azure SQL for your app
"""

import os
import shutil
from pathlib import Path

def switch_to_azure_sql():
    """Switch Django app to use Azure SQL Database"""
    backend_dir = Path(__file__).parent
    
    # Backup current settings if not already backed up
    current_settings = backend_dir / "ama_backend" / "settings.py"
    backup_settings = backend_dir / "ama_backend" / "settings_backup.py"
    
    if current_settings.exists() and not backup_settings.exists():
        shutil.copy2(current_settings, backup_settings)
        print("📋 Backed up current settings to settings_backup.py")
    
    # Copy Azure SQL settings
    azure_settings = backend_dir / "azure_sql_settings.py"
    if azure_settings.exists():
        shutil.copy2(azure_settings, current_settings)
        print("✅ Switched to Azure SQL Database configuration")
        print("🔗 Database: luca_azure_ama")
        print("🏢 Server: luca-azure-ama.database.windows.net")
        print("🔐 Auth: ActiveDirectoryInteractive")
    else:
        print("❌ Azure SQL settings file not found!")

def switch_to_docker():
    """Switch back to Docker SQL Server"""
    backend_dir = Path(__file__).parent
    current_settings = backend_dir / "ama_backend" / "settings.py"
    backup_settings = backend_dir / "ama_backend" / "settings_backup.py"
    
    if backup_settings.exists():
        shutil.copy2(backup_settings, current_settings)
        print("✅ Switched back to Docker SQL Server configuration")
    else:
        print("❌ No backup settings found!")

def show_current_database():
    """Show which database configuration is currently active"""
    backend_dir = Path(__file__).parent
    current_settings = backend_dir / "ama_backend" / "settings.py"
    
    if current_settings.exists():
        with open(current_settings, 'r') as f:
            content = f.read()
            
        if 'azure_mssql_backend' in content:
            print("📍 Current: Azure SQL Database (Serverless)")
        elif 'fabric' in content.lower():
            print("📍 Current: Microsoft Fabric SQL")
        elif 'mssql' in content:
            print("📍 Current: Docker SQL Server")
        else:
            print("📍 Current: Unknown database configuration")
    else:
        print("❌ No settings file found!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🔄 Database Switching Tool")
        print("=" * 30)
        print("Usage:")
        print("  python switch_database.py azure    # Switch to Azure SQL")
        print("  python switch_database.py docker   # Switch back to Docker")
        print("  python switch_database.py status   # Show current database")
        print()
        show_current_database()
    else:
        command = sys.argv[1].lower()
        
        if command == "azure":
            switch_to_azure_sql()
        elif command == "docker":
            switch_to_docker()
        elif command == "status":
            show_current_database()
        else:
            print("❌ Unknown command. Use: azure, docker, or status")
