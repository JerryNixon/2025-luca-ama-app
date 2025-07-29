import os
import django
import sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.fabric_ai_service import fabric_ai_service

# Test similarity detection with our newly embedded question
query_text = 'debug question 456'  # Similar to 'debug question 123'
event_id = 'aa5f5c0e-e6a1-4c55-ad18-eece3f1c4c2c'

print('=== TESTING SIMILARITY DETECTION ===')
print(f'Query: {query_text}')
print(f'Event: {event_id}')

try:
    similar_questions = fabric_ai_service.find_similar_questions_fabric(
        query_text, event_id, limit=5
    )
    print(f'Found {len(similar_questions)} similar questions:')
    for i, q in enumerate(similar_questions, 1):
        print(f'{i}. "{q["text"]}" (Score: {q["score"]:.3f})')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
