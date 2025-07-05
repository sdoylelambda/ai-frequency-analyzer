# gui.py

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def build_gui(root, fig, start_callback, stop_callback):
    """Builds the full Tkinter + Matplotlib GUI and returns widgets as a dict."""

    # === Buttons ===
    start_button = tk.Button(root, text="Start Visualization", command=start_callback)
    start_button.grid(row=0, column=0, padx=10, pady=5)

    stop_button = tk.Button(root, text="Stop Visualization", command=stop_callback)
    stop_button.grid(row=0, column=1, padx=10, pady=5)

    # === Filter Strength Controls ===
    filter_frame = ttk.LabelFrame(root, text="Filter Sensitivity", padding=10)
    filter_frame.grid(row=0, column=3, sticky='w', padx=10, pady=5)

    filter_strength_var = tk.IntVar(value=3)
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
    counter_frame = ttk.LabelFrame(root, text="Frequency Detection Count", padding=10)
    counter_frame.grid(row=5, column=3, sticky='we', padx=10)

    counter_labels = {}  # Dictionary to store labels for dynamic updating

    from config import CHAKRA_FREQUENCY_BANDS
    for idx, (_, _, label, color) in enumerate(CHAKRA_FREQUENCY_BANDS):
        text_var = tk.StringVar(value=f"{label}: 0")
        lbl = ttk.Label(counter_frame, textvariable=text_var, foreground=color)
        lbl.grid(row=idx // 2, column=idx % 2, sticky='w', padx=5, pady=2)
        counter_labels[label] = text_var

    # === Checkbox: Alert Mode ===
    alert_var = tk.BooleanVar()
    alert_checkbox = tk.Checkbutton(root, text="Alert Mode", variable=alert_var)
    alert_checkbox.grid(row=2, column=0, columnspan=2)

    # === Status Label ===
    status_label = tk.Label(root, text="Status: Ready")
    status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=0)

    # === Log Box ===
    log_text = tk.Text(root, height=10, width=50, wrap=tk.WORD)
    log_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
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
        "counter_labels": counter_labels
    }
