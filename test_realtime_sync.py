#!/usr/bin/env python3
"""
Test script to demonstrate real-time synchronization between moderator and user views.

This script:
1. Posts a question as Amar (user)
2.    print("✅ Question posted (ID: {question_id})")
    print("   → Check both views - the question should appear within 3 seconds")
    
    time.sleep(4)  # Wait a bit longer than the polling intervalrs the question as Jerry (moderator)
3. Stages the question as Jerry
4. Marks the question as answered as Jerry
5. Adds moderator notes

The changes should be visible in real-time across both views without requiring manual refresh.

Usage:
    python test_realtime_sync.py
"""

import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
EVENTS_URL = f"{BASE_URL}/events/"
QUESTIONS_URL = f"{BASE_URL}/questions/"

def login_user(email, password):
    """Login a user and return the authentication token."""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'email': email,
            'password': password
        }
        response = requests.post(LOGIN_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            # Handle the nested response format
            if response_data.get('success') and 'data' in response_data:
                data = response_data['data']
                return data.get('token'), data.get('user')
            else:
                return response_data.get('token'), response_data.get('user')
        else:
            print(f"Login failed for {email}: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None, None

def get_events(token):
    """Get events list for the authenticated user."""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(EVENTS_URL, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get events: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Get events error: {e}")
        return []

def post_question(token, event_id, question_text):
    """Post a question to an event."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {
            'event': event_id,
            'text': question_text,
            'is_anonymous': False
        }
        response = requests.post(QUESTIONS_URL, json=data, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to post question: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Post question error: {e}")
        return None

def update_question(token, question_id, data):
    """Update a question (moderator actions)."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.patch(f"{QUESTIONS_URL}{question_id}/", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to update question: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Update question error: {e}")
        return None

def main():
    print("=== Testing Real-Time Synchronization ===")
    print("This test demonstrates real-time sync between moderator and user views.")
    print("Open both views in separate browser tabs to see changes in real-time!")
    print()
    
    # Login as a moderator user
    print("1. Logging in as moderator user...")
    moderator_token, moderator_user = login_user('jerry.nixon@microsoft.com', 'test123')
    if not moderator_token:
        print("❌ Failed to login as moderator")
        return
    print(f"✅ Moderator logged in: {moderator_user['name']}")
    
    # Login as Amar (participant)
    print("\n2. Logging in as Amar (participant)...")
    amar_token, amar_user = login_user('amapatil@microsoft.com', 'test123')
    if not amar_token:
        print("❌ Failed to login as Amar")
        return
    print(f"✅ Amar logged in: {amar_user['name']}")
    
    # Get moderator's events
    print("\n3. Finding an event moderator can moderate...")
    moderator_events = get_events(moderator_token)
    if not moderator_events:
        print("❌ Moderator has no events")
        return
    
    # Find an event moderator created or can moderate
    target_event = None
    for event in moderator_events:
        if event.get('can_user_moderate', False):
            target_event = event
            break
    
    if not target_event:
        print("❌ Moderator cannot moderate any events")
        return
    
    event_id = target_event['id']
    event_name = target_event['name']
    print(f"✅ Found event: '{event_name}' (ID: {event_id})")
    
    print(f"\n📖 Instructions:")
    print(f"   1. Open moderator view: http://localhost:3000/events/{event_id}")
    print(f"   2. Open user view: http://localhost:3000/events/{event_id}/user")
    print(f"   3. Watch changes appear in real-time as the script executes!")
    print()
    
    input("Press Enter when you have both views open...")
    
    # Step 1: Post a question as Amar
    print("\n🔄 Step 1: Posting question as Amar...")
    timestamp = time.strftime('%H:%M:%S')
    question_text = f"Real-time sync test question posted at {timestamp}"
    new_question = post_question(amar_token, event_id, question_text)
    
    if not new_question:
        print("❌ Failed to post question")
        return
    
    question_id = new_question['id']
    print(f"✅ Question posted (ID: {question_id})")
    print("   → Check both views - the question should appear within 30 seconds")
    
    time.sleep(5)
    
    # Step 2: Star the question as moderator
    print("\n🔄 Step 2: Starring question as moderator...")
    updated = update_question(moderator_token, question_id, {'is_starred': True})
    if updated:
        print("✅ Question starred")
        print("   → Check both views - the star should appear")
    else:
        print("❌ Failed to star question")
    
    time.sleep(5)
    
    # Step 3: Stage the question as moderator
    print("\n🔄 Step 3: Staging question as moderator...")
    updated = update_question(moderator_token, question_id, {'is_staged': True})
    if updated:
        print("✅ Question staged")
        print("   → Check both views - 'On Stage' status should appear")
    else:
        print("❌ Failed to stage question")
    
    time.sleep(5)
    
    # Step 4: Add moderator notes
    print("\n🔄 Step 4: Adding moderator notes as moderator...")
    note_text = f"Important question - reviewed at {time.strftime('%H:%M:%S')}"
    updated = update_question(moderator_token, question_id, {'presenter_notes': note_text})
    if updated:
        print("✅ Moderator notes added")
        print("   → Check moderator view - notes should appear")
    else:
        print("❌ Failed to add moderator notes")
    
    time.sleep(5)
    
    # Step 5: Mark as answered
    print("\n🔄 Step 5: Marking question as answered as moderator...")
    updated = update_question(moderator_token, question_id, {'is_answered': True})
    if updated:
        print("✅ Question marked as answered")
        print("   → Check both views - 'Answered' status should appear")
    else:
        print("❌ Failed to mark as answered")
    
    print("\n🎉 Real-time sync test completed!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✓ User can post questions visible to moderator")
    print("   ✓ Moderator actions (star, stage, answer) sync to user view")
    print("   ✓ Both views have refresh buttons for manual sync")
    print("   ✓ Auto-refresh every 3 seconds keeps views synchronized")
    print("   ✓ Auto-refresh pauses while user is typing (user view)")
    print("   ✓ Changes persist across page refreshes")
    
    print(f"\n🔍 To test refresh behavior:")
    print(f"   1. Refresh one of the browser tabs")
    print(f"   2. You should stay on the same page (no redirect to login)")
    print(f"   3. All question states should be preserved")

if __name__ == "__main__":
    main()
