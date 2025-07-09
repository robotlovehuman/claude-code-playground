# The Basha Knowledge MCP Server: Complete In-Depth Guide

## Table of Contents
1. [Introduction: Understanding MCP and Claude Code](#introduction)
2. [The Architecture: How Claude Code Uses MCP](#architecture)
3. [The Basha Knowledge System: What We Built](#basha-system)
4. [Motivation: Why This Matters](#motivation)
5. [Installation and Setup](#installation)
6. [Using Basha with Claude Code](#usage)
7. [Maintenance Guide](#maintenance)
8. [Expanding and Improving](#expansion)
9. [Advanced Testing and Development](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Technical Deep Dive](#technical)
12. [Future Roadmap](#roadmap)

---

## 1. Introduction: Understanding MCP and Claude Code {#introduction}

### What is MCP (Model Context Protocol)?

The Model Context Protocol (MCP) is a revolutionary open standard that enables secure, controlled interactions between AI assistants and external tools, data sources, and services. Think of it as a universal language that allows AI systems to safely communicate with the outside world.

**Key MCP Concepts:**
- **Protocol**: Standardized JSON-RPC communication over stdin/stdout
- **Tools**: Functions that AI can call to perform actions
- **Resources**: Data sources the AI can read from
- **Prompts**: Pre-configured workflows that orchestrate tools and provide guidance
- **Security**: Sandboxed execution with explicit permission controls

### What is Claude Code?

Claude Code is Anthropic's AI-powered coding assistant that combines the intelligence of Claude with practical development capabilities. It can:
- Write, edit, and understand code
- Execute commands and scripts
- Manage files and projects
- Integrate with external tools through MCP

### The Connection: How They Work Together

```
┌─────────────────┐     MCP Protocol      ┌──────────────────┐
│  Claude Code    │ ◄──────────────────► │   MCP Server     │
│  (AI Assistant) │   JSON-RPC/stdio      │  (Your Tools)    │
└─────────────────┘                       └──────────────────┘
         │                                          │
         ▼                                          ▼
    User Requests                            External Systems
   "Search my docs"                         (Database, APIs, 
                                             File System)
```

**The Flow:**
1. User asks Claude Code to perform a task
2. Claude Code identifies which MCP tools/prompts to use
3. Sends JSON-RPC request to MCP server
4. MCP server executes the function with local permissions
5. Returns results to Claude Code
6. Claude Code presents results to user

---

## 2. The Architecture: How Claude Code Uses MCP {#architecture}

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude Code                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MCP Client Integration                  │   │
│  │  • Tool Discovery    • Prompt Management           │   │
│  │  • Request Routing   • Response Handling           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                          JSON-RPC Protocol
                          (stdin/stdout)
                                  │
┌─────────────────────────────────┼───────────────────────────┐
│                     Basha Knowledge MCP Server              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │   Smart Prompts  │  │      Tools      │  │  Database  │  │
│  │  • /basha-assets │  │  • search_docs  │  │            │  │
│  │  • /basha-test   │  │  • add_document │  │ PostgreSQL │  │
│  │  • /basha-learn  │  │  • get_stats    │  │     +      │  │
│  │  • /basha-discover│  │  • find_sources │  │  pgvector  │  │
│  │  • /basha-explore │  │  • analyze_doc  │  │            │  │
│  └─────────────────┘  └─────────────────┘  └────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI Integration Layer                    │   │
│  │     OpenAI API (text-embedding-3-large)             │   │
│  │         3072-dimensional embeddings                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Communication Protocol

**1. Initialization**
```json
// Claude Code → MCP Server
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "0.1.0",
    "capabilities": {}
  }
}

// MCP Server → Claude Code
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "0.1.0",
    "capabilities": {
      "tools": {},
      "prompts": {}
    }
  }
}
```

**2. Tool Discovery**
```json
// Claude Code requests available tools
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}

// Server responds with tool definitions
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "search_docs",
        "description": "Search documents using semantic similarity",
        "inputSchema": {...}
      }
    ]
  }
}
```

**3. Tool Execution**
```json
// Claude Code calls a tool
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_docs",
    "arguments": {
      "query": "machine learning",
      "limit": 5
    }
  }
}
```

---

## 3. The Basha Knowledge System: What We Built {#basha-system}

### Overview

The Basha Knowledge MCP Server is an intelligent document management system that transforms how you interact with your information. Instead of keyword-based search, it understands the meaning and context of your queries.

### Core Features

**1. Semantic Search**
- Uses OpenAI's text-embedding-3-large model
- 3072-dimensional vector representations
- Cosine similarity for meaning-based matching
- Sub-second search performance

**2. Document Management**
- Add documents with rich metadata
- Automatic embedding generation
- Persistent storage in PostgreSQL
- Support for various content types

**3. Smart Discovery**
- Scan directories for potential knowledge sources
- Analyze document suitability
- Batch ingestion workflows
- File type recognition

**4. Guided Workflows**
- Interactive prompts that guide users
- Context-aware recommendations
- Multi-step orchestration
- Next-action suggestions

### Technical Stack

```
┌─────────────────────────────────────────┐
│           User Interface Layer          │
│         Claude Code Integration         │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│          MCP Protocol Layer             │
│      JSON-RPC over stdin/stdout         │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│        Application Logic Layer          │
│  • Tool Implementations                 │
│  • Prompt Orchestration                 │
│  • Error Handling                       │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│           AI Service Layer              │
│    OpenAI Embeddings API                │
│    (text-embedding-3-large)             │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│          Data Storage Layer             │
│      PostgreSQL + pgvector              │
│    Vector Similarity Search             │
└─────────────────────────────────────────┘
```

---

## 4. Motivation: Why This Matters {#motivation}

### The Problem

As developers and knowledge workers, we face a critical challenge:
- **Information Overload**: Documentation scattered across countless files
- **Search Limitations**: Traditional keyword search misses context
- **Knowledge Silos**: Information exists but isn't discoverable
- **Context Loss**: Related concepts aren't connected

### The Solution

The Basha Knowledge system addresses these challenges by:

**1. Semantic Understanding**
```
Traditional Search: "python error handling"
❌ Only finds exact matches

Semantic Search: "python error handling"
✅ Also finds:
  - "exception management in Python"
  - "try-catch blocks for Python developers"
  - "debugging Python applications"
  - "Python error recovery strategies"
```

**2. Intelligent Workflows**
Instead of remembering complex commands:
```bash
# Traditional approach
$ grep -r "error" . | head -20
$ find . -name "*.py" -exec grep -l "exception" {} \;
$ cat file.py | grep -A 5 -B 5 "try:"

# Basha approach
/basha-explore
> Search: error handling patterns
> Automatic semantic search across all documents
> Ranked results by relevance
> Context-aware suggestions for next steps
```

**3. Knowledge Graph Building**
- Documents are connected by meaning
- Discover unexpected relationships
- Build understanding across domains
- Create your personal AI knowledge assistant

### Real-World Impact

**For Individual Developers:**
- Find solutions faster
- Never lose important information
- Build on past learnings
- Create searchable code documentation

**For Teams:**
- Shared knowledge base
- Consistent information access
- Reduced onboarding time
- Preserved institutional knowledge

**For Organizations:**
- Scalable knowledge management
- AI-powered documentation
- Reduced information redundancy
- Enhanced decision-making

---

## 5. Installation and Setup {#installation}

### Prerequisites

**System Requirements:**
- macOS, Linux, or Windows (with WSL)
- Python 3.11 or higher
- PostgreSQL 14+ with pgvector extension
- Claude Code installed
- OpenAI API key

### Step 1: Database Setup

```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
createdb basha_knowledge

# Install pgvector extension
psql -d basha_knowledge -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Step 2: Python Environment

```bash
# Create conda environment
conda create -n basha_mcp python=3.11
conda activate basha_mcp

# Install dependencies
pip install 'mcp[cli]' openai psycopg2-binary python-dotenv
```

### Step 3: Environment Configuration

Create `.env` file in the project directory:
```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Step 4: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/basha-mcp-playground.git
cd basha-mcp-playground

# Navigate to the MCP server
cd phase_8_claude_integration

# Make executable
chmod +x basha_knowledge_mcp.py
```

### Step 5: Register with Claude Code

```bash
# Add the MCP server
claude mcp add basha-knowledge \
  /path/to/conda/envs/basha_mcp/bin/python \
  /path/to/basha_knowledge_mcp.py

# Verify registration
claude mcp list
# Should show: basha-knowledge

# Check server details
claude mcp get basha-knowledge
```

### Step 6: Database Configuration

Edit `basha_knowledge_mcp.py` if needed:
```python
# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'basha_knowledge',
    'user': 'your_username',  # Update this
    'password': ''            # Update if needed
}
```

### Step 7: Verify Installation

```bash
# Test the server directly
cd phase_10_final_test
python final_integration_test.py

# Should see: "PHASE 10 COMPLETE: ALL SYSTEMS SUCCESSFUL!"
```

---

## 6. Using Basha with Claude Code {#usage}

### Getting Started

Once installed, the Basha Knowledge tools and prompts are automatically available in any Claude Code session.

### Smart Prompts (Recommended Starting Point)

**1. System Overview**
```
/basha-assets
```
Shows all available capabilities, tools, and prompts with quick start guide.

**2. System Health Check**
```
/basha-test
```
Runs comprehensive diagnostics:
- Database connection
- OpenAI API status
- Document count
- Search functionality
- Performance metrics

**3. Document Discovery**
```
/basha-discover
```
Scans your project for potential knowledge sources:
- Finds all text-based files
- Groups by file type
- Shows recent modifications
- Suggests next actions

**4. Learning Workflow**
```
/basha-learn
```
Guided document ingestion:
- Analyzes found documents
- Checks suitability
- Provides ingestion commands
- Tracks progress

**5. Knowledge Exploration**
```
/basha-explore
```
Interactive knowledge base search:
- Natural language queries
- Semantic result ranking
- Exploration suggestions
- Connection discovery

### Direct Tool Usage

**1. Search Documents**
```python
search_docs({
    "query": "machine learning best practices",
    "limit": 5
})
```

**2. Add Document**
```python
add_document({
    "content": "Your document content here...",
    "metadata": {
        "source": "manual",
        "category": "machine-learning",
        "tags": ["ml", "best-practices"]
    }
})
```

**3. Get Statistics**
```python
get_stats()
```

**4. Find Data Sources**
```python
find_data_sources({
    "directory": "./docs"
})
```

**5. Analyze Document**
```python
analyze_document({
    "file_path": "./docs/guide.md"
})
```

### Practical Workflows

#### Workflow 1: Building Your Knowledge Base

```bash
# Step 1: Discover what you have
/basha-discover

# Step 2: Start learning process
/basha-learn

# Step 3: Add specific documents
add_document({
    "content": "Content from important file...",
    "metadata": {"source": "project-docs"}
})

# Step 4: Verify additions
get_stats()

# Step 5: Test search
search_docs({"query": "your topic"})
```

#### Workflow 2: Daily Knowledge Search

```bash
# Quick search for specific topic
search_docs({"query": "error handling patterns"})

# Explore related concepts
/basha-explore
> topic: "exception management"

# Deep dive into results
analyze_document({"file_path": "found_file.py"})
```

#### Workflow 3: Project Documentation

```bash
# Scan project for documentation
find_data_sources({"directory": "./src"})

# Analyze code files
analyze_document({"file_path": "./src/main.py"})

# Add code documentation
add_document({
    "content": "Main application entry point...",
    "metadata": {
        "source": "code",
        "file": "main.py",
        "type": "documentation"
    }
})
```

### Advanced Search Techniques

**1. Conceptual Queries**
```python
# Instead of: "python list comprehension"
search_docs({"query": "elegant ways to transform lists in Python"})
```

**2. Problem-Solution Queries**
```python
# Find solutions to specific problems
search_docs({"query": "how to handle database connection timeouts"})
```

**3. Relationship Queries**
```python
# Discover connections
search_docs({"query": "relationship between async and performance"})
```

**4. Learning Queries**
```python
# Educational searches
search_docs({"query": "explain decorator pattern with examples"})
```

---

## 7. Maintenance Guide {#maintenance}

### Regular Maintenance Tasks

#### Daily Tasks

**1. Check System Health**
```bash
# In Claude Code
/basha-test

# Check for:
# - Database connection: ✅
# - Document count growth
# - Search performance < 1s
```

**2. Monitor Database Size**
```sql
-- Check database size
psql -d basha_knowledge -c "
SELECT 
    pg_database_size('basha_knowledge') / 1024 / 1024 as size_mb,
    (SELECT COUNT(*) FROM documents) as doc_count;
"
```

#### Weekly Tasks

**1. Backup Database**
```bash
# Create backup
pg_dump basha_knowledge > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

**2. Update Dependencies**
```bash
conda activate basha_mcp
pip install --upgrade mcp openai psycopg2-binary
```

**3. Clean Orphaned Data**
```sql
-- Remove documents without embeddings
DELETE FROM documents 
WHERE embedding IS NULL 
AND created_at < NOW() - INTERVAL '7 days';
```

#### Monthly Tasks

**1. Performance Optimization**
```sql
-- Analyze and vacuum database
psql -d basha_knowledge -c "ANALYZE documents;"
psql -d basha_knowledge -c "VACUUM ANALYZE documents;"
```

**2. Review Metadata Quality**
```python
# In Claude Code
get_stats()
# Then query documents with poor metadata
search_docs({"query": "documents without category"})
```

### Troubleshooting Common Issues

#### Issue 1: Database Connection Failed
```bash
# Check PostgreSQL status
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Restart if needed
brew services restart postgresql      # macOS
sudo systemctl restart postgresql     # Linux

# Verify connection
psql -d basha_knowledge -c "SELECT 1;"
```

#### Issue 2: OpenAI API Errors
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API directly
python -c "
from openai import OpenAI
client = OpenAI()
print(client.models.list())
"
```

#### Issue 3: Slow Search Performance
```sql
-- Check table size
SELECT 
    relname as table,
    pg_size_pretty(pg_total_relation_size(relid)) as size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Rebuild statistics
ANALYZE documents;
```

#### Issue 4: MCP Server Not Found
```bash
# Re-register server
claude mcp remove basha-knowledge
claude mcp add basha-knowledge \
  /path/to/python \
  /path/to/basha_knowledge_mcp.py

# Verify
claude mcp list
```

### Log Management

**1. Enable Logging**
Add to `basha_knowledge_mcp.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='basha_mcp.log'
)
```

**2. Monitor Logs**
```bash
# Watch logs in real-time
tail -f basha_mcp.log

# Search for errors
grep ERROR basha_mcp.log

# Check recent activity
tail -n 100 basha_mcp.log
```

### Performance Monitoring

**1. Create Monitoring Script**
```python
# monitor_performance.py
import asyncio
import time
from basha_knowledge_mcp import EnhancedBashaMCPServer

async def monitor():
    server = EnhancedBashaMCPServer()
    
    # Test search performance
    start = time.time()
    results = await server.search_documents("test", 5)
    search_time = time.time() - start
    
    # Test embedding performance
    start = time.time()
    embedding = server.get_embedding("test embedding")
    embed_time = time.time() - start
    
    # Get stats
    stats = await server.get_stats()
    
    print(f"Search Time: {search_time:.3f}s")
    print(f"Embedding Time: {embed_time:.3f}s")
    print(f"Total Documents: {stats['total_documents']}")
    
    # Alert if performance degrades
    if search_time > 1.0:
        print("⚠️ WARNING: Search performance degraded!")
    if embed_time > 0.5:
        print("⚠️ WARNING: Embedding performance degraded!")

asyncio.run(monitor())
```

---

## 8. Expanding and Improving {#expansion}

### Adding New Tools

**1. Tool Template**
```python
# In basha_knowledge_mcp.py

# Add to tool list
Tool(
    name="your_tool_name",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"},
            "param2": {"type": "integer", "description": "Optional param", "default": 10}
        },
        "required": ["param1"]
    }
)

# Add tool handler
elif name == "your_tool_name":
    param1 = arguments.get("param1")
    param2 = arguments.get("param2", 10)
    
    try:
        # Your tool logic here
        result = await server.your_method(param1, param2)
        return [TextContent(type="text", text=f"Result: {result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**2. Example: Export Tool**
```python
# Add export functionality
async def export_knowledge(self, format: str = "json") -> str:
    """Export knowledge base"""
    with self.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM documents")
            docs = cur.fetchall()
            
            if format == "json":
                return json.dumps(docs, default=str, indent=2)
            elif format == "csv":
                # CSV export logic
                pass
```

### Adding New Prompts

**1. Prompt Template**
```python
# Add to prompt list
Prompt(
    name="basha-insights",
    description="Generate insights from your knowledge base",
    arguments=[
        {
            "name": "topic",
            "description": "Topic to analyze",
            "required": False
        }
    ]
)

# Add prompt handler
elif name == "basha-insights":
    topic = arguments.get("topic", "general")
    
    # Complex workflow
    stats = await server.get_stats()
    
    # Search for topic
    if topic != "general":
        results = await server.search_documents(topic, 10)
    
    # Generate insights
    response = f"""📊 **Knowledge Base Insights: {topic}**
    
Total Documents: {stats['total_documents']}
Topic Coverage: {len(results)} relevant documents

Key Themes:
• [Analyze and list themes]
• [Identify patterns]
• [Suggest connections]

Recommendations:
• [Suggest areas to expand]
• [Identify gaps]
• [Propose next steps]
"""
    return response
```

### Enhancing Search Capabilities

**1. Metadata Filtering**
```python
async def search_with_metadata(self, query: str, filters: Dict) -> List[Dict]:
    """Search with metadata filters"""
    query_embedding = self.get_embedding(query)
    
    # Build WHERE clause
    where_clauses = ["embedding IS NOT NULL"]
    params = [query_embedding, query_embedding]
    
    if 'category' in filters:
        where_clauses.append("metadata->>'category' = %s")
        params.append(filters['category'])
    
    if 'after_date' in filters:
        where_clauses.append("created_at > %s")
        params.append(filters['after_date'])
    
    where_sql = " AND ".join(where_clauses)
    params.append(limit)
    
    # Execute query
    with self.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT *, 1 - (embedding <=> %s::vector) as similarity
                FROM documents
                WHERE {where_sql}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, params)
            return cur.fetchall()
```

**2. Hybrid Search (Keyword + Semantic)**
```python
async def hybrid_search(self, query: str, limit: int = 5) -> List[Dict]:
    """Combine keyword and semantic search"""
    # Semantic search
    semantic_results = await self.search_documents(query, limit * 2)
    
    # Keyword search
    with self.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *, 
                       ts_rank(to_tsvector('english', content), 
                              plainto_tsquery('english', %s)) as keyword_score
                FROM documents
                WHERE to_tsvector('english', content) @@ 
                      plainto_tsquery('english', %s)
                ORDER BY keyword_score DESC
                LIMIT %s
            """, (query, query, limit * 2))
            keyword_results = cur.fetchall()
    
    # Merge and re-rank
    # [Implementation of merging logic]
    return merged_results[:limit]
```

### Adding AI Capabilities

**1. Summarization**
```python
async def summarize_documents(self, doc_ids: List[int]) -> str:
    """Generate summary of multiple documents"""
    # Fetch documents
    docs = await self.get_documents_by_ids(doc_ids)
    
    # Prepare prompt
    combined_text = "\n\n".join([doc['content'] for doc in docs])
    
    # Call GPT for summarization
    response = self.openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize these documents concisely"},
            {"role": "user", "content": combined_text}
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

**2. Question Answering**
```python
async def answer_question(self, question: str) -> str:
    """Answer questions using knowledge base"""
    # Search for relevant documents
    results = await self.search_documents(question, 5)
    
    if not results:
        return "No relevant information found in knowledge base."
    
    # Prepare context
    context = "\n\n".join([
        f"Document {i+1}: {doc['content'][:500]}..."
        for i, doc in enumerate(results)
    ])
    
    # Generate answer
    response = self.openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Answer based on the provided context"},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    
    return response.choices[0].message.content
```

### Integration Extensions

**1. GitHub Integration**
```python
# Add tool for GitHub documentation
Tool(
    name="import_github_readme",
    description="Import README from GitHub repository",
    inputSchema={
        "type": "object",
        "properties": {
            "repo_url": {"type": "string", "description": "GitHub repository URL"}
        },
        "required": ["repo_url"]
    }
)

# Implementation
async def import_github_readme(self, repo_url: str) -> int:
    """Import README from GitHub"""
    # Parse repo URL
    # Fetch README content
    # Add to knowledge base
    pass
```

**2. Slack Integration**
```python
# Tool for Slack messages
async def import_slack_thread(self, thread_url: str) -> int:
    """Import important Slack discussions"""
    # Connect to Slack API
    # Fetch thread content
    # Process and add to knowledge base
    pass
```

### Performance Optimizations

**1. Batch Processing**
```python
async def batch_add_documents(self, documents: List[Dict]) -> List[int]:
    """Add multiple documents efficiently"""
    doc_ids = []
    
    # Get all embeddings in parallel
    contents = [doc['content'] for doc in documents]
    embeddings = await self.batch_get_embeddings(contents)
    
    # Batch insert
    with self.get_db_connection() as conn:
        with conn.cursor() as cur:
            for doc, embedding in zip(documents, embeddings):
                cur.execute("""
                    INSERT INTO documents (content, embedding, metadata)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (doc['content'], embedding, json.dumps(doc.get('metadata', {}))))
                doc_ids.append(cur.fetchone()[0])
            conn.commit()
    
    return doc_ids
```

**2. Caching**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_embedding(self, text_hash: str) -> List[float]:
    """Cache embeddings for repeated text"""
    # This is called with hash of text
    # Actual implementation would store/retrieve from cache
    pass

def get_embedding_with_cache(self, text: str) -> List[float]:
    """Get embedding with caching"""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Check cache first
    cached = self.cached_embedding(text_hash)
    if cached:
        return cached
    
    # Generate new embedding
    embedding = self.get_embedding(text)
    
    # Store in cache
    self.cached_embedding(text_hash, embedding)
    
    return embedding
```

---

## 9. Advanced Testing and Development {#testing}

### Testing Framework

**1. Unit Tests**
```python
# test_basha_mcp.py
import pytest
import asyncio
from basha_knowledge_mcp import EnhancedBashaMCPServer

@pytest.fixture
async def server():
    """Create test server instance"""
    server = EnhancedBashaMCPServer()
    server.setup_database()
    return server

@pytest.mark.asyncio
async def test_add_document(server):
    """Test document addition"""
    doc_id = await server.add_document(
        "Test document content",
        {"category": "test"}
    )
    assert isinstance(doc_id, int)
    assert doc_id > 0

@pytest.mark.asyncio
async def test_search_documents(server):
    """Test search functionality"""
    # Add test document
    await server.add_document("Python programming guide", {"category": "programming"})
    
    # Search for it
    results = await server.search_documents("Python", 5)
    assert len(results) > 0
    assert results[0]['similarity'] > 0

@pytest.mark.asyncio
async def test_semantic_similarity(server):
    """Test semantic search quality"""
    # Add related documents
    await server.add_document("Machine learning with Python", {"topic": "ml"})
    await server.add_document("Deep learning frameworks", {"topic": "ml"})
    await server.add_document("Cooking recipes collection", {"topic": "food"})
    
    # Search for ML content
    results = await server.search_documents("artificial intelligence", 3)
    
    # ML documents should rank higher
    ml_docs = [r for r in results if r['metadata'].get('topic') == 'ml']
    assert len(ml_docs) >= 2
    assert ml_docs[0]['similarity'] > 0.3
```

**2. Integration Tests**
```python
# test_integration.py
import subprocess
import json

def test_mcp_server_registration():
    """Test MCP server is registered"""
    result = subprocess.run(
        ['claude', 'mcp', 'list'],
        capture_output=True,
        text=True
    )
    assert 'basha-knowledge' in result.stdout

def test_mcp_protocol():
    """Test MCP protocol communication"""
    # Initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "0.1.0"}
    }
    
    # Send to server and verify response
    # [Implementation of protocol testing]
    pass

def test_tool_execution():
    """Test tool execution through MCP"""
    tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_stats",
            "arguments": {}
        }
    }
    
    # Verify tool executes correctly
    # [Implementation]
    pass
```

**3. Performance Tests**
```python
# test_performance.py
import time
import asyncio
from statistics import mean, stdev

async def test_search_performance(server, iterations=100):
    """Test search performance"""
    search_times = []
    
    for _ in range(iterations):
        start = time.time()
        await server.search_documents("test query", 5)
        search_times.append(time.time() - start)
    
    avg_time = mean(search_times)
    std_dev = stdev(search_times)
    
    print(f"Average search time: {avg_time:.3f}s")
    print(f"Standard deviation: {std_dev:.3f}s")
    print(f"Max time: {max(search_times):.3f}s")
    print(f"Min time: {min(search_times):.3f}s")
    
    # Assert performance requirements
    assert avg_time < 1.0, "Average search time exceeds 1 second"
    assert max(search_times) < 2.0, "Maximum search time exceeds 2 seconds"

async def test_embedding_performance(server, iterations=50):
    """Test embedding generation performance"""
    embed_times = []
    test_texts = [
        "Short text",
        "Medium length text with more content to process",
        "Long text " * 100  # Longer text
    ]
    
    for text in test_texts:
        for _ in range(iterations):
            start = time.time()
            server.get_embedding(text)
            embed_times.append(time.time() - start)
    
    avg_time = mean(embed_times)
    print(f"Average embedding time: {avg_time:.3f}s")
    
    assert avg_time < 0.5, "Average embedding time exceeds 0.5 seconds"
```

### Development Workflow

**1. Local Development Setup**
```bash
# Create development branch
git checkout -b feature/your-feature

# Set up test database
createdb basha_knowledge_test

# Run tests
pytest tests/ -v

# Check code quality
pylint basha_knowledge_mcp.py
black basha_knowledge_mcp.py
```

**2. Test-Driven Development**
```python
# 1. Write test first
async def test_new_feature(server):
    """Test the new feature"""
    result = await server.new_feature("input")
    assert result == "expected output"

# 2. Implement feature
async def new_feature(self, input: str) -> str:
    """Implementation"""
    # Make test pass
    return "expected output"

# 3. Refactor and improve
async def new_feature(self, input: str) -> str:
    """Improved implementation"""
    # Real implementation
    processed = self.process_input(input)
    return self.generate_output(processed)
```

**3. Debugging MCP Issues**
```bash
# Enable MCP debug mode
claude --mcp-debug

# Check server logs
tail -f ~/.claude/logs/mcp-*.log

# Test server directly
python basha_knowledge_mcp.py --test

# Use verbose mode
BASHA_DEBUG=1 python basha_knowledge_mcp.py
```

### Continuous Integration

**1. GitHub Actions Workflow**
```yaml
# .github/workflows/test.yml
name: Test Basha MCP

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Set up database
      run: |
        psql -h localhost -U postgres -c "CREATE DATABASE basha_knowledge_test;"
        psql -h localhost -U postgres -d basha_knowledge_test -c "CREATE EXTENSION vector;"
      env:
        PGPASSWORD: postgres
    
    - name: Run tests
      run: |
        pytest tests/ -v
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        DATABASE_URL: postgresql://postgres:postgres@localhost/basha_knowledge_test
```

**2. Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/pylint
    rev: v2.17.0
    hooks:
      - id: pylint
        args: [--disable=C0116]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
```

### Load Testing

```python
# load_test.py
import asyncio
import random
from concurrent.futures import ThreadPoolExecutor
import time

async def simulate_user(user_id: int, server, duration: int = 60):
    """Simulate a user interacting with the system"""
    start_time = time.time()
    actions = 0
    
    while time.time() - start_time < duration:
        # Random action
        action = random.choice(['search', 'add', 'stats'])
        
        try:
            if action == 'search':
                query = random.choice(['python', 'error', 'database', 'api'])
                await server.search_documents(query, 5)
            elif action == 'add':
                content = f"Test document {user_id}-{actions}"
                await server.add_document(content, {"user": user_id})
            else:
                await server.get_stats()
            
            actions += 1
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            print(f"User {user_id} error: {e}")
    
    return actions

async def load_test(num_users: int = 10, duration: int = 60):
    """Run load test"""
    server = EnhancedBashaMCPServer()
    
    print(f"Starting load test with {num_users} users for {duration} seconds")
    
    # Create tasks for all users
    tasks = [
        simulate_user(i, server, duration)
        for i in range(num_users)
    ]
    
    # Run concurrently
    start = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start
    
    # Calculate statistics
    total_actions = sum(results)
    actions_per_second = total_actions / total_time
    
    print(f"\nLoad Test Results:")
    print(f"Total actions: {total_actions}")
    print(f"Actions per second: {actions_per_second:.2f}")
    print(f"Average actions per user: {total_actions / num_users:.2f}")

# Run load test
asyncio.run(load_test(num_users=20, duration=120))
```

---

## 10. Troubleshooting {#troubleshooting}

### Common Issues and Solutions

#### Issue: "MCP server not found"
```bash
# Symptom
Claude Code shows: "No MCP servers configured"

# Solution 1: Re-register server
claude mcp remove basha-knowledge
claude mcp add basha-knowledge /path/to/python /path/to/server.py

# Solution 2: Check Claude Code config
cat ~/.claude/config.json | grep mcp

# Solution 3: Verify server path
ls -la /path/to/basha_knowledge_mcp.py
```

#### Issue: "Database connection failed"
```bash
# Symptom
Error: "connection to server at localhost failed"

# Solution 1: Check PostgreSQL
brew services list | grep postgresql
sudo systemctl status postgresql

# Solution 2: Verify database exists
psql -l | grep basha_knowledge

# Solution 3: Check permissions
psql -c "\du" | grep your_username

# Solution 4: Reset database
dropdb basha_knowledge
createdb basha_knowledge
psql -d basha_knowledge -c "CREATE EXTENSION vector;"
```

#### Issue: "OpenAI API error"
```bash
# Symptom
Error: "Invalid API key" or "Rate limit exceeded"

# Solution 1: Verify API key
python -c "import os; print(os.getenv('OPENAI_API_KEY')[:10] + '...')"

# Solution 2: Check API limits
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Solution 3: Use different model
# In server code, change:
model="text-embedding-3-large"  # to
model="text-embedding-3-small"  # cheaper, smaller
```

#### Issue: "Slow search performance"
```sql
-- Symptom: Searches take > 2 seconds

-- Solution 1: Check table size
SELECT 
    COUNT(*) as doc_count,
    pg_size_pretty(pg_total_relation_size('documents')) as table_size
FROM documents;

-- Solution 2: Vacuum and analyze
VACUUM ANALYZE documents;

-- Solution 3: Check for NULL embeddings
SELECT COUNT(*) FROM documents WHERE embedding IS NULL;

-- Solution 4: Limit result size
-- In searches, use smaller limit values
```

#### Issue: "Import errors"
```bash
# Symptom
ImportError: No module named 'mcp'

# Solution 1: Activate environment
conda activate basha_mcp

# Solution 2: Reinstall dependencies
pip install --upgrade 'mcp[cli]'

# Solution 3: Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Solution 4: Verify installation
pip show mcp
```

### Error Messages Explained

**1. "embedding index too large"**
- Cause: pgvector has dimension limits for certain index types
- Solution: Remove index or use different index type
- Prevention: Use appropriate index for high dimensions

**2. "JSON-RPC parse error"**
- Cause: Malformed request to MCP server
- Solution: Check request format, ensure proper JSON
- Prevention: Use official MCP client libraries

**3. "Tool not found"**
- Cause: Tool name mismatch or not registered
- Solution: Check tool name spelling, verify registration
- Prevention: Use consistent naming convention

**4. "Prompt timeout"**
- Cause: Complex prompt taking too long
- Solution: Optimize prompt logic, add timeouts
- Prevention: Break complex prompts into smaller steps

### Debug Mode

**1. Enable Debug Logging**
```python
# Add to server
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug(f"Search query: {query}")
logger.info(f"Found {len(results)} results")
logger.error(f"Database error: {e}")
```

**2. MCP Protocol Debugging**
```python
# Add protocol logging
class DebugMCPServer(Server):
    async def handle_request(self, request):
        logger.debug(f"Received: {json.dumps(request, indent=2)}")
        response = await super().handle_request(request)
        logger.debug(f"Sending: {json.dumps(response, indent=2)}")
        return response
```

**3. Performance Profiling**
```python
import cProfile
import pstats

def profile_function():
    """Profile specific function"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Function to profile
    results = asyncio.run(server.search_documents("test", 10))
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

---

## 11. Technical Deep Dive {#technical}

### Vector Embeddings Explained

**What are embeddings?**
Embeddings are numerical representations of text that capture semantic meaning. The text-embedding-3-large model converts text into 3072-dimensional vectors where similar meanings have similar vectors.

**Example:**
```python
# Text representations
text1 = "Python programming language"
text2 = "Python coding and development"  
text3 = "Snake species information"

# After embedding (simplified)
embedding1 = [0.82, 0.15, 0.92, ...]  # 3072 numbers
embedding2 = [0.79, 0.18, 0.89, ...]  # Similar to embedding1
embedding3 = [0.21, 0.65, 0.33, ...]  # Different from embedding1

# Similarity calculation
similarity_1_2 = cosine_similarity(embedding1, embedding2)  # ~0.95 (high)
similarity_1_3 = cosine_similarity(embedding1, embedding3)  # ~0.20 (low)
```

### Cosine Similarity Mathematics

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between vectors"""
    # Dot product
    dot_product = np.dot(vec1, vec2)
    
    # Magnitudes
    magnitude1 = np.linalg.norm(vec1)
    magnitude2 = np.linalg.norm(vec2)
    
    # Cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    
    return similarity

# pgvector uses 1 - cosine_distance
# So similarity = 1 - distance
```

### MCP Protocol Details

**Message Flow:**
```
1. Initialize
   Client → Server: {"method": "initialize", "params": {...}}
   Server → Client: {"result": {"capabilities": {...}}}

2. List Tools
   Client → Server: {"method": "tools/list"}
   Server → Client: {"result": {"tools": [...]}}

3. Call Tool
   Client → Server: {"method": "tools/call", "params": {"name": "...", "arguments": {...}}}
   Server → Client: {"result": {"content": [...]}}
```

**Error Handling:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": "Missing required parameter: query"
  }
}
```

### Database Schema Details

```sql
-- Full schema
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional indexes for performance
    INDEX idx_created_at ON documents(created_at DESC),
    INDEX idx_metadata_gin ON documents USING gin(metadata)
);

-- Full-text search support
ALTER TABLE documents ADD COLUMN content_tsvector tsvector;
UPDATE documents SET content_tsvector = to_tsvector('english', content);
CREATE INDEX idx_content_fts ON documents USING gin(content_tsvector);

-- Example metadata queries
SELECT * FROM documents 
WHERE metadata @> '{"category": "python"}'
ORDER BY created_at DESC;

-- Combined search
SELECT *,
       1 - (embedding <=> %s::vector) as semantic_score,
       ts_rank(content_tsvector, plainto_tsquery('english', %s)) as keyword_score
FROM documents
WHERE embedding IS NOT NULL
ORDER BY (semantic_score * 0.7 + keyword_score * 0.3) DESC;
```

### Performance Optimization Techniques

**1. Connection Pooling**
```python
from psycopg2 import pool

class PooledBashaMCPServer:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min and max connections
            **DB_CONFIG
        )
    
    def get_db_connection(self):
        return self.connection_pool.getconn()
    
    def return_db_connection(self, conn):
        self.connection_pool.putconn(conn)
```

**2. Batch Embedding Generation**
```python
async def batch_get_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """Get embeddings in batches for efficiency"""
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=batch,
            encoding_format="float"
        )
        
        embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(embeddings)
    
    return all_embeddings
```

**3. Query Optimization**
```python
# Use prepared statements
SEARCH_QUERY = """
PREPARE search_plan AS
SELECT id, content, metadata, created_at,
       1 - (embedding <=> $1::vector) as similarity
FROM documents
WHERE embedding IS NOT NULL
ORDER BY embedding <=> $1::vector
LIMIT $2;
"""

# Execute prepared statement
cur.execute("EXECUTE search_plan (%s, %s)", (query_embedding, limit))
```

### Security Considerations

**1. Input Validation**
```python
def validate_input(self, text: str) -> str:
    """Validate and sanitize input"""
    # Length check
    if len(text) > 10000:
        raise ValueError("Text too long (max 10000 characters)")
    
    # Basic sanitization
    text = text.strip()
    
    # SQL injection prevention (handled by parameterized queries)
    # XSS prevention (if outputting to web)
    
    return text
```

**2. Rate Limiting**
```python
from functools import wraps
import time

def rate_limit(calls_per_minute: int = 60):
    """Rate limiting decorator"""
    min_interval = 60.0 / calls_per_minute
    last_called = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            key = f"{func.__name__}:{id(self)}"
            
            if key in last_called:
                elapsed = time.time() - last_called[key]
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)
            
            last_called[key] = time.time()
            return await func(self, *args, **kwargs)
        
        return wrapper
    return decorator

# Usage
@rate_limit(calls_per_minute=30)
async def search_documents(self, query: str, limit: int = 5):
    # Implementation
    pass
```

**3. API Key Management**
```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        # Load encrypted key
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
        
    def get_api_key(self):
        """Get decrypted API key"""
        encrypted = os.getenv('ENCRYPTED_OPENAI_KEY')
        return self.cipher.decrypt(encrypted.encode()).decode()
```

---

## 12. Future Roadmap {#roadmap}

### Short Term (1-3 months)

**1. Enhanced Search Features**
- [ ] Faceted search with metadata filtering
- [ ] Search history and analytics
- [ ] Saved searches and alerts
- [ ] Search result explanations

**2. Improved Document Management**
- [ ] Bulk import from various sources
- [ ] Automatic tagging and categorization
- [ ] Document versioning
- [ ] Duplicate detection

**3. Better Integration**
- [ ] VSCode extension
- [ ] Browser extension for web content
- [ ] CLI tool for command-line usage
- [ ] REST API endpoint option

### Medium Term (3-6 months)

**1. Advanced AI Features**
- [ ] Document summarization
- [ ] Question answering system
- [ ] Knowledge graph visualization
- [ ] Automatic insight generation

**2. Collaboration Features**
- [ ] Shared knowledge bases
- [ ] Team permissions
- [ ] Collaborative annotations
- [ ] Knowledge base merging

**3. Performance Improvements**
- [ ] Distributed search
- [ ] Caching layer
- [ ] Async processing queue
- [ ] Optimized embedding storage

### Long Term (6-12 months)

**1. Multi-Modal Support**
- [ ] Image embeddings
- [ ] Code understanding
- [ ] Audio transcription
- [ ] Video content analysis

**2. Advanced Workflows**
- [ ] Custom prompt builder
- [ ] Workflow automation
- [ ] Integration marketplace
- [ ] Plugin system

**3. Enterprise Features**
- [ ] SSO integration
- [ ] Audit logging
- [ ] Compliance tools
- [ ] Advanced security

### Community Contributions

**How to Contribute:**
1. Fork the repository
2. Create feature branch
3. Implement with tests
4. Submit pull request

**Contribution Ideas:**
- New tool implementations
- Language translations
- Documentation improvements
- Bug fixes and optimizations
- Integration examples

### Research Directions

**1. Embedding Improvements**
- Experiment with different models
- Fine-tuning for specific domains
- Hybrid embedding approaches
- Compression techniques

**2. Search Algorithm Research**
- Learning to rank
- Personalized search
- Context-aware retrieval
- Query understanding

**3. Knowledge Organization**
- Automatic taxonomy generation
- Concept extraction
- Relationship mapping
- Knowledge validation

---

## Conclusion

The Basha Knowledge MCP Server represents a significant step forward in how we interact with information. By combining semantic search, intelligent workflows, and seamless Claude Code integration, it transforms scattered documentation into an intelligent, searchable knowledge system.

### Key Takeaways

1. **Semantic Search Works**: Finding information by meaning, not keywords, fundamentally changes how we access knowledge

2. **Smart Prompts > Raw Tools**: Guided workflows make complex systems accessible and powerful

3. **MCP Enables Integration**: The Model Context Protocol provides a secure, standardized way to extend AI capabilities

4. **Incremental Development Wins**: Building from simple tests to production system ensures reliability

5. **Knowledge Compounds**: Each document added makes the system more valuable

### Final Thoughts

This system is more than a search tool—it's a foundation for building your personal AI knowledge assistant. As you add more documents, create custom workflows, and integrate with your tools, it becomes increasingly valuable and tailored to your needs.

The journey from playground to production demonstrates that with the right architecture and incremental approach, we can build sophisticated AI-powered systems that genuinely enhance our capabilities as developers and knowledge workers.

**Happy knowledge building! 🚀**

---

*For questions, contributions, or discussions, please open an issue on GitHub or reach out to the community.*