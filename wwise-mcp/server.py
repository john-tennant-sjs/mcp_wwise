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
        "Natural-language or UI field labels are not WAAPI strings. Before wwise_set_property or "
        "wwise_set_reference: use wwise_get_object to read the target's \"type\", then call "
        "wwise_resolve_waapi_field with that object_type and the user's label to obtain waapi_name, "
        "kind (property or reference), and suggested_tool; then call the setter once with the returned name. "
        "For exploration or when the label is already a known WAAPI identifier, wwise_get_property_names "
        "still lists every valid name for the type (use the bundled reference snapshot "
        "wwise-mcp/reference/wobject_waapi_names_2023_1_17.json if WAAPI is offline).\n\n"
        "Use wwise_set_reference only for reference-type fields; use wwise_set_property for scalar/list "
        "properties. Output bus routing on Sound uses the reference name \"OutputBus\" (see reference bundle notes). "
        "OutputBus references only work against a Bus type, not AuxBus."
    ),
)

for _tool_module in ALL_TOOLS:
    _tool_module.register(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
