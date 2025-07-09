#!/usr/bin/env python3
"""
Phase 1: Test OpenAI Embedding Integration
Goal: Verify we can get embeddings from OpenAI API
Test: Embed 3 simple words, verify dimensions
"""

import os
import sys
from pathlib import Path
import openai
from dotenv import load_dotenv
import json
import time

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_embedding(text: str, model="text-embedding-3-large") -> list[float]:
    """Get embedding for a single text using OpenAI API"""
    try:
        start_time = time.time()
        
        response = openai.embeddings.create(
            input=text,
            model=model
        )
        
        embedding = response.data[0].embedding
        elapsed_time = time.time() - start_time
        
        print(f"✅ Embedded '{text}' in {elapsed_time:.3f}s")
        print(f"   Dimensions: {len(embedding)}")
        
        return embedding
    
    except Exception as e:
        print(f"❌ Error embedding '{text}': {e}")
        return None

def test_basic_embeddings():
    """Test embedding 3 simple words"""
    print("=== Phase 1: OpenAI Embedding Test ===\n")
    
    # Test words
    test_words = ["hello", "world", "cat"]
    embeddings = {}
    
    for word in test_words:
        print(f"Testing word: '{word}'")
        embedding = get_embedding(word)
        
        if embedding:
            embeddings[word] = {
                "dimensions": len(embedding),
                "first_5": embedding[:5],
                "last_5": embedding[-5:]
            }
            print(f"   First 5 values: {embedding[:5]}")
            print(f"   Last 5 values: {embedding[-5:]}")
            print()
    
    # Summary
    print("\n=== Summary ===")
    print(f"Successfully embedded {len(embeddings)}/{len(test_words)} words")
    
    if embeddings:
        first_word = list(embeddings.keys())[0]
        expected_dims = 3072  # text-embedding-3-large
        actual_dims = embeddings[first_word]["dimensions"]
        
        print(f"Expected dimensions: {expected_dims}")
        print(f"Actual dimensions: {actual_dims}")
        print(f"Dimensions match: {'✅' if actual_dims == expected_dims else '❌'}")
        
        # Save results
        with open("embedding_results.json", "w") as f:
            json.dump(embeddings, f, indent=2)
        print(f"\nResults saved to embedding_results.json")
        
        return actual_dims == expected_dims
    
    return False

if __name__ == "__main__":
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    # Run test
    success = test_basic_embeddings()
    
    if success:
        print("\n✅ Phase 1 PASSED: OpenAI embeddings working!")
        sys.exit(0)
    else:
        print("\n❌ Phase 1 FAILED: Check errors above")
        sys.exit(1)