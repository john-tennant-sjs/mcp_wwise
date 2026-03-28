"""
wwise_copy_object — ak.wwise.core.object.copy
Copy a Wwise object to a new parent.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.copy"
TOOL_NAME = "wwise_copy_object"


def wwise_copy_object(
    object_ref: str,
    parent: str,
    on_name_conflict: str = "rename",
    dry_run: bool = False,
) -> dict:
    """
    Copy a Wwise object to a new parent location.

    Args:
        object_ref:       Path or GUID of the object to copy.
        parent:           Path or GUID of the destination parent.
        on_name_conflict: "rename" | "replace" | "fail". Default: "rename".
        dry_run:          If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref or not parent:
        err = "object_ref and parent are required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    try:
        with connect() as client:
            if not object_exists(client, object_ref):
                err = f"Source object does not exist: {object_ref}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            if not object_exists(client, parent):
                err = f"Parent does not exist: {parent}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {
                "object": object_ref, "parent": parent, "onNameConflict": on_name_conflict,
            })
            if not result or not result.get("id"):
                err = "copy returned no id."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = object_exists(client, result["id"])

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": result if checks["post_check"] else None,
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_copy_object)
