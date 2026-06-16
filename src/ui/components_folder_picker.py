"""
Folder Picker Component
For selecting dataset directory
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, BG_ACCENT,
    TEXT_PRIMARY, BUTTON_BG, BUTTON_FG,
    PADDING_NORMAL, PADDING_SMALL
)


class FolderPickerComponent(ttk.LabelFrame):
    """Folder picker and dataset validation panel."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Dataset Selection", padding=PADDING_NORMAL)
        self.pack(fill=tk.X, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.selected_folder = tk.StringVar(value="No folder selected")
        
        # Container frame
        container = ttk.Frame(self)
        container.pack(fill=tk.X)
        
        # Selected folder display
        folder_label = tk.Label(
            container,
            text="Selected Folder:",
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        folder_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Folder path display
        self.folder_display = tk.Label(
            container,
            textvariable=self.selected_folder,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            wraplength=600,
            justify=tk.LEFT
        )
        self.folder_display.pack(anchor=tk.W, fill=tk.X, pady=(0, PADDING_NORMAL))
        
        # Button frame
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(PADDING_NORMAL, 0))
        
        # Browse button
        self.browse_btn = tk.Button(
            button_frame,
            text="Browse Folder",
            font=FONT_NORMAL,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.browse_btn.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Info label
        info_label = tk.Label(
            button_frame,
            text="✓ Pilih folder yang berisi file PNG (minimum 10 file)",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # File count placeholder
        self.file_count_var = tk.StringVar(value="Files found: 0")
        count_label = tk.Label(
            button_frame,
            textvariable=self.file_count_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        count_label.pack(side=tk.RIGHT)
    
    
    def get_selected_folder(self):
        """Return selected folder path."""
        return self.selected_folder.get()
    
    def set_file_count(self, count):
        """Update file count display."""
        self.file_count_var.set(f"Files found: {count}")
