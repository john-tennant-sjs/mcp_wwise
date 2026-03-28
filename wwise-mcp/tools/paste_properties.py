"""
wwise_paste_properties — ak.wwise.core.object.pasteProperties
Paste properties from one object to one or more target objects.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.pasteProperties"
TOOL_NAME = "wwise_paste_properties"

VALID_PASTE_MODES = {"replaceEntire", "mergeValues", "mergeAndOverwrite"}


def wwise_paste_properties(
    source: str,
    targets: list[str],
    paste_mode: str = "replaceEntire",
    inclusion: list[str] | None = None,
    exclusion: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Paste properties from a source object to one or more target objects.

    Args:
        source:     Path or GUID of the source object.
        targets:    List of paths or GUIDs of target objects.
        paste_mode: "replaceEntire", "mergeValues", or "mergeAndOverwrite".
        inclusion:  Property names to include (omit for all).
        exclusion:  Property names to exclude.
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not source or not source.strip():
        err = "source must be a non-empty string."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if not targets:
        err = "targets must be a non-empty list."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if paste_mode not in VALID_PASTE_MODES:
        err = f"Invalid paste_mode '{paste_mode}'. Must be one of {sorted(VALID_PASTE_MODES)}."
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
            if not object_exists(client, source):
                err = f"Source object does not exist: {source}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            args: dict = {
                "source": source,
                "targets": targets,
                "pasteMode": paste_mode,
            }
            if inclusion:
                args["inclusion"] = inclusion
            if exclusion:
                args["exclusion"] = exclusion

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "object.pasteProperties returned None."
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
    mcp.tool()(wwise_paste_properties)
