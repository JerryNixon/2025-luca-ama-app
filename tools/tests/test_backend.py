#!/usr/bin/env python3
"""
Test script to verify the AMA backend is working correctly
"""
import requests
import json

def test_backend():
    base_url = "http://127.0.0.1:8000/api"
    
    print("=== Testing AMA Backend Connection ===")
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✓ Backend is running (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend connection failed: {e}")
        return False
    
    # Test 2: Check events endpoint
    try:
        response = requests.get(f"{base_url}/events/", timeout=5)
        print(f"✓ Events endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data)} events")
    except requests.exceptions.RequestException as e:
        print(f"✗ Events endpoint failed: {e}")
    
    # Test 3: Check auth endpoint
    try:
        response = requests.post(f"{base_url}/auth/login/", 
                               json={"username": "test", "password": "test"}, 
                               timeout=5)
        print(f"✓ Auth endpoint accessible (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"✗ Auth endpoint failed: {e}")
    
    print("\n=== Backend Test Complete ===")
    return True

if __name__ == "__main__":
    test_backend()
