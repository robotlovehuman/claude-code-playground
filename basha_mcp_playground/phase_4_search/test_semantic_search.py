#!/usr/bin/env python3
"""
Phase 4: First Semantic Search
Goal: Combine pgvector + embeddings to search documents
Test: Store 3 docs, search for "greeting", find "Hello world" doc
"""

import os
import sys
import time
import psycopg2
from pathlib import Path
import openai
from dotenv import load_dotenv
from typing import List, Tuple, Optional
import json

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database configuration
DB_NAME = "toy_vector_test"
DB_USER = "kimomaxmac"
DB_HOST = "localhost"

def get_embedding_with_retry(text: str, model="text-embedding-3-large", max_retries=3) -> Optional[List[float]]:
    """Get embedding with retry logic"""
    for attempt in range(max_retries):
        try:
            response = openai.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
            
        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                wait_time = 2 ** attempt
                print(f"  ⚠️  Server overloaded, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Error: {e}")
                return None
    
    return None

def setup_search_table():
    """Create table for semantic search test"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST
        )
        cur = conn.cursor()
        
        # Create search test table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_docs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding vector(3072),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Clear existing data
        cur.execute("TRUNCATE TABLE search_docs;")
        
        conn.commit()
        print("✅ Search table created/cleared")
        return conn
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return None

def store_test_documents(conn):
    """Store test documents with embeddings"""
    test_docs = [
        {
            "title": "Greeting Document",
            "content": "Hello world! This is a friendly greeting document."
        },
        {
            "title": "Technical Guide", 
            "content": "This document explains how to configure PostgreSQL databases."
        },
        {
            "title": "Food Recipe",
            "content": "To make a delicious pasta, you need tomatoes and garlic."
        }
    ]
    
    stored_ids = []
    cur = conn.cursor()
    
    for doc in test_docs:
        print(f"\n  Storing: {doc['title']}")
        
        # Get embedding
        embedding = get_embedding_with_retry(doc['content'])
        if not embedding:
            print(f"  ❌ Failed to embed {doc['title']}")
            continue
        
        # Store document
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        cur.execute("""
            INSERT INTO search_docs (title, content, embedding)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (doc['title'], doc['content'], embedding_str))
        
        doc_id = cur.fetchone()[0]
        stored_ids.append(doc_id)
        print(f"  ✅ Stored with ID: {doc_id}")
    
    conn.commit()
    return stored_ids

def semantic_search(conn, query: str, limit: int = 3) -> List[Tuple]:
    """Search for documents similar to the query"""
    print(f"\n🔍 Searching for: '{query}'")
    
    # Get embedding for query
    query_embedding = get_embedding_with_retry(query)
    if not query_embedding:
        print("❌ Failed to embed query")
        return []
    
    # Convert to PostgreSQL format
    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
    
    # Search using cosine similarity
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            id,
            title,
            content,
            1 - (embedding <=> %s::vector) AS similarity
        FROM search_docs
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (embedding_str, embedding_str, limit))
    
    results = cur.fetchall()
    return results

def test_semantic_search():
    """Main test function"""
    print("=== Phase 4: Semantic Search Test ===\n")
    
    # Setup database
    print("1. Setting up database...")
    conn = setup_search_table()
    if not conn:
        return False
    
    # Store test documents
    print("\n2. Storing test documents...")
    doc_ids = store_test_documents(conn)
    if len(doc_ids) < 3:
        print("❌ Failed to store all documents")
        return False
    
    # Test searches
    print("\n3. Testing semantic searches...")
    
    test_queries = [
        "greeting",
        "database configuration",
        "cooking instructions"
    ]
    
    all_passed = True
    
    for query in test_queries:
        results = semantic_search(conn, query, limit=1)
        
        if results:
            top_result = results[0]
            print(f"\n  Query: '{query}'")
            print(f"  Top Result: '{top_result[1]}'")
            print(f"  Similarity: {top_result[3]:.4f}")
            print(f"  Content: '{top_result[2][:50]}...'")
            
            # Verify expected results
            if query == "greeting" and "Greeting" not in top_result[1]:
                print("  ❌ Expected to find Greeting Document")
                all_passed = False
            elif query == "database configuration" and "Technical" not in top_result[1]:
                print("  ❌ Expected to find Technical Guide")
                all_passed = False
            elif query == "cooking instructions" and "Recipe" not in top_result[1]:
                print("  ❌ Expected to find Food Recipe")
                all_passed = False
            else:
                print("  ✅ Correct match!")
        else:
            print(f"  ❌ No results for '{query}'")
            all_passed = False
    
    # Cleanup
    conn.close()
    
    return all_passed

if __name__ == "__main__":
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    # Run test
    success = test_semantic_search()
    
    if success:
        print("\n✅ Phase 4 PASSED: Semantic search working perfectly!")
        sys.exit(0)
    else:
        print("\n❌ Phase 4 FAILED: Check errors above")
        sys.exit(1)