import sys, os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.ui_commands_execute import wwise_ui_commands_execute


def test_ui_commands_execute_known_command():
    # FindInProjectExplorerSyncGroup1 is a standard Wwise UI command
    r = wwise_ui_commands_execute("FindInProjectExplorerSyncGroup1")
    assert r["success"], r["error"]


@pytest.mark.no_waapi
def test_ui_commands_execute_empty_command():
    r = wwise_ui_commands_execute("")
    assert not r["success"]


@pytest.mark.no_waapi
def test_ui_commands_execute_dry_run():
    r = wwise_ui_commands_execute("SomeCommand", dry_run=True)
    assert r["success"]
