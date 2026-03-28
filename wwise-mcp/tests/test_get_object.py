import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tools.get_object import wwise_get_object
from tests.conftest import TEST_PARENT, DEFAULT_WORK_UNIT


def test_get_object_by_path():
    r = wwise_get_object(from_path=[DEFAULT_WORK_UNIT])
    assert r["success"], r["error"]
    assert isinstance(r["data"], list)
    assert len(r["data"]) >= 1
    assert all("id" in o for o in r["data"])


def test_get_object_multiple_props(test_sound):
    r = wwise_get_object(
        from_path=[test_sound["path"]],
        return_props=["id", "name", "type", "path", "@Volume"],
    )
    assert r["success"], r["error"]
    obj = r["data"][0]
    assert obj["type"] == "Sound"
    assert "@Volume" in obj


def test_get_object_missing_path():
    # WAAPI returns None for non-existent paths — tool maps this to success=False
    r = wwise_get_object(from_path=["\\NonExistent\\Path\\Here"])
    assert not r["success"]


def test_get_object_no_args():
    r = wwise_get_object()
    assert not r["success"]
    assert r["error"]
