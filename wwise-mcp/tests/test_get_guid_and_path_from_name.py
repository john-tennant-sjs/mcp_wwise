import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tools.get_guid_and_path_from_name import wwise_get_guid_and_path_from_name
from tests.conftest import TEST_PARENT


# ---------------------------------------------------------------------------
# dry_run (no Wwise required)
# ---------------------------------------------------------------------------

def test_dry_run_returns_mock():
    r = wwise_get_guid_and_path_from_name(name="_dry_run_object", dry_run=True)
    assert r["success"], r["error"]
    assert isinstance(r["data"], list)
    assert len(r["data"]) >= 1
    assert "id" in r["data"][0]
    assert "path" in r["data"][0]


# ---------------------------------------------------------------------------
# live tests (Wwise required)
# ---------------------------------------------------------------------------

def test_exact_name_hit_returns_guid_and_path(test_sound):
    r = wwise_get_guid_and_path_from_name(name=test_sound["name"])
    assert r["success"], r["error"]
    assert isinstance(r["data"], list)
    assert len(r["data"]) >= 1
    match = next((o for o in r["data"] if o["id"] == test_sound["id"]), None)
    assert match is not None, "Expected to find the test sound in results"
    assert "path" in match
    # Path root varies by Wwise version (e.g. "Actor-Mixer Hierarchy" vs "Containers")
    assert match["path"].endswith(f"\\MCP_Tests\\{test_sound['name']}")


def test_exact_name_returns_both_guid_and_path_fields(test_sound):
    r = wwise_get_guid_and_path_from_name(name=test_sound["name"])
    assert r["success"], r["error"]
    for obj in r["data"]:
        assert "id" in obj
        assert "path" in obj


def test_missing_name_returns_empty_list():
    r = wwise_get_guid_and_path_from_name(name="__no_such_object_xyzzy__")
    assert r["success"], r["error"]
    assert r["data"] == []


def test_empty_name_returns_failure():
    r = wwise_get_guid_and_path_from_name(name="")
    assert not r["success"]
    assert r["error"]
