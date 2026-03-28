"""Write all 15 Phase 2 response schema files to tests/schemas/."""
import json
from pathlib import Path

SCHEMAS_DIR = Path(__file__).parent.parent / "tests" / "schemas"
SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)

SUCCESS_ERROR = {
    "success": {"type": "boolean"},
    "error": {"type": ["string", "null"]},
}


def schema(data_schema):
    return {
        "type": "object",
        "required": ["success", "data", "error"],
        "properties": {**SUCCESS_ERROR, "data": data_schema},
    }


NULL_OR = lambda s: {"oneOf": [s, {"type": "null"}]}
ID_NAME = {"type": "object", "required": ["id", "name"],
           "properties": {"id": {"type": "string"}, "name": {"type": "string"}}}

SCHEMAS = {
    "wwise_get_object": schema(NULL_OR({
        "type": "array",
        "items": {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}},
    })),
    "wwise_create_object": schema(NULL_OR(ID_NAME)),
    "wwise_delete_object": schema(NULL_OR({
        "type": "object", "required": ["deleted"],
        "properties": {"deleted": {"type": "string"}},
    })),
    "wwise_set_property": schema(NULL_OR({
        "type": "object", "required": ["property", "value"],
        "properties": {"property": {"type": "string"}, "value": {}},
    })),
    "wwise_set_name": schema(NULL_OR({
        "type": "object", "required": ["new_name"],
        "properties": {"new_name": {"type": "string"}},
    })),
    "wwise_set_notes": schema(NULL_OR({
        "type": "object", "required": ["notes"],
        "properties": {"notes": {"type": "string"}},
    })),
    "wwise_set_object": schema(NULL_OR({
        "type": "object", "required": ["updated"],
        "properties": {"updated": {"type": "integer"}},
    })),
    "wwise_copy_object": schema(NULL_OR(ID_NAME)),
    "wwise_move_object": schema(NULL_OR(ID_NAME)),
    "wwise_set_reference": schema(NULL_OR({
        "type": "object", "required": ["reference", "value"],
        "properties": {"reference": {"type": "string"}, "value": {"type": "string"}},
    })),
    "wwise_save_project": schema({"type": "null"}),
    "wwise_create_transport": schema(NULL_OR({
        "type": "object", "required": ["transport"],
        "properties": {"transport": {"type": "integer"}},
    })),
    "wwise_transport_execute": schema(NULL_OR({
        "type": "object", "required": ["action", "transport"],
        "properties": {"action": {"type": "string"}, "transport": {"type": "integer"}},
    })),
    "wwise_import_audio": schema(NULL_OR({
        "type": "object", "required": ["imported"],
        "properties": {"imported": {"type": "array"}},
    })),
    "wwise_generate_soundbank": schema(NULL_OR({"type": "object"})),
}

for name, s in SCHEMAS.items():
    (SCHEMAS_DIR / f"{name}_response.json").write_text(json.dumps(s, indent=2))

print(f"Written {len(SCHEMAS)} schema files to {SCHEMAS_DIR}")
