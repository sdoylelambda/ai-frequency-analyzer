from datetime import datetime
from src.utils.config import CHAKRA_FREQUENCY_BANDS


def match_frequency_to_band(freq, bands=CHAKRA_FREQUENCY_BANDS, global_tolerance=0.02, debug=False):
    closest = None
    min_diff = float('inf')

    for start, end, label, color in bands:
        if not (start < end):
            continue

        center = (start + end) / 2
        tolerance = global_tolerance * center

        diff = abs(freq - center)
        if diff <= tolerance:
            return label, color
        if diff < min_diff:
            closest = (label, center, diff)
            min_diff = diff

    if debug and closest:
        label, center, diff = closest
        print(f"[DEBUG] Closest band: {label} (center {center:.1f} Hz), diff: {diff:.2f} Hz")

    return None, None


def log_alert_to_file(frequency, magnitude, label):
    """Logs a frequency alert to a .log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("../src/logs/frequency_alerts_testing.log", "a") as log_file:
        log_line = f"[{timestamp}] ALERT: {label or 'Unknown'} — {frequency:.1f} Hz, Magnitude: {magnitude:.1f}\n"
        log_file.write(log_line)


def log_alert_to_gui(alert_widget, message, color="white"):
    """Safely appends a message to the GUI alert text box (Tkinter Text widget)."""
    if alert_widget:
        alert_widget.configure(state='normal')
        alert_widget.insert('end', message + "\n", color)
        alert_widget.tag_config(color, foreground=color)
        alert_widget.see('end')
        alert_widget.configure(state='disabled')
