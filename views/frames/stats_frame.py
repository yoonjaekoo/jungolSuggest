"""
Stats Frame for Jungol Recommender.
Displays various statistics about solved problems, tags, tiers, etc.
"""

import customtkinter as ctk

class StatsFrame(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("개요")
        self.tabview.add("태그별")
        self.tabview.add("난이도별")
        self.tabview.add("최근 활동")

        self._create_overview_tab()
        self._create_by_tag_tab()
        self._create_by_tier_tab()
        self._create_recent_tab()

    def _create_overview_tab(self):
        tab = self.tabview.tab("개요")
        tab.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(tab, text="개요 통계", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="ew")

        stats_frame = ctk.CTkFrame(tab)
        stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        total_frame = ctk.CTkFrame(stats_frame)
        total_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(total_frame, text="전체 문제", font=ctk.CTkFont(size=16)).pack(padx=10, pady=(10,5))
        self.total_value = ctk.CTkLabel(total_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.total_value.pack(padx=10, pady=(0,10))

        solved_frame = ctk.CTkFrame(stats_frame)
        solved_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(solved_frame, text="푼 문제", font=ctk.CTkFont(size=16)).pack(padx=10, pady=(10,5))
        self.solved_value = ctk.CTkLabel(solved_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.solved_value.pack(padx=10, pady=(0,10))

        fav_frame = ctk.CTkFrame(stats_frame)
        fav_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(fav_frame, text="즐겨찾기", font=ctk.CTkFont(size=16)).pack(padx=10, pady=(10,5))
        self.fav_value = ctk.CTkLabel(fav_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.fav_value.pack(padx=10, pady=(0,10))

        progress_frame = ctk.CTkFrame(stats_frame)
        progress_frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(progress_frame, text="진행률", font=ctk.CTkFont(size=16)).pack(padx=10, pady=(10,5))
        self.progress_value = ctk.CTkLabel(progress_frame, text="로딩 중...", font=ctk.CTkFont(size=20, weight="bold"))
        self.progress_value.pack(padx=10, pady=(0,10))

        self._update_overview_tab()

    def _create_by_tag_tab(self):
        tab = self.tabview.tab("태그별")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self.tag_stats_frame = ctk.CTkScrollableFrame(tab, label_text="태그 통계")
        self.tag_stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tag_stats_frame.grid_columnconfigure(0, weight=1)

        self._update_by_tag_tab()

    def _create_by_tier_tab(self):
        tab = self.tabview.tab("난이도별")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self.tier_stats_frame = ctk.CTkScrollableFrame(tab, label_text="난이도 통계")
        self.tier_stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tier_stats_frame.grid_columnconfigure(0, weight=1)

        self._update_by_tier_tab()

    def _create_recent_tab(self):
        tab = self.tabview.tab("최근 활동")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self.recent_activity_frame = ctk.CTkScrollableFrame(tab, label_text="최근 활동")
        self.recent_activity_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.recent_activity_frame.grid_columnconfigure(0, weight=1)

        self._update_recent_tab()

    def _update_overview_tab(self):
        total = len(self.model.get_problems())
        self.total_value.configure(text=str(total))

        solved_count = getattr(self.model, 'solved_count', 0)
        self.solved_value.configure(text=str(solved_count))

        fav_count = getattr(self.model, 'favorite_count', 0)
        self.fav_value.configure(text=str(fav_count))

        if total > 0:
            progress = solved_count / total
            self.progress_value.configure(text=f"{progress:.1%}")
        else:
            self.progress_value.configure(text="0%")

    def _update_by_tag_tab(self):
        for widget in self.tag_stats_frame.winfo_children():
            widget.destroy()
        placeholder = ctk.CTkLabel(self.tag_stats_frame, text="태그 통계가 여기에 표시됩니다.\n(푼 문제 추적 기능 구현 필요)")
        placeholder.grid(row=0, column=0, padx=10, pady=10)

    def _update_by_tier_tab(self):
        for widget in self.tier_stats_frame.winfo_children():
            widget.destroy()
        placeholder = ctk.CTkLabel(self.tier_stats_frame, text="난이도 통계가 여기에 표시됩니다.\n(푼 문제 추적 기능 구현 필요)")
        placeholder.grid(row=0, column=0, padx=10, pady=10)

    def _update_recent_tab(self):
        for widget in self.recent_activity_frame.winfo_children():
            widget.destroy()

        recent = self.model.recent_recommendations[-10:]
        if recent:
            for i, prob_num in enumerate(recent):
                label = ctk.CTkLabel(self.recent_activity_frame, text=f"추천된 문제 #{prob_num}")
                label.grid(row=i, column=0, padx=10, pady=2, sticky="w")
        else:
            label = ctk.CTkLabel(self.recent_activity_frame, text="최근 활동이 없습니다.")
            label.grid(row=0, column=0, padx=10, pady=10)

    def update_all(self):
        self._update_overview_tab()
        self._update_by_tag_tab()
        self._update_by_tier_tab()
        self._update_recent_tab()

