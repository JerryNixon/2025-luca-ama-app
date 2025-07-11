#!/usr/bin/env python3
"""
Quick Button Response Test
Tests the actual API endpoints that the frontend buttons use.
"""

import time
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_auth_and_get_token():
    """Test basic authentication and get a working token"""
    print("🔑 Testing authentication...")
    
    # Try to access events without auth
    start = time.time()
    response = requests.get(f'{BASE_URL}/api/events/')
    duration = time.time() - start
    print(f"No auth request took: {duration:.3f}s, status: {response.status_code}")
    
    # Try with admin endpoint
    admin_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        start = time.time()
        auth_response = requests.post(f'{BASE_URL}/api/auth/login/', json=admin_data)
        auth_duration = time.time() - start
        print(f"Auth request took: {auth_duration:.3f}s, status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            token = data.get('access_token')
            if token:
                print(f"✅ Got auth token: {token[:20]}...")
                return token
    except Exception as e:
        print(f"Auth failed: {e}")
    
    return None

def test_button_endpoints(token=None):
    """Test the specific endpoints that buttons call"""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    print(f"\n🧪 Testing API endpoints (with auth: {bool(token)})...")
    
    # Test getting events (page load)
    start = time.time()
    try:
        response = requests.get(f'{BASE_URL}/api/events/', headers=headers, timeout=5)
        duration = time.time() - start
        print(f"📊 GET /api/events/ - {duration:.3f}s (Status: {response.status_code})")
        
        if response.status_code == 200:
            events = response.json()
            if events:
                event_id = events[0]['id']
                print(f"Using event ID: {event_id}")
                
                # Test getting questions for an event
                start = time.time()
                questions_response = requests.get(f'{BASE_URL}/api/events/{event_id}/questions/', headers=headers, timeout=5)
                duration = time.time() - start
                print(f"📊 GET /api/events/{event_id}/questions/ - {duration:.3f}s (Status: {questions_response.status_code})")
                
                if questions_response.status_code == 200:
                    questions = questions_response.json()
                    if questions:
                        question_id = questions[0]['id']
                        print(f"Using question ID: {question_id}")
                        
                        # Test the button operations
                        button_tests = [
                            ('POST', f'/api/questions/{question_id}/upvote/', None, 'Upvote'),
                            ('PATCH', f'/api/questions/{question_id}/', {'is_starred': True}, 'Star'),
                            ('POST', f'/api/questions/{question_id}/stage/', None, 'Stage'),
                            ('PATCH', f'/api/questions/{question_id}/', {'is_answered': True}, 'Answer'),
                        ]
                        
                        print(f"\n🎯 Testing button operations...")
                        for method, endpoint, data, name in button_tests:
                            start = time.time()
                            try:
                                if method == 'POST':
                                    resp = requests.post(f'{BASE_URL}{endpoint}', headers=headers, json=data, timeout=5)
                                elif method == 'PATCH':
                                    resp = requests.patch(f'{BASE_URL}{endpoint}', headers=headers, json=data, timeout=5)
                                
                                duration = time.time() - start
                                status_icon = "✅" if resp.status_code < 400 else "❌"
                                lag_icon = "🐌" if duration > 0.5 else "⚡" if duration < 0.1 else "📊"
                                
                                print(f"{status_icon} {lag_icon} {name} Button - {duration:.3f}s (Status: {resp.status_code})")
                                
                                if duration > 0.5:
                                    print(f"   ⚠️  This will feel sluggish to users!")
                                
                            except requests.exceptions.Timeout:
                                print(f"❌ ⏰ {name} Button - TIMEOUT (>5s)")
                            except Exception as e:
                                print(f"❌ {name} Button - Error: {e}")
    
    except requests.exceptions.Timeout:
        print(f"❌ ⏰ GET /api/events/ - TIMEOUT (>5s)")
    except Exception as e:
        print(f"❌ GET /api/events/ - Error: {e}")

def main():
    print("🚀 Quick Button Performance Test")
    print("=" * 50)
    
    # Test without authentication first
    test_button_endpoints(token=None)
    
    # Try to get authentication
    token = test_auth_and_get_token()
    if token:
        test_button_endpoints(token=token)
    
    print("\n" + "=" * 50)
    print("📋 ANALYSIS:")
    print("• < 100ms: Instant (⚡)")
    print("• 100-500ms: Acceptable (📊)")
    print("• > 500ms: Sluggish (🐌)")
    print("• > 1s: Very slow")
    print("• Timeout: Critical issue")
    
    print("\n🔍 If you see slow responses:")
    print("• Check if you're using a remote database (Fabric SQL)")
    print("• Consider caching frequently accessed data")
    print("• Add database indexes for common queries")
    print("• Use local database for development")

if __name__ == "__main__":
    main()
