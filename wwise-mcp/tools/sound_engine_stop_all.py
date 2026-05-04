"""
wwise_sound_engine_stop_all — ak.soundengine.stopAll
Stop all sounds currently playing in the Wwise sound engine.

Always passes gameObject=AK_INVALID_GAME_OBJECT (0xFFFFFFFFFFFFFFFF), which
mirrors AK::SoundEngine::StopAll() with its default parameter. This works on
Wwise 2023 (gameObject required) and 2025+ (gameObject optional but accepted).
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.soundengine.stopAll"
TOOL_NAME = "wwise_sound_engine_stop_all"

# Mirrors AK_INVALID_GAME_OBJECT from the Wwise C++ SDK ((AkGameObjectID)-1).
# Passing this to stopAll means "stop sounds on all game objects" and works
# on both Wwise 2023 (where gameObject is required) and 2025+ (where it is
# optional but still accepted).
AK_INVALID_GAME_OBJECT = 0xFFFFFFFFFFFFFFFF


def wwise_sound_engine_stop_all(dry_run: bool = False) -> dict:
    """
    Stop all sounds currently playing in the Wwise sound engine.

    Calls ak.soundengine.stopAll with gameObject=AK_INVALID_GAME_OBJECT
    (0xFFFFFFFFFFFFFFFF), which stops sounds across all game objects.
    This works on both Wwise 2023 (gameObject required) and 2025+ (optional).

    Args:
        dry_run: If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    checks["pre_check"] = True

    if dry_run:
        mock = get_mock_response(TOOL_NAME)
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    try:
        with connect() as client:
            # Always pass AK_INVALID_GAME_OBJECT — required in 2023, optional but
            # accepted in 2025. Using a unified call avoids version-branching.
            args: dict = {"gameObject": AK_INVALID_GAME_OBJECT}

            result = client.call(WAAPI_URI, args)
            # ak.soundengine.stopAll returns {} on success; None signals failure
            if result is None:
                err = (
                    f"soundengine.stopAll returned None (args={args}). "
                    "No sounds may be playing, or the game object ID was rejected."
                )
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
    mcp.tool()(wwise_sound_engine_stop_all)
