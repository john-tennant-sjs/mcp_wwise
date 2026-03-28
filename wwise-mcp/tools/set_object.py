"""
wwise_set_object — ak.wwise.core.object.set
Set multiple properties on one or more Wwise objects in a single call.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.set"
TOOL_NAME = "wwise_set_object"


def wwise_set_object(objects: list[dict], dry_run: bool = False) -> dict:
    """
    Set multiple properties on Wwise objects in one batch call.

    Each item in `objects` must have an "object" key (path or GUID) plus
    property keys prefixed with "@" (e.g. "@Volume", "@Pitch").

    Args:
        objects:  List of dicts, each with "object" + "@property": value pairs.
        dry_run:  If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not objects:
        err = "objects list is empty."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    for item in objects:
        if "object" not in item:
            err = f"Item missing 'object' key: {item}"
            write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
            return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock = {**mock, "data": {"updated": len(objects)}}
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    try:
        with connect() as client:
            for item in objects:
                if not object_exists(client, item["object"]):
                    err = f"Object does not exist: {item['object']}"
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {"objects": objects})
            if result is None:
                err = "object.set returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            first = objects[0]
            prop_keys = [k for k in first if k.startswith("@")]
            if prop_keys:
                ref = first["object"]
                verify = client.call(
                    "ak.wwise.core.object.get",
                    {"from": {"path": [ref]} if ref.startswith("\\") else {"id": [ref]},
                     "options": {"return": [prop_keys[0]]}},
                )
                checks["post_check"] = bool(verify and verify.get("return"))
            else:
                checks["post_check"] = True

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": {"updated": len(objects)},
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_object)
