#!/usr/bin/env python3
"""
Test script to verify moderator notes persistence functionality.

This script:
1. Tests posting a question as Amar
2. Tests adding a moderator note as Jerry
3. Verifies the note persists after refresh
4. Tests updating the note

Usage:
    python test_moderator_notes.py
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
            data = response.json()
            return data.get('token'), data.get('user')
        else:
            print(f"Login failed for {email}: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Login error for {email}: {e}")
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

def update_question(token, question_id, data):
    """Update a question with moderator notes."""
    try:
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
        response = requests.put(f"{QUESTIONS_URL}{question_id}/", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to update question: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Update question error: {e}")
        return None

def main():
    print("=== Testing Moderator Notes Persistence ===\n")
    
    # Login as Jerry (moderator)
    print("1. Logging in as Jerry...")
    jerry_token, jerry_user = login_user('jerry.nixon@microsoft.com', 'test123')
    if not jerry_token:
        print("❌ Failed to login as Jerry")
        return
    print(f"✅ Jerry logged in successfully: {jerry_user['name']}")
    
    # Login as Amar (participant)
    print("\n2. Logging in as Amar...")
    amar_token, amar_user = login_user('amapatil@microsoft.com', 'test123')
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
    
    # Find an event Jerry created or can moderate
    target_event = None
    for event in jerry_events:
        if event.get('can_user_moderate', False):
            target_event = event
            break
    
    if not target_event:
        print("❌ Jerry cannot moderate any events")
        return
    
    event_id = target_event['id']
    event_name = target_event['name']
    print(f"✅ Found event Jerry can moderate: '{event_name}' (ID: {event_id})")
    
    # Post a question as Amar (if he can access the event)
    print("\n4. Posting a test question as Amar...")
    question_text = f"Test question for moderator notes at {time.strftime('%H:%M:%S')}"
    new_question = post_question(amar_token, event_id, question_text)
    if not new_question:
        print("❌ Failed to post question as Amar")
        return
    
    question_id = new_question['id']
    print(f"✅ Question posted successfully by Amar (ID: {question_id})")
    
    # Add moderator note as Jerry
    print("\n5. Adding moderator note as Jerry...")
    note_text = f"This is an important question - reviewed at {time.strftime('%H:%M:%S')}"
    
    update_data = {
        'presenter_notes': note_text
    }
    
    updated_question = update_question(jerry_token, question_id, update_data)
    if not updated_question:
        print("❌ Failed to add moderator note")
        return
    
    print(f"✅ Moderator note added: '{note_text}'")
    
    # Verify the note was saved by fetching questions again
    print("\n6. Verifying note persistence...")
    questions = get_questions(jerry_token, event_id)
    
    # Find our specific question
    saved_question = None
    for q in questions:
        if q['id'] == question_id:
            saved_question = q
            break
    
    if not saved_question:
        print("❌ Could not find the question")
        return
    
    saved_note = saved_question.get('presenter_notes', '')
    if saved_note == note_text:
        print(f"✅ Note persisted correctly: '{saved_note}'")
    else:
        print(f"❌ Note not saved correctly. Expected: '{note_text}', Got: '{saved_note}'")
        return
    
    # Test updating the note
    print("\n7. Testing note update...")
    updated_note_text = f"Updated note - {time.strftime('%H:%M:%S')}"
    
    update_data = {
        'presenter_notes': updated_note_text
    }
    
    updated_question = update_question(jerry_token, question_id, update_data)
    if not updated_question:
        print("❌ Failed to update moderator note")
        return
    
    # Verify the updated note
    questions = get_questions(jerry_token, event_id)
    saved_question = None
    for q in questions:
        if q['id'] == question_id:
            saved_question = q
            break
    
    if saved_question and saved_question.get('presenter_notes', '') == updated_note_text:
        print(f"✅ Note updated correctly: '{updated_note_text}'")
    else:
        print(f"❌ Note update failed")
        return
    
    # Summary
    print("\n=== Summary ===")
    print(f"✅ Event: '{event_name}' (ID: {event_id})")
    print(f"✅ Question: ID {question_id}")
    print(f"✅ Moderator note created and persisted")
    print(f"✅ Moderator note updated successfully")
    print("\n💡 The moderator notes API is working correctly!")
    print("💡 If notes don't persist in the UI, check:")
    print("   - Frontend is calling the update API correctly")
    print("   - UI is refreshing question data after saving")
    print("   - Field names match between frontend and backend")

if __name__ == "__main__":
    main()
