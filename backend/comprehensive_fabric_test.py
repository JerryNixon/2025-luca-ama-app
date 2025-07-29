#!/usr/bin/env python3
"""
Complete End-to-End Test of Similarity Detection Flow
Tests the complete journey from question creation to similarity detection
"""

import os
import sys
import django
import json
import requests
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.models import Question, Event, User
from api.fabric_ai_service import FabricAIService

def main():
    print("🧪 Complete End-to-End Similarity Detection Test")
    print("=" * 60)
    
    # Find the test event
    test_event = Event.objects.filter(name__icontains="Fabric Quick Test").first()
    if not test_event:
        print("❌ Test event not found")
        return
    
    print(f"✅ Using test event: {test_event.name}")
    print(f"   Event ID: {test_event.id}")
    
    # Test data
    new_questions = [
        "What are the best practices for machine learning projects?",
        "How do I start learning artificial intelligence?",
        "What's the weather forecast for tomorrow?",  # Different topic
    ]
    
    ai_service = FabricAIService()
    
    for i, question_text in enumerate(new_questions, 1):
        print(f"\n{'-' * 40}")
        print(f"🧪 TEST {i}: Creating and testing question")
        print(f"Question: '{question_text}'")
        
        # Step 1: Create a new question manually (simulating the API)
        try:
            # Get a test user
            user = User.objects.first()
            if not user:
                print("❌ No users found")
                continue
            
            print("📝 Step 1: Creating question in database...")
            question = Question.objects.create(
                text=question_text,
                author=user,
                event=test_event
            )
            print(f"   ✅ Question created with ID: {question.id}")
            
            # Step 2: Process with AI (simulating the perform_create logic)
            print("🤖 Step 2: Processing with AI service...")
            try:
                ai_results = ai_service.process_question_with_fabric_ai(
                    str(question.id),
                    question_text
                )
                print(f"   ✅ AI processing completed")
                print(f"   📊 Results: {ai_results}")
            except Exception as e:
                print(f"   ❌ AI processing failed: {e}")
                continue
            
            # Step 3: Verify the question has embeddings
            print("🔍 Step 3: Verifying embeddings were generated...")
            question.refresh_from_db()
            if question.embedding_json:
                embedding_data = json.loads(question.embedding_json)
                print(f"   ✅ Embedding generated: {len(embedding_data)} dimensions")
                print(f"   📊 AI processed: {question.fabric_ai_processed}")
            else:
                print(f"   ❌ No embedding generated")
                continue
            
            # Step 4: Test similarity detection (simulating frontend API call)
            print("🔍 Step 4: Testing similarity detection...")
            similar_questions = ai_service.find_similar_questions_fabric(
                question_text, str(test_event.id), 10
            )
            print(f"   📊 Found {len(similar_questions)} similar questions")
            
            for sim in similar_questions:
                # Skip self-matches
                if sim['id'] != str(question.id):
                    print(f"   - Score: {sim['similarity_score']:.3f} | Text: {sim['text'][:50]}...")
            
            # Step 5: Test with a slightly different question
            print("🔍 Step 5: Testing similarity with modified question...")
            modified_text = question_text.replace("machine learning", "ML").replace("artificial intelligence", "AI")
            similar_to_modified = ai_service.find_similar_questions_fabric(
                modified_text, str(test_event.id), 10
            )
            print(f"   📊 Modified question found {len(similar_to_modified)} similar questions")
            
            for sim in similar_to_modified:
                if sim['id'] == str(question.id):
                    print(f"   ✅ Original question detected with score: {sim['similarity_score']:.3f}")
                    break
            else:
                print(f"   ⚠️  Original question not detected as similar")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("🏁 End-to-End Test Complete!")
    
    # Final verification: show all questions in the event with their embedding status
    print(f"\n📊 Final Status - All questions in event:")
    all_questions = Question.objects.filter(event=test_event)
    for q in all_questions:
        has_embedding = bool(q.embedding_json)
        print(f"   - {q.text[:50]}... | Embedding: {has_embedding} | AI Processed: {q.fabric_ai_processed}")

if __name__ == "__main__":
    main()
