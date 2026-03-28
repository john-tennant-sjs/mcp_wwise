import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.transport_prepare import wwise_transport_prepare


def test_transport_prepare_sound(test_sound):
    r = wwise_transport_prepare(test_sound["id"])
    assert r["success"], r["error"]


def test_transport_prepare_nonexistent():
    r = wwise_transport_prepare("\\NonExistent\\Path")
    assert not r["success"]


def test_transport_prepare_empty_ref():
    r = wwise_transport_prepare("")
    assert not r["success"]


def test_transport_prepare_dry_run():
    r = wwise_transport_prepare("\\some\\path", dry_run=True)
    assert r["success"]
