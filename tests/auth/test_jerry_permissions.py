#!/usr/bin/env python3
"""
Test the events API to see what permissions Jerry has for the Luca Town Hall event
"""

import requests
import json

# Jerry's credentials
email = "jerry.nixon@microsoft.com"
password = "test123"

print("="*60)
print("TESTING JERRY'S EVENT PERMISSIONS")
print("="*60)

# Step 1: Login to get token
print("\n1. Logging in...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/auth/login/",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['data']['token']
        print(f"✅ Login successful! Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Get events list
print("\n2. Getting events list...")
try:
    response = requests.get(
        "http://127.0.0.1:8000/api/events/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Events retrieved successfully!")
        print(f"Number of events: {len(events)}")
        
        # Look for Luca Town Hall event
        luca_event = None
        for event in events:
            if "Luca" in event.get("name", ""):
                luca_event = event
                break
        
        if luca_event:
            print(f"\n🎯 Found Luca Town Hall event:")
            print(f"   ID: {luca_event['id']}")
            print(f"   Name: {luca_event['name']}")
            print(f"   User Role: {luca_event.get('user_role_in_event', 'Not specified')}")
            print(f"   Can Moderate: {luca_event.get('can_user_moderate', 'Not specified')}")
            print(f"   Can Access: {luca_event.get('can_user_access', 'Not specified')}")
            print(f"   Is Creator: {luca_event.get('is_created_by_user', 'Not specified')}")
            
            # Step 3: Get specific event details
            print(f"\n3. Getting event details for {luca_event['id']}...")
            try:
                response = requests.get(
                    f"http://127.0.0.1:8000/api/events/{luca_event['id']}/",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    event_details = response.json()
                    print(f"✅ Event details retrieved!")
                    print(f"Event details: {json.dumps(event_details, indent=2)}")
                else:
                    print(f"❌ Event details failed: {response.text}")
            except Exception as e:
                print(f"❌ Event details error: {e}")
        else:
            print("❌ Luca Town Hall event not found")
            print("Available events:")
            for event in events:
                print(f"   - {event.get('name', 'No name')}")
    else:
        print(f"❌ Events retrieval failed: {response.text}")
        
except Exception as e:
    print(f"❌ Events error: {e}")

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)
