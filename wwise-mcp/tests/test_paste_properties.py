import sys, os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.paste_properties import wwise_paste_properties


def test_paste_properties_same_type(test_sound, test_sound2):
    r = wwise_paste_properties(test_sound["path"], [test_sound2["path"]])
    assert r["success"], r["error"]


def test_paste_properties_nonexistent_source():
    r = wwise_paste_properties("\\NonExistent\\Source", ["\\Actor-Mixer Hierarchy\\Default Work Unit"])
    assert not r["success"]


@pytest.mark.no_waapi
def test_paste_properties_empty_source():
    r = wwise_paste_properties("", ["\\some\\target"])
    assert not r["success"]


@pytest.mark.no_waapi
def test_paste_properties_empty_targets():
    r = wwise_paste_properties("\\some\\source", [])
    assert not r["success"]


@pytest.mark.no_waapi
def test_paste_properties_invalid_mode():
    r = wwise_paste_properties("\\some\\source", ["\\target"], paste_mode="badMode")
    assert not r["success"]


@pytest.mark.no_waapi
def test_paste_properties_dry_run():
    r = wwise_paste_properties("\\source", ["\\target"], dry_run=True)
    assert r["success"]
