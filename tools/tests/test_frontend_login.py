"""
Test frontend login flow by simulating API calls
"""
import requests
import json

# Test login flow
def test_login_flow():
    """Test the complete login flow"""
    print("🔍 Testing Frontend Login Flow...")
    
    # Step 1: Test login API
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    credentials = {
        "email": "moderator@microsoft.com",
        "password": "moderator123"
    }
    
    print(f"Step 1: POST {login_url}")
    print(f"Credentials: {credentials}")
    
    try:
        response = requests.post(login_url, json=credentials, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user = data['data']['user']
                token = data['data']['token']
                print(f"✅ Login successful!")
                print(f"User: {user['name']} ({user['email']})")
                print(f"Role: {user['role']}")
                print(f"Token: {token[:50]}...")
                
                # Step 2: Test /auth/me/ endpoint with token
                print(f"\nStep 2: GET /auth/me/ with token")
                me_url = "http://127.0.0.1:8000/api/auth/me/"
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                me_response = requests.get(me_url, headers=headers, timeout=10)
                print(f"Status: {me_response.status_code}")
                print(f"Response: {me_response.text}")
                
                if me_response.status_code == 200:
                    print("✅ Token validation successful!")
                    return True
                else:
                    print("❌ Token validation failed!")
                    return False
            else:
                print("❌ Login failed - success=false")
                return False
        else:
            print(f"❌ Login failed - status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def main():
    """Run the test"""
    print("🚀 Frontend Login Flow Test")
    print("=" * 50)
    
    if test_login_flow():
        print("\n✅ Backend authentication is working correctly!")
        print("\n🔧 If frontend login isn't working, check:")
        print("  1. Browser console for JavaScript errors")
        print("  2. Network tab in browser developer tools")
        print("  3. CORS issues in browser")
        print("  4. Make sure frontend is using correct API URL")
        print("  5. Check if cookies are being set properly")
        
        print("\n🎯 Debug steps:")
        print("  1. Open browser to http://localhost:3000")
        print("  2. Open developer tools (F12)")
        print("  3. Try to login and watch console/network tabs")
        print("  4. Check if API calls are being made")
        print("  5. Check if cookies are being set")
    else:
        print("\n❌ Backend authentication has issues")

if __name__ == "__main__":
    main()
