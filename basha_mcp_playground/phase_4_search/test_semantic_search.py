#!/usr/bin/env python3
"""
Phase 4: First Semantic Search
Goal: Implement basic semantic search using pgvector
Test: Search for "greeting" should find "Hello world" document
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_embedding(text: str) -> list[float]:
    """Get embedding using text-embedding-3-large"""
    try:
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def setup_test_data():
    """Setup test documents"""
    conn = psycopg2.connect(dbname="toy_vector_test", user="kimomaxmac", host="localhost")
    cur = conn.cursor()
    
    try:
        # Clear and recreate table
        cur.execute("DROP TABLE IF EXISTS semantic_docs;")
        cur.execute("""
            CREATE TABLE semantic_docs (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(3072)
            );
        """)
        
        # Test documents
        test_docs = [
            "Hello world, this is a greeting message",
            "The cat sat on the mat",
            "Python is a programming language",
            "Good morning, how are you today?",
            "Machine learning uses vectors"
        ]
        
        print("Setting up test documents...")
        for doc in test_docs:
            embedding = get_embedding(doc)
            if embedding:
                embedding_str = f"[{','.join(map(str, embedding))}]"
                cur.execute(
                    "INSERT INTO semantic_docs (content, embedding) VALUES (%s, %s);",
                    (doc, embedding_str)
                )
                print(f"  ✓ Added: '{doc[:30]}...'")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def search_docs(query: str, top_k: int = 1):
    """Search for similar documents"""
    print(f"\nSearching for: '{query}'")
    
    # Get query embedding
    query_embedding = get_embedding(query)
    if not query_embedding:
        return None
    
    conn = psycopg2.connect(dbname="toy_vector_test", user="kimomaxmac", host="localhost")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Convert to pgvector format
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Semantic similarity search
        cur.execute("""
            SELECT 
                id,
                content,
                embedding <=> %s::vector AS distance
            FROM semantic_docs
            ORDER BY distance
            LIMIT %s;
        """, (embedding_str, top_k))
        
        results = cur.fetchall()
        return results
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def test_semantic_search():
    """Main test function"""
    print("=== Phase 4: Semantic Search Test ===\n")
    
    # 1. Setup test data
    if not setup_test_data():
        return False
    
    # 2. Test searches
    test_queries = [
        ("greeting", "Hello world"),     # Should find greeting messages
        ("animal", "cat"),              # Should find cat document
        ("coding", "Python")            # Should find programming doc
    ]
    
    print("\n--- Running test searches ---")
    all_passed = True
    
    for query, expected_word in test_queries:
        results = search_docs(query, top_k=1)
        
        if results and len(results) > 0:
            top_result = results[0]
            content = top_result['content']
            distance = top_result['distance']
            
            if expected_word.lower() in content.lower():
                print(f"✅ Query '{query}' correctly found: '{content}'")
                print(f"   Distance: {distance:.4f}")
            else:
                print(f"❌ Query '{query}' found unexpected: '{content}'")
                all_passed = False
        else:
            print(f"❌ Query '{query}' returned no results")
            all_passed = False
    
    if all_passed:
        print("\n✅ Phase 4 PASSED: Semantic search working!")
        return True
    else:
        print("\n❌ Phase 4 FAILED: Some searches didn't work as expected")
        return False

if __name__ == "__main__":
    success = test_semantic_search()
    sys.exit(0 if success else 1)