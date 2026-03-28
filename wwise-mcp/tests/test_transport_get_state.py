"""
Transport objects are session-scoped: they exist only while the WAAPI connection
that created them is open. These tests verify contract, validation, and error behaviour.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.create_transport import wwise_create_transport
from tools.transport_get_state import wwise_transport_get_state


def test_transport_get_state_stale_id(test_sound):
    """A transport from a closed session is unknown — expect graceful failure."""
    ct = wwise_create_transport(test_sound["id"])
    assert ct["success"], ct["error"]
    transport_id = ct["data"]["transport"]
    r = wwise_transport_get_state(transport_id)
    assert not r["success"]  # "Unknown transport object."


def test_transport_get_state_invalid_id():
    r = wwise_transport_get_state(-1)
    assert not r["success"]


def test_transport_get_state_dry_run():
    r = wwise_transport_get_state(0, dry_run=True)
    assert r["success"]
    assert r["data"]["state"] == "stopped"
