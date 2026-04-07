import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.add_rtpc_binding import wwise_add_rtpc_binding


def test_add_rtpc_binding_dry_run_success():
    r = wwise_add_rtpc_binding(
        object_ref="{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}",
        property_name="Bypass",
        control_input="{BBBBBBBB-CCCC-DDDD-EEEE-FFFFFFFFFFFF}",
        points=[
            {"x": 0, "y": 0, "shape": "Constant"},
            {"x": 1, "y": 1, "shape": "Constant"},
        ],
        dry_run=True,
    )
    assert r["success"], r["error"]
    assert r["data"]["updated"] == 1


def test_add_rtpc_binding_schema_validation():
    r = wwise_add_rtpc_binding(
        object_ref="{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}",
        property_name="Bypass",
        control_input="{BBBBBBBB-CCCC-DDDD-EEEE-FFFFFFFFFFFF}",
        points=[{"x": 0, "y": 0}],
        dry_run=True,
    )
    assert not r["success"]
    assert "input schema violation" in r["error"]
