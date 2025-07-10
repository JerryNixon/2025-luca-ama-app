"""
Final Application Test - Verify complete AMA application functionality
Tests backend, frontend, database connectivity, and authentication
"""
import subprocess
import time
import requests
import json
from datetime import datetime

class AMAApplicationTester:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        
    def test_result(self, test_name, success, message=""):
        """Record test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'success': success
        })
        print(f"{status} - {test_name}: {message}")
    
    def test_backend_health(self):
        """Test backend server health"""
        print("\n🔍 Testing Backend Health...")
        
        # Test admin endpoint (should work)
        try:
            response = requests.get(f"{self.backend_url}/admin/", timeout=5)
            if response.status_code == 200:
                self.test_result("Backend Admin", True, "Django admin accessible")
            else:
                self.test_result("Backend Admin", False, f"Status: {response.status_code}")
        except Exception as e:
            self.test_result("Backend Admin", False, f"Error: {e}")
        
        # Test API endpoints (should be protected)
        try:
            response = requests.get(f"{self.backend_url}/api/events/", timeout=5)
            if response.status_code == 401:
                self.test_result("API Security", True, "Events endpoint properly protected")
            else:
                self.test_result("API Security", False, f"Status: {response.status_code}")
        except Exception as e:
            self.test_result("API Security", False, f"Error: {e}")
    
    def test_frontend_health(self):
        """Test frontend server health"""
        print("\n🌐 Testing Frontend Health...")
        
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=5)
            if response.status_code == 200:
                self.test_result("Frontend Server", True, "Next.js app accessible")
            else:
                self.test_result("Frontend Server", False, f"Status: {response.status_code}")
        except Exception as e:
            self.test_result("Frontend Server", False, f"Error: {e}")
    
    def test_cors_config(self):
        """Test CORS configuration"""
        print("\n🔗 Testing CORS Configuration...")
        
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = requests.options(f"{self.backend_url}/api/events/", headers=headers, timeout=5)
            
            if 'Access-Control-Allow-Origin' in response.headers:
                allowed_origin = response.headers.get('Access-Control-Allow-Origin')
                if allowed_origin == 'http://localhost:3000':
                    self.test_result("CORS Configuration", True, "Frontend origin allowed")
                else:
                    self.test_result("CORS Configuration", False, f"Wrong origin: {allowed_origin}")
            else:
                self.test_result("CORS Configuration", False, "No CORS headers found")
        except Exception as e:
            self.test_result("CORS Configuration", False, f"Error: {e}")
    
    def test_database_connectivity(self):
        """Test database connectivity through Django"""
        print("\n🗄️ Testing Database Connectivity...")
        
        try:
            # Run Django management command to check database
            result = subprocess.run(
                ['python', 'manage.py', 'check', '--database=default'],
                cwd='backend',
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.test_result("Database Connection", True, "Django database check passed")
            else:
                self.test_result("Database Connection", False, f"Django check failed: {result.stderr}")
        except Exception as e:
            self.test_result("Database Connection", False, f"Error: {e}")
    
    def test_authentication(self):
        """Test authentication endpoint"""
        print("\n🔐 Testing Authentication...")
        
        # Test login endpoint with valid credentials
        test_user = {
            "email": "moderator@microsoft.com",
            "password": "moderator123"
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login/",
                json=test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_result("Authentication", True, "Login successful with test user")
                    return data['data']['token']
                else:
                    self.test_result("Authentication", False, "Login failed - invalid response")
            else:
                self.test_result("Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.test_result("Authentication", False, f"Error: {e}")
        
        return None
    
    def test_authenticated_endpoints(self, token):
        """Test authenticated endpoints"""
        print("\n🔒 Testing Authenticated Endpoints...")
        
        if not token:
            self.test_result("Authenticated Endpoints", False, "No token available")
            return
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Test events endpoint with authentication
            response = requests.get(f"{self.backend_url}/api/events/", headers=headers, timeout=5)
            if response.status_code == 200:
                self.test_result("Events API", True, "Events endpoint accessible with token")
            else:
                self.test_result("Events API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.test_result("Events API", False, f"Error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🎯 FINAL TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            print(f"   {result['status']} - {result['test']}")
            if result['message']:
                print(f"      {result['message']}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Your AMA application is ready for production!")
            print("\n📋 What's working:")
            print("   • Django backend on port 8000")
            print("   • Next.js frontend on port 3000")
            print("   • Microsoft Fabric SQL database")
            print("   • Authentication with JWT tokens")
            print("   • CORS configuration for frontend-backend communication")
            print("   • API endpoints are properly secured")
            
            print("\n🚀 Next Steps:")
            print("   1. Open frontend: http://localhost:3000")
            print("   2. Login with: moderator@microsoft.com / moderator123")
            print("   3. Create events and test full functionality")
            print("   4. All data will be stored in Microsoft Fabric SQL")
        else:
            print("\n⚠️  Some tests failed - check the details above")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 AMA Application Final Test Suite")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_backend_health()
        self.test_frontend_health()
        self.test_cors_config()
        self.test_database_connectivity()
        token = self.test_authentication()
        self.test_authenticated_endpoints(token)
        
        self.print_summary()

if __name__ == "__main__":
    tester = AMAApplicationTester()
    tester.run_all_tests()
