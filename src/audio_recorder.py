"""Audio recording module for speech recognition."""

import wave
from pathlib import Path

import numpy as np
import sounddevice as sd


class AudioRecorder:
    """Class to record audio from microphone."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "int16",
    ):
        """Initialize audio recorder.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for vosk)
            channels: Number of audio channels (default: 1)
            dtype: Data type for audio samples (default: int16)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.is_recording = False
        self.audio_data: list[np.ndarray] = []

    def callback(self, indata: np.ndarray, frames: int, time: float, status: bool) -> None:
        """Callback function for audio stream.

        Args:
            indata: Input audio data
            frames: Number of frames
            time: Stream time
            status: Stream status
        """
        if status:
            print(f"Warning: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def start_recording(self) -> None:
        """Start recording audio from microphone."""
        self.audio_data = []
        self.is_recording = True

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self.callback,
        )
        self.stream.start()

    def stop_recording(self) -> None:
        """Stop recording audio."""
        self.is_recording = False
        if hasattr(self, "stream"):
            self.stream.stop()
            self.stream.close()

    def save_to_file(self, filepath: str) -> Path:
        """Save recorded audio to WAV file.

        Args:
            filepath: Path to save the WAV file

        Returns:
            Path object of the saved file
        """
        if not self.audio_data:
            raise ValueError("No audio data recorded. Start recording first.")

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        audio_array = np.concatenate(self.audio_data, axis=0)

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_array.tobytes())

        return path

    def record_for_duration(self, duration: float) -> Path:
        """Record audio for a specific duration.

        Args:
            duration: Recording duration in seconds

        Returns:
            Path to saved WAV file
        """
        self.audio_data = []
        sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
        )
        sd.wait()

        # Get the recorded data
        audio_array = sd.getstream().read(int(duration * self.sample_rate)) if sd.getstream() else np.array([])

        path = Path("temp_recording.wav")
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_array.tobytes())

        return path
