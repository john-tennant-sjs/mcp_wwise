import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.get_info import wwise_get_info


def test_get_info_live():
    r = wwise_get_info()
    assert r["success"], r["error"]
    assert "version" in r["data"]
    assert isinstance(r["data"]["version"], dict)


def test_get_info_dry_run():
    r = wwise_get_info(dry_run=True)
    assert r["success"]
    assert "version" in r["data"]
