"""
conftest.py — shared pytest fixtures for Phase 2 live tests.

IMPORTANT: WAAPI allows only one connection per process at a time.
Fixtures open a connection, do setup/teardown, and CLOSE it before yielding.
Tool functions then open their own connection during the test body.

When WAAPI is not reachable (e.g. GitHub Actions without Wwise), tests that are
not marked ``@pytest.mark.no_waapi`` are skipped — see ``pytest_collection_modifyitems``.
"""

from __future__ import annotations

import pytest
from waapi import WaapiClient

WAAPI_URL = "ws://127.0.0.1:9000/waapi"
TEST_PARENT = "\\Actor-Mixer Hierarchy\\Default Work Unit\\MCP_Tests"
DEFAULT_WORK_UNIT = "\\Actor-Mixer Hierarchy\\Default Work Unit"


def _waapi_reachable() -> bool:
    try:
        with WaapiClient(url=WAAPI_URL) as client:
            r = client.call(
                "ak.wwise.core.object.get",
                {
                    "from": {"path": [DEFAULT_WORK_UNIT]},
                    "options": {"return": ["id"]},
                },
            )
            return r is not None
    except Exception:
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    if getattr(config.option, "collectonly", False):
        return
    if getattr(config, "_waapi_reachable", None) is None:
        config._waapi_reachable = _waapi_reachable()
    if config._waapi_reachable:
        return
    skip_unmarked = pytest.mark.skip(
        reason="WAAPI not reachable (no Wwise / WAAPI on ws://127.0.0.1:9000). "
        "Open the test project in Wwise locally to run integration tests.",
    )
    for item in items:
        if item.get_closest_marker("no_waapi"):
            continue
        item.add_marker(skip_unmarked)


@pytest.fixture(scope="session")
def ensure_mcp_tests_container():
    """Ensure the MCP_Tests ActorMixer exists before any tests run."""
    with WaapiClient(url=WAAPI_URL) as client:
        existing = client.call(
            "ak.wwise.core.object.get",
            {"from": {"path": [TEST_PARENT]}, "options": {"return": ["id"]}},
        )
        if not (existing and existing.get("return")):
            client.call("ak.wwise.core.object.create", {
                "parent": DEFAULT_WORK_UNIT,
                "type": "ActorMixer",
                "name": "MCP_Tests",
                "onNameConflict": "merge",
            })
    # Connection is CLOSED before yielding — tools can now connect freely.
    yield


@pytest.fixture
def test_sound(ensure_mcp_tests_container):
    """
    Create a temporary Sound inside MCP_Tests.
    Connection is closed before yielding so tool functions can connect.
    Yields {"id": ..., "name": ..., "path": ...}.
    """
    obj_id = None
    with WaapiClient(url=WAAPI_URL) as client:
        result = client.call("ak.wwise.core.object.create", {
            "parent": TEST_PARENT,
            "type": "Sound",
            "name": "_test_sound",
            "onNameConflict": "replace",
        })
        assert result and result.get("id"), "Could not create test Sound"
        obj_id = result["id"]
    # Connection closed — test body runs here
    yield {"id": obj_id, "name": "_test_sound", "path": f"{TEST_PARENT}\\_test_sound"}
    # Teardown: open a fresh connection to delete
    with WaapiClient(url=WAAPI_URL) as client:
        client.call("ak.wwise.core.object.delete", {"object": obj_id})


@pytest.fixture
def test_sound2(ensure_mcp_tests_container):
    """
    A second temporary Sound for tests that need two objects.
    Connection is closed before yielding.
    """
    obj_id = None
    with WaapiClient(url=WAAPI_URL) as client:
        result = client.call("ak.wwise.core.object.create", {
            "parent": TEST_PARENT,
            "type": "Sound",
            "name": "_test_sound2",
            "onNameConflict": "replace",
        })
        assert result and result.get("id"), "Could not create test Sound2"
        obj_id = result["id"]
    yield {"id": obj_id, "name": "_test_sound2", "path": f"{TEST_PARENT}\\_test_sound2"}
    with WaapiClient(url=WAAPI_URL) as client:
        client.call("ak.wwise.core.object.delete", {"object": obj_id})


@pytest.fixture
def test_actor_mixer(ensure_mcp_tests_container):
    """
    Create a temporary ActorMixer inside MCP_Tests.
    Connection is closed before yielding.
    """
    obj_id = None
    with WaapiClient(url=WAAPI_URL) as client:
        result = client.call("ak.wwise.core.object.create", {
            "parent": TEST_PARENT,
            "type": "ActorMixer",
            "name": "_test_am",
            "onNameConflict": "replace",
        })
        assert result and result.get("id"), "Could not create test ActorMixer"
        obj_id = result["id"]
    yield {"id": obj_id, "name": "_test_am", "path": f"{TEST_PARENT}\\_test_am"}
    with WaapiClient(url=WAAPI_URL) as client:
        client.call("ak.wwise.core.object.delete", {"object": obj_id})
