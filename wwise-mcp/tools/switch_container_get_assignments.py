"""
wwise_switch_container_get_assignments — ak.wwise.core.switchContainer.getAssignments
List all child-to-state/switch assignments for a Switch Container.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.switchContainer.getAssignments"
TOOL_NAME = "wwise_switch_container_get_assignments"


def wwise_switch_container_get_assignments(
    object_ref: str,
    dry_run: bool = False,
) -> dict:
    """
    Return all child-to-state/switch assignments for a Switch Container.

    Args:
        object_ref: Path or GUID of the Switch Container.
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref or not object_ref.strip():
        err = "object_ref must be a non-empty string."
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
                err = f"Object does not exist: {object_ref}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {"id": object_ref})
            if result is None:
                err = "switchContainer.getAssignments returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            assignments = result.get("return", [])
            checks["post_check"] = isinstance(assignments, list)

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"assignments": assignments} if checks["post_check"] else None,
        "error": None if checks["post_check"] else "return key missing",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_switch_container_get_assignments)
