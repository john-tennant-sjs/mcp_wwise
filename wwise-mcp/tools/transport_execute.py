"""
wwise_transport_execute — ak.wwise.core.transport.executeAction
Play, stop, pause, resume, or seek. Creates/destroys transport internally.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.transport.executeAction"
TOOL_NAME = "wwise_transport_execute"
VALID_ACTIONS = {"play", "stop", "pause", "resume", "playStop", "seek"}


def wwise_transport_execute(
    object_ref: str,
    action: str = "play",
    seek_position: float | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Audition a Wwise object. Creates a transport, executes the action, destroys the transport.

    Args:
        object_ref:    Path or GUID of the object to audition.
        action:        One of "play", "stop", "pause", "resume", "playStop", "seek".
        seek_position: Position in ms (required when action == "seek").
        dry_run:       If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if action not in VALID_ACTIONS:
        err = f"Invalid action '{action}'. Must be one of {sorted(VALID_ACTIONS)}."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {**mock, "data": {"action": action, "transport": 0}}
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

            t = client.call("ak.wwise.core.transport.create", {"object": object_ref})
            if not t or t.get("transport") is None:
                err = "Could not create transport."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            transport_id = t["transport"]

            exec_args: dict = {"transport": transport_id, "action": action}
            if action == "seek" and seek_position is not None:
                exec_args["seekPosition"] = seek_position

            result = client.call(WAAPI_URI, exec_args)
            if result is None:
                err = "executeAction returned None."
                client.call("ak.wwise.core.transport.destroy", {"transport": transport_id})
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            state = client.call("ak.wwise.core.transport.getState", {"transport": transport_id})
            checks["post_check"] = bool(state and "state" in state)

            if action not in {"stop", "pause"}:
                client.call(WAAPI_URI, {"transport": transport_id, "action": "stop"})
            client.call("ak.wwise.core.transport.destroy", {"transport": transport_id})

    except Exception as e:
        if transport_id is not None:
            try:
                with connect() as c:
                    c.call("ak.wwise.core.transport.destroy", {"transport": transport_id})
            except Exception:
                pass
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"],
                "data": {"action": action, "transport": transport_id} if checks["post_check"] else None,
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_transport_execute)
