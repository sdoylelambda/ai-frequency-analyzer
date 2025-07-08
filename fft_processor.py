import numpy as np
from alert_system import match_frequency_to_band
from scipy.signal import find_peaks


def compute_fft(audio_buffer, sample_rate=44100):
    """Computes FFT and returns (frequencies, magnitudes)."""
    fft_data = np.fft.fft(audio_buffer)
    freqs = np.fft.fftfreq(len(fft_data), 1 / sample_rate)
    magnitude = np.abs(fft_data[:len(freqs) // 2])
    freqs = freqs[:len(freqs) // 2]
    return freqs, magnitude


def detect_peaks(freqs, magnitude, threshold_multiplier=5):
    """
    Detect peaks in the frequency spectrum based on a dynamic noise floor.
    Returns a list of (freq, mag, label, color) tuples for significant peaks.
    """
    peaks = []

    # Dynamic noise thresholding
    noise_floor = np.percentile(magnitude, 85)  # Use top 15% as reference
    threshold = noise_floor * threshold_multiplier

    # Make these GUI buttons
    MIN_MAGNITUDE_THRESHOLD = 10000  # Adjust as needed
    MAX_MAGNITUDE_THRESHOLD = 100000  # Adjust as needed
    MIN_FREQUENCY_THRESHOLD = .1  # Adjust as needed
    MAX_FREQUENCY_THRESHOLD = 1000  # Adjust as needed

    for i in range(3, len(magnitude) - 3):
        if magnitude[i] > threshold:
            peak_freq = freqs[i]
            peak_mag = magnitude[i]

            # ⛔ Optional: Filter out very low/high Magnitude
            if peak_mag < MIN_MAGNITUDE_THRESHOLD or peak_mag > MAX_MAGNITUDE_THRESHOLD:
                continue

            # ⛔ Optional: Filter out very low/high frequencies
            if peak_freq < MIN_FREQUENCY_THRESHOLD or peak_freq > MAX_FREQUENCY_THRESHOLD:
                continue

            label, color = match_frequency_to_band(peak_freq)
            peaks.append((peak_freq, peak_mag, label, color))

    return peaks

# Adaptive frequency - if activated in alert_system.py
# def detect_peaks(freqs, magnitude, threshold_multiplier=3, min_magnitude=2000):
#     """
#     Detect significant frequency peaks above a noise threshold.
#     Also filters out low-magnitude false positives.
#     """
#     noise_floor = np.percentile(magnitude, 85)
#     threshold = noise_floor * threshold_multiplier
#
#     # Find peaks in the FFT magnitude spectrum
#     peak_indices, _ = find_peaks(magnitude, height=threshold)
#
#     peaks = []
#     for idx in peak_indices:
#         peak_freq = freqs[idx]
#         peak_mag = magnitude[idx]
#
#         if peak_mag < min_magnitude:
#             continue  # skip weak detections
#
#         label, color = match_frequency_to_band(peak_freq)
#         peaks.append((peak_freq, peak_mag, label, color))
#
#     return peaks


