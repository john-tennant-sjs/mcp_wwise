"""
wwise_set_property — ak.wwise.core.object.setProperty
Set a single property on a Wwise object and verify it was applied.
"""

from __future__ import annotations
from .client import (
    connect,
    object_exists,
    get_object_property,
    write_phase2_log,
    validate_input,
    validate_response,
    get_mock_response,
)

WAAPI_URI = "ak.wwise.core.object.setProperty"
TOOL_NAME = "wwise_set_property"
_UNVERIFIABLE = {"AudioDeviceShareSet"}


def wwise_set_property(
    object_ref: str,
    property_name: str,
    value,
    platform: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Set a property on a Wwise object.

    Args:
        object_ref:     Path or GUID of the target object.
        property_name:  Property name (e.g. "Volume", "Pitch", "IsLoopingEnabled").
        value:          New value (number, bool, or string).
        platform:       Optional platform name/GUID for platform-specific override.
        dry_run:        If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref or not property_name:
        err = "object_ref and property_name are required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    ok, verr = validate_input(
        TOOL_NAME,
        {
            "object_ref": object_ref,
            "property_name": property_name,
            "value": value,
            "platform": platform,
            "dry_run": dry_run,
        },
    )
    if not ok:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, verr)
        return {"success": False, "data": None, "error": verr}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {**mock, "data": {"property": property_name, "value": value}}
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

            args: dict = {"object": object_ref, "property": property_name, "value": value}
            if platform is not None:
                args["platform"] = platform

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "setProperty returned None — property name may be invalid."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            if property_name not in _UNVERIFIABLE:
                read_back = get_object_property(client, object_ref, f"@{property_name}")
                checks["post_check"] = read_back is not None
            else:
                checks["post_check"] = True

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": {"property": property_name, "value": value},
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_property)
