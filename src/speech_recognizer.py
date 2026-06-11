"""Speech recognition module using Vosk library."""

from pathlib import Path
from typing import Generator, Optional

from vosk import KaldiRecognizer, Model, SetLogLevel


class SpeechRecognizer:
    """Class to recognize speech using Vosk library."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        sample_rate: int = 16000,
        language: str = "ru",
    ):
        """Initialize speech recognizer.

        Args:
            model_path: Path to Vosk model. If None, downloads default model.
            sample_rate: Sample rate in Hz (default: 16000)
            language: Language code for the model (default: "ru" for Russian)
        """
        self.sample_rate = sample_rate

        # Disable Vosk logging
        SetLogLevel(-1)

        if model_path:
            self.model = Model(model_path)
        else:
            # Download model if not exists
            try:
                from vosk import download_model
                model_path = download_model(language)
                self.model = Model(model_path)
            except ImportError:
                # Fallback: try to use default model
                self.model = Model(lang=language)

        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

    def recognize_file(self, wav_path: str) -> str:
        """Recognize speech from a WAV file.

        Args:
            wav_path: Path to WAV file

        Returns:
            Recognized text
        """
        from wave import open as wave_open

        path = Path(wav_path)
        if not path.exists():
            raise FileNotFoundError(f"WAV file not found: {wav_path}")

        with wave_open(str(path), "rb") as wf:
            if wf.getframerate() != self.sample_rate:
                raise ValueError(
                    f"Invalid sample rate: {wf.getframerate()}. "
                    f"Expected {self.sample_rate} Hz."
                )

            self.recognizer.Reset()

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if self.recognizer.AcceptWaveform(data):
                    pass

            return self.recognizer.FinalResult()

    def recognize_chunked(
        self, wav_path: str
    ) -> Generator[str, None, None]:
        """Recognize speech in chunks (streaming).

        Args:
            wav_path: Path to WAV file

        Yields:
            Partial recognition results
        """
        from wave import open as wave_open

        path = Path(wav_path)
        if not path.exists():
            raise FileNotFoundError(f"WAV file not found: {wav_path}")

        with wave_open(str(path), "rb") as wf:
            if wf.getframerate() != self.sample_rate:
                raise ValueError(
                    f"Invalid sample rate: {wf.getframerate()}. "
                    f"Expected {self.sample_rate} Hz."
                )

            self.recognizer.Reset()

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if self.recognizer.AcceptWaveform(data):
                    yield self.recognizer.Result()

            final_result = self.recognizer.FinalResult()
            if final_result:
                yield final_result

    def recognize_live(self, audio_bytes: bytes) -> Optional[str]:
        """Recognize speech from raw audio bytes.

        Args:
            audio_bytes: Raw audio data

        Returns:
            Recognized text or None if not complete
        """
        if self.recognizer.AcceptWaveform(audio_bytes):
            return self.recognizer.Result()
        return None

    def get_final_result(self) -> str:
        """Get final recognition result.

        Returns:
            Final recognized text
        """
        return self.recognizer.FinalResult()
