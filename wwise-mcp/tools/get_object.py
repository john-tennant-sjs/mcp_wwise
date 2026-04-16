"""
wwise_get_object — ak.wwise.core.object.get
Query Wwise objects by path or WAQL and return requested properties.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.get"
TOOL_NAME = "wwise_get_object"
DEFAULT_RETURN = ["id", "name", "type", "path"]


def wwise_get_object(
    from_path: list[str] | None = None,
    from_id: list[str] | None = None,
    waql: str | None = None,
    return_props: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Query Wwise objects by path, GUID list, or WAQL expression.

    PREFER DEDICATED HELPERS over this tool for common lookups:
    - To find objects by name → use wwise_get_guid_and_path_from_name (exact match,
      returns all GUIDs + paths, no WAQL authoring required).
    - To resolve a GUID to a path → use wwise_get_path_from_guid.
    Reserve wwise_get_object for bulk queries, type-filtered scans, or cases where
    you already know the exact path or need custom return_props.

    Args:
        from_path:    List of object paths (e.g. ["\\\\Actor-Mixer Hierarchy"]).
        from_id:      List of GUIDs.
        waql:         WAQL query string (e.g. "$ where type = \\"Sound\\"").
        return_props: Properties to return. Defaults to [id, name, type, path].
        dry_run:      If True, skip WAAPI call and return mock response.

    Returns:
        {"success": bool, "data": [objects...], "error": str|None}
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    # PRE-CHECK
    if not any([from_path, from_id, waql]):
        err = "Must provide from_path, from_id, or waql."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    props = return_props or DEFAULT_RETURN

    # EXECUTE
    try:
        with connect() as client:
            if waql:
                # waql is a top-level argument; the deprecated `from.search` field
                # is a free-text token search, not a WAQL expression.
                result = client.call(WAAPI_URI, {"waql": waql, "options": {"return": props}})
            elif from_path:
                result = client.call(WAAPI_URI, {"from": {"path": from_path}, "options": {"return": props}})
            else:
                result = client.call(WAAPI_URI, {"from": {"id": from_id}, "options": {"return": props}})
    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    if result is None:
        err = "WAAPI returned None (check object path/WAQL)."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["execute"] = True

    objects = result.get("return", [])
    checks["post_check"] = isinstance(objects, list)

    response = {"success": checks["post_check"], "data": objects if checks["post_check"] else None,
                "error": None if checks["post_check"] else "unexpected response shape"}

    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok

    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_object)
