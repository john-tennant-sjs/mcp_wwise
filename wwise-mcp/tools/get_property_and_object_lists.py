"""
wwise_get_property_and_object_lists — ak.wwise.core.object.getPropertyAndObjectLists
Enum values and object-list metadata for a property (by object instance or by type + property).
"""

from __future__ import annotations
from .client import (
    connect,
    object_exists,
    write_phase2_log,
    validate_response,
    get_mock_response,
    resolve_class_id_for_type,
)

WAAPI_URI = "ak.wwise.core.object.getPropertyAndObjectLists"
TOOL_NAME = "wwise_get_property_and_object_lists"


def wwise_get_property_and_object_lists(
    property_name: str,
    object_ref: str | None = None,
    object_type: str | None = None,
    class_id: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Return list metadata / possible values for a property.

    Provide either object_ref (concrete object path or GUID) or object_type / class_id.

    Args:
        property_name: WAAPI property name (e.g. \"3DSpatialization\", \"OutputBus\").
        object_ref:    Path or GUID of an object — uses instance-scoped WAAPI args when set.
        object_type:   Wwise type string if object_ref is omitted (e.g. \"Sound\").
        class_id:      Overrides object_type when object_ref is omitted.
        dry_run:       If True, skip WAAPI and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not property_name or not property_name.strip():
        err = "property_name is required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    ref = (object_ref or "").strip()
    otype = (object_type or "").strip() if object_type else ""

    if not ref and class_id is None and not otype:
        err = "Provide object_ref, or object_type, or class_id (with property_name)."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    prop = property_name.strip()

    try:
        with connect() as client:
            if ref:
                if not object_exists(client, ref):
                    err = f"Object does not exist: {ref}"
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}
                args = {"object": ref, "property": prop}
            else:
                cid = class_id
                if cid is None:
                    cid = resolve_class_id_for_type(client, otype)
                    if cid is None:
                        err = f"Unknown Wwise type {otype!r} (no matching classId from getTypes)."
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": None, "error": err}
                args = {"classId": cid, "property": prop}

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = (
                    "getPropertyAndObjectLists returned None — check property name and args; "
                    "use wwise_get_property_names for valid names on this type."
                )
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = "return" in result

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    payload = result.get("return") if checks["post_check"] else None
    data = {
        "property": prop,
        "waapi_args": args,
        "return": payload,
    }
    response = {
        "success": checks["post_check"],
        "data": data if checks["post_check"] else None,
        "error": None if checks["post_check"] else "missing return in response",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_property_and_object_lists)
