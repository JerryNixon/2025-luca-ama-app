import requests
import json

# Test login endpoint
login_url = "http://127.0.0.1:8000/api/auth/login/"
test_user = {
    "email": "moderator@microsoft.com",
    "password": "moderator123"
}

print("🔐 Testing Authentication...")
print(f"Login URL: {login_url}")
print(f"Test User: {test_user['email']}")

try:
    response = requests.post(login_url, json=test_user)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Login successful!")
            print(f"User: {data['data']['user']['name']}")
            print(f"Role: {data['data']['user']['role']}")
            print(f"Token: {data['data']['token'][:50]}...")
        else:
            print("❌ Login failed")
    else:
        print("❌ Login request failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
