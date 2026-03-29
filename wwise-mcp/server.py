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
        "Provides tools to interact with a running Wwise instance via WAAPI on port 9000.\n\n"
        "Before wwise_set_property or wwise_set_reference: use wwise_get_object to read the target's "
        "\"type\", then call wwise_get_property_names with that type (or class_id) to obtain the exact "
        "WAAPI strings for that object type. If WAAPI is unavailable, consult the bundled reference "
        "snapshot under wwise-mcp/reference/wobject_waapi_names_2023_1_17.json. "
        "Do not guess alternate casings, camelCase variants, or UI labels for property or reference names.\n\n"
        "Use wwise_set_reference only for reference-type fields; use wwise_set_property for scalar/list "
        "properties. Output bus routing on Sound uses the reference name \"OutputBus\" (see reference bundle notes)."
        "OutputBus references only work against a Bus type, not AuxBus"
    ),
)

for _tool_module in ALL_TOOLS:
    _tool_module.register(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
