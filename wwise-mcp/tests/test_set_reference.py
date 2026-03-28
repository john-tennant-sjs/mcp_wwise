import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from waapi import WaapiClient
from tools.set_reference import wwise_set_reference
from tools.get_object import wwise_get_object
from tests.conftest import WAAPI_URL


def _get_first_conversion():
    """Return the id of the first Conversion object, or None."""
    with WaapiClient(url=WAAPI_URL) as client:
        r = client.call("ak.wwise.core.object.get", {
            "from": {"ofType": ["Conversion"]},
            "options": {"return": ["id", "name"]},
        })
        if r and r.get("return"):
            return r["return"][0]["id"]
    return None


def test_set_conversion_reference(test_sound):
    conv_id = _get_first_conversion()
    if conv_id is None:
        pytest.skip("No Conversion objects in this project.")
    r = wwise_set_reference(test_sound["id"], "Conversion", conv_id)
    assert r["success"], r["error"]


def test_set_reference_invalid_object():
    r = wwise_set_reference("\\NonExistent\\Path", "Conversion", "")
    assert not r["success"]


def test_set_reference_invalid_value(test_sound):
    r = wwise_set_reference(test_sound["id"], "Conversion", "\\NonExistent\\Conv")
    assert not r["success"]
