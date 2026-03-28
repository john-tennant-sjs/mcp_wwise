"""
scripts/validate_contracts.py — Phase 3/4 contract validation (no Wwise required).

For each of the 39 tools:
  1. Load the contract from contracts/<tool>.json
  2. Call the tool with dry_run=True and minimal valid inputs
  3. Validate the returned response against the contract's output_schema
  4. Report pass/fail per tool

Exit code: 0 if schema_violations == 0, else 1.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

LOGS_DIR = ROOT / "logs"
LOG_FILE = LOGS_DIR / "phase3.jsonl"

# ---------------------------------------------------------------------------
# Dry-run call specs: (tool_function, kwargs)
# These use minimal valid inputs that pass the pre_check without Wwise.
# ---------------------------------------------------------------------------
from tools.get_object import wwise_get_object
from tools.create_object import wwise_create_object
from tools.delete_object import wwise_delete_object
from tools.set_property import wwise_set_property
from tools.set_name import wwise_set_name
from tools.set_notes import wwise_set_notes
from tools.set_object import wwise_set_object
from tools.copy_object import wwise_copy_object
from tools.move_object import wwise_move_object
from tools.set_reference import wwise_set_reference
from tools.save_project import wwise_save_project
from tools.create_transport import wwise_create_transport
from tools.transport_execute import wwise_transport_execute
from tools.import_audio import wwise_import_audio
from tools.generate_soundbank import wwise_generate_soundbank
# Phase 4 — Batch 1
from tools.transport_destroy import wwise_transport_destroy
from tools.transport_get_state import wwise_transport_get_state
from tools.transport_prepare import wwise_transport_prepare
from tools.get_info import wwise_get_info
from tools.undo_begin_group import wwise_undo_begin_group
from tools.undo_end_group import wwise_undo_end_group
from tools.undo_cancel_group import wwise_undo_cancel_group
from tools.log_get import wwise_log_get
from tools.ui_get_selected_objects import wwise_ui_get_selected_objects
from tools.switch_container_get_assignments import wwise_switch_container_get_assignments
from tools.switch_container_add_assignment import wwise_switch_container_add_assignment
from tools.switch_container_remove_assignment import wwise_switch_container_remove_assignment
# Phase 4 — Batch 2
from tools.soundbank_get_inclusions import wwise_soundbank_get_inclusions
from tools.soundbank_set_inclusions import wwise_soundbank_set_inclusions
from tools.get_attenuation_curve import wwise_get_attenuation_curve
from tools.set_attenuation_curve import wwise_set_attenuation_curve
from tools.profiler_start_capture import wwise_profiler_start_capture
from tools.profiler_stop_capture import wwise_profiler_stop_capture
from tools.profiler_get_cursor_time import wwise_profiler_get_cursor_time
from tools.profiler_enable_data import wwise_profiler_enable_data
from tools.profiler_get_voice_contributions import wwise_profiler_get_voice_contributions
from tools.ui_commands_execute import wwise_ui_commands_execute
from tools.paste_properties import wwise_paste_properties
from tools.get_schema import wwise_get_schema
from tools.ui_bring_to_foreground import wwise_ui_bring_to_foreground
from tools.client import validate_response

MOCK_PATH = "\\Actor-Mixer Hierarchy\\Default Work Unit\\MCP_Tests\\_dry_run"
MOCK_ID = "{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}"

DRY_RUN_CALLS = [
    ("wwise_get_object",        wwise_get_object,        {"from_path": [MOCK_PATH], "dry_run": True}),
    ("wwise_create_object",     wwise_create_object,     {"parent": MOCK_PATH, "object_type": "Sound", "name": "_dr", "dry_run": True}),
    ("wwise_delete_object",     wwise_delete_object,     {"object_ref": MOCK_PATH, "dry_run": True}),
    ("wwise_set_property",      wwise_set_property,      {"object_ref": MOCK_PATH, "property_name": "Volume", "value": -6.0, "dry_run": True}),
    ("wwise_set_name",          wwise_set_name,          {"object_ref": MOCK_PATH, "new_name": "_renamed", "dry_run": True}),
    ("wwise_set_notes",         wwise_set_notes,         {"object_ref": MOCK_PATH, "notes": "test", "dry_run": True}),
    ("wwise_set_object",        wwise_set_object,        {"objects": [{"object": MOCK_PATH, "@Volume": -3.0}], "dry_run": True}),
    ("wwise_copy_object",       wwise_copy_object,       {"object_ref": MOCK_PATH, "parent": MOCK_PATH, "dry_run": True}),
    ("wwise_move_object",       wwise_move_object,       {"object_ref": MOCK_PATH, "parent": MOCK_PATH, "dry_run": True}),
    ("wwise_set_reference",     wwise_set_reference,     {"object_ref": MOCK_PATH, "reference": "Conversion", "value": MOCK_ID, "dry_run": True}),
    ("wwise_save_project",      wwise_save_project,      {"dry_run": True}),
    ("wwise_create_transport",  wwise_create_transport,  {"object_ref": MOCK_PATH, "dry_run": True}),
    ("wwise_transport_execute", wwise_transport_execute, {"object_ref": MOCK_PATH, "action": "play", "dry_run": True}),
    ("wwise_import_audio",      wwise_import_audio,      {"imports": [{"audioFile": "T:\\fake.wav", "objectPath": MOCK_PATH + "\\<Sound>_dr"}], "dry_run": True}),
    ("wwise_generate_soundbank",wwise_generate_soundbank,{"dry_run": True}),
    # Phase 4 — Batch 1
    ("wwise_transport_destroy",           wwise_transport_destroy,           {"transport": 0, "dry_run": True}),
    ("wwise_transport_get_state",         wwise_transport_get_state,         {"transport": 0, "dry_run": True}),
    ("wwise_transport_prepare",           wwise_transport_prepare,           {"object_ref": MOCK_PATH, "dry_run": True}),
    ("wwise_get_info",                    wwise_get_info,                    {"dry_run": True}),
    ("wwise_undo_begin_group",            wwise_undo_begin_group,            {"dry_run": True}),
    ("wwise_undo_end_group",              wwise_undo_end_group,              {"display_name": "_test", "dry_run": True}),
    ("wwise_undo_cancel_group",           wwise_undo_cancel_group,           {"dry_run": True}),
    ("wwise_log_get",                     wwise_log_get,                     {"channel": "general", "dry_run": True}),
    ("wwise_ui_get_selected_objects",     wwise_ui_get_selected_objects,     {"dry_run": True}),
    ("wwise_switch_container_get_assignments", wwise_switch_container_get_assignments, {"object_ref": MOCK_PATH, "dry_run": True}),
    ("wwise_switch_container_add_assignment",  wwise_switch_container_add_assignment,  {"child": MOCK_PATH, "state_or_switch": MOCK_PATH, "dry_run": True}),
    ("wwise_switch_container_remove_assignment", wwise_switch_container_remove_assignment, {"child": MOCK_PATH, "state_or_switch": MOCK_PATH, "dry_run": True}),
    # Phase 4 — Batch 2
    ("wwise_soundbank_get_inclusions",    wwise_soundbank_get_inclusions,    {"soundbank": MOCK_PATH, "dry_run": True}),
    ("wwise_soundbank_set_inclusions",    wwise_soundbank_set_inclusions,    {"soundbank": MOCK_PATH, "inclusions": [{"object": MOCK_PATH, "filter": ["events"]}], "dry_run": True}),
    ("wwise_get_attenuation_curve",       wwise_get_attenuation_curve,       {"object_ref": MOCK_PATH, "curve_type": "VolumeDryUsage", "dry_run": True}),
    ("wwise_set_attenuation_curve",       wwise_set_attenuation_curve,       {"object_ref": MOCK_PATH, "curve_type": "VolumeDryUsage", "use": "Custom", "points": [{"x": 0, "y": 0, "shape": "Linear"}], "dry_run": True}),
    ("wwise_profiler_start_capture",      wwise_profiler_start_capture,      {"dry_run": True}),
    ("wwise_profiler_stop_capture",       wwise_profiler_stop_capture,       {"dry_run": True}),
    ("wwise_profiler_get_cursor_time",    wwise_profiler_get_cursor_time,    {"cursor": "capture", "dry_run": True}),
    ("wwise_profiler_enable_data",        wwise_profiler_enable_data,        {"data_types": ["voices"], "dry_run": True}),
    ("wwise_profiler_get_voice_contributions", wwise_profiler_get_voice_contributions, {"voice_pipeline_id": 0, "time": 0, "dry_run": True}),
    ("wwise_ui_commands_execute",         wwise_ui_commands_execute,         {"command": "FindInProjectExplorer", "dry_run": True}),
    ("wwise_paste_properties",            wwise_paste_properties,            {"source": MOCK_PATH, "targets": [MOCK_PATH], "dry_run": True}),
    ("wwise_get_schema",                  wwise_get_schema,                  {"uri": "ak.wwise.core.object.get", "dry_run": True}),
    ("wwise_ui_bring_to_foreground",      wwise_ui_bring_to_foreground,      {"dry_run": True}),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_log(entry: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> int:
    print("=" * 60)
    print("Phase 3/4 — Contract Validation (dry_run mode, no Wwise needed)")
    print("=" * 60)

    violations = 0
    results = []

    for tool_name, fn, kwargs in DRY_RUN_CALLS:
        try:
            response = fn(**kwargs)
        except Exception as e:
            violations += 1
            results.append((tool_name, False, f"exception: {e}"))
            continue

        ok, verr = validate_response(tool_name, response)
        if not ok:
            violations += 1
            results.append((tool_name, False, verr))
        else:
            results.append((tool_name, True, None))

    # Print summary
    print()
    for tool_name, passed, err in results:
        status = "PASS" if passed else "FAIL"
        line = f"  [{status}] {tool_name}"
        if err:
            line += f"\n         ERROR: {err}"
        print(line)

    passed_count = sum(1 for _, p, _ in results if p)
    print()
    print(f"Result: {passed_count}/{len(results)} tools — {violations} schema violation(s)")
    print("=" * 60)

    # Write phase3 log
    log_entry = {
        "timestamp": utc_now(),
        "phase": "3",
        "check": "contract_validation",
        "tool": None,
        "pass": violations == 0,
        "error": None if violations == 0 else f"{violations} schema violation(s)",
        "detail": {
            "tools_with_contracts": len(results),
            "schema_violations": violations,
            "dry_run_mode": True,
        },
    }
    write_log(log_entry)
    print(json.dumps(log_entry, indent=2))

    return 0 if violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
