#!/usr/bin/env python3
"""
Test similarity with actual similar questions
"""

import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import Question, Event
from api.fabric_ai_service import FabricAIService

def main():
    print("🧪 Testing AI similarity detection with similar questions...")
    
    # Find the test event
    test_event = Event.objects.filter(name__icontains="Fabric Quick Test").first()
    if not test_event:
        print("❌ Test event not found")
        return
    
    ai_service = FabricAIService()
    
    # Test with questions very similar to the existing ones
    test_questions = [
        "How does machine learning differ from traditional programming?",  # Exact match
        "What's the difference between ML and traditional programming?",   # Very similar 
        "How is machine learning different from regular programming?",     # Very similar
        "What makes machine learning different from normal coding?",       # Similar concept
        "How does weather prediction work?",                               # Completely different
    ]
    
    for test_q in test_questions:
        print(f"\n🔍 Testing: '{test_q}'")
        similar = ai_service.find_similar_questions_fabric(test_q, str(test_event.id), 10)
        print(f"   Found {len(similar)} similar questions")
        
        for sim in similar:
            print(f"   - Score: {sim['similarity_score']:.3f} | Text: {sim['text']}")

if __name__ == "__main__":
    main()
