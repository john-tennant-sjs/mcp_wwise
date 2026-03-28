import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waapi import WaapiClient
from tools.delete_object import wwise_delete_object
from tests.conftest import TEST_PARENT, WAAPI_URL


def _create(name):
    with WaapiClient(url=WAAPI_URL) as c:
        r = c.call("ak.wwise.core.object.create", {
            "parent": TEST_PARENT, "type": "Sound",
            "name": name, "onNameConflict": "replace",
        })
        return r["id"]


def test_delete_by_path():
    _create("_td_sound")
    r = wwise_delete_object(f"{TEST_PARENT}\\_td_sound")
    assert r["success"], r["error"]


def test_delete_by_guid():
    obj_id = _create("_td_by_guid")
    r = wwise_delete_object(obj_id)
    assert r["success"], r["error"]


def test_delete_nonexistent():
    r = wwise_delete_object("\\Actor-Mixer Hierarchy\\Default Work Unit\\__does_not_exist__")
    assert not r["success"]
