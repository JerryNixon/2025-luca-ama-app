import os
import sys

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
import django
django.setup()

# Import models
from api.models import User, Event, Question

print("🔍 Testing Fabric SQL Database...")
print(f"Users: {User.objects.count()}")
print(f"Events: {Event.objects.count()}")
print(f"Questions: {Question.objects.count()}")

# Show some users
users = User.objects.all()[:5]
print("\n👥 Users:")
for user in users:
    print(f"  - {user.username} ({user.email}) - {user.role}")
