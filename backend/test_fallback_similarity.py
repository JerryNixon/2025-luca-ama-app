#!/usr/bin/env python3
"""
Fallback Similarity Detection without VECTOR_DISTANCE
Using basic cosine similarity calculation with existing embeddings
"""

import os
import django
import json
import struct
from typing import List

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ama_backend.settings')
django.setup()

from api.fabric_ai_service import fabric_ai_service
from api.models import Question

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    import numpy as np
    
    # Normalize vectors
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    
    # Calculate cosine similarity
    return np.dot(vec1_norm, vec2_norm)

def find_similar_questions_fallback(question_text: str, event_id: str, limit: int = 5):
    """Find similar questions using Python-based cosine similarity"""
    
    # Generate embedding for the input question
    embedding_binary, embedding_json = fabric_ai_service.generate_embedding_with_fabric(question_text)
    
    if not embedding_json:
        return []
    
    # Get all questions with embeddings from the database
    questions = Question.objects.filter(
        event_id=event_id,
        embedding_json__isnull=False
    ).values('id', 'text', 'embedding_json', 'upvotes', 'created_at')
    
    similarities = []
    
    for q in questions:
        try:
            # Parse the stored embedding JSON
            stored_embedding = json.loads(q['embedding_json'])
            
            # Calculate similarity
            similarity = cosine_similarity(embedding_json, stored_embedding)
            
            similarities.append({
                'id': str(q['id']),
                'text': q['text'],
                'similarity_score': float(similarity),
                'upvote_count': q['upvotes'] or 0,
                'created_at': q['created_at'].isoformat() if q['created_at'] else None
            })
            
        except Exception as e:
            print(f"Error processing question {q['id']}: {e}")
            continue
    
    # Sort by similarity score
    similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Filter by threshold and return top results
    threshold = fabric_ai_service.similarity_threshold
    filtered = [s for s in similarities if s['similarity_score'] >= threshold]
    
    return filtered[:limit]

# Test the fallback function
print("🔍 FALLBACK SIMILARITY DETECTION TEST")
print("=" * 50)

test_question = "how is the weather like today?"
event_id = "abe6ad88-b6ff-4cc6-9f83-2003e54c69bb"

print(f"📝 Test question: '{test_question}'")
print(f"🎯 Event ID: {event_id}")
print(f"🔧 Similarity threshold: {fabric_ai_service.similarity_threshold}")
print()

try:
    similar_questions = find_similar_questions_fallback(test_question, event_id, 5)
    
    print(f"📋 Found {len(similar_questions)} similar questions:")
    for i, q in enumerate(similar_questions, 1):
        print(f"  {i}. \"{q['text']}\" (similarity: {q['similarity_score']:.3f})")
        
    if len(similar_questions) > 0:
        print("\n🎉 SUCCESS: Similarity detection is working with fallback method!")
    else:
        print("\n❌ No similar questions found even with fallback method")
        
except Exception as e:
    print(f"❌ Error in fallback similarity: {e}")
    import traceback
    traceback.print_exc()
