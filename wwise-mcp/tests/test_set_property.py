import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.set_property import wwise_set_property


def test_set_volume(test_sound):
    r = wwise_set_property(test_sound["id"], "Volume", -12.0)
    assert r["success"], r["error"]
    assert r["data"]["property"] == "Volume"


def test_set_pitch(test_sound):
    r = wwise_set_property(test_sound["id"], "Pitch", 200)
    assert r["success"], r["error"]


def test_set_loop_enabled(test_sound):
    r = wwise_set_property(test_sound["id"], "IsLoopingEnabled", True)
    assert r["success"], r["error"]


def test_set_invalid_object():
    r = wwise_set_property("\\NonExistent\\Path", "Volume", 0.0)
    assert not r["success"]
