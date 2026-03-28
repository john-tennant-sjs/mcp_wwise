import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from waapi import WaapiClient
from tools.set_name import wwise_set_name
from tests.conftest import TEST_PARENT, WAAPI_URL


def test_set_name_by_id(test_sound):
    r = wwise_set_name(test_sound["id"], "_renamed_sound")
    assert r["success"], r["error"]
    assert r["data"]["new_name"] == "_renamed_sound"
    # Rename back so fixture teardown (which uses original id) works
    wwise_set_name(test_sound["id"], "_test_sound")


def test_set_name_by_path(test_sound):
    r = wwise_set_name(test_sound["path"], "_renamed_by_path")
    assert r["success"], r["error"]
    # Rename back
    wwise_set_name(test_sound["id"], "_test_sound")


def test_set_name_nonexistent():
    r = wwise_set_name("\\NonExistent\\Path\\Obj", "new_name")
    assert not r["success"]
