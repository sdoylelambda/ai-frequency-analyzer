import numpy as np
from src.gui.gui import match_frequency_to_band
from collections import deque


def compute_fft(audio_buffer, sample_rate=44100):
    fft_data = np.fft.fft(audio_buffer)
    freqs = np.fft.fftfreq(len(fft_data), 1 / sample_rate)
    magnitude = np.abs(fft_data[:len(freqs) // 2])
    freqs = freqs[:len(freqs) // 2]

    # 🛡️ Clip huge outliers that ruin thresholds
    magnitude = np.clip(magnitude, 0, 500000)

    return freqs, magnitude


recent_detections = deque(maxlen=30)


def is_duplicate(freq, tolerance=3):
    """Check if a similar frequency was recently detected."""
    for f in recent_detections:
        if abs(f - freq) < tolerance:
            return True
    return False


def is_harmonic(freq, base_freqs, tolerance=2.0):
    """Check if freq is a harmonic of any base frequency."""
    for base in base_freqs:
        ratio = freq / base
        if np.isclose(ratio, round(ratio), atol=tolerance / base):
            return True
    return False


# thinking .125-.15 threshold
def detect_peaks(freqs, magnitude, threshold=200000, match_rate_threshold=0.125, debug=True):  # threshold=10000 match_rate_threshold=0.5
    """Detect base frequency peaks from FFT data with harmonic suppression and match rate gating."""
    freqs = np.asarray(freqs)
    magnitude = np.asarray(magnitude)

    if debug:
        print("Raw freqs sample:", freqs[:10])
        print("Raw mags sample:", magnitude[:10])
        print("NaNs in freqs:", np.isnan(freqs).any())
        print("NaNs in magnitude:", np.isnan(magnitude).any())
        print("Zeros in magnitude:", np.sum(magnitude == 0))

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

    # 🎯 Peak detection
    peaks = []
    matched_peaks = 0
    total_peaks = 0
    skip_radius_hz = 2  # ADJUST HZ RANGE FINDER ---- MAYBE MAKE THIS ZERO AND ADJUST RANGES ON CONFIG
    used_freqs = []

    for freq, mag in sorted(zip(freqs, magnitude), key=lambda x: -x[1]):
        if mag < threshold:
            continue
        if any(abs(freq - used) < skip_radius_hz for used in used_freqs):
            continue

        total_peaks += 1
        label, color = match_frequency_to_band(freq)
        if label:
            matched_peaks += 1
            used_freqs.append(freq)
            peaks.append((freq, mag, label, color))
            print("Added - ", freq, mag, threshold, label)

    # 🔒 Match rate gating
    if total_peaks == 0 or matched_peaks == 0:
        match_rate = 0.0
    else:
        match_rate = matched_peaks / total_peaks

    if debug:
        print(f"Match rate: {matched_peaks}/{total_peaks} ({match_rate:.1%})")
        print(f"Threshold========> {threshold}")

    if match_rate < match_rate_threshold:
        if debug:
            print(f"[INFO] Match rate below threshold ({match_rate:.1%} < {match_rate_threshold:.1%}), suppressing detection.")
        return []

    print('peaks:::::::::::::::::', peaks)

    return peaks



