# 🎵 Real-Time FFT Audio Analyzer
### Frequency Detection · Analysis · Tone Generation

![Version](https://img.shields.io/badge/version-0.0.3-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Platform](https://img.shields.io/badge/platform-Linux-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

---

> ⚠️ This application is intended for experimental and research use only. It is not a medical device.

---

## 📖 Overview

A real-time audio frequency analyzer built in Python that uses **Fast Fourier Transform (FFT)** and **AI-assisted frequency analysis** to detect and classify specific frequencies from live audio input. Designed for music analysis, voice analysis, meditation, sound healing research, and acoustic experimentation.

The app listens to your system's audio input, identifies frequencies of interest — including predefined named frequency bands (e.g., solfeggio scale, musical tuning standards, low-frequency resonance ranges) — and displays live results through a polished GUI with hit counters, visual FFT output, and a built-in tone generator. AI-powered analysis provides summaries, classifications, and insights directly in the interface, with offline and cloud-enabled options.

---

## ✨ Features

### 🔬 Real-Time Detection
- Live FFT analysis of audio input
- Detects **30+ named frequency bands** across solfeggio, brainwave, chakra, and metaphysical systems
- Hit counter per frequency — validates genuine detections above configurable thresholds
- Visual FFT display updated in real-time

### 🤖 AI Analysis
- Local AI-assisted classification and summary generation using local and remote LLM inference via **Ollama / phi3:mini** — fully offline and **Groq** cloud API
- Automatic fallback to **phi3:mini** local if **Groq** cloud API is unavailable
- Automatic fallback to built-in summary if neither is available
- AI analysis opens in a separate popup — view both reviews side by side
- Replaces legacy ChatGPT clipboard flow with seamless in-app analysis

### 🎛️ GUI
- Dark mode interface built with **CustomTkinter**
- Filter sensitivity controls
- Clear button to reset session data
- On-launch disclaimer and setup instructions popup
- Calibration flow — silence calibration for background noise filtering

### 🔊 Tone Generator
- Play any frequency directly through the GUI
- Pre built frequency generator for all named frequency bands
- Play sweeps starting and ending on selected frequencies 
- Useful for testing, meditation, or validation
- Plays until manually stopped

### 📊 Song Scoring & Review
- Scores a song based on which frequencies are detected and how strongly
- Identifies primary and secondary chakra/solfeggio activations
- Detects tuning standard (432 Hz vs 440 Hz)
- Example output: *"This track primarily activates the Heart and Crown chakras, with undertones of Root and Sacral. Strong 528 Hz presence — good for inspiration and concentration."*

### 📁 Alert Logging
- Every frequency detection above threshold is logged to `frequency_alerts.log`
- Timestamped entries with frequency, magnitude, and label
- Full session history preserved

### 📦 Standalone Executable
- Ships as a single `.exe` — no Python installation required
- Built with PyInstaller

---

## 🎯 Detected Frequency Bands

| Category | Frequencies |
|---|---|
| **Solfeggio Scale** | 396, 417, 528, 639, 741, 852 Hz |
| **Deep Resonance** | 136.1 Hz (OM / Third Eye Low Octave) |
| **Biofield / Somatic** | 172 Hz, 215 Hz, 285 Hz |
| **Symbolic / Metaphysical** | 777, 888, 999, 1111 Hz |
| **Chakra System** | Root (256/272/396 Hz), Sacral (290/417 Hz), Solar Plexus (320–341 Hz), Heart (432/639 Hz), Throat (741 Hz), Third Eye (852 Hz), Crown (963 Hz) |
| **Agitation Band** | 70–90 Hz |

---

## 🚀 Getting Started

### Option A — Download the Executable (Windows)
1. Download the `.exe` from the `/dist` folder
2. Run it — no installation needed
3. Follow the on-screen calibration instructions

### Option B — Run from Source

**Requirements:** Python 3.10+

```bash
git clone https://github.com/yourusername/real-time-fft-audio-analyzer.git
cd real-time-fft-audio-analyzer
pip install -r requirements-windows.txt
python main.py
```
```
Use requirements-linux.txt for Linux environments.
```

### First Run
1. **Calibrate in silence** — the app will prompt you to sit quietly for a few seconds to establish a noise floor baseline
2. **Adjust filter sensitivity** as needed using the GUI controls if getting false positives 
3. **Play audio** through your system and watch detections appear in real-time
4. Use the **Tone Generator** to test specific frequencies directly

---

## 🗂️ Project Structure

```
real-time-fft-audio-analyzer/
├── src/
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_stream.py
│   │   └── tone_player.py
│   │
│   ├── frequency_detection_tools/
│   │   ├── __init__.py
│   │   ├── debug_tone.py
│   │   ├── frequency_generators.py
│   │   └── trigger_each_chakra_energy_pattern_flag.py
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── gui.py
│   │   ├── alert_system.py
│   │   ├── disclaimer.py
│   │   └── setup.py
│   │
│   ├── models/
│   │   └── analysis_engine.py
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   └── fft_processor.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logger.py
│   │
│   └── web_app/
│       ├── __init__.py
│       └── main_app.py
│
├── dist/                       # Prebuilt Windows executable
├── main.py                     # Application entry point
├── requirements-windows.txt
├── requirements-linux.txt
└── README.md
```

---

## 📦 Tech Stack

| Library | Purpose |
|---|---|
| `numpy` / `scipy` | FFT computation and signal processing |
| `PyAudio` / `sounddevice` | Real-time audio capture |
| `customtkinter` | dark-mode GUI |
| `matplotlib` | Live FFT visualization |
| `Flask` + `websockets` | Backend / web interface (in progress) |
| `PyInstaller` | Windows executable packaging |
| `pyttsx3` | Tone generation |
| `ollama` | Local AI-assisted frequency analysis (LLM inference) |
| `requests` | Optional API calls / Groq cloud API |

---

## 📋 Release Notes

### v0.0.3 *(current)*
- Updated GUI — dark mode, setup instructions
- Tone generator — play any frequency for testing or meditation
- Clear button — reset session data
- Fine-tuned frequency detection
- Sweep any frequency range
- New frequencies added to detector list
- Standalone `.exe` release
- AI-powered frequency analysis via local LLM (Ollama / phi3:mini)
- Falls back to Groq cloud API if Ollama is unavailable
- Falls back to built-in summary if neither is available
- AI analysis opens in a separate popup — view both reviews side by side
- Legacy ChatGPT clipboard flow replaced with in-app analysis
- Linux version

### v0.0.2
- Song scoring and review system
- Tuning detection (432 Hz vs 440 Hz)
- Expanded frequency detection list

### v0.0.1
- Initial release
- Real-time chakra frequency detection
- High / mid / low activation levels across 7 chakras, fear, and discomfort bands

---

## 🗺️ Roadmap

- [ ] macOS version
- [ ] Log viewer popup in GUI
- [ ] Updated GUI with 3d cymatic visualizer 
- [ ] Web version using app's detection logic (Pyodide / browser-based)
- [ ] Hosted backend
- [ ] Crash reporter — popup on error with one-click email report

---

## 🤝 Contributing

Pull requests welcome. Please open an issue first to discuss major changes.

---

## 🌍 Website

https://real-time-audio-analyzer.netlify.app/

---

## 📄 License


MIT License — see `LICENSE` for details.

