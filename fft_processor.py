import numpy as np
from alert_system import match_frequency_to_band
from scipy.signal import find_peaks


def compute_fft(audio_buffer, sample_rate=44100):
    fft_data = np.fft.fft(audio_buffer)
    freqs = np.fft.fftfreq(len(fft_data), 1 / sample_rate)
    magnitude = np.abs(fft_data[:len(freqs) // 2])
    freqs = freqs[:len(freqs) // 2]

    # 🛡️ Clip huge outliers that ruin thresholds
    magnitude = np.clip(magnitude, 0, 500000)

    return freqs, magnitude


def detect_peaks(freqs, magnitude, threshold_multiplier=5, debug=True):
    """Detect peaks in the frequency spectrum based on a dynamic noise floor."""
    freqs = np.asarray(freqs)
    magnitude = np.asarray(magnitude)

    # 🔍 Debug info (optional)
    if debug:
        print("Raw freqs sample:", freqs[:10])
        print("Raw mags sample:", magnitude[:10])
        print("NaNs in freqs:", np.isnan(freqs).any())
        print("NaNs in magnitude:", np.isnan(magnitude).any())
        print("Zeros in magnitude:", (magnitude == 0).sum())

    # 🚫 Sanity check
    if freqs.size == 0 or magnitude.size == 0:
        if debug:
            print("Match rate: 0/0 (no data)")
        return []

    # 🧼 Remove invalid entries
    valid = (
        np.isfinite(freqs) &
        np.isfinite(magnitude) &
        (freqs > 0) &
        (magnitude > 0)
    )
    freqs = freqs[valid]
    magnitude = magnitude[valid]

    if freqs.size == 0 or magnitude.size == 0:
        if debug:
            print("Match rate: 0/0 (no usable data)")
        return []

    # 📈 Dynamic Thresholds (safe fallback)
    try:
        min_mag_threshold = np.percentile(magnitude, 88)
        if not np.isfinite(min_mag_threshold) or min_mag_threshold <= 0:
            if debug:
                print("[WARN] Invalid min_mag_threshold; using fallback.")
            min_mag_threshold = 10000
    except Exception as e:
        if debug:
            print(f"[ERROR] min_mag_threshold failed: {e}")
        min_mag_threshold = 10000

    try:
        noise_floor = np.percentile(magnitude, 85)
        if not np.isfinite(noise_floor) or noise_floor <= 0:
            if debug:
                print("[WARN] Invalid noise_floor; using fallback.")
            noise_floor = np.mean(magnitude) if np.mean(magnitude) > 0 else 10000
    except Exception as e:
        if debug:
            print(f"[ERROR] noise_floor failed: {e}")
        noise_floor = 10000

    threshold = noise_floor * threshold_multiplier
    max_mag_threshold = 100000
    min_freq = 0.1
    max_freq = 1000

    # 🎯 Peak detection
    peaks = []
    total_peaks = 0
    matched_peaks = 0

    for freq, mag in zip(freqs, magnitude):
        if mag < 2500:
            continue

        if (
            mag >= threshold and
            min_mag_threshold <= mag <= max_mag_threshold and
            min_freq <= freq <= max_freq
        ):
            total_peaks += 1
            label, color = match_frequency_to_band(freq)
            if label:
                matched_peaks += 1
                peaks.append((freq, mag, label, color))

    # 📊 Match rate report
    if debug:
        if total_peaks > 0:
            print(f"Match rate: {matched_peaks}/{total_peaks} ({matched_peaks / total_peaks:.1%})")
        else:
            print("Match rate: 0/0 (no usable peaks)")

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


