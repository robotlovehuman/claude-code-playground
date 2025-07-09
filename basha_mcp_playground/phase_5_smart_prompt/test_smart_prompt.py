#!/usr/bin/env python3
"""
Phase 5: First Smart Prompt
Goal: Create a prompt that orchestrates multiple tools
Test: /basha-test returns search result + guidance
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from dotenv import load_dotenv
import json

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class SmartMCPServer:
    """MCP server with smart prompts that orchestrate tools"""
    
    def __init__(self):
        self.db_config = {
            "dbname": "toy_vector_test",
            "user": "kimomaxmac",
            "host": "localhost"
        }
        
        # Define tools
        self.tools = {
            "search_docs": {
                "description": "Search documents by semantic similarity",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            "add_doc": {
                "description": "Add a new document to the knowledge base",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Document content"}
                    },
                    "required": ["content"]
                }
            }
        }
        
        # Define prompts (smart workflows)
        self.prompts = {
            "basha-test": {
                "description": "Test semantic search and provide guidance",
                "handler": self.prompt_test
            },
            "basha-learn": {
                "description": "Learn from new documents",
                "handler": self.prompt_learn
            }
        }
    
    def get_embedding(self, text: str) -> list[float]:
        """Get embedding using OpenAI"""
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-3-large"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}", file=sys.stderr)
            return None
    
    def tool_search_docs(self, query: str):
        """Tool: Search for similar documents"""
        embedding = self.get_embedding(query)
        if not embedding:
            return {"error": "Failed to get embedding"}
        
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            embedding_str = f"[{','.join(map(str, embedding))}]"
            
            cur.execute("""
                SELECT content, embedding <=> %s::vector AS distance
                FROM semantic_docs
                ORDER BY distance
                LIMIT 3;
            """, (embedding_str,))
            
            results = cur.fetchall()
            return {"results": results}
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()
    
    def prompt_test(self, args=None):
        """Smart prompt: Test search and provide guidance"""
        # Step 1: Run a test search
        search_result = self.tool_search_docs("greeting")
        
        # Step 2: Analyze results
        if "results" in search_result and len(search_result["results"]) > 0:
            top_result = search_result["results"][0]
            response = f"🔍 Search Test Results:\n\n"
            response += f"Query: 'greeting'\n"
            response += f"Found: '{top_result['content']}'\n"
            response += f"Distance: {top_result['distance']:.4f}\n\n"
            response += "✅ Semantic search is working!\n\n"
            response += "💡 Next steps:\n"
            response += "- Try: /basha-learn to add new documents\n"
            response += "- Search for any topic with search_docs tool\n"
            response += "- Lower distance = more similar (0 = exact match)"
        else:
            response = "❌ Search test failed. Check database connection."
        
        return response
    
    def prompt_learn(self, args=None):
        """Smart prompt: Guide through adding documents"""
        response = "📚 Document Learning Workflow:\n\n"
        response += "1. I'll help you add documents to the knowledge base\n"
        response += "2. Each document gets vectorized for semantic search\n"
        response += "3. Use the 'add_doc' tool with your content\n\n"
        response += "Example:\n"
        response += "add_doc({\"content\": \"Your document text here\"})\n\n"
        response += "💡 Tips:\n"
        response += "- Add diverse documents for better search\n"
        response += "- Longer documents provide more context\n"
        response += "- Documents are instantly searchable after adding"
        
        return response
    
    def handle_prompt_call(self, prompt_name: str, args=None):
        """Execute a smart prompt"""
        if prompt_name in self.prompts:
            handler = self.prompts[prompt_name]["handler"]
            return handler(args)
        return f"Unknown prompt: {prompt_name}"
    
    def test_smart_prompt(self):
        """Test the smart prompt functionality"""
        print("=== Phase 5: Smart Prompt Test ===\n")
        
        # Test the basha-test prompt
        print("Testing /basha-test prompt...")
        result = self.handle_prompt_call("basha-test")
        print(result)
        
        # Check if it contains expected elements
        expected = ["Search Test Results", "Semantic search is working", "Next steps"]
        success = all(exp in result for exp in expected)
        
        if success:
            print("\n✅ Phase 5 PASSED: Smart prompt orchestrates tools and provides guidance!")
            return True
        else:
            print("\n❌ Phase 5 FAILED: Smart prompt missing expected elements")
            return False

def main():
    """Run Phase 5 test"""
    server = SmartMCPServer()
    
    # Ensure test data exists
    conn = psycopg2.connect(
        dbname="toy_vector_test",
        user="kimomaxmac",
        host="localhost"
    )
    cur = conn.cursor()
    
    try:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'semantic_docs'
            );
        """)
        
        if not cur.fetchone()[0]:
            print("Creating test data...")
            # Create minimal test data
            cur.execute("""
                CREATE TABLE semantic_docs (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector(3072)
                );
            """)
            
            # Add one test document
            embedding = server.get_embedding("Hello world, this is a greeting")
            if embedding:
                embedding_str = f"[{','.join(map(str, embedding))}]"
                cur.execute(
                    "INSERT INTO semantic_docs (content, embedding) VALUES (%s, %s);",
                    ("Hello world, this is a greeting", embedding_str)
                )
            
            conn.commit()
    finally:
        cur.close()
        conn.close()
    
    # Run the test
    return server.test_smart_prompt()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)