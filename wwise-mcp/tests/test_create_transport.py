import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.create_transport import wwise_create_transport


def test_create_transport_sound(test_sound):
    r = wwise_create_transport(test_sound["id"])
    assert r["success"], r["error"]
    assert isinstance(r["data"]["transport"], int)


def test_create_transport_by_path(test_sound):
    r = wwise_create_transport(test_sound["path"])
    assert r["success"], r["error"]


def test_create_transport_nonexistent():
    r = wwise_create_transport("\\NonExistent\\Sound")
    assert not r["success"]
