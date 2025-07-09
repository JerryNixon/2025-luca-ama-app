#!/usr/bin/env python3
"""
Test script to verify the moderator view question refresh functionality.

This script:
1. Tests posting a question as Amar to Jerry's event
2. Checks if Jerry can see the question via API
3. Validates the question appears in the moderator view

Usage:
    python test_moderator_refresh.py
"""

import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
EVENTS_URL = f"{BASE_URL}/events/"
QUESTIONS_URL = f"{BASE_URL}/questions/"

def login_user(username, password):
    """Login a user and return the authentication token."""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'username': username,
            'password': password
        }
        response = requests.post(LOGIN_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token'), data.get('user')
        else:
            print(f"Login failed for {username}: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Login error for {username}: {e}")
        return None, None

def get_events(token):
    """Get events list for the authenticated user."""
    try:
        headers = {'Authorization': f'Token {token}'}
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
            'Authorization': f'Token {token}',
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

def get_questions(token, event_id):
    """Get questions for an event."""
    try:
        headers = {'Authorization': f'Token {token}'}
        response = requests.get(f"{QUESTIONS_URL}?event={event_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get questions: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Get questions error: {e}")
        return []

def main():
    print("=== Testing Moderator View Question Refresh ===\n")
    
    # Login as Jerry (event creator)
    print("1. Logging in as Jerry...")
    jerry_token, jerry_user = login_user('jerry', 'test123')
    if not jerry_token:
        print("❌ Failed to login as Jerry")
        return
    print(f"✅ Jerry logged in successfully: {jerry_user['name']}")
    
    # Login as Amar (participant)
    print("\n2. Logging in as Amar...")
    amar_token, amar_user = login_user('amar', 'test123')
    if not amar_token:
        print("❌ Failed to login as Amar")
        return
    print(f"✅ Amar logged in successfully: {amar_user['name']}")
    
    # Get Jerry's events
    print("\n3. Getting Jerry's events...")
    jerry_events = get_events(jerry_token)
    if not jerry_events:
        print("❌ Jerry has no events")
        return
    
    # Find an event Jerry created
    jerry_created_event = None
    for event in jerry_events:
        if event.get('is_created_by_user', False):
            jerry_created_event = event
            break
    
    if not jerry_created_event:
        print("❌ Jerry has not created any events")
        return
    
    event_id = jerry_created_event['id']
    event_name = jerry_created_event['name']
    print(f"✅ Found Jerry's event: '{event_name}' (ID: {event_id})")
    
    # Check if Amar can access this event
    print("\n4. Checking if Amar can access Jerry's event...")
    amar_events = get_events(amar_token)
    amar_can_access = any(e['id'] == event_id for e in amar_events)
    
    if not amar_can_access:
        print("❌ Amar cannot access Jerry's event")
        return
    print("✅ Amar can access Jerry's event")
    
    # Get initial question count for Jerry's view
    print("\n5. Getting initial questions (Jerry's view)...")
    initial_questions_jerry = get_questions(jerry_token, event_id)
    initial_count = len(initial_questions_jerry)
    print(f"✅ Initial question count for Jerry: {initial_count}")
    
    # Post a question as Amar
    question_text = f"Test question from Amar at {time.strftime('%H:%M:%S')}"
    print(f"\n6. Posting question as Amar: '{question_text}'...")
    new_question = post_question(amar_token, event_id, question_text)
    if not new_question:
        print("❌ Failed to post question as Amar")
        return
    print(f"✅ Question posted successfully by Amar (ID: {new_question['id']})")
    
    # Check if Jerry can see the new question
    print("\n7. Checking if Jerry can see the new question...")
    updated_questions_jerry = get_questions(jerry_token, event_id)
    updated_count = len(updated_questions_jerry)
    
    if updated_count > initial_count:
        print(f"✅ Jerry can see the new question! Count increased from {initial_count} to {updated_count}")
        
        # Find the specific question
        for q in updated_questions_jerry:
            if q['text'] == question_text:
                print(f"✅ Found the specific question: ID {q['id']}, by {q['author']['name']}")
                break
    else:
        print(f"❌ Jerry cannot see the new question. Count: {updated_count} (expected: {initial_count + 1})")
        return
    
    # Summary
    print("\n=== Summary ===")
    print(f"✅ Event: '{event_name}' (ID: {event_id})")
    print(f"✅ Creator: Jerry (can moderate)")
    print(f"✅ Participant: Amar (can post questions)")
    print(f"✅ Question posted by Amar is visible to Jerry via API")
    print("\n💡 The API is working correctly!")
    print("💡 If Jerry doesn't see the question in the UI, the issue is likely:")
    print("   - Frontend not refreshing questions automatically")
    print("   - Field name mismatches in the UI")
    print("   - Caching issues in the browser")
    print("\n🔄 Try using the Refresh button in the moderator view!")

if __name__ == "__main__":
    main()
