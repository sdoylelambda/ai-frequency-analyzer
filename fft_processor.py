import numpy as np
from alert_system import match_frequency_to_band
from scipy.signal import find_peaks
from collections import deque
from scipy.ndimage import gaussian_filter1d
from config import CHAKRA_FREQUENCY_BANDS


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


def get_dynamic_detection_params(center_freq: float) -> dict:
    # Reference anchors
    min_freq = 136.1
    max_freq = 963
    min_tol = 1.0  # ±1 Hz at lowest freq
    max_tol = 10.0  # ±10 Hz at 963
    min_mag = 5000  # ~5k is typical for your detections
    max_mag = 60000  # This keeps it tight enough to still detect 100k+ hits

    # Normalize freq (0 to 1 range)
    norm = (center_freq - min_freq) / (max_freq - min_freq)
    norm = max(0, min(norm, 1))  # Clamp to [0,1]

    # Linear interpolation
    tolerance = min_tol + (max_tol - min_tol) * norm
    mag_threshold = min_mag + (max_mag - min_mag) * norm

    return {
        "tolerance": round(tolerance, 2),
        "mag_threshold": round(mag_threshold, 2)
    }


# Test Values
print('DYNAMIC TEST=============>', get_dynamic_detection_params(136.1))  # Should return something like (5.0, 2000)
print('DYNAMIC TEST=============>', get_dynamic_detection_params(432))    # Should return mid-range
print('DYNAMIC TEST=============>', get_dynamic_detection_params(963))    # Should return (100.0, 90000)


def detect_peaks(freqs, magnitude, bands=CHAKRA_FREQUENCY_BANDS, debug=False):
    """Detects peaks based on dynamic per-frequency tolerance and magnitude thresholds."""
    freqs = np.asarray(freqs)
    magnitude = np.asarray(magnitude)

    if freqs.size == 0 or magnitude.size == 0:
        if debug:
            print("Empty frequency or magnitude data.")
        return []

    # Sanitize input
    valid = (
        np.isfinite(freqs) &
        np.isfinite(magnitude) &
        (freqs > 0) &
        (magnitude > 0)
    )
    freqs = freqs[valid]
    magnitude = magnitude[valid]

    if freqs.size == 0:
        if debug:
            print("No valid freq/mag pairs after sanitizing.")
        return []

    peaks = []
    matched_labels = set()

    for start, end, label, color in bands:
        center_freq = (start + end) / 2
        params = get_dynamic_detection_params(center_freq)
        tolerance = params["tolerance"]
        mag_threshold = params["mag_threshold"]

        # Search for best match in this band
        best_match = None
        best_mag = 0

        for freq, mag in zip(freqs, magnitude):
            if abs(freq - center_freq) <= tolerance and mag >= mag_threshold:
                if mag > best_mag:
                    best_match = (freq, mag, label, color)
                    best_mag = mag

        if best_match and label not in matched_labels:
            peaks.append(best_match)
            matched_labels.add(label)

            if debug:
                print(f"[PEAK DETECTED] {label} @ {best_match[0]:.1f} Hz, Mag: {best_match[1]:.1f}, Tol: {tolerance:.2f}, MinMag: {mag_threshold:.1f}")

    if debug:
        print(f"Total peaks matched: {len(peaks)} / {len(bands)}")

    return peaks


# def detect_peaks(freqs, magnitude, threshold=10000, match_rate_threshold=0.5, debug=True):
#     """Detect base frequency peaks from FFT data with harmonic suppression and match rate gating."""
#     freqs = np.asarray(freqs)
#     magnitude = np.asarray(magnitude)
#
#     if debug:
#         print("Raw freqs sample:", freqs[:10])
#         print("Raw mags sample:", magnitude[:10])
#         print("NaNs in freqs:", np.isnan(freqs).any())
#         print("NaNs in magnitude:", np.isnan(magnitude).any())
#         print("Zeros in magnitude:", np.sum(magnitude == 0))
#
#     if freqs.size == 0 or magnitude.size == 0:
#         if debug:
#             print("Match rate: 0/0 (no data)")
#         return []
#
#     # 🧼 Remove invalid entries
#     valid = (
#         np.isfinite(freqs) &
#         np.isfinite(magnitude) &
#         (freqs > 0) &
#         (magnitude > 0)
#     )
#     freqs = freqs[valid]
#     magnitude = magnitude[valid]
#
#     if freqs.size == 0 or magnitude.size == 0:
#         if debug:
#             print("Match rate: 0/0 (no usable data)")
#         return []
#
#     # 🎯 Peak detection
#     peaks = []
#     matched_peaks = 0
#     total_peaks = 0
#     skip_radius_hz = 8
#     used_freqs = []
#
#     for freq, mag in sorted(zip(freqs, magnitude), key=lambda x: -x[1]):
#         if mag < threshold:
#             continue
#         if any(abs(freq - used) < skip_radius_hz for used in used_freqs):
#             continue
#
#         total_peaks += 1
#         label, color = match_frequency_to_band(freq)
#         if label:
#             matched_peaks += 1
#             used_freqs.append(freq)
#             peaks.append((freq, mag, label, color))
#
#     # 🔒 Match rate gating
#     if total_peaks == 0 or matched_peaks == 0:
#         match_rate = 0.0
#     else:
#         match_rate = matched_peaks / total_peaks
#
#     if debug:
#         print(f"Match rate: {matched_peaks}/{total_peaks} ({match_rate:.1%})")
#
#     if match_rate < match_rate_threshold:
#         if debug:
#             print(f"[INFO] Match rate below threshold ({match_rate:.1%} < {match_rate_threshold:.1%}), suppressing detection.")
#         return []
#
#     return peaks


# def detect_peaks(freqs, magnitude, threshold_multiplier=5, debug=True):
#     """Detect peaks in the frequency spectrum based on a dynamic noise floor."""
#     freqs = np.asarray(freqs)
#     magnitude = np.asarray(magnitude)
#
#     # 🔍 Debug info
#     if debug:
#         print("Raw freqs sample:", freqs[:10])
#         print("Raw mags sample:", magnitude[:10])
#         print("NaNs in freqs:", np.isnan(freqs).any())
#         print("NaNs in magnitude:", np.isnan(magnitude).any())
#         print("Zeros in magnitude:", (magnitude == 0).sum())
#
#     if freqs.size == 0 or magnitude.size == 0:
#         if debug: print("Match rate: 0/0 (no data)")
#         return []
#
#     # 🧼 Remove invalid entries
#     valid = (
#         np.isfinite(freqs) &
#         np.isfinite(magnitude) &
#         (freqs > 0)
#     )
#     freqs = freqs[valid]
#     magnitude = magnitude[valid]
#
#     if freqs.size == 0 or magnitude.size == 0:
#         if debug: print("Match rate: 0/0 (no usable data)")
#         return []
#
#     # 💡 Replace zeros with epsilon before thresholds
#     magnitude = np.where(magnitude == 0, 1e-9, magnitude)
#
#     # 🧹 Smooth signal to reduce spikes
#     smoothed = np.convolve(magnitude, np.ones(3) / 3, mode='same')
#
#     # 📈 Dynamic thresholds with fallbacks
#     try:
#         min_mag_threshold = np.percentile(smoothed, 88)
#         if not np.isfinite(min_mag_threshold) or min_mag_threshold <= 0:
#             if debug: print("[WARN] Invalid min_mag_threshold; using fallback.")
#             min_mag_threshold = 10000
#     except Exception as e:
#         if debug: print(f"[ERROR] min_mag_threshold failed: {e}")
#         min_mag_threshold = 10000
#
#     try:
#         noise_floor = np.percentile(smoothed, 85)
#         if not np.isfinite(noise_floor) or noise_floor <= 0:
#             if debug: print("[WARN] Invalid noise_floor; using fallback.")
#             noise_floor = np.mean(smoothed) if np.mean(smoothed) > 0 else 10000
#     except Exception as e:
#         if debug: print(f"[ERROR] noise_floor failed: {e}")
#         noise_floor = 10000
#
#     threshold = noise_floor * threshold_multiplier
#     max_mag_threshold = 100000
#     min_freq = 0.1
#     max_freq = 1000
#
#     # 🎯 Peak detection
#     peaks = []
#     total_peaks = 0
#     matched_peaks = 0
#
#     for freq, mag in zip(freqs, smoothed):
#         if mag < 15000:  # Pre-cutoff  -------    MAY NEED TO ADJUST TO GET FILTERED CORRECTLY!
#             continue
#         if (
#             mag >= threshold and
#             min_mag_threshold <= mag <= max_mag_threshold and
#             min_freq <= freq <= max_freq
#         ):
#             total_peaks += 1
#             label, color = match_frequency_to_band(freq)
#             if label:
#                 matched_peaks += 1
#                 peaks.append((freq, mag, label, color))
#
#     # 📊 Match rate report
#     if debug:
#         if total_peaks > 0:
#             print(f"Match rate: {matched_peaks}/{total_peaks} ({matched_peaks / total_peaks:.1%})")
#         else:
#             print("Match rate: 0/0 (no usable peaks)")
#
#     return peaks







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


