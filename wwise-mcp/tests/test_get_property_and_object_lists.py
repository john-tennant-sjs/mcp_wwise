import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.get_property_and_object_lists import wwise_get_property_and_object_lists

pytestmark = pytest.mark.no_waapi


def test_get_property_and_object_lists_dry_run():
    r = wwise_get_property_and_object_lists(property_name="Volume", object_type="Sound", dry_run=True)
    assert r["success"], r["error"]
    assert r["data"]["property"] == "Volume"
    assert "waapi_args" in r["data"]


def test_get_property_and_object_lists_missing_property():
    r = wwise_get_property_and_object_lists(property_name="", object_type="Sound")
    assert not r["success"]


def test_get_property_and_object_lists_missing_target():
    r = wwise_get_property_and_object_lists(property_name="Volume")
    assert not r["success"]
