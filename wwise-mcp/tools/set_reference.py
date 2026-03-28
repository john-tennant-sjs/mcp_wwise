"""
wwise_set_reference — ak.wwise.core.object.setReference
Set a reference-type property on a Wwise object.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.setReference"
TOOL_NAME = "wwise_set_reference"


def wwise_set_reference(
    object_ref: str,
    reference: str,
    value: str,
    platform: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Set a reference-type property on a Wwise object.

    Args:
        object_ref: Path or GUID of the object to modify.
        reference:  Reference name (e.g. "Conversion"). See Wwise object docs.
        value:      Path or GUID of the target object (or "" to clear).
        platform:   Optional platform name/GUID.
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref or not reference:
        err = "object_ref and reference are required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {**mock, "data": {"reference": reference, "value": value}}
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
            if value and not object_exists(client, value):
                err = f"Referenced object does not exist: {value}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            args: dict = {"object": object_ref, "reference": reference, "value": value}
            if platform is not None:
                args["platform"] = platform

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "setReference returned None — reference name may be invalid."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            verify = client.call(
                "ak.wwise.core.object.get",
                {"from": {"path": [object_ref]} if object_ref.startswith("\\") else {"id": [object_ref]},
                 "options": {"return": [reference]}},
            )
            checks["post_check"] = bool(verify and verify.get("return"))

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": {"reference": reference, "value": value},
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_reference)
