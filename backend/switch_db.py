#!/usr/bin/env python3
"""
Simple Database Switcher for AMA App
Switches between Fabric SQL and Azure SQL databases
"""

import os
import shutil
from pathlib import Path

# Database configurations
DATABASES = {
    'fabric': {
        'file': '.env',
        'name': 'Microsoft Fabric SQL',
        'description': 'Production Fabric SQL Database'
    },
    'azure': {
        'file': '.env.azure_sql.simple',
        'name': 'Azure SQL Serverless',
        'description': 'Azure SQL Database for testing'
    },
    'local': {
        'file': '.env.local',
        'name': 'Local SQLite',
        'description': 'Local development database'
    }
}

def switch_database(target_db):
    """Switch to target database by copying env file"""
    backend_dir = Path(__file__).parent
    
    if target_db not in DATABASES:
        print(f"❌ Unknown database: {target_db}")
        print(f"Available: {list(DATABASES.keys())}")
        return False
    
    config = DATABASES[target_db]
    source_file = backend_dir / config['file']
    target_file = backend_dir / '.env'
    
    if not source_file.exists():
        print(f"❌ Configuration file not found: {source_file}")
        return False
    
    # Backup current .env
    backup_file = backend_dir / '.env.backup'
    if target_file.exists():
        shutil.copy2(target_file, backup_file)
        print(f"📁 Backed up current config to .env.backup")
    
    # Copy new configuration
    shutil.copy2(source_file, target_file)
    
    print(f"✅ Switched to: {config['name']}")
    print(f"📊 Description: {config['description']}")
    print(f"🔧 Config file: {config['file']} → .env")
    
    return True

def show_current_database():
    """Show current database configuration"""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env'
    
    if not env_file.exists():
        print("❌ No .env file found")
        return
    
    # Read first few lines to identify database
    with open(env_file, 'r') as f:
        content = f.read()
        
    if 'FABRIC SQL' in content.upper():
        print("📊 Current: Microsoft Fabric SQL")
    elif 'AZURE SQL' in content.upper():
        print("📊 Current: Azure SQL Database")
    elif 'SQLITE' in content.upper():
        print("📊 Current: Local SQLite")
    else:
        print("📊 Current: Unknown database configuration")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("🔄 Database Switcher for AMA App")
        print("=" * 40)
        show_current_database()
        print("\nUsage: python switch_db.py <database>")
        print("\nAvailable databases:")
        for key, config in DATABASES.items():
            print(f"  {key:10} - {config['name']}")
        sys.exit(1)
    
    target = sys.argv[1].lower()
    if switch_database(target):
        print("\n🎯 Next steps:")
        print("1. Restart Django server")
        print("2. Run migrations if needed: python manage.py migrate")
        print("3. Test connection: python manage.py check")
    else:
        sys.exit(1)
