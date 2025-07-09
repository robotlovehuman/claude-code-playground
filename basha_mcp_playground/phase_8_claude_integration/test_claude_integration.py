#!/usr/bin/env python3
"""
Test script for Claude Code MCP Integration
Tests that the MCP server is properly configured and accessible to Claude Code
"""

import os
import sys
import json
import subprocess

def test_claude_integration():
    """Test the Claude Code MCP integration"""
    print("=== Phase 8: Claude Code MCP Integration Test ===\n")
    
    # Test 1: Verify Claude Code can list the MCP server
    print("1. Testing MCP server registration...")
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout.strip()
            if 'basha-knowledge' in output:
                print("✅ MCP server is registered with Claude Code")
                print(f"   Output: {output}")
            else:
                print("❌ MCP server not found in Claude Code list")
                return False
        else:
            print(f"❌ Failed to list MCP servers: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout waiting for Claude Code response")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server list: {e}")
        return False
    
    # Test 2: Get detailed server information
    print("\n2. Testing server details...")
    try:
        result = subprocess.run(['claude', 'mcp', 'get', 'basha-knowledge'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout.strip()
            print("✅ Server details retrieved successfully:")
            print(f"   {output}")
        else:
            print(f"❌ Failed to get server details: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error getting server details: {e}")
        return False
    
    # Test 3: Verify server executable and dependencies
    print("\n3. Testing server executable...")
    try:
        server_path = "/Users/kimomaxmac/codingMacMaxHQ/local_ai_hq/kimoFrameWork/claudeCodePlayground/basha_mcp_playground/phase_8_claude_integration/basha_knowledge_mcp.py"
        
        # Check if server file exists and is executable
        if os.path.exists(server_path) and os.access(server_path, os.X_OK):
            print("✅ Server file exists and is executable")
        else:
            print("❌ Server file missing or not executable")
            return False
        
        # Check Python environment
        python_path = "/opt/homebrew/Caskroom/miniconda/base/envs/ai_stuff/bin/python"
        if os.path.exists(python_path):
            print("✅ Python environment available")
        else:
            print("❌ Python environment not found")
            return False
        
    except Exception as e:
        print(f"❌ Error checking server executable: {e}")
        return False
    
    # Test 4: Test environment variables
    print("\n4. Testing environment setup...")
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("✅ OPENAI_API_KEY is set")
        else:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        # Test database connection (basic check)
        import psycopg2
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='basha_knowledge',
                user='kimomaxmac',
                password=''
            )
            conn.close()
            print("✅ Database connection available")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing environment: {e}")
        return False
    
    # Test 5: Create integration verification script
    print("\n5. Creating integration verification...")
    try:
        verification_script = """
# Basha Knowledge MCP Server Integration Verification

## How to Test:
1. In a new Claude Code session, try these commands:
   - `get_stats` - Should show knowledge base statistics
   - `search_docs` with query "test" - Should search documents
   - `add_document` with sample content - Should add to knowledge base

2. Try smart prompts:
   - `/basha-assets` - Should show server capabilities
   - `/basha-test` - Should run diagnostics
   - `/basha-learn` - Should show learning workflow

## Expected Results:
- Tools should work without errors
- Smart prompts should provide guided workflows
- Database operations should complete successfully
- OpenAI embeddings should generate properly

## Troubleshooting:
- If tools fail, check database connection
- If embeddings fail, verify OpenAI API key
- If server doesn't start, check Python environment
"""
        
        with open("INTEGRATION_VERIFICATION.md", "w") as f:
            f.write(verification_script)
        
        print("✅ Integration verification guide created")
        
    except Exception as e:
        print(f"❌ Error creating verification script: {e}")
        return False
    
    # Test 6: Summary and next steps
    print("\n6. Integration summary...")
    print("✅ Phase 8 PASSED: Claude Code MCP Integration complete!")
    print()
    print("🎯 **Integration Status:**")
    print("• MCP server registered with Claude Code")
    print("• Server executable and dependencies verified")
    print("• Environment variables configured")
    print("• Database connection available")
    print("• Ready for real-time Claude Code usage")
    print()
    print("🚀 **Next Steps:**")
    print("• Test the integration in a new Claude Code session")
    print("• Try the smart prompts: /basha-assets, /basha-test, /basha-learn")
    print("• Add documents with add_document tool")
    print("• Search with search_docs tool")
    print("• Build your intelligent knowledge base!")
    
    return True

if __name__ == "__main__":
    success = test_claude_integration()
    sys.exit(0 if success else 1)