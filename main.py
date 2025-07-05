# main.py

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from audio_stream import AudioStream
from fft_processor import compute_fft, detect_peaks
from alert_system import log_alert_to_file, log_alert_to_gui
from logger import log_to_gui, log_to_console
from gui import build_gui
from config import SAMPLE_RATE, FRAME_SIZE, CHAKRA_FREQUENCY_BANDS


class AudioVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cymatics Frequency Analyzer")

        self.audio = AudioStream()
        self.data_buffer = np.zeros(FRAME_SIZE)
        self.is_running = False
        self.filter_strength_multiplier = 3

        # Matplotlib Setup
        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(2, 1, figsize=(10, 10))
        self.fig.tight_layout(pad=3.0)
        self.line_waveform, = self.ax_waveform.plot([], [], lw=2)
        self.line_spectrum, = self.ax_spectrum.plot([], [], lw=2)

        # Build GUI
        self.widgets = build_gui(
            self.root,
            self.fig,
            self.start_visualization,
            self.stop_visualization
        )

        # Wire up widget references
        self.alert_var = self.widgets["alert_var"]
        self.log_text = self.widgets["log_text"]
        self.status_label = self.widgets["status_label"]
        self.alert_text = self.widgets["alert_text"]
        self.filter_strength_var = self.widgets["filter_strength_var"]

        self.widgets["increase_btn"].config(command=self.increase_filter_strength)
        self.widgets["decrease_btn"].config(command=self.decrease_filter_strength)

    def increase_filter_strength(self):
        self.filter_strength_multiplier += 1
        log_to_console(f"Filter strength: {self.filter_strength_multiplier}x")

    def decrease_filter_strength(self):
        if self.filter_strength_multiplier > 1:
            self.filter_strength_multiplier -= 1
            log_to_console(f"Filter strength: {self.filter_strength_multiplier}x")

    def start_visualization(self):
        try:
            self.audio.open_stream()
        except RuntimeError as e:
            log_to_gui(self.log_text, f"Error: {e}")
            return

        self.is_running = True
        self.status_label.config(text="Status: Visualizing...")
        log_to_gui(self.log_text, "Visualization started.")
        self.visualize_audio()

    def stop_visualization(self):
        self.is_running = False
        self.audio.close()
        self.status_label.config(text="Status: Stopped")
        log_to_gui(self.log_text, "Visualization stopped.")

    def visualize_audio(self):
        import matplotlib.animation as animation
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_line,
            blit=True,
            cache_frame_data=False,
            interval=30
        )
        self.read_audio_data()

    def read_audio_data(self):
        if not self.is_running:
            return

        try:
            self.data_buffer = self.audio.read_data()
            if self.alert_var.get():
                pass  # future real-time hidden message logic
        except Exception as e:
            self.status_label.config(text="Mic Error")
            self.stop_visualization()
            return

        self.root.after(10, self.read_audio_data)

    def update_line(self, frame):
        self.line_waveform.set_ydata(self.data_buffer)
        self.line_waveform.set_xdata(np.arange(len(self.data_buffer)))
        self.ax_waveform.set_ylim(-4000, 4000)
        self.ax_waveform.set_xlim(0, len(self.data_buffer))

        freqs, magnitude = compute_fft(self.data_buffer)
        self.line_spectrum.set_data(freqs, magnitude)
        self.ax_spectrum.set_xlim(0, 5000)
        self.ax_spectrum.set_ylim(0, np.max(magnitude) + 100)

        # Clear old visuals
        for artist in list(self.ax_spectrum.artists) + list(self.ax_spectrum.patches):
            artist.remove()

        # Detect and render peaks
        peaks = detect_peaks(freqs, magnitude, threshold_multiplier=self.filter_strength_multiplier)
        for freq, mag, label, color in peaks:
            alert_msg = f"{label or 'Peak'}: {freq:.1f} Hz (Mag: {mag:.0f})"
            log_alert_to_file(freq, mag, label)
            log_alert_to_gui(self.alert_text, alert_msg, color or "white")
            self.ax_spectrum.plot(freq, mag, 'ro' if "⚠" in (label or "") else 'go')
            self.ax_spectrum.axvline(freq, color=color or 'white', linestyle='--', alpha=0.8)

        return self.line_waveform, self.line_spectrum


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioVisualizerApp(root)
    root.mainloop()




# import numpy as np
# import pyaudio
# import struct
# import tkinter as tk
# from tkinter import ttk
# from tkinter import messagebox
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from datetime import datetime
# from alert_system import match_frequency_to_band, log_alert_to_file, log_alert_to_gui
# from fft_processor import compute_fft, detect_peaks
# from alert_system import log_alert_to_file, log_alert_to_gui
# from audio_stream import AudioStream
# from gui import build_gui
# from logger import log_to_gui, log_to_console
#
#
# class AudioVisualizerApp:
#     def __init__(self, root):
#         self.audio = AudioStream()
#         self.alert_text = None
#         self.canvas = None
#         self.log_text = None
#         self.log_label = None
#         self.alert_checkbox = None
#         self.alert_var = None
#         self.start_button = None
#         self.stop_button = None
#         self.status_label = None
#         self.filter_strength = None
#         self.widgets = None
#         self.root = root
#         self.root.title("Cymatics Sound Visualization")
#         self.filter_strength_multiplier = 2  # Or whatever your default is
#
#         # Matplotlib Setup: Two vertically stacked subplots
#         self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(2, 1, figsize=(10, 10))
#         self.fig.tight_layout(pad=3.0)
#
#         # Create the waveform line
#         self.line_waveform, = self.ax_waveform.plot([], [], lw=2)
#         self.ax_waveform.set_title("Audio Waveform")
#         self.ax_waveform.set_xlabel("Sample Points")
#         self.ax_waveform.set_ylabel("Amplitude")
#         self.ax_waveform.set_xlim(0, 1024)
#         self.ax_waveform.set_ylim(-4000, 4000)
#
#         # Create the frequency spectrum line
#         self.line_spectrum, = self.ax_spectrum.plot([], [], lw=2)
#         self.ax_spectrum.set_title("Frequency Spectrum")
#         self.ax_spectrum.set_xlabel("Frequency (Hz)")
#         self.ax_spectrum.set_ylabel("Magnitude")
#         self.ax_spectrum.set_xlim(0, 5000)  # Nyquist limit for 44100 Hz sample rate
#         self.ax_spectrum.set_xlim(0, 5000)  # Nyquist limit for 44100 Hz sample rate
#         self.ax_spectrum.set_ylim(0, 1000)
#
#         # GUI Setup
#         self.setup_gui()
#
#         # === Filter Control Frame ===
#         self.filter_frame = ttk.LabelFrame(self.root, text="Filter Sensitivity", padding=10)
#         self.filter_frame.grid(row=1, column=0, sticky='w', padx=10, pady=10)
#
#         self.filter_strength_var = tk.IntVar(value=self.filter_strength)
#
#         self.filter_label = ttk.Label(self.filter_frame, text="Strength:")
#         self.filter_label.grid(row=0, column=0)
#
#         self.filter_display = ttk.Label(self.filter_frame, textvariable=self.filter_strength_var, width=4,
#                                         anchor='center')
#         self.filter_display.grid(row=0, column=1)
#
#         self.increase_btn = ttk.Button(self.filter_frame, text="▲", command=self.increase_filter_strength, width=3)
#         self.increase_btn.grid(row=0, column=2, padx=(5, 0))
#
#         self.decrease_btn = ttk.Button(self.filter_frame, text="▼", command=self.decrease_filter_strength, width=3)
#         self.decrease_btn.grid(row=0, column=3)
#
#         # Audio Stream Setup
#         self.stream = None
#         self.is_running = False
#
#         # Visualization Data
#         self.data_buffer = np.zeros(1024)
#
#         # Initialize Animation
#         self.ani = None
#         self.freq_labels = []
#
#     def increase_filter_strength(self):
#         self.filter_strength_multiplier += 1
#         print(f"Filter sensitivity increased to {self.filter_strength_multiplier}x")
#
#     def decrease_filter_strength(self):
#         if self.filter_strength_multiplier > 1:
#             self.filter_strength_multiplier -= 1
#             print(f"Filter sensitivity decreased to {self.filter_strength_multiplier}x")
#
#     def setup_gui(self):
#         # Add Start and Stop buttons
#         self.start_button = tk.Button(self.root, text="Start Visualization", command=self.start_visualization)
#         self.start_button.grid(row=0, column=0, padx=10, pady=10)
#
#         self.stop_button = tk.Button(self.root, text="Stop Visualization", command=self.stop_visualization)
#         self.stop_button.grid(row=0, column=1, padx=10, pady=10)
#
#         # Add Checkbox for Alert Mode
#         self.alert_var = tk.BooleanVar()
#         self.alert_checkbox = tk.Checkbutton(self.root, text="Alert Mode", variable=self.alert_var)
#         self.alert_checkbox.grid(row=1, column=0, columnspan=2)
#
#         # Add Status Label
#         self.status_label = tk.Label(self.root, text="Status: Ready")
#         self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
#
#         # Add Message Log
#         self.log_label = tk.Label(self.root, text="Log:")
#         self.log_label.grid(row=3, column=0, padx=10, pady=10)
#
#         self.log_text = tk.Text(self.root, height=10, width=50, wrap=tk.WORD)
#         self.log_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
#         self.log_text.config(state=tk.DISABLED)  # Set as read-only initially
#
#         # Matplotlib canvas
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
#         self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)
#
#         # Tune Out Noise/background frequencies
#         tk.Label(self.root, text="Filter Sensitivity:").grid(row=99, column=0, sticky='w')
#
#         self.filter_strength_var = tk.DoubleVar(value=5.0)
#         filter_spinbox = tk.Spinbox(
#             self.root,
#             from_=1.0,
#             to=20.0,
#             increment=0.5,
#             textvariable=self.filter_strength_var,
#             width=5
#         )
#         filter_spinbox.grid(row=99, column=10, sticky='w')
#
#         # Alert display box
#         self.alert_text = tk.Text(self.root, height=10, width=100, bg='black', fg='white', font=("Courier", 10))
#         self.alert_text.grid(row=3, column=0, columnspan=2, pady=5, sticky='nsew')
#         self.alert_text.insert(tk.END, "⚡ Frequency Alert Log ⚡\n\n")
#         self.alert_text.configure(state='disabled')
#
#     def log_message(self, message):
#         """Logs messages to the GUI's text area."""
#         log_to_gui(self.log_text, message)
#         log_to_console(message)
#
#     def start_visualization(self):
#         """Start the audio visualization."""
#         try:
#             self.audio.open_stream()
#         except RuntimeError as e:
#             messagebox.showerror("Error", str(e))
#             self.stop_visualization()
#             return
#
#     def stop_visualization(self):
#         """Stop the audio visualization."""
#         self.audio.close()
#         # self.audio.terminate()
#
#     def visualize_audio(self):
#         """Visualizes the audio data and sets up the animation."""
#         p = pyaudio.PyAudio()
#         input_device_index = self.get_input_device_index(p)
#
#         if input_device_index is None:
#             messagebox.showerror("Error", "No input device found.")
#             self.stop_visualization()
#             return
#
#         self.stream = p.open(format=pyaudio.paInt16,
#                              channels=1,
#                              rate=44100,
#                              input=True,
#                              frames_per_buffer=1024,
#                              input_device_index=input_device_index)
#
#         self.ani = animation.FuncAnimation(
#             self.fig,
#             self.update_line,
#             blit=True,
#             cache_frame_data=False,
#             interval=30  # Control frame rate (lower value means smoother)
#         )
#
#         self.widgets = build_gui(
#             self.root,
#             self.fig,
#             self.start_visualization,
#             self.stop_visualization
#         )
#
#         # Attach widgets to self for easy access
#         self.alert_var = self.widgets["alert_var"]
#         self.log_text = self.widgets["log_text"]
#         self.status_label = self.widgets["status_label"]
#         self.alert_text = self.widgets["alert_text"]
#         self.filter_strength_var = self.widgets["filter_strength_var"]
#
#         self.widgets["increase_btn"].config(command=self.increase_filter_strength)
#         self.widgets["decrease_btn"].config(command=self.decrease_filter_strength)
#
#         self.read_audio_data()
#
#     def get_input_device_index(self, p):
#         """Gets the input device index."""
#         for i in range(p.get_device_count()):
#             device_info = p.get_device_info_by_index(i)
#             if device_info.get('maxInputChannels') > 0:
#                 print(f"Using device: {device_info['name']}")
#                 return i
#         return None
#
#     def read_audio_data(self):
#         """Read audio data from the microphone."""
#         try:
#             self.data_buffer = self.audio.read_data()
#             # continue FFT, alerts, etc...
#         except OSError:
#             self.status_label.config(text="Status: Mic Error")
#             self.stop_visualization()
#
#     def check_for_hidden_messages(self, data):
#         """Checks for hidden messages in the audio data."""
#         # Placeholder for hidden message detection
#         # In a real implementation, you could analyze the data and trigger alerts
#         self.log_message("Checking for hidden messages...")
#
#     def alert_log(self, message, color="white"):
#         self.alert_text.configure(state='normal')
#         self.alert_text.insert(tk.END, message + "\n", color)
#         self.alert_text.tag_config(color, foreground=color)
#         self.alert_text.see(tk.END)
#         self.alert_text.configure(state='disabled')
#
#     def update_line(self, frame):
#         # Update waveform
#         self.line_waveform.set_ydata(self.data_buffer)
#         self.line_waveform.set_xdata(np.arange(len(self.data_buffer)))
#         self.ax_waveform.set_ylim(-4000, 4000)
#         self.ax_waveform.set_xlim(0, len(self.data_buffer))
#
#         # Compute FFT
#         freqs, magnitude = compute_fft(self.data_buffer)
#         self.line_spectrum.set_data(freqs, magnitude)
#         self.ax_spectrum.set_xlim(0, 5000)
#         self.ax_spectrum.set_ylim(0, np.max(magnitude) + 100)
#
#         # Clear old highlights
#         for artist in list(self.ax_spectrum.artists) + list(self.ax_spectrum.patches):
#             artist.remove()
#
#         # Detect peaks
#         peaks = detect_peaks(freqs, magnitude, threshold_multiplier=self.filter_strength_multiplier)
#
#         for freq_val, mag, label, color in peaks:
#             alert_msg = f"{label or 'Peak'}: {freq_val:.1f} Hz (Mag: {mag:.0f})"
#             log_alert_to_file(freq_val, mag, label)
#             log_alert_to_gui(self.alert_text, alert_msg, color or "white")
#             self.ax_spectrum.plot(freq_val, mag, 'ro' if "⚠" in (label or "") else 'go')
#             self.ax_spectrum.axvline(freq_val, color=color or 'white', linestyle='--', alpha=0.8)
#
#         return self.line_waveform, self.line_spectrum
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = AudioVisualizerApp(root)
#     root.mainloop()

# Code Walkthrough:
# 1. GUI Setup:
# We initialize a Tkinter window and create buttons for starting and stopping the visualization.
#
# A Detection Mode dropdown allows the user to choose between:
#
# Simple Threshold: Alerts on high amplitude (adjustable by slider).
#
# Frequency Analysis: Uses Fast Fourier Transform (FFT) to detect dominant frequencies.
#
# The Log Box records detected messages with timestamps.
#
# 2. Audio Setup:
# We use PyAudio to capture microphone input.
#
# The audio stream is configured for:
#
# Format: 16-bit integer (paInt16)
#
# Channels: 1 (Mono)
#
# Sample Rate: 44100 Hz
#
# Buffer Size: 1024 samples per frame
#
# 3. Visualization:
# The audio is visualized using Matplotlib in a live animated graph.
#
# The graph shows the real-time amplitude of the captured sound waves.
#
# 4. Hidden Message Detection:
# The detect_hidden_messages() method uses the selected mode:
#
# Simple Threshold: Compares the audio amplitude against a threshold value.
#
# If the amplitude exceeds the threshold, an alert is logged.
#
# Frequency Analysis: Uses FFT to identify the dominant frequency of the sound.
#
# It logs the detected frequency in the log box.
#
# 5. Error Handling and Cleanup:
# The code gracefully handles microphone errors and stops visualization without crashing.
#
# Proper logging ensures transparency about what the app is detecting.


# import numpy as np
# import pyaudio
# import struct
# import tkinter as tk
# from tkinter import messagebox, ttk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from datetime import datetime
#
# class AudioVisualizerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Cymatics Sound Visualization")
#
#         # Matplotlib Setup
#         self.fig, self.ax = plt.subplots()
#         self.ax.set_title("Cymatics Sound Visualization")
#         self.ax.set_xlabel("Sample Points")
#         self.ax.set_ylabel("Amplitude")
#         self.line, = self.ax.plot([], [], lw=2)
#
#         # GUI Setup
#         self.setup_gui()
#
#         # Audio Stream Setup
#         self.stream = None
#         self.is_running = False
#
#         # Visualization Data
#         self.data_buffer = np.zeros(1024)
#
#         # Initialize Animation
#         self.ani = None
#
#     def setup_gui(self):
#         # Add Start and Stop buttons
#         self.start_button = tk.Button(self.root, text="Start Visualization", command=self.start_visualization)
#         self.start_button.grid(row=0, column=0, padx=10, pady=10)
#
#         self.stop_button = tk.Button(self.root, text="Stop Visualization", command=self.stop_visualization)
#         self.stop_button.grid(row=0, column=1, padx=10, pady=10)
#
#         # Add Detection Mode Dropdown
#         self.mode_label = tk.Label(self.root, text="Detection Mode:")
#         self.mode_label.grid(row=1, column=0)
#
#         self.mode_var = tk.StringVar(value="Simple Threshold")
#         self.mode_dropdown = ttk.Combobox(self.root, textvariable=self.mode_var, state="readonly")
#         self.mode_dropdown['values'] = ("Simple Threshold", "Frequency Analysis")
#         self.mode_dropdown.grid(row=1, column=1)
#         self.mode_dropdown.bind("<<ComboboxSelected>>", self.update_mode)
#
#         # Threshold Slider (only for Simple Threshold mode)
#         self.threshold_label = tk.Label(self.root, text="Threshold:")
#         self.threshold_label.grid(row=2, column=0)
#
#         self.threshold_slider = tk.Scale(self.root, from_=100, to=5000, orient="horizontal")
#         self.threshold_slider.grid(row=2, column=1)
#         self.threshold_slider.set(1000)  # Default value
#
#         # Status Label
#         self.status_label = tk.Label(self.root, text="Status: Ready")
#         self.status_label.grid(row=3, column=0, columnspan=2)
#
#         # Log for Detected Messages
#         self.log_label = tk.Label(self.root, text="Detection Log:")
#         self.log_label.grid(row=4, column=0, padx=10, pady=10)
#
#         self.log_text = tk.Text(self.root, height=10, width=60, wrap=tk.WORD)
#         self.log_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
#         self.log_text.config(state=tk.DISABLED)
#
#         # Matplotlib canvas
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
#         self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, padx=10, pady=10)
#
#     def log_message(self, message):
#         """Logs messages to the GUI's text area."""
#         self.log_text.config(state=tk.NORMAL)
#         self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
#         self.log_text.config(state=tk.DISABLED)
#         self.log_text.yview(tk.END)
#
#     def update_mode(self, event=None):
#         """Adjust GUI based on detection mode."""
#         if self.mode_var.get() == "Simple Threshold":
#             self.threshold_slider.grid()
#             self.threshold_label.grid()
#         else:
#             self.threshold_slider.grid_remove()
#             self.threshold_label.grid_remove()
#
#     def start_visualization(self):
#         """Start the audio visualization."""
#         self.is_running = True
#         self.status_label.config(text="Status: Visualizing...")
#         self.log_message("Started visualization.")
#         self.visualize_audio()
#
#     def stop_visualization(self):
#         """Stop the audio visualization."""
#         if self.stream:
#             self.stream.stop_stream()
#             self.stream.close()
#         self.is_running = False
#         self.status_label.config(text="Status: Stopped")
#         self.log_message("Stopped visualization.")
#
#     def visualize_audio(self):
#         """Visualizes the audio data and sets up the animation."""
#         p = pyaudio.PyAudio()
#         input_device_index = self.get_input_device_index(p)
#
#         if input_device_index is None:
#             messagebox.showerror("Error", "No input device found.")
#             self.stop_visualization()
#             return
#
#         self.stream = p.open(format=pyaudio.paInt16,
#                              channels=1,
#                              rate=44100,
#                              input=True,
#                              frames_per_buffer=1024,
#                              input_device_index=input_device_index)
#
#         self.ani = animation.FuncAnimation(
#             self.fig,
#             self.update_line,
#             blit=True,
#             cache_frame_data=False,
#             interval=50
#         )
#
#         self.read_audio_data()
#
#     def get_input_device_index(self, p):
#         """Gets the input device index."""
#         for i in range(p.get_device_count()):
#             device_info = p.get_device_info_by_index(i)
#             if device_info.get('maxInputChannels') > 0:
#                 return i
#         return None
#
#     def read_audio_data(self):
#         """Read audio data from the microphone."""
#         if not self.is_running:
#             return
#
#         try:
#             data = self.stream.read(1024, exception_on_overflow=False)
#             data_int = struct.unpack(str(1024) + 'h', data)
#             self.data_buffer = np.array(data_int, dtype='h')
#
#             # Apply selected detection mode
#             self.detect_hidden_messages()
#
#             self.root.after(10, self.read_audio_data)
#         except OSError:
#             self.status_label.config(text="Status: Microphone Error")
#             self.stop_visualization()
#
#     def detect_hidden_messages(self):
#         """Detects hidden messages based on the selected mode."""
#         if self.mode_var.get() == "Simple Threshold":
#             threshold = self.threshold_slider.get()
#             if np.max(np.abs(self.data_buffer)) > threshold:
#                 self.log_message("Alert: High amplitude detected!")
#
#         elif self.mode_var.get() == "Frequency Analysis":
#             freq_data = np.fft.rfft(self.data_buffer)
#             dominant_freq = np.argmax(np.abs(freq_data))
#             self.log_message(f"Dominant Frequency: {dominant_freq} Hz")
#
#     def update_line(self, frame):
#         """Update the plot with new data."""
#         self.line.set_ydata(self.data_buffer)
#         self.line.set_xdata(np.arange(len(self.data_buffer)))
#         self.ax.set_ylim(-4000, 4000)
#         self.ax.set_xlim(0, len(self.data_buffer))
#         self.canvas.draw()
#         return self.line,
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = AudioVisualizerApp(root)
#     root.mainloop()



# when noise is loud enough it says message detected

# import numpy as np
# import pyaudio
# import struct
# import tkinter as tk
# from tkinter import messagebox
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
#
# class AudioVisualizerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Cymatics Sound Visualization")
#
#         # Matplotlib Setup
#         self.fig, self.ax = plt.subplots()
#         self.ax.set_title("Cymatics Sound Visualization")
#         self.ax.set_xlabel("Sample Points")
#         self.ax.set_ylabel("Amplitude")
#         self.line, = self.ax.plot([], [], lw=2)
#
#         # GUI Setup
#         self.setup_gui()
#
#         # Audio Stream Setup
#         self.stream = None
#         self.is_running = False
#
#         # Visualization Data
#         self.data_buffer = np.zeros(1024)
#
#         # Initialize Animation
#         self.ani = None
#
#     def setup_gui(self):
#         # Add Start and Stop buttons
#         self.start_button = tk.Button(self.root, text="Start Visualization", command=self.start_visualization)
#         self.start_button.grid(row=0, column=0, padx=10, pady=10)
#
#         self.stop_button = tk.Button(self.root, text="Stop Visualization", command=self.stop_visualization)
#         self.stop_button.grid(row=0, column=1, padx=10, pady=10)
#
#         # Add Checkbox for Alert Mode
#         self.alert_var = tk.BooleanVar()
#         self.alert_checkbox = tk.Checkbutton(self.root, text="Alert Mode", variable=self.alert_var)
#         self.alert_checkbox.grid(row=1, column=0, columnspan=2)
#
#         # Add Status Label
#         self.status_label = tk.Label(self.root, text="Status: Ready")
#         self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
#
#         # Add Message Log
#         self.log_label = tk.Label(self.root, text="Log:")
#         self.log_label.grid(row=3, column=0, padx=10, pady=10)
#
#         self.log_text = tk.Text(self.root, height=10, width=50, wrap=tk.WORD)
#         self.log_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
#         self.log_text.config(state=tk.DISABLED)  # Set as read-only initially
#
#         # Matplotlib canvas
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
#         self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)
#
#     def log_message(self, message):
#         """Logs messages to the GUI's text area."""
#         self.log_text.config(state=tk.NORMAL)
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.config(state=tk.DISABLED)
#         self.log_text.yview(tk.END)
#
#     def start_visualization(self):
#         """Start the audio visualization."""
#         self.is_running = True
#         self.status_label.config(text="Status: Visualizing...")
#         self.log_message("Started visualization.")
#
#         # Start audio stream and animation
#         self.visualize_audio()
#
#     def stop_visualization(self):
#         """Stop the audio visualization."""
#         if self.stream:
#             self.stream.stop_stream()
#             self.stream.close()
#         self.is_running = False
#         self.status_label.config(text="Status: Stopped")
#         self.log_message("Stopped visualization.")
#
#     def visualize_audio(self):
#         """Visualizes the audio data and sets up the animation."""
#         p = pyaudio.PyAudio()
#         input_device_index = self.get_input_device_index(p)
#
#         if input_device_index is None:
#             messagebox.showerror("Error", "No input device found.")
#             self.stop_visualization()
#             return
#
#         self.stream = p.open(format=pyaudio.paInt16,
#                              channels=1,
#                              rate=44100,
#                              input=True,
#                              frames_per_buffer=1024,
#                              input_device_index=input_device_index)
#
#         self.ani = animation.FuncAnimation(
#             self.fig,
#             self.update_line,
#             blit=True,
#             cache_frame_data=False,
#             interval=50  # Control frame rate (lower value means smoother)
#         )
#
#         self.read_audio_data()
#
#     def get_input_device_index(self, p):
#         """Gets the input device index."""
#         for i in range(p.get_device_count()):
#             device_info = p.get_device_info_by_index(i)
#             if device_info.get('maxInputChannels') > 0:
#                 print(f"Using device: {device_info['name']}")
#                 return i
#         return None
#
#     def read_audio_data(self):
#         """Read audio data from the microphone."""
#         if not self.is_running:
#             return
#
#         try:
#             data = self.stream.read(1024, exception_on_overflow=False)
#             data_int = struct.unpack(str(1024) + 'h', data)
#             self.data_buffer = np.array(data_int, dtype='h')
#
#             if self.alert_var.get():
#                 self.check_for_hidden_messages(self.data_buffer)
#
#             self.root.after(10, self.read_audio_data)
#         except OSError:
#             self.status_label.config(text="Status: Microphone Error")
#             self.stop_visualization()
#
#     def check_for_hidden_messages(self, data):
#         """Checks for hidden messages in the audio data."""
#         # Basic example: Detects if the amplitude exceeds a threshold
#         threshold = 3000  # Adjust this value as needed
#         if np.max(np.abs(data)) > threshold:
#             self.alert_hidden_message()
#
#     def alert_hidden_message(self):
#         """Triggers a hidden message alert."""
#         self.status_label.config(text="Status: Hidden Message Detected!")
#         self.log_message("⚠️ Hidden message detected!")
#
#     def update_line(self, frame):
#         """Update the plot with new data."""
#         self.line.set_ydata(self.data_buffer)
#         self.line.set_xdata(np.arange(len(self.data_buffer)))
#         self.ax.set_ylim(-4000, 4000)
#         self.ax.set_xlim(0, len(self.data_buffer))
#         return self.line,
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = AudioVisualizerApp(root)
#     root.mainloop()
#





# Loads and shows voice in graph

# import numpy as np
# import pyaudio
# import struct
# import tkinter as tk
# from tkinter import messagebox
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
#
#
# class AudioVisualizerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Cymatics Sound Visualization")
#
#         # Matplotlib Setup
#         self.fig, self.ax = plt.subplots()
#         self.ax.set_title("Cymatics Sound Visualization")
#         self.ax.set_xlabel("Sample Points")
#         self.ax.set_ylabel("Amplitude")
#         self.line, = self.ax.plot([], [], lw=2)
#
#         # GUI Setup
#         self.setup_gui()
#
#         # Audio Stream Setup
#         self.stream = None
#         self.is_running = False
#
#         # Visualization Data
#         self.data_buffer = np.zeros(1024)
#
#         # Initialize Animation
#         self.ani = None
#
#     def setup_gui(self):
#         # Add Start and Stop buttons
#         self.start_button = tk.Button(self.root, text="Start Visualization", command=self.start_visualization)
#         self.start_button.grid(row=0, column=0, padx=10, pady=10)
#
#         self.stop_button = tk.Button(self.root, text="Stop Visualization", command=self.stop_visualization)
#         self.stop_button.grid(row=0, column=1, padx=10, pady=10)
#
#         # Add Checkbox for Alert Mode
#         self.alert_var = tk.BooleanVar()
#         self.alert_checkbox = tk.Checkbutton(self.root, text="Alert Mode", variable=self.alert_var)
#         self.alert_checkbox.grid(row=1, column=0, columnspan=2)
#
#         # Add Status Label
#         self.status_label = tk.Label(self.root, text="Status: Ready")
#         self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
#
#         # Add Message Log
#         self.log_label = tk.Label(self.root, text="Log:")
#         self.log_label.grid(row=3, column=0, padx=10, pady=10)
#
#         self.log_text = tk.Text(self.root, height=10, width=50, wrap=tk.WORD)
#         self.log_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
#         self.log_text.config(state=tk.DISABLED)  # Set as read-only initially
#
#         # Matplotlib canvas
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
#         self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)
#
#     def log_message(self, message):
#         """Logs messages to the GUI's text area."""
#         self.log_text.config(state=tk.NORMAL)
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.config(state=tk.DISABLED)
#         self.log_text.yview(tk.END)
#
#     def start_visualization(self):
#         """Start the audio visualization."""
#         self.is_running = True
#         self.status_label.config(text="Status: Visualizing...")
#         self.log_message("Started visualization.")
#
#         # Start audio stream and animation
#         self.visualize_audio()
#
#     def stop_visualization(self):
#         """Stop the audio visualization."""
#         if self.stream:
#             self.stream.stop_stream()
#             self.stream.close()
#         self.is_running = False
#         self.status_label.config(text="Status: Stopped")
#         self.log_message("Stopped visualization.")
#
#     def visualize_audio(self):
#         """Visualizes the audio data and sets up the animation."""
#         p = pyaudio.PyAudio()
#         input_device_index = self.get_input_device_index(p)
#
#         if input_device_index is None:
#             messagebox.showerror("Error", "No input device found.")
#             self.stop_visualization()
#             return
#
#         self.stream = p.open(format=pyaudio.paInt16,
#                              channels=1,
#                              rate=44100,
#                              input=True,
#                              frames_per_buffer=1024,
#                              input_device_index=input_device_index)
#
#         self.ani = animation.FuncAnimation(
#             self.fig,
#             self.update_line,
#             blit=True,
#             cache_frame_data=False,
#             interval=50  # Control frame rate (lower value means smoother)
#         )
#
#         self.read_audio_data()
#
#     def get_input_device_index(self, p):
#         """Gets the input device index."""
#         for i in range(p.get_device_count()):
#             device_info = p.get_device_info_by_index(i)
#             if device_info.get('maxInputChannels') > 0:
#                 print(f"Using device: {device_info['name']}")
#                 return i
#         return None
#
#     def read_audio_data(self):
#         """Read audio data from the microphone."""
#         if not self.is_running:
#             return
#
#         try:
#             data = self.stream.read(1024, exception_on_overflow=False)
#             data_int = struct.unpack(str(1024) + 'h', data)
#             self.data_buffer = np.array(data_int, dtype='h')
#
#             if self.alert_var.get():
#                 self.check_for_hidden_messages(self.data_buffer)
#
#             self.root.after(10, self.read_audio_data)
#         except OSError:
#             self.status_label.config(text="Status: Microphone Error")
#             self.stop_visualization()
#
#     def check_for_hidden_messages(self, data):
#         """Checks for hidden messages in the audio data."""
#         # Placeholder for hidden message detection
#         # In a real implementation, you could analyze the data and trigger alerts
#         self.log_message("Checking for hidden messages...")
#
#     def update_line(self, frame):
#         """Update the plot with new data."""
#         self.line.set_ydata(self.data_buffer)
#         self.line.set_xdata(np.arange(len(self.data_buffer)))
#         self.ax.set_ylim(-4000, 4000)
#         self.ax.set_xlim(0, len(self.data_buffer))
#         return self.line,
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = AudioVisualizerApp(root)
#     root.mainloop()
