# audio_stream.py

import pyaudio
import struct
import numpy as np
from config import SAMPLE_RATE, FRAME_SIZE


class AudioStream:
    def __init__(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None
        self.device_index = self.get_input_device_index()

    def get_input_device_index(self):
        """Auto-selects the first input device with a mic."""
        for i in range(self.pyaudio_instance.get_device_count()):
            info = self.pyaudio_instance.get_device_info_by_index(i)
            if info.get('maxInputChannels') > 0:
                print(f"[AudioStream] Using device: {info['name']}")
                return i
        print("[AudioStream] No input device found.")
        return None

    def open_stream(self):
        """Opens the microphone stream."""
        if self.device_index is None:
            raise RuntimeError("No valid input device found.")

        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAME_SIZE,
            input_device_index=self.device_index
        )

    def read_data(self):
        """Reads a single frame and returns numpy array."""
        if self.stream is None:
            raise RuntimeError("Audio stream not open.")
        data = self.stream.read(FRAME_SIZE, exception_on_overflow=False)
        data_int = struct.unpack(str(FRAME_SIZE) + 'h', data)
        return np.array(data_int, dtype='h')

    def close(self):
        """Stops and closes the stream."""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def terminate(self):
        """Releases PyAudio resources."""
        self.pyaudio_instance.terminate()
