import tkinter as tk
from tkinter import Toplevel, Label, Text, Scrollbar, Frame, Button, BOTH, RIGHT, Y
import webbrowser

DONATION_URL = "https://cymatics-frequncy-analyzer.netlify.app/"  # <-- replace with your real link


def show_setup(root):
    """Display setup & instructions popup at program start."""
    popup = Toplevel(root)
    popup.title("App Setup & Instructions")
    popup.geometry("700x800")

    # --- SCROLLABLE FRAME ---
    frame = Frame(popup)
    frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)

    textbox = Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Helvetica", 11))
    textbox.pack(side="left", fill=BOTH, expand=True)
    scrollbar.config(command=textbox.yview)

    # --- Content ---
    content = """
🛠️ Setup Instructions
---------------------------------
1. Connect a working microphone (USB or built-in).
2. Ensure your OS microphone permissions are enabled.
3. For best results, use wired headphones (to prevent speaker feedback).
4. Play audio through speakers or your environment, the app listens in real time.
5. Adjust the "Filter Strength" if detection seems too sensitive or too quiet.

🎶 How to Use
---------------------------------
- Watch the FFT graph update in real time.
- Chakra frequencies will highlight with vertical lines when detected.
- Counts update in the right panel as frequencies are identified.
- Use the Review button to see an analysis of chakra balance & observations.

❓ Common Questions
---------------------------------
Q: I see false detections or too many hits.
A: Adjust the filter strength down (weaker) or up (stronger). Try again.

Q: The app shows no detections.
A: Make sure sound is loud enough, and check the mic input device in your system.

Q: Can I use headphones instead of speakers?
A: The app works best if the microphone can "hear" the music. Headphones will prevent detection unless you route audio internally.

Q: Is this medical advice?
A: No. This app is experimental, spiritual, and educational only. It is not a substitute for medical treatment.

🚀 Planned Features
---------------------------------
- AI-powered chakra & energy readings.
- Mobile apps for iOS and Android.
- Offline self-contained AI (no internet needed).
- Advanced review summaries with emotional + spiritual insights.
- Custom alerts for healing tones and disruptive frequencies.
- Visualization of chakra activations over time.

💜 Support the Project
---------------------------------
This app is free to use, but if you’d like to support development, get more info, or make a suggestion click the link below:
"""
    textbox.insert("1.0", content)
    textbox.config(state="disabled")

    # --- Clickable donation link ---
    link_label = Label(popup, text="👉 Donate here", font=("Helvetica", 11, "underline"),
                       fg="blue", cursor="hand2")
    link_label.pack(pady=5)
    link_label.bind("<Button-1>", lambda e: webbrowser.open_new(DONATION_URL))

    # --- Close button ---
    Button(popup, text="Close", command=popup.destroy).pack(pady=10)
