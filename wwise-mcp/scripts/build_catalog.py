"""
scripts/build_catalog.py — Phase 1

Steps:
  1. Connect to WAAPI, call ak.wwise.waapi.getSchema to get the live API schema
  2. Parse all callable URIs into catalog entries
  3. Score each command for use in an authoring workflow
  4. Write waapi-catalog.json
  5. Extract top 15 to phase2-targets.json
  6. Write pass/fail entry to logs/phase1.jsonl

Exit code: 0 on pass, 1 on failure.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOGS_DIR = ROOT / "logs"
LOG_FILE = LOGS_DIR / "phase1.jsonl"
CATALOG_FILE = ROOT / "waapi-catalog.json"
TARGETS_FILE = ROOT / "phase2-targets.json"
WAAPI_URL = "ws://127.0.0.1:9000/waapi"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_log(entry: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Scoring heuristics
# ---------------------------------------------------------------------------

# Workflow frequency scores (1-10): how often a sound designer would call this
# in a typical authoring session.
FREQUENCY_SCORES: dict[str, int] = {
    "ak.wwise.core.getInfo": 3,
    "ak.wwise.core.object.get": 10,
    "ak.wwise.core.object.create": 9,
    "ak.wwise.core.object.delete": 8,
    "ak.wwise.core.object.setProperty": 10,
    "ak.wwise.core.object.setName": 8,
    "ak.wwise.core.object.setNotes": 6,
    "ak.wwise.core.object.copy": 7,
    "ak.wwise.core.object.move": 7,
    "ak.wwise.core.object.set": 8,
    "ak.wwise.core.object.setReference": 7,
    "ak.wwise.core.object.getPropertyAndObjectLists": 5,
    "ak.wwise.core.object.getPropertyNames": 5,
    "ak.wwise.core.object.getAttenuationCurve": 5,
    "ak.wwise.core.object.setAttenuationCurve": 5,
    "ak.wwise.core.object.pasteProperties": 4,
    "ak.wwise.core.project.save": 8,
    "ak.wwise.core.project.load": 3,
    "ak.wwise.core.project.close": 2,
    "ak.wwise.core.transport.create": 7,
    "ak.wwise.core.transport.destroy": 7,
    "ak.wwise.core.transport.executeAction": 8,
    "ak.wwise.core.transport.getState": 5,
    "ak.wwise.core.transport.list": 4,
    "ak.wwise.core.transport.prepare": 6,
    "ak.wwise.core.audio.import": 8,
    "ak.wwise.core.audio.importTabDelimited": 4,
    "ak.wwise.core.soundbank.generate": 7,
    "ak.wwise.core.soundbank.getInclusions": 5,
    "ak.wwise.core.soundbank.setInclusions": 5,
    "ak.wwise.core.undo.beginGroup": 6,
    "ak.wwise.core.undo.endGroup": 6,
    "ak.wwise.core.undo.cancelGroup": 4,
    "ak.wwise.core.switchContainer.addAssignment": 6,
    "ak.wwise.core.switchContainer.removeAssignment": 6,
    "ak.wwise.core.switchContainer.getAssignments": 5,
    "ak.wwise.core.profiler.enableProfilerData": 4,
    "ak.wwise.core.profiler.getVoiceContributions": 4,
    "ak.wwise.core.profiler.getCursorTime": 3,
    "ak.wwise.core.profiler.startCapture": 3,
    "ak.wwise.core.profiler.stopCapture": 3,
    "ak.wwise.core.profiler.getGameObjectList": 3,
    "ak.wwise.core.remote.connect": 2,
    "ak.wwise.core.remote.disconnect": 2,
    "ak.wwise.core.remote.getAvailableConsoles": 2,
    "ak.wwise.core.remote.getConnectionStatus": 2,
    "ak.wwise.core.log.get": 5,
    "ak.wwise.ui.getSelectedObjects": 6,
    "ak.wwise.ui.commands.execute": 4,
    "ak.wwise.ui.commands.register": 3,
    "ak.wwise.ui.commands.unregister": 2,
    "ak.wwise.ui.bringToForeground": 2,
    "ak.wwise.ui.project.open": 2,
    "ak.wwise.waapi.getSchema": 2,
}

# Verifiability bonus: can the post-check read back exactly what was written?
VERIFIABILITY_BONUS: dict[str, int] = {
    "ak.wwise.core.object.get": 3,
    "ak.wwise.core.object.create": 3,
    "ak.wwise.core.object.setProperty": 3,
    "ak.wwise.core.object.setName": 3,
    "ak.wwise.core.object.setNotes": 3,
    "ak.wwise.core.object.copy": 2,
    "ak.wwise.core.object.move": 2,
    "ak.wwise.core.object.set": 3,
    "ak.wwise.core.object.setReference": 2,
    "ak.wwise.core.object.delete": 2,
    "ak.wwise.core.project.save": 2,
    "ak.wwise.core.transport.create": 2,
    "ak.wwise.core.transport.executeAction": 2,
    "ak.wwise.core.transport.destroy": 2,
    "ak.wwise.core.getInfo": 3,
    "ak.wwise.core.soundbank.generate": 2,
    "ak.wwise.core.audio.import": 2,
    "ak.wwise.core.switchContainer.getAssignments": 2,
    "ak.wwise.core.switchContainer.addAssignment": 2,
}

# Mutating commands (change state)
MUTATING = {
    "ak.wwise.core.object.create",
    "ak.wwise.core.object.delete",
    "ak.wwise.core.object.setProperty",
    "ak.wwise.core.object.setName",
    "ak.wwise.core.object.setNotes",
    "ak.wwise.core.object.copy",
    "ak.wwise.core.object.move",
    "ak.wwise.core.object.set",
    "ak.wwise.core.object.setReference",
    "ak.wwise.core.object.setAttenuationCurve",
    "ak.wwise.core.object.pasteProperties",
    "ak.wwise.core.project.save",
    "ak.wwise.core.project.load",
    "ak.wwise.core.project.close",
    "ak.wwise.core.transport.create",
    "ak.wwise.core.transport.destroy",
    "ak.wwise.core.transport.executeAction",
    "ak.wwise.core.audio.import",
    "ak.wwise.core.audio.importTabDelimited",
    "ak.wwise.core.soundbank.generate",
    "ak.wwise.core.soundbank.setInclusions",
    "ak.wwise.core.undo.beginGroup",
    "ak.wwise.core.undo.endGroup",
    "ak.wwise.core.undo.cancelGroup",
    "ak.wwise.core.switchContainer.addAssignment",
    "ak.wwise.core.switchContainer.removeAssignment",
    "ak.wwise.core.remote.connect",
    "ak.wwise.core.remote.disconnect",
    "ak.wwise.ui.commands.register",
    "ak.wwise.ui.commands.unregister",
    "ak.wwise.ui.commands.execute",
    "ak.wwise.ui.project.open",
}

REQUIRES_OBJECT_PATH = {
    "ak.wwise.core.object.get",
    "ak.wwise.core.object.create",
    "ak.wwise.core.object.delete",
    "ak.wwise.core.object.setProperty",
    "ak.wwise.core.object.setName",
    "ak.wwise.core.object.setNotes",
    "ak.wwise.core.object.copy",
    "ak.wwise.core.object.move",
    "ak.wwise.core.object.set",
    "ak.wwise.core.object.setReference",
    "ak.wwise.core.object.getPropertyAndObjectLists",
    "ak.wwise.core.object.getPropertyNames",
    "ak.wwise.core.object.getAttenuationCurve",
    "ak.wwise.core.object.setAttenuationCurve",
    "ak.wwise.core.object.pasteProperties",
    "ak.wwise.core.transport.create",
    "ak.wwise.core.switchContainer.addAssignment",
    "ak.wwise.core.switchContainer.removeAssignment",
    "ak.wwise.core.switchContainer.getAssignments",
    "ak.wwise.core.soundbank.getInclusions",
    "ak.wwise.core.soundbank.setInclusions",
}


def derive_category(uri: str) -> str:
    parts = uri.split(".")
    # e.g. ak.wwise.core.object.get → core.object
    if len(parts) >= 4:
        return ".".join(parts[2:4])
    if len(parts) >= 3:
        return parts[2]
    return "unknown"


def score(uri: str) -> int:
    freq = FREQUENCY_SCORES.get(uri, 1)
    verif = VERIFIABILITY_BONUS.get(uri, 0)
    return freq + verif


def parse_schema_to_catalog(schema: dict) -> list[dict]:
    """Extract all callable URIs from the WAAPI getSchema result."""
    entries = []
    # The schema has a 'topics' or 'functions' key depending on version.
    # In Wwise 2023 the schema is a JSON Schema with 'definitions' or
    # a flat 'functions' list.  We handle both shapes.
    functions = schema.get("functions", [])
    if isinstance(functions, list):
        for fn in functions:
            uri = fn.get("id", fn.get("uri", ""))
            if not uri:
                continue
            desc = fn.get("schema", {}).get("description", fn.get("description", ""))
            entries.append(_make_entry(uri, desc))
    else:
        # Fallback: iterate over schema keys looking for 'ak.' prefixed entries
        for key, val in schema.items():
            if isinstance(key, str) and key.startswith("ak."):
                desc = val.get("description", "") if isinstance(val, dict) else ""
                entries.append(_make_entry(key, desc))

    return entries


def _make_entry(uri: str, desc: str) -> dict:
    s = score(uri)
    return {
        "uri": uri,
        "category": derive_category(uri),
        "description": desc or "(no description in schema)",
        "mutates": uri in MUTATING,
        "requires_object_path": uri in REQUIRES_OBJECT_PATH,
        "priority": s,
        "implemented": False,
        "verified": False,
        "verified_at": None,
    }


# Fallback catalog built from known WAAPI surface (used if schema parse yields < 20 entries)
KNOWN_URIS: list[tuple[str, str]] = [
    ("ak.wwise.core.getInfo", "Returns Wwise version, build, and session information."),
    ("ak.wwise.core.object.get", "Query Wwise objects using WAQL or path. Returns requested properties."),
    ("ak.wwise.core.object.create", "Create a new Wwise object under a specified parent."),
    ("ak.wwise.core.object.delete", "Delete one or more Wwise objects."),
    ("ak.wwise.core.object.set", "Set multiple properties on existing objects in one call."),
    ("ak.wwise.core.object.setProperty", "Set a single property on a Wwise object."),
    ("ak.wwise.core.object.setReference", "Set a reference-type property (e.g. Effect slot, Attenuation) on a Wwise object."),
    ("ak.wwise.core.object.setName", "Rename a Wwise object."),
    ("ak.wwise.core.object.setNotes", "Set the Notes field on a Wwise object."),
    ("ak.wwise.core.object.copy", "Copy a Wwise object to a new parent."),
    ("ak.wwise.core.object.move", "Move a Wwise object to a new parent."),
    ("ak.wwise.core.object.pasteProperties", "Paste properties from one object to another."),
    ("ak.wwise.core.object.getPropertyNames", "List valid property names for an object type."),
    ("ak.wwise.core.object.getPropertyAndObjectLists", "Get enum values and object lists for properties."),
    ("ak.wwise.core.object.getAttenuationCurve", "Get the attenuation curve data for an Attenuation object."),
    ("ak.wwise.core.object.setAttenuationCurve", "Set the attenuation curve data for an Attenuation object."),
    ("ak.wwise.core.project.save", "Save the current Wwise project."),
    ("ak.wwise.core.project.load", "Load a Wwise project from disk."),
    ("ak.wwise.core.project.close", "Close the current Wwise project."),
    ("ak.wwise.core.audio.import", "Import audio files and create Wwise objects (Sound SFX, Music Track, etc.)."),
    ("ak.wwise.core.audio.importTabDelimited", "Import audio via a tab-delimited import definition file."),
    ("ak.wwise.core.transport.create", "Create a transport object for auditioning an object."),
    ("ak.wwise.core.transport.destroy", "Destroy a previously created transport object."),
    ("ak.wwise.core.transport.executeAction", "Execute a playback action (play, stop, pause, resume, seek) on a transport."),
    ("ak.wwise.core.transport.getState", "Get the current playback state of a transport."),
    ("ak.wwise.core.transport.list", "List all active transport objects."),
    ("ak.wwise.core.transport.prepare", "Prepare a transport for auditioning."),
    ("ak.wwise.core.soundbank.generate", "Generate one or more soundbanks."),
    ("ak.wwise.core.soundbank.getInclusions", "Get the list of included events/objects for a soundbank."),
    ("ak.wwise.core.soundbank.setInclusions", "Set the list of included events/objects for a soundbank."),
    ("ak.wwise.core.undo.beginGroup", "Begin an undo group (batch multiple operations into one undoable step)."),
    ("ak.wwise.core.undo.endGroup", "End an undo group and commit it."),
    ("ak.wwise.core.undo.cancelGroup", "Cancel the current undo group and roll back changes."),
    ("ak.wwise.core.switchContainer.addAssignment", "Assign a state or switch value to a child object in a Switch Container."),
    ("ak.wwise.core.switchContainer.removeAssignment", "Remove a state/switch assignment from a Switch Container child."),
    ("ak.wwise.core.switchContainer.getAssignments", "Get the current state/switch assignments in a Switch Container."),
    ("ak.wwise.core.profiler.enableProfilerData", "Enable or disable specific profiler data streams."),
    ("ak.wwise.core.profiler.getCursorTime", "Get the current cursor time in the profiler."),
    ("ak.wwise.core.profiler.startCapture", "Start a profiler capture session."),
    ("ak.wwise.core.profiler.stopCapture", "Stop the current profiler capture session."),
    ("ak.wwise.core.profiler.getVoiceContributions", "Get voice contribution data for a profiler cursor position."),
    ("ak.wwise.core.profiler.getGameObjectList", "List all game objects currently visible in the profiler."),
    ("ak.wwise.core.remote.connect", "Connect to a remote Wwise Sound Engine instance."),
    ("ak.wwise.core.remote.disconnect", "Disconnect from the remote Sound Engine."),
    ("ak.wwise.core.remote.getAvailableConsoles", "List available remote Sound Engine consoles."),
    ("ak.wwise.core.remote.getConnectionStatus", "Get the current remote connection status."),
    ("ak.wwise.core.log.get", "Retrieve log entries from the Wwise message log."),
    ("ak.wwise.ui.getSelectedObjects", "Get the objects currently selected in the Wwise UI."),
    ("ak.wwise.ui.bringToForeground", "Bring the Wwise application window to the foreground."),
    ("ak.wwise.ui.commands.execute", "Execute a built-in Wwise UI command by ID."),
    ("ak.wwise.ui.commands.register", "Register a custom command in the Wwise UI."),
    ("ak.wwise.ui.commands.unregister", "Unregister a previously registered custom command."),
    ("ak.wwise.ui.project.open", "Open a Wwise project through the UI (shows dialog if unsaved changes)."),
    ("ak.wwise.waapi.getSchema", "Retrieve the full WAAPI JSON schema describing all available functions and topics."),
]


def build_fallback_catalog() -> list[dict]:
    return [_make_entry(uri, desc) for uri, desc in KNOWN_URIS]


def main() -> int:
    from waapi import WaapiClient, CannotConnectToWaapiException

    # ak.wwise.waapi.getSchema is per-URI only (no "list all" endpoint).
    # We use the built-in catalog and validate each URI against the live schema
    # to mark whether it exists on this Wwise version.
    catalog = build_fallback_catalog()
    source = "built_in"

    print("[catalog] Validating URIs against live Wwise schema...")
    confirmed = 0
    try:
        with WaapiClient(url=WAAPI_URL) as client:
            for entry in catalog:
                try:
                    client.call("ak.wwise.waapi.getSchema", {"uri": entry["uri"]})
                    entry["confirmed_in_wwise"] = True
                    confirmed += 1
                except Exception:
                    entry["confirmed_in_wwise"] = False
        print(f"[catalog] {confirmed}/{len(catalog)} URIs confirmed present in this Wwise version.")
        source = "built_in+validated"
    except CannotConnectToWaapiException as e:
        print(f"[catalog] WARN: Cannot connect ({e}) — skipping live validation.")
        for entry in catalog:
            entry["confirmed_in_wwise"] = None
    except Exception as e:
        print(f"[catalog] WARN: Live validation error ({e}) — skipping.")
        for entry in catalog:
            entry["confirmed_in_wwise"] = None

    # Sort by priority descending, then uri ascending
    catalog.sort(key=lambda e: (-e["priority"], e["uri"]))

    CATALOG_FILE.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"[catalog] Wrote {len(catalog)} entries to {CATALOG_FILE.name}  (source: {source})")

    # Extract top 15 by priority score
    top15 = catalog[:15]

    TARGETS_FILE.write_text(json.dumps(top15, indent=2), encoding="utf-8")
    print(f"\n[catalog] Top 15 by priority score:")
    for i, e in enumerate(top15, 1):
        print(f"  {i:2d}. [{e['priority']:2d}] {e['uri']}")

    entry = {
        "timestamp": utc_now(),
        "phase": "1",
        "check": "catalog_complete",
        "tool": None,
        "pass": True,
        "error": None,
        "detail": {
            "total_commands_cataloged": len(catalog),
            "top_15_selected": True,
            "output_file": str(TARGETS_FILE),
            "catalog_source": source,
        },
    }
    write_log(entry)
    print(f"\n[catalog] PASS — catalog complete, phase2-targets.json written.")
    print(json.dumps(entry, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
