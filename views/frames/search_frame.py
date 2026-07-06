"""
Search Frame for Jungol Recommender.
Allows the user to search for problems by number, title, or tag.
"""

import customtkinter as ctk

class SearchFrame(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        self.search_label = ctk.CTkLabel(self.search_frame, text="검색:")
        self.search_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="문제 번호, 제목 또는 태그를 입력하세요...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<Return>", self.search_event)

        self.search_button = ctk.CTkButton(self.search_frame, text="검색", command=self.search_event)
        self.search_button.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="ew")

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.search_number_var = ctk.BooleanVar(value=True)
        self.search_number_cb = ctk.CTkCheckBox(self.options_frame, text="번호", variable=self.search_number_var)
        self.search_number_cb.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.search_title_var = ctk.BooleanVar(value=True)
        self.search_title_cb = ctk.CTkCheckBox(self.options_frame, text="제목", variable=self.search_title_var)
        self.search_title_cb.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.search_tag_var = ctk.BooleanVar(value=True)
        self.search_tag_cb = ctk.CTkCheckBox(self.options_frame, text="태그", variable=self.search_tag_var)
        self.search_tag_cb.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.results_frame = ctk.CTkScrollableFrame(self, label_text="검색 결과")
        self.results_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)

        self.result_widgets = []

    def search_event(self, event=None):
        query = self.search_entry.get().strip()
        if not query:
            self.show_results([])
            return

        search_in = []
        if self.search_number_var.get():
            search_in.append("number")
        if self.search_title_var.get():
            search_in.append("title")
        if self.search_tag_var.get():
            search_in.append("tag")

        results = self._perform_search(query, search_in)
        self.show_results(results)

    def _perform_search(self, query: str, search_in: list) -> list:
        results = []
        problems = self.model.get_problems()
        for problem in problems:
            match = False
            if "number" in search_in:
                try:
                    query_num = int(query)
                    if problem.get("number") == query_num:
                        match = True
                except ValueError:
                    if str(problem.get("number")) == query:
                        match = True
            if not match and "title" in search_in:
                if query.lower() in problem.get("title", "").lower():
                    match = True
            if not match and "tag" in search_in:
                tags = problem.get("tags", [])
                for tag in tags:
                    if query.lower() in tag.lower():
                        match = True
                        break
            if match:
                results.append(problem)
        return results

    def show_results(self, results: list):
        for widget in self.result_widgets:
            widget.destroy()
        self.result_widgets.clear()

        if not results:
            no_results_label = ctk.CTkLabel(self.results_frame, text="검색 결과가 없습니다.")
            no_results_label.grid(row=0, column=0, padx=10, pady=10)
            self.result_widgets.append(no_results_label)
            return

        for i, problem in enumerate(results):
            result_frame = ctk.CTkFrame(self.results_frame)
            result_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            result_frame.grid_columnconfigure(0, weight=1)

            info_text = f"#{problem.get('number')} - {problem.get('title')}"
            info_label = ctk.CTkLabel(result_frame, text=info_text, anchor="w")
            info_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

            meta_text = f"난이도: {problem.get('tier', 'N/A')} | 태그: {', '.join(problem.get('tags', []))}"
            meta_label = ctk.CTkLabel(result_frame, text=meta_text, anchor="w", font=ctk.CTkFont(size=12))
            meta_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

            view_button = ctk.CTkButton(result_frame, text="상세 보기", command=lambda p=problem: self.view_problem_details(p))
            view_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

            self.result_widgets.append(result_frame)

    def view_problem_details(self, problem: dict):
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(f"문제 #{problem.get('number')}")
        detail_window.geometry("500x400")

        details = f"문제 번호: {problem.get('number')}\n\n"
        details += f"제목: {problem.get('title')}\n\n"
        details += f"난이도: {problem.get('tier')}\n\n"
        details += f"태그: {', '.join(problem.get('tags', []))}\n\n"
        details += f"링크: {problem.get('link')}\n\n"
        details += f"설명:\n{problem.get('description', '설명이 없습니다.')}"

        textbox = ctk.CTkTextbox(detail_window, wrap="word")
        textbox.pack(padx=10, pady=10, fill="both", expand=True)
        textbox.insert("1.0", details)
        textbox.configure(state="disabled")

