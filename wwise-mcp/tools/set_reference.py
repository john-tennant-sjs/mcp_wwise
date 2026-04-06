"""
wwise_set_reference — ak.wwise.core.object.setReference
Set a reference-type property on a Wwise object.
"""

from __future__ import annotations

from .client import (
    connect,
    get_mock_response,
    object_exists,
    resolve_class_id_for_type,
    validate_response,
    write_phase2_log,
)

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
                # Try to give a more specific diagnosis: wrong value type is a common cause.
                value_type: str | None = None
                if value:
                    vinfo = client.call(
                        "ak.wwise.core.object.get",
                        {"from": {"path": [value]} if value.startswith("\\") else {"id": [value]},
                         "options": {"return": ["type"]}},
                    )
                    if vinfo and vinfo.get("return"):
                        value_type = vinfo["return"][0].get("type")

                modifier_type: str | None = None
                reference_in_names: bool | None = None
                try:
                    oref = client.call(
                        "ak.wwise.core.object.get",
                        {
                            "from": {"path": [object_ref]}
                            if object_ref.startswith("\\")
                            else {"id": [object_ref]},
                            "options": {"return": ["type"]},
                        },
                    )
                    if oref and oref.get("return"):
                        modifier_type = oref["return"][0].get("type")
                    if modifier_type:
                        cid = resolve_class_id_for_type(client, modifier_type)
                        if cid is not None:
                            pn = client.call(
                                "ak.wwise.core.object.getPropertyNames", {"classId": cid}
                            )
                            lst = pn.get("return") if pn else []
                            if isinstance(lst, list):
                                reference_in_names = reference in lst
                except Exception:
                    reference_in_names = None

                if reference_in_names is False and modifier_type:
                    err = (
                        f"setReference returned None — reference \"{reference}\" does not appear in "
                        f"getPropertyNames for type \"{modifier_type}\" in this Wwise session, so WAAPI likely "
                        f"does not expose this slot on this object. "
                        f"(The value object's type is \"{value_type or 'unknown'}\".)"
                    )
                    suggestion = (
                        "Trust live wwise_get_property_names over static reference JSON: if Effect0..Effect3 are "
                        "missing for Bus, ak.wwise.core.object.setReference cannot assign bus effects from MCP in "
                        "this build — use the Wwise Authoring UI (bus > Effects tab) or contact Audiokinetic. "
                        "For types that do list Effect0..Effect3, the value must be an Effect object (see Q&A 6315)."
                    )
                elif value_type:
                    err = (
                        f"setReference rejected by WAAPI — the value object is type \"{value_type}\", "
                        f"which is incompatible with reference \"{reference}\" on this object. "
                        f"Use wwise_get_object to find the correct target type."
                    )
                    suggestion = (
                        "Call wwise_get_object with return_props including \"type\", then wwise_get_property_names "
                        "for that type. Use an exact name from the returned list for setReference; for output bus "
                        "routing on Sound the reference is \"OutputBus\" and the value must be a Bus (not AuxBus). "
                        "For effect slots on bus/voice objects (Sound, Bus, AuxBus, Actor-Mixer, random/sequence "
                        "containers, etc.), the reference names are typically \"Effect0\"..\"Effect3\" and the value "
                        "must be an object of type Effect (see reference bundle reference_target_types and "
                        "Audiokinetic Q&A on WAAPI effects). Do not try alternate spellings."
                    )
                else:
                    err = "setReference returned None — reference name is likely invalid or not a reference on this object."
                    suggestion = (
                        "Call wwise_get_object with return_props including \"type\", then wwise_get_property_names "
                        "for that type. Use an exact name from the returned list for setReference; for output bus "
                        "routing on Sound the reference is \"OutputBus\" and the value must be a Bus (not AuxBus). "
                        "For effect slots on bus/voice objects (Sound, Bus, AuxBus, Actor-Mixer, random/sequence "
                        "containers, etc.), the reference names are typically \"Effect0\"..\"Effect3\" and the value "
                        "must be an object of type Effect (see reference bundle reference_target_types and "
                        "Audiokinetic Q&A on WAAPI effects). Do not try alternate spellings."
                    )
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err, "suggestion": suggestion}
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

    response: dict = {"success": checks["post_check"], "data": {"reference": reference, "value": value},
                      "error": None if checks["post_check"] else "post_check failed"}
    if not checks["post_check"]:
        response["suggestion"] = (
            "Verify the reference name with wwise_get_property_names for the object's type; "
            "ensure the target value path/GUID exists and matches the expected reference kind."
        )
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_set_reference)
