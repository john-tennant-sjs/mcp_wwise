"""
wwise_generate_soundbank — ak.wwise.core.soundbank.generate
Generate one or more soundbanks.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.soundbank.generate"
TOOL_NAME = "wwise_generate_soundbank"


def wwise_generate_soundbank(
    soundbanks: list[str] | None = None,
    platforms: list[str] | None = None,
    languages: list[str] | None = None,
    write_to_disk: bool = True,
    rebuild: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Generate soundbanks for the current Wwise project.

    Args:
        soundbanks:    List of soundbank names/GUIDs. Omit to generate all.
        platforms:     List of platform names. Omit for all platforms.
        languages:     List of language names/GUIDs. Omit for all languages.
        write_to_disk: Write generated banks to disk. Default: True.
        rebuild:       Force full rebuild. Default: False.
        dry_run:       If True, skip WAAPI call and return mock response.
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
            info = client.call("ak.wwise.core.getInfo")
            if not info:
                err = "Cannot reach Wwise."
                checks["pre_check"] = False
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}

            args: dict = {"writeToDisk": write_to_disk, "rebuildSoundBanks": rebuild}
            if soundbanks:
                args["soundbanks"] = [{"name": sb} for sb in soundbanks]
            if platforms:
                args["platforms"] = platforms
            if languages:
                args["languages"] = [{"name": lang} for lang in languages]

            result = client.call(WAAPI_URI, args)
            if result is None:
                err = "soundbank.generate returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = isinstance(result, dict)

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"], "data": result if checks["post_check"] else None,
                "error": None if checks["post_check"] else "post_check failed"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_generate_soundbank)
