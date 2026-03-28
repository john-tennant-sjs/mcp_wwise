import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.get_schema import wwise_get_schema


def test_get_schema_known_uri():
    r = wwise_get_schema("ak.wwise.core.object.get")
    assert r["success"], r["error"]
    assert "argsSchema" in r["data"]


def test_get_schema_empty_uri():
    r = wwise_get_schema("")
    assert not r["success"]


def test_get_schema_unknown_uri():
    r = wwise_get_schema("ak.wwise.core.nonexistent.command")
    assert not r["success"]


def test_get_schema_dry_run():
    r = wwise_get_schema("ak.wwise.core.object.get", dry_run=True)
    assert r["success"]
    assert "argsSchema" in r["data"]
