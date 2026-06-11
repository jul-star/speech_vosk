"""Tests for audio_recorder module."""

import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from audio_recorder import AudioRecorder


class TestAudioRecorder:
    """Test cases for AudioRecorder class."""

    def test_init_default_values(self):
        """Test default initialization values."""
        recorder = AudioRecorder()
        assert recorder.sample_rate == 16000
        assert recorder.channels == 1
        assert recorder.dtype == "int16"
        assert recorder.is_recording is False
        assert recorder.audio_data == []

    def test_init_custom_values(self):
        """Test custom initialization values."""
        recorder = AudioRecorder(sample_rate=44100, channels=2, dtype="float32")
        assert recorder.sample_rate == 44100
        assert recorder.channels == 2
        assert recorder.dtype == "float32"

    def test_callback_with_status(self):
        """Test callback function with status."""
        recorder = AudioRecorder()
        recorder.is_recording = True

        mock_indata = MagicMock()
        mock_indata.copy.return_value = np.array([1, 2, 3])

        # Mock status to be truthy
        recorder.callback(mock_indata, 10, 0.0, status=True)
        # Status still adds data, just prints warning
        assert len(recorder.audio_data) == 1

    def test_callback_without_status(self):
        """Test callback function without status."""
        recorder = AudioRecorder()
        recorder.is_recording = True

        mock_indata = MagicMock()
        mock_indata.copy.return_value = np.array([1, 2, 3])

        recorder.callback(mock_indata, 10, 0.0, status=False)
        assert len(recorder.audio_data) == 1

    def test_callback_not_recording(self):
        """Test callback function when not recording."""
        recorder = AudioRecorder()
        recorder.is_recording = False

        mock_indata = MagicMock()
        recorder.callback(mock_indata, 10, 0.0, status=False)
        assert recorder.audio_data == []

    @patch("audio_recorder.sd.InputStream")
    def test_start_recording(self, mock_stream_class):
        """Test starting recording."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream

        recorder = AudioRecorder()
        recorder.start_recording()

        assert recorder.is_recording is True
        mock_stream.start.assert_called_once()

    @patch("audio_recorder.sd.InputStream")
    def test_stop_recording(self, mock_stream_class):
        """Test stopping recording."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream

        recorder = AudioRecorder()
        recorder.start_recording()
        recorder.stop_recording()

        assert recorder.is_recording is False
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch("audio_recorder.sd.InputStream")
    def test_save_to_file_success(self, mock_stream_class):
        """Test saving audio to file."""
        recorder = AudioRecorder()
        recorder.audio_data = [np.array([1, 2, 3], dtype=np.int16)]

        path = recorder.save_to_file("test_output.wav")

        assert path.exists()
        assert path.suffix == ".wav"
        path.unlink()  # Cleanup

    @patch("audio_recorder.sd.InputStream")
    def test_save_to_file_no_data(self, mock_stream_class):
        """Test saving audio with no data raises error."""
        recorder = AudioRecorder()

        with pytest.raises(ValueError, match="No audio data recorded"):
            recorder.save_to_file("test_output.wav")

    @patch("audio_recorder.sd.InputStream")
    def test_save_to_file_creates_directories(self, mock_stream_class, tmp_path):
        """Test that save_to_file creates parent directories."""
        recorder = AudioRecorder()
        recorder.audio_data = [np.array([1, 2, 3], dtype=np.int16)]

        output_dir = tmp_path / "subdir" / "nested"
        output_file = output_dir / "test.wav"

        path = recorder.save_to_file(str(output_file))

        assert path.exists()
        path.unlink()
