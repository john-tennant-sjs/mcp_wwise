import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.set_notes import wwise_set_notes


def test_set_notes_basic(test_sound):
    r = wwise_set_notes(test_sound["id"], "Phase 2 test note")
    assert r["success"], r["error"]
    assert r["data"]["notes"] == "Phase 2 test note"


def test_set_notes_empty_string(test_sound):
    r = wwise_set_notes(test_sound["id"], "")
    assert r["success"], r["error"]


def test_set_notes_multiline(test_sound):
    note = "Line 1\nLine 2\nLine 3"
    r = wwise_set_notes(test_sound["id"], note)
    assert r["success"], r["error"]
    assert r["data"]["notes"] == note


def test_set_notes_nonexistent():
    r = wwise_set_notes("\\NonExistent\\Path\\Obj", "note")
    assert not r["success"]
