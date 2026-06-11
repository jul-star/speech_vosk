#!/usr/bin/env python3
"""Main script for speech recognition and saving to file."""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    from .audio_recorder import AudioRecorder, calculate_audio_level
    from .speech_recognizer import SpeechRecognizer
except ImportError:
    from audio_recorder import AudioRecorder, calculate_audio_level
    from speech_recognizer import SpeechRecognizer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Record speech and save recognized text to file"
    )
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=10.0,
        help="Recording duration in seconds (default: 10)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output/output.txt",
        help="Output text file (default: output/output.txt)"
    )
    parser.add_argument(
        "--audio",
        type=str,
        default="wav/recording.wav",
        help="Audio file to save (default: wav/recording.wav)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to Vosk model directory"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="ru",
        help="Language code (default: ru)"
    )
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()

    # Create directories if they don't exist
    Path("wav").mkdir(parents=True, exist_ok=True)
    Path("output").mkdir(parents=True, exist_ok=True)

    # Initialize recorder
    recorder = AudioRecorder(sample_rate=16000)

    print(f"Recording for {args.duration} seconds...")
    recorder.start_recording()

    try:
        import time
        elapsed = 0
        interval = 30  # Показать прогресс каждые 30 секунд
        while elapsed < args.duration:
            time.sleep(min(interval, args.duration - elapsed))
            elapsed += interval
            print(f"Progress: {elapsed}/{args.duration} seconds")
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
    finally:
        recorder.stop_recording()

    # Save audio
    audio_path = recorder.save_to_file(args.audio)
    print(f"Audio saved to: {audio_path}")

    # Show audio level
    level = calculate_audio_level(str(audio_path))
    if level is not None:
        if level < 5:
            level_msg = f"Level: {level:.1f}% (too quiet - check microphone)"
        elif level > 80:
            level_msg = f"Level: {level:.1f}% (too loud - reduce volume)"
        else:
            level_msg = f"Level: {level:.1f}% (good)"
        print(level_msg)
    else:
        print("Level: N/A (could not calculate)")

    # Initialize recognizer
    print("Recognizing speech...")
    try:
        recognizer = SpeechRecognizer(
            model_path=args.model,
            language=args.language
        )
        print(f"Using language: {args.language}")
    except Exception as e:
        print(f"Error initializing recognizer: {e}")
        print("Please install Vosk model: pip install vosk")
        sys.exit(1)

    # Recognize speech
    print("Recognizing speech...")
    result = recognizer.recognize_file(str(audio_path))

    # Parse JSON result
    try:
        result_data = json.loads(result)
        text = result_data.get("text", "")
    except json.JSONDecodeError:
        text = result

    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Recognized text saved to: {output_path}")
    
    if text.strip():
        print(f"Text: {text}")
    else:
        print("Warning: No speech was recognized. Possible reasons:")
        print("  - No speech was recorded")
        print("  - Vosk model not found or incorrect language")
        print("  - Audio quality issues (check microphone)")
        print(f"  - Raw result: {result[:100] if result else 'empty'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
