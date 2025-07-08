#!/usr/bin/env python3
"""
Simple API test
"""

import requests
import json

try:
    # Test login
    response = requests.post('http://localhost:8000/api/login/', json={
        'email': 'moderator@microsoft.com',
        'password': 'testpass123'
    })
    print(f"Login status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Login successful!")
        token = data['data']['token']
        
        # Test getting events
        events_response = requests.get('http://localhost:8000/api/events/', headers={
            'Authorization': f'Bearer {token}'
        })
        print(f"Events status: {events_response.status_code}")
        print(f"Events data: {events_response.json()}")
        
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
