"""
wwise_ui_commands_execute — ak.wwise.ui.commands.execute
Execute a Wwise UI command by its command ID.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.ui.commands.execute"
TOOL_NAME = "wwise_ui_commands_execute"


def wwise_ui_commands_execute(
    command: str,
    objects: list[str] | None = None,
    platforms: list[str] | None = None,
    value: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Execute a Wwise UI command.

    Args:
        command:   Command ID string (e.g., "FindInProjectExplorerSyncGroup1").
        objects:   List of object paths or GUIDs to pass to the command (optional).
        platforms: List of platform names (optional).
        value:     String value argument for the command (optional).
        dry_run:   If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not command or not command.strip():
        err = "command must be a non-empty string."
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
            args: dict = {"command": command}
            if objects:
                args["objects"] = objects
            if platforms:
                args["platforms"] = platforms
            if value is not None:
                args["value"] = value

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "ui.commands.execute returned None."
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
    mcp.tool()(wwise_ui_commands_execute)
