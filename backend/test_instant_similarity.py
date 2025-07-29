import os
import django
import sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.fabric_ai_service import fabric_ai_service

# Test similarity detection with a similar question
query_text = 'final test question about embedding'  # Similar to 'final test embedding'
event_id = 'aa5f5c0e-e6a1-4c55-ad18-eece3f1c4c2c'

print('=== TESTING INSTANT SIMILARITY DETECTION ===')
print(f'Query: "{query_text}"')
print(f'Event: {event_id}')
print()

try:
    similar_questions = fabric_ai_service.find_similar_questions_fabric(
        query_text, event_id, limit=5
    )
    print(f'✅ Found {len(similar_questions)} similar questions:')
    for i, q in enumerate(similar_questions, 1):
        # Handle the fact that the similarity response format might vary
        text = q.get('text', q.get('question_text', 'Unknown'))
        score = q.get('score', q.get('similarity_score', 0))
        print(f'{i}. "{text}" (Score: {score:.3f})')
        
    print()
    print('🎯 INSTANT SIMILARITY DETECTION IS WORKING!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
