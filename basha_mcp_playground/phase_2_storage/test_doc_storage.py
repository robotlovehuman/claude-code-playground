#!/usr/bin/env python3
"""
Phase 2: Test Document Storage with Real Embeddings
Goal: Store a simple document with text-embedding-3-large embeddings in PostgreSQL
Test: Store one "Hello world" doc, verify it's saved with correct embedding
"""

import os
import sys
import time
import psycopg2
from pathlib import Path
import openai
from dotenv import load_dotenv
import json
import numpy as np
from psycopg2.extras import Json
from typing import List, Optional

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
    """Get embedding with retry logic for handling 529 overload errors"""
    for attempt in range(max_retries):
        try:
            print(f"  Attempting to embed (attempt {attempt + 1}/{max_retries})...")
            
            response = openai.embeddings.create(
                input=text,
                model=model
            )
            
            embedding = response.data[0].embedding
            print(f"  ✅ Successfully embedded '{text}' - {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"  ⚠️  Server overloaded, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Error: {e}")
                return None
    
    print(f"  ❌ Failed after {max_retries} attempts")
    return None

def setup_database():
    """Create test table for storing documents with embeddings"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST
        )
        cur = conn.cursor()
        
        # Enable pgvector if not already enabled
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create simple test table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_docs (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(3072),  -- text-embedding-3-large dimensions
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Clear any existing test data
        cur.execute("TRUNCATE TABLE test_docs;")
        
        conn.commit()
        print("✅ Database table created/cleared")
        return conn
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return None

def store_document(conn, content: str, embedding: List[float]):
    """Store a document with its embedding"""
    try:
        cur = conn.cursor()
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        cur.execute("""
            INSERT INTO test_docs (content, embedding)
            VALUES (%s, %s)
            RETURNING id;
        """, (content, embedding_str))
        
        doc_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"✅ Document stored with ID: {doc_id}")
        return doc_id
        
    except Exception as e:
        print(f"❌ Storage error: {e}")
        conn.rollback()
        return None

def verify_storage(conn, doc_id: int):
    """Verify the document was stored correctly"""
    try:
        cur = conn.cursor()
        
        # Retrieve the document
        cur.execute("""
            SELECT id, content, 
                   embedding::text,
                   vector_dims(embedding) as dimensions
            FROM test_docs 
            WHERE id = %s;
        """, (doc_id,))
        
        result = cur.fetchone()
        if result:
            print(f"\n✅ Verification successful:")
            print(f"   ID: {result[0]}")
            print(f"   Content: '{result[1]}'")
            print(f"   Embedding dimensions: {result[3]}")
            print(f"   First 5 values: {result[2][:50]}...")
            return True
        else:
            print(f"❌ Document not found")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def test_document_storage():
    """Main test function"""
    print("=== Phase 2: Document Storage Test ===\n")
    
    # Test document
    test_content = "Hello world - this is a test document for vector storage"
    
    # Setup database
    print("1. Setting up database...")
    conn = setup_database()
    if not conn:
        return False
    
    # Get embedding
    print(f"\n2. Getting embedding for: '{test_content}'")
    embedding = get_embedding_with_retry(test_content)
    if not embedding:
        return False
    
    # Store document
    print(f"\n3. Storing document in PostgreSQL...")
    doc_id = store_document(conn, test_content, embedding)
    if not doc_id:
        return False
    
    # Verify storage
    print(f"\n4. Verifying storage...")
    success = verify_storage(conn, doc_id)
    
    # Cleanup
    conn.close()
    
    return success

if __name__ == "__main__":
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    # Run test
    success = test_document_storage()
    
    if success:
        print("\n✅ Phase 2 PASSED: Document storage with embeddings working!")
        sys.exit(0)
    else:
        print("\n❌ Phase 2 FAILED: Check errors above")
        sys.exit(1)