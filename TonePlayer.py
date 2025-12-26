import numpy as np
import sounddevice as sd
import threading
import time


class TonePlayer:
    def __init__(self):
        self.active_streams = {}   # freq → stream
        self.stop_flags = {}       # freq → threading.Event()

    # --- Normalize frequency into a consistent base octave ---
    def normalize_octave(self, freq):
        f = float(freq)
        while f > 450:        # shift down 1 octave while too bright
            f /= 2
        return f

    # --- Play a tone once for N seconds ---
    def play_tone_once(self, freq, duration):
        sample_rate = 44100

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * freq * t).astype(np.float32)

        sd.play(tone, sample_rate)
        print(f"PLAYING TONE {freq} Hz")
        sd.wait()

    # --- Toggle continuous tone (smooth, no pulsing) ---
    def toggle_tone(self, freq):
        freq = self.normalize_octave(freq)

        # Stop if already playing
        if freq in self.active_streams:
            print(f"🔇 Stopping {freq} Hz")
            self.stop_flags[freq].set()
            self.active_streams[freq].stop()
            self.active_streams[freq].close()
            del self.active_streams[freq]
            del self.stop_flags[freq]
            return

        print(f"🎵 Starting continuous tone: {freq} Hz")

        stop_flag = threading.Event()
        self.stop_flags[freq] = stop_flag

        sample_rate = 44100
        cycle_len = int(sample_rate / freq)

        t = np.linspace(0, cycle_len / sample_rate, cycle_len, False)
        wave = np.sin(2 * np.pi * freq * t).astype(np.float32)

        # Seamless infinite loop without pulsing
        def callback(outdata, frames, time, status):
            if stop_flag.is_set():
                raise sd.CallbackStop()

            reps = int(np.ceil(frames / len(wave)))
            tiled = np.tile(wave, reps)[:frames]
            outdata[:] = tiled.reshape(-1, 1)

        stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            callback=callback
        )

        self.active_streams[freq] = stream
        stream.start()
