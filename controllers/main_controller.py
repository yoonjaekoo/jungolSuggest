"""
Main Controller for the Jungol Recommender application.
Coordinates between the model and view, and manages the application flow.
"""

import customtkinter as ctk
from views.main_view import MainView
from models.app_model import AppModel

class MainController(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("정올 문제 추천기")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Initialize model and view
        self.model = AppModel()
        self.view = MainView(self, self.model, self)
        self.view.pack(fill="both", expand=True)

        # Bind closing event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start background tasks if needed (e.g., data loading)
        self.model.start_background_tasks()

    def on_closing(self):
        """Handle window closing event."""
        self.model.stop_background_tasks()
        self.destroy()

