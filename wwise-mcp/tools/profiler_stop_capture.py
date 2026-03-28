"""
wwise_profiler_stop_capture — ak.wwise.core.profiler.stopCapture
Stop the current profiler capture session.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.profiler.stopCapture"
TOOL_NAME = "wwise_profiler_stop_capture"


def wwise_profiler_stop_capture(dry_run: bool = False) -> dict:
    """
    Stop the current profiler capture session.

    Args:
        dry_run: If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    try:
        with connect() as client:
            result = client.call(WAAPI_URI)
            if result is None:
                err = "profiler.stopCapture returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            cursor_time = result.get("return")
            checks["post_check"] = cursor_time is not None

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"cursor": cursor_time} if checks["post_check"] else None,
        "error": None if checks["post_check"] else "cursor time not returned",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_profiler_stop_capture)
