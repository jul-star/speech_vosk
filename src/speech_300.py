#!/usr/bin/env python3
"""Wrapper script for 300-second (5-minute) speech recording."""

import subprocess
import sys
from datetime import datetime


def main():
    """Run speech recording for 300 seconds."""
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    output_file = f"output/result_300_{timestamp}.txt"

    cmd = [
        sys.executable,
        "record_speech.py",
        "--duration", "300",
        "--output", output_file,
    ]

    print(f"Starting 300-second (5-minute) recording...")
    print(f"Output file: {output_file}")
    print(f"Audio file: wav/recording.wav")

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
