#!/usr/bin/env python3
"""
Test AMA API Endpoints
=====================
Test the Django REST API endpoints with sample data
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = 'http://127.0.0.1:8000/api'

def test_api_endpoints():
    """Test various AMA API endpoints"""
    
    print("🔗 Testing AMA API Endpoints...")
    print("-" * 50)
    
    # Test endpoints
    endpoints = [
        ('GET', '/events/', 'List all events'),
        ('GET', '/events/public/', 'List public events'),
        ('GET', '/users/', 'List all users'),
    ]
    
    # Test each endpoint
    for method, endpoint, description in endpoints:
        try:
            print(f"📡 Testing: {description}")
            print(f"   {method} {BASE_URL}{endpoint}")
            
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Success: {len(data)} items returned")
                else:
                    print(f"   ✅ Success: Response received")
                
                # Show first item if it's a list
                if isinstance(data, list) and len(data) > 0:
                    print(f"   📄 First item: {json.dumps(data[0], indent=2)[:200]}...")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            
        print()
    
    print("🎪 Sample Event Share Links (you can access these):")
    share_links = [
        'kALgQSbAsdee',  # Tech Leadership AMA
        'HU5NVQ4c2bwk',  # Supabase vs Traditional Databases  
        '4BXmkgMP6f19'   # Career Development Q&A
    ]
    
    for link in share_links:
        print(f"   🔗 http://127.0.0.1:8000/api/events/join/{link}/")
    
    print("\n💡 You can test these URLs in your browser or with curl!")

if __name__ == "__main__":
    test_api_endpoints()
