"""
Tests for attenuation curve get/set.
Requires an Attenuation object in the project; creates one in MCP_Tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waapi import WaapiClient

from tools.get_attenuation_curve import wwise_get_attenuation_curve
from tools.set_attenuation_curve import wwise_set_attenuation_curve

WAAPI_URL = "ws://127.0.0.1:9000/waapi"
ATTN_PARENT = "\\Attenuations\\Default Work Unit"


def _create_attenuation():
    with WaapiClient(url=WAAPI_URL) as c:
        r = c.call("ak.wwise.core.object.create", {
            "parent": ATTN_PARENT,
            "type": "Attenuation",
            "name": "_test_attn",
            "onNameConflict": "replace"
        })
        if r:
            return r["id"], f"{ATTN_PARENT}\\_test_attn"
    return None, None


def _delete_obj(obj_id):
    with WaapiClient(url=WAAPI_URL) as c:
        c.call("ak.wwise.core.object.delete", {"object": obj_id})


def test_get_attenuation_curve_live():
    attn_id, attn_path = _create_attenuation()
    if attn_id is None:
        import pytest; pytest.skip("Could not create Attenuation object")
    try:
        r = wwise_get_attenuation_curve(attn_path, "VolumeDryUsage")
        assert r["success"], r["error"]
        assert "points" in r["data"]
        assert "use" in r["data"]
    finally:
        _delete_obj(attn_id)


def test_set_attenuation_curve_live():
    attn_id, attn_path = _create_attenuation()
    if attn_id is None:
        import pytest; pytest.skip("Could not create Attenuation object")
    try:
        points = [
            {"x": 0.0, "y": 0.0, "shape": "Linear"},
            {"x": 50.0, "y": -6.0, "shape": "Linear"},
            {"x": 100.0, "y": -200.0, "shape": "Linear"},
        ]
        r = wwise_set_attenuation_curve(attn_path, "VolumeDryUsage", "Custom", points)
        assert r["success"], r["error"]
    finally:
        _delete_obj(attn_id)


def test_get_attenuation_curve_invalid_type():
    r = wwise_get_attenuation_curve("\\some\\path", "InvalidCurveType")
    assert not r["success"]


def test_set_attenuation_curve_invalid_use():
    r = wwise_set_attenuation_curve("\\p", "VolumeDryUsage", "BadUse", [{"x": 0, "y": 0, "shape": "Linear"}])
    assert not r["success"]


def test_get_attenuation_curve_dry_run():
    r = wwise_get_attenuation_curve("\\Attenuations\\Default Work Unit\\_test", "VolumeDryUsage", dry_run=True)
    assert r["success"]
    assert "points" in r["data"]


def test_set_attenuation_curve_dry_run():
    r = wwise_set_attenuation_curve(
        "\\Attenuations\\Default Work Unit\\_test", "VolumeDryUsage", "Custom",
        [{"x": 0, "y": 0, "shape": "Linear"}], dry_run=True
    )
    assert r["success"]
