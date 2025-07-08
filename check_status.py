#!/usr/bin/env python3
"""
Comprehensive status check for the AMA application
Tests both backend and frontend connectivity
"""
import requests
import json
import time
import sys
import os

def check_backend():
    """Check if Django backend is running and responding"""
    print("=== Checking Backend Status ===")
    
    try:
        # Test basic connectivity
        response = requests.get("http://127.0.0.1:8000/api/", timeout=5)
        if response.status_code == 200:
            print("✓ Backend API is running")
        else:
            print(f"⚠ Backend API responded with status {response.status_code}")
            
        # Test admin interface
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        if response.status_code in [200, 302]:  # 302 is redirect to login
            print("✓ Django admin interface is accessible")
        else:
            print(f"⚠ Django admin interface issue (Status: {response.status_code})")
            
        # Test CORS preflight
        response = requests.options("http://127.0.0.1:8000/api/events/", 
                                  headers={"Origin": "http://localhost:3000"}, 
                                  timeout=5)
        if response.status_code == 200:
            print("✓ CORS configuration is working")
        else:
            print(f"⚠ CORS configuration may have issues (Status: {response.status_code})")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Backend is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("✗ Backend request timed out")
        return False
    except Exception as e:
        print(f"✗ Backend error: {e}")
        return False

def check_frontend():
    """Check if Next.js frontend is running"""
    print("\n=== Checking Frontend Status ===")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is running")
            return True
        else:
            print(f"⚠ Frontend responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Frontend is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("✗ Frontend request timed out")
        return False
    except Exception as e:
        print(f"✗ Frontend error: {e}")
        return False

def check_database():
    """Check database connectivity through Django admin"""
    print("\n=== Checking Database Status ===")
    
    try:
        # This will fail if database is not accessible
        response = requests.get("http://127.0.0.1:8000/admin/api/user/", timeout=10)
        if response.status_code in [200, 302]:  # 302 is redirect to login
            print("✓ Database connection is working")
            return True
        else:
            print(f"⚠ Database connection issue (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend to test database")
        return False
    except Exception as e:
        print(f"⚠ Database test error: {e}")
        return False

def main():
    """Main status check function"""
    print("🔍 AMA Application Status Check")
    print("=" * 40)
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    database_ok = check_database() if backend_ok else False
    
    print("\n" + "=" * 40)
    print("📊 Summary:")
    print(f"Backend:  {'✓ Running' if backend_ok else '✗ Not running'}")
    print(f"Frontend: {'✓ Running' if frontend_ok else '✗ Not running'}")
    print(f"Database: {'✓ Connected' if database_ok else '✗ Not connected'}")
    
    if backend_ok and frontend_ok and database_ok:
        print("\n🎉 All systems are operational!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://127.0.0.1:8000/api/")
        print("👤 Django Admin: http://127.0.0.1:8000/admin/")
        return 0
    else:
        print("\n⚠️  Some systems are not operational")
        if not backend_ok:
            print("   • Start backend with: .\\start-backend.ps1")
        if not frontend_ok:
            print("   • Start frontend with: .\\start-frontend.ps1")
        return 1

if __name__ == "__main__":
    sys.exit(main())
