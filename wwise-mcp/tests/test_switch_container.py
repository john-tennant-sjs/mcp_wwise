"""
Tests for Switch Container assignment tools.
Requires a SwitchContainer with a Switch Group assigned to it.
Since these are complex to set up fully (need Switch Group + Switch values),
most live tests verify the error path; we also test dry_run and get_assignments
on an existing SwitchContainer.
"""
import sys, os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waapi import WaapiClient

from tools.switch_container_get_assignments import wwise_switch_container_get_assignments
from tools.switch_container_add_assignment import wwise_switch_container_add_assignment
from tools.switch_container_remove_assignment import wwise_switch_container_remove_assignment

WAAPI_URL = "ws://127.0.0.1:9000/waapi"
TEST_PARENT = "\\Actor-Mixer Hierarchy\\Default Work Unit\\MCP_Tests"


def _create_switch_container():
    """Create a temporary SwitchContainer and return (sc_id, sc_path, child_id)."""
    sc_id = sc_path = child_id = None
    with WaapiClient(url=WAAPI_URL) as c:
        sc = c.call("ak.wwise.core.object.create", {
            "parent": TEST_PARENT, "type": "SwitchContainer",
            "name": "_test_sc", "onNameConflict": "replace"
        })
        if sc:
            sc_id = sc["id"]
            sc_path = f"{TEST_PARENT}\\_test_sc"
            snd = c.call("ak.wwise.core.object.create", {
                "parent": sc_path, "type": "Sound",
                "name": "_test_sc_snd", "onNameConflict": "replace"
            })
            if snd:
                child_id = snd["id"]
    return sc_id, sc_path, child_id


def _delete_obj(obj_id):
    with WaapiClient(url=WAAPI_URL) as c:
        c.call("ak.wwise.core.object.delete", {"object": obj_id})


def test_switch_container_get_assignments_empty():
    sc_id, sc_path, child_id = _create_switch_container()
    try:
        r = wwise_switch_container_get_assignments(sc_path)
        assert r["success"], r["error"]
        assert isinstance(r["data"]["assignments"], list)
        assert r["data"]["assignments"] == []
    finally:
        if sc_id:
            _delete_obj(sc_id)


def test_switch_container_get_assignments_nonexistent():
    r = wwise_switch_container_get_assignments("\\NonExistent\\SC")
    assert not r["success"]


def test_switch_container_add_assignment_bad_refs():
    # Both child and state_or_switch don't exist — expect failure
    r = wwise_switch_container_add_assignment("\\Bad\\Child", "\\Bad\\State")
    assert not r["success"]


def test_switch_container_remove_assignment_bad_refs():
    r = wwise_switch_container_remove_assignment("\\Bad\\Child", "\\Bad\\State")
    assert not r["success"]


@pytest.mark.no_waapi
def test_switch_container_get_assignments_dry_run():
    r = wwise_switch_container_get_assignments("\\some\\path", dry_run=True)
    assert r["success"]
    assert isinstance(r["data"]["assignments"], list)


@pytest.mark.no_waapi
def test_switch_container_add_assignment_dry_run():
    r = wwise_switch_container_add_assignment("\\child", "\\state", dry_run=True)
    assert r["success"]


@pytest.mark.no_waapi
def test_switch_container_remove_assignment_dry_run():
    r = wwise_switch_container_remove_assignment("\\child", "\\state", dry_run=True)
    assert r["success"]


@pytest.mark.no_waapi
def test_switch_container_add_empty_child():
    r = wwise_switch_container_add_assignment("", "\\state")
    assert not r["success"]


@pytest.mark.no_waapi
def test_switch_container_remove_empty_state():
    r = wwise_switch_container_remove_assignment("\\child", "")
    assert not r["success"]
