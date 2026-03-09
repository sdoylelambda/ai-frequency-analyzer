import numpy as np
import sounddevice as sd

# Settings
duration = 5  # seconds
sample_rate = 44100
frequency = 136.1  # Hz
amplitude = 0.5  # between 0.0 and 1.0

# Generate sine wave
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
tone = amplitude * np.sin(2 * np.pi * frequency * t)

print(f"Playing {frequency} Hz tone for {duration} seconds...")
sd.play(tone, samplerate=sample_rate)
sd.wait()
print("Done.")