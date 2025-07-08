"""
Simple test to check if login API is working
"""
import requests
import json

# Test the login endpoint
url = "http://127.0.0.1:8000/api/auth/login/"
data = {
    "email": "moderator@microsoft.com",
    "password": "moderator123"
}

print("Testing login API...")
print(f"URL: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Login API works!")
    else:
        print("❌ Login API failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
