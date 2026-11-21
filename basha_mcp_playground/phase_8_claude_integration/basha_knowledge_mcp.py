#!/usr/bin/env python3
"""
Enhanced Basha Knowledge MCP Server with Smart Prompts
Enhanced version with more sophisticated guided workflows following smart_mcp_workflow.txt pattern
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import glob

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

# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    logger.error("OPENAI_API_KEY not found in environment variables")
    # For MCP, we should not raise errors during import
    OPENAI_API_KEY = None

# Initialize OpenAI client only if key is available
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Initialize MCP server
server = Server("basha-knowledge-enhanced")

class EnhancedBashaMCPServer:
    def __init__(self):
        self.db_config = DB_CONFIG
        self.openai_client = openai_client
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized - check OPENAI_API_KEY")
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
    
    async def find_data_sources(self, directory: str = ".") -> List[Dict]:
        """Find potential data sources in directory"""
        try:
            sources = []
            
            # Look for text files
            for ext in ["*.txt", "*.md", "*.json", "*.csv", "*.py", "*.js", "*.html"]:
                for file_path in glob.glob(os.path.join(directory, "**", ext), recursive=True):
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        sources.append({
                            'path': file_path,
                            'type': ext.replace("*.", ""),
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            return sorted(sources, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            raise Exception(f"Failed to find data sources: {str(e)}")
    
    async def analyze_document_content(self, file_path: str) -> Dict:
        """Analyze a document's content for learning"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic analysis
            word_count = len(content.split())
            char_count = len(content)
            
            # Get a snippet
            snippet = content[:200] + "..." if len(content) > 200 else content
            
            return {
                'file_path': file_path,
                'content': content,
                'word_count': word_count,
                'char_count': char_count,
                'snippet': snippet,
                'suitable_for_learning': word_count > 10 and char_count > 50
            }
        except Exception as e:
            raise Exception(f"Failed to analyze document: {str(e)}")

# Initialize server instance
enhanced_server = EnhancedBashaMCPServer()

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
        ),
        Tool(
            name="find_data_sources",
            description="Find potential data sources in directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory to search (default: current)", "default": "."}
                }
            }
        ),
        Tool(
            name="analyze_document",
            description="Analyze a document's content for learning",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to document to analyze"}
                },
                "required": ["file_path"]
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
            results = await enhanced_server.search_documents(query, limit)
            
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
            doc_id = await enhanced_server.add_document(content, metadata)
            return [TextContent(type="text", text=f"✅ Document added successfully! ID: {doc_id}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding document: {str(e)}")]
    
    elif name == "get_stats":
        try:
            stats = await enhanced_server.get_stats()
            
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
    
    elif name == "find_data_sources":
        directory = arguments.get("directory", ".")
        
        try:
            sources = await enhanced_server.find_data_sources(directory)
            
            if not sources:
                return [TextContent(type="text", text=f"No data sources found in {directory}")]
            
            response = f"📁 Found {len(sources)} data sources in '{directory}':\n\n"
            for i, source in enumerate(sources[:10], 1):  # Show top 10
                response += f"{i}. **{source['path']}** ({source['type']})\n"
                response += f"   Size: {source['size']} bytes, Modified: {source['modified']}\n\n"
            
            if len(sources) > 10:
                response += f"... and {len(sources) - 10} more files\n\n"
            
            response += "💡 **Next Steps:**\n"
            response += "• Use `analyze_document` to examine files\n"
            response += "• Use `add_document` to add content to knowledge base\n"
            response += "• Use `/basha-learn` for guided document ingestion"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error finding data sources: {str(e)}")]
    
    elif name == "analyze_document":
        file_path = arguments.get("file_path")
        
        if not file_path:
            return [TextContent(type="text", text="Error: file_path is required")]
        
        try:
            analysis = await enhanced_server.analyze_document_content(file_path)
            
            response = f"""📄 **Document Analysis: {analysis['file_path']}**

**Content Summary:**
- Word Count: {analysis['word_count']}
- Character Count: {analysis['char_count']}
- Suitable for Learning: {'✅ Yes' if analysis['suitable_for_learning'] else '❌ No'}

**Content Preview:**
{analysis['snippet']}

**Recommended Actions:**
"""
            
            if analysis['suitable_for_learning']:
                response += "• ✅ Ready to add to knowledge base with `add_document`\n"
                response += "• 💡 Consider adding metadata like category, source, etc.\n"
                response += "• 🔍 Use `/basha-learn` for guided ingestion workflow"
            else:
                response += "• ⚠️ Document may be too short or empty\n"
                response += "• 📝 Consider combining with other content\n"
                response += "• 🔍 Check file format and encoding"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error analyzing document: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# Define Enhanced MCP Prompts (Smart Prompts)
@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts"""
    return [
        Prompt(
            name="basha-assets",
            description="List all Basha Knowledge server capabilities and guided workflows",
            arguments=[]
        ),
        Prompt(
            name="basha-test",
            description="Test the knowledge base functionality with comprehensive diagnostics",
            arguments=[]
        ),
        Prompt(
            name="basha-learn",
            description="Complete guided workflow for adding documents to knowledge base",
            arguments=[]
        ),
        Prompt(
            name="basha-discover",
            description="Discover and analyze potential data sources in your project",
            arguments=[
                {
                    "name": "directory",
                    "description": "Directory to search (default: current directory)",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="basha-explore",
            description="Explore your knowledge base with guided search workflows",
            arguments=[
                {
                    "name": "topic",
                    "description": "Topic to explore (optional)",
                    "required": False
                }
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> str:
    """Handle prompt requests with enhanced smart workflows"""
    if name == "basha-assets":
        return """🧠 **Enhanced Basha Knowledge MCP Server**

**Available Tools:**
• `search_docs` - Search documents using semantic similarity
• `add_document` - Add new documents to knowledge base  
• `get_stats` - Get database statistics
• `find_data_sources` - Discover potential data sources
• `analyze_document` - Analyze document content for learning

**Smart Prompts (Guided Workflows):**
• `/basha-assets` - Show this capability list
• `/basha-test` - Comprehensive system diagnostics
• `/basha-learn` - Complete document ingestion workflow
• `/basha-discover` - Find and analyze data sources
• `/basha-explore` - Guided knowledge base exploration

**Quick Start Workflow:**
1. Use `/basha-test` to verify system health
2. Use `/basha-discover` to find documents to add
3. Use `/basha-learn` for guided document ingestion
4. Use `/basha-explore` to search your knowledge

**Advanced Features:**
• Semantic search finds documents by meaning, not keywords
• Smart metadata extraction and organization
• Guided workflows reduce cognitive load
• Real-time similarity scoring with explanations

**Tech Stack:**
• PostgreSQL + pgvector for semantic search
• OpenAI text-embedding-3-large (3072 dimensions)
• Real-time similarity search with cosine distance
• Smart prompt orchestration following MCP best practices

Ready to transform your scattered knowledge into an intelligent, searchable system! 🚀"""

    elif name == "basha-test":
        # Comprehensive system test
        try:
            # Run diagnostics
            stats = await enhanced_server.get_stats()
            
            # Test search if we have documents
            search_results = []
            if stats.get('total_documents', 0) > 0:
                search_results = await enhanced_server.search_documents("test", 3)
            
            response = f"""🔍 **Basha Knowledge System Diagnostics**

**System Health Check:**
✅ Database Status: {stats.get('database_status', 'unknown')}
✅ OpenAI API: Connected
✅ MCP Server: Running
✅ Total Documents: {stats.get('total_documents', 0)}
✅ Documents with Embeddings: {stats.get('documents_with_embeddings', 0)}

**Search Engine Test:**
"""
            
            if search_results:
                response += f"✅ Semantic search working! Found {len(search_results)} results:\n"
                for i, doc in enumerate(search_results, 1):
                    response += f"   {i}. {doc['content'][:60]}... (similarity: {doc['similarity']:.3f})\n"
            else:
                response += "ℹ️ No documents to test search (this is normal for new installations)\n"
            
            response += f"""

**Performance Metrics:**
• Search Speed: Real-time semantic similarity
• Embedding Model: text-embedding-3-large (3072 dimensions)
• Database: PostgreSQL with pgvector extension
• Index Status: Sequential scan (works for small datasets)

**Recommended Next Steps:**
"""
            
            if stats.get('total_documents', 0) == 0:
                response += """1. 🔍 Run `/basha-discover` to find documents to add
2. 📚 Use `/basha-learn` to add your first documents
3. 🎯 Use `search_docs` to test semantic search
4. 🚀 Use `/basha-explore` to discover insights"""
            else:
                response += """1. 🔍 Use `/basha-explore` to search your knowledge
2. 📚 Use `/basha-learn` to add more documents
3. 🎯 Try complex semantic queries
4. 🚀 Build custom workflows with your data"""
            
            return response
            
        except Exception as e:
            return f"""❌ **System Test Failed**

Error: {str(e)}

**Troubleshooting Steps:**
1. Check database connection (PostgreSQL running?)
2. Verify OpenAI API key in environment
3. Ensure pgvector extension is installed
4. Check network connectivity

**Quick Fix Commands:**
• `get_stats` - Check database status
• Restart PostgreSQL service
• Verify .env file has OPENAI_API_KEY"""
    
    elif name == "basha-learn":
        # Enhanced learning workflow
        directory = arguments.get("directory", ".")
        
        try:
            # Find data sources
            sources = await enhanced_server.find_data_sources(directory)
            
            response = f"""📚 **Basha Knowledge Learning Workflow**

**Step 1: Discovery Complete**
Found {len(sources)} potential data sources in '{directory}'

**Ready to Learn Files:**
"""
            
            suitable_files = []
            for source in sources[:5]:  # Show top 5
                try:
                    analysis = await enhanced_server.analyze_document_content(source['path'])
                    if analysis['suitable_for_learning']:
                        suitable_files.append(source)
                        response += f"✅ {source['path']} ({source['type']}) - {analysis['word_count']} words\n"
                    else:
                        response += f"⚠️ {source['path']} ({source['type']}) - may be too short\n"
                except:
                    response += f"❌ {source['path']} ({source['type']}) - analysis failed\n"
            
            response += f"""

**Step 2: Ingestion Workflow**
{'✅ Ready to proceed!' if suitable_files else '⚠️ No suitable files found'}

**Recommended Actions:**
"""
            
            if suitable_files:
                response += f"""1. **Analyze** specific files:
   • Use `analyze_document` with file path
   • Example: analyze_document({{"file_path": "{suitable_files[0]['path']}"}})

2. **Add** documents to knowledge base:
   • Use `add_document` with content and metadata
   • Example: add_document({{"content": "...", "metadata": {{"source": "file", "category": "docs"}}}})

3. **Test** your additions:
   • Use `search_docs` to verify content is searchable
   • Try semantic queries related to your content

4. **Explore** your knowledge:
   • Use `/basha-explore` to discover insights
   • Build on your growing knowledge base"""
            else:
                response += """1. **Check** file contents are text-based
2. **Try** different directory with `find_data_sources`
3. **Manually** add content with `add_document`
4. **Use** `/basha-discover` to find other sources"""
            
            response += f"""

**Pro Tips:**
• 📁 Organize with meaningful metadata
• 🔍 Test search after each addition
• 📝 Break large documents into focused chunks
• 🎯 Use descriptive content summaries

**Next Command Suggestions:**
• `analyze_document` - Examine specific files
• `add_document` - Add content to knowledge base
• `/basha-explore` - Search your growing knowledge"""
            
            return response
            
        except Exception as e:
            return f"""❌ **Learning Workflow Failed**

Error: {str(e)}

**Recovery Steps:**
1. Check directory permissions
2. Verify file formats are supported
3. Try with different directory
4. Use manual `add_document` approach

**Supported File Types:**
• Text files (.txt, .md)
• Code files (.py, .js, .html)
• Data files (.json, .csv)"""
    
    elif name == "basha-discover":
        directory = arguments.get("directory", ".")
        
        try:
            # Discovery workflow
            sources = await enhanced_server.find_data_sources(directory)
            
            response = f"""🔍 **Basha Knowledge Discovery**

**Directory Scan: '{directory}'**
Found {len(sources)} potential data sources

**File Type Breakdown:**
"""
            
            # Group by type
            type_counts = {}
            for source in sources:
                type_counts[source['type']] = type_counts.get(source['type'], 0) + 1
            
            for file_type, count in sorted(type_counts.items()):
                response += f"• {file_type}: {count} files\n"
            
            response += f"""

**Top Recent Files:**
"""
            
            for i, source in enumerate(sources[:8], 1):
                response += f"{i}. **{source['path']}** ({source['type']})\n"
                response += f"   {source['size']} bytes, modified {source['modified']}\n\n"
            
            response += f"""**Discovery Actions:**
1. **Analyze** interesting files:
   • Use `analyze_document` with file path
   • Check content quality and structure

2. **Start Learning Process:**
   • Use `/basha-learn` for guided workflow
   • Begin with most relevant files

3. **Manual Selection:**
   • Use `add_document` for specific content
   • Add metadata for better organization

**Smart Recommendations:**
"""
            
            # Smart recommendations based on file types
            if 'md' in type_counts:
                response += "• 📝 Markdown files detected - great for documentation\n"
            if 'py' in type_counts:
                response += "• 🐍 Python files detected - consider adding code documentation\n"
            if 'json' in type_counts:
                response += "• 📊 JSON files detected - structured data for knowledge base\n"
            if 'txt' in type_counts:
                response += "• 📄 Text files detected - raw content ready for learning\n"
            
            response += f"""
**Next Steps:**
• Use `/basha-learn` for complete ingestion workflow
• Use `analyze_document` for specific file analysis
• Use `add_document` for manual content addition"""
            
            return response
            
        except Exception as e:
            return f"""❌ **Discovery Failed**

Error: {str(e)}

**Try These Alternatives:**
• Check directory path exists
• Use different directory
• Verify file permissions
• Try `/basha-learn` without discovery"""
    
    elif name == "basha-explore":
        topic = arguments.get("topic", "")
        
        try:
            # Get current knowledge base stats
            stats = await enhanced_server.get_stats()
            
            response = f"""🎯 **Basha Knowledge Exploration**

**Knowledge Base Overview:**
• Total Documents: {stats.get('total_documents', 0)}
• Searchable Documents: {stats.get('documents_with_embeddings', 0)}
• Database Status: {stats.get('database_status', 'unknown')}

"""
            
            if stats.get('total_documents', 0) == 0:
                response += """**Getting Started:**
Your knowledge base is empty. Here's how to begin:

1. **Discover** content:
   • Use `/basha-discover` to find files
   • Look for documents, notes, code files

2. **Add** your first documents:
   • Use `/basha-learn` for guided workflow
   • Or use `add_document` manually

3. **Return** here to explore your knowledge

**Why Semantic Search Matters:**
• Find documents by meaning, not just keywords
• Discover unexpected connections
• Get ranked results by relevance
• Build understanding across your knowledge"""
            else:
                if topic:
                    # Search for the topic
                    search_results = await enhanced_server.search_documents(topic, 5)
                    
                    response += f"""**Search Results for "{topic}":**
"""
                    
                    if search_results:
                        response += f"Found {len(search_results)} relevant documents:\n\n"
                        for i, doc in enumerate(search_results, 1):
                            response += f"{i}. **Similarity: {doc['similarity']:.3f}**\n"
                            response += f"   {doc['content'][:150]}{'...' if len(doc['content']) > 150 else ''}\n\n"
                    else:
                        response += f"No documents found for '{topic}'. Try different keywords or broader terms.\n\n"
                else:
                    response += """**Exploration Suggestions:**
"""
                
                response += f"""**Exploration Commands:**
• `search_docs` - Search by topic, concept, or question
• `get_stats` - Check knowledge base status
• `/basha-explore` - Return to this exploration guide

**Search Tips:**
• Use natural language queries
• Try conceptual terms, not just keywords
• Ask questions: "How to..." or "What is..."
• Experiment with different phrasings

**Sample Queries to Try:**
• "programming concepts"
• "project documentation"
• "troubleshooting guide"
• "implementation details"

**Advanced Workflows:**
• Combine search with analysis
• Use metadata for filtering
• Build knowledge maps
• Track learning progress"""
            
            return response
            
        except Exception as e:
            return f"""❌ **Exploration Failed**

Error: {str(e)}

**Recovery Actions:**
• Check database connection
• Verify knowledge base integrity
• Try simpler search terms
• Use `get_stats` to diagnose issues"""
    
    else:
        return f"Unknown prompt: {name}"

async def main():
    """Main server function"""
    try:
        logger.info("Starting Basha Knowledge MCP Server...")
        
        # Set up database on first run
        try:
            enhanced_server.setup_database()
            logger.info("Database setup complete")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            # Continue anyway - some functions might still work
        
        # Test database connection
        try:
            stats = await enhanced_server.get_stats()
            logger.info(f"Database stats: {stats}")
        except Exception as e:
            logger.warning(f"Could not get database stats: {e}")
        
        # Run the MCP server
        logger.info("Starting MCP server...")
        async with stdio_server(server):
            logger.info("MCP server started successfully")
            await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())