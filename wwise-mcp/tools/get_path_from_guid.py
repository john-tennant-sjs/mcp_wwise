"""
wwise_get_path_from_guid — GUID-to-path lookup via ak.wwise.core.object.get
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.get"
TOOL_NAME = "wwise_get_path_from_guid"


def wwise_get_path_from_guid(
    guid: str,
    dry_run: bool = False,
) -> dict:
    """
    Resolve a Wwise object GUID to its full project path.

    Args:
        guid:    Object GUID in the form {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}.
        dry_run: If True, skip WAAPI and return the contract mock response.

    Returns:
        {"success": bool, "data": {"guid": ..., "path": ...} | None, "error": str|None}
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    # PRE-CHECK
    if not guid or not isinstance(guid, str):
        err = "guid must be a non-empty string."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    # EXECUTE
    try:
        with connect() as client:
            result = client.call(
                WAAPI_URI,
                {"from": {"id": [guid]}, "options": {"return": ["id", "path"]}},
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
    if not objects:
        err = f"No object found for GUID: {guid}"
        checks["post_check"] = False
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    obj = objects[0]
    checks["post_check"] = "path" in obj

    if not checks["post_check"]:
        err = "WAAPI response missing 'path' field."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    response = {
        "success": True,
        "data": {"guid": obj.get("id", guid), "path": obj["path"]},
        "error": None,
    }

    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok

    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_path_from_guid)
