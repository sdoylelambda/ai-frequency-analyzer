import tkinter as tk
import threading
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.config import CHAKRA_FREQUENCY_BANDS
from src.alert_system import match_frequency_to_band
from TonePlayer import TonePlayer


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

    # === Instructions Label ===
    status_label = tk.Label(root, text="Instructions")
    status_label.grid(row=1, column=2, columnspan=2, padx=2, pady=2)
    status_label = tk.Label(root, text="1 - Click Start Simulation Button")
    status_label.grid(row=1, column=3, columnspan=2, padx=2, pady=2)
    status_label = tk.Label(root, text="2 - Click Calibrate In Silence Button")
    status_label.grid(row=2, column=3, columnspan=2, padx=2, pady=2)
    status_label = tk.Label(root, text="3 - Play music, talk, etc.")
    status_label.grid(row=3, column=3, columnspan=2, padx=2, pady=2)
    status_label = tk.Label(root, text="4 - Click Generate Review Button.")
    status_label.grid(row=1, column=4, columnspan=2, padx=2, pady=2)
    status_label = tk.Label(root, text="5 - Click AI Review Button.")
    status_label.grid(row=2, column=4, columnspan=2, padx=2, pady=2)
    status_label = tk.Label(root, text="6 - Paste in text box and press enter.")
    status_label.grid(row=3, column=4, columnspan=2, padx=2, pady=2)

    # === Calibration Button ===
    calibrate_button = tk.Button(root, text="Calibrate in Silence", command=calibrate_silence)
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
    outer_frame = tk.LabelFrame(
        root,
        text="Frequency Detection Count",
        bg="black",
        fg="white",
        padx=10, pady=10
    )
    outer_frame.grid(row=5, column=3, sticky='nsew', padx=2, pady=2)

    outer_frame.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)

    # ⚠ Renamed canvas → freq_canvas
    freq_canvas = tk.Canvas(outer_frame, bg="black", highlightthickness=0)
    freq_canvas.grid(row=0, column=0, sticky="nsew")

    freq_canvas.config(width=1000)

    scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=freq_canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    freq_canvas.configure(yscrollcommand=scrollbar.set)

    # ⚠ Renamed scroll window
    scrollable_frame = tk.Frame(freq_canvas, bg="black")
    canvas_window = freq_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def update_scroll_region(event=None):
        freq_canvas.configure(scrollregion=freq_canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", update_scroll_region)

    def resize_canvas(event):
        freq_canvas.itemconfig(canvas_window, width=event.width)

    freq_canvas.bind("<Configure>", resize_canvas)

    # --- Mouse wheel support ---
    def _on_mousewheel(event):
        freq_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_mac(event):
        freq_canvas.yview_scroll(int(-event.delta), "units")

    def _on_mousewheel_linux(event):
        if event.num == 4:
            freq_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            freq_canvas.yview_scroll(1, "units")

    freq_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    freq_canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel_mac)
    freq_canvas.bind_all("<Button-4>", _on_mousewheel_linux)
    freq_canvas.bind_all("<Button-5>", _on_mousewheel_linux)

    # ---------------------------------------------------------------------
    # Frequency Counter Items
    # ---------------------------------------------------------------------

    counter_labels = {}
    frequency_counts = {}
    counter_vars = {}

    def on_audio_stopped():
        single_playing.set(False)
        sweep_playing.set(False)

        btn_single.config(text="▶️ Play")
        btn_sweep.config(text="▶️ Play Tone(s)")

    tone_player = TonePlayer()
    tone_player.set_on_stop_callback(on_audio_stopped)

    for idx, (low, high, label, color) in enumerate(CHAKRA_FREQUENCY_BANDS):

        # Choose a deterministic test frequency
        if "Hz" in label:
            # Try to extract explicit anchor like "432 Hz"
            parts = label.split()
            freq_candidates = [p.replace("Hz", "") for p in parts if p.replace('.', '').isdigit()]
            freq = float(freq_candidates[0]) if freq_candidates else (low + high) / 2
        else:
            freq = (low + high) / 2  # fallback: band center

        row = idx // 2
        col = (idx % 2) * 3

        frequency_counts[label] = 0
        var = tk.StringVar(value=f"{label}: 0")
        counter_vars[label] = var

        lbl = tk.Label(
            scrollable_frame,
            textvariable=var,
            fg=color,
            bg="black"
        )
        lbl.grid(row=row, column=col, sticky='w', padx=5, pady=2)
        counter_labels[label] = lbl

        btn_test_5s = tk.Button(
            scrollable_frame,
            text="▶️ 5s",
            bg="gray20",
            fg="white",
            width=4,
            command=lambda f=freq: threading.Thread(
                target=tone_player.play_tone_once,
                args=(f, 5),
                daemon=True
            ).start()
        )
        btn_test_5s.grid(row=row, column=col + 1, padx=5)

        btn_toggle = tk.Button(
            scrollable_frame,
            text="🔁",
            bg="gray30",
            fg="white",
            width=3,
            command=lambda f=freq: tone_player.toggle_tone(f)
        )
        btn_toggle.grid(row=row, column=col + 2, padx=5)

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

    single_freq_var = tk.StringVar(value="432")
    single_dur_var = tk.StringVar(value="5")
    single_playing = tk.BooleanVar(value=False)

    def toggle_single_tone():
        try:
            freq = float(single_freq_var.get())
            duration = float(single_dur_var.get())
            if freq <= 0 or duration <= 0:
                raise ValueError
        except ValueError:
            print("Invalid single tone parameters")
            return

        if tone_player.is_playing:
            tone_player.stop()
            single_playing.set(False)
            btn_single.config(text="▶️ Play")
            return

        tone_player.toggle_timed_tone(freq, duration)
        single_playing.set(True)
        btn_single.config(text="⏹ Stop")
        print(f"Playing {freq} Hz for {duration} s")

    single_frame = tk.Frame(scrollable_frame, bg="black")
    single_frame.grid(columnspan=3, pady=10, sticky="w", row=1)

    tk.Label(single_frame, text="Single Tone:", fg="white", bg="black").pack(side="left", padx=5)

    tk.Entry(single_frame, textvariable=single_freq_var, width=6).pack(side="left")
    tk.Label(single_frame, text="Hz", fg="white", bg="black").pack(side="left", padx=5)

    tk.Label(single_frame, text="Duration (s):", fg="white", bg="black").pack(side="left", padx=5)
    tk.Entry(single_frame, textvariable=single_dur_var, width=4).pack(side="left")

    btn_single = tk.Button(
        single_frame,
        text="▶️ Play",
        bg="gray20",
        fg="white",
        width=10,
        command=toggle_single_tone
    )
    btn_single.pack(side="left", padx=5)

    # =========================
    # Frequency Sweep Controls
    # =========================

    sweep_start_var = tk.StringVar(value="80")
    sweep_end_var = tk.StringVar(value="8000")
    sweep_duration_var = tk.StringVar(value="10")
    sweep_playing = tk.BooleanVar(value=False)

    def toggle_sweep():
        try:
            start_str = sweep_start_var.get().strip()
            end_str = sweep_end_var.get().strip()
            duration = float(sweep_duration_var.get())

            start = float(start_str)
            end = float(end_str) if end_str else None

            if start <= 0 or duration <= 0:
                raise ValueError

        except ValueError:
            print("Invalid sweep parameters")
            return

        # --- STOP ---
        if tone_player.is_playing:
            tone_player.stop()
            sweep_playing.set(False)
            btn_sweep.config(text="▶️ Play")
            return

        # --- SINGLE FREQUENCY MODE ---
        if end is None or abs(end - start) < 0.01:
            tone_player.toggle_single_tone(start)
            sweep_playing.set(True)
            btn_sweep.config(text="⏹ Stop")
            print(f"Playing single tone: {start} Hz")
            return

        # --- SWEEP MODE ---
        if end <= start:
            print("End frequency must be greater than start")
            return

        tone_player.toggle_sweep(start, end, duration)
        sweep_playing.set(True)
        btn_sweep.config(text="⏹ Stop Sweep")
        print(f"Sweeping {start} → {end} Hz")

    sweep_frame = tk.Frame(scrollable_frame, bg="black")
    sweep_frame.grid(columnspan=3, pady=10, sticky="w", row=0)

    tk.Label(sweep_frame, text="Sweep:", fg="white", bg="black").pack(side="left", padx=5)

    tk.Entry(sweep_frame, textvariable=sweep_start_var, width=6).pack(side="left")
    tk.Label(sweep_frame, text="→", fg="white", bg="black").pack(side="left", padx=2)

    tk.Entry(sweep_frame, textvariable=sweep_end_var, width=6).pack(side="left")
    tk.Label(sweep_frame, text="Hz", fg="white", bg="black").pack(side="left", padx=5)

    tk.Label(sweep_frame, text="Duration (s):", fg="white", bg="black").pack(side="left", padx=5)
    tk.Entry(sweep_frame, textvariable=sweep_duration_var, width=4).pack(side="left")

    btn_sweep = tk.Button(
        sweep_frame,
        text="▶️ Play Tone(s)",
        bg="gray20",
        fg="white",
        width=10,
        command=toggle_sweep
    )
    btn_sweep.pack(side="left", padx=5)

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

