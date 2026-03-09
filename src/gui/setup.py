import customtkinter as ctk
import webbrowser


DONATION_URL = "https://cymatics-frequncy-analyzer.netlify.app/"

SETUP_TEXT = """
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


def show_setup(root):
    popup = ctk.CTkToplevel(root)
    popup.title("App Setup & Instructions")
    popup.geometry("700x800")
    popup.transient(root)
    popup.lift()
    popup.focus_force()

    # --- Content Frame ---
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Scrollable Textbox
    textbox = ctk.CTkTextbox(frame, width=660, height=600, font=("Helvetica", 18))
    textbox.pack(side="top", fill="both", expand=True)
    textbox.insert("0.0", SETUP_TEXT)
    textbox.configure(state="disabled")

    # --- Close Button ---
    def close_popup():
        if popup.winfo_exists():
            popup.grab_release()
            popup.destroy()

    close_btn = ctk.CTkButton(frame, text="Close", corner_radius=12,
                              font=("Helvetica", 18, "bold"), command=close_popup)
    close_btn.pack(pady=10)

    # --- Donate Button ---
    def open_donation():
        webbrowser.open_new(DONATION_URL)

    donate_btn = ctk.CTkButton(frame, text="Donate / Support", corner_radius=12,
                               font=("Helvetica", 18), command=open_donation)
    donate_btn.pack(pady=5)

    # Handle window X safely
    popup.protocol("WM_DELETE_WINDOW", close_popup)

    # Do NOT use wait_window — modal behavior is handled by grab_set
    # root.wait_window(popup)  # remove this line

    return popup
