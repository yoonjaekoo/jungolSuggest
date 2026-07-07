"""
Tier Selector Component.
Allows the user to select a minimum and maximum tier (difficulty) range.
"""

import customtkinter as ctk

class TierSelector(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="난이도 범위:")
        self.label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 0), sticky="w")

        self.min_label = ctk.CTkLabel(self, text="최소:")
        self.min_label.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="e")
        self.min_optionmenu = ctk.CTkOptionMenu(self, values=[], command=self._on_tier_change)
        self.min_optionmenu.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="ew")

        self.max_label = ctk.CTkLabel(self, text="최대:")
        self.max_label.grid(row=2, column=0, padx=(5, 0), pady=5, sticky="e")
        self.max_optionmenu = ctk.CTkOptionMenu(self, values=[], command=self._on_tier_change)
        self.max_optionmenu.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="ew")

        self.grid_columnconfigure(1, weight=1)

        self._tier_update_id = None
        self.model.on_data_loaded(self.update_tiers)
        self.update_tiers()

    def update_tiers(self):
        if self._tier_update_id is not None:
            self.after_cancel(self._tier_update_id)
        self._tier_update_id = self.after_idle(self._do_update_tiers)

    def _do_update_tiers(self):
        self._tier_update_id = None
        tiers = self.model.get_tiers()
        if tiers:
            self.min_optionmenu.configure(values=tiers)
            self.max_optionmenu.configure(values=tiers)
            if self.min_optionmenu.get() not in tiers:
                self.min_optionmenu.set(tiers[0])
            if self.max_optionmenu.get() not in tiers:
                self.max_optionmenu.set(tiers[-1])
            self._on_tier_change()
        else:
            self.min_optionmenu.configure(values=["난이도 없음"])
            self.max_optionmenu.configure(values=["난이도 없음"])
            self.min_optionmenu.set("난이도 없음")
            self.max_optionmenu.set("난이도 없음")

    def _on_tier_change(self, choice=None):
        min_tier = self.min_optionmenu.get()
        max_tier = self.max_optionmenu.get()
        if min_tier != "난이도 없음" and max_tier != "난이도 없음":
            self.model.set_selected_tier_range(min_tier, max_tier)

