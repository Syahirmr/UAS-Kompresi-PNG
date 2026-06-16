"""
Header Component
Displays application title and information
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import (
    FONT_TITLE, FONT_SMALL, BG_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, PADDING_NORMAL
)


class HeaderComponent(ttk.Frame):
    """Header section with application title and info."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="Header.TFrame")
        
        # Main container
        self.pack(fill=tk.X, padx=PADDING_NORMAL, pady=PADDING_NORMAL)
        
        # Title
        title_label = tk.Label(
            self,
            text="PNG Compression Comparison System",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_SECONDARY
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            self,
            text="Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI",
            font=FONT_SMALL,
            fg=TEXT_SECONDARY,
            bg=BG_SECONDARY
        )
        subtitle_label.pack(anchor=tk.W)
        
        # Separator
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=PADDING_NORMAL)
