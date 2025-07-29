#!/usr/bin/env python3
"""
Test script to check if questions have embeddings and debug similarity detection
"""

import os
import sys
import django
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import Question, Event
from api.fabric_ai_service import FabricAIService

def main():
    print("🔍 Checking questions and embeddings...")
    
    # Find the test event
    test_event = Event.objects.filter(title__icontains="Fabric Quick Test").first()
    if not test_event:
        print("❌ Test event not found")
        return
    
    print(f"✅ Found test event: {test_event.title}")
    
    # Get all questions for this event
    questions = Question.objects.filter(event_id=test_event.id)
    print(f"📝 Event has {questions.count()} questions")
    
    for q in questions:
        print(f"\n🔍 Question: {q.text[:50]}...")
        print(f"   ID: {q.id}")
        print(f"   Has embedding_json: {bool(q.embedding_json)}")
        print(f"   Fabric AI processed: {q.fabric_ai_processed}")
        print(f"   Has valid embedding: {q.has_valid_embedding()}")
        
        if q.embedding_json:
            try:
                embedding = json.loads(q.embedding_json)
                print(f"   Embedding length: {len(embedding)}")
                print(f"   First 3 values: {embedding[:3]}")
            except:
                print(f"   ❌ Invalid embedding JSON")
    
    # Test similarity with a simple question
    print(f"\n🧪 Testing similarity detection...")
    ai_service = FabricAIService()
    
    # Test with different questions
    test_questions = [
        "what is the weather like",
        "how are you doing",
        "tell me about your work",
        "what do you think about ai"
    ]
    
    for test_q in test_questions:
        print(f"\n🔍 Testing: '{test_q}'")
        similar = ai_service.find_similar_questions_fabric(test_q, str(test_event.id), 10)
        print(f"   Found {len(similar)} similar questions")
        
        for sim in similar:
            print(f"   - Score: {sim['similarity_score']:.3f} | Text: {sim['text'][:50]}...")

if __name__ == "__main__":
    main()
