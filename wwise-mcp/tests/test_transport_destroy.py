"""
Transport objects are session-scoped: they exist only while the WAAPI connection
that created them is open. Since each tool call opens/closes its own connection,
a transport created by wwise_create_transport is already gone by the time
wwise_transport_destroy tries to use a new connection.
These tests verify contract, validation, and error behaviour.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.transport_destroy import wwise_transport_destroy


def test_transport_destroy_stale_id(test_sound):
    """A transport ID from a closed session is unknown — expect graceful failure."""
    from tools.create_transport import wwise_create_transport
    ct = wwise_create_transport(test_sound["id"])
    assert ct["success"], ct["error"]
    # The connection that created the transport is now closed; transport is gone.
    transport_id = ct["data"]["transport"]
    r = wwise_transport_destroy(transport_id)
    assert not r["success"]  # "Unknown transport object."


def test_transport_destroy_invalid_id():
    r = wwise_transport_destroy(-1)
    assert not r["success"]


def test_transport_destroy_dry_run():
    r = wwise_transport_destroy(0, dry_run=True)
    assert r["success"]
