"""
Folder Picker Component
For selecting dataset directory
"""

import customtkinter as ctk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    SUCCESS_COLOR, ERROR_COLOR, PADDING_NORMAL, PADDING_SMALL,
    BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR
)


class FolderPickerComponent(ctk.CTkFrame):
    """Folder picker and dataset validation panel styled as a modern card."""
    
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
        
        self.selected_folder = ctk.StringVar(value="No folder selected")
        self.validation_status = ctk.StringVar(value="Dataset belum dipilih")
        
        # Section Header Title
        folder_title = ctk.CTkLabel(
            self,
            text="Dataset Selection",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 2, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        folder_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        # Folder path display
        self.folder_display = ctk.CTkLabel(
            self,
            textvariable=self.selected_folder,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_PRIMARY,
            wraplength=800,
            justify="left"
        )
        self.folder_display.pack(anchor="w", fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Action Bar (Browse, info, count)
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Browse Button
        self.browse_btn = ctk.CTkButton(
            action_frame,
            text="Browse Folder",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=36,
            width=140
        )
        self.browse_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Info Label
        info_label = ctk.CTkLabel(
            action_frame,
            text="✓ Pilih folder yang berisi file PNG (minimum 10 file)",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY
        )
        info_label.pack(side="left", fill="x", expand=True, anchor="w")
        
        # File count badge
        self.file_count_var = ctk.StringVar(value="Files found: 0")
        self.count_badge = ctk.CTkLabel(
            action_frame,
            textvariable=self.file_count_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY,
            fg_color=("#e5e5e5", "#3a3a3a"),
            corner_radius=CONTROL_RADIUS,
            padx=10,
            pady=4
        )
        self.count_badge.pack(side="right")

        # Validation status label
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.validation_status,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=ERROR_COLOR,
            justify="left"
        )
        self.status_label.pack(anchor="w", fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
    
    def get_selected_folder(self):
        """Return selected folder path."""
        return self.selected_folder.get()
    
    def set_file_count(self, count):
        """Update file count display."""
        self.file_count_var.set(f"Files found: {count}")

    def set_selected_folder(self, folder_path):
        """Update selected folder display."""
        self.selected_folder.set(str(folder_path))

    def set_validation_status(self, message, valid=False):
        """Update dataset validation status."""
        self.validation_status.set(message)
        self.status_label.configure(text_color=SUCCESS_COLOR if valid else ERROR_COLOR)
