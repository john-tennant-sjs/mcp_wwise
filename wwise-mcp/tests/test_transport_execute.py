import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.transport_execute import wwise_transport_execute


def test_play_stop(test_sound):
    r = wwise_transport_execute(test_sound["id"], action="play")
    assert r["success"], r["error"]
    assert r["data"]["action"] == "play"


def test_play_by_path(test_sound):
    r = wwise_transport_execute(test_sound["path"], action="play")
    assert r["success"], r["error"]


def test_invalid_action(test_sound):
    r = wwise_transport_execute(test_sound["id"], action="explode")
    assert not r["success"]


def test_invalid_object():
    r = wwise_transport_execute("\\NonExistent\\Sound", action="play")
    assert not r["success"]
