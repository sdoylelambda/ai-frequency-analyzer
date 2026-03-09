import customtkinter as ctk


DISCLAIMER_TEXT = """ 
DISCLAIMER & TERMS OF USE

Welcome! Please Read Before Using the App

This app is designed for entertainment, exploration, and personal discovery. It is not a substitute for medical, psychological, legal, financial, or professional advice, and results may vary from person to person.

Some features use AI (OpenAI’s ChatGPT) to provide insights. These insights are for entertainment purposes only, may be incomplete or imperfect, and this app is independently developed—not affiliated with, endorsed by, or sponsored by OpenAI.

Please use the app responsibly:

Ensure a safe environment while using audio or exercises.

Supervise minors if they are using the app.

Avoid sharing sensitive personal information.

By continuing, you acknowledge that you understand the app is experimental and accept all risks, including technical issues, misinterpretation of results, or emotional reactions.

Enjoy exploring your sound and energy world!

AI Attribution:
This software incorporates AI insights generated via OpenAI’s ChatGPT for entertainment purposes only.
It is independently developed and is not affiliated with, endorsed by, or sponsored by OpenAI.
Learn more: OpenAI Terms of Use - https://openai.com/policies/terms-of-use/

--------------------------------------------------------
Developer Contact: Sean Doyle / sdoyledev@gmail.com / https://cymatics-frequncy-analyzer.netlify.app/
"""


def show_disclaimer(root):
    """
    Displays the disclaimer as a CustomTkinter modal popup.
    Blocks the main window until user clicks 'Accept'.
    Returns the Toplevel window for wait_window usage.
    """
    root.withdraw()  # Hide main window until accepted

    popup = ctk.CTkToplevel(root)
    popup.title("Disclaimer & Terms of Use")
    popup.geometry("600x500")
    popup.grab_set()  # Make modal
    popup.focus_set()

    # Scrollable text area
    text_box = ctk.CTkTextbox(popup, width=560, height=400, font=("Helvetica", 18))
    text_box.pack(padx=20, pady=20)
    text_box.insert("0.0", DISCLAIMER_TEXT)
    text_box.configure(state="disabled")  # Make read-only

    # Accept button
    def accept():
        popup.destroy()
        root.deiconify()  # Show main window

    accept_btn = ctk.CTkButton(popup, text="Accept", corner_radius=12, font=("Helvetica", 18, "bold"), command=accept)
    accept_btn.pack(pady=10)

    return popup
