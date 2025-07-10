#!/usr/bin/env python3
"""
Test script to verify "only one question on stage at a time" logic.

This script:
1. Posts multiple questions as a user
2. Stages them one by one as a moderator
3. Verifies that only one question is staged at any time
4. Tests both the dedicated staging endpoint and general update endpoint

Usage:
    python test_staging_logic.py
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

def get_questions(token, event_id):
    """Get questions for an event."""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{QUESTIONS_URL}?event={event_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get questions: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Get questions error: {e}")
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

def stage_question_dedicated(token, question_id):
    """Stage question using dedicated staging endpoint."""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(f"{QUESTIONS_URL}{question_id}/stage/", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to stage question: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Stage question error: {e}")
        return None

def stage_question_patch(token, question_id, is_staged):
    """Stage question using general PATCH endpoint."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {'is_staged': is_staged}
        response = requests.patch(f"{QUESTIONS_URL}{question_id}/", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to update question: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Update question error: {e}")
        return None

def count_staged_questions(questions):
    """Count how many questions are currently staged."""
    return sum(1 for q in questions if q.get('is_staged', False))

def main():
    print("=== Testing 'Only One Question On Stage At A Time' Logic ===\n")
    
    # Login users
    print("1. Logging in users...")
    jerry_token, jerry_user = login_user('jerry.nixon@microsoft.com', 'test123')
    if not jerry_token:
        print("❌ Failed to login Jerry")
        return
    print(f"✅ Jerry logged in: {jerry_user['name']}")
    
    amar_token, amar_user = login_user('amapatil@microsoft.com', 'test123')
    if not amar_token:
        print("❌ Failed to login Amar")
        return
    print(f"✅ Amar logged in: {amar_user['name']}")
    
    # Find an event Jerry can moderate
    print("\n2. Finding an event Jerry can moderate...")
    jerry_events = get_events(jerry_token)
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
    print(f"✅ Found event: '{event_name}' (ID: {event_id})")
    
    # Post multiple test questions
    print("\n3. Posting multiple test questions...")
    questions = []
    for i in range(3):
        question_text = f"Test question {i+1} for staging logic - {time.strftime('%H:%M:%S')}"
        new_question = post_question(amar_token, event_id, question_text)
        if new_question:
            questions.append(new_question)
            print(f"   ✅ Posted question {i+1}: ID {new_question['id']}")
        else:
            print(f"   ❌ Failed to post question {i+1}")
            return
    
    if len(questions) < 3:
        print("❌ Need at least 3 questions for testing")
        return
    
    print(f"✅ Posted {len(questions)} test questions")
    
    # Test 1: Stage questions using dedicated endpoint
    print("\n4. Testing dedicated staging endpoint...")
    
    # Stage first question
    print("   Staging question 1...")
    result = stage_question_dedicated(jerry_token, questions[0]['id'])
    if not result:
        print("   ❌ Failed to stage question 1")
        return
    
    # Check questions state
    current_questions = get_questions(jerry_token, event_id)
    staged_count = count_staged_questions(current_questions)
    print(f"   Staged questions count: {staged_count}")
    
    if staged_count == 1:
        print("   ✅ Only one question is staged")
    else:
        print(f"   ❌ Expected 1 staged question, found {staged_count}")
        return
    
    # Stage second question (should unstage first)
    print("   Staging question 2...")
    result = stage_question_dedicated(jerry_token, questions[1]['id'])
    if not result:
        print("   ❌ Failed to stage question 2")
        return
    
    # Check questions state
    current_questions = get_questions(jerry_token, event_id)
    staged_count = count_staged_questions(current_questions)
    staged_question = next((q for q in current_questions if q.get('is_staged')), None)
    
    print(f"   Staged questions count: {staged_count}")
    if staged_count == 1 and staged_question and staged_question['id'] == questions[1]['id']:
        print("   ✅ Only question 2 is staged (question 1 was unstaged)")
    else:
        print(f"   ❌ Expected only question 2 to be staged")
        return
    
    # Test 2: Stage questions using PATCH endpoint
    print("\n5. Testing general PATCH endpoint with staging...")
    
    # Stage third question using PATCH
    print("   Staging question 3 via PATCH...")
    result = stage_question_patch(jerry_token, questions[2]['id'], True)
    if not result:
        print("   ❌ Failed to stage question 3 via PATCH")
        return
    
    # Check questions state
    current_questions = get_questions(jerry_token, event_id)
    staged_count = count_staged_questions(current_questions)
    staged_question = next((q for q in current_questions if q.get('is_staged')), None)
    
    print(f"   Staged questions count: {staged_count}")
    if staged_count == 1 and staged_question and staged_question['id'] == questions[2]['id']:
        print("   ✅ Only question 3 is staged (question 2 was unstaged)")
    else:
        print(f"   ❌ Expected only question 3 to be staged")
        return
    
    # Test 3: Unstage current question
    print("\n6. Testing unstaging...")
    
    # Unstage question 3
    print("   Unstaging question 3...")
    result = stage_question_dedicated(jerry_token, questions[2]['id'])
    if not result:
        print("   ❌ Failed to unstage question 3")
        return
    
    # Check questions state
    current_questions = get_questions(jerry_token, event_id)
    staged_count = count_staged_questions(current_questions)
    
    print(f"   Staged questions count: {staged_count}")
    if staged_count == 0:
        print("   ✅ No questions are staged")
    else:
        print(f"   ❌ Expected 0 staged questions, found {staged_count}")
        return
    
    # Summary
    print("\n=== Staging Logic Test Results ===")
    print("✅ Dedicated staging endpoint enforces 'only one staged at a time'")
    print("✅ General PATCH endpoint also enforces the rule")
    print("✅ Staging a new question automatically unstages the previous one")
    print("✅ Unstaging works correctly")
    print("✅ Question staging logic is working perfectly!")
    
    print(f"\n🎯 Test completed with event: '{event_name}' (ID: {event_id})")
    print("💡 The staging logic ensures smooth AMA session flow with clear focus")

if __name__ == "__main__":
    main()
