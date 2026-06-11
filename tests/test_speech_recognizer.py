"""Tests for speech_recognizer module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from speech_recognizer import SpeechRecognizer


class TestSpeechRecognizer:
    """Test cases for SpeechRecognizer class."""

    def test_init_default(self):
        """Test default initialization."""
        # Skip actual model loading for unit tests
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model") as mock_model, \
             patch("speech_recognizer.KaldiRecognizer"):
            recognizer = SpeechRecognizer()

            mock_model.assert_called_once()

    def test_init_custom_model_path(self):
        """Test initialization with custom model path."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model") as mock_model, \
             patch("speech_recognizer.KaldiRecognizer"):
            recognizer = SpeechRecognizer(model_path="/custom/path")

            mock_model.assert_called_once_with("/custom/path")

    def test_init_custom_language(self):
        """Test initialization with custom language."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model") as mock_model, \
             patch("speech_recognizer.KaldiRecognizer"):
            recognizer = SpeechRecognizer(language="en")

            mock_model.assert_called_once()

    def test_recognize_file_success(self, sample_wav_file):
        """Test successful file recognition."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer") as mock_recognizer_class:
            
            mock_recognizer = MagicMock()
            mock_recognizer.Reset.return_value = None
            mock_recognizer.AcceptWaveform.return_value = True
            mock_recognizer.FinalResult.return_value = json.dumps({"text": "hello world"})
            mock_recognizer_class.return_value = mock_recognizer

            recognizer = SpeechRecognizer()

            result = recognizer.recognize_file(str(sample_wav_file))

            assert result == '{"text": "hello world"}'

    def test_recognize_file_not_found(self):
        """Test recognizing non-existent file raises error."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer"):
            recognizer = SpeechRecognizer()

            with pytest.raises(FileNotFoundError):
                recognizer.recognize_file("nonexistent.wav")

    def test_recognize_file_wrong_sample_rate(self, tmp_path):
        """Test recognizing file with wrong sample rate raises error."""
        import wave

        # Create WAV file with wrong sample rate
        wav_file = tmp_path / "wrong_rate.wav"
        with wave.open(str(wav_file), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)  # Wrong rate
            wf.writeframes(b"\x00\x00\x00\x00")

        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer"):
            recognizer = SpeechRecognizer()

            with pytest.raises(ValueError, match="Invalid sample rate"):
                recognizer.recognize_file(str(wav_file))

    def test_recognize_live_complete(self):
        """Test live recognition with complete result."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer") as mock_recognizer_class:
            
            mock_recognizer = MagicMock()
            mock_recognizer.AcceptWaveform.return_value = True
            mock_recognizer.Result.return_value = json.dumps({"text": "test"})
            mock_recognizer_class.return_value = mock_recognizer

            recognizer = SpeechRecognizer()

            result = recognizer.recognize_live(b"audio_data")

            assert result == '{"text": "test"}'

    def test_recognize_live_incomplete(self):
        """Test live recognition with incomplete result."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer") as mock_recognizer_class:
            
            mock_recognizer = MagicMock()
            mock_recognizer.AcceptWaveform.return_value = False
            mock_recognizer_class.return_value = mock_recognizer

            recognizer = SpeechRecognizer()

            result = recognizer.recognize_live(b"audio_data")

            assert result is None

    def test_get_final_result(self):
        """Test getting final result."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer") as mock_recognizer_class:
            
            mock_recognizer = MagicMock()
            mock_recognizer.FinalResult.return_value = json.dumps({"text": "final"})
            mock_recognizer_class.return_value = mock_recognizer

            recognizer = SpeechRecognizer()

            result = recognizer.get_final_result()

            assert result == '{"text": "final"}'

    def test_recognize_chunked(self, sample_wav_file):
        """Test chunked recognition."""
        with patch("speech_recognizer.SetLogLevel"), \
             patch("speech_recognizer.Model"), \
             patch("speech_recognizer.KaldiRecognizer") as mock_recognizer_class:
            
            mock_recognizer = MagicMock()
            mock_recognizer.Reset.return_value = None
            mock_recognizer.AcceptWaveform.side_effect = [False, True]
            mock_recognizer.Result.return_value = json.dumps({"text": "chunk1"})
            mock_recognizer.FinalResult.return_value = json.dumps({"text": "final"})
            mock_recognizer_class.return_value = mock_recognizer

            recognizer = SpeechRecognizer()

            results = list(recognizer.recognize_chunked(str(sample_wav_file)))

            assert len(results) >= 1
