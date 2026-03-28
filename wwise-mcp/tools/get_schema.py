"""
wwise_get_schema — ak.wwise.waapi.getSchema
Retrieve the JSON schema for a specific WAAPI command URI.
"""

from __future__ import annotations
from .client import connect, write_phase2_log, validate_response, get_mock_response

WAAPI_URI = "ak.wwise.waapi.getSchema"
TOOL_NAME = "wwise_get_schema"


def wwise_get_schema(
    uri: str,
    dry_run: bool = False,
) -> dict:
    """
    Retrieve the argument and result JSON schemas for a WAAPI command.

    Args:
        uri:     The WAAPI URI to retrieve the schema for
                 (e.g., "ak.wwise.core.object.get").
        dry_run: If True, skip WAAPI call and return mock response.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if not uri or not uri.strip():
        err = "uri must be a non-empty string."
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
            result = client.call(WAAPI_URI, {"uri": uri})
            if result is None:
                err = f"waapi.getSchema returned None for uri={uri!r}."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            checks["execute"] = True
            checks["post_check"] = "argsSchema" in result or "resultSchema" in result

    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    response = {
        "success": checks["post_check"],
        "data": result if checks["post_check"] else None,
        "error": None if checks["post_check"] else "schema keys missing from response",
    }
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    return response if passed else {**response, "success": False, "error": verr or "schema_match failed"}


def register(mcp) -> None:
    mcp.tool()(wwise_get_schema)
