#!/usr/bin/env python3
"""
Debug Stage API Endpoint
Tests the staging endpoint directly to identify the issue.
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_stage_endpoint():
    """Test the staging endpoint to debug the error"""
    print("🔍 Testing Stage API Endpoint...")
    
    # First, try to get events and questions
    try:
        print("\n1. Testing basic API access...")
        events_response = requests.get(f'{BASE_URL}/api/events/')
        print(f"Events endpoint status: {events_response.status_code}")
        
        if events_response.status_code == 200:
            events = events_response.json()
            if events:
                event_id = events[0]['id']
                print(f"✅ Found event ID: {event_id}")
                
                # Get questions for this event
                questions_response = requests.get(f'{BASE_URL}/api/events/{event_id}/questions/')
                print(f"Questions endpoint status: {questions_response.status_code}")
                
                if questions_response.status_code == 200:
                    questions = questions_response.json()
                    if questions:
                        question_id = questions[0]['id']
                        print(f"✅ Found question ID: {question_id}")
                        
                        # Test the staging endpoint
                        print(f"\n2. Testing staging endpoint...")
                        stage_url = f'{BASE_URL}/api/questions/{question_id}/stage/'
                        
                        print(f"Calling POST {stage_url}")
                        stage_response = requests.post(stage_url)
                        
                        print(f"Stage response status: {stage_response.status_code}")
                        print(f"Stage response headers: {dict(stage_response.headers)}")
                        
                        try:
                            response_data = stage_response.json()
                            print(f"Stage response data: {json.dumps(response_data, indent=2)}")
                        except:
                            print(f"Stage response text: {stage_response.text}")
                        
                        # Check if the endpoint exists
                        if stage_response.status_code == 404:
                            print("\n❌ Stage endpoint not found!")
                            print("Let's check what endpoints are available...")
                            
                            # Try alternative endpoints
                            alternatives = [
                                f'/api/questions/{question_id}/',
                                f'/api/questions/{question_id}/toggle-stage/',
                                f'/api/questions/{question_id}/staging/',
                            ]
                            
                            for alt_url in alternatives:
                                test_response = requests.post(f'{BASE_URL}{alt_url}')
                                print(f"  {alt_url}: {test_response.status_code}")
                        
                    else:
                        print("❌ No questions found")
                else:
                    print(f"❌ Questions request failed: {questions_response.text}")
            else:
                print("❌ No events found")
        else:
            print(f"❌ Events request failed: {events_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_structure():
    """Check the API structure"""
    print("\n🏗️  Checking API URL Structure...")
    
    # Test common endpoints
    endpoints = [
        '/api/',
        '/api/events/',
        '/api/questions/',
        '/admin/',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")

if __name__ == "__main__":
    test_api_structure()
    test_stage_endpoint()
