import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waapi import WaapiClient
from tools.copy_object import wwise_copy_object
from tests.conftest import TEST_PARENT, WAAPI_URL


def _delete(obj_id):
    with WaapiClient(url=WAAPI_URL) as c:
        c.call("ak.wwise.core.object.delete", {"object": obj_id})


def test_copy_sound(test_sound):
    r = wwise_copy_object(test_sound["id"], TEST_PARENT, on_name_conflict="rename")
    assert r["success"], r["error"]
    assert r["data"]["id"] != test_sound["id"]
    _delete(r["data"]["id"])


def test_copy_invalid_source():
    r = wwise_copy_object("\\NonExistent\\Source", TEST_PARENT)
    assert not r["success"]


def test_copy_invalid_parent(test_sound):
    r = wwise_copy_object(test_sound["id"], "\\NonExistent\\Parent")
    assert not r["success"]
