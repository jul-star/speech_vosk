# Speech Recognition with Vosk

Speech-to-text application using Vosk library for offline Russian speech recognition.
CPU is enough!

## Installation

Install the package with dependencies:

```bash
pip install -e ".[dev]"
pip install -e ".[speech]"
```

Or all at once:

```bash
pip install -e ".[dev,speech]"
```

## Usage

### Record and Recognize Speech

```bash
# Default: 10 seconds, output/output.txt, wav/recording.wav
python -m src.record_speech

# Custom duration and output
python -m src.record_speech --duration 60 --output result.txt

# Custom audio file path
python -m src.record_speech --audio wav/my_recording.wav

# Different language (requires model download)
python -m src.record_speech --language en
```

**Note:** Press `Ctrl+C` to stop recording early. Progress is shown every 30 seconds for recordings longer than 30 seconds.

### Quick 60-Second Recording

```bash
python -m src.speech_60
```

Output: `output/result_YYYY_MM_DD_HH_MM.txt`

**Note:** Press `Ctrl+C` to stop recording early. Progress is shown every 30 seconds.

### Quick 300-Second (5-Minute) Recording

```bash
python -m src.speech_300
```

Output: `output/result_300_YYYY_MM_DD_HH_MM.txt`

**Note:** Press `Ctrl+C` to stop recording early. Progress is shown every 30 seconds.

### Windows Batch Files

Double-click or run from command prompt:

```cmd
speech_60.bat    # 60-second recording
speech_300.bat   # 300-second recording
```

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-d, --duration` | 10.0 | Recording duration in seconds |
| `-o, --output` | output/output.txt | Output text file path |
| `--audio` | wav/recording.wav | Audio file path (WAV format) |
| `--model` | None | Path to Vosk model directory |
| `--language` | ru | Language code (ru/en) |

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── audio_recorder.py      # Audio recording module
│   ├── speech_recognizer.py   # Speech recognition module
│   ├── record_speech.py       # Main recording script
│   ├── speech_60.py           # 60-second recording wrapper
│   └── speech_300.py          # 300-second recording wrapper
├── tests/
│   ├── conftest.py
│   ├── test_audio_recorder.py
│   ├── test_speech_recognizer.py
│   ├── test_record_speech.py
│   ├── test_speech_60.py
│   └── test_speech_300.py
├── wav/                       # Audio files (auto-created)
├── output/                    # Text output files (auto-created)
├── doc/                       # Documentation
├── pyproject.toml             # Project configuration
├── ruff.toml                  # Linter configuration
├── KODA.md                    # KODA AI configuration
├── README.md                  # This file
├── speech_60.bat              # Windows shortcut for 60s recording
└── speech_300.bat             # Windows shortcut for 300s recording
```

## Development

### Running Tests

```bash
pytest
```

### Running Tests with Coverage

```bash
pytest --cov=src
```

### Running Linter

```bash
ruff check .
```

### Fix Linting Issues

```bash
ruff check . --fix
```

## Requirements

- Python 3.10+
- Vosk 0.3.45+
- sounddevice 0.4.6+
- soundfile 0.13.0+
- numpy 1.24.0+

## License

MIT
