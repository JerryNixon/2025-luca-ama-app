#!/usr/bin/env python3
"""
Configure Supabase for WebSocket Access
======================================
Set up proper CORS and RLS policies for direct browser connections
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

def setup_supabase_websockets():
    """Configure Supabase for WebSocket connections from browser"""
    
    print("🔧 Configuring Supabase for WebSocket Access...")
    print("=" * 50)
    
    try:
        # Import supabase client
        from supabase import create_client, Client
        
        # Your Supabase credentials
        url = "https://eysipjwmfgtvmjqgfojn.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5c2lwandtZmd0dm1qcWdmb2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwNDc3NzQsImV4cCI6MjA1MjYyMzc3NH0.1r8vNJIlEG5dTTJGf_LCuA_vQOJILnK8ZM5HryUMUGM"
        
        supabase: Client = create_client(url, key)
        
        print(f"✅ Supabase client created successfully")
        print(f"🌐 URL: {url}")
        
        # Test basic query first
        print("\n🔍 Testing basic query...")
        result = supabase.table("api_question").select("id, text, created_at").limit(1).execute()
        
        if result.data:
            print(f"✅ Basic query successful: {len(result.data)} records")
            print(f"📋 Sample record: {result.data[0]}")
        else:
            print("⚠️  No data returned, but connection successful")
        
        # Test realtime channel creation
        print("\n🔄 Testing realtime channel creation...")
        
        # Create a test channel
        channel = supabase.channel('test-channel')
        print(f"✅ Channel created: {channel}")
        
        return supabase, True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Run: pip install supabase")
        return None, False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check internet connection")
        print("2. Verify Supabase project is active")
        print("3. Check API keys are correct")
        print("4. Ensure RLS policies allow access")
        return None, False

def check_rls_policies():
    """Check Row Level Security policies"""
    print("\n🛡️ Checking Row Level Security Policies...")
    print("=" * 50)
    
    print("📋 Required RLS Policies for WebSocket access:")
    print("1. api_question table: SELECT policy for anon role")
    print("2. api_event table: SELECT policy for anon role")
    print("3. api_user table: SELECT policy for anon role")
    print()
    print("🔧 To fix RLS policies:")
    print("1. Go to Supabase Dashboard → Authentication → Policies")
    print("2. For each table (api_question, api_event, api_user):")
    print("   - Create policy: 'Enable read access for all users'")
    print("   - Policy type: SELECT")
    print("   - Target roles: anon, authenticated")
    print("   - Policy definition: true (allow all reads)")

if __name__ == "__main__":
    print("🚀 Supabase WebSocket Configuration")
    print("=" * 60)
    
    supabase, success = setup_supabase_websockets()
    
    if success:
        print("\n✅ Supabase connection successful!")
        print("🎯 Ready to test WebSocket subscriptions")
    else:
        print("\n❌ Supabase connection failed")
        check_rls_policies()
    
    print("\n📋 Next Steps:")
    print("1. If connection successful → Test WebSocket subscriptions")
    print("2. If connection failed → Fix RLS policies in Supabase dashboard")
    print("3. Then run WebSocket test page")
