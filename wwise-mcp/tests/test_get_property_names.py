import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.get_property_names import wwise_get_property_names


def test_get_property_names_dry_run():
    r = wwise_get_property_names(object_type="Sound", dry_run=True)
    assert r["success"], r["error"]
    assert r["data"]["class_id"]
    assert "Volume" in r["data"]["names"]


def test_get_property_names_class_id_dry_run():
    r = wwise_get_property_names(class_id=65552, dry_run=True)
    assert r["success"]


def test_get_property_names_missing_args():
    r = wwise_get_property_names()
    assert not r["success"]
