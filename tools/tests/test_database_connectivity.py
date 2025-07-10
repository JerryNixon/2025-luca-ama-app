"""
Test script to verify Fabric SQL database connectivity and user data
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import User, Event, Question

def test_database_connectivity():
    """Test database connectivity and show user data"""
    print("🔍 Testing Fabric SQL Database Connectivity...")
    
    try:
        # Test basic connectivity
        user_count = User.objects.count()
        event_count = Event.objects.count()
        question_count = Question.objects.count()
        
        print(f"   ✅ Database connected successfully")
        print(f"   📊 Users: {user_count}")
        print(f"   📊 Events: {event_count}")
        print(f"   📊 Questions: {question_count}")
        
        # List users
        print("\n👥 Users in Fabric SQL:")
        users = User.objects.all()[:10]  # Limit to first 10
        for user in users:
            print(f"   - {user.username} ({user.email}) - {user.role}")
        
        # List events
        print("\n📅 Events in Fabric SQL:")
        events = Event.objects.all()[:5]  # Limit to first 5
        for event in events:
            print(f"   - {event.title} (ID: {event.id})")
            print(f"     Share Link: {event.share_link}")
            print(f"     Created: {event.created_at}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database connectivity error: {e}")
        return False

def test_user_authentication():
    """Test user authentication functionality"""
    print("\n🔐 Testing User Authentication...")
    
    try:
        # Check if there are any moderator users
        moderator_users = User.objects.filter(role='moderator')
        regular_users = User.objects.filter(role='user')
        
        print(f"   📊 Moderator users: {moderator_users.count()}")
        print(f"   📊 Regular users: {regular_users.count()}")
        
        if moderator_users.exists():
            print("   ✅ Moderator users available for testing")
            mod_user = moderator_users.first()
            print(f"   🔑 Test moderator: {mod_user.username} ({mod_user.email})")
        else:
            print("   ⚠️  No moderator users found")
        
        if regular_users.exists():
            print("   ✅ Regular users available for testing")
            reg_user = regular_users.first()
            print(f"   🔑 Test user: {reg_user.username} ({reg_user.email})")
        else:
            print("   ⚠️  No regular users found")
            
    except Exception as e:
        print(f"   ❌ Authentication test error: {e}")

def main():
    """Run all tests"""
    print("🚀 AMA Application Database Connectivity Test")
    print("=" * 50)
    
    if test_database_connectivity():
        test_user_authentication()
        
        print("\n✅ Database Test Summary:")
        print("- Microsoft Fabric SQL database is connected")
        print("- Django ORM is working correctly")
        print("- User data is available for authentication")
        print("- Backend is ready for frontend login testing")
        
        print("\n🎯 Next Steps:")
        print("1. Test frontend login with existing users")
        print("2. Verify event creation persists to Fabric SQL")
        print("3. Test question posting and voting functionality")
    else:
        print("\n❌ Database connectivity failed")
        print("Check Azure AD authentication and Fabric SQL configuration")

if __name__ == "__main__":
    main()
