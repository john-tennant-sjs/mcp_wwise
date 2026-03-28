"""
wwise_switch_container_add_assignment — ak.wwise.core.switchContainer.addAssignment
Assign a child object to a State or Switch in a Switch Container.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.switchContainer.addAssignment"
TOOL_NAME = "wwise_switch_container_add_assignment"


def wwise_switch_container_add_assignment(
    child: str,
    state_or_switch: str,
    dry_run: bool = False,
) -> dict:
    """
    Assign a Switch Container child to a State or Switch value.

    Args:
        child:          Path or GUID of the child object (must be a direct child of a
                        Switch Container).
        state_or_switch: Path or GUID of the State or Switch to assign to.
        dry_run:        If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not child or not child.strip():
        err = "child must be a non-empty string."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if not state_or_switch or not state_or_switch.strip():
        err = "state_or_switch must be a non-empty string."
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
            result = client.call(WAAPI_URI, {"child": child, "stateOrSwitch": state_or_switch})
            if result is None:
                err = "switchContainer.addAssignment returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = True

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": True, "data": None, "error": None}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_switch_container_add_assignment)
