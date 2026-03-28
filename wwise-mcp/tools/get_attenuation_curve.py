"""
wwise_get_attenuation_curve — ak.wwise.core.object.getAttenuationCurve
Retrieve attenuation curve data for an Attenuation object.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.object.getAttenuationCurve"
TOOL_NAME = "wwise_get_attenuation_curve"

VALID_CURVE_TYPES = {
    "VolumeDryUsage", "VolumeWetGameUsage", "VolumeWetUserUsage",
    "LowPassFilterUsage", "HighPassFilterUsage", "SpreadUsage", "FocusUsage",
}


def wwise_get_attenuation_curve(
    object_ref: str,
    curve_type: str,
    platform: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Retrieve the attenuation curve points for a given curve type on an Attenuation object.

    Args:
        object_ref:  Path or GUID of the Attenuation object.
        curve_type:  Curve to retrieve. One of: VolumeDryUsage, VolumeWetGameUsage,
                     VolumeWetUserUsage, LowPassFilterUsage, HighPassFilterUsage,
                     SpreadUsage, FocusUsage.
        platform:    Platform name (omit for the current/default platform).
        dry_run:     If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not object_ref or not object_ref.strip():
        err = "object_ref must be a non-empty string."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if curve_type not in VALID_CURVE_TYPES:
        err = f"Invalid curve_type '{curve_type}'. Must be one of {sorted(VALID_CURVE_TYPES)}."
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
            if not object_exists(client, object_ref):
                err = f"Object does not exist: {object_ref}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            args: dict = {"object": object_ref, "curveType": curve_type}
            if platform:
                args["platform"] = platform

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "object.getAttenuationCurve returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = "points" in result and "use" in result

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": result if checks["post_check"] else None,
        "error": None if checks["post_check"] else "points/use keys missing",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_attenuation_curve)
