#!/usr/bin/env python3
"""
API Endpoint Testing Script for AMA App
Tests all the REST API endpoints to ensure they work correctly
"""

import requests
import json
import sys
from datetime import datetime

class AMAAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            
            print(f"{'✅' if success else '❌'} {method.upper()} {endpoint}")
            print(f"   Status: {response.status_code} (expected {expected_status})")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict) and 'data' in json_data:
                        print(f"   Data: {len(json_data['data'])} items" if isinstance(json_data['data'], list) else "Data returned")
                    else:
                        print(f"   Response: {str(json_data)[:100]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"   Response: {response.text[:100]}...")
            
            print()
            return success, response
            
        except requests.exceptions.ConnectionError:
            print(f"❌ {method.upper()} {endpoint}")
            print("   Error: Cannot connect to server. Is Django running?")
            print()
            return False, None
        except Exception as e:
            print(f"❌ {method.upper()} {endpoint}")
            print(f"   Error: {str(e)}")
            print()
            return False, None
    
    def run_all_tests(self):
        """Run all API endpoint tests"""
        print("🚀 AMA API Endpoint Testing")
        print("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        
        # Test 1: Health check / Root endpoint
        success, _ = self.test_endpoint('GET', '/api/')
        total_tests += 1
        if success: passed_tests += 1
        
        # Test 2: List all events
        success, events_response = self.test_endpoint('GET', '/api/events/')
        total_tests += 1
        if success: passed_tests += 1
        
        # Test 3: Get specific event (if we have events)
        event_id = None
        if events_response and events_response.status_code == 200:
            try:
                events_data = events_response.json()
                if events_data.get('data') and len(events_data['data']) > 0:
                    event_id = events_data['data'][0]['id']
                    success, _ = self.test_endpoint('GET', f'/api/events/{event_id}/')
                    total_tests += 1
                    if success: passed_tests += 1
                else:
                    print("ℹ️  No events found, skipping specific event test")
            except:
                print("⚠️  Could not parse events response")
        
        # Test 4: Get questions for specific event
        if event_id:
            success, questions_response = self.test_endpoint('GET', f'/api/events/{event_id}/questions/')
            total_tests += 1
            if success: passed_tests += 1
        else:
            print("ℹ️  No event ID available, skipping event questions test")
        
        # Test 5: List all questions
        success, _ = self.test_endpoint('GET', '/api/questions/')
        total_tests += 1
        if success: passed_tests += 1
        
        # Test 6: Create new question (POST)
        if event_id:
            test_question_data = {
                "event": event_id,
                "text": f"🧪 Test question created at {datetime.now().strftime('%H:%M:%S')}",
                "author": "040838ad-ad2f-424c-818a-d7755bf07bdd",  # Sam Participant ID
                "is_anonymous": False
            }
            success, create_response = self.test_endpoint('POST', '/api/questions/', test_question_data, 201)
            total_tests += 1
            if success: passed_tests += 1
            
            # Test 7: Update the created question (PUT)
            if create_response and create_response.status_code == 201:
                try:
                    created_question = create_response.json()
                    if created_question.get('data'):
                        question_id = created_question['data']['id']
                        update_data = {
                            "text": f"🔄 Updated test question at {datetime.now().strftime('%H:%M:%S')}",
                            "upvotes": 5
                        }
                        success, _ = self.test_endpoint('PUT', f'/api/questions/{question_id}/', update_data)
                        total_tests += 1
                        if success: passed_tests += 1
                        
                        # Test 8: Delete the test question
                        success, _ = self.test_endpoint('DELETE', f'/api/questions/{question_id}/', expected_status=204)
                        total_tests += 1
                        if success: passed_tests += 1
                except Exception as e:
                    print(f"⚠️  Could not test question update/delete: {e}")
        else:
            print("ℹ️  No event ID available, skipping question create/update/delete tests")
        
        # Test 9: Test non-existent endpoint (should return 404)
        success, _ = self.test_endpoint('GET', '/api/nonexistent/', expected_status=404)
        total_tests += 1
        if success: passed_tests += 1
        
        # Test Results Summary
        print("📊 Test Results Summary")
        print("=" * 30)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All API tests passed! Your endpoints are working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Check the errors above.")
            
        return passed_tests == total_tests

def main():
    """Run the API tests"""
    print("Starting AMA API endpoint tests...")
    print("Make sure your Django server is running on localhost:8000\n")
    
    tester = AMAAPITester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
