#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("simple-test")

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location."""
    return f"Forecast for {latitude}, {longitude}"

if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport='stdio')