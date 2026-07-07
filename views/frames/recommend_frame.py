"""
Recommend Frame for Jungol Recommender.
Displays controls for filtering and getting problem recommendations.
"""

import customtkinter as ctk
from views.components.tag_selector import TagSelector
from views.components.tier_selector import TierSelector
from views.components.recommendation_controls import RecommendationControls

class RecommendFrame(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.tag_selector = TagSelector(self.controls_frame, self.model, self.controller)
        self.tag_selector.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.tier_selector = TierSelector(self.controls_frame, self.model, self.controller)
        self.tier_selector.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.rec_controls = RecommendationControls(self.controls_frame, self.model, self.controller)
        self.rec_controls.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.get_rec_button = ctk.CTkButton(self.controls_frame, text="추천 받기", command=self.get_recommendation)
        self.get_rec_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.model.on_data_loaded(self._on_data_loaded)

    def _on_data_loaded(self):
        self.after_idle(self.tag_selector.update_tags)
        self.after_idle(self.tier_selector.update_tiers)

        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(0, weight=1)

        self.problem_details = ctk.CTkTextbox(self.display_frame, width=600, height=200, wrap="word")
        self.problem_details.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.problem_details.configure(state="disabled")

        self.action_frame = ctk.CTkFrame(self.display_frame)
        self.action_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.action_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.solved_button = ctk.CTkButton(self.action_frame, text="해결 완료", command=self.mark_as_solved)
        self.solved_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.favorite_button = ctk.CTkButton(self.action_frame, text="즐겨찾기 추가", command=self.add_to_favorites)
        self.favorite_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.unfavorite_button = ctk.CTkButton(self.action_frame, text="즐겨찾기 제거", command=self.remove_from_favorites)
        self.unfavorite_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.web_button = ctk.CTkButton(self.action_frame, text="정올에서 열기", command=self.open_on_jungol)
        self.web_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", height=20)
        self.status_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.current_problem = None

    def get_recommendation(self):
        self.status_label.configure(text="로딩 중...", text_color="orange")
        self.update_idletasks()

        problem = self.model.get_recommendation()

        if problem is None:
            self.status_label.configure(text="현재 필터에 맞는 문제가 없습니다.", text_color="red")
            self.clear_display()
            return

        self.current_problem = problem
        self.display_problem(problem)
        self.status_label.configure(text="추천이 로드되었습니다.", text_color="green")

    def display_problem(self, problem: dict):
        self.problem_details.configure(state="normal")
        self.problem_details.delete("1.0", "end")
        details = f"문제 번호: {problem.get('number', 'N/A')}\n"
        details += f"제목: {problem.get('title', 'N/A')}\n"
        details += f"난이도: {problem.get('tier', 'N/A')}\n"
        details += f"태그: {', '.join(problem.get('tags', []))}\n"
        details += f"링크: {problem.get('link', 'N/A')}\n"
        details += f"\n설명:\n{problem.get('description', '설명이 없습니다.')}"
        self.problem_details.insert("1.0", details)
        self.problem_details.configure(state="disabled")

    def clear_display(self):
        self.problem_details.configure(state="normal")
        self.problem_details.delete("1.0", "end")
        self.problem_details.configure(state="disabled")
        self.current_problem = None

    def mark_as_solved(self):
        if self.current_problem:
            problem_number = self.current_problem.get('number')
            memo = ctk.CTkInputDialog(text="메모를 입력하세요 (선택사항):", title="해결 완료 표시").get_input()
            if memo is None:
                memo = ""
            self.model.mark_as_solved(problem_number, memo=memo)
            self.status_label.configure(text=f"문제 {problem_number}번을 해결 완료로 표시했습니다.", text_color="green")

    def add_to_favorites(self):
        if self.current_problem:
            problem_number = self.current_problem.get('number')
            self.model.add_to_favorites(problem_number)
            self.status_label.configure(text=f"문제 {problem_number}번을 즐겨찾기에 추가했습니다.", text_color="green")

    def remove_from_favorites(self):
        if self.current_problem:
            problem_number = self.current_problem.get('number')
            self.model.remove_from_favorites(problem_number)
            self.status_label.configure(text=f"문제 {problem_number}번을 즐겨찾기에서 제거했습니다.", text_color="green")

    def open_on_jungol(self):
        if self.current_problem:
            link = self.current_problem.get('link')
            if link:
                import webbrowser
                webbrowser.open(link)
            else:
                self.status_label.configure(text="이 문제에 대한 링크가 없습니다.", text_color="orange")

