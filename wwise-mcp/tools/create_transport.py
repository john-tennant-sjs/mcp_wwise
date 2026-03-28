"""
wwise_create_transport — ak.wwise.core.transport.create
Create a transport object for auditioning a Wwise object.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.transport.create"
TOOL_NAME = "wwise_create_transport"


def wwise_create_transport(
    object_ref: str,
    game_object_id: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Create a transport for auditioning a Wwise object.

    Args:
        object_ref:      Path or GUID of the object to audition.
        game_object_id:  Optional game object ID for playback context.
        dry_run:         If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref:
        err = "object_ref is required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    transport_id: int | None = None
    try:
        with connect() as client:
            if not object_exists(client, object_ref):
                err = f"Object does not exist: {object_ref}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            args: dict = {"object": object_ref}
            if game_object_id is not None:
                args["gameObject"] = game_object_id

            result = client.call(WAAPI_URI, args)
            if result is None or result.get("transport") is None:
                err = "transport.create returned None or no transport id."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            transport_id = result["transport"]

            state = client.call("ak.wwise.core.transport.getState", {"transport": transport_id})
            checks["post_check"] = bool(state and "state" in state)

            client.call("ak.wwise.core.transport.destroy", {"transport": transport_id})

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": {"transport": transport_id} if checks["post_check"] else None,
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_create_transport)
