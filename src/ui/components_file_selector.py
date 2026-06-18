"""
File Selector Component
For navigating through dataset files
"""

import customtkinter as ctk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    PADDING_NORMAL, PADDING_SMALL
)


class FileSelectorComponent(ctk.CTkFrame):
    """File navigation and selection panel styled as a modern card."""
    
    def __init__(self, parent):
        # Card container setup
        super().__init__(
            parent, 
            fg_color=BG_ACCENT, 
            corner_radius=8, 
            border_width=1, 
            border_color=("#dddddd", "#3f3f3f")
        )
        self.pack(fill="x", padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.current_file_var = ctk.StringVar(value="No file selected")
        self.file_info_var = ctk.StringVar(value="0/0")
        self.change_callback = None
        
        # Section Title
        nav_title = ctk.CTkLabel(
            self,
            text="File Navigation",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 2, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        nav_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        # File dropdown list
        list_frame = ctk.CTkFrame(self, fg_color="transparent")
        list_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        list_label = ctk.CTkLabel(
            list_frame,
            text="File List:",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        list_label.pack(side="left", padx=(0, PADDING_NORMAL))
        
        self.file_list = ctk.CTkOptionMenu(
            list_frame,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            dropdown_font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            command=self._on_dropdown_change,
            height=36,
            width=280,
            fg_color=BUTTON_BG,
            button_color=BUTTON_BG,
            button_hover_color=BUTTON_HOVER,
            dropdown_fg_color=BG_ACCENT,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=BUTTON_HOVER,
            text_color=BUTTON_FG
        )
        self.file_list.configure(values=[])
        self.file_list.set("")
        self.file_list.pack(side="left", fill="x", expand=True)
        
        # Current file path label
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Current File:",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        info_label.pack(side="left", padx=(0, PADDING_NORMAL))
        
        self.file_display = ctk.CTkLabel(
            info_frame,
            textvariable=self.current_file_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY,
            wraplength=600,
            justify="left",
            anchor="w"
        )
        self.file_display.pack(side="left", fill="x", expand=True)
        
        # Navigation buttons row
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Previous button
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ Previous",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=6,
            height=36,
            width=120,
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Next button
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=6,
            height=36,
            width=120,
            state="disabled"
        )
        self.next_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Position badge
        counter_label = ctk.CTkLabel(
            nav_frame,
            text="Position:",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        counter_label.pack(side="left", padx=(PADDING_NORMAL, 0))
        
        self.counter_display = ctk.CTkLabel(
            nav_frame,
            textvariable=self.file_info_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY,
            fg_color=("#e5e5e5", "#3a3a3a"),
            corner_radius=6,
            padx=10,
            pady=4,
            width=60
        )
        self.counter_display.pack(side="left", padx=(PADDING_NORMAL, 0))

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
