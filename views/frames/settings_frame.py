"""
Settings Frame for Jungol Recommender.
Allows the user to configure application settings.
"""

import customtkinter as ctk
import tkinter.messagebox as tkmb

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="설정")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.appearance_mode_label = ctk.CTkLabel(self.scrollable_frame, text="화면 모드:", font=ctk.CTkFont(size=16))
        self.appearance_mode_label.grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.scrollable_frame, values=["밝음", "어두움", "시스템"], command=self.change_appearance_mode)
        self.appearance_mode_optionmenu.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.appearance_mode_optionmenu.set("어두움")

        self.default_mode_label = ctk.CTkLabel(self.scrollable_frame, text="기본 추천 모드:", font=ctk.CTkFont(size=16))
        self.default_mode_label.grid(row=2, column=0, padx=10, pady=(20, 5), sticky="w")
        self.default_mode_optionmenu = ctk.CTkOptionMenu(self.scrollable_frame, values=["랜덤", "순차", "쉬움", "어려움"], command=self.change_default_mode)
        self.default_mode_optionmenu.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.default_mode_optionmenu.set("랜덤")

        self.auto_update_label = ctk.CTkLabel(self.scrollable_frame, text="자동 업데이트:", font=ctk.CTkFont(size=16))
        self.auto_update_label.grid(row=4, column=0, padx=10, pady=(20, 5), sticky="w")
        self.auto_update_var = ctk.BooleanVar(value=True)
        self.auto_update_checkbox = ctk.CTkCheckBox(self.scrollable_frame, text="시작 시 자동 데이터 업데이트 사용", variable=self.auto_update_var)
        self.auto_update_checkbox.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

        self.cache_label = ctk.CTkLabel(self.scrollable_frame, text="캐시:", font=ctk.CTkFont(size=16))
        self.cache_label.grid(row=6, column=0, padx=10, pady=(20, 5), sticky="w")
        self.clear_cache_button = ctk.CTkButton(self.scrollable_frame, text="캐시 비우기", command=self.clear_cache)
        self.clear_cache_button.grid(row=7, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.update_button = ctk.CTkButton(self.scrollable_frame, text="지금 데이터 업데이트", command=self.update_data_now)
        self.update_button.grid(row=8, column=0, padx=10, pady=(20, 10), sticky="ew")

        self.version_label = ctk.CTkLabel(self.scrollable_frame, text="정올 문제 추천기 v1.0", font=ctk.CTkFont(size=12))
        self.version_label.grid(row=9, column=0, padx=10, pady=(20, 10), sticky="ew")

    def change_appearance_mode(self, new_mode: str):
        mode_map = {"밝음": "light", "어두움": "dark", "시스템": "system"}
        ctk.set_appearance_mode(mode_map.get(new_mode, "dark"))

    def change_default_mode(self, choice: str):
        mode_map = {"랜덤": "random", "순차": "sequential", "쉬움": "easy", "어려움": "hard"}
        mode = mode_map.get(choice, "random")
        self.model.recommendation_mode = mode

    def clear_cache(self):
        if self.model.cache_service:
            self.model.cache_service.clear_cache()
            tkmb.showinfo("캐시 비움", "캐시가 비워졌습니다. 다음 업데이트 시 데이터를 다시 다운로드합니다.")
        else:
            tkmb.showerror("오류", "캐시 서비스를 사용할 수 없습니다.")

    def update_data_now(self):
        self.model.stop_background_tasks()
        self.model.start_background_tasks()
        tkmb.showinfo("업데이트 시작", "데이터 업데이트가 백그라운드에서 시작되었습니다. 대시보드에서 진행 상황을 확인하세요.")

