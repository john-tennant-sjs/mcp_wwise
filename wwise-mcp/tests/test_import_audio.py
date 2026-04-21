import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import wave
import struct
import pytest
from waapi import WaapiClient
from tools.import_audio import wwise_import_audio
from tests.conftest import TEST_PARENT, WAAPI_URL

ORIGINALS_SFX = os.getenv("WWISE_ORIGINALS_SFX")


def _make_wav(path: str) -> None:
    """Write a minimal valid 1-second 44.1kHz mono WAV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = 44100
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(struct.pack(f"<{n}h", *([0] * n)))


def _delete_object(ref: str) -> None:
    with WaapiClient(url=WAAPI_URL) as c:
        c.call("ak.wwise.core.object.delete", {"object": ref})


@pytest.fixture
def temp_wav():
    """Create a temp WAV in the project's Originals/SFX folder."""
    if not ORIGINALS_SFX:
        pytest.skip("Set WWISE_ORIGINALS_SFX to run import-audio integration tests.")
    wav_path = os.path.join(ORIGINALS_SFX, "_test_import.wav")
    _make_wav(wav_path)
    yield wav_path
    if os.path.exists(wav_path):
        os.remove(wav_path)


def test_import_audio_basic(temp_wav):
    # objectPath format: \\hierarchy\\parent\\<Type>name
    import_path = f"{TEST_PARENT}\\<Sound>_imported_sound"
    r = wwise_import_audio(
        imports=[{
            "audioFile": temp_wav,
            "objectPath": import_path,
        }],
        import_operation="replaceExisting",
    )
    assert r["success"], r["error"]
    assert len(r["data"]["imported"]) >= 1
    _delete_object(f"{TEST_PARENT}\\_imported_sound")


@pytest.mark.no_waapi
def test_import_audio_empty():
    r = wwise_import_audio(imports=[])
    assert not r["success"]


@pytest.mark.no_waapi
def test_import_audio_missing_file():
    r = wwise_import_audio(imports=[{
        "audioFile": "T:\\does_not_exist.wav",
        "objectPath": f"<Sound>\\\\{TEST_PARENT}\\\\test",
    }])
    assert not r["success"]
