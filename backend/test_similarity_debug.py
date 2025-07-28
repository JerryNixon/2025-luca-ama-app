#!/usr/bin/env python3
"""
Test Similarity Detection Directly
This will help us understand why similar questions aren't being found
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.fabric_ai_service import fabric_ai_service
from api.models import Question

print("🔍 SIMILARITY DETECTION DEBUG")
print("=" * 50)

# Test parameters
test_question = "how is the weather like today?"
event_id = "abe6ad88-b6ff-4cc6-9f83-2003e54c69bb"

print(f"📝 Test question: '{test_question}'")
print(f"🎯 Event ID: {event_id}")
print(f"🔧 Similarity threshold: {fabric_ai_service.similarity_threshold}")
print(f"🤖 Azure OpenAI client: {'✅ Available' if fabric_ai_service.azure_client else '❌ Not available'}")
print()

# Check what questions exist in the database
print("📊 Questions in database:")
questions = Question.objects.filter(event_id=event_id).values('id', 'text', 'embedding_vector')
for i, q in enumerate(questions, 1):
    has_embedding = q['embedding_vector'] is not None
    print(f"  {i}. \"{q['text']}\" [{'✅' if has_embedding else '❌'} embedding]")
print()

# Generate embedding for our test question
print("🚀 Generating embedding for test question...")
try:
    embedding_binary, embedding_json = fabric_ai_service.generate_embedding_with_fabric(test_question)
    if embedding_binary:
        print(f"✅ Test embedding generated ({len(embedding_binary)} bytes)")
    else:
        print("❌ Failed to generate test embedding")
        exit(1)
except Exception as e:
    print(f"❌ Error generating embedding: {e}")
    exit(1)

# Test similarity detection
print("\n🔍 Testing similarity detection...")
try:
    similar_questions = fabric_ai_service.find_similar_questions_fabric(
        test_question,
        event_id,
        limit=5
    )
    
    print(f"📋 Found {len(similar_questions)} similar questions:")
    for i, q in enumerate(similar_questions, 1):
        print(f"  {i}. \"{q['text']}\" (similarity: {q['similarity_score']:.3f})")
    
    if len(similar_questions) == 0:
        print("\n🔍 DEBUG: Why no similar questions found?")
        print("Let's check individual similarity scores...")
        
        # Manual similarity check
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TOP 10
                    q.text,
                    CASE 
                        WHEN q.embedding_vector IS NOT NULL 
                        THEN 1.0 - VECTOR_DISTANCE(q.embedding_vector, %s, 'cosine')
                        ELSE 0.0 
                    END as similarity_score
                FROM api_question q
                WHERE q.event_id = %s 
                    AND q.embedding_vector IS NOT NULL
                ORDER BY similarity_score DESC
            """, [embedding_binary, event_id])
            
            results = cursor.fetchall()
            print(f"\n📊 Raw similarity scores:")
            for text, score in results:
                print(f"  - \"{text[:40]}...\" = {score:.3f} {'✅' if score >= fabric_ai_service.similarity_threshold else '❌'}")

except Exception as e:
    print(f"❌ Error in similarity detection: {e}")
    import traceback
    traceback.print_exc()
