SAMPLE_RATE = 44100
FRAME_SIZE = 16384  # or 16384 or 1024 or 8192
FILTER_STRENGTH_DEFAULT = 5

CHAKRA_FREQUENCY_BANDS = []

base_bands = [

    # =========================
    # Brainwave / EEG bands  --- TYPICAL HARDWARE - OUT OF BOUNDS
    # =========================
    # (0.1, 0.5, "Infra-Delta (physiological / vestibular)", 'darkred'),
    # (0.5, 4.0, "Delta", 'red'),
    # (4.0, 8.0, "Theta", 'lightgreen'),
    # (8.0, 12.0, "Alpha", 'lightpink'),
    # (12.0, 30.0, "Beta", 'orange'),
    # (30.0, 80.0, "Gamma", 'gold'),   # upper bound varies by source

    # =========================
    # Infra sound / emotional response bands --- TYPICAL HARDWARE - OUT OF BOUNDS
    # =========================
    # (18.0, 20.0, "Fear / Anxiety Infrasound", 'darkred'),  # well-documented range - OUT OF BOUNDS
    (70.0, 90.0, "70 - 90 Hz - Agitation / Irritation Band", 'tomato'),

    # =========================
    # Deep resonance / meditative
    # =========================
    (134.0, 138.0, "136.1 Hz - OM Resonance – Third Eye (Low Octave)", 'purple'),
    # NOTE: 136.1 Hz is the most cited value; range widened slightly for detection stability

    # =========================
    # Bio field / somatic / emotional (non-chakra)
    # =========================
    (170.0, 176.0, "172 Hz – Inner Balance / Spleen Meridian", 'blue'),
    (210.0, 222.0, "215 Hz – Emotional Clearing / Regeneration", 'skyblue'),
    (275.0, 295.0, "285 Hz – Tissue Healing / Restoration", 'turquoise'),

    # =========================
    # Chakra system (harmonic model)
    # =========================
    (248.0, 272.0, "256-272 Hz - Root Chakra (Low Harmonic)", 'red'),
    # commonly cited roots: ~256, ~272
    (389, 401, "396Hz – Root Chakra", 'red'),

    (276.0, 304.0, "290Hz - Sacral Chakra", 'orange'),
    # overlaps musical D–E range; intentionally moderate width
    (414, 420, "417Hz Sacral Chakra", 'orange'),
    # Other sources cite 417 hz

    (308.0, 348.0, "320–341 Hz - Solar Plexus Chakra", 'yellow'),
    # includes 320–341 commonly cited values

    # =========================
    # Heart chakra (dual activation)
    # =========================
    (418.0, 446.0, "432 Hz - Heart Chakra – Coherence ", 'green'),
    # NOTE: 432 Hz is not exclusive to heart, but strongly associated with coherence

    (620.0, 660.0, "639 Hz - Heart Chakra – Relational ", 'green'),
    # NOTE: 639 Hz is the canonical solfeggio heart frequency

    # =========================
    # Upper chakras
    # =========================
    (720.0, 780.0, "741 Hz - Throat Chakra ", 'cyan'),

    (820.0, 880.0, "852 Hz - Third Eye Chakra ", 'indigo'),
    # complements 136.1 Hz as higher octave / cognitive activation

    (940.0, 1000.0, "963 Hz - Crown Chakra ", 'violet'),

    # =========================
    # Solfeggio system (explicit, non-chakra)
    # =========================
    (390.0, 405.0, "396 Hz – Solfeggio (Liberation from Fear)", 'red'),
    # NOTE: emotional grounding, not strictly root chakra

    (410.0, 430.0, "417 Hz – Solfeggio (Change / Transition)", 'orange'),

    (515.0, 540.0, "528 Hz – Solfeggio (Repair / Transformation)", 'green'),
    # extremely common; wider band due to harmonic spread

    (735.0, 760.0, "741 Hz – Solfeggio (Expression / Cleansing)", 'cyan'),

    (840.0, 880.0, "852 Hz – Solfeggio (Insight / Awareness)", 'indigo'),

    # =========================
    # High symbolic / metaphysical bands
    # =========================

    (760.0, 800.0, "777 Hz – Positive Flow / Alignment", 'gold'),
    # NOTE: less standardized; range chosen conservatively

    (870.0, 910.0, "888 Hz – Abundance / Continuity", 'purple'),
    # NOTE: numerological association, not acoustic consensus

    (960.0, 1040.0, "999 Hz – Completion / Transformation", 'white'),

    (1080.0, 1160.0, "1111 Hz – Awakening / Threshold", 'orange'),
]

# Include base bands and harmonics (Commented out above)
for band in base_bands:
    CHAKRA_FREQUENCY_BANDS.append(band)
    # CHAKRA_FREQUENCY_BANDS.extend(generate_harmonics(band))



