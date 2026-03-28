"""
scripts/status.py — single command phase-by-phase status summary.
Reads all logs/*.jsonl files and prints a summary table.
"""

import json
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "logs"

PHASES = ["0", "1", "2", "3", "4", "5"]


def read_latest(log_file: Path) -> dict[tuple[str, str], dict]:
    """
    Return a dict keyed by (check, tool) with the best entry:
    prefer the most recent PASS; fall back to the most recent FAIL.
    """
    best: dict[tuple[str, str], dict] = {}
    if not log_file.exists():
        return best
    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (entry.get("check", ""), entry.get("tool", ""))
            existing = best.get(key)
            if existing is None:
                best[key] = entry
            elif entry.get("pass") and not existing.get("pass"):
                best[key] = entry  # upgrade fail → pass
            elif entry.get("pass") == existing.get("pass"):
                best[key] = entry  # same status, keep latest
    return best


def main() -> None:
    print("\n=== Wwise MCP — Phase Status ===\n")

    for phase in PHASES:
        log_file = LOGS_DIR / f"phase{phase}.jsonl"
        entries = read_latest(log_file)

        if not entries:
            print(f"Phase {phase}: no log data")
            continue

        print(f"Phase {phase}:")
        for (check, tool), entry in sorted(entries.items()):
            status = "PASS" if entry.get("pass") else "FAIL"
            label = check or "(no check)"
            if tool:
                label = f"{label} / {tool}"
            error = f"  ERROR: {entry['error']}" if not entry.get("pass") and entry.get("error") else ""
            print(f"  [{status}] {label}{error}")
        print()


if __name__ == "__main__":
    main()
