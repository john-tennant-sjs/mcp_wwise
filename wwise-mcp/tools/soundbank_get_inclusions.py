"""
wwise_soundbank_get_inclusions — ak.wwise.core.soundbank.getInclusions
List objects included in a soundbank.
"""

from __future__ import annotations
from .client import connect, object_exists, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.soundbank.getInclusions"
TOOL_NAME = "wwise_soundbank_get_inclusions"


def wwise_soundbank_get_inclusions(
    soundbank: str,
    dry_run: bool = False,
) -> dict:
    """
    Return the list of objects explicitly included in a soundbank.

    Args:
        soundbank: Path or GUID of the SoundBank object.
        dry_run:   If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not soundbank or not soundbank.strip():
        err = "soundbank must be a non-empty string."
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
            if not object_exists(client, soundbank):
                err = f"Object does not exist: {soundbank}"
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            result = client.call(WAAPI_URI, {"soundbank": soundbank})
            if result is None:
                err = "soundbank.getInclusions returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            inclusions = result.get("inclusions", [])
            checks["post_check"] = isinstance(inclusions, list)

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"inclusions": inclusions} if checks["post_check"] else None,
        "error": None if checks["post_check"] else "inclusions key missing",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_soundbank_get_inclusions)
