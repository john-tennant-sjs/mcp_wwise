"""
Undo groups are session-scoped: beginGroup and endGroup/cancelGroup must be
called within the same WAAPI connection. Since each tool call opens its own
connection, begin+end across two tool calls will fail.
These tests verify individual tool contracts and error behaviour.
"""
import sys, os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.undo_begin_group import wwise_undo_begin_group
from tools.undo_end_group import wwise_undo_end_group
from tools.undo_cancel_group import wwise_undo_cancel_group


def test_undo_begin_group_live():
    r = wwise_undo_begin_group()
    assert r["success"], r["error"]
    # Note: no matching endGroup — the connection closing discards the open group.


def test_undo_end_group_without_begin():
    """endGroup with no active group in this session should fail."""
    r = wwise_undo_end_group("_test_group")
    assert not r["success"]


def test_undo_cancel_group_without_begin():
    """cancelGroup with no active group in this session should fail."""
    r = wwise_undo_cancel_group()
    assert not r["success"]


def test_undo_end_group_empty_name():
    r = wwise_undo_end_group("")
    assert not r["success"]


@pytest.mark.no_waapi
def test_undo_begin_dry_run():
    r = wwise_undo_begin_group(dry_run=True)
    assert r["success"]


@pytest.mark.no_waapi
def test_undo_end_dry_run():
    r = wwise_undo_end_group("_test", dry_run=True)
    assert r["success"]


@pytest.mark.no_waapi
def test_undo_cancel_dry_run():
    r = wwise_undo_cancel_group(dry_run=True)
    assert r["success"]
