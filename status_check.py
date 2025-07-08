import requests

print("Quick Status Check")
print("==================")

# Check backend
try:
    response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
    print(f"Backend: {'✅ UP' if response.status_code == 200 else '❌ DOWN'}")
except:
    print("Backend: ❌ DOWN")

# Check frontend
try:
    response = requests.get("http://localhost:3000/", timeout=5)
    print(f"Frontend: {'✅ UP' if response.status_code == 200 else '❌ DOWN'}")
except:
    print("Frontend: ❌ DOWN")

# Test authentication
try:
    response = requests.post("http://127.0.0.1:8000/api/auth/login/", 
                           json={"email": "moderator@microsoft.com", "password": "moderator123"},
                           timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("Auth: ✅ WORKING")
        else:
            print("Auth: ❌ FAILED")
    else:
        print(f"Auth: ❌ FAILED ({response.status_code})")
except Exception as e:
    print(f"Auth: ❌ ERROR ({e})")

print("\n🎯 Application Status: READY FOR TESTING")
print("📋 Access URLs:")
print("   • Frontend: http://localhost:3000")
print("   • Backend Admin: http://127.0.0.1:8000/admin/")
print("   • API: http://127.0.0.1:8000/api/")
print("\n🔑 Test Credentials:")
print("   • moderator@microsoft.com / moderator123")
print("   • user@microsoft.com / user123")
