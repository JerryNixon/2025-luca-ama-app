"""
Debug login issues - check users in database and test authentication
"""
import requests
import json
import sys
import os

# Add backend to path for Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
import django
django.setup()

from api.models import User

def check_database_users():
    """Check what users exist in the database"""
    print("🔍 Checking Users in Database...")
    
    try:
        users = User.objects.all()
        print(f"Total users found: {users.count()}")
        
        for user in users:
            print(f"  - Email: {user.email}")
            print(f"    Name: {user.name}")
            print(f"    Role: {user.role}")
            print(f"    Active: {user.is_active}")
            print(f"    Has Password: {bool(user.password)}")
            print("    ---")
        
        return users.count() > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_api_login():
    """Test the login API endpoint"""
    print("\n🔐 Testing Login API...")
    
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    test_credentials = {
        "email": "moderator@microsoft.com",
        "password": "moderator123"
    }
    
    try:
        print(f"Sending request to: {login_url}")
        print(f"With credentials: {test_credentials['email']}")
        
        response = requests.post(login_url, json=test_credentials, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login API is working!")
                return True
            else:
                print("❌ Login API returned success=false")
        else:
            print(f"❌ Login API returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login API error: {e}")
    
    return False

def create_test_user():
    """Create a test user if none exist"""
    print("\n👤 Creating Test User...")
    
    try:
        # Create moderator user
        user, created = User.objects.get_or_create(
            email='moderator@microsoft.com',
            defaults={
                'name': 'Test Moderator',
                'role': 'moderator',
                'is_active': True,
                'is_staff': True,
            }
        )
        
        # Set password
        user.set_password('moderator123')
        user.save()
        
        if created:
            print("✅ Created new moderator user")
        else:
            print("✅ Updated existing moderator user")
        
        print(f"User details:")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.name}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Has Password: {bool(user.password)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🔧 Login Diagnostics")
    print("=" * 50)
    
    # Check database users
    has_users = check_database_users()
    
    # Create test user if needed
    if not has_users:
        print("No users found, creating test user...")
        create_test_user()
    
    # Test login API
    login_works = test_api_login()
    
    print("\n" + "=" * 50)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if login_works:
        print("✅ Backend login is working correctly")
        print("❓ The issue might be in the frontend")
        print("\n🔍 Check frontend console for errors:")
        print("  1. Open browser developer tools (F12)")
        print("  2. Go to Console tab")
        print("  3. Try logging in and check for errors")
        print("  4. Check Network tab for failed requests")
    else:
        print("❌ Backend login is not working")
        print("🔧 Steps to fix:")
        print("  1. Ensure backend server is running")
        print("  2. Check database connectivity")
        print("  3. Verify user credentials")

if __name__ == "__main__":
    main()
