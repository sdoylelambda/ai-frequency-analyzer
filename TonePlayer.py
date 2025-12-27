import numpy as np
import sounddevice as sd
import threading
import time


class TonePlayer:
    def __init__(self):
        self.active_streams = {}   # freq → stream
        self.stop_flags = {}       # freq → threading.Event()
        self.is_playing = False
        self.play_thread = None

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

    def stop(self):
        self.is_playing = False

        if hasattr(self, "stream"):
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass

        self.stream = None

    def play_sweep(self, start_freq, end_freq, duration):
        self.is_playing = True
        sample_rate = 44100
        total_samples = int(sample_rate * duration)

        self.phase = 0.0
        self.sample_index = 0

        def callback(outdata, frames, time_info, status):
            if not self.is_playing:
                outdata[:] = 0
                raise sd.CallbackStop()

            output = np.zeros(frames, dtype=np.float32)

            for i in range(frames):
                t = self.sample_index / sample_rate

                if t >= duration:
                    self.is_playing = False
                    raise sd.CallbackStop()

                # ✅ LOGARITHMIC SWEEP (this is your line — correct place)
                freq = start_freq * (end_freq / start_freq) ** (t / duration)

                # phase increment (this is the key)
                self.phase += 2 * np.pi * freq / sample_rate
                output[i] = np.sin(self.phase)

                self.sample_index += 1

            outdata[:, 0] = output

        self.stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            callback=callback,
            dtype="float32"
        )

        self.stream.start()

        self.stream = sd.OutputStream(
            channels=1,
            callback=callback,
            samplerate=self.sample_rate,
            dtype="float32"
        )

        self.stream.start()

    def toggle_sweep(self, start_freq, end_freq, duration):
        if self.is_playing:
            self.stop()
            return

        self.play_thread = threading.Thread(
            target=self.play_sweep,
            args=(start_freq, end_freq, duration),
            daemon=True
        )
        self.play_thread.start()

    def toggle_single_tone(self, freq):
        if self.is_playing:
            self.stop()
            return

        self.is_playing = True
        self.current_freq = freq

        def callback(outdata, frames, time, status):
            if not self.is_playing:
                outdata[:] = np.zeros((frames, 1), dtype=np.float32)
                return

            t = (np.arange(frames) + callback.phase) / self.sample_rate
            outdata[:, 0] = np.sin(2 * np.pi * self.current_freq * t).astype(np.float32)
            callback.phase += frames

        callback.phase = 0

        self.sample_rate = 44100
        self.stream = sd.OutputStream(
            channels=1,
            callback=callback,
            samplerate=self.sample_rate,
            dtype='float32'
        )

        self.stream.start()
