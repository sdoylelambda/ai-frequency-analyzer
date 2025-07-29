import numpy as np
import sounddevice as sd
import time


def play_tone(freq=528.0, duration=2.0, volume=0.5, sample_rate=44100):
    """
    Play a sine wave tone at the given frequency.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * freq * t)
    audio = tone * volume
    sd.play(audio, samplerate=sample_rate)
    sd.wait()  # Wait until audio finishes


def run_diagnostic_tone_tests():
    """
    Runs test sequences to verify chakra detection logic:
    - Suppressed, Balanced, and Overstimulated conditions for each chakra.
    - Includes other complex pattern triggers.
    """
    chakra_test_map = {
        'root': 396,
        'sacral': 417,
        'solar_plexus': 528,
        'heart': 432,
        'throat': 741,
        'third_eye': 136.1,
        'crown': 963
    }

    # Hold all tests here
    test_sequences = []

    # Add tests for each chakra (suppressed, balanced, overstimulated)
    for chakra, freq in chakra_test_map.items():
        test_sequences.extend([
            {
                "label": f"🔻 Suppressed {chakra.title()} Chakra",
                "tones": [f for c, f in chakra_test_map.items() if c != chakra],
                "note": f"Skips {chakra} to simulate under-activation."
            },
            {
                "label": f"⚖️ Balanced {chakra.title()} Chakra",
                "tones": list(chakra_test_map.values()),
                "note": f"Tests all chakras equally including {chakra}."
            },
            {
                "label": f"🔺 Overstimulated {chakra.title()} Chakra",
                "tones": [freq] * 4 + [f for c, f in chakra_test_map.items() if c != chakra],
                "note": f"Repeats {chakra} tone to simulate overstimulation."
            }
        ])

    # Add other specialized test sequences
    test_sequences += [
        {
            "label": "🚨 High-Frequency Stress Pattern",
            "tones": [12000, 14000, 16000],
            "note": "Tests stress warning for high non-chakra content."
        },
        {
            "label": "🧘 Balanced Activation Pattern",
            "tones": list(chakra_test_map.values()),
            "note": "Should generate highest balance score, fewest flags."
        },
        {
            "label": "🟥 Root Dominant, Spiritual Suppressed",
            "tones": [396, 396, 417, 396],  # No crown/third_eye
            "note": "Simulates fear-based tone cluster."
        },
    ]

    print("🧪 Starting Full Diagnostic Chakra Tone Test...\n")

    try:
        for test in test_sequences:
            print(f"\n▶ {test['label']}")
            print(f"ℹ️  {test['note']}\n")
            for freq in test["tones"]:
                print(f"🎵 Playing {freq} Hz")
                play_tone(freq=freq, duration=1.8)
                time.sleep(0.2)
            print("⏳ Analyze the GUI + popup for flags and chakra score.")
            print("-" * 60)
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted.")

    print("\n✅ Diagnostic test suite finished.")


run_diagnostic_tone_tests()

