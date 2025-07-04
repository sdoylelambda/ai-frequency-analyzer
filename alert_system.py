# alert_system.py

from datetime import datetime
from config import CHAKRA_FREQUENCY_BANDS

def match_frequency_to_band(freq):
    """Returns the label and color of a matching frequency band, or None if no match."""
    for start, end, label, color in CHAKRA_FREQUENCY_BANDS:
        if start <= freq <= (end if end != start else start + 3):
            return label, color
    return None, None


def log_alert_to_file(frequency, magnitude, label):
    """Logs a frequency alert to a .log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("frequency_alerts.log", "a") as log_file:
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
