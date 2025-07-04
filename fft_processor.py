# fft_processor.py

import numpy as np
from alert_system import match_frequency_to_band

def compute_fft(audio_buffer, sample_rate=44100):
    """Computes FFT and returns (frequencies, magnitudes)."""
    fft_data = np.fft.fft(audio_buffer)
    freqs = np.fft.fftfreq(len(fft_data), 1 / sample_rate)
    magnitude = np.abs(fft_data[:len(freqs) // 2])
    freqs = freqs[:len(freqs) // 2]
    return freqs, magnitude


def detect_peaks(freqs, magnitude, threshold_multiplier=5):
    """Returns a list of peaks: [(freq, mag, label, color)]"""
    peaks = []
    for i in range(3, len(magnitude) - 3):
        local_avg = np.mean(magnitude[i - 3:i + 4])
        if magnitude[i] > local_avg * threshold_multiplier:
            freq = freqs[i]
            mag = magnitude[i]
            label, color = match_frequency_to_band(freq)
            peaks.append((freq, mag, label, color))
    return peaks
