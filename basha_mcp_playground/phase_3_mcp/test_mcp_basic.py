#!/usr/bin/env python3
"""
Phase 3: Basic MCP Server Test
Goal: Create simplest possible MCP server with one tool
Test: Tool returns "Hello from MCP"
"""

import json
import sys
from typing import Dict, Any

class SimpleMCPServer:
    """Minimal MCP server implementation"""
    
    def __init__(self):
        self.tools = {
            "test_tool": {
                "description": "A simple test tool that returns a greeting",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "test-mcp-server",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "tools": {"listChanged": False}
                }
            }
        }
    
    def handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": name,
                        "description": info["description"],
                        "inputSchema": info["parameters"]
                    }
                    for name, info in self.tools.items()
                ]
            }
        }
    
    def handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        tool_name = request["params"]["name"]
        
        if tool_name == "test_tool":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "Hello from MCP! 🎉"
                        }
                    ]
                }
            }
        
        # Tool not found
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32601,
                "message": f"Tool not found: {tool_name}"
            }
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route requests to appropriate handlers"""
        method = request.get("method")
        
        handlers = {
            "initialize": self.handle_initialize,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tool_call
        }
        
        handler = handlers.get(method)
        if handler:
            return handler(request)
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
    
    def run(self):
        """Run the MCP server"""
        print("=== Phase 3: Basic MCP Server Test ===\n", file=sys.stderr)
        print("Server starting...", file=sys.stderr)
        
        # Simple test mode - simulate a tool call
        if "--test" in sys.argv:
            print("Running in test mode\n", file=sys.stderr)
            
            # Test initialize
            init_request = {"jsonrpc": "2.0", "method": "initialize", "id": 1}
            init_response = self.handle_request(init_request)
            print(f"Initialize response: {json.dumps(init_response, indent=2)}\n", file=sys.stderr)
            
            # Test tools list
            list_request = {"jsonrpc": "2.0", "method": "tools/list", "id": 2}
            list_response = self.handle_request(list_request)
            print(f"Tools list: {json.dumps(list_response, indent=2)}\n", file=sys.stderr)
            
            # Test tool call
            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 3,
                "params": {"name": "test_tool", "arguments": {}}
            }
            call_response = self.handle_request(call_request)
            print(f"Tool call response: {json.dumps(call_response, indent=2)}\n", file=sys.stderr)
            
            result = call_response.get("result", {}).get("content", [{}])[0].get("text", "")
            if "Hello from MCP" in result:
                print("✅ Phase 3 PASSED: MCP server responds correctly!", file=sys.stderr)
                return True
            else:
                print("❌ Phase 3 FAILED: Unexpected response", file=sys.stderr)
                return False
        
        # Normal server mode - read from stdin
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    server = SimpleMCPServer()
    if "--test" in sys.argv:
        success = server.run()
        sys.exit(0 if success else 1)
    else:
        server.run()