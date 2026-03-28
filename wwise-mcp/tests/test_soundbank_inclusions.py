"""
Tests for soundbank get/set inclusions.
Uses the Default SoundBank if available.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waapi import WaapiClient

from tools.soundbank_get_inclusions import wwise_soundbank_get_inclusions
from tools.soundbank_set_inclusions import wwise_soundbank_set_inclusions

WAAPI_URL = "ws://127.0.0.1:9000/waapi"


def _get_default_soundbank_path():
    with WaapiClient(url=WAAPI_URL) as c:
        r = c.call("ak.wwise.core.object.get", {
            "from": {"ofType": ["SoundBank"]},
            "options": {"return": ["id", "name", "path"]}
        })
        if r and r.get("return"):
            return r["return"][0]["path"]
    return None


def test_soundbank_get_inclusions_live():
    sb_path = _get_default_soundbank_path()
    if sb_path is None:
        import pytest; pytest.skip("No SoundBank found in project")
    r = wwise_soundbank_get_inclusions(sb_path)
    assert r["success"], r["error"]
    assert isinstance(r["data"]["inclusions"], list)


def test_soundbank_get_inclusions_nonexistent():
    r = wwise_soundbank_get_inclusions("\\SoundBanks\\NonExistent")
    assert not r["success"]


def test_soundbank_get_inclusions_empty_ref():
    r = wwise_soundbank_get_inclusions("")
    assert not r["success"]


def test_soundbank_get_inclusions_dry_run():
    r = wwise_soundbank_get_inclusions("\\SoundBanks\\Default Work Unit\\Init", dry_run=True)
    assert r["success"]
    assert isinstance(r["data"]["inclusions"], list)


def test_soundbank_set_inclusions_invalid_operation():
    r = wwise_soundbank_set_inclusions(
        "\\SoundBanks\\Default Work Unit\\Init",
        inclusions=[{"object": "\\Actor-Mixer Hierarchy\\Default Work Unit", "filter": ["events"]}],
        operation="invalid"
    )
    assert not r["success"]


def test_soundbank_set_inclusions_empty_list():
    r = wwise_soundbank_set_inclusions("\\sb", inclusions=[])
    assert not r["success"]


def test_soundbank_set_inclusions_dry_run():
    r = wwise_soundbank_set_inclusions(
        "\\SoundBanks\\Default Work Unit\\Init",
        inclusions=[{"object": "\\Actor-Mixer Hierarchy\\Default Work Unit", "filter": ["events"]}],
        dry_run=True
    )
    assert r["success"]
