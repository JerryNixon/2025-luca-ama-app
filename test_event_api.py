#!/usr/bin/env python3
"""
Test script to verify event API endpoints work correctly
"""

import os
import sys
import django
import requests
import json

# Add the project root to Python path
sys.path.append('c:/Users/t-lucahadife/Documents/luca-ama-app/backend')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

# Setup Django
django.setup()

from api.models import User, Event

def test_event_api():
    """Test the event API endpoints"""
    
    # Test data
    base_url = "http://localhost:8000/api"
    
    print("=== Testing Event API ===")
    
    # First, login to get token
    print("\n1. Testing login...")
    login_data = {
        "email": "jerry@example.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result['data']['token']
            headers = {"Authorization": f"Bearer {token}"}
            print("✓ Login successful")
            
            # Test event list
            print("\n2. Testing event list...")
            events_response = requests.get(f"{base_url}/events/", headers=headers)
            print(f"Events list status: {events_response.status_code}")
            
            if events_response.status_code == 200:
                events = events_response.json()
                print(f"✓ Found {len(events)} events")
                
                if events:
                    # Test first event details
                    first_event_id = events[0]['id']
                    print(f"\n3. Testing event details for ID: {first_event_id}")
                    
                    event_response = requests.get(f"{base_url}/events/{first_event_id}/", headers=headers)
                    print(f"Event detail status: {event_response.status_code}")
                    
                    if event_response.status_code == 200:
                        event_data = event_response.json()
                        print("✓ Event details retrieved successfully")
                        print(f"Event name: {event_data['name']}")
                        print(f"User role: {event_data.get('user_role_in_event', 'N/A')}")
                        print(f"Can moderate: {event_data.get('can_user_moderate', False)}")
                        print(f"Can access: {event_data.get('can_user_access', False)}")
                        print(f"Is creator: {event_data.get('is_created_by_user', False)}")
                    else:
                        print(f"✗ Event details failed: {event_response.text}")
                else:
                    print("No events found to test")
            else:
                print(f"✗ Events list failed: {events_response.text}")
        else:
            print(f"✗ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"✗ API test failed: {str(e)}")

if __name__ == "__main__":
    test_event_api()
