import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from config import CHAKRA_FREQUENCY_BANDS
from collections import defaultdict
from alert_system import match_frequency_to_band


def update_frequency_count(self, freq):
    label, color = match_frequency_to_band(freq)
    if label:
        self.frequency_counts[label] += 1
        self.update_frequency_counter_display()


def update_frequency_counter_display(self):
    self.counter_text.config(state='normal')
    self.counter_text.delete('1.0', tk.END)
    self.counter_text.insert(tk.END, "🔢 Frequency Detection Counts:\n")
    for label, count in sorted(self.frequency_counts.items(), key=lambda x: -x[1]):
        self.counter_text.insert(tk.END, f"{label}: {count}\n")
    self.counter_text.config(state='disabled')


def build_gui(root, fig, start_callback, stop_callback, calibrate_silence):
    """Builds the full Tkinter + Matplotlib GUI and returns widgets as a dict."""

    # === Calibration Button ===
    calibrate_button = ttk.Button(root, text="Calibrate in Silence", command=calibrate_silence)
    calibrate_button.grid(row=0, column=3)
    calibrate_button.config(state='normal')  # ✅ Make sure it's clickable

    # === Buttons ===
    start_button = tk.Button(root, text="Start Visualization", command=start_callback)
    start_button.grid(row=0, column=1, padx=10, pady=5)

    stop_button = tk.Button(root, text="Stop Visualization", command=stop_callback)
    stop_button.grid(row=0, column=2, padx=10, pady=5)

    # === Filter Strength Controls ===
    filter_frame = ttk.LabelFrame(root, text="Filter Sensitivity", padding=10)
    filter_frame.grid(row=0, column=4, sticky='w', padx=10, pady=5)

    filter_strength_var = tk.IntVar(value=10)
    filter_label = ttk.Label(filter_frame, text="Strength:")
    filter_label.grid(row=0, column=0)

    filter_display = ttk.Label(filter_frame, textvariable=filter_strength_var, width=4, anchor='center')
    filter_display.grid(row=0, column=1)

    # Buttons are dummy for now — actual command wiring happens outside
    increase_btn = ttk.Button(filter_frame, text="▲", width=3)
    increase_btn.grid(row=0, column=2, padx=(5, 0))

    decrease_btn = ttk.Button(filter_frame, text="▼", width=3)
    decrease_btn.grid(row=0, column=3)

    # === Frequency Counter Frame ===
    counter_frame = tk.LabelFrame(root, text="Frequency Detection Count", bg="black", fg="white", padx=10, pady=10)
    counter_frame.grid(row=5, column=3, sticky='we', padx=10)

    counter_labels = {}
    frequency_counts = {}
    counter_vars = {}

    # Only one counter per unique frequency label
    unique_labels = list({label: color for _, _, label, color in CHAKRA_FREQUENCY_BANDS}.items())
    for idx, (label, color) in enumerate(unique_labels):
        frequency_counts[label] = 0
        var = tk.StringVar(value=f"{label}: 0")
        counter_vars[label] = var
        lbl = tk.Label(counter_frame, textvariable=var, foreground=color, background="black")
        lbl.grid(row=idx // 2, column=idx % 2, sticky='w', padx=5, pady=2)
        counter_labels[label] = lbl

    # === Checkbox: Alert Mode ===
    alert_var = tk.BooleanVar()
    alert_checkbox = tk.Checkbutton(root, text="Alert Mode", variable=alert_var)
    alert_checkbox.grid(row=2, column=0, columnspan=2)

    # === Status Label ===
    status_label = tk.Label(root, text="Status: Ready")
    status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=0)

    # === Log Box ===
    log_text = tk.Text(root, height=20, width=100, wrap=tk.WORD)
    log_text.grid(row=5, column=0, columnspan=2, padx=0, pady=0)
    log_text.config(state=tk.DISABLED)

    # === Alert Box ===
    alert_text = tk.Text(root, height=10, width=100, bg='black', fg='white', font=("Courier", 10))
    alert_text.grid(row=6, column=0, columnspan=2, pady=5, sticky='nsew')
    alert_text.insert('end', "⚡ Frequency Alert Log ⚡\n\n")
    alert_text.config(state='disabled')

    # === Matplotlib Canvas ===
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=6, column=3, columnspan=2, padx=10, pady=5)

    return {
        "start_button": start_button,
        "stop_button": stop_button,
        "alert_var": alert_var,
        "alert_checkbox": alert_checkbox,
        "status_label": status_label,
        "log_text": log_text,
        "alert_text": alert_text,
        "filter_strength_var": filter_strength_var,
        "increase_btn": increase_btn,
        "decrease_btn": decrease_btn,
        "canvas": canvas,
        "counter_labels": counter_vars,
        "calibrate_button": calibrate_button,
        "counter_vars": counter_vars,
        "frequency_counts": frequency_counts
    }

