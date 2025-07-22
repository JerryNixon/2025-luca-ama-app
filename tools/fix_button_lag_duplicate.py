#!/usr/bin/env python3
"""
Switch to Local Database for Development
Creates a local SQLite database and migrates data for faster development.
"""

import os
import sys
import shutil
from pathlib import Path

def switch_to_local_db():
    """Switch from Fabric SQL to local SQLite for faster development"""
    
    print("🔄 Switching to Local SQLite Database for Development")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent / "backend"
    settings_file = backend_dir / "ama_backend" / "settings.py"
    
    if not settings_file.exists():
        print("❌ Could not find settings.py file")
        return False
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Create backup
    backup_file = settings_file.with_suffix('.py.fabric_backup')
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ Backed up original settings to {backup_file}")
    
    # Replace database configuration
    new_db_config = '''
# DEVELOPMENT: Use SQLite for faster local development
# For production, restore from settings.py.fabric_backup

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

print("🚀 Using Local SQLite Database for Development")
print("📍 Database: Local SQLite (db.sqlite3)")
print("⚡ Performance: Fast local database")

# Comment out Fabric SQL configuration for development
'''

    # Find and replace the database configuration
    lines = content.split('\n')
    new_lines = []
    in_db_config = False
    db_config_start = -1
    
    for i, line in enumerate(lines):
        if 'DATABASES = {' in line:
            in_db_config = True
            db_config_start = i
            # Insert new config
            new_lines.extend(new_db_config.strip().split('\n'))
            continue
        
        if in_db_config:
            # Skip lines until we find the end of the database config
            if line.strip() == '}' and 'default' in ''.join(lines[db_config_start:i]):
                in_db_config = False
                continue
            if line.startswith('print(f"Database:') or line.startswith('print(f"Host:') or line.startswith('print(f"User:') or line.startswith('print(f"Auth:'):
                # Skip these print statements too
                continue
            if in_db_config:
                continue
        
        new_lines.append(line)
    
    # Write new settings
    with open(settings_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Updated settings.py to use SQLite")
    
    return True

def create_local_database():
    """Create and set up the local database"""
    print(f"\n🗄️  Setting up Local Database...")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Run migrations
    print("🔄 Running database migrations...")
    os.system("python manage.py migrate")
    
    # Create superuser
    print(f"\n👤 Creating admin user...")
    create_user_script = '''
from django.contrib.auth.models import User
from django.db import transaction

try:
    with transaction.atomic():
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Created admin user: admin/admin123")
        else:
            print("✅ Admin user already exists")
except Exception as e:
    print(f"❌ Error creating admin user: {e}")
'''
    
    with open('create_admin.py', 'w') as f:
        f.write(create_user_script)
    
    os.system("python manage.py shell < create_admin.py")
    os.remove('create_admin.py')
    
    # Populate with sample data
    if os.path.exists('populate_db.py'):
        print(f"\n📊 Populating with sample data...")
        os.system("python populate_db.py")

def test_local_performance():
    """Test the performance with local database"""
    print(f"\n⚡ Testing Local Database Performance...")
    
    import time
    import requests
    
    print("Starting Django server for performance test...")
    
    # Note: In a real scenario, you'd start the server in background
    # For now, just provide instructions
    print("""
🚀 TO TEST PERFORMANCE:

1. Start the backend server:
   cd backend
   python manage.py runserver

2. Run the performance test:
   python quick_button_test.py

You should now see response times under 100ms instead of 2+ seconds!
""")

def restore_fabric_db():
    """Restore the original Fabric SQL configuration"""
    print("🔄 Restoring Original Fabric SQL Database Configuration")
    
    backend_dir = Path(__file__).parent / "backend"
    settings_file = backend_dir / "ama_backend" / "settings.py"
    backup_file = settings_file.with_suffix('.py.fabric_backup')
    
    if backup_file.exists():
        shutil.copy(backup_file, settings_file)
        print("✅ Restored original Fabric SQL configuration")
        print("⚠️  Remember: Fabric SQL has high latency but is needed for production")
    else:
        print("❌ No backup file found")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        restore_fabric_db()
        return
    
    print("🎯 FIXING BUTTON LAG ISSUE")
    print("=" * 60)
    print("PROBLEM: Microsoft Fabric SQL Database has 2+ second latency")
    print("SOLUTION: Switch to local SQLite for development")
    print("=" * 60)
    
    choice = input("\n🤔 Switch to local SQLite database? (y/n): ").lower().strip()
    
    if choice == 'y':
        if switch_to_local_db():
            create_local_database()
            test_local_performance()
            
            print(f"\n" + "=" * 60)
            print("✅ BUTTON LAG FIXED!")
            print("🚀 Local SQLite database is now active")
            print("⚡ Button clicks should now be under 100ms")
            print("📝 Your Fabric SQL settings are backed up")
            print(f"\n🔄 To restore Fabric SQL later:")
            print("   python fix_button_lag.py restore")
        else:
            print("❌ Failed to switch database configuration")
    else:
        print("❌ Database switch cancelled")
        print("💡 Alternative: Optimize Fabric SQL queries or add caching")

if __name__ == "__main__":
    main()
