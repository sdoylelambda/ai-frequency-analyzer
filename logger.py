# logger.py

from datetime import datetime


def log_to_gui(text_widget, message):
    """Logs a message to a Tkinter Text widget (read-only)."""
    if text_widget:
        text_widget.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        text_widget.insert('end', f"{timestamp} - {message}\n")
        text_widget.config(state='disabled')
        text_widget.yview('end')


def log_to_console(message):
    """Prints message to stdout (for debug or dev logging)."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{timestamp} - {message}")
