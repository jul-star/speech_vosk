"""Tests for speech_60.py wrapper script."""

import subprocess
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestSpeech60Main:
    """Test cases for speech_60 main function."""

    @patch("speech_60.subprocess.run")
    @patch("speech_60.datetime")
    def test_main_success(self, mock_datetime, mock_run):
        """Test successful execution."""
        mock_run.return_value = MagicMock(returncode=0)

        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025_01_15_14_30"
        mock_datetime.now.return_value = mock_now

        from speech_60 import main

        result = main()

        assert result == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[1] == "record_speech.py"
        assert call_args[2] == "--duration"
        assert call_args[3] == "60"
        assert call_args[4] == "--output"
        assert call_args[5].startswith("output/result_2025_01_15_14_30.txt")

    @patch("speech_60.subprocess.run")
    @patch("speech_60.datetime")
    def test_main_failure(self, mock_datetime, mock_run):
        """Test execution with failure."""
        mock_run.return_value = MagicMock(returncode=1)

        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025_01_15_14_30"
        mock_datetime.now.return_value = mock_now

        from speech_60 import main

        result = main()

        assert result == 1

    @patch("speech_60.subprocess.run")
    @patch("speech_60.datetime")
    def test_main_output_format(self, mock_datetime, mock_run):
        """Test output file naming format."""
        mock_run.return_value = MagicMock(returncode=0)

        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025_06_15_09_45"
        mock_datetime.now.return_value = mock_now

        from speech_60 import main

        main()

        call_args = mock_run.call_args[0][0]
        output_file = call_args[5]
        assert output_file.startswith("output/result_")
        assert output_file.endswith(".txt")
