#!/usr/bin/env python3
"""
Jungol Recommender - Main Entry Point
"""

import customtkinter as ctk
from controllers.main_controller import MainController

def main():
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    # Create the main controller (which will set up the MVC)
    app = MainController()
    app.mainloop()

if __name__ == "__main__":
    main()