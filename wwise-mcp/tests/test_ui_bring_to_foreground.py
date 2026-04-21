import sys, os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.ui_bring_to_foreground import wwise_ui_bring_to_foreground


def test_ui_bring_to_foreground_live():
    r = wwise_ui_bring_to_foreground()
    assert r["success"], r["error"]


@pytest.mark.no_waapi
def test_ui_bring_to_foreground_dry_run():
    r = wwise_ui_bring_to_foreground(dry_run=True)
    assert r["success"]
