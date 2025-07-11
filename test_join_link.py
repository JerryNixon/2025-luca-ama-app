import requests
import json

def test_join_link_api():
    """Test the join link API endpoint"""
    share_link = "gf2lqnGt"
    
    print(f"🔗 Testing join link API for: {share_link}")
    print("=" * 50)
    
    # Test the backend API endpoint for join link
    api_url = f"http://127.0.0.1:8000/api/events/join/{share_link}/"
    
    print(f"📡 GET {api_url}")
    
    try:
        response = requests.get(api_url)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Event data:")
            print(f"   Full response: {json.dumps(data, indent=2)}")
            print(f"   Event ID: {data.get('event_id')}")
            print(f"   Event Name: {data.get('event_name')}")
            print(f"   Created By: {data.get('created_by')}")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Error response:")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend - is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_join_link_api()
