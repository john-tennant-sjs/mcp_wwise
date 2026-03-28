"""
wwise_ui_get_selected_objects — ak.wwise.ui.getSelectedObjects
Retrieve the list of objects currently selected in the Wwise UI.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.ui.getSelectedObjects"
TOOL_NAME = "wwise_ui_get_selected_objects"

DEFAULT_RETURN = ["id", "name", "path", "type"]


def wwise_ui_get_selected_objects(
    return_props: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Return the objects currently selected in the Wwise authoring UI.

    Args:
        return_props: Object properties to return (default: id, name, path, type).
        dry_run:      If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    props = return_props or DEFAULT_RETURN

    try:
        with connect() as client:
            result = client.call(WAAPI_URI, {}, {"return": props})
            if result is None:
                err = "ui.getSelectedObjects returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            objects = result.get("objects", [])
            checks["post_check"] = isinstance(objects, list)

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"objects": objects} if checks["post_check"] else None,
        "error": None if checks["post_check"] else "objects key missing",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_ui_get_selected_objects)
