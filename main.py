import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from audio_stream import AudioStream
from fft_processor import compute_fft, detect_peaks
from alert_system import log_alert_to_file, log_alert_to_gui
from logger import log_to_gui
from gui import build_gui
from config import SAMPLE_RATE, FRAME_SIZE


class AudioVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cymatics Frequency Analyzer")

        self.audio = AudioStream()
        self.data_buffer = np.zeros(FRAME_SIZE)
        self.sample_rate = SAMPLE_RATE
        self.is_running = False
        self.filter_strength_multiplier = 10
        self.calibrated = False
        self.baseline_fft = None
        self.calibration_in_progress = False

        # Setup matplotlib figure and axes
        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.tight_layout(pad=3.0)
        self.line_waveform, = self.ax_waveform.plot([], [], lw=2)
        self.line_spectrum, = self.ax_spectrum.plot([], [], lw=2)

        # Build GUI and extract widgets
        self.widgets = build_gui(
            self.root,
            self.fig,
            self.start_visualization,
            self.stop_visualization,
            self.calibrate_silence
        )

        self.canvas = self.widgets["canvas"]
        self.alert_var = self.widgets["alert_var"]
        self.alert_text = self.widgets["alert_text"]
        self.log_text = self.widgets["log_text"]
        self.status_label = self.widgets["status_label"]
        self.calibrate_button = self.widgets["calibrate_button"]
        self.filter_strength_var = self.widgets["filter_strength_var"]
        self.frequency_counts = self.widgets["frequency_counts"]
        self.counter_vars = self.widgets["counter_vars"]

        self.widgets["increase_btn"].config(command=self.increase_filter_strength)
        self.widgets["decrease_btn"].config(command=self.decrease_filter_strength)

    def start_visualization(self):
        self.audio.open_stream()
        self.is_running = True
        self.animate()
        log_to_gui(self.log_text, "▶️ Visualization started")

    def stop_visualization(self):
        self.is_running = False
        self.audio.close_stream()
        log_to_gui(self.log_text, "⏹ Visualization stopped")

    def increase_filter_strength(self):
        self.filter_strength_multiplier += 1
        log_to_gui(self.log_text, f"Filter strength: {self.filter_strength_multiplier}")

    def decrease_filter_strength(self):
        self.filter_strength_multiplier = max(1, self.filter_strength_multiplier - 1)
        log_to_gui(self.log_text, f"Filter strength: {self.filter_strength_multiplier}")

    def calibrate_silence(self):
        if not self.is_running or self.calibration_in_progress:
            return

        self.calibration_in_progress = True
        self.calibrate_button.config(state='disabled')
        log_to_gui(self.log_text, "Calibrating... Please stay silent.")

        collected_mags = []

        def collect_frame(i=0):
            if i >= 30:
                self.baseline_fft = np.mean(collected_mags, axis=0)
                self.calibrated = True
                self.calibration_in_progress = False
                self.calibrate_button.config(state='normal')
                log_to_gui(self.log_text, "✅ Baseline noise profile calibrated.")
                return

            try:
                data = self.audio.read_data()
                freqs, mag = compute_fft(data, self.sample_rate)
                collected_mags.append(mag)
                self.root.after(30, lambda: collect_frame(i + 1))
            except Exception as e:
                log_to_gui(self.log_text, f"Calibration failed: {e}")
                self.calibration_in_progress = False
                self.calibrate_button.config(state='normal')

        self.root.after(100, collect_frame)

    def animate(self):
        if not self.is_running:
            return

        try:
            self.data_buffer = self.audio.read_data()
        except Exception as e:
            log_to_gui(self.log_text, f"Audio read error: {e}")
            return

        self.line_waveform.set_ydata(self.data_buffer)
        self.line_waveform.set_xdata(np.arange(len(self.data_buffer)))
        self.ax_waveform.set_ylim(-4000, 4000)
        self.ax_waveform.set_xlim(0, len(self.data_buffer))

        freqs, mag = compute_fft(self.data_buffer, self.sample_rate)
        adjusted_mag = mag if self.baseline_fft is None else np.clip(mag - self.baseline_fft, 0, None)

        self.ax_spectrum.clear()
        self.ax_spectrum.plot(freqs, adjusted_mag, color='cyan')
        self.ax_spectrum.set_xlim(0, 1000)
        self.ax_spectrum.set_ylim(0, np.max(adjusted_mag) + 100)

        threshold = 10000 * self.filter_strength_multiplier

        for freq, mag, label, color in detect_peaks(freqs, adjusted_mag, threshold=threshold):
            log_alert_to_file(freq, mag, label)
            log_alert_to_gui(self.alert_text, f"{label}: {freq:.1f} Hz (Mag: {mag:.0f})", color or "white")
            self.ax_spectrum.axvline(freq, color=color or "white", linestyle="--", alpha=0.8)

            if self.calibrated and label in self.frequency_counts:
                self.frequency_counts[label] += 1
                self.counter_vars[label].set(f"{label}: {self.frequency_counts[label]}")

        self.canvas.draw()
        self.root.after(50, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioVisualizerApp(root)
    root.mainloop()


# import tkinter as tk
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#
# from audio_stream import AudioStream
# from fft_processor import compute_fft, detect_peaks
# from alert_system import log_alert_to_file, log_alert_to_gui
# from logger import log_to_gui
# from gui import build_gui
# from config import SAMPLE_RATE, FRAME_SIZE
#
#
# class AudioVisualizerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Cymatics Frequency Analyzer")
#
#         self.audio = AudioStream()
#         self.data_buffer = np.zeros(FRAME_SIZE)
#         self.sample_rate = SAMPLE_RATE
#         self.is_running = False
#         self.filter_strength_multiplier = 10
#         self.calibrated = False
#         self.baseline_fft = None
#         self.calibration_in_progress = False
#
#         # Setup matplotlib figure and axes
#         self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(1, 2, figsize=(12, 5))
#         self.fig.tight_layout(pad=3.0)
#         self.line_waveform, = self.ax_waveform.plot([], [], lw=2)
#         self.line_spectrum, = self.ax_spectrum.plot([], [], lw=2)
#
#         # Build GUI and extract widgets
#         self.widgets = build_gui(
#             self.root,
#             self.fig,
#             self.start_visualization,
#             self.stop_visualization,
#             self.calibrate_silence
#         )
#
#         self.canvas = self.widgets["canvas"]
#         self.alert_var = self.widgets["alert_var"]
#         self.alert_text = self.widgets["alert_text"]
#         self.log_text = self.widgets["log_text"]
#         self.status_label = self.widgets["status_label"]
#         self.calibrate_button = self.widgets["calibrate_button"]
#         self.filter_strength_var = self.widgets["filter_strength_var"]
#         self.frequency_counts = self.widgets["frequency_counts"]
#         self.counter_vars = self.widgets["counter_vars"]
#
#         self.widgets["increase_btn"].config(command=self.increase_filter_strength)
#         self.widgets["decrease_btn"].config(command=self.decrease_filter_strength)
#
#     def start_visualization(self):
#         self.audio.open_stream()
#         self.is_running = True
#         self.animate()
#         log_to_gui(self.log_text, "▶️ Visualization started")
#
#     def stop_visualization(self):
#         self.is_running = False
#         self.audio.close_stream()
#         log_to_gui(self.log_text, "⏹ Visualization stopped")
#
#     def increase_filter_strength(self):
#         self.filter_strength_multiplier += 1
#         log_to_gui(self.log_text, f"Filter strength: {self.filter_strength_multiplier}")
#
#     def decrease_filter_strength(self):
#         self.filter_strength_multiplier = max(1, self.filter_strength_multiplier - 1)
#         log_to_gui(self.log_text, f"Filter strength: {self.filter_strength_multiplier}")
#
#     def calibrate_silence(self):
#         if not self.is_running or self.calibration_in_progress:
#             return
#
#         self.calibration_in_progress = True
#         self.calibrate_button.config(state='disabled')
#         log_to_gui(self.log_text, "Calibrating... Please stay silent.")
#
#         collected_mags = []
#
#         def collect_frame(i=0):
#             if i >= 30:
#                 self.baseline_fft = np.mean(collected_mags, axis=0)
#                 self.calibrated = True
#                 self.calibration_in_progress = False
#                 self.calibrate_button.config(state='normal')
#                 log_to_gui(self.log_text, "✅ Baseline noise profile calibrated.")
#                 return
#
#             try:
#                 data = self.audio.read_data()
#                 freqs, mag = compute_fft(data, self.sample_rate)
#                 collected_mags.append(mag)
#                 self.root.after(30, lambda: collect_frame(i + 1))
#             except Exception as e:
#                 log_to_gui(self.log_text, f"Calibration failed: {e}")
#                 self.calibration_in_progress = False
#                 self.calibrate_button.config(state='normal')
#
#         self.root.after(100, collect_frame)
#
#     def animate(self):
#         if not self.is_running:
#             return
#
#         try:
#             self.data_buffer = self.audio.read_data()
#         except Exception as e:
#             log_to_gui(self.log_text, f"Audio read error: {e}")
#             return
#
#         self.line_waveform.set_ydata(self.data_buffer)
#         self.line_waveform.set_xdata(np.arange(len(self.data_buffer)))
#         self.ax_waveform.set_ylim(-4000, 4000)
#         self.ax_waveform.set_xlim(0, len(self.data_buffer))
#
#         freqs, mag = compute_fft(self.data_buffer, self.sample_rate)
#         adjusted_mag = mag if self.baseline_fft is None else np.clip(mag - self.baseline_fft, 0, None)
#
#         self.ax_spectrum.clear()
#         self.ax_spectrum.plot(freqs, adjusted_mag, color='cyan')
#         self.ax_spectrum.set_xlim(0, 1000)
#         self.ax_spectrum.set_ylim(0, np.max(adjusted_mag) + 100)
#
#         threshold = 10000 * self.filter_strength_multiplier
#
#         for freq, mag, label, color in detect_peaks(freqs, adjusted_mag, debug=True):
#             log_alert_to_file(freq, mag, label)
#             log_alert_to_gui(self.alert_text, f"{label}: {freq:.1f} Hz (Mag: {mag:.0f})", color or "white")
#             self.ax_spectrum.axvline(freq, color=color or "white", linestyle="--", alpha=0.8)
#
#             if self.calibrated and label in self.frequency_counts:
#                 self.frequency_counts[label] += 1
#                 self.counter_vars[label].set(f"{label}: {self.frequency_counts[label]}")
#
#         self.canvas.draw()
#         self.root.after(50, self.animate)
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = AudioVisualizerApp(root)
#     root.mainloop()
