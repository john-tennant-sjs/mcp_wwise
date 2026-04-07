"""
wwise_set_object — ak.wwise.core.object.set
Set multiple properties on one or more Wwise objects in a single call.
"""

from __future__ import annotations
from copy import deepcopy
from difflib import get_close_matches

from .client import (
    connect,
    object_exists,
    resolve_class_id_for_type,
    write_phase2_log,
    validate_input,
    validate_response,
    get_mock_response,
)

WAAPI_URI = "ak.wwise.core.object.set"
TOOL_NAME = "wwise_set_object"
_COMMON_AT_KEY_FIXES = {
    "PropertyName": "@PropertyName",
    "ControlInput": "@ControlInput",
    "Curve": "@Curve",
    "RTPC": "@RTPC",
    "Effects": "@Effects",
}
_COMMON_CASE_FIXES = {"Points": "points"}
_ALLOWED_OBJECT_ITEM_KEYS = {
    "object",
    "name",
    "children",
    "platform",
    "notes",
    "listMode",
    "onNameConflict",
    "import",
}


def _normalize_object_payload(items: list[dict], autofix: bool) -> tuple[list[dict], list[str], list[str]]:
    normalized = deepcopy(items)
    applied: list[str] = []
    problems: list[str] = []

    def walk(node, path: str):
        if isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
            return
        if not isinstance(node, dict):
            return

        original_keys = list(node.keys())
        for key in original_keys:
            value = node[key]
            current_path = f"{path}.{key}"

            if key in _COMMON_AT_KEY_FIXES:
                fixed = _COMMON_AT_KEY_FIXES[key]
                if autofix:
                    node[fixed] = node.pop(key)
                    key = fixed
                    value = node[key]
                    current_path = f"{path}.{key}"
                    applied.append(f"{path}: replaced {fixed[1:]} with {fixed}")
                else:
                    problems.append(f"{current_path}: use {_COMMON_AT_KEY_FIXES[key]!r} in object.set payloads.")

            if key in _COMMON_CASE_FIXES:
                fixed = _COMMON_CASE_FIXES[key]
                if autofix:
                    node[fixed] = node.pop(key)
                    key = fixed
                    value = node[key]
                    current_path = f"{path}.{key}"
                    applied.append(f"{path}: replaced {key} with {fixed}")
                else:
                    problems.append(f"{current_path}: curve points key should be 'points' (lowercase).")

            walk(value, current_path)

    for idx, item in enumerate(normalized):
        walk(item, f"objects[{idx}]")

    return normalized, applied, problems


def _collect_object_level_issues(items: list[dict], strict: bool) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            problems.append(f"objects[{idx}] must be an object.")
            continue
        for key in item.keys():
            if key.startswith("@"):
                continue
            if key not in _ALLOWED_OBJECT_ITEM_KEYS:
                msg = (
                    f"objects[{idx}].{key}: unexpected non-@ key for object.set. "
                    "Settable fields should generally be prefixed with '@'."
                )
                if strict:
                    problems.append(msg)
                else:
                    warnings.append(msg)
    return problems, warnings


def wwise_set_object(
    objects: list[dict],
    dry_run: bool = False,
    strict: bool = True,
    autofix: bool = False,
) -> dict:
    """
    Set multiple properties on Wwise objects in one batch call.

    Each item in `objects` must have an "object" key (path or GUID) plus
    property keys prefixed with "@" (e.g. "@Volume", "@Pitch").

    Args:
        objects:  List of dicts, each with "object" + "@property": value pairs.
        dry_run:  If True, skip WAAPI call and return mock response.

    SPECIAL CASE — Assigning effects to buses/sounds:
    Effect slots cannot be set via wwise_set_reference. Instead use wwise_set_object
    with an "@Effects" array. Each element must be an EffectSlot object:

        {
          "object": "<bus-or-sound-guid>",
          "@Effects": [
            {
              "type": "EffectSlot",
              "name": "",
              "@Effect": "<effect-preset-guid>"
            }
          ]
        }

    To assign to a specific slot (0–3), use "name": "0" through "name": "3".
    An empty "name" defaults to slot 0.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}
    normalized_objects, normalizations_applied, payload_issues = _normalize_object_payload(objects or [], autofix)
    object_level_errors, object_level_warnings = _collect_object_level_issues(normalized_objects, strict=strict)

    if payload_issues and strict and not autofix:
        err = "Payload preflight failed: " + " | ".join(payload_issues[:8])
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {
            "success": False,
            "data": None,
            "error": err,
            "suggestion": (
                "Use @-prefixed keys in object.set payloads (for example: @RTPC, @PropertyName, "
                "@ControlInput, @Curve) and use lowercase 'points' inside @Curve."
            ),
        }

    if object_level_errors:
        err = "Payload preflight failed: " + " | ".join(object_level_errors[:8])
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    input_payload = {
        "objects": normalized_objects,
        "dry_run": dry_run,
        "strict": strict,
        "autofix": autofix,
    }
    ok, verr = validate_input(TOOL_NAME, input_payload)
    if not ok:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, verr)
        return {"success": False, "data": None, "error": verr}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        mock_data = {"updated": len(normalized_objects)}
        if normalizations_applied:
            mock_data["normalizations_applied"] = normalizations_applied
        if object_level_warnings:
            mock_data["warnings"] = object_level_warnings
        mock = {**mock, "data": mock_data}
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    try:
        with connect() as client:
            all_prop_names: set[str] = set()
            for item in normalized_objects:
                if not object_exists(client, item["object"]):
                    err = f"Object does not exist: {item['object']}"
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}

                oinfo = client.call(
                    "ak.wwise.core.object.get",
                    {
                        "from": {"path": [item["object"]]} if item["object"].startswith("\\") else {"id": [item["object"]]},
                        "options": {"return": ["type"]},
                    },
                )
                otype = None
                if oinfo and oinfo.get("return"):
                    otype = oinfo["return"][0].get("type")
                if otype:
                    class_id = resolve_class_id_for_type(client, otype)
                    if class_id is not None:
                        pnames = client.call("ak.wwise.core.object.getPropertyNames", {"classId": class_id})
                        names = pnames.get("return") if pnames else None
                        if isinstance(names, list):
                            all_prop_names.update(n for n in names if isinstance(n, str))

                for key in [k for k in item.keys() if k.startswith("@")]:
                    bare = key[1:]
                    if all_prop_names and bare not in all_prop_names and strict:
                        alternatives = get_close_matches(bare, list(all_prop_names), n=4, cutoff=0.45)
                        if alternatives:
                            err = (
                                f"{key!r} does not appear in live getPropertyNames for this object type. "
                                f"Did you mean: {alternatives!r}?"
                            )
                        else:
                            err = f"{key!r} does not appear in live getPropertyNames for this object type."
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {"objects": normalized_objects})
            if result is None:
                err = "object.set returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {
                    "success": False,
                    "data": None,
                    "error": err,
                    "suggestion": (
                        "Common causes: missing @ prefix on settable fields, wrong list/object shape, or wrong "
                        "curve points key casing. Try @RTPC with @PropertyName/@ControlInput and @Curve.points."
                    ),
                }
            checks["execute"] = True

            first = normalized_objects[0]
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

    response_data: dict = {"updated": len(normalized_objects)}
    if normalizations_applied:
        response_data["normalizations_applied"] = normalizations_applied
    if object_level_warnings:
        response_data["warnings"] = object_level_warnings

    response = {
        "success": checks["post_check"],
        "data": response_data,
        "error": None if checks["post_check"] else "post_check failed",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_object)
