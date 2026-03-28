import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.generate_soundbank import wwise_generate_soundbank


def test_generate_all_banks():
    """Generate all soundbanks (no filter) — tests the call works end-to-end."""
    r = wwise_generate_soundbank(write_to_disk=False)
    assert r["success"], r["error"]


def test_generate_with_platform():
    """Generate for Windows platform only."""
    r = wwise_generate_soundbank(platforms=["Windows"], write_to_disk=False)
    assert r["success"], r["error"]


def test_generate_nonexistent_bank():
    """Requesting a nonexistent bank should still return success (Wwise ignores unknown banks)."""
    r = wwise_generate_soundbank(soundbanks=["__nonexistent_bank__"], write_to_disk=False)
    # Wwise doesn't error on unknown bank names in generate; it just skips them
    assert r["success"], r["error"]
