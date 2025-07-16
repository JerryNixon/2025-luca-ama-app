#!/usr/bin/env python3
"""
Button Performance Diagnostic Script
Tests API response times for all button actions to identify performance bottlenecks.
"""

import time
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000'
AUTH_HEADERS = {
    'Authorization': 'Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0',  # Admin token
    'Content-Type': 'application/json'
}

class PerformanceTimer:
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        print(f"🔄 Starting {self.operation_name}...")
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "✅" if exc_type is None else "❌"
        print(f"{status} {self.operation_name} completed in {duration:.3f}s")
        if duration > 0.5:
            print(f"⚠️  WARNING: {self.operation_name} took longer than 500ms - users will notice lag!")
        elif duration > 1.0:
            print(f"🚨 CRITICAL: {self.operation_name} took longer than 1 second - this is very slow!")
        return False

def test_api_endpoint(method, url, data=None, description=""):
    """Test a single API endpoint and measure response time"""
    with PerformanceTimer(f"{method} {description}"):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=AUTH_HEADERS, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=AUTH_HEADERS, json=data, timeout=10)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=AUTH_HEADERS, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=AUTH_HEADERS, timeout=10)
            
            if response.status_code >= 400:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return response.status_code, None
            
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, None
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: {description} took longer than 10 seconds!")
            return None, "TIMEOUT"
        except Exception as e:
            print(f"❌ Error in {description}: {e}")
            return None, str(e)

def test_database_connectivity():
    """Test database response times"""
    print("\n🗄️  Testing Database Connectivity...")
    
    # Test basic database query (get events)
    status, result = test_api_endpoint(
        'GET', f'{BASE_URL}/api/events/', 
        description="Database - Get Events"
    )
    
    if status == 200 and result:
        print(f"📊 Found {len(result)} events in database")
        return result[0]['id'] if result else None
    return None

def test_question_operations(event_id):
    """Test all question-related operations that correspond to frontend buttons"""
    print(f"\n🎯 Testing Question Operations for Event {event_id}...")
    
    # Test getting questions (what happens on page load/refresh)
    status, questions = test_api_endpoint(
        'GET', f'{BASE_URL}/api/events/{event_id}/questions/',
        description="Get Questions (Page Load)"
    )
    
    if not questions or len(questions) == 0:
        print("❌ No questions found, creating a test question...")
        status, new_question = test_api_endpoint(
            'POST', f'{BASE_URL}/api/events/{event_id}/questions/',
            data={'text': 'Test question for performance testing', 'is_anonymous': False},
            description="Create Test Question"
        )
        if status == 201:
            question_id = new_question['id']
            print(f"✅ Created test question with ID: {question_id}")
        else:
            print("❌ Failed to create test question")
            return
    else:
        question_id = questions[0]['id']
        print(f"📝 Using existing question ID: {question_id}")
    
    # Test button operations in sequence
    operations = [
        # Upvote button
        ('POST', f'{BASE_URL}/api/questions/{question_id}/upvote/', None, "Upvote Question"),
        ('DELETE', f'{BASE_URL}/api/questions/{question_id}/upvote/', None, "Remove Upvote"),
        
        # Star button (moderator action)
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_starred': True}, "Star Question"),
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_starred': False}, "Unstar Question"),
        
        # Stage button (moderator action) - using dedicated endpoint
        ('POST', f'{BASE_URL}/api/questions/{question_id}/stage/', None, "Stage Question"),
        ('POST', f'{BASE_URL}/api/questions/{question_id}/stage/', None, "Unstage Question"),
        
        # Answer button (moderator action)
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_answered': True}, "Mark as Answered"),
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_answered': False}, "Mark as Unanswered"),
        
        # Presenter notes (moderator action)
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'presenter_notes': 'Test notes'}, "Add Presenter Notes"),
    ]
    
    print(f"\n🧪 Testing {len(operations)} button operations...")
    
    total_time = 0
    slow_operations = []
    
    for method, url, data, description in operations:
        start_time = time.time()
        status, result = test_api_endpoint(method, url, data, description)
        operation_time = time.time() - start_time
        total_time += operation_time
        
        if operation_time > 0.3:  # Operations taking longer than 300ms
            slow_operations.append((description, operation_time))
        
        if status and status >= 400:
            print(f"⚠️  HTTP {status} for {description}")
        
        # Small delay between operations to simulate user interaction
        time.sleep(0.1)
    
    print(f"\n📊 PERFORMANCE SUMMARY:")
    print(f"📊 Total time for all button operations: {total_time:.3f}s")
    print(f"📊 Average time per operation: {total_time/len(operations):.3f}s")
    
    if slow_operations:
        print(f"\n🐌 SLOW OPERATIONS (>300ms):")
        for op, duration in slow_operations:
            print(f"   • {op}: {duration:.3f}s")
    else:
        print(f"\n🚀 All operations completed quickly (<300ms)")

def test_frontend_performance():
    """Test frontend static file loading times"""
    print("\n🌐 Testing Frontend Performance...")
    
    # Test main page load
    with PerformanceTimer("Frontend - Main Page Load"):
        try:
            response = requests.get('http://localhost:3000', timeout=10)
            print(f"📄 Frontend status: {response.status_code}")
            content_length = len(response.content)
            print(f"📄 Response size: {content_length:,} bytes")
        except Exception as e:
            print(f"⚠️  Frontend may not be running: {e}")

def test_concurrent_requests(event_id, question_id):
    """Test what happens when multiple button clicks happen quickly"""
    print(f"\n⚡ Testing Concurrent Button Clicks...")
    
    # Simulate rapid clicking scenario
    operations = [
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_starred': True}, "Rapid Star #1"),
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_starred': False}, "Rapid Star #2"),
        ('PATCH', f'{BASE_URL}/api/questions/{question_id}/', {'is_starred': True}, "Rapid Star #3"),
    ]
    
    start_time = time.time()
    
    for method, url, data, description in operations:
        test_api_endpoint(method, url, data, description)
        time.sleep(0.05)  # Very rapid clicks (50ms apart)
    
    total_time = time.time() - start_time
    print(f"📊 Three rapid operations completed in: {total_time:.3f}s")

def run_performance_diagnostics():
    """Run comprehensive performance diagnostics"""
    print("🚀 Starting Button Performance Diagnostics")
    print("=" * 60)
    
    # Test database connectivity and get event ID
    event_id = test_database_connectivity()
    
    if not event_id:
        print("❌ Cannot continue without valid event ID")
        return
    
    # Test question operations (the actual button actions)
    test_question_operations(event_id)
    
    # Test frontend performance
    test_frontend_performance()
    
    # Get a question ID for concurrent testing
    status, questions = test_api_endpoint(
        'GET', f'{BASE_URL}/api/events/{event_id}/questions/',
        description="Get Question for Concurrency Test"
    )
    
    if questions and len(questions) > 0:
        test_concurrent_requests(event_id, questions[0]['id'])
    
    print("\n" + "=" * 60)
    print("📋 PERFORMANCE ANALYSIS COMPLETE")
    print("\n🔍 What the results mean:")
    print("• < 100ms: Excellent - feels instant")
    print("• 100-300ms: Good - slight delay but acceptable")
    print("• 300-500ms: Noticeable lag - users will feel it")
    print("• 500ms+: Poor - very sluggish, investigate immediately")
    print("• 1s+: Critical - unacceptable for button clicks")
    
    print("\n🔧 Common causes of slow buttons:")
    print("• Database queries without indexes")
    print("• Complex business logic in views")
    print("• Network latency (less likely on localhost)")
    print("• Frontend JavaScript blocking main thread")
    print("• Missing database connection pooling")

if __name__ == "__main__":
    run_performance_diagnostics()
