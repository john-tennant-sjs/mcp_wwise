import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waapi import WaapiClient
from tools.move_object import wwise_move_object
from tests.conftest import TEST_PARENT, DEFAULT_WORK_UNIT, WAAPI_URL


def _create(name, parent=TEST_PARENT):
    with WaapiClient(url=WAAPI_URL) as c:
        r = c.call("ak.wwise.core.object.create", {
            "parent": parent, "type": "Sound",
            "name": name, "onNameConflict": "replace",
        })
        return r["id"]


def _delete(obj_id):
    with WaapiClient(url=WAAPI_URL) as c:
        c.call("ak.wwise.core.object.delete", {"object": obj_id})


def test_move_to_different_parent(test_actor_mixer):
    # Create a Sound at TEST_PARENT, then move it into the test ActorMixer
    obj_id = _create("_tm_sound")
    r = wwise_move_object(obj_id, test_actor_mixer["id"])
    assert r["success"], r["error"]
    assert r["data"]["id"] == obj_id
    _delete(obj_id)


def test_move_nonexistent():
    r = wwise_move_object("\\NonExistent\\Object", TEST_PARENT)
    assert not r["success"]


def test_move_invalid_parent(test_sound):
    r = wwise_move_object(test_sound["id"], "\\NonExistent\\Parent")
    assert not r["success"]
