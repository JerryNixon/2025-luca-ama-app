#!/usr/bin/env python3
"""
Test check-user endpoint for Jerry
"""

import requests
import json

def test_check_user():
    """Test the check-user endpoint"""
    print("Testing check-user endpoint for Jerry...")
    
    # Test the endpoint
    response = requests.post("http://localhost:8000/api/auth/check-user/", json={
        "email": "jerry.nixon@microsoft.com"
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        exists = data.get('data', {}).get('exists', False)
        print(f"Jerry exists in database: {exists}")
        
        if exists:
            print("✅ Jerry should be able to use database login")
        else:
            print("❌ Jerry not found - this is the problem!")
    else:
        print("❌ Endpoint failed")

if __name__ == "__main__":
    test_check_user()
