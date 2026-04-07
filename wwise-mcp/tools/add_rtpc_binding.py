"""
wwise_add_rtpc_binding — convenience wrapper over ak.wwise.core.object.set
Create an RTPC entry with a curve on an object's @RTPC list.
"""

from __future__ import annotations

from .client import (
    connect,
    get_mock_response,
    object_exists,
    validate_input,
    validate_response,
    write_phase2_log,
)

WAAPI_URI = "ak.wwise.core.object.set"
TOOL_NAME = "wwise_add_rtpc_binding"


def wwise_add_rtpc_binding(
    object_ref: str,
    property_name: str,
    control_input: str,
    points: list[dict],
    rtpc_name: str = "",
    notes: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Add an RTPC binding to an object/list item that owns an @RTPC list.

    Args:
        object_ref: Target object GUID or path (e.g. EffectSlot GUID).
        property_name: Target property name for the RTPC (WAAPI name, e.g. "Bypass").
        control_input: GUID/path of the Game Parameter/ControlInput.
        points: Curve points list with dicts: {"x": number, "y": number, "shape": string}.
        rtpc_name: Optional RTPC object name.
        notes: Optional notes.
        dry_run: Skip WAAPI and return contract mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}
    args = {
        "object_ref": object_ref,
        "property_name": property_name,
        "control_input": control_input,
        "points": points,
        "rtpc_name": rtpc_name,
        "notes": notes,
        "dry_run": dry_run,
    }
    ok, verr = validate_input(TOOL_NAME, args)
    if not ok:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, verr)
        return {"success": False, "data": None, "error": verr}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {
            **mock,
            "data": {"updated": 1, "object_ref": object_ref, "property_name": property_name},
        }
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
            if not object_exists(client, control_input):
                err = f"ControlInput does not exist: {control_input}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            rtpc_row = {
                "type": "RTPC",
                "name": rtpc_name,
                "@PropertyName": property_name,
                "@ControlInput": control_input,
                "@Curve": {
                    "type": "Curve",
                    "points": points,
                },
            }
            if notes is not None:
                rtpc_row["notes"] = notes

            result = client.call(
                WAAPI_URI,
                {"objects": [{"object": object_ref, "@RTPC": [rtpc_row]}]},
            )
            if result is None:
                err = "object.set returned None while creating RTPC."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {
                    "success": False,
                    "data": None,
                    "error": err,
                    "suggestion": (
                        "Ensure target owns an @RTPC list (for example EffectSlot/Sound/Bus contexts) and that "
                        "property_name/control_input are valid WAAPI identifiers."
                    ),
                }
            checks["execute"] = True

            verify = client.call(
                "ak.wwise.core.object.get",
                {
                    "from": {"path": [object_ref]} if object_ref.startswith("\\") else {"id": [object_ref]},
                    "options": {"return": ["@RTPC"]},
                },
            )
            checks["post_check"] = bool(verify and verify.get("return"))
    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"updated": 1, "object_ref": object_ref, "property_name": property_name},
        "error": None if checks["post_check"] else "post_check failed",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_add_rtpc_binding)
