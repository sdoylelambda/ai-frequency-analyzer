import numpy as np
import sounddevice as sd
import threading
import time


class TonePlayer:
    def __init__(self):
        self.sample_rate = 44100
        self.stream = None
        self.is_playing = False
        self.mode = None   # "tone" or "sweep"

        # tone state
        self.current_freq = 440.0
        self.phase = 0.0

        # sweep state
        self.sweep_start = 0
        self.sweep_end = 0
        self.sweep_duration = 0
        self.sweep_sample_index = 0

    # --------------------------
    # Utility
    # --------------------------
    def normalize_octave(self, freq):
        f = float(freq)
        while f > 450:
            f /= 2
        return f

    def stop(self):
        self.is_playing = False
        self.mode = None

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass

        self.stream = None
        self.phase = 0.0

    # --------------------------
    # One-shot tone
    # --------------------------
    def play_tone_once(self, freq, duration):
        freq = self.normalize_octave(freq)
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(2 * np.pi * freq * t).astype(np.float32)
        sd.play(tone, self.sample_rate)
        sd.wait()

    # --------------------------
    # Continuous tone toggle
    # --------------------------
    def toggle_tone(self, freq):
        freq = self.normalize_octave(freq)

        if self.is_playing and self.mode == "tone":
            self.stop()
            return

        self.stop()
        self.is_playing = True
        self.mode = "tone"
        self.current_freq = freq
        self.phase = 0.0

        def callback(outdata, frames, time_info, status):
            if not self.is_playing:
                outdata[:] = 0
                raise sd.CallbackStop()

            t = np.arange(frames) / self.sample_rate
            outdata[:, 0] = np.sin(self.phase + 2 * np.pi * self.current_freq * t)
            self.phase += 2 * np.pi * self.current_freq * frames / self.sample_rate
            self.phase %= 2 * np.pi

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=callback
        )
        self.stream.start()

    # --------------------------
    # Sweep toggle (SAFE)
    # --------------------------
    def toggle_sweep(self, start_freq, end_freq, duration):
        if self.is_playing and self.mode == "sweep":
            self.stop()
            return

        self.stop()
        self.is_playing = True
        self.mode = "sweep"

        self.sweep_start = float(start_freq)
        self.sweep_end = float(end_freq)
        self.sweep_duration = float(duration)
        self.sweep_sample_index = 0
        self.phase = 0.0

        total_samples = int(self.sample_rate * self.sweep_duration)

        def callback(outdata, frames, time_info, status):
            if not self.is_playing:
                outdata[:] = 0
                raise sd.CallbackStop()

            output = np.zeros(frames, dtype=np.float32)

            for i in range(frames):
                if self.sweep_sample_index >= total_samples:
                    self.is_playing = False
                    raise sd.CallbackStop()

                t = self.sweep_sample_index / self.sample_rate
                freq = self.sweep_start * (
                    self.sweep_end / self.sweep_start
                ) ** (t / self.sweep_duration)

                self.phase += 2 * np.pi * freq / self.sample_rate
                output[i] = np.sin(self.phase)

                self.sweep_sample_index += 1

            outdata[:, 0] = output

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=callback
        )
        self.stream.start()
