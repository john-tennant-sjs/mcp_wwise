"""
scripts/write_contracts.py — generate contracts/ directory for all 15 Phase 2 tools.

Each contract contains:
  - tool:          tool function name
  - waapi_uri:     WAAPI procedure URI
  - input_schema:  JSON Schema for the tool's arguments
  - output_schema: JSON Schema for the tool's return value (shared with tests/schemas/)
  - mock_response: A minimal valid response for dry_run mode
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = ROOT / "contracts"
CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

MOCK_ID = "{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}"
MOCK_NAME = "_dry_run_object"
MOCK_PATH = "\\Actor-Mixer Hierarchy\\Default Work Unit\\MCP_Tests\\_dry_run_object"

# ---------------------------------------------------------------------------
# Shared output schema fragments
# ---------------------------------------------------------------------------
SUCCESS_ERROR = {
    "success": {"type": "boolean"},
    "error": {"type": ["string", "null"]},
}

NULL_OR = lambda s: {"oneOf": [s, {"type": "null"}]}
ID_NAME_OBJ = {
    "type": "object",
    "required": ["id", "name"],
    "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
    "additionalProperties": True,
}


def out(data_schema):
    return {
        "type": "object",
        "required": ["success", "data", "error"],
        "properties": {**SUCCESS_ERROR, "data": data_schema},
        "additionalProperties": False,
    }


# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------
CONTRACTS = {

"wwise_get_object": {
    "tool": "wwise_get_object",
    "waapi_uri": "ak.wwise.core.object.get",
    "input_schema": {
        "type": "object",
        "properties": {
            "from_path": {"oneOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
            "from_id":   {"oneOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
            "waql":      {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "return_props": {"oneOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "array",
        "items": {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}},
    })),
    "mock_response": {
        "success": True,
        "data": [{"id": MOCK_ID, "name": MOCK_NAME, "type": "Sound", "path": MOCK_PATH}],
        "error": None,
    },
},

"wwise_create_object": {
    "tool": "wwise_create_object",
    "waapi_uri": "ak.wwise.core.object.create",
    "input_schema": {
        "type": "object",
        "required": ["parent", "object_type", "name"],
        "properties": {
            "parent":           {"type": "string"},
            "object_type":      {"type": "string"},
            "name":             {"type": "string"},
            "on_name_conflict": {"type": "string", "enum": ["fail", "rename", "replace", "merge"]},
            "notes":            {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "dry_run":          {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR(ID_NAME_OBJ)),
    "mock_response": {"success": True, "data": {"id": MOCK_ID, "name": MOCK_NAME}, "error": None},
},

"wwise_delete_object": {
    "tool": "wwise_delete_object",
    "waapi_uri": "ak.wwise.core.object.delete",
    "input_schema": {
        "type": "object",
        "required": ["object_ref"],
        "properties": {"object_ref": {"type": "string"}, "dry_run": {"type": "boolean"}},
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["deleted"],
        "properties": {"deleted": {"type": "string"}},
    })),
    "mock_response": {"success": True, "data": {"deleted": MOCK_PATH}, "error": None},
},

"wwise_set_property": {
    "tool": "wwise_set_property",
    "waapi_uri": "ak.wwise.core.object.setProperty",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "property_name", "value"],
        "properties": {
            "object_ref":    {"type": "string"},
            "property_name": {"type": "string"},
            "value":         {},
            "platform":      {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "dry_run":       {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["property", "value"],
        "properties": {"property": {"type": "string"}, "value": {}},
    })),
    "mock_response": {"success": True, "data": {"property": "Volume", "value": -6.0}, "error": None},
},

"wwise_set_name": {
    "tool": "wwise_set_name",
    "waapi_uri": "ak.wwise.core.object.setName",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "new_name"],
        "properties": {
            "object_ref": {"type": "string"},
            "new_name":   {"type": "string"},
            "dry_run":    {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["new_name"],
        "properties": {"new_name": {"type": "string"}},
    })),
    "mock_response": {"success": True, "data": {"new_name": MOCK_NAME}, "error": None},
},

"wwise_set_notes": {
    "tool": "wwise_set_notes",
    "waapi_uri": "ak.wwise.core.object.setNotes",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "notes"],
        "properties": {
            "object_ref": {"type": "string"},
            "notes":      {"type": "string"},
            "dry_run":    {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["notes"],
        "properties": {"notes": {"type": "string"}},
    })),
    "mock_response": {"success": True, "data": {"notes": "dry run note"}, "error": None},
},

"wwise_set_object": {
    "tool": "wwise_set_object",
    "waapi_uri": "ak.wwise.core.object.set",
    "input_schema": {
        "type": "object",
        "required": ["objects"],
        "properties": {
            "objects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["object"],
                    "properties": {
                        "object": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "children": {"type": "array"},
                        "platform": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                        "notes": {"type": "string"},
                        "listMode": {"type": "string", "enum": ["replaceAll", "append"]},
                        "onNameConflict": {"type": "string", "enum": ["rename", "replace", "fail", "merge"]},
                        "import": {"type": "object"},
                    },
                    "patternProperties": {"^@[:_a-zA-Z0-9]+$": {}},
                    "additionalProperties": False,
                },
                "minItems": 1,
            },
            "dry_run": {"type": "boolean"},
            "strict": {"type": "boolean"},
            "autofix": {"type": "boolean"},
        },
        "additionalProperties": False,
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["updated"],
        "properties": {
            "updated": {"type": "integer", "minimum": 1},
            "normalizations_applied": {"type": "array", "items": {"type": "string"}},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
    })),
    "mock_response": {"success": True, "data": {"updated": 1}, "error": None},
},

"wwise_add_rtpc_binding": {
    "tool": "wwise_add_rtpc_binding",
    "waapi_uri": "ak.wwise.core.object.set",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "property_name", "control_input", "points"],
        "properties": {
            "object_ref": {"type": "string"},
            "property_name": {"type": "string"},
            "control_input": {"type": "string"},
            "points": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "required": ["x", "y", "shape"],
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "shape": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            },
            "rtpc_name": {"type": "string"},
            "notes": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "dry_run": {"type": "boolean"},
        },
        "additionalProperties": False,
    },
    "output_schema": out(NULL_OR({
        "type": "object",
        "required": ["updated", "object_ref", "property_name"],
        "properties": {
            "updated": {"type": "integer", "minimum": 1},
            "object_ref": {"type": "string"},
            "property_name": {"type": "string"},
        },
    })),
    "mock_response": {
        "success": True,
        "data": {"updated": 1, "object_ref": MOCK_ID, "property_name": "OutputBusVolume"},
        "error": None,
    },
},

"wwise_copy_object": {
    "tool": "wwise_copy_object",
    "waapi_uri": "ak.wwise.core.object.copy",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "parent"],
        "properties": {
            "object_ref":       {"type": "string"},
            "parent":           {"type": "string"},
            "on_name_conflict": {"type": "string", "enum": ["rename", "replace", "fail"]},
            "dry_run":          {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR(ID_NAME_OBJ)),
    "mock_response": {"success": True, "data": {"id": MOCK_ID, "name": MOCK_NAME + "_01"}, "error": None},
},

"wwise_move_object": {
    "tool": "wwise_move_object",
    "waapi_uri": "ak.wwise.core.object.move",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "parent"],
        "properties": {
            "object_ref":       {"type": "string"},
            "parent":           {"type": "string"},
            "on_name_conflict": {"type": "string", "enum": ["rename", "replace", "fail"]},
            "dry_run":          {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR(ID_NAME_OBJ)),
    "mock_response": {"success": True, "data": {"id": MOCK_ID, "name": MOCK_NAME}, "error": None},
},

"wwise_set_reference": {
    "tool": "wwise_set_reference",
    "waapi_uri": "ak.wwise.core.object.setReference",
    "input_schema": {
        "type": "object",
        "required": ["object_ref", "reference", "value"],
        "properties": {
            "object_ref": {"type": "string"},
            "reference":  {"type": "string"},
            "value":      {"type": "string"},
            "platform":   {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "dry_run":    {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["reference", "value"],
        "properties": {"reference": {"type": "string"}, "value": {"type": "string"}},
    })),
    "mock_response": {"success": True, "data": {"reference": "Conversion", "value": MOCK_ID}, "error": None},
},

"wwise_save_project": {
    "tool": "wwise_save_project",
    "waapi_uri": "ak.wwise.core.project.save",
    "input_schema": {
        "type": "object",
        "properties": {"dry_run": {"type": "boolean"}},
    },
    "output_schema": out({"type": "null"}),
    "mock_response": {"success": True, "data": None, "error": None},
},

"wwise_create_transport": {
    "tool": "wwise_create_transport",
    "waapi_uri": "ak.wwise.core.transport.create",
    "input_schema": {
        "type": "object",
        "required": ["object_ref"],
        "properties": {
            "object_ref":     {"type": "string"},
            "game_object_id": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
            "dry_run":        {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["transport"],
        "properties": {"transport": {"type": "integer"}},
    })),
    "mock_response": {"success": True, "data": {"transport": 0}, "error": None},
},

"wwise_transport_execute": {
    "tool": "wwise_transport_execute",
    "waapi_uri": "ak.wwise.core.transport.executeAction",
    "input_schema": {
        "type": "object",
        "required": ["object_ref"],
        "properties": {
            "object_ref":    {"type": "string"},
            "action":        {"type": "string", "enum": ["play", "stop", "pause", "resume", "playStop", "seek"]},
            "seek_position": {"oneOf": [{"type": "number"}, {"type": "null"}]},
            "dry_run":       {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["action", "transport"],
        "properties": {"action": {"type": "string"}, "transport": {"type": "integer"}},
    })),
    "mock_response": {"success": True, "data": {"action": "play", "transport": 0}, "error": None},
},

"wwise_import_audio": {
    "tool": "wwise_import_audio",
    "waapi_uri": "ak.wwise.core.audio.import",
    "input_schema": {
        "type": "object",
        "required": ["imports"],
        "properties": {
            "imports": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["audioFile", "objectPath"],
                    "properties": {
                        "audioFile":  {"type": "string"},
                        "objectPath": {"type": "string"},
                    },
                },
                "minItems": 1,
            },
            "import_operation":        {"type": "string"},
            "import_language":         {"type": "string"},
            "default_object_type":     {"type": "string"},
            "default_import_location": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "dry_run":                 {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({
        "type": "object", "required": ["imported"],
        "properties": {"imported": {"type": "array"}},
    })),
    "mock_response": {
        "success": True,
        "data": {"imported": [{"id": MOCK_ID, "name": "_dry_run_import"}]},
        "error": None,
    },
},

"wwise_generate_soundbank": {
    "tool": "wwise_generate_soundbank",
    "waapi_uri": "ak.wwise.core.soundbank.generate",
    "input_schema": {
        "type": "object",
        "properties": {
            "soundbanks":   {"oneOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
            "platforms":    {"oneOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
            "languages":    {"oneOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
            "write_to_disk": {"type": "boolean"},
            "rebuild":       {"type": "boolean"},
            "dry_run":       {"type": "boolean"},
        },
    },
    "output_schema": out(NULL_OR({"type": "object"})),
    "mock_response": {"success": True, "data": {}, "error": None},
},

}  # end CONTRACTS dict


def main():
    for name, contract in CONTRACTS.items():
        path = CONTRACTS_DIR / f"{name}.json"
        path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
    print(f"Written {len(CONTRACTS)} contracts to {CONTRACTS_DIR}")


if __name__ == "__main__":
    main()
