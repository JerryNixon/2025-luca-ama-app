#!/usr/bin/env python
"""
Azure SQL Server Runner
======================
Starts Django development server for Azure SQL with ODBC compatibility fixes
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Set environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

def run_azure_server():
    """Run Django server with Azure SQL compatibility"""
    
    # Setup Django
    django.setup()
    
    print("🔵 Starting Django Server for Azure SQL Database")
    print("📍 Database: Azure SQL Database (Serverless)")
    print("🔗 Connection: Custom Backend with ODBC fixes")
    print("🌍 Server: http://localhost:8000")
    print("📊 Admin: http://localhost:8000/admin/")
    print()
    
    # Override some settings for compatibility
    settings.DEBUG = True
    
    # Start server without migration checks
    try:
        from django.core.management.commands.runserver import Command as RunServerCommand
        from django.core.management.base import CommandParser
        
        # Create runserver command
        command = RunServerCommand()
        
        # Run without migration checks
        old_check_migrations = command.check_migrations
        command.check_migrations = lambda: None
        
        # Execute runserver
        execute_from_command_line(['manage.py', 'runserver', '8000'])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("\n💡 Suggestion: Try running with Fabric SQL instead")
        print("   python switch_database.py fabric")

if __name__ == "__main__":
    run_azure_server()
