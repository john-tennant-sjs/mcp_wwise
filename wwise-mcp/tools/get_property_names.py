"""
wwise_get_property_names — ak.wwise.core.object.getPropertyNames
List WAAPI property/reference name strings for a Wwise object type (via classId).
"""

from __future__ import annotations
from .client import (
    connect,
    write_phase2_log,
    validate_response,
    get_mock_response,
    resolve_class_id_for_type,
)

WAAPI_URI = "ak.wwise.core.object.getPropertyNames"
TOOL_NAME = "wwise_get_property_names"


def wwise_get_property_names(
    object_type: str | None = None,
    class_id: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Return the list of property/reference names WAAPI accepts for a given type.

    Args:
        object_type: Wwise type string from wwise_get_object (e.g. \"Sound\").
                     Ignored if class_id is set.
        class_id:    Numeric classId from ak.wwise.core.object.getTypes; overrides object_type.
        dry_run:     If True, skip WAAPI and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if class_id is None and (not object_type or not str(object_type).strip()):
        err = "Provide object_type (e.g. from wwise_get_object) or class_id."
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
            cid = class_id
            if cid is None:
                cid = resolve_class_id_for_type(client, object_type.strip())  # type: ignore[union-attr]
                if cid is None:
                    err = f"Unknown Wwise type {object_type!r} (no matching classId from getTypes)."
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {"classId": cid})
            if result is None:
                err = "getPropertyNames returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            names = result.get("return")
            if not isinstance(names, list):
                err = "getPropertyNames response missing return list."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = all(isinstance(n, str) for n in names)

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    resolved_type = object_type.strip() if object_type else None
    data = {"class_id": cid, "object_type": resolved_type, "names": names if checks["post_check"] else []}
    response = {
        "success": checks["post_check"],
        "data": data if checks["post_check"] else None,
        "error": None if checks["post_check"] else "unexpected name types in return",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_property_names)
