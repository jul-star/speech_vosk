#!/usr/bin/env python3
"""Wrapper script for 60-second speech recording."""

import subprocess
import sys
from datetime import datetime


def main():
    """Run speech recording for 60 seconds."""
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    output_file = f"output/result_{timestamp}.txt"

    cmd = [
        sys.executable,
        "record_speech.py",
        "--duration", "60",
        "--output", output_file,
    ]

    print("Starting 60-second recording...")
    print(f"Output file: {output_file}")
    print("Audio file: wav/recording.wav")

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
