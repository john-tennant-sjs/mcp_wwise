import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.ui_get_selected_objects import wwise_ui_get_selected_objects


def test_ui_get_selected_objects_live():
    r = wwise_ui_get_selected_objects()
    assert r["success"], r["error"]
    assert isinstance(r["data"]["objects"], list)


def test_ui_get_selected_objects_custom_props():
    r = wwise_ui_get_selected_objects(return_props=["id", "name"])
    assert r["success"], r["error"]


def test_ui_get_selected_objects_dry_run():
    r = wwise_ui_get_selected_objects(dry_run=True)
    assert r["success"]
    assert isinstance(r["data"]["objects"], list)
