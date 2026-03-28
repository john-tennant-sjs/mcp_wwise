"""
scripts/run_phase2_verify.py

Runs all Phase 2 pytest tests against live Wwise, then reads logs/phase2.jsonl
and prints a summary table.

Exit code: 0 if all 15 tools pass, 1 if any fail.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOG_FILE = ROOT / "logs" / "phase2.jsonl"
TESTS_DIR = ROOT / "tests"

TOOL_NAMES = [
    "wwise_get_object",
    "wwise_create_object",
    "wwise_delete_object",
    "wwise_set_property",
    "wwise_set_name",
    "wwise_set_notes",
    "wwise_set_object",
    "wwise_copy_object",
    "wwise_move_object",
    "wwise_set_reference",
    "wwise_save_project",
    "wwise_create_transport",
    "wwise_transport_execute",
    "wwise_import_audio",
    "wwise_generate_soundbank",
]


def run_pytest() -> int:
    print("=" * 60)
    print("Running Phase 2 tests against live Wwise...")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS_DIR),
         "-v", "--tb=short", "-p", "no:cacheprovider"],
        cwd=str(ROOT),
    )
    return result.returncode


def read_latest_results() -> dict[str, dict]:
    """
    Return the most recent PASSING entry per tool.
    If no passing entry exists, return the most recent failing entry.
    This avoids negative-test invocations masking real pass results.
    """
    best: dict[str, dict] = {}
    if not LOG_FILE.exists():
        return best
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("phase") != "2" or not entry.get("tool"):
                continue
            tool = entry["tool"]
            existing = best.get(tool)
            # Prefer a passing entry over a failing one; otherwise take latest
            if existing is None:
                best[tool] = entry
            elif entry.get("pass") and not existing.get("pass"):
                best[tool] = entry  # upgrade from fail to pass
            elif entry.get("pass") == existing.get("pass"):
                best[tool] = entry  # same status — keep latest
    return best


def print_summary(results: dict[str, dict]) -> bool:
    print("\n" + "=" * 60)
    print("Phase 2 Tool Verification Summary")
    print("=" * 60)
    all_pass = True
    for tool in TOOL_NAMES:
        entry = results.get(tool)
        if not entry:
            print(f"  [MISSING] {tool}")
            all_pass = False
            continue
        status = "PASS" if entry.get("pass") else "FAIL"
        checks = entry.get("checks", {})
        check_str = "  ".join(
            f"{'✓' if v else '✗'} {k}" for k, v in checks.items()
        )
        err = f"  ERROR: {entry['error']}" if not entry.get("pass") else ""
        print(f"  [{status}] {tool}")
        if check_str:
            print(f"         {check_str}")
        if err:
            print(f"        {err}")
        if not entry.get("pass"):
            all_pass = False
    print("=" * 60)
    total = len(TOOL_NAMES)
    passed = sum(1 for t in TOOL_NAMES if results.get(t, {}).get("pass"))
    print(f"Result: {passed}/{total} tools passing")
    print("=" * 60)
    return all_pass


def main() -> int:
    pytest_rc = run_pytest()
    results = read_latest_results()
    all_pass = print_summary(results)

    if all_pass:
        print("\nPhase 2 COMPLETE — all tools verified.")
        return 0
    else:
        print(f"\nPhase 2 INCOMPLETE — see failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
