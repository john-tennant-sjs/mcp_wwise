import sys, os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.log_get import wwise_log_get


def test_log_get_general():
    r = wwise_log_get("general")
    assert r["success"], r["error"]
    assert isinstance(r["data"]["items"], list)
    assert r["data"]["channel"] == "general"


def test_log_get_soundbank_generate():
    r = wwise_log_get("soundbankGenerate")
    assert r["success"], r["error"]


@pytest.mark.no_waapi
def test_log_get_invalid_channel():
    r = wwise_log_get("invalid_channel")
    assert not r["success"]


@pytest.mark.no_waapi
def test_log_get_dry_run():
    r = wwise_log_get(dry_run=True)
    assert r["success"]
    assert isinstance(r["data"]["items"], list)
