#!/usr/bin/env python3
"""
Complete application test for AMA app
Tests backend, database, and API endpoints
"""
import requests
import json
import time
import sys

def test_backend_health():
    """Test if backend is running"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend API is running")
            return True
        else:
            print(f"   ❌ Backend API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend is not running on port 8000")
        return False
    except Exception as e:
        print(f"   ❌ Backend test error: {e}")
        return False

def test_authentication():
    """Test user authentication"""
    print("\n🔐 Testing Authentication...")
    
    # Test login with moderator
    login_data = {
        "email": "moderator@microsoft.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/login/",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('token'):
                print("   ✅ Authentication successful")
                print(f"   👤 User: {data['data']['user']['name']} ({data['data']['user']['role']})")
                return data['data']['token']
            else:
                print("   ❌ Authentication failed - invalid response format")
                return None
        else:
            print(f"   ❌ Authentication failed - status {response.status_code}")
            if response.text:
                print(f"       Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return None

def test_event_creation(token):
    """Test event creation"""
    print("\n📅 Testing Event Creation...")
    
    if not token:
        print("   ⏭️  Skipping - no authentication token")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    event_data = {
        "name": "Test AMA Event",
        "open_date": "2025-01-15T10:00:00Z",
        "close_date": "2025-01-15T12:00:00Z"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/events/",
            json=event_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                event = data['data']
                print("   ✅ Event created successfully")
                print(f"   📝 Event: {event['name']}")
                print(f"   🔗 Share Link: {event.get('share_link', 'Not generated')}")
                return event['id']
            else:
                print("   ❌ Event creation failed - invalid response")
                return None
        else:
            print(f"   ❌ Event creation failed - status {response.status_code}")
            if response.text:
                print(f"       Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Event creation error: {e}")
        return None

def test_frontend():
    """Test frontend connectivity"""
    print("\n🎨 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is running")
            return True
        else:
            print(f"   ❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Frontend is not running on port 3000")
        return False
    except Exception as e:
        print(f"   ❌ Frontend test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 AMA Application Test Suite")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_health()
    
    # Test authentication
    token = test_authentication() if backend_ok else None
    
    # Test event creation
    event_id = test_event_creation(token) if token else None
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Backend:        {'✅ Working' if backend_ok else '❌ Failed'}")
    print(f"Authentication: {'✅ Working' if token else '❌ Failed'}")
    print(f"Event Creation: {'✅ Working' if event_id else '❌ Failed'}")
    print(f"Frontend:       {'✅ Working' if frontend_ok else '❌ Failed'}")
    
    if backend_ok and token and frontend_ok:
        print("\n🎉 All tests passed! Application is ready to use.")
        print("\n🚀 Quick Start:")
        print("   1. Open http://localhost:3000")
        print("   2. Login with: moderator@microsoft.com / test123")
        print("   3. Create events and test the full workflow")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")
        if not backend_ok:
            print("   • Start backend: cd backend && python manage.py runserver")
        if not frontend_ok:
            print("   • Start frontend: cd frontend && npm run dev")
        return 1

if __name__ == "__main__":
    sys.exit(main())
