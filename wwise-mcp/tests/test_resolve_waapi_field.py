import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.resolve_waapi_field import normalize_label, wwise_resolve_waapi_field

ROOT = os.path.join(os.path.dirname(__file__), "..", "reference", "wobject_waapi_names_2023_1_17.json")


def test_normalize_label_collapses_space():
    assert normalize_label("  Output   Bus  ") == "output bus"


def test_resolve_output_bus_sound_offline():
    r = wwise_resolve_waapi_field(
        object_type="Sound",
        user_label="output bus",
        use_live_validation=False,
    )
    assert r["success"], r["error"]
    d = r["data"]
    assert d["waapi_name"] == "OutputBus"
    assert d["kind"] == "reference"
    assert d["suggested_tool"] == "wwise_set_reference"
    assert d["source"] == "alias"
    assert d["class_id"] is None


def test_resolve_exact_canonical_property():
    r = wwise_resolve_waapi_field(
        object_type="Sound",
        user_label="Volume",
        use_live_validation=False,
    )
    assert r["success"], r["error"]
    assert r["data"]["waapi_name"] == "Volume"
    assert r["data"]["kind"] == "property"
    assert r["data"]["suggested_tool"] == "wwise_set_property"
    assert r["data"]["source"] == "exact_match"


def test_resolve_dry_run():
    r = wwise_resolve_waapi_field(object_type="Sound", user_label="x", dry_run=True)
    assert r["success"], r["error"]
    assert r["data"]["waapi_name"] == "OutputBus"


def test_resolve_missing_user_label():
    r = wwise_resolve_waapi_field(object_type="Sound", user_label="", use_live_validation=False)
    assert not r["success"]


def test_resolve_unknown_type_offline():
    r = wwise_resolve_waapi_field(
        object_type="NotARealWwiseType",
        user_label="volume",
        use_live_validation=False,
    )
    assert not r["success"]


def test_bundle_display_aliases_align_with_lists():
    with open(ROOT, encoding="utf-8") as f:
        bundle = json.load(f)
    for type_name, entry in bundle.items():
        if type_name.startswith("_") or not isinstance(entry, dict):
            continue
        aliases = entry.get("display_aliases") or {}
        props = set(entry.get("property_names") or [])
        refs = set(entry.get("reference_names") or [])
        for key, row in aliases.items():
            assert key == key.strip().lower()
            assert " " not in key or key == " ".join(key.split())
            wname = row["waapi_name"]
            kind = row["kind"]
            assert kind in ("property", "reference")
            if kind == "property":
                assert wname in props
            else:
                assert wname in refs
