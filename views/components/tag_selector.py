"""
Tag Selector Component.
Allows the user to select multiple tags from a list.
"""

import customtkinter as ctk
from typing import List

class TagSelector(ctk.CTkFrame):
    def __init__(self, master, model, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.model = model
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="태그:")
        self.label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="태그 선택", height=150)
        self.scrollable_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.tag_variables = {}

        self.update_tags()

    def update_tags(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.tag_variables.clear()

        tags = self.model.get_tags()
        for i, tag in enumerate(tags):
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=tag, variable=var, command=self._on_tag_change)
            cb.grid(row=i, column=0, padx=5, pady=2, sticky="w")
            self.tag_variables[tag] = var

    def _on_tag_change(self):
        selected_tags = [tag for tag, var in self.tag_variables.items() if var.get()]
        self.model.set_selected_tags(selected_tags)

    def get_selected_tags(self) -> List[str]:
        return [tag for tag, var in self.tag_variables.items() if var.get()]

