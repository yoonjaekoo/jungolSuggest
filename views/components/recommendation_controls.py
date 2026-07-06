"""
Recommendation Controls Component.
Contains controls for recommendation mode and exclusion options.
"""

import customtkinter as ctk

class RecommendationControls(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="추천 옵션:")
        self.label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 0), sticky="w")

        self.mode_label = ctk.CTkLabel(self, text="모드:")
        self.mode_label.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="e")
        self.mode_optionmenu = ctk.CTkOptionMenu(self, values=["랜덤", "순차", "쉬움", "어려움"], command=self._on_mode_change)
        self.mode_optionmenu.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="ew")
        self.mode_optionmenu.set("랜덤")

        self.exclude_solved_var = ctk.BooleanVar(value=True)
        self.exclude_solved_checkbox = ctk.CTkCheckBox(self, text="푼 문제 제외", variable=self.exclude_solved_var, command=self._on_exclude_solved_change)
        self.exclude_solved_checkbox.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.exclude_favorites_var = ctk.BooleanVar(value=False)
        self.exclude_favorites_checkbox = ctk.CTkCheckBox(self, text="즐겨찾기 제외", variable=self.exclude_favorites_var, command=self._on_exclude_favorites_change)
        self.exclude_favorites_checkbox.grid(row=3, column=0, padx=5, pady=2, sticky="w")

        self.exclude_recent_var = ctk.BooleanVar(value=True)
        self.exclude_recent_checkbox = ctk.CTkCheckBox(self, text="최근 추천 제외", variable=self.exclude_recent_var, command=self._on_exclude_recent_change)
        self.exclude_recent_checkbox.grid(row=4, column=0, padx=5, pady=2, sticky="w")

        self.grid_columnconfigure(1, weight=1)

    def _on_mode_change(self, choice):
        mode_map = {"랜덤": "random", "순차": "sequential", "쉬움": "easy", "어려움": "hard"}
        mode = mode_map.get(choice, "random")
        self.model.recommendation_mode = mode

    def _on_exclude_solved_change(self):
        self.model.exclude_solved = self.exclude_solved_var.get()

    def _on_exclude_favorites_change(self):
        self.model.exclude_favorites = self.exclude_favorites_var.get()

    def _on_exclude_recent_change(self):
        self.model.exclude_recent = self.exclude_recent_var.get()

