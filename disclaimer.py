import tkinter as tk
from tkinter import messagebox

DISCLAIMER_TEXT = """
DISCLAIMER & TERMS OF USE

IMPORTANT — PLEASE READ CAREFULLY BEFORE USING THIS SOFTWARE:

1. Educational and Experimental Use Only:
   This software is intended solely for educational, experimental, entertainment, and personal exploration purposes. 
   It is not a medical device, diagnostic tool, or substitute for professional advice of any kind.

2. No Medical or Health Claims:
   The software does not diagnose, treat, cure, or prevent any disease or health condition. 
   Any references to chakras, frequencies, energy balance, or well-being are based on cultural, spiritual, or experimental traditions 
   and should not be interpreted as medical or scientific fact. 
   Always consult a licensed physician or qualified professional regarding health concerns.

3. User Responsibility:
   By using this software, you agree that you are solely responsible for how you use the information, visualizations, or analyses provided. 
   The developer(s) of this software disclaim all liability for any harm, loss, injury, or consequence resulting from its use.

4. Data and Privacy:
   This software may process audio input through your microphone for real-time analysis. 
   No audio data is stored, transmitted, or shared unless explicitly implemented by the user. 
   Users are responsible for ensuring compliance with privacy regulations in their own jurisdiction.

5. AI Integration:
   If AI or machine learning features are included or enabled, they are experimental and may generate incomplete, inaccurate, 
   or subjective outputs. AI-generated content should never be relied upon for professional, medical, legal, or financial decisions.

6. Copyright and Fair Use:
   Playing copyrighted music or media into the software for analysis may involve fair use issues depending on jurisdiction. 
   Users are solely responsible for ensuring compliance with copyright law when using the software with third-party material.

7. Technical Limitations:
   Real-time signal analysis may be affected by background noise, hardware limitations, or environmental conditions. 
   Results may vary significantly and should not be considered definitive or precise.

8. Assumption of Risk:
   By running this program, you acknowledge and accept all risks associated with its use, 
   including but not limited to: misinterpretation of results, emotional or psychological responses, 
   technical malfunctions, or data inaccuracies.

9. No Warranty:
   This software is provided "AS IS" without warranty of any kind, express or implied, including but not limited to 
   warranties of merchantability, fitness for a particular purpose, or non-infringement.

10. Agreement:
   By clicking "OK" and using this software, you acknowledge that you have read, understood, and agreed to this disclaimer. 
   If you do not agree, click "Cancel" and exit the program immediately.

--------------------------------------------------------
Developer Contact: Sean Doyle / sdoyledev@gmail.com
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
