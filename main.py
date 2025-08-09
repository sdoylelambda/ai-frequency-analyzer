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
from tkinter import Button, Toplevel, Label, END, Text, RIGHT, Frame, Scrollbar, Y, BOTH


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
        self.min_energy_for_flags = 10000  # or another reasonable threshold value
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

        # Review button
        self.widgets["review_btn"] = Button(self.root, text="Generate Review")
        self.widgets["review_btn"].grid(row=1, column=0, columnspan=2, pady=5)
        self.widgets["review_btn"].config(command=self.show_review)

    def log_message(self, message):
        # self.widgets["log_text"].insert(END, message + "\n")
        # self.widgets["log_text"].see(END)
        log_to_gui(self.log_text, message + "\n")

    # Move these to Utils folder/file

    def analyze_chakra_energy_balance(self, frequencies, amplitudes, debug=True):
        chakra_bands = {
            'root': (20, 60),
            'sacral': (60, 120),
            'solar_plexus': (120, 250),
            'heart': (250, 400),
            'throat': (400, 600),
            'third_eye': (600, 900),
            'crown': (900, 1200)
        }

        min_chakra_pct = 5.0  # Ignore chakras below this percentage -- adjustable var - add to GUI

        chakra_energy = {}
        total_energy = 0

        # Calculate energy in each chakra band
        for chakra, (low, high) in chakra_bands.items():
            mask = (frequencies >= low) & (frequencies < high)
            energy = np.sum(amplitudes[mask])
            chakra_energy[chakra] = energy
            total_energy += energy

        # Normalize
        chakra_percentages = {
            chakra: round((energy / total_energy) * 100, 2)
            for chakra, energy in chakra_energy.items()
        }

        # Remove chakras that don't meet threshold (optional)
        filtered_chakra_percentages = {
            chakra: pct for chakra, pct in chakra_percentages.items()
            if pct >= min_chakra_pct
        }

        if total_energy == 0:
            return {
                "chakra_energies": {k: 0 for k in filtered_chakra_percentages},
                "balance_score": 0.0,
                "flags": ["🔴 No signal detected in chakra range."]
            }

        energy_values = np.array(list(filtered_chakra_percentages.values()))
        std_dev = np.std(energy_values)
        balance_score = round(1.0 - min(std_dev / 40.0, 1.0), 2)

        flags = []
        threshold_low = 5
        threshold_high = 30

        # ⚠️ Add energy guard here using the dynamically passed min_energy_for_flags
        # if self.min_energy_for_flags is None:
        #     min_energy_for_flags = 1.5 * getattr(self, "baseline_energy", 3000)  # fallback if baseline_energy missing
        # if debug:
        #     print("Min energy for flags:", min_energy_for_flags)
        if total_energy > self.min_energy_for_flags:
            # Individual Chakra Checks
            for chakra, value in filtered_chakra_percentages.items():
                if value > 25:  # may need to adjust - perhaps make adjustable via GUI
                    if threshold_low < value < threshold_high:
                        flags.append(f"✅ {chakra.title()} is well-balanced ({value:.1f}%)")
                    elif value < threshold_low:
                        flags.append(f"🟧 Chakra suppression: {chakra.replace('_', ' ').title()} is unusually low.")
                    elif value > threshold_high:
                        flags.append(f"🟨 Chakra over stimulation: {chakra.replace('_', ' ').title()} is dominating.")

        # Only run complex pattern checks if total energy exceeds noise threshold
        if total_energy > 200000:  # <-- adjust this value based on your noise floor

            # Complex Pattern-Based Flags
            if filtered_chakra_percentages.get('root', 0) > 25 and all(
                    filtered_chakra_percentages.get('c', 0) < 10 for c in ['heart', 'throat', 'third_eye', 'crown']):
                flags.append(
                    "🟥 This audio overstimulates survival instincts while suppressing emotional and spiritual centers.")

            if all(filtered_chakra_percentages.get(c, 0) < threshold_low for c in ['heart', 'throat']):
                flags.append("🟧 Dampen heart and communication centers.")  # due to tonal compression.")

            if filtered_chakra_percentages.get('crown', 0) < 3 and filtered_chakra_percentages.get('third_eye', 0) < 3:
                flags.append("🟨 Dull intuitive and cognitive energy")  # . Prolonged exposure not recommended.")

            if max(frequencies) > 10000 and total_energy > 0 and sum(amplitudes[frequencies > 10000]) > 0.3 * total_energy:
                flags.append(
                    "🟥 High-frequency content may cause stress or anxiety.")  # while failing to activate any energy "
                    # "centers.")

        if debug:
            print(f"Total Energy: {total_energy}")
            print("Filtered Chakra %:", filtered_chakra_percentages)

        # Placeholder NLP-based flag (can be linked to actual speech emotion detection results)
        # You can toggle this from your NLP results if applicable
        # Example: if emotional_disconnection_score > 0.7:
        # flags.append("🟨 Speech pattern shows signs of emotional disconnection.
        # May lead to low-vibration entrainment.")
        if 'speech_analysis_trigger' in chakra_energy:  # placeholder for future integration
            flags.append(
                "🟨 Speech pattern shows signs of emotional disconnection. May lead to low-vibration entrainment.")

        if balance_score < 0.5:
            flags.append("🔺 Energy distribution is imbalanced. Consider grounding or focusing techniques.")

        if debug:
            print("Chakra %:", filtered_chakra_percentages)
            print("Balance score:", balance_score)
            print("Flags:", flags)

        return {
            "chakra_energies": filtered_chakra_percentages,
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

    def show_review(self):
        summary_text, _ = self.generate_review()

        if summary_text:
            self.log_message("\n📝 Review Generated:")
            self.log_message(summary_text)
        else:
            self.log_message("No chakra hits detected yet.")

        # Run energy balance analysis (if FFT data exists)
        freqs = getattr(self, "latest_fft_freqs", None)
        mags = getattr(self, "latest_fft_mags", None)

        if freqs is not None and mags is not None and len(freqs) == len(mags):
            balance = self.analyze_chakra_energy_balance(freqs, mags)
        else:
            balance = {
                "chakra_energies": {},
                "balance_score": 0.0,
                "flags": ["⚠️ No valid FFT data available."]
            }

        # Generate paragraph summary
        balance_lines = []

        # Checks if 440hz or 432hz
        # --- tuning: result from self.detect_tuning(freqs, mags, debug=False) ---
        tuning = self.detect_tuning(freqs, mags, debug=False)
        balance["tuning"] = tuning

        targets = tuning.get("targets", {})
        pct432 = float(targets.get("432Hz", {}).get("pct_of_total", 0.0))
        pct440 = float(targets.get("440Hz", {}).get("pct_of_total", 0.0))
        sum_target_pct = pct432 + pct440

        # Normalized (relative) percentages between the two candidates
        if sum_target_pct > 0:
            norm432 = (pct432 / sum_target_pct) * 100.0
            norm440 = (pct440 / sum_target_pct) * 100.0
        else:
            norm432 = norm440 = 0.0

        # Decision thresholds (tweak these to taste)
        ABS_MIN_PCT = 1.0  # candidate must be >=1% of total energy to be considered "strong"
        REL_MIN_PCT = 75.0  # candidate must be >=75% of the two-target energy to be strongly dominant
        SNR_DB_MIN = 6.0  # optional: require ~6 dB SNR (set to None to disable SNR check)

        # helper to compute simple SNR for a target window (peak vs median)
        def _compute_peak_snr_db(freqs, mags, low, high):
            mask = (freqs >= low) & (freqs <= high) & np.isfinite(freqs)
            if not np.any(mask):
                return None, 0.0  # no data in window
            peak = float(np.nanmax(mags[mask]))
            # background - use median of full finite mags as a simple baseline
            bg = float(np.nanmedian(mags[np.isfinite(mags)])) if np.any(np.isfinite(mags)) else 0.0
            eps = 1e-12
            snr_db = 10.0 * np.log10((peak + eps) / (bg + eps)) if bg > 0 else None
            return snr_db, peak

        # Determine dominant candidate and SNRs (if freqs/mags available)
        dominant_name = "432Hz" if pct432 > pct440 else "440Hz"
        dominant_pct = max(pct432, pct440)
        dominant_norm = max(norm432, norm440)

        # Optionally compute SNR for dominant window (needs raw arrays)
        snr_ok = True
        snr_info = {}
        if 'bin_width' in tuning and freqs is not None and mags is not None:
            used_tol = tuning.get("used_tolerance", tuning.get("bin_width", 1.0))
            tval = 432.0 if dominant_name == "432Hz" else 440.0
            low = tval - used_tol
            high = tval + used_tol
            snr_db, peak_amp = _compute_peak_snr_db(np.asarray(freqs), np.asarray(mags), low, high)
            snr_info = {"snr_db": snr_db, "peak_amp": peak_amp, "window": (low, high)}
            if SNR_DB_MIN is not None and snr_db is not None:
                snr_ok = snr_db >= SNR_DB_MIN

        # Combined decision rules
        if sum_target_pct <= 0:
            tuning_message = "No measurable energy at 432 Hz or 440 Hz."
            confidence_level = "none"
        elif dominant_pct >= ABS_MIN_PCT and dominant_norm >= REL_MIN_PCT and snr_ok:
            # strong absolute + relative + (optional) SNR -> confident
            tuning_message = (
                f"Confident match: {dominant_name} — {dominant_pct:.2f}% of total energy "
                f"({dominant_norm:.0f}% vs other candidate)."
            )
            confidence_level = "high"
        elif dominant_pct >= ABS_MIN_PCT and dominant_norm >= (REL_MIN_PCT * 0.6):
            # decent absolute + moderate relative -> likely
            tuning_message = (
                f"Likely {dominant_name} ({dominant_pct:.2f}% of total energy, "
                f"{dominant_norm:.0f}% relative between candidates)."
            )
            confidence_level = "medium"
        else:
            # low absolute energy -> low confidence even if relative split looks big
            tuning_message = (
                f"Low confidence on tuning: {norm432:.0f}% vs {norm440:.0f}% between 432Hz and 440Hz "
                f"(432Hz: {pct432:.2f}% of total energy, 440Hz: {pct440:.2f}% of total energy). "
                "Likely in some other tuning unless one candidate grows above the threshold."
            )
            confidence_level = "low"

        # attach additional info for UI / logging
        flags = balance.get("flags", []) or []
        flags.insert(0, f"🎵 {tuning_message}")
        balance["flags"] = flags
        balance["tuning_message"] = tuning_message
        balance["tuning_confidence"] = confidence_level
        balance["tuning_snr_info"] = snr_info

        # Chakra Review
        sorted_chakras = sorted(
            balance["chakra_energies"].items(), key=lambda x: x[1], reverse=True
        )
        for chakra, pct in sorted_chakras:
            if pct >= 20:
                balance_lines.append(
                    f"✅ {chakra.capitalize()} is highly activated ({pct:.1f}%), suggesting strength in {CHAKRA_EFFECTS.get(chakra, 'that area')}.")
            elif pct >= 10:
                balance_lines.append(f"ℹ️ {chakra.capitalize()} shows moderate engagement ({pct:.1f}%).")
            elif pct > 0:
                balance_lines.append(f"☁️ {chakra.capitalize()} shows only subtle activation ({pct:.1f}%).")
            else:
                balance_lines.append(f"⚫ {chakra.capitalize()} was not detected.")

        balance_lines.append(f"\n🧭 Overall Energy Balance Score: {balance['balance_score'] * 10:.1f}/10")
        if balance["flags"]:
            balance_lines.append("\n⚠️ Observations:")
            balance_lines.extend(balance["flags"])

        # Create pop-up window
        popup = Toplevel(self.root)
        popup.title("Chakra Activation Review")
        popup.geometry("600x1000")

        Label(popup, text="🧘 Chakra Activation Summary", font=("Helvetica", 14, "bold")).pack(pady=10)

        # --- SCROLLABLE TEXT WIDGET WITH PARAGRAPH & FLAG SUMMARY ---
        frame = Frame(popup)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        textbox = Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        textbox.pack(side="left", fill=BOTH, expand=True)
        scrollbar.config(command=textbox.yview)

        paragraph = "\n\n".join(balance_lines)
        textbox.insert("1.0", paragraph)
        textbox.config(state="disabled")

        # --- Divider ---
        Label(popup, text="―" * 70, fg="gray").pack(pady=10)

        # --- DETAILED PERCENTAGE REPORT ---
        Label(popup, text="📐 Detailed Chakra Energy Percentages", font=("Helvetica", 12, "bold")).pack(pady=(5, 2))

        for chakra, pct in balance["chakra_energies"].items():
            Label(
                popup,
                text=f"{chakra.capitalize()}: {pct:.2f}%",
                justify="left",
                anchor="w",
                font=("Helvetica", 10)
            ).pack(anchor="w", padx=20)

        Label(
            popup,
            text=f"\n🧭 Balance Score: {balance['balance_score'] * 10:.1f}/10",
            font=("Helvetica", 11, "italic"),
            fg="blue"
        ).pack(pady=10)

        # --- FLAGS SECTION (already in paragraph, but optional to repeat) ---
        if balance["flags"]:
            Label(popup, text="⚠️ Flags:", font=("Helvetica", 11, "bold")).pack(pady=(10, 0))
            for flag in balance["flags"]:
                Label(
                    popup,
                    text=flag,
                    justify="left",
                    anchor="w",
                    wraplength=560,
                    fg="red",
                    font=("Helvetica", 9)
                ).pack(anchor="w", padx=20, pady=2)

        Button(popup, text="Close", command=popup.destroy).pack(pady=15)

    def alert_chakra_flags(self, flags):
        if flags:
            self.log_message("⚠️ Chakra Imbalance Alerts:")
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

        # ✅ Store latest snapshot for chakra energy balance analysis
        self.latest_fft_freqs = freqs
        self.latest_fft_mags = adjusted_mag  # use adjusted to match what's being visualized

        self.ax_spectrum.clear()
        self.ax_spectrum.plot(freqs, adjusted_mag, color='cyan')
        self.ax_spectrum.set_xlim(0, 1000)
        self.ax_spectrum.set_ylim(0, np.max(adjusted_mag) + 100)

        # Adjust threshold value here
        threshold = 25000 * self.filter_strength_multiplier

        for freq, mag, label, color in detect_peaks(freqs, adjusted_mag, threshold=threshold):
            log_alert_to_file(freq, mag, label)
            log_alert_to_gui(self.alert_text, f"{label}: {freq:.1f} Hz (Mag: {mag:.0f})", color or "white")
            self.ax_spectrum.axvline(freq, color=color or "white", linestyle="--", alpha=0.8)

            if self.calibrated and label in self.frequency_counts:
                self.frequency_counts[label] += 1
                self.counter_vars[label].set(f"{label}: {self.frequency_counts[label]}")

            # ✅ Real-time chakra energy balance check
            if self.calibrated:
                self.latest_fft_freqs = freqs
                self.latest_fft_mags = adjusted_mag

                # Only analyze if the total energy exceeds a noise threshold
                energy = np.sum(adjusted_mag)
                noise_floor = 3000  # You can tune this based on real-world quiet room FFT

                if energy > noise_floor:
                    balance = self.analyze_chakra_energy_balance(freqs, adjusted_mag)
                    self.alert_chakra_flags(balance["flags"])

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
