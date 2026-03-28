"""
wwise_profiler_get_voice_contributions — ak.wwise.core.profiler.getVoiceContributions
Retrieve voice contribution data at a given profiler time.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.profiler.getVoiceContributions"
TOOL_NAME = "wwise_profiler_get_voice_contributions"


def wwise_profiler_get_voice_contributions(
    voice_pipeline_id: int,
    time: int,
    busses_pipeline_id: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Retrieve voice contribution data for a specific voice at a profiler time.

    Args:
        voice_pipeline_id:  Pipeline ID of the voice.
        time:               Profiler cursor time in ms.
        busses_pipeline_id: Optional pipeline ID of the bus.
        dry_run:            If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not isinstance(voice_pipeline_id, int) or voice_pipeline_id < 0:
        err = f"voice_pipeline_id must be a non-negative integer, got: {voice_pipeline_id!r}"
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    if not isinstance(time, int) or time < 0:
        err = f"time must be a non-negative integer (ms), got: {time!r}"
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
            args: dict = {"voicePipelineID": voice_pipeline_id, "time": time}
            if busses_pipeline_id is not None:
                args["bussesPipelineID"] = busses_pipeline_id

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "profiler.getVoiceContributions returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            contributions = result.get("return", [])
            checks["post_check"] = isinstance(contributions, list)

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": {"contributions": contributions} if checks["post_check"] else None,
        "error": None if checks["post_check"] else "return key missing",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_profiler_get_voice_contributions)
