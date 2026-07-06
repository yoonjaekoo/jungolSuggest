"""
Main View for Jungol Recommender.
Contains the layout and UI components, and handles user interactions.
"""

import customtkinter as ctk
from views.frames.recommend_frame import RecommendFrame
from views.frames.dashboard_frame import DashboardFrame
from views.frames.search_frame import SearchFrame
from views.frames.stats_frame import StatsFrame
from views.frames.settings_frame import SettingsFrame

class MainView(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Create navigation buttons
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="정올 문제 추천기", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="대시보드", command=self.dashboard_button_event)
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)

        self.recommend_button = ctk.CTkButton(self.sidebar_frame, text="추천", command=self.recommend_button_event)
        self.recommend_button.grid(row=2, column=0, padx=20, pady=10)

        self.search_button = ctk.CTkButton(self.sidebar_frame, text="검색", command=self.search_button_event)
        self.search_button.grid(row=3, column=0, padx=20, pady=10)

        self.stats_button = ctk.CTkButton(self.sidebar_frame, text="통계", command=self.stats_button_event)
        self.stats_button.grid(row=5, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="설정", command=self.settings_button_event)
        self.settings_button.grid(row=6, column=0, padx=20, pady=10)

        # Create main content area (where frames will be displayed)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 20), pady=(20, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Initialize frames
        self.frames = {
            "dashboard": DashboardFrame(self.main_frame, self.model, self.controller),
            "recommend": RecommendFrame(self.main_frame, self.model, self.controller),
            "search": SearchFrame(self.main_frame, self.model, self.controller),
            "stats": StatsFrame(self.main_frame, self.model, self.controller),
            "settings": SettingsFrame(self.main_frame, self.model, self.controller)
        }

        # Show the recommend frame by default
        self.show_frame("recommend")

    def show_frame(self, frame_name):
        """Raise the specified frame to the top."""
        for frame in self.frames.values():
            frame.grid_forget()
        frame = self.frames[frame_name]
        frame.grid(row=0, column=0, sticky="nsew")

    def dashboard_button_event(self):
        self.show_frame("dashboard")

    def recommend_button_event(self):
        self.show_frame("recommend")

    def search_button_event(self):
        self.show_frame("search")

    def stats_button_event(self):
        self.show_frame("stats")

    def settings_button_event(self):
        self.show_frame("settings")

