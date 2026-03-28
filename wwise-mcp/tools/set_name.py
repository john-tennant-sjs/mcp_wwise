"""
wwise_set_name — ak.wwise.core.object.setName
Rename a Wwise object.
"""

from __future__ import annotations
from .client import connect, object_exists, get_object_property, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.setName"
TOOL_NAME = "wwise_set_name"


def wwise_set_name(object_ref: str, new_name: str, dry_run: bool = False) -> dict:
    """
    Rename a Wwise object.

    Args:
        object_ref: Path or GUID of the object to rename.
        new_name:   The new name.
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref or not new_name:
        err = "object_ref and new_name are required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {**mock, "data": {"new_name": new_name}}
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    try:
        with connect() as client:
            if not object_exists(client, object_ref):
                err = f"Object does not exist: {object_ref}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {"object": object_ref, "value": new_name})
            if result is None:
                err = "setName returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            actual_name = get_object_property(client, object_ref, "name")
            if actual_name is None and "\\" in object_ref:
                parent_path = "\\".join(object_ref.rstrip("\\").split("\\")[:-1])
                actual_name = get_object_property(client, f"{parent_path}\\{new_name}", "name")
            checks["post_check"] = actual_name == new_name

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": {"new_name": new_name},
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_name)
