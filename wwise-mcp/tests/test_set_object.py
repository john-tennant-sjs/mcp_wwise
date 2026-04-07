import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.set_object import wwise_set_object
from tools.set_property import wwise_set_property


def test_set_object_single(test_sound):
    r = wwise_set_object([
        {"object": test_sound["id"], "@Volume": -6.0, "@Pitch": 100}
    ])
    assert r["success"], r["error"]
    assert r["data"]["updated"] == 1


def test_set_object_empty_list():
    r = wwise_set_object([])
    assert not r["success"]


def test_set_object_missing_object_key():
    r = wwise_set_object([{"@Volume": -3.0}])
    assert not r["success"]


def test_set_object_nonexistent():
    r = wwise_set_object([{"object": "\\NonExistent\\Path", "@Volume": 0.0}])
    assert not r["success"]


def test_set_object_rejects_missing_at_fields_in_strict_mode():
    r = wwise_set_object(
        [{"object": "{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}", "PropertyName": "Bypass"}],
        dry_run=True,
    )
    assert not r["success"]
    assert "@PropertyName" in r["error"] or "@PropertyName" in (r.get("suggestion") or "")


def test_set_object_autofix_normalizes_common_rtpc_keys():
    r = wwise_set_object(
        [
            {
                "object": "{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}",
                "RTPC": [
                    {
                        "type": "RTPC",
                        "name": "",
                        "PropertyName": "Bypass",
                        "ControlInput": "{BBBBBBBB-CCCC-DDDD-EEEE-FFFFFFFFFFFF}",
                        "Curve": {
                            "type": "Curve",
                            "Points": [
                                {"x": 0, "y": 0, "shape": "Constant"},
                                {"x": 1, "y": 1, "shape": "Constant"},
                            ],
                        },
                    }
                ],
            }
        ],
        dry_run=True,
        autofix=True,
    )
    assert r["success"], r["error"]
    assert r["data"]["updated"] == 1
    assert r["data"].get("normalizations_applied")


def test_set_property_input_schema_violation_is_returned():
    r = wwise_set_property("\\Actor-Mixer Hierarchy", "Volume", -3.0, platform=123)
    assert not r["success"]
    assert "input schema violation" in r["error"]
