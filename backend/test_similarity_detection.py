#!/usr/bin/env python3
"""
Test the similarity detection functionality
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.fabric_ai_service import FabricAIService
from api.models import Event

def test_similarity_detection():
    print("🧪 Testing AI similarity detection...")
    
    ai_service = FabricAIService()
    
    # Find an event with questions
    events = Event.objects.all()
    test_event = None
    
    for event in events:
        if event.questions.count() > 0:
            test_event = event
            break
    
    if not test_event:
        print("❌ No events with questions found")
        return
    
    print(f"✅ Testing with event: {test_event.name}")
    print(f"   Event has {test_event.questions.count()} questions")
    
    # Test similarity detection
    test_question = "how is the weather today"
    
    try:
        print(f"\n🔍 Testing similarity for: '{test_question}'")
        similar_questions = ai_service.find_similar_questions_fabric(
            test_question,
            str(test_event.id),
            limit=5
        )
        
        print(f"✅ Found {len(similar_questions)} similar questions")
        for q in similar_questions:
            print(f"   - {q.get('text', 'N/A')[:60]}... (similarity: {q.get('similarity_score', 'N/A')})")
            
    except Exception as e:
        print(f"❌ Similarity detection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_similarity_detection()
