import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import customtkinter as ctk
import webbrowser
import pyperclip  # pip install pyperclip
import threading
import sounddevice as sd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.audio.audio_stream import AudioStream
from src.processing.fft_processor import compute_fft, detect_peaks
from src.gui.alert_system import log_alert_to_file, log_alert_to_gui
from utils.logger import log_to_gui
from src.gui.gui import build_gui
from src.audio.TonePlayer import TonePlayer
from src.gui.disclaimer import show_disclaimer
from src.gui.setup import show_setup
from utils.config import SAMPLE_RATE, FRAME_SIZE
from tkinter import Button, Toplevel, Label, Text, RIGHT, Frame, Scrollbar, Y, BOTH

# Removed import here for latest fine-tuning


CHAKRA_EFFECTS = {
    'root': "Grounding and physical stability",
    'sacral': "Emotional flow and creativity",
    'solar_plexus': "Empowerment and self-confidence",
    'heart': "Love, healing, and connection",
    'throat': "Communication and authenticity",
    'third_eye': "Insight, clarity, and intuition",
    'crown': "Spiritual connection and peace"
}


class AudioVisualizerApp:
    def __init__(self, root):
        # ----------------------------
        # Global style settings
        # ----------------------------
        self.DEFAULT_FONT = ("Helvetica", 12)
        self.DEFAULT_BUTTON_FONT = ("Helvetica", 14, "bold")
        self.DEFAULT_BUTTON_CORNER_RADIUS = 12
        self.DEFAULT_BUTTON_WIDTH = 140
        self.DEFAULT_BUTTON_HEIGHT = 40

        self.DEFAULT_LABEL_FONT = ("Helvetica", 13)
        self.DEFAULT_ENTRY_FONT = ("Helvetica", 13)
        self.DEFAULT_ENTRY_WIDTH = 200
        self.DEFAULT_BUTTON_COLOR = 'teal'
        self.DEFAULT_BUTTON_HOVER_COLOR = 'blue'

        self.latest_peaks = None
        self.min_energy_for_flags = 10000
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
        self.latest_fft_mags = None
        self.latest_fft_freqs = None

        # ----------------------------
        # Main frame
        # ----------------------------
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ----------------------------
        # Matplotlib figure
        # ----------------------------
        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.tight_layout(pad=3.0)
        self.line_waveform, = self.ax_waveform.plot([], [], lw=2)
        self.line_spectrum, = self.ax_spectrum.plot([], [], lw=2)

        # ----------------------------
        # Build GUI widgets inside self.frame
        # ----------------------------
        self.widgets = build_gui(
            self.frame,  # Pass frame as parent!
            self.fig,
            self.start_visualization,
            self.stop_visualization,
            self.calibrate_silence
        )

        # Extract main widgets
        self.canvas = self.widgets["canvas"]
        self.alert_var = self.widgets["alert_var"]
        self.alert_text = self.widgets["alert_text"]
        self.log_text = self.widgets["log_text"]
        self.status_label = self.widgets["status_label"]
        self.calibrate_button = self.widgets["calibrate_button"]
        self.filter_strength_var = self.widgets["filter_strength_var"]
        self.frequency_counts = self.widgets["frequency_counts"]
        self.counter_vars = self.widgets["counter_vars"]

        # ----------------------------
        # Start / Stop Visualization Buttons
        # ----------------------------
        self.widgets["start_btn"] = ctk.CTkButton(
            self.frame, text="Start Visualization", command=self.start_visualization,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["start_btn"].grid(row=0, column=0, padx=5, pady=5)

        self.widgets["stop_btn"] = ctk.CTkButton(
            self.frame, text="Stop Visualization", command=self.stop_visualization,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["stop_btn"].grid(row=1, column=1, padx=5, pady=5)

        # === Calibration Button ===
        self.widgets["calibrate_button"] = ctk.CTkButton(
            self.frame,  # Use your main frame so it aligns with other buttons
            text="Calibrate in Silence",
            command=self.calibrate_silence,
            font=self.DEFAULT_BUTTON_FONT,
            corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS,
            fg_color=self.DEFAULT_BUTTON_COLOR,
            hover_color=self.DEFAULT_BUTTON_HOVER_COLOR,
            width=self.DEFAULT_BUTTON_WIDTH,
            height=self.DEFAULT_BUTTON_HEIGHT
        )
        self.widgets["calibrate_button"].grid(row=0, column=1, padx=5, pady=5)

        # ----------------------------
        # Control Buttons
        # ----------------------------
        self.widgets["clear_btn"] = ctk.CTkButton(
            self.frame, text="Clear All", command=self.clear_all,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["clear_btn"].grid(row=1, column=0, padx=5, pady=5)

        self.widgets["increase_btn"] = ctk.CTkButton(
            self.frame, text="Increase Filter", command=self.increase_filter_strength,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["increase_btn"].grid(row=0, column=2, padx=5, pady=5)

        self.widgets["decrease_btn"] = ctk.CTkButton(
            self.frame, text="Decrease Filter", command=self.decrease_filter_strength,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["decrease_btn"].grid(row=0, column=3, padx=5, pady=5)

        self.widgets["frequency_generators"] = ctk.CTkButton(
            self.frame, text="Test Frequencies", command=self.start_frequency_generators_thread,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["frequency_generators"].grid(row=1, column=2, padx=5, pady=5)

        self.widgets["review_btn"] = ctk.CTkButton(
            self.frame, text="Generate Review", command=self.show_review,
            font=self.DEFAULT_BUTTON_FONT, corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS
        )
        self.widgets["review_btn"].grid(row=2, column=1, columnspan=3, pady=5)

        # Status label
        self.widgets["status_label"] = ctk.CTkLabel(
            self.frame, text="Status: Ready", font=self.DEFAULT_LABEL_FONT
        )
        self.widgets["status_label"].grid(row=3, column=0, columnspan=3, pady=5)

        # ----------------------------
        # Matplotlib canvas
        # ----------------------------
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Make row 4 expandable
        self.frame.grid_rowconfigure(4, weight=1)
        self.frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Test frequencies for generator
        self.test_freqs = [172, 215, 285, 396, 417, 432, 528, 741, 963]

        # ----------------------------
        # Test Freq
        # ----------------------------
        self.tone_player = TonePlayer()

    def play_tone(self, freq=528.0, duration=2.0, volume=0.5, sample_rate=44100):
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(freq * 2 * np.pi * t)
        audio = tone * volume
        sd.play(audio, samplerate=sample_rate)
        sd.wait()  # Wait for this tone to finish

    def frequency_generators(self):
        for freq in self.test_freqs:
            print(f"Playing {freq} Hz")
            self.play_tone(freq=freq, duration=5.0)

    def start_frequency_generators_thread(self):
        # Run frequency_generators in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.frequency_generators)
        thread.daemon = True  # thread closes when GUI closes
        thread.start()

    def log_message(self, message):
        # self.widgets["log_text"].insert(END, message + "\n")
        # self.widgets["log_text"].see(END)
        log_to_gui(self.log_text, message + "\n")

    # Move these to Utils folder/file

    def analyze_chakra_energy_balance(self, peaks, debug=True):
        """
        Analyze chakra balance using already-detected peaks.
        Peaks format: [(freq, mag, label, color), ...]
        """

        if not peaks:
            return {
                "chakra_energies": {},
                "balance_score": 0.0,
                "flags": ["🔴 No peaks detected."]
            }

        # --- Aggregate energy by chakra (using the label from peaks) ---
        chakra_energy = {}
        total_energy = 0.0

        for freq, mag, label, color in peaks:
            # Adjust mag for freq - (mag decreases as freq increases)
            def frequency_weight(freq):
                if freq < 200:
                    return 1.0
                elif freq < 400:
                    return 3
                elif freq < 800:
                    return 5.0
                else:
                    return 10.0

            mag = mag * frequency_weight(freq)
            print('MAG==============================>', mag)

            # normalize label (strip Hz info, keep chakra if present)
            chakra = None
            if "Chakra" in label:
                chakra = label.split("–")[-1].strip().lower()  # e.g. "Heart Chakra (4th)" -> "heart chakra (4th)"
                # optionally map to just root/sacral/etc if needed
                chakra = chakra.split()[0]  # keep just the first word like "heart"
            else:
                continue  # skip non-chakra peaks if you want strictly chakra bands

            chakra_energy[chakra] = chakra_energy.get(chakra, 0) + mag
            total_energy += mag

        if total_energy == 0:
            return {
                "chakra_energies": {c: 0 for c in chakra_energy},
                "balance_score": 0.0,
                "flags": ["🔴 No chakra energy detected."]
            }

        # --- Normalize to percentages ---
        chakra_percentages = {
            chakra: round((energy / total_energy) * 100, 2)
            for chakra, energy in chakra_energy.items()
        }

        # --- Balance score ---
        energy_values = list(chakra_percentages.values())
        std_dev = np.std(energy_values) if energy_values else 0
        balance_score = round(1.0 - min(std_dev / 40.0, 1.0), 2)

        # --- Flags ---
        flags = []
        threshold_low = 5
        threshold_high = 40

        for chakra, pct in chakra_percentages.items():
            if threshold_low < pct < threshold_high:
                flags.append(f"✅ {chakra.title()} is well-balanced ({pct:.1f}%)")
            elif pct <= threshold_low:
                flags.append(f"🟧 {chakra.title()} is unusually low ({pct:.1f}%).")
            elif pct >= threshold_high:
                flags.append(f"🟨 {chakra.title()} is dominating ({pct:.1f}%).")

        if balance_score < 0.5:
            flags.append("🔺 Energy distribution is imbalanced. Consider grounding or focusing techniques.")

        if debug:
            print("Chakra %:", chakra_percentages)
            print("Balance score:", balance_score)
            print("Flags:", flags)

        return {
            "chakra_energies": chakra_percentages,
            "balance_score": balance_score,
            "flags": flags
        }

    def generate_review(self):
        if not self.frequency_counts:
            self.log_message("No chakra data available yet.")
            return "", {}

        # Sort chakras by hit count descending
        sorted_chakras = sorted(
            self.frequency_counts.items(), key=lambda x: x[1], reverse=True
        )

        summary_lines = []
        full_counts = {}

        for chakra, count in sorted_chakras:
            effect = CHAKRA_EFFECTS.get(chakra, "Unknown Effect")
            full_counts[chakra] = count
            if count > 0:
                summary_lines.append(f"{chakra.capitalize()} ({count} hits): {effect}")

        summary_text = "\n".join(summary_lines)
        return summary_text, full_counts

    def generate_activation_summary(self):
        if not self.frequency_counts:
            return "No chakra hits recorded yet."

        sorted_chakras = sorted(
            self.frequency_counts.items(), key=lambda x: x[1], reverse=True
        )

        summary = []
        for chakra, count in sorted_chakras:
            if count > 0:
                effect = CHAKRA_EFFECTS.get(chakra, "Unknown effect")
                summary.append(f"🔹 {chakra.capitalize()} ({count} hits): {effect}")
        return "\n".join(summary) if summary else "No active chakra hits detected."

    # def generate_paragraph_review(self):    Now show review below
    #     if not self.frequency_counts:
    #         return "No chakra data available yet.", {}
    #
    #     sorted_chakras = sorted(
    #         self.frequency_counts.items(), key=lambda x: x[1], reverse=True
    #     )
    #
    #     best = [ch for ch, cnt in sorted_chakras if cnt >= 5]
    #     moderate = [ch for ch, cnt in sorted_chakras if 2 <= cnt < 5]
    #     trace = [ch for ch, cnt in sorted_chakras if cnt == 1]
    #
    #     lines = []
    #
    #     if best:
    #         effects = [CHAKRA_EFFECTS.get(ch, "") for ch in best if CHAKRA_EFFECTS.get(ch, "")]
    #         effect_str = ", ".join(effects) if effects else "varied energetic responses"
    #         lines.append("🟢 Strong activation in: " + ", ".join(best).title() +
    #                      f" — suggesting: {effect_str}.")
    #     if moderate:
    #         effects = [CHAKRA_EFFECTS.get(ch, "") for ch in moderate if CHAKRA_EFFECTS.get(ch, "")]
    #         effect_str = ", ".join(effects) if effects else "moderate energetic influences"
    #         lines.append("🟡 Moderate presence of: " + ", ".join(moderate).title() +
    #                      f", possibly indicating: {effect_str}.")
    #     if trace:
    #         effects = [CHAKRA_EFFECTS.get(ch, "") for ch in trace if CHAKRA_EFFECTS.get(ch, "")]
    #         effect_str = ", ".join(effects) if effects else "subtle signals"
    #         lines.append("🔵 Trace signals in: " + ", ".join(trace).title() +
    #                      f", may reflect: {effect_str}.")
    #
    #     if not lines:
    #         lines.append("No significant chakra activation was detected.")
    #
    #     paragraph = "\n\n".join(lines)
    #     return paragraph, dict(sorted_chakras)

    def build_paragraph_summary(self, chakra_energies):
        """
        Turn chakra_energies dict into a narrative paragraph.
        Example: { 'Heart Chakra': 22.0, 'Solar Plexus': 5.0, ... }
        """
        if not chakra_energies:
            return "No significant chakra activity was detected during this session."

        parts = []
        for chakra, pct in sorted(chakra_energies.items(), key=lambda x: x[1], reverse=True):
            if pct >= 20:
                parts.append(f"your {chakra} is strongly activated at about {pct:.1f}%.")
            elif pct >= 10:
                parts.append(f"your {chakra} shows a moderate presence around {pct:.1f}%.")
            elif pct > 0:
                parts.append(f"there is a subtle trace of {chakra} activity ({pct:.1f}%).")

        paragraph = "Overall, " + " ".join(parts)
        return paragraph[0].upper() + paragraph[1:]

    def show_review(self):
        summary_text, _ = self.generate_review()

        if summary_text:
            self.log_message("\n📝 Review Generated:")
            self.log_message(summary_text)
        else:
            self.log_message("No chakra hits detected yet.")

        # --- Gather cached data ---
        peaks = getattr(self, "latest_peaks", []) or []
        freqs = getattr(self, "latest_fft_freqs", None)
        mags = getattr(self, "latest_fft_mags", None)

        # --- Primary: analyze from peaks ---
        if len(peaks) > 0:
            balance = self.analyze_chakra_energy_balance(peaks)
        else:
            # --- Fallback: synthesize percentages from frequency_counts (if any) ---
            counts = getattr(self, "frequency_counts", {}) or {}
            nonzero = {k: v for k, v in counts.items() if v > 0}
            if nonzero:
                total = sum(nonzero.values())
                chakra_energies = {k: round((v / total) * 100.0, 2) for k, v in nonzero.items()}
                balance = {
                    "chakra_energies": chakra_energies,
                    "balance_score": 0.0,
                    "flags": ["ℹ️ Using hit-count fallback (no peaks cached this frame)."]
                }
            else:
                balance = {
                    "chakra_energies": {},
                    "balance_score": 0.0,
                    "flags": ["⚠️ No peaks available for review."]
                }

        # --- Tuning analysis (432 vs 440) if FFT available ---
        if freqs is not None and mags is not None:
            tuning = self.detect_tuning(freqs, mags, debug=False)

            # pull percentages (support both your schemas)
            pct432 = tuning.get("pct432", tuning.get("targets", {}).get("432Hz", {}).get("pct_of_total", 0.0))
            pct440 = tuning.get("pct440", tuning.get("targets", {}).get("440Hz", {}).get("pct_of_total", 0.0))
            sum_target_pct = pct432 + pct440

            # Normalized relative percentages
            if sum_target_pct > 0:
                norm432 = (pct432 / sum_target_pct) * 100.0
                norm440 = (pct440 / sum_target_pct) * 100.0
            else:
                norm432 = norm440 = 0.0

            # Decision thresholds
            ABS_MIN_PCT = 1.0
            REL_MIN_PCT = 75.0
            SNR_DB_MIN = 6.0

            # SNR helper
            def _compute_peak_snr_db(freqs_, mags_, low, high):
                mask = (freqs_ >= low) & (freqs_ <= high) & np.isfinite(freqs_)
                if not np.any(mask):
                    return None, 0.0
                peak = float(np.nanmax(mags_[mask]))
                bg = float(np.nanmedian(mags_[np.isfinite(mags_)])) if np.any(np.isfinite(mags_)) else 0.0
                eps = 1e-12
                snr_db = 10.0 * np.log10((peak + eps) / (bg + eps)) if bg > 0 else None
                return snr_db, peak

            # Determine dominant
            dominant_name = "432Hz" if pct432 > pct440 else "440Hz"
            dominant_pct = max(pct432, pct440)
            dominant_norm = max(norm432, norm440)

            snr_ok = True
            snr_info = {}
            if "bin_width" in tuning:
                used_tol = tuning.get("used_tolerance", tuning.get("bin_width", 1.0))
                tval = 432.0 if dominant_name == "432Hz" else 440.0
                low = tval - used_tol
                high = tval + used_tol
                snr_db, peak_amp = _compute_peak_snr_db(np.asarray(freqs), np.asarray(mags), low, high)
                snr_info = {"snr_db": snr_db, "peak_amp": peak_amp, "window": (low, high)}
                if SNR_DB_MIN is not None and snr_db is not None:
                    snr_ok = snr_db >= SNR_DB_MIN

            # Apply decision rules
            if sum_target_pct <= 0:
                tuning_message = "No measurable energy at 432 Hz or 440 Hz."
                confidence_level = "none"
            elif dominant_pct >= ABS_MIN_PCT and dominant_norm >= REL_MIN_PCT and snr_ok:
                tuning_message = (
                    f"Confident match: {dominant_name} — {dominant_pct:.2f}% of total energy "
                    f"({dominant_norm:.0f}% vs other candidate)."
                )
                confidence_level = "high"
            elif dominant_pct >= ABS_MIN_PCT and dominant_norm >= (REL_MIN_PCT * 0.6):
                tuning_message = (
                    f"Likely {dominant_name} ({dominant_pct:.2f}% of total energy, "
                    f"{dominant_norm:.0f}% relative between candidates)."
                )
                confidence_level = "medium"
            else:
                tuning_message = (
                    f"Low confidence on tuning: {norm432:.0f}% vs {norm440:.0f}% between 432Hz and 440Hz "
                    f"(432Hz: {pct432:.2f}% of total energy, 440Hz: {pct440:.2f}% of total energy). "
                    "Likely in some other tuning unless one candidate grows above the threshold."
                )
                confidence_level = "low"

            # Attach to balance & flags
            flags = balance.get("flags", []) or []
            flags.insert(0, f"🎵 {tuning_message}")
            balance["flags"] = flags
            balance["tuning_message"] = tuning_message
            balance["tuning_confidence"] = confidence_level
            balance["tuning_snr_info"] = snr_info

        # --- Build Review Text ---
        balance_lines = []

        # --- Paragraph Summary ---
        paragraph_summary = self.build_paragraph_summary(balance.get("chakra_energies", {}))
        balance_lines.insert(0, "📝 Narrative Summary:\n" + paragraph_summary + "\n")

        # Turn full review into one string
        review_text = "\n".join(balance_lines)

        # CHATGPT_URL = "https://chat.openai.com/"
        #
        # def add_ai_review_button(popup, review_text):
        #     def open_chatgpt():
        #         pyperclip.copy(review_text)  # Copy review to clipboard
        #         webbrowser.open(CHATGPT_URL)  # Open ChatGPT in browser
        #
        #     Button(
        #         popup,
        #         text="🤖 AI Review (via ChatGPT)",
        #         command=open_chatgpt,
        #         bg="purple",
        #         fg="white"
        #     ).pack(pady=10)
        #
        # add_ai_review_button(popup, review_text)

        # Helper: extract the first frequency from a label to sort by Hz
        def _extract_freq_from_label(text):
            import re
            m = re.search(r"(\d+(?:\.\d+)?)\s*hz", text, flags=re.I)
            if not m:
                m = re.search(r"\b(\d+(?:\.\d+)?)\b", text)
            try:
                return float(m.group(1)) if m else float("inf")
            except Exception:
                return float("inf")

        # Chakra & frequency activations
        energies = balance.get("chakra_energies", {})
        items = []
        for label, pct in energies.items():
            if pct >= 20:
                line = f"✅ {label} is highly activated ({pct:.1f}%)."
            elif pct >= 10:
                line = f"ℹ️ {label} shows moderate engagement ({pct:.1f}%)."
            elif pct > 0:
                line = f"☁️ {label} shows subtle activation ({pct:.1f}%)."
            else:
                line = f"⚫ {label} was not detected."

            # append hit count if tracked
            hit_count = self.frequency_counts.get(label, 0) if hasattr(self, "frequency_counts") else 0
            if hit_count > 0:
                line += f" ({hit_count} detections)"

            items.append((_extract_freq_from_label(label), line))

        if items:
            items.sort(key=lambda t: t[0])
            balance_lines.append("📡 Chakra & Frequency Activations (by Hz):")
            for _, line in items:
                balance_lines.append(line)

        # ✅ Always show balance score
        balance_lines.append(f"\n🧭 Overall Energy Balance Score: {balance.get('balance_score', 0.0) * 10:.1f}/10")


        # THIS MAKE DUPLICATE ENTRY
        # ✅ Also show tuning message inline (if present)
        # if "tuning_message" in balance:
        #     balance_lines.append(f"\n🎵 Tuning Analysis: {balance['tuning_message']}")

        # ✅ Observations / flags
        if balance.get("flags"):
            balance_lines.append("\n⚠️ Observations:")
            balance_lines.extend(balance["flags"])

        # --- Pop-up Window ---
        popup = Toplevel(self.root)
        popup.title("Chakra Activation Review")
        popup.geometry("600x1000")

        Label(popup, text="🧘 Chakra Activation Summary", font=("Helvetica", 14, "bold")).pack(pady=10)

        frame = Frame(popup)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        textbox = Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        textbox.pack(side="left", fill=BOTH, expand=True)
        scrollbar.config(command=textbox.yview)

        paragraph = "\n\n".join(balance_lines) if balance_lines else "No data available."
        textbox.insert("1.0", paragraph)
        textbox.config(state="disabled")

        Label(popup, text="―" * 70, fg="gray").pack(pady=10)

        # Detailed percentages (same order as above)
        Label(popup, text="📐 Detailed Chakra Energy Percentages", font=("Helvetica", 12, "bold")).pack(pady=(5, 2))
        for _, line in items:
            # extract label and pct from the built lines if you prefer, or just iterate energies again:
            pass  # optional: you can keep your previous “detailed list” block here if you like.

        Button(popup, text="Close", command=popup.destroy).pack(pady=15)

        CHATGPT_URL = "https://chat.openai.com/"

        def add_ai_review_button(popup, review_text):
            def open_chatgpt():
                pyperclip.copy(review_text)  # Copy review to clipboard
                webbrowser.open(CHATGPT_URL)  # Open ChatGPT in browser

            Button(
                popup,
                text="🤖 AI Review (via ChatGPT) - paste (control + v) into text box",
                command=open_chatgpt,
                bg="purple",
                fg="white"
            ).pack(pady=10)

        add_ai_review_button(popup, review_text)


        # --- Chakra + Extra Frequency Hit Counts ---
        # --- This is now redundant ---
        # if hasattr(self, "frequency_counts") and self.frequency_counts:
        #     balance_lines.append("\n📊 Frequency Hit Counts (Chakras + Specials):")
        #
        #     # Extract numeric frequency if possible for sorting
        #     def extract_freq(label):
        #         import re
        #         match = re.search(r"(\d+(?:\.\d+)?)", label)
        #         return float(match.group(1)) if match else float("inf")
        #
        #     sorted_counts = sorted(
        #         ((label, count) for label, count in self.frequency_counts.items() if count > 0),
        #         key=lambda x: extract_freq(x[0])
        #     )
        #
        #     for label, count in sorted_counts:
        #         balance_lines.append(f"   {label}: {count} detections")
        #
        #     # --- Debug Info ---
        # balance_lines.append("\n--- DEBUG ---")
        # balance_lines.append(f"Peaks count: {len(peaks)}")
        # if freqs is not None:
        #     balance_lines.append(f"FFT size: {len(freqs)}")
        # balance_lines.append(f"432%: {pct432:.2f} | 440%: {pct440:.2f}")
        # if "tuning_snr_info" in balance:
        #     balance_lines.append(f"SNR info: {balance['tuning_snr_info']}")

        # --- Pop-up Window ---
        # popup = Toplevel(self.root)
        # popup.title("Chakra Activation Review")
        # popup.geometry("650x1000")
        #
        # Label(popup, text="🧘 Chakra & Frequency Activation Summary", font=("Helvetica", 14, "bold")).pack(pady=10)
        #
        # frame = Frame(popup)
        # frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        #
        # scrollbar = Scrollbar(frame)
        # scrollbar.pack(side=RIGHT, fill=Y)
        #
        # textbox = Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        # textbox.pack(side="left", fill=BOTH, expand=True)
        # scrollbar.config(command=textbox.yview)
        #
        # paragraph = "\n\n".join(balance_lines)
        # textbox.insert("1.0", paragraph)
        # textbox.config(state="disabled")

        # Button(popup, text="Close", command=popup.destroy).pack(pady=15)

    def alert_chakra_flags(self, flags):
        if flags:
            # self.log_message("⚠️ Chakra Imbalance Alerts:")
            for flag in flags:
                self.log_message(flag)

    # def show_review(self):
    #     summary_text, _ = self.generate_review()
    #
    #     if summary_text:
    #         self.log_message("\n📝 Review Generated:")
    #         self.log_message(summary_text)
    #     else:
    #         self.log_message("No chakra hits detected yet.")
    #
    #     # Run energy balance analysis (if FFT data exists)
    #     freqs = getattr(self, "latest_fft_freqs", None)
    #     mags = getattr(self, "latest_fft_mags", None)
    #
    #     if freqs is not None and mags is not None and len(freqs) == len(mags):
    #         balance = self.analyze_chakra_energy_balance(freqs, mags)
    #     else:
    #         balance = {
    #             "chakra_energies": {},
    #             "balance_score": 0.0,
    #             "flags": ["⚠️ No valid FFT data available."]
    #         }
    #
    #     # Create pop-up window
    #     popup = Toplevel(self.root)
    #     popup.title("Chakra Activation Review")
    #     popup.geometry("520x1000")
    #
    #     Label(popup, text="🧘 Chakra Activation Report", font=("Helvetica", 14, "bold")).pack(pady=10)
    #
    #     # --- GUI Summary (hit counts & effects) ---
    #     for chakra in CHAKRA_EFFECTS:
    #         count = self.frequency_counts.get(chakra, 0)
    #         effect = CHAKRA_EFFECTS.get(chakra, "Unknown Effect")
    #         Label(
    #             popup,
    #             text=f"{chakra.capitalize()}: {count} hits\n↳ {effect}",
    #             justify="left",
    #             anchor="w",
    #             wraplength=480,
    #             font=("Helvetica", 10)
    #         ).pack(anchor="w", padx=20, pady=3)
    #
    #     # --- Separator ---
    #     Label(popup, text="―" * 70, fg="gray").pack(pady=10)
    #
    #     # --- Chakra Energy Balance Report ---
    #     Label(popup, text="🔬 Chakra Energy Balance Analysis", font=("Helvetica", 13, "bold")).pack(pady=(10, 5))
    #
    #     for chakra, pct in balance["chakra_energies"].items():
    #         Label(
    #             popup,
    #             text=f"{chakra.capitalize()}: {pct:.2f}%",
    #             justify="left",
    #             anchor="w",
    #             font=("Helvetica", 10)
    #         ).pack(anchor="w", padx=20)
    #
    #     Label(
    #         popup,
    #         text=f"\n🧭 Balance Score: {balance['balance_score'] * 10:.1f}/10",
    #         font=("Helvetica", 11, "italic"),
    #         fg="blue"
    #     ).pack(pady=10)
    #
    #     if balance["flags"]:
    #         Label(popup, text="⚠️ Observations:", font=("Helvetica", 11, "bold")).pack(pady=(10, 0))
    #         for flag in balance["flags"]:
    #             Label(
    #                 popup,
    #                 text=flag,
    #                 justify="left",
    #                 anchor="w",
    #                 wraplength=480,
    #                 fg="red",
    #                 font=("Helvetica", 9)
    #             ).pack(anchor="w", padx=20, pady=2)
    #
    #     Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def detect_tuning(self,
                      frequencies,
                      amplitudes,
                      targets=(432.0, 440.0),
                      tolerance_hz=1.0,
                      min_pct_for_detection=1.0,
                      debug=False):
        """
        Detect presence of tuning tones (e.g., 432Hz / 440Hz) by summing energy
        inside a small window around each target frequency.

        Returns a dict:
            {
                "targets": {
                    "432Hz": {"energy": float, "pct_of_total": float, "window": (low, high)},
                    "440Hz": {...}
                },
                "detected": "432Hz" | "440Hz" | None,
                "bin_width": float,
                "used_tolerance": float,
                "min_pct_for_detection": float,
                "total_energy": float
            }

        Notes:
        - tolerance_hz is a suggested tolerance; the function will ensure the
          actual tolerance is at least half the FFT bin width (median diff of freqs).
        - pct_of_total is percent of total energy across all finite frequency bins.
        """
        freqs = np.asarray(frequencies, dtype=float)
        amps = np.asarray(amplitudes, dtype=float)

        # Basic validation
        if freqs.shape != amps.shape:
            raise ValueError(f"frequencies and amplitudes must have same shape: {freqs.shape} != {amps.shape}")

        # Handle empty input
        if freqs.size == 0:
            return {
                "targets": {},
                "detected": None,
                "bin_width": 0.0,
                "used_tolerance": tolerance_hz,
                "min_pct_for_detection": min_pct_for_detection,
                "total_energy": 0.0
            }

        # Mask out non-finite frequency rows; zero-out non-finite amps to avoid NaN propagation
        finite_freq_mask = np.isfinite(freqs)
        amps = np.where(np.isfinite(amps), amps, 0.0)

        # Compute total energy over finite-frequency bins
        total_energy = float(np.nansum(amps[finite_freq_mask]))

        # Estimate bin width using median diff of freqs (only on finite freqs)
        finite_freqs = freqs[finite_freq_mask]
        if finite_freqs.size <= 1:
            bin_width = float(tolerance_hz)
        else:
            diffs = np.diff(finite_freqs)
            # ignore any non-finite diffs just in case
            diffs = diffs[np.isfinite(diffs)]
            bin_width = float(np.median(diffs)) if diffs.size > 0 else float(tolerance_hz)

        # Ensure tolerance respects at least half a bin
        used_tol = max(float(tolerance_hz), bin_width / 2.0)

        results = {}
        for t in targets:
            low = float(t) - used_tol
            high = float(t) + used_tol
            mask = (freqs >= low) & (freqs <= high) & finite_freq_mask
            energy = float(np.nansum(amps[mask]))
            pct_of_total = (energy / total_energy) * 100.0 if total_energy > 0 else 0.0
            results[f"{int(round(t))}Hz"] = {
                "energy": energy,
                "pct_of_total": pct_of_total,
                "window": (low, high)
            }
            if debug:
                print(
                    f"[tuning] {int(round(t))}Hz window {low:.3f}-{high:.3f} Hz -> energy={energy:.6f}, pct={pct_of_total:.4f}%",
                    flush=True)

        # Decide which tuning (if any) qualifies
        best_name, best_data = max(results.items(), key=lambda kv: kv[1]["pct_of_total"]) if results else (None, None)
        detected = best_name if (
                    best_data is not None and best_data["pct_of_total"] >= float(min_pct_for_detection)) else None

        tuning_info = {
            "targets": results,
            "detected": detected,
            "bin_width": bin_width,
            "used_tolerance": used_tol,
            "min_pct_for_detection": float(min_pct_for_detection),
            "total_energy": total_energy
        }

        if debug:
            print("Tuning detection summary:", tuning_info, flush=True)

        return tuning_info

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
                self.baseline_fft = mag

                # Compute total energy in chakra range during calibration
                chakra_freq_mask = (freqs >= 20) & (freqs <= 1200)
                self.baseline_energy = float(np.sum(mag[chakra_freq_mask]))
                print(f"[Calibration] Baseline chakra energy: {self.baseline_energy:.2f}")

                self.root.after(30, lambda: collect_frame(i + 1))
            except Exception as e:
                log_to_gui(self.log_text, f"Calibration failed: {e}")
                self.calibration_in_progress = False
                self.calibrate_button.config(state='normal')

        self.root.after(100, collect_frame)

    def clear_all(self):
        # Reset frequency counts but keep names
        for label, var in self.counter_vars.items():
            self.frequency_counts[label] = 0
            current_text = var.get()
            # Split at the last colon (so labels with ":" still work)
            if ":" in current_text:
                name, _ = current_text.rsplit(":", 1)
                var.set(f"{name}: 0")
            else:
                var.set(f"{label}: 0")

        # Clear logs
        if hasattr(self.log_text, "delete"):
            self.log_text.delete(1.0, tk.END)
        else:
            self.log_text.config(text="")

        # Clear alerts
        if hasattr(self.alert_text, "delete"):
            self.alert_text.delete(1.0, tk.END)
        else:
            self.alert_text.config(text="")

    def update_all_widgets(self, parent=None):
        """Recursively updates all widgets to modern style."""
        if parent is None:
            parent = self.root

        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(
                    font=self.DEFAULT_BUTTON_FONT,
                    corner_radius=self.DEFAULT_BUTTON_CORNER_RADIUS,
                    width=self.DEFAULT_BUTTON_WIDTH,
                    height=self.DEFAULT_BUTTON_HEIGHT,
                    fg_color=self.DEFAULT_BUTTON_COLOR,
                    hover_color=self.DEFAULT_BUTTON_HOVER_COLOR,
                )
            elif isinstance(widget, ctk.CTkLabel):
                widget.configure(font=self.DEFAULT_FONT)
            elif isinstance(widget, ctk.CTkEntry):
                widget.configure(font=self.DEFAULT_FONT, width=220)
            elif isinstance(widget, ctk.CTkTextbox):
                widget.configure(font=self.DEFAULT_FONT)

            if widget.winfo_children():
                self.update_all_widgets(widget)

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
        self.ax_spectrum.plot(freqs, adjusted_mag, color="cyan")
        self.ax_spectrum.set_xlim(0, 1000)
        self.ax_spectrum.set_ylim(0, np.max(adjusted_mag) + 100)

        threshold = 25000 * self.filter_strength_multiplier

        # ✅ Store latest FFT arrays (always!)
        self.latest_fft_freqs = freqs
        self.latest_fft_mags = adjusted_mag

        # ✅ Detect peaks & store them
        peaks = detect_peaks(freqs, adjusted_mag, threshold=threshold)
        self.latest_peaks = peaks

        for freq, mag, label, color in peaks:
            log_alert_to_file(freq, mag, label)
            log_alert_to_gui(self.alert_text, f"{label}: {freq:.1f} Hz (Mag: {mag:.0f})", color or "white")
            self.ax_spectrum.axvline(freq, color=color or "white", linestyle="--", alpha=0.8)

            if self.calibrated and label in self.frequency_counts:
                self.frequency_counts[label] += 1
                self.counter_vars[label].set(f"{label}: {self.frequency_counts[label]}")

        # ✅ Real-time chakra balance analysis (optional, live alerts)
        if self.calibrated:
            energy = np.sum(adjusted_mag)
            noise_floor = 3000
            if energy > noise_floor:
                balance = self.analyze_chakra_energy_balance(peaks)
                self.alert_chakra_flags(balance["flags"])

        self.canvas.draw()
        self.root.after(50, self.animate)


if __name__ == "__main__":
    # --- CustomTkinter appearance ---
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    # --- Initialize main window ---
    root = ctk.CTk()
    root.title("Audio Visualizer App")

    # --- Dynamically size main app to 90% of screen and center ---
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    w = int(screen_width * 0.7)
    h = int(screen_height * 0.8)
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    # --- Step 1: Show Disclaimer (modal) ---
    disclaimer_popup = show_disclaimer(root)
    # Modal handled by grab_set inside show_disclaimer

    # --- Step 2: Initialize main app ---
    app = AudioVisualizerApp(root)
    app.update_all_widgets()  # apply modern fonts and button styling

    # --- Step 3: Show Setup (non-modal) ---
    setup_popup = show_setup(root)
    # Make sure grab_set is removed in show_setup so main app remains usable

    # --- Run main loop ---
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
