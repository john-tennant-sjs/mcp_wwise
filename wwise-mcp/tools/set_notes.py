"""
wwise_set_notes — ak.wwise.core.object.setNotes
Set the Notes field on a Wwise object.
"""

from __future__ import annotations
from .client import connect, object_exists, get_object_property, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.setNotes"
TOOL_NAME = "wwise_set_notes"


def wwise_set_notes(object_ref: str, notes: str, dry_run: bool = False) -> dict:
    """
    Set the notes/comments on a Wwise object.

    Args:
        object_ref: Path or GUID of the target object.
        notes:      The notes string to set.
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref:
        err = "object_ref is required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {**mock, "data": {"notes": notes}}
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

            result = client.call(WAAPI_URI, {"object": object_ref, "value": notes})
            if result is None:
                err = "setNotes returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            read_back = get_object_property(client, object_ref, "notes")
            checks["post_check"] = read_back == notes

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": {"notes": notes},
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_notes)
