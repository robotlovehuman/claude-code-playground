#!/usr/bin/env python3
"""
Test script for Basha MCP Server
Tests the real MCP server implementation
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import the server
sys.path.append(str(Path(__file__).parent))

from basha_mcp_server import BashaMCPServer

async def test_basha_server():
    """Test the Basha MCP Server functionality"""
    print("=== Phase 6: Real MCP Server Test ===\n")
    
    # Initialize server
    server = BashaMCPServer()
    
    # Test 1: Database connection and setup
    print("1. Testing database connection...")
    try:
        server.setup_database()
        stats = await server.get_stats()
        print(f"✅ Database connected: {stats}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test 2: Add a test document
    print("\n2. Testing document addition...")
    try:
        doc_id = await server.add_document(
            "This is a test document about Python programming and MCP servers",
            {"source": "test", "category": "programming"}
        )
        print(f"✅ Document added with ID: {doc_id}")
    except Exception as e:
        print(f"❌ Document addition failed: {e}")
        return False
    
    # Test 3: Add another document
    print("\n3. Adding another test document...")
    try:
        doc_id2 = await server.add_document(
            "Claude Code is an AI assistant that helps with programming tasks",
            {"source": "test", "category": "AI"}
        )
        print(f"✅ Second document added with ID: {doc_id2}")
    except Exception as e:
        print(f"❌ Second document addition failed: {e}")
        return False
    
    # Test 4: Semantic search
    print("\n4. Testing semantic search...")
    try:
        results = await server.search_documents("programming", 3)
        print(f"✅ Found {len(results)} documents for 'programming':")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc['content'][:50]}... (similarity: {doc['similarity']:.3f})")
    except Exception as e:
        print(f"❌ Semantic search failed: {e}")
        return False
    
    # Test 5: Different search query
    print("\n5. Testing different search query...")
    try:
        results = await server.search_documents("AI assistant", 3)
        print(f"✅ Found {len(results)} documents for 'AI assistant':")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc['content'][:50]}... (similarity: {doc['similarity']:.3f})")
    except Exception as e:
        print(f"❌ Second search failed: {e}")
        return False
    
    # Test 6: Final stats
    print("\n6. Final database stats...")
    try:
        stats = await server.get_stats()
        print(f"✅ Final stats: {stats}")
    except Exception as e:
        print(f"❌ Stats retrieval failed: {e}")
        return False
    
    print("\n✅ Phase 6 PASSED: Real MCP Server is working!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_basha_server())
    sys.exit(0 if success else 1)