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
        "CHOOSING THE RIGHT TOOL:\n"
        "- wwise_set_reference: Use when assigning one independent project object to a "
        "named slot on another (e.g. OutputBus, Attenuation, Conversion). The target "
        "has its own GUID and path in the project.\n\n"
        "- wwise_set_object: Use when modifying owned/embedded structure on an object — "
        "especially any property that appears as a list or array of slots in the Wwise "
        "UI (e.g. Effects, RTPC bindings, Aux Sends). These use @PropertyName with "
        "structured child objects, not a flat reference.\n\n"
        "When in doubt: if setReference returns a type-mismatch error, the property "
        "likely requires the object.set array pattern instead.\n\n"
        "For RTPC authoring, prefer wwise_add_rtpc_binding over raw wwise_set_object when possible. "
        "It builds a validated object.set payload with @RTPC, @PropertyName, @ControlInput, and @Curve.points.\n\n"
        "Output bus routing on Sound uses the reference name \"OutputBus\" (see reference bundle notes). "
        "OutputBus references only work against a Bus type, not AuxBus.\n\n"
        "Effects — always assign effects with wwise_set_object (ak.wwise.core.object.set). Do not use "
        "wwise_set_reference for Effect0..Effect3 or other effect-slot references; that path does not work for "
        "assigning effects. Set \"@Effects\" to an array of EffectSlot dicts: each item has \"type\": \"EffectSlot\", "
        "\"name\": \"\", and \"@Effect\" set to the existing Effect preset/shareset GUID as a string (same format as "
        "Wwise object ids). For inline plug-in instances use a nested @Effect object with classId and plug-in "
        "properties (Audiokinetic WAAPI example \"Setting an effect plug-in\"). Prefer the GUID string form for "
        "existing presets; an object-shaped @Effect such as {\"id\": \"...\"} may cause object.set to return None."
    ),
)

for _tool_module in ALL_TOOLS:
    _tool_module.register(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
