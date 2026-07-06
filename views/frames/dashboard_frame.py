"""
Dashboard Frame for Jungol Recommender.
Displays an overview of the user's progress and statistics.
"""

import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="대시보드")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(self.scrollable_frame, text="정올 문제 추천기 대시보드", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="ew")

        stats_frame = ctk.CTkFrame(self.scrollable_frame)
        stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        total_label = ctk.CTkLabel(stats_frame, text="전체 문제", font=ctk.CTkFont(size=16))
        total_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        self.total_value = ctk.CTkLabel(stats_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.total_value.grid(row=1, column=0, padx=10, pady=(0, 10))

        solved_label = ctk.CTkLabel(stats_frame, text="푼 문제", font=ctk.CTkFont(size=16))
        solved_label.grid(row=0, column=1, padx=10, pady=(10, 5))
        self.solved_value = ctk.CTkLabel(stats_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.solved_value.grid(row=1, column=1, padx=10, pady=(0, 10))

        fav_label = ctk.CTkLabel(stats_frame, text="즐겨찾기", font=ctk.CTkFont(size=16))
        fav_label.grid(row=0, column=2, padx=10, pady=(10, 5))
        self.fav_value = ctk.CTkLabel(stats_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.fav_value.grid(row=1, column=2, padx=10, pady=(0, 10))

        progress_label = ctk.CTkLabel(self.scrollable_frame, text="전체 진행률", font=ctk.CTkFont(size=16))
        progress_label.grid(row=2, column=0, padx=10, pady=(20, 5), sticky="w")
        self.progress_bar = ctk.CTkProgressBar(self.scrollable_frame)
        self.progress_bar.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)

        recent_label = ctk.CTkLabel(self.scrollable_frame, text="최근 활동", font=ctk.CTkFont(size=16))
        recent_label.grid(row=4, column=0, padx=10, pady=(20, 5), sticky="w")
        self.recent_textbox = ctk.CTkTextbox(self.scrollable_frame, height=150, wrap="word")
        self.recent_textbox.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.recent_textbox.configure(state="disabled")

        self.update_dashboard()

    def update_dashboard(self):
        """Update the dashboard with the latest data from the model."""
        # Update statistics
        total_problems = len(self.model.get_problems())
        self.total_value.configure(text=str(total_problems))

        # For solved and favorites, we need to get from the model or database
        # We'll assume the model has methods to get these counts
        solved_count = getattr(self.model, 'solved_count', 0)  # placeholder
        self.solved_value.configure(text=str(solved_count))

        fav_count = getattr(self.model, 'favorite_count', 0)  # placeholder
        self.fav_value.configure(text=str(fav_count))

        # Update progress bar
        if total_problems > 0:
            progress = solved_count / total_problems
        else:
            progress = 0
        self.progress_bar.set(progress)

        # Update recent activity (we'll get from model's recent recommendations)
        recent = self.model.recent_recommendations[-10:]  # last 10
        self.recent_textbox.configure(state="normal")
        self.recent_textbox.delete("1.0", "end")
        if recent:
            for prob_num in recent:
                self.recent_textbox.insert("end", f"추천된 문제 #{prob_num}\n")
        else:
            self.recent_textbox.insert("end", "최근 활동이 없습니다.\n")
        self.recent_textbox.configure(state="disabled")

