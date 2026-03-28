import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.set_object import wwise_set_object


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
