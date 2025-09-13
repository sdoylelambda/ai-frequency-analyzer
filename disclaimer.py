import tkinter as tk
from tkinter import messagebox

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
    Displays the disclaimer popup.
    If user accepts, program continues.
    If user cancels, program exits.
    """
    root.withdraw()  # Hide main window until user accepts
    response = messagebox.askokcancel("Disclaimer & Terms of Use", DISCLAIMER_TEXT)
    if not response:
        root.destroy()
        exit(0)
    root.deiconify()  # Show main window once disclaimer accepted
