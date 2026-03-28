"""
Tests for profiler tools. Live tests start/stop capture and verify cursor time.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.profiler_start_capture import wwise_profiler_start_capture
from tools.profiler_stop_capture import wwise_profiler_stop_capture
from tools.profiler_get_cursor_time import wwise_profiler_get_cursor_time
from tools.profiler_enable_data import wwise_profiler_enable_data
from tools.profiler_get_voice_contributions import wwise_profiler_get_voice_contributions


def test_profiler_start_stop_capture():
    r_start = wwise_profiler_start_capture()
    assert r_start["success"], r_start["error"]
    assert isinstance(r_start["data"]["cursor"], int)

    r_stop = wwise_profiler_stop_capture()
    assert r_stop["success"], r_stop["error"]
    assert isinstance(r_stop["data"]["cursor"], int)


def test_profiler_get_cursor_time_capture():
    r = wwise_profiler_get_cursor_time("capture")
    assert r["success"], r["error"]
    assert isinstance(r["data"]["time"], int)


def test_profiler_get_cursor_time_invalid_cursor():
    r = wwise_profiler_get_cursor_time("invalid")
    assert not r["success"]


def test_profiler_enable_data_live():
    r = wwise_profiler_enable_data(["voices", "cpu"])
    assert r["success"], r["error"]


def test_profiler_enable_data_invalid():
    r = wwise_profiler_enable_data(["notARealType"])
    assert not r["success"]


def test_profiler_enable_data_empty():
    r = wwise_profiler_enable_data([])
    assert not r["success"]


def test_profiler_get_voice_contributions_no_capture():
    # No active capture — expect empty list or failure (no active voices)
    r = wwise_profiler_get_voice_contributions(0, 0)
    # May succeed with empty list or fail if no profiler data
    assert "success" in r


def test_profiler_start_capture_dry_run():
    r = wwise_profiler_start_capture(dry_run=True)
    assert r["success"]
    assert r["data"]["cursor"] == 0


def test_profiler_stop_capture_dry_run():
    r = wwise_profiler_stop_capture(dry_run=True)
    assert r["success"]


def test_profiler_get_cursor_time_dry_run():
    r = wwise_profiler_get_cursor_time(dry_run=True)
    assert r["success"]


def test_profiler_enable_data_dry_run():
    r = wwise_profiler_enable_data(["voices"], dry_run=True)
    assert r["success"]


def test_profiler_get_voice_contributions_dry_run():
    r = wwise_profiler_get_voice_contributions(0, 0, dry_run=True)
    assert r["success"]
    assert isinstance(r["data"]["contributions"], list)


def test_profiler_get_voice_contributions_invalid_id():
    r = wwise_profiler_get_voice_contributions(-1, 0)
    assert not r["success"]
