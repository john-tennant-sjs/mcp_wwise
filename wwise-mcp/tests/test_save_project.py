import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.save_project import wwise_save_project


def test_save_project():
    r = wwise_save_project()
    assert r["success"], r["error"]
    assert r["error"] is None
