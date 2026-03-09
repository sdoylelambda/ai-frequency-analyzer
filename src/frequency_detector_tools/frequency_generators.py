import numpy as np
import sounddevice as sd


test_freqs = [172, 215, 285, 396, 417, 432, 528, 741, 963]


def play_tone(freq=528.0, duration=2.0, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * 2 * np.pi * t)
    audio = tone * volume
    sd.play(audio, samplerate=sample_rate)
    sd.wait()  # wait until this tone finishes


def frequency_generators():
    # Run each frequency sequentially
    for freq in test_freqs:
        print(f"Playing {freq} Hz")
        play_tone(freq=freq, duration=5.0)


