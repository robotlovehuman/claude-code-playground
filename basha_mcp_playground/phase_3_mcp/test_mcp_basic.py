#!/usr/bin/env python3
"""
Phase 3: Basic MCP Server Test
Goal: Create simplest possible MCP server with one tool
Test: Server responds to "test_tool" with "Hello from MCP"
"""

import json
import sys
import asyncio
from typing import Any, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Minimal MCP server implementation"""
    
    def __init__(self):
        self.tools = {
            "test_tool": {
                "description": "A simple test tool that returns a greeting",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC request"""
        method = request.get("method")
        request_id = request.get("id", 1)
        
        logger.info(f"Received request: {method}")
        
        if method == "initialize":
            return self.create_response(request_id, {
                "protocolVersion": "1.0",
                "serverInfo": {
                    "name": "test-mcp-server",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "tools": {}
                }
            })
        
        elif method == "tools/list":
            return self.create_response(request_id, {
                "tools": [
                    {
                        "name": name,
                        "description": info["description"],
                        "inputSchema": info["inputSchema"]
                    }
                    for name, info in self.tools.items()
                ]
            })
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            
            if tool_name == "test_tool":
                return self.create_response(request_id, {
                    "result": {
                        "message": "Hello from MCP! 🎉",
                        "status": "success",
                        "details": "MCP server is working correctly"
                    }
                })
            else:
                return self.create_error(request_id, -32602, f"Unknown tool: {tool_name}")
        
        else:
            return self.create_error(request_id, -32601, f"Method not found: {method}")
    
    def create_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create JSON-RPC response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def create_error(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Simple MCP Server...")
        logger.info("Available tools: test_tool")
        
        reader, writer = await asyncio.open_connection(None, None)
        
        try:
            while True:
                # Read request from stdin
                line = await reader.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.decode())
                    response = await self.handle_request(request)
                    
                    # Write response to stdout
                    writer.write(json.dumps(response).encode() + b'\n')
                    await writer.drain()
                    
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
        
        finally:
            writer.close()
            await writer.wait_closed()

def test_server_locally():
    """Test the server with a simple request"""
    print("=== Phase 3: MCP Server Test ===\n")
    
    server = SimpleMCPServer()
    
    # Test requests
    test_requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "test_tool"}}
    ]
    
    async def run_tests():
        for req in test_requests:
            print(f"Testing: {req['method']}")
            response = await server.handle_request(req)
            print(f"Response: {json.dumps(response, indent=2)}\n")
            
            # Verify response
            if "error" in response:
                return False
            if req["method"] == "tools/call" and "Hello from MCP" not in str(response):
                return False
        
        return True
    
    # Run tests
    success = asyncio.run(run_tests())
    
    if success:
        print("✅ All MCP server tests passed!")
        return True
    else:
        print("❌ MCP server test failed")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run local test
        success = test_server_locally()
        sys.exit(0 if success else 1)
    else:
        # Run as MCP server
        server = SimpleMCPServer()
        try:
            asyncio.run(server.run())
        except KeyboardInterrupt:
            logger.info("Server stopped")