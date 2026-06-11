"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_audio_data():
    """Provide sample audio data for testing."""
    import numpy as np
    return np.array([1, 2, 3, 4, 5], dtype=np.int16)


@pytest.fixture
def sample_wav_file(tmp_path, sample_audio_data):
    """Create a sample WAV file for testing."""
    import wave

    wav_file = tmp_path / "sample.wav"
    with wave.open(str(wav_file), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(sample_audio_data.tobytes())

    return wav_file
