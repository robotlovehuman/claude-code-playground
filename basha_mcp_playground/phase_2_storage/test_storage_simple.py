#!/usr/bin/env python3
"""
Phase 2: Test Document Storage with Real Embeddings
Goal: Store one document with real embedding in PostgreSQL
"""

import os
import sys
from pathlib import Path
import psycopg2
import openai
from dotenv import load_dotenv
import time

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

def main():
    print("=== Phase 2: Document Storage Test ===\n")
    
    # Connect to database
    conn = psycopg2.connect(dbname="toy_vector_test", user="kimomaxmac", host="localhost")
    cur = conn.cursor()
    
    try:
        # 1. Setup table
        print("1. Creating table...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("DROP TABLE IF EXISTS test_docs;")
        cur.execute("""
            CREATE TABLE test_docs (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(3072)  -- text-embedding-3-large
            );
        """)
        conn.commit()
        print("✅ Table created\n")
        
        # 2. Get embedding
        test_text = "Hello world - this is a test document"
        print(f"2. Getting embedding for: '{test_text}'")
        embedding = get_embedding(test_text)
        
        if not embedding:
            return False
            
        print(f"✅ Got embedding with {len(embedding)} dimensions\n")
        
        # 3. Store document
        print("3. Storing in PostgreSQL...")
        embedding_str = f"[{','.join(map(str, embedding))}]"
        cur.execute(
            "INSERT INTO test_docs (content, embedding) VALUES (%s, %s) RETURNING id;",
            (test_text, embedding_str)
        )
        doc_id = cur.fetchone()[0]
        conn.commit()
        print(f"✅ Stored with ID: {doc_id}\n")
        
        # 4. Verify
        print("4. Verifying...")
        cur.execute("""
            SELECT id, content, 
                   vector_dims(embedding) as dimensions
            FROM test_docs WHERE id = %s;
        """, (doc_id,))
        
        result = cur.fetchone()
        print(f"✅ Verified - ID: {result[0]}, Content: '{result[1]}'")
        print(f"   Embedding dimensions stored: {result[2]}")
        
        print("\n✅ Phase 2 PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)