"""
wwise_profiler_enable_data — ak.wwise.core.profiler.enableProfilerData
Enable specific profiler data types for capture.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.profiler.enableProfilerData"
TOOL_NAME = "wwise_profiler_enable_data"

VALID_DATA_TYPES = {
    "cpu", "memory", "stream", "voices", "listener", "obstructionOcclusion",
    "markersNotification", "soundbanks", "loadedMedia", "preparedEvents",
    "preparedGameSyncs", "interactiveMusic", "streamingDevice", "meter",
    "auxiliarySends", "apiCalls", "spatialAudio", "spatialAudioRaycasting",
    "voiceInspector", "audioObjects", "gameSyncs",
}


def wwise_profiler_enable_data(
    data_types: list[str],
    dry_run: bool = False,
) -> dict:
    """
    Enable the specified profiler data types for the next capture session.

    Args:
        data_types: List of data type name strings to enable. Valid values:
                    "voices", "busses", "performance", "gameSyncs", "outputs",
                    "streamingDevices".
        dry_run:    If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not data_types:
        err = "data_types must not be empty."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    invalid = [dt for dt in data_types if dt not in VALID_DATA_TYPES]
    if invalid:
        err = f"Invalid data types: {invalid}. Valid: {sorted(VALID_DATA_TYPES)}."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    # WAAPI expects objects: [{"dataType": "voices"}, ...]
    payload = [{"dataType": dt} for dt in data_types]

    try:
        with connect() as client:
            result = client.call(WAAPI_URI, {"dataTypes": payload})
            if result is None:
                err = "profiler.enableProfilerData returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = True

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": True, "data": None, "error": None}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_profiler_enable_data)
