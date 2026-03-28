"""
wwise_import_audio — ak.wwise.core.audio.import
Import audio files into the Wwise project.
"""

from __future__ import annotations
from pathlib import Path
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.core.audio.import"
TOOL_NAME = "wwise_import_audio"


def wwise_import_audio(
    imports: list[dict],
    import_operation: str = "useExisting",
    import_language: str = "SFX",
    default_object_type: str = "Sound",
    default_import_location: str | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Import audio files into the Wwise project.

    Each item in `imports` must have:
      - "audioFile":   Absolute path to the audio file on disk.
      - "objectPath":  Absolute: "\\\\Hierarchy\\\\Parent\\\\<Type>name"
                       Relative: "<Type>name"  (requires default_import_location)

    Args:
        imports:                  List of import items.
        import_operation:         "useExisting" | "replaceExisting" | "createNew".
        import_language:          Language tag (e.g. "SFX", "English(US)").
        default_object_type:      Fallback object type. Default: "Sound".
        default_import_location:  Default import root path/GUID (optional).
        dry_run:                  If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not imports:
        err = "imports list is empty."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    for item in imports:
        if "audioFile" not in item or "objectPath" not in item:
            err = f"Each import item needs 'audioFile' and 'objectPath': {item}"
            write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
            return {"success": False, "data": None, "error": err}
        if not dry_run and not Path(item["audioFile"]).exists():
            err = f"Audio file not found: {item['audioFile']}"
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
            default: dict = {
                "importLanguage": import_language,
                "objectType": default_object_type,
            }
            if default_import_location:
                default["importLocation"] = default_import_location

            result = client.call(WAAPI_URI, {
                "importOperation": import_operation,
                "default": default,
                "imports": imports,
            })
            if result is None:
                err = "audio.import returned None."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True

            imported_objects = result.get("objects", [])
            checks["post_check"] = len(imported_objects) > 0

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {"success": checks["post_check"],
                "data": {"imported": imported_objects} if checks["post_check"] else None,
                "error": None if checks["post_check"] else "no objects imported"}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_import_audio)
