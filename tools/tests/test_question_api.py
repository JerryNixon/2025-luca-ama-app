#!/usr/bin/env python3
"""
Test script to verify the question API functionality
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'
EVENT_ID = 'abe6ad88-b6ff-4cc6-9f83-2003e54c69bb'  # Luca Town hall

def login_user(email, password):
    """Login and get JWT token"""
    print(f"🔐 Logging in as {email}...")
    response = requests.post(f'{BASE_URL}/auth/login/', json={
        'email': email,
        'password': password
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            token = data['data']['token']
            user = data['data']['user']
            print(f"✅ Logged in successfully as {user['name']} ({user['role']})")
            return token, user
        else:
            print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
            return None, None
    else:
        print(f"❌ Login failed with status {response.status_code}: {response.text}")
        return None, None

def get_event(token, event_id):
    """Get event details"""
    print(f"📅 Getting event {event_id}...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/events/{event_id}/', headers=headers)
    
    if response.status_code == 200:
        event = response.json()
        print(f"✅ Event found: {event['name']}")
        return event
    else:
        print(f"❌ Failed to get event: {response.status_code} - {response.text}")
        return None

def get_questions(token, event_id):
    """Get questions for event"""
    print(f"❓ Getting questions for event {event_id}...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/events/{event_id}/questions/', headers=headers)
    
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ Found {len(questions)} questions")
        for i, q in enumerate(questions):
            print(f"   {i+1}. {q['text'][:50]}... by {q['author']['name']}")
        return questions
    else:
        print(f"❌ Failed to get questions: {response.status_code} - {response.text}")
        return None

def create_question(token, event_id, text, is_anonymous=False):
    """Create a new question"""
    print(f"➕ Creating new question...")
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'text': text,
        'is_anonymous': is_anonymous
    }
    response = requests.post(f'{BASE_URL}/events/{event_id}/questions/', 
                           headers=headers, json=data)
    
    if response.status_code == 201:
        question = response.json()
        print(f"✅ Question created successfully: {question['id']}")
        return question
    else:
        print(f"❌ Failed to create question: {response.status_code} - {response.text}")
        return None

def main():
    print("🧪 Testing Question API Functionality")
    print("=" * 50)
    
    # Login as Jerry
    token, user = login_user('jerry.nixon@microsoft.com', 'test123')
    if not token:
        print("❌ Cannot proceed without login")
        return
    
    # Get event details
    event = get_event(token, EVENT_ID)
    if not event:
        print("❌ Cannot proceed without event access")
        return
    
    # Get existing questions
    questions_before = get_questions(token, EVENT_ID)
    if questions_before is None:
        print("❌ Cannot get questions")
        return
    
    # Create a new question
    test_question = f"Test question from API script at {requests.get('http://worldtimeapi.org/api/timezone/America/Los_Angeles').json()['datetime']}"
    new_question = create_question(token, EVENT_ID, test_question)
    
    if new_question:
        # Get questions again to verify
        questions_after = get_questions(token, EVENT_ID)
        if questions_after and len(questions_after) > len(questions_before):
            print("✅ Question was successfully added and persisted!")
        else:
            print("❌ Question might not have been saved properly")
    
    print("\n🎉 Test completed!")

if __name__ == '__main__':
    main()
