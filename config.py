# config.py

SAMPLE_RATE = 44100
FRAME_SIZE = 16384  # or 16384 or 1024 or 8192
FILTER_STRENGTH_DEFAULT = 5

CHAKRA_FREQUENCY_BANDS = []

# Base bands: (start, end, label, color)

# Wide Range Detection
# base_bands = [
#     (134, 138,  "OM (C#3) 3rd Eye (6th)", 'purple'),
#     (170, 174,  "172Hz – Inner Balance / Spleen Meridian", 'blue'),
#     (213, 217,  "215Hz – Emotional Clearing / Regeneration", 'skyblue'),
#     (283, 287,  "285Hz – Tissue Healing / Restoration", 'turquoise'),
#     (394, 398,  "Solfeggio 396Hz Root Chakra (1st)", 'orange'),
#     (415, 419,  "Solfeggio 417Hz Sacral Chakra (2nd)", 'orange'),
#     (430, 434,  "Solfeggio 432Hz Heart Chakra (4th)", 'orange'),
#     (526, 530,  "Solfeggio 528Hz Solar Plexus Chakra (3rd)", 'green'),
#     (739, 743,  "Solfeggio 741Hz Throat Chakra (5th)", 'cyan'),
#     (961, 965,  "Solfeggio 963Hz Crown Chakra (7th)", 'violet'),
#
#     (4, 8,      "Theta (brainwave)", 'lightgreen'),
#     (8, 12,     "Alpha (brainwave)", 'lightpink'),
#     (0.1, 4,    "Sub-Delta (disorienting)", 'red'),
#     (18, 20,    "Fear/Infrasound", 'darkred'),
#     (70, 90,    "Agitation Band", 'tomato'),
#     (664, 668,  "666Hz (symbolic)", 'black'),
# ]

# Ultra Wide Range Detection
# base_bands = [
#     (133, 139, "OM (C#3) 3rd Eye (6th)", 'purple'),
#     (170, 175, "172Hz – Inner Balance / Spleen Meridian", 'blue'),
#     (212, 218, "215Hz – Emotional Clearing / Regeneration", 'skyblue'),
#     (280, 290, "285Hz – Tissue Healing / Restoration", 'turquoise'),
#     (393, 399, "Solfeggio 396Hz Root Chakra (1st)", 'orange'),
#     (414, 420, "Solfeggio 417Hz Sacral Chakra (2nd)", 'orange'),
#     (429, 435, "Solfeggio 432Hz Heart Chakra (4th)", 'orange'),
#     (525, 531, "Solfeggio 528Hz Solar Plexus Chakra (3rd)", 'green'),
#     (738, 744, "Solfeggio 741Hz Throat Chakra (5th)", 'cyan'),
#     (960, 966, "Solfeggio 963Hz Crown Chakra (7th)", 'violet'),
#     (4, 8, "Theta", 'lightgreen'),
#     (8, 12, "Alpha", 'lightpink'),
#     (0.1, 4, "Sub-Delta (disorienting)", 'red'),
#     (18, 20, "Fear/Infrasound", 'darkred'),
#     (70, 90, "Agitation Band", 'tomato'),
#     (666, 666, "666Hz (symbolic)", 'black'),
# ]

# CURRENT TESTING -  VALUES UPDATED 12.26.25
base_bands = [

    # =========================
    # Brainwave / EEG bands
    # =========================
    (0.1, 0.5, "Infra-Delta (physiological / vestibular)", 'darkred'),
    (0.5, 4.0, "Delta", 'red'),
    (4.0, 8.0, "Theta", 'lightgreen'),
    (8.0, 12.0, "Alpha", 'lightpink'),
    (12.0, 30.0, "Beta", 'orange'),
    (30.0, 80.0, "Gamma", 'gold'),   # upper bound varies by source

    # =========================
    # Infrasound / emotional response bands
    # =========================
    (18.0, 20.0, "Fear / Anxiety Infrasound", 'darkred'),  # well-documented range
    (70.0, 90.0, "Agitation / Irritation Band", 'tomato'),

    # =========================
    # Deep resonance / meditative
    # =========================
    (134.0, 138.0, "OM Resonance – Third Eye (Low Octave)", 'purple'),
    # NOTE: 136.1 Hz is the most cited value; range widened slightly for detection stability

    # =========================
    # Biofield / somatic / emotional (non-chakra)
    # =========================
    (170.0, 176.0, "172 Hz – Inner Balance / Spleen Meridian", 'blue'),
    (210.0, 222.0, "215 Hz – Emotional Clearing / Regeneration", 'skyblue'),
    (275.0, 295.0, "285 Hz – Tissue Healing / Restoration", 'turquoise'),

    # =========================
    # Chakra system (harmonic model)
    # =========================
    (248.0, 272.0, "Root Chakra (Low Harmonic)", 'red'),
    # commonly cited roots: ~256, ~272

    (276.0, 304.0, "Sacral Chakra", 'orange'),
    # overlaps musical D–E range; intentionally moderate width

    (308.0, 348.0, "Solar Plexus Chakra", 'yellow'),
    # includes 320–341 commonly cited values

    # =========================
    # Heart chakra (dual activation)
    # =========================
    (418.0, 446.0, "Heart Chakra – Coherence (432 Hz)", 'green'),
    # NOTE: 432 Hz is not exclusive to heart, but strongly associated with coherence

    (620.0, 660.0, "Heart Chakra – Relational (639 Hz)", 'green'),
    # NOTE: 639 Hz is the canonical solfeggio heart frequency

    # =========================
    # Upper chakras
    # =========================
    (720.0, 780.0, "Throat Chakra (741 Hz)", 'cyan'),

    (820.0, 880.0, "Third Eye Chakra (852 Hz)", 'indigo'),
    # complements 136.1 Hz as higher octave / cognitive activation

    (940.0, 1000.0, "Crown Chakra (963 Hz)", 'violet'),

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
    (660.0, 675.0, "666 Hz – Symbolic / Cultural Resonance", 'darkred'),
    # NOTE: no physiological basis; included only because users expect it

    (760.0, 800.0, "777 Hz – Positive Flow / Alignment", 'gold'),
    # NOTE: less standardized; range chosen conservatively

    (870.0, 910.0, "888 Hz – Abundance / Continuity", 'purple'),
    # NOTE: numerological association, not acoustic consensus

    (960.0, 1040.0, "999 Hz – Completion / Transformation", 'white'),

    (1080.0, 1160.0, "1111 Hz – Awakening / Threshold", 'orange'),
]


# VALUES UPDATED 12.26.25
# base_bands = [
#     (4, 8, "Theta", 'lightgreen'),
#     (8, 12, "Alpha", 'lightpink'),
#
#     # --- Deep resonance / meditative ---
#     (134.5, 137.5, "OM Resonance – Third Eye (Low Octave)", 'purple'),
#
#     # --- Biofield / emotional / somatic (NOT chakras) ---
#     (168, 176, "172 Hz – Inner Balance / Spleen Meridian", 'blue'),
#     (208, 222, "215 Hz – Emotional Clearing / Regeneration", 'skyblue'),
#     (275, 295, "285 Hz – Tissue Healing / Restoration", 'turquoise'),
#
#     # --- Chakra core bands (harmonic model) ---
#     (248, 272, "Root Chakra", 'red'),
#     (276, 304, "Sacral Chakra", 'orange'),
#     (308, 348, "Solar Plexus Chakra", 'yellow'),
#
#     # --- Heart (dual activation) ---
#     (418, 446, "Heart Chakra – Coherence (432 Hz)", 'green'),
#     (620, 660, "Heart Chakra – Relational (639 Hz)", 'green'),
#
#     # --- Upper centers ---
#     (720, 780, "Throat Chakra (741 Hz)", 'cyan'),
#     (820, 880, "Third Eye Chakra (852 Hz)", 'indigo'),
#     (940, 1000, "Crown Chakra (963 Hz)", 'violet'),
#
#
#     (390.5, 401.5, "396 Hz – Solfeggio - Liberation from fear", 'red'),  # TWEAK
#     (745, 809, "777 Hz - Positive Energy Flow", 'gold'),
#     (856, 920, "888 Hz - Abundance and Prosperity", 'purple'),
#     (960, 1038, "999 Hz - Manifestation and Transformation", 'white'),
#     (1071, 1151, "1111 Hz - Spiritual Awakening", 'orange'),
#
#     (0.1, 3.9, "Sub-Delta (disorienting)", 'red'),
#     (18, 20, "Fear/Infrasound", 'darkred'),
#     (70, 90, "Agitation Band", 'tomato'),
#     (666, 666, "666 Hz (symbolic)", 'red'),
# ]


# Works Well

# Narrow Range Detection (+-2) except first 3

# OLDER VALUES
#
# base_bands = [
#     (4, 8, "Theta", 'lightgreen'),
#     (8, 12, "Alpha", 'lightpink'),
#
#     (134.1, 138.1, "136.1 Hz - OM (C#3) 3rd Eye (6th)", 'violet'),  # TWEAK
#
#     (171, 173, "172 Hz – Inner Balance / Spleen Meridian", 'yellow'),
#     (210, 220, "215 Hz – Emotional Clearing / Regeneration", 'skyblue'),
#     (284, 286, "285 Hz – Tissue Healing / Restoration", 'turquoise'),
#
#     (390.5, 401.5, "396 Hz – Solfeggio - Liberation from fear", 'red'),  # TWEAK
#     (410.5, 423.5, "417 Hz – Sacral Chakra (2nd)", 'orange'),
#     (425, 439, "432 Hz – Heart Chakra (4th)", 'green'),
#
#     (515, 531, "528 Hz – Solar Plexus Chakra (3rd)", 'yellow'),
#     (721, 761, "741 Hz – Throat Chakra (5th)", 'cyan'),
#     (745, 809, "777 Hz - Positive Energy Flow", 'gold'),
#     (856, 920, "888 Hz - Abundance and Prosperity", 'purple'),
#     (940, 986, "963 Hz – Crown Chakra (7th)", 'violet'),
#     (960, 1038, "999 Hz - Manifestation and Transformation", 'white'),
#     (1071, 1151, "1111 Hz - Spiritual Awakening", 'orange'),
#
#     (0.1, 3.9, "Sub-Delta (disorienting)", 'red'),
#     (18, 20, "Fear/Infrasound", 'darkred'),
#     (70, 90, "Agitation Band", 'tomato'),
#     (666, 666, "666 Hz (symbolic)", 'red'),
# ]

# ADD THESE NEXT
# 1111
# 999
# 888
# 777

    # ("Theta", 'lightgreen'),
    # ("Alpha", 'lightpink'),
    #
    # ("Sub-Delta (disorienting)", 'red'),
    # ("Fear/Infrasound", 'darkred'),
    # ("Agitation Band", 'tomato'),
    # ("666Hz (symbolic)", 'red'),
    #
    # ("1111 - Spiritual Awakening", 'gold'),
    # ("999 - Manifestation and Transformation", 'gold'),
    # ("888 - Abundance and Prosperity", 'gold'),
    # ("777 - Positive Energy Flow", 'violet'),



# base_bands = [
#     (134.1, 138.1, "136.1 - OM (C#3) 3rd Eye (6th)", 'purple'),  # no hits
#
#     (170.5, 173.5, "172Hz – Inner Balance / Spleen Meridian", 'blue'),  # no hits
#     (214.7, 215.3, "215Hz – Emotional Clearing / Regeneration", 'skyblue'),
#     (289, 291, "285Hz – Tissue Healing / Restoration", 'turquoise'),  # no hits
#
#     (389, 401, "396Hz – Root Chakra (1st)", 'black'),
#     (407, 427, "417Hz - Sacral Chakra (2nd)", 'red'),
#     (417, 445, "432Hz - Heart Chakra (4th)", 'orange'),  # no hits
#     (517, 529, "528Hz - Solar Plexus Chakra (3rd)", 'green'),  # no hits
#     (718, 764, "741Hz - Throat Chakra (5th)", 'cyan'),
#     (936, 990, "963Hz - Crown Chakra (7th)", 'violet'),
# ]

# NEW FREQUENCIES TO ADD === 888,1111   +   LIST AT BOTTOM OF PAGE (NEGATIVE, ALPHA, DETA, THETA, ETC.)






# Exact Range Detection
# base_bands = [
#     (136.1, 136.1, "OM (C#3) 3rd Eye (6th)", 'purple'),
#
#     (172, 172, "172Hz – Inner Balance / Spleen Meridian", 'blue'),
#     (215, 215, "215Hz – Emotional Clearing / Regeneration", 'skyblue'),
#     (285, 285, "285Hz – Tissue Healing / Restoration", 'turquoise'),
#
#     (396, 396, "396Hz - Root Chakra (1st)", 'orange'),
#     (417, 417, "417Hz - Sacral Chakra (2nd)", 'orange'),
#     (432, 432, "432Hz - Heart Chakra (4th)", 'orange'),
#     (528, 528, "528Hz - Solar Plexus Chakra (3rd)", 'green'),
#     (741, 741, "741Hz - Throat Chakra (5th)", 'cyan'),
#     (963, 963, "963Hz - Crown Chakra (7th)", 'violet'),
# ]

# Removed Positive frequencies due to wide range = wide multiples = many false hits

#     (4, 8, "Theta", 'lightgreen'),
#     (8, 12, "Alpha", 'lightpink'),
# ]

# Removed Negative frequencies due to wide range = wide multiples = many false hits

#     (0.1, 4, "⚠ Sub-Delta (disorienting)", 'red'),
#     (18, 20, "⚠ Fear/Infrasound", 'darkred'),
#     (70, 90, "⚠ Agitation Band", 'tomato'),
#     (666, 666, "⚠ 666Hz (symbolic)", 'black'),
# ]

# CHECK MORE HARMONICS FOR SAME FREQ
# def generate_harmonics(base_band, max_freq=10000):
#     start, end, label, color = base_band
#     harmonics = []
#     base_center = (start + end) / 2
#     multiplier = 2
#     while (base_center * multiplier) < max_freq:
#         new_start = start * multiplier
#         new_end = end * multiplier
#         log_label = f"{label} (Harmonic x{multiplier})"
#         new_label = label
#         harmonics.append((new_start, new_end, new_label, color))
#         multiplier += 1
#     return harmonics


# Include base bands and harmonics (Commented out above)
for band in base_bands:
    CHAKRA_FREQUENCY_BANDS.append(band)
    # CHAKRA_FREQUENCY_BANDS.extend(generate_harmonics(band))



