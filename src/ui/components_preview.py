"""
Preview Component
Side-by-side image preview display
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import (
    FONT_NORMAL, BG_ACCENT,
    TEXT_SECONDARY, PADDING_NORMAL,
    PADDING_SMALL
)


class PreviewComponent(ttk.LabelFrame):
    """Side-by-side preview of original and compressed images."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Preview Results", padding=PADDING_NORMAL)
        self.pack(fill=tk.BOTH, expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        # Preview container
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Original image panel
        original_panel = ttk.LabelFrame(
            preview_frame,
            text="Original Image",
            padding=PADDING_NORMAL
        )
        original_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING_NORMAL))
        
        # Original image placeholder
        self.original_label = tk.Label(
            original_panel,
            text="[ ORIGINAL PREVIEW ]",
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
            width=40,
            height=20,
            relief=tk.SUNKEN,
            borderwidth=1,
            justify=tk.CENTER
        )
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        # Compressed image panel
        compressed_panel = ttk.LabelFrame(
            preview_frame,
            text="Compressed Image",
            padding=PADDING_NORMAL
        )
        compressed_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(PADDING_NORMAL, 0))
        
        # Compressed preview placeholder
        self.compressed_label = tk.Label(
            compressed_panel,
            text="[ COMPRESSED PREVIEW ]",
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
            width=40,
            height=20,
            relief=tk.SUNKEN,
            borderwidth=1,
            justify=tk.CENTER
        )
        self.compressed_label.pack(fill=tk.BOTH, expand=True)
        
    
    def display_images(self, original_path, compressed_path):
        """
        Placeholder for preview display.
        
        MILESTONE 2: Dataset loader akan connect ke sini.
        """
        self.original_label.config(text="[ ORIGINAL PREVIEW ]")
        self.compressed_label.config(text="[ COMPRESSED PREVIEW ]")

    def clear(self):
        """Clear preview placeholders."""
        self.original_label.config(text="[ ORIGINAL PREVIEW ]")
        self.compressed_label.config(text="[ COMPRESSED PREVIEW ]")
