"""
File Selector Component
For navigating through dataset files
"""

import customtkinter as ctk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    PADDING_NORMAL, PADDING_SMALL, BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR
)


class FileSelectorComponent(ctk.CTkFrame):
    """File navigation and selection panel styled as a modern horizontal toolbar."""
    
    def __init__(self, parent):
        # Card container setup
        super().__init__(
            parent, 
            fg_color=BG_ACCENT, 
            corner_radius=BORDER_RADIUS, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        self.pack(fill="x", padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.current_file_var = ctk.StringVar(value="No file selected")
        self.file_info_var = ctk.StringVar(value="0/0")
        self.change_callback = None
        
        # Horizontal layout alignment
        # Left section: File list dropdown and counter
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.pack(side="left", fill="y", padx=(PADDING_NORMAL, 0), pady=PADDING_SMALL)
        
        list_label = ctk.CTkLabel(
            left_container,
            text="File List:",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        list_label.pack(side="left", padx=(0, PADDING_SMALL))
        
        self.file_list = ctk.CTkOptionMenu(
            left_container,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            dropdown_font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            command=self._on_dropdown_change,
            height=36,
            width=220,
            fg_color=BUTTON_BG,
            button_color=BUTTON_BG,
            button_hover_color=BUTTON_HOVER,
            dropdown_fg_color=BG_ACCENT,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=BUTTON_HOVER,
            text_color=BUTTON_FG,
            corner_radius=CONTROL_RADIUS
        )
        self.file_list.configure(values=[])
        self.file_list.set("")
        self.file_list.pack(side="left", padx=PADDING_SMALL)
        
        self.counter_display = ctk.CTkLabel(
            left_container,
            textvariable=self.file_info_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY,
            fg_color=("#e5e5e5", "#3a3a3a"),
            corner_radius=CONTROL_RADIUS,
            padx=10,
            pady=4,
            width=65
        )
        self.counter_display.pack(side="left", padx=PADDING_SMALL)

        # Right section: Navigation buttons (packed first from the right)
        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.pack(side="right", fill="y", padx=(0, PADDING_NORMAL), pady=PADDING_SMALL)

        self.next_btn = ctk.CTkButton(
            right_container,
            text="Next ▶",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=36,
            width=100,
            state="disabled"
        )
        self.next_btn.pack(side="right", padx=(PADDING_SMALL, 0))
        
        self.prev_btn = ctk.CTkButton(
            right_container,
            text="◀ Previous",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=36,
            width=100,
            state="disabled"
        )
        self.prev_btn.pack(side="right", padx=PADDING_SMALL)

        # Middle section: Current file path label
        middle_container = ctk.CTkFrame(self, fg_color="transparent")
        middle_container.pack(side="left", fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)

        path_label = ctk.CTkLabel(
            middle_container,
            text="Current File:",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        path_label.pack(side="left", padx=(0, PADDING_SMALL))

        self.file_display = ctk.CTkLabel(
            middle_container,
            textvariable=self.current_file_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY,
            wraplength=500,
            justify="left",
            anchor="w"
        )
        self.file_display.pack(side="left", fill="x", expand=True)

    def set_change_callback(self, callback):
        """Set callback for combobox selection change event."""
        self.change_callback = callback

    def _on_dropdown_change(self, value):
        """Triggered on option change; delegates to change_callback."""
        # Sync label string var
        self.current_file_var.set(value)
        # Find index and update counter
        values = self.file_list.cget("values")
        if value in values:
            idx = values.index(value)
            self._update_counter(idx, len(values))
        if self.change_callback:
            self.change_callback(None) # pass dummy event argument for compatibility
    
    def populate_files(self, file_list):
        """Populate file list combobox."""
        self.file_list.configure(values=file_list)
        if file_list:
            self.file_list.set(file_list[0])
            self.current_file_var.set(file_list[0])
            self._update_counter(0, len(file_list))
            self.next_btn.configure(state="normal" if len(file_list) > 1 else "disabled")
        else:
            self.clear()
    
    def get_current_file(self):
        """Get currently selected file."""
        return self.file_list.get()

    def get_current_index(self):
        """Get selected file index."""
        val = self.file_list.get()
        values = self.file_list.cget("values")
        if val in values:
            return values.index(val)
        return -1

    def select_index(self, index):
        """Select file by index and update navigation state."""
        values = self.file_list.cget("values")
        if not values or index < 0 or index >= len(values):
            return

        self.file_list.set(values[index])
        self.current_file_var.set(values[index])
        self._update_counter(index, len(values))

    def clear(self):
        """Clear all file selector values."""
        self.file_list.configure(values=[])
        self.file_list.set("")
        self.current_file_var.set("No file selected")
        self.file_info_var.set("0/0")
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")
    
    def _update_counter(self, current, total):
        """Update file counter display and button active states."""
        self.file_info_var.set(f"{current + 1}/{total}")
        self.prev_btn.configure(state="normal" if current > 0 else "disabled")
        self.next_btn.configure(state="normal" if current < total - 1 else "disabled")
