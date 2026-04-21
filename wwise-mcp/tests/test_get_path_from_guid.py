import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tools.get_path_from_guid import wwise_get_path_from_guid
from tests.conftest import TEST_PARENT


# ---------------------------------------------------------------------------
# dry_run (no Wwise required)
# ---------------------------------------------------------------------------

@pytest.mark.no_waapi
def test_dry_run_returns_mock():
    r = wwise_get_path_from_guid(guid="{AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE}", dry_run=True)
    assert r["success"], r["error"]
    assert isinstance(r["data"], dict)
    assert "guid" in r["data"]
    assert "path" in r["data"]


# ---------------------------------------------------------------------------
# live tests (Wwise required)
# ---------------------------------------------------------------------------

def test_valid_guid_returns_path(test_sound):
    r = wwise_get_path_from_guid(guid=test_sound["id"])
    assert r["success"], r["error"]
    # Path root varies by Wwise version (e.g. "Actor-Mixer Hierarchy" vs "Containers")
    assert r["data"]["path"].endswith(f"\\MCP_Tests\\{test_sound['name']}")
    assert r["data"]["guid"] == test_sound["id"]


def test_unknown_guid_returns_failure():
    r = wwise_get_path_from_guid(guid="{00000000-0000-0000-0000-000000000000}")
    assert not r["success"]
    assert r["error"]


@pytest.mark.no_waapi
def test_empty_guid_returns_failure():
    r = wwise_get_path_from_guid(guid="")
    assert not r["success"]
    assert r["error"]
