import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from waapi import WaapiClient
from tools.create_object import wwise_create_object
from tests.conftest import TEST_PARENT, WAAPI_URL


def _delete(obj_id):
    with WaapiClient(url=WAAPI_URL) as c:
        c.call("ak.wwise.core.object.delete", {"object": obj_id})


def test_create_sound():
    r = wwise_create_object(TEST_PARENT, "Sound", "_tc_sound", on_name_conflict="replace")
    assert r["success"], r["error"]
    assert r["data"]["id"]
    _delete(r["data"]["id"])


def test_create_actor_mixer():
    r = wwise_create_object(TEST_PARENT, "ActorMixer", "_tc_am", on_name_conflict="replace")
    assert r["success"], r["error"]
    _delete(r["data"]["id"])


def test_create_invalid_parent():
    r = wwise_create_object("\\NonExistent\\Parent", "Sound", "_tc_bad")
    assert not r["success"]


def test_create_name_conflict_fail():
    # Create once
    r1 = wwise_create_object(TEST_PARENT, "Sound", "_tc_conflict", on_name_conflict="replace")
    assert r1["success"]
    # Second create with fail should fail
    r2 = wwise_create_object(TEST_PARENT, "Sound", "_tc_conflict", on_name_conflict="fail")
    assert not r2["success"]
    _delete(r1["data"]["id"])
