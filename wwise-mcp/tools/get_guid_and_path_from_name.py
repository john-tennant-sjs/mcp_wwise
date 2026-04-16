"""
wwise_get_guid_and_path_from_name — exact name lookup via ak.wwise.core.object.get
Returns all objects whose name exactly matches, with their GUID and path.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.get"
TOOL_NAME = "wwise_get_guid_and_path_from_name"


def wwise_get_guid_and_path_from_name(
    name: str,
    dry_run: bool = False,
) -> dict:
    """
    Look up all Wwise objects whose name exactly matches the given string.

    Returns every match with its GUID (id), path, name, and type — useful when
    you need to resolve a human-readable name before calling other tools.

    Args:
        name:    Exact object name to search for (case-sensitive).
        dry_run: If True, skip WAAPI and return the contract mock response.

    Returns:
        {"success": bool, "data": [{"id": ..., "path": ..., "name": ..., "type": ...}, ...], "error": str|None}
        data is an empty list when no matches are found (success stays True).
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    # PRE-CHECK
    if not name or not isinstance(name, str):
        err = "name must be a non-empty string."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    # Escape double-quotes inside the name before embedding in WAQL
    escaped = name.replace('"', '\\"')
    waql = f'$ where name = "{escaped}"'

    # EXECUTE
    try:
        with connect() as client:
            result = client.call(
                WAAPI_URI,
                {"waql": waql, "options": {"return": ["id", "path", "name", "type"]}},
            )
    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    if result is None:
        err = "WAAPI returned None."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["execute"] = True

    objects = result.get("return", [])
    # Filter to exact name matches only (WAQL 'where name =' is already exact, but guard anyway)
    matches = [o for o in objects if o.get("name") == name]
    checks["post_check"] = isinstance(matches, list)

    response = {
        "success": True,
        "data": matches,
        "error": None,
    }

    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok

    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_guid_and_path_from_name)
