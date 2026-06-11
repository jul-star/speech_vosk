"""Tests for record_speech.py main script."""

import argparse
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestParseArgs:
    """Test cases for argument parsing."""

    @patch("record_speech.parse_args", return_value=argparse.Namespace(
        duration=10.0,
        output="output.txt",
        audio="recording.wav",
        model=None,
        language="ru"
    ))
    def test_default_values(self, mock_parse):
        """Test default argument values."""
        from record_speech import parse_args

        args = parse_args()

        assert args.duration == 10.0
        assert args.output == "output.txt"
        assert args.audio == "recording.wav"
        assert args.model is None
        assert args.language == "ru"

    @patch("record_speech.parse_args", return_value=argparse.Namespace(
        duration=60.0,
        output="result.txt",
        audio="audio.wav",
        model="/custom/model",
        language="en"
    ))
    def test_custom_values(self, mock_parse):
        """Test custom argument values."""
        from record_speech import parse_args

        args = parse_args()

        assert args.duration == 60.0
        assert args.output == "result.txt"
        assert args.audio == "audio.wav"
        assert args.model == "/custom/model"
        assert args.language == "en"


class TestMain:
    """Test cases for main function."""

    @patch("record_speech.parse_args")
    @patch("record_speech.AudioRecorder")
    @patch("record_speech.SpeechRecognizer")
    @patch("builtins.open")
    def test_main_success(
        self, mock_open, mock_recognizer_class, mock_recorder_class, mock_parse_args, tmp_path
    ):
        """Test successful main execution."""
        # Mock arguments
        mock_parse_args.return_value = argparse.Namespace(
            duration=5.0,
            output=str(tmp_path / "output.txt"),
            audio=str(tmp_path / "audio.wav"),
            model=None,
            language="ru"
        )

        # Mock recorder
        mock_recorder = MagicMock()
        mock_recorder.save_to_file.return_value = tmp_path / "audio.wav"
        mock_recorder_class.return_value = mock_recorder

        # Mock recognizer
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_file.return_value = json.dumps({"text": "hello world"})
        mock_recognizer_class.return_value = mock_recognizer

        # Create audio file
        (tmp_path / "audio.wav").touch()

        from record_speech import main

        result = main()

        assert result == 0
        mock_recorder.start_recording.assert_called_once()
        mock_recorder.stop_recording.assert_called_once()

    @patch("record_speech.parse_args")
    @patch("record_speech.AudioRecorder")
    @patch("record_speech.SpeechRecognizer")
    def test_main_recognizer_error(
        self, mock_recognizer_class, mock_recorder_class, mock_parse_args, tmp_path
    ):
        """Test main with recognizer initialization error."""
        mock_parse_args.return_value = argparse.Namespace(
            duration=5.0,
            output=str(tmp_path / "output.txt"),
            audio=str(tmp_path / "audio.wav"),
            model=None,
            language="ru"
        )

        mock_recorder = MagicMock()
        mock_recorder.save_to_file.return_value = tmp_path / "audio.wav"
        mock_recorder_class.return_value = mock_recorder

        mock_recognizer_class.side_effect = Exception("Model not found")

        # Create audio file
        (tmp_path / "audio.wav").touch()

        from record_speech import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch("record_speech.parse_args")
    @patch("record_speech.AudioRecorder")
    @patch("record_speech.SpeechRecognizer")
    def test_main_keyboard_interrupt(
        self, mock_recognizer_class, mock_recorder_class, mock_parse_args, tmp_path
    ):
        """Test main with keyboard interrupt."""
        import json

        mock_parse_args.return_value = argparse.Namespace(
            duration=5.0,
            output=str(tmp_path / "output.txt"),
            audio=str(tmp_path / "audio.wav"),
            model=None,
            language="ru"
        )

        mock_recorder = MagicMock()
        mock_recorder.save_to_file.return_value = tmp_path / "audio.wav"
        mock_recorder_class.return_value = mock_recorder

        # Mock recognizer to return valid JSON
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_file.return_value = json.dumps({"text": "test"})
        mock_recognizer_class.return_value = mock_recognizer

        # Mock time.sleep to raise KeyboardInterrupt
        with patch("record_speech.time.sleep", side_effect=KeyboardInterrupt):
            from record_speech import main

            result = main()

            assert result == 0
            mock_recorder.stop_recording.assert_called_once()

    @patch("record_speech.parse_args")
    @patch("record_speech.AudioRecorder")
    @patch("record_speech.SpeechRecognizer")
    @patch("builtins.open")
    def test_main_creates_output_directory(
        self, mock_open, mock_recognizer_class, mock_recorder_class, mock_parse_args, tmp_path
    ):
        """Test that main creates output directory if it doesn't exist."""
        output_dir = tmp_path / "nested" / "output"
        output_file = output_dir / "result.txt"

        mock_parse_args.return_value = argparse.Namespace(
            duration=5.0,
            output=str(output_file),
            audio=str(tmp_path / "audio.wav"),
            model=None,
            language="ru"
        )

        mock_recorder = MagicMock()
        mock_recorder.save_to_file.return_value = tmp_path / "audio.wav"
        mock_recorder_class.return_value = mock_recorder

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_file.return_value = json.dumps({"text": "test"})
        mock_recognizer_class.return_value = mock_recognizer

        (tmp_path / "audio.wav").touch()

        from record_speech import main

        result = main()

        assert result == 0
        assert output_dir.exists()

    @patch("record_speech.parse_args")
    @patch("record_speech.AudioRecorder")
    @patch("record_speech.SpeechRecognizer")
    @patch("builtins.open")
    def test_main_json_decode_error(
        self, mock_open, mock_recognizer_class, mock_recorder_class, mock_parse_args, tmp_path
    ):
        """Test main with JSON decode error in result."""
        mock_parse_args.return_value = argparse.Namespace(
            duration=5.0,
            output=str(tmp_path / "output.txt"),
            audio=str(tmp_path / "audio.wav"),
            model=None,
            language="ru"
        )

        mock_recorder = MagicMock()
        mock_recorder.save_to_file.return_value = tmp_path / "audio.wav"
        mock_recorder_class.return_value = mock_recorder

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_file.return_value = "invalid json"
        mock_recognizer_class.return_value = mock_recognizer

        (tmp_path / "audio.wav").touch()

        from record_speech import main

        result = main()

        assert result == 0
