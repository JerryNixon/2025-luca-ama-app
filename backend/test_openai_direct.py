#!/usr/bin/env python3
"""
Direct Azure OpenAI Test
Simple test to verify Azure OpenAI connection without Django complexity
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

print("🧪 DIRECT AZURE OPENAI TEST")
print("=" * 40)

# Check environment variables
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')
api_version = os.getenv('AZURE_OPENAI_API_VERSION')
model = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL')

print(f"📋 Configuration:")
print(f"   Endpoint: {endpoint}")
print(f"   API Version: {api_version}")
print(f"   Model: {model}")
print(f"   API Key: {'✅ SET' if api_key else '❌ NOT SET'}")
print()

if not all([endpoint, api_key, api_version, model]):
    print("❌ Missing configuration!")
    exit(1)

try:
    # Test Azure OpenAI client initialization
    print("🔧 Testing Azure OpenAI client...")
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    print("✅ Azure OpenAI client initialized successfully!")
    
    # Test embedding generation
    print("🚀 Testing embedding generation...")
    response = client.embeddings.create(
        model=model,
        input="test question for similarity"
    )
    
    embedding = response.data[0].embedding
    print(f"✅ Embedding generated! Dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    print("\n🎉 SUCCESS: Azure OpenAI is working perfectly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"   Type: {type(e)}")
    
    # Get full traceback for debugging
    import traceback
    print(f"\n🔍 FULL TRACEBACK:")
    traceback.print_exc()
    
    # Try to diagnose the issue
    if "proxies" in str(e).lower():
        print("\n🔍 DIAGNOSIS: 'Proxies' error suggests version compatibility issue")
        print("   Solution: Update OpenAI library or check initialization parameters")
    
    # Check OpenAI version details
    try:
        import openai
        print(f"\n📦 OPENAI LIBRARY INFO:")
        print(f"   Version: {openai.__version__}")
        print(f"   File location: {openai.__file__}")
    except Exception as ve:
        print(f"   Could not get version info: {ve}")
    
    exit(1)
