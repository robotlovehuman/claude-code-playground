#!/usr/bin/env python3
"""
Basha Knowledge MCP Server
A real MCP server that provides semantic search over documents using OpenAI embeddings and PostgreSQL+pgvector
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union

# MCP Server imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    Prompt,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Database and AI imports
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'basha_knowledge',
    'user': 'kimomaxmac',
    'password': ''  # No password for local development
}

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize MCP server
server = Server("basha-knowledge")

class BashaMCPServer:
    def __init__(self):
        self.db_config = DB_CONFIG
        self.openai_client = openai_client
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
    
    def setup_database(self):
        """Set up database tables if they don't exist"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                # Create table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding VECTOR(3072),
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Note: Skipping vector index due to dimension limit in pgvector
                # The search will still work, just slower on large datasets
                conn.commit()
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """Search documents using semantic similarity"""
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, content, metadata, created_at,
                               1 - (embedding <=> %s::vector) as similarity
                        FROM documents
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, query_embedding, limit))
                    
                    results = []
                    for row in cur.fetchall():
                        results.append({
                            'id': row['id'],
                            'content': row['content'],
                            'metadata': dict(row['metadata']) if row['metadata'] else {},
                            'similarity': float(row['similarity']),
                            'created_at': row['created_at'].isoformat()
                        })
                    
                    return results
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    async def add_document(self, content: str, metadata: Dict = None) -> int:
        """Add a document to the knowledge base"""
        try:
            # Get embedding
            embedding = self.get_embedding(content)
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO documents (content, embedding, metadata)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (content, embedding, json.dumps(metadata or {})))
                    
                    doc_id = cur.fetchone()[0]
                    conn.commit()
                    return doc_id
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM documents")
                    total_docs = cur.fetchone()[0]
                    
                    cur.execute("SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL")
                    docs_with_embeddings = cur.fetchone()[0]
                    
                    return {
                        'total_documents': total_docs,
                        'documents_with_embeddings': docs_with_embeddings,
                        'database_status': 'connected'
                    }
        except Exception as e:
            return {
                'error': str(e),
                'database_status': 'error'
            }

# Initialize server instance
basha_server = BashaMCPServer()

# Set up database on startup
try:
    basha_server.setup_database()
except Exception as e:
    print(f"Database setup failed: {e}", file=sys.stderr)

# Define MCP Tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_docs",
            description="Search documents using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Number of results (default: 5)", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_document",
            description="Add a new document to the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Document content"},
                    "metadata": {"type": "object", "description": "Optional metadata"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="get_stats",
            description="Get database statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    if name == "search_docs":
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        
        if not query:
            return [TextContent(type="text", text="Error: query is required")]
        
        try:
            results = await basha_server.search_documents(query, limit)
            
            if not results:
                return [TextContent(type="text", text=f"No documents found for query: '{query}'")]
            
            response = f"🔍 Found {len(results)} documents for '{query}':\n\n"
            for i, doc in enumerate(results, 1):
                response += f"{i}. **Similarity: {doc['similarity']:.3f}**\n"
                response += f"   Content: {doc['content'][:200]}{'...' if len(doc['content']) > 200 else ''}\n"
                response += f"   ID: {doc['id']}, Created: {doc['created_at']}\n\n"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Search error: {str(e)}")]
    
    elif name == "add_document":
        content = arguments.get("content")
        metadata = arguments.get("metadata", {})
        
        if not content:
            return [TextContent(type="text", text="Error: content is required")]
        
        try:
            doc_id = await basha_server.add_document(content, metadata)
            return [TextContent(type="text", text=f"✅ Document added successfully! ID: {doc_id}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding document: {str(e)}")]
    
    elif name == "get_stats":
        try:
            stats = await basha_server.get_stats()
            
            if 'error' in stats:
                return [TextContent(type="text", text=f"Database error: {stats['error']}")]
            
            response = f"""📊 **Basha Knowledge Base Stats**
            
Total Documents: {stats['total_documents']}
Documents with Embeddings: {stats['documents_with_embeddings']}
Database Status: {stats['database_status']}
"""
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Stats error: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# Define MCP Prompts (Smart Prompts)
@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts"""
    return [
        Prompt(
            name="basha-assets",
            description="List all Basha Knowledge server capabilities",
            arguments=[]
        ),
        Prompt(
            name="basha-test",
            description="Test the knowledge base functionality",
            arguments=[]
        ),
        Prompt(
            name="basha-learn",
            description="Guide for adding documents to knowledge base",
            arguments=[]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> str:
    """Handle prompt requests"""
    if name == "basha-assets":
        return """🧠 **Basha Knowledge MCP Server**

**Available Tools:**
• `search_docs` - Search documents using semantic similarity
• `add_document` - Add new documents to knowledge base  
• `get_stats` - Get database statistics

**Available Prompts:**
• `/basha-assets` - Show this capability list
• `/basha-test` - Test search functionality
• `/basha-learn` - Guide for adding documents

**Quick Start:**
1. Use `/basha-test` to verify everything works
2. Use `search_docs` to find documents by meaning
3. Use `add_document` to grow your knowledge base
4. Use `/basha-learn` for guided document workflows

**Tech Stack:**
• PostgreSQL + pgvector for semantic search
• OpenAI text-embedding-3-large (3072 dimensions)
• Real-time similarity search with cosine distance

Ready to be your intelligent knowledge assistant! 🚀"""

    elif name == "basha-test":
        # Run a test search
        try:
            results = await basha_server.search_documents("test", 3)
            stats = await basha_server.get_stats()
            
            response = f"""🔍 **Basha Knowledge Test Results**

**Database Status:** {stats.get('database_status', 'unknown')}
**Total Documents:** {stats.get('total_documents', 0)}
**Documents with Embeddings:** {stats.get('documents_with_embeddings', 0)}

**Test Search Results:**
"""
            if results:
                for i, doc in enumerate(results, 1):
                    response += f"{i}. {doc['content'][:100]}... (similarity: {doc['similarity']:.3f})\n"
                response += "\n✅ Semantic search is working!"
            else:
                response += "No documents found. Try adding some with `add_document`."
            
            response += "\n\n💡 **Next Steps:**\n"
            response += "• Use `search_docs` to find documents by meaning\n"
            response += "• Use `add_document` to add new knowledge\n"
            response += "• Use `/basha-learn` for guided workflows"
            
            return response
            
        except Exception as e:
            return f"❌ Test failed: {str(e)}\n\nTry checking your database connection and OpenAI API key."
    
    elif name == "basha-learn":
        return """📚 **Basha Knowledge Learning Guide**

**Adding Documents:**
Use the `add_document` tool to add knowledge:

```
add_document({
    "content": "Your document content here",
    "metadata": {"source": "manual", "category": "notes"}
})
```

**Best Practices:**
• Add clear, descriptive content
• Include relevant metadata for organization
• Use meaningful document titles/summaries
• Break large documents into focused chunks

**Workflow:**
1. **Prepare** - Organize your documents
2. **Add** - Use `add_document` for each piece
3. **Test** - Use `search_docs` to verify
4. **Refine** - Add more context if needed

**Pro Tips:**
• Search works by meaning, not just keywords
• Similar concepts will cluster together
• Higher similarity scores = better matches
• Use `/basha-test` to verify functionality

Ready to build your intelligent knowledge base! 🎯"""
    
    else:
        return f"Unknown prompt: {name}"

async def main():
    """Main server function"""
    try:
        # Test database connection
        await basha_server.get_stats()
        
        # Run the MCP server
        await stdio_server(server)
        
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())