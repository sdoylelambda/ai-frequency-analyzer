from src.main_app import AudioVisualizerApp
import customtkinter as ctk
from src.gui.disclaimer import show_disclaimer
from src.gui.setup import show_setup


if __name__ == "__main__":
    # --- CustomTkinter appearance ---
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    # --- Initialize main window ---
    root = ctk.CTk()
    root.title("Audio Visualizer App")

    # --- Dynamically size main app to 90% of screen and center ---
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    w = int(screen_width * 0.7)
    h = int(screen_height * 0.8)
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    # --- Step 1: Show Disclaimer (modal) ---
    disclaimer_popup = show_disclaimer(root)
    # Modal handled by grab_set inside show_disclaimer

    # --- Step 2: Initialize main app ---
    app = AudioVisualizerApp(root)
    app.update_all_widgets()  # apply modern fonts and button styling

    # --- Step 3: Show Setup (non-modal) ---
    setup_popup = show_setup(root)
    # Make sure grab_set is removed in show_setup so main app remains usable

    # --- Run main loop ---
    root.mainloop()