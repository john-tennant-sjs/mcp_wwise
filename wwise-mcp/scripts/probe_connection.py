"""
Phase 0 connection probe.
Connects to WAAPI on ws://localhost:9000/waapi, calls ak.wwise.core.getInfo,
and writes a structured result to logs/phase0.jsonl.

Exit code: 0 on pass, 1 on failure.
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOGS_DIR / "phase0.jsonl"
WAAPI_URL = "ws://127.0.0.1:9000/waapi"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_log(entry: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))


def run_probe() -> dict:
    from waapi import WaapiClient, CannotConnectToWaapiException

    try:
        with WaapiClient(url=WAAPI_URL) as client:
            result = client.call("ak.wwise.core.getInfo")
    except CannotConnectToWaapiException as e:
        return {
            "timestamp": utc_now(),
            "phase": "0",
            "check": "connection_probe",
            "tool": None,
            "pass": False,
            "error": f"CannotConnectToWaapiException: {e}",
            "detail": {
                "transport": "websocket",
                "port": 9000,
                "url": WAAPI_URL,
            },
        }
    except Exception as e:
        return {
            "timestamp": utc_now(),
            "phase": "0",
            "check": "connection_probe",
            "tool": None,
            "pass": False,
            "error": f"{type(e).__name__}: {e}",
            "detail": {
                "transport": "websocket",
                "port": 9000,
                "url": WAAPI_URL,
                "traceback": traceback.format_exc(),
            },
        }

    if result is None:
        return {
            "timestamp": utc_now(),
            "phase": "0",
            "check": "connection_probe",
            "tool": None,
            "pass": False,
            "error": "ak.wwise.core.getInfo returned None",
            "detail": {"transport": "websocket", "port": 9000},
        }

    wwise_version = result.get("version", {})
    version_str = (
        f"{wwise_version.get('displayName', '')} "
        f"(build {wwise_version.get('build', '?')})"
    ).strip()

    return {
        "timestamp": utc_now(),
        "phase": "0",
        "check": "connection_probe",
        "tool": None,
        "pass": True,
        "error": None,
        "detail": {
            "wwise_version": version_str,
            "transport": "websocket",
            "port": 9000,
            "url": WAAPI_URL,
            "raw_getInfo": result,
        },
    }


def main() -> int:
    print(f"[probe] Connecting to {WAAPI_URL} ...")
    entry = run_probe()
    write_log(entry)

    if entry["pass"]:
        print("\n[probe] PASS — Phase 0 connection verified.")
        return 0
    else:
        print(f"\n[probe] FAIL — {entry['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
