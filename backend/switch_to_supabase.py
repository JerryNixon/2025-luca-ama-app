#!/usr/bin/env python3
"""
Supabase Database Switching Script
================================
Switch Django app to use Supabase PostgreSQL for ORM testing
"""

import os
import shutil
from pathlib import Path

def switch_to_supabase():
    """Switch Django app to use Supabase PostgreSQL"""
    backend_dir = Path(__file__).parent
    
    print("🔄 Switching to Supabase PostgreSQL Database...")
    
    # Backup current settings
    current_settings = backend_dir / "ama_backend" / "settings.py"
    backup_settings = backend_dir / "ama_backend" / "settings_backup.py"
    
    if current_settings.exists() and not backup_settings.exists():
        shutil.copy2(current_settings, backup_settings)
        print("📦 Current settings backed up")
    
    # Copy Supabase settings
    supabase_settings = backend_dir / "supabase_settings.py"
    if supabase_settings.exists():
        shutil.copy2(supabase_settings, current_settings)
        print("✅ Supabase settings applied")
    else:
        print("❌ Supabase settings file not found!")
        return False
    
    # Copy environment file
    env_supabase = backend_dir / ".env.supabase"
    env_current = backend_dir / ".env"
    
    if env_supabase.exists():
        # Backup current .env
        if env_current.exists():
            shutil.copy2(env_current, backend_dir / ".env.backup")
        shutil.copy2(env_supabase, env_current)
        print("🌍 Environment variables updated")
    
    print("🎉 Successfully switched to Supabase!")
    print("\n📝 Next steps:")
    print("1. Update .env.supabase with your actual Supabase credentials")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py runserver")
    
    return True

def switch_back():
    """Switch back to previous configuration"""
    backend_dir = Path(__file__).parent
    
    print("🔄 Switching back to previous configuration...")
    
    # Restore settings
    current_settings = backend_dir / "ama_backend" / "settings.py"
    backup_settings = backend_dir / "ama_backend" / "settings_backup.py"
    
    if backup_settings.exists():
        shutil.copy2(backup_settings, current_settings)
        print("✅ Previous settings restored")
    
    # Restore environment
    env_current = backend_dir / ".env"
    env_backup = backend_dir / ".env.backup"
    
    if env_backup.exists():
        shutil.copy2(env_backup, env_current)
        print("🌍 Previous environment restored")
    
    print("🎉 Successfully switched back!")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'supabase':
            switch_to_supabase()
        elif sys.argv[1] == 'back':
            switch_back()
        else:
            print("Usage: python switch_to_supabase.py [supabase|back]")
    else:
        print("🔄 Database Configuration Switcher")
        print("Options:")
        print("  python switch_to_supabase.py supabase - Switch to Supabase")
        print("  python switch_to_supabase.py back     - Switch back to previous config")

if __name__ == "__main__":
    main()
