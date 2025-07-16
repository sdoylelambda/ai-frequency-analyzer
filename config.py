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


# Works Well

# Narrow Range Detection (+-2) except first 3

# CURRENT TESTING
#
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
base_bands = [
    (136.1, 136.1, "OM (C#3) 3rd Eye (6th)", 'purple'),

    (172, 172, "172Hz – Inner Balance / Spleen Meridian", 'blue'),
    (215, 215, "215Hz – Emotional Clearing / Regeneration", 'skyblue'),
    (285, 285, "285Hz – Tissue Healing / Restoration", 'turquoise'),

    (396, 396, "Solfeggio 396Hz Root Chakra (1st)", 'orange'),
    (417, 417, "Solfeggio 417Hz Sacral Chakra (2nd)", 'orange'),
    (432, 432, "Solfeggio 432Hz Heart Chakra (4th)", 'orange'),
    (528, 528, "Solfeggio 528Hz Solar Plexus Chakra (3rd)", 'green'),
    (741, 741, "Solfeggio 741Hz Throat Chakra (5th)", 'cyan'),
    (963, 963, "Solfeggio 963Hz Crown Chakra (7th)", 'violet'),
]

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



