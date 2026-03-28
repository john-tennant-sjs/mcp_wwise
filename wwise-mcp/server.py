"""
Wwise MCP Server — entry point.
Transport: stdio (local only).
"""

from fastmcp import FastMCP
from tools import ALL_TOOLS

mcp = FastMCP(
    name="wwise-mcp",
    instructions=(
        "MCP server for Audiokinetic Wwise. "
        "Provides tools to interact with a running Wwise instance via WAAPI on port 9000."
    ),
)

for _tool_module in ALL_TOOLS:
    _tool_module.register(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
