"""
wwise_create_object — ak.wwise.core.object.create
Create a new Wwise object under a specified parent.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.create"
TOOL_NAME = "wwise_create_object"


def wwise_create_object(
    parent: str,
    object_type: str,
    name: str,
    on_name_conflict: str = "fail",
    notes: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Create a new Wwise object.

    Args:
        parent:           Path or GUID of the parent object.
        object_type:      Wwise type string (e.g. "Sound", "ActorMixer", "Event").
        name:             Name of the new object.
        on_name_conflict: "fail" | "rename" | "replace" | "merge". Default: "fail".
        notes:            Optional notes string.
        dry_run:          If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not parent or not object_type or not name:
        err = "parent, object_type, and name are required."
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
            if not object_exists(client, parent):
                err = f"Parent does not exist: {parent}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            args: dict = {"parent": parent, "type": object_type, "name": name,
                          "onNameConflict": on_name_conflict}
            if notes is not None:
                args["notes"] = notes

            result = client.call(WAAPI_URI, args)
            if not result or not result.get("id"):
                err = "Create returned no id — type may be invalid or name conflict."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            verify = client.call(
                "ak.wwise.core.object.get",
                {"from": {"id": [result["id"]]}, "options": {"return": ["id", "name", "type"]}},
            )
            checks["post_check"] = bool(verify and verify.get("return"))

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
    mcp.tool()(wwise_create_object)
