"""
wwise_soundbank_set_inclusions — ak.wwise.core.soundbank.setInclusions
Modify the inclusion list of a soundbank.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.soundbank.setInclusions"
TOOL_NAME = "wwise_soundbank_set_inclusions"

VALID_OPERATIONS = {"add", "remove", "replace"}


def wwise_soundbank_set_inclusions(
    soundbank: str,
    inclusions: list[dict],
    operation: str = "add",
    dry_run: bool = False,
) -> dict:
    """
    Add, remove, or replace inclusions in a soundbank.

    Each inclusion dict must have:
      - "object": Path or GUID of the object to include.
      - "filter": List of inclusion filters, e.g. ["events", "structures", "media"].

    Args:
        soundbank:  Path or GUID of the SoundBank object.
        inclusions: List of inclusion dicts.
        operation:  "add", "remove", or "replace". Default: "add".
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not soundbank or not soundbank.strip():
        err = "soundbank must be a non-empty string."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if not inclusions:
        err = "inclusions list must not be empty."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if operation not in VALID_OPERATIONS:
        err = f"Invalid operation '{operation}'. Must be one of {sorted(VALID_OPERATIONS)}."
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
            if not object_exists(client, soundbank):
                err = f"Object does not exist: {soundbank}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {
                "soundbank": soundbank,
                "operation": operation,
                "inclusions": inclusions,
            })
            if result is None:
                err = "soundbank.setInclusions returned None."
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
    mcp.tool()(wwise_soundbank_set_inclusions)
