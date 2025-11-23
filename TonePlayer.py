import numpy as np
import sounddevice as sd
import threading
import time


class TonePlayer:
    def __init__(self):
        self.active_streams = {}   # freq → stream
        self.stop_flags = {}       # freq → threading.Event()

    # --- Play a tone once for N seconds ---
    def play_tone_once(self, freq, duration):
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * freq * t).astype(np.float32)

        sd.play(tone, sample_rate)
        sd.wait()

    # --- Toggle continuous tone ---
    def toggle_tone(self, freq):

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

        # Stream callback for smooth continuous output
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
