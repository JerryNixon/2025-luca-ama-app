import os
import django
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)
os.chdir(backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import Event

def test_is_active_field():
    """Test if is_active field is working"""
    print("🧪 Testing is_active field...")
    
    # Check if the field exists in the model
    try:
        field = Event._meta.get_field('is_active')
        print(f"✅ Field exists: {field}")
        print(f"   Type: {type(field)}")
        print(f"   Default: {field.default}")
    except Exception as e:
        print(f"❌ Field not found: {e}")
    
    # Try to create an event directly without serializer
    print("\n🔧 Testing direct model creation...")
    from api.models import User
    
    # Get a user to use as creator
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    try:
        # Try creating with is_active explicitly
        event = Event.objects.create(
            name="Direct Test Event",
            created_by=user,
            is_active=True
        )
        print(f"✅ Event created successfully: {event.id}")
        print(f"   is_active value: {event.is_active}")
        
        # Clean up
        event.delete()
        print("✅ Event deleted")
        
    except Exception as e:
        print(f"❌ Failed to create event: {e}")

if __name__ == "__main__":
    test_is_active_field()
