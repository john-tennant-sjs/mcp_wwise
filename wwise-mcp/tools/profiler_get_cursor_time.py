"""
wwise_profiler_get_cursor_time — ak.wwise.core.profiler.getCursorTime
Get the current time position of the profiler cursor.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.profiler.getCursorTime"
TOOL_NAME = "wwise_profiler_get_cursor_time"

VALID_CURSORS = {"capture", "user"}


def wwise_profiler_get_cursor_time(
    cursor: str = "capture",
    dry_run: bool = False,
) -> dict:
    """
    Get the time position (in ms) of the specified profiler cursor.

    Args:
        cursor:  "capture" or "user". Default: "capture".
        dry_run: If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if cursor not in VALID_CURSORS:
        err = f"Invalid cursor '{cursor}'. Must be one of {sorted(VALID_CURSORS)}."
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
            result = client.call(WAAPI_URI, {"cursor": cursor})
            if result is None:
                err = "profiler.getCursorTime returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            time_ms = result.get("return")
            checks["post_check"] = time_ms is not None

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"time": time_ms, "cursor": cursor} if checks["post_check"] else None,
        "error": None if checks["post_check"] else "time not returned",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_profiler_get_cursor_time)
