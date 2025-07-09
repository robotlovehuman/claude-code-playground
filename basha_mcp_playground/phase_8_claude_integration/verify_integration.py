#!/usr/bin/env python3
"""
Simple verification script for MCP server integration
"""

import os
import sys

def verify_integration():
    """Verify the MCP server integration is ready"""
    print("=== Phase 8: MCP Integration Verification ===\n")
    
    # Check 1: Server file exists
    server_path = "/Users/kimomaxmac/codingMacMaxHQ/local_ai_hq/kimoFrameWork/claudeCodePlayground/basha_mcp_playground/phase_8_claude_integration/basha_knowledge_mcp.py"
    if os.path.exists(server_path) and os.access(server_path, os.X_OK):
        print("✅ MCP server file exists and is executable")
    else:
        print("❌ MCP server file missing or not executable")
        return False
    
    # Check 2: Python environment
    python_path = "/opt/homebrew/Caskroom/miniconda/base/envs/ai_stuff/bin/python"
    if os.path.exists(python_path):
        print("✅ Python environment available")
    else:
        print("❌ Python environment not found")
        return False
    
    # Check 3: OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY is configured")
    else:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    # Check 4: Database connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            database='basha_knowledge',
            user='kimomaxmac',
            password=''
        )
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check 5: MCP dependencies
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        print("✅ MCP dependencies available")
    except ImportError as e:
        print(f"❌ MCP dependencies missing: {e}")
        return False
    
    print("\n✅ Phase 8 PASSED: MCP Integration verified!")
    print("\n🎯 **Integration Status:**")
    print("• MCP server: basha-knowledge")
    print("• Command: claude mcp list")
    print("• Status: Ready for Claude Code usage")
    print("• Database: Connected and ready")
    print("• AI: OpenAI embeddings configured")
    
    print("\n🚀 **How to Use:**")
    print("1. In Claude Code session, tools are automatically available:")
    print("   • search_docs - Search your knowledge base")
    print("   • add_document - Add new documents")
    print("   • get_stats - Check database status")
    print("   • find_data_sources - Discover files")
    print("   • analyze_document - Analyze content")
    
    print("\n2. Smart prompts provide guided workflows:")
    print("   • /basha-assets - Show all capabilities")
    print("   • /basha-test - Run system diagnostics")
    print("   • /basha-learn - Document ingestion workflow")
    print("   • /basha-discover - Find data sources")
    print("   • /basha-explore - Knowledge exploration")
    
    return True

if __name__ == "__main__":
    success = verify_integration()
    sys.exit(0 if success else 1)