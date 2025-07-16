#!/usr/bin/env python3
"""
Database Configuration Switcher

Easily switch between different database configurations:
- Docker SQL Server (Local)
- Microsoft Fabric SQL
- Azure SQL Database (Serverless)

Usage:
    python switch_database.py docker
    python switch_database.py fabric  
    python switch_database.py azure_sql
"""

import os
import sys
import shutil
from pathlib import Path

def switch_database(db_type):
    """Switch database configuration based on type"""
    
    backend_dir = Path(__file__).parent
    
    # Database configuration mappings
    configs = {
        'docker': {
            'env_file': '.env.local',
            'settings': 'ama_backend.settings',
            'description': 'Local Docker SQL Server 2019',
            'performance': 'Fast (Local)',
            'use_case': 'Local development'
        },
        'fabric': {
            'env_file': '.env',
            'settings': 'ama_backend.settings',
            'description': 'Microsoft Fabric SQL Database',
            'performance': 'Variable (Cloud)',
            'use_case': 'Production/Cloud testing'
        },
        'azure_sql': {
            'env_file': '.env.azure_sql',
            'settings': 'azure_sql_settings',
            'description': 'Azure SQL Database (Serverless)',
            'performance': 'Testing (Cloud)',
            'use_case': 'Performance comparison'
        }
    }
    
    if db_type not in configs:
        print(f"❌ Invalid database type: {db_type}")
        print(f"✅ Available options: {', '.join(configs.keys())}")
        return False
    
    config = configs[db_type]
    
    print(f"🔄 Switching to {config['description']}...")
    print("=" * 60)
    
    # Copy environment file
    env_source = backend_dir / config['env_file']
    env_target = backend_dir / '.env.active'
    
    if env_source.exists():
        shutil.copy2(env_source, env_target)
        print(f"✅ Environment: {config['env_file']} → .env.active")
    else:
        print(f"❌ Environment file not found: {config['env_file']}")
        return False
    
    # Update manage.py if needed (for custom settings)
    manage_py = backend_dir / 'manage.py'
    if db_type == 'azure_sql':
        # Update manage.py to use custom settings
        with open(manage_py, 'r') as f:
            content = f.read()
        
        # Replace the settings module
        updated_content = content.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')",
            f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{config['settings']}')"
        )
        
        with open(manage_py, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Settings: Updated manage.py to use {config['settings']}")
    else:
        # Reset to default settings
        with open(manage_py, 'r') as f:
            content = f.read()
        
        updated_content = content.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azure_sql_settings')",
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')"
        )
        
        with open(manage_py, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Settings: Reset manage.py to default settings")
    
    print("\n📊 Database Configuration:")
    print(f"   Type: {config['description']}")
    print(f"   Performance: {config['performance']}")
    print(f"   Use Case: {config['use_case']}")
    print(f"   Settings Module: {config['settings']}")
    
    print("\n🚀 Next Steps:")
    if db_type == 'azure_sql':
        print("   1. Ensure Azure SQL Database is created and configured")
        print("   2. Update .env.azure_sql with your connection details")
        print("   3. Run: python manage.py migrate")
        print("   4. Run performance tests")
    else:
        print("   1. Run: python manage.py migrate")
        print("   2. Start the development server")
    
    print(f"\n✅ Successfully switched to {db_type} database configuration!")
    return True

def show_current_config():
    """Show current database configuration"""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env.active'
    
    if env_file.exists():
        print("📊 Current Database Configuration:")
        print("-" * 40)
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith(('DATABASE_TYPE=', 'AZURE_SQL_', 'FABRIC_', 'DJANGO_SETTINGS_MODULE=')):
                    print(f"   {line.strip()}")
    else:
        print("❌ No active configuration found")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("🔧 Database Configuration Switcher")
        print("=" * 40)
        print("Usage: python switch_database.py <database_type>")
        print("\nAvailable database types:")
        print("  docker    - Local Docker SQL Server 2019")
        print("  fabric    - Microsoft Fabric SQL Database") 
        print("  azure_sql - Azure SQL Database (Serverless)")
        print("\nExamples:")
        print("  python switch_database.py docker")
        print("  python switch_database.py azure_sql")
        print("\nCurrent configuration:")
        show_current_config()
        sys.exit(1)
    
    db_type = sys.argv[1].lower()
    success = switch_database(db_type)
    
    if not success:
        sys.exit(1)
