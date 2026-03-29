"""
tools/client.py — shared WAAPI connection helper, log writer, and contract utilities.
Every tool imports from here; nothing else is shared.
"""

from __future__ import annotations

import asyncio
import json
import jsonschema
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from waapi import WaapiClient, CannotConnectToWaapiException

WAAPI_URL = "ws://127.0.0.1:9000/waapi"
ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / "logs"
PHASE2_LOG = LOGS_DIR / "phase2.jsonl"
CONTRACTS_DIR = ROOT_DIR / "contracts"

__all__ = [
    "connect",
    "WaapiClient",
    "CannotConnectToWaapiException",
    "write_phase2_log",
    "utc_now",
    "object_exists",
    "get_object_property",
    "resolve_class_id_for_type",
    "load_contract",
    "validate_response",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def connect() -> Generator[WaapiClient, None, None]:
    """Context manager that yields a connected WaapiClient on port 9000.

    Creates a fresh event loop for the current thread if none exists — required
    when running inside FastMCP's AnyIO worker threads.
    """
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    with WaapiClient(url=WAAPI_URL) as client:
        yield client


def write_phase2_log(
    tool: str,
    waapi_uri: str,
    checks: dict[str, bool],
    passed: bool,
    error: str | None = None,
) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": utc_now(),
        "phase": "2",
        "tool": tool,
        "waapi_uri": waapi_uri,
        "checks": checks,
        "pass": passed,
        "error": error,
    }
    with PHASE2_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def object_exists(client: WaapiClient, ref: str) -> bool:
    """Return True if a Wwise object identified by GUID or path exists."""
    result = client.call(
        "ak.wwise.core.object.get",
        {"from": {"path": [ref]} if ref.startswith("\\") else {"id": [ref]},
         "options": {"return": ["id"]}},
    )
    return bool(result and result.get("return"))


def get_object_property(client: WaapiClient, ref: str, prop: str):
    """Return the value of a single property on an object, or None."""
    result = client.call(
        "ak.wwise.core.object.get",
        {"from": {"path": [ref]} if ref.startswith("\\") else {"id": [ref]},
         "options": {"return": [prop]}},
    )
    if result and result.get("return"):
        return result["return"][0].get(prop)
    return None


def resolve_class_id_for_type(client: WaapiClient, object_type: str) -> int | None:
    """Map a Wwise type string (e.g. from wwise_get_object \"type\") to classId for getPropertyNames."""
    result = client.call("ak.wwise.core.object.getTypes", {})
    if not result or "return" not in result:
        return None
    for entry in result["return"]:
        if entry.get("name") == object_type:
            cid = entry.get("classId")
            return int(cid) if cid is not None else None
    return None


# ---------------------------------------------------------------------------
# Contract utilities (Phase 3)
# ---------------------------------------------------------------------------

_contract_cache: dict[str, dict] = {}


def load_contract(tool_name: str) -> dict:
    """Load and cache the contract JSON for a tool."""
    if tool_name not in _contract_cache:
        path = CONTRACTS_DIR / f"{tool_name}.json"
        _contract_cache[tool_name] = json.loads(path.read_text(encoding="utf-8"))
    return _contract_cache[tool_name]


def validate_response(tool_name: str, response: dict) -> tuple[bool, str | None]:
    """
    Validate a tool response dict against its contract's output_schema.
    Returns (ok: bool, error_message: str | None).
    """
    try:
        contract = load_contract(tool_name)
        jsonschema.validate(response, contract["output_schema"])
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"schema violation: {e.message} at {list(e.absolute_path)}"
    except FileNotFoundError:
        return False, f"contract file not found for {tool_name}"
    except Exception as e:
        return False, str(e)


def get_mock_response(tool_name: str) -> dict:
    """Return the mock response from a tool's contract (used in dry_run mode)."""
    contract = load_contract(tool_name)
    return dict(contract["mock_response"])
