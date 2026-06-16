"""
File Selector Component
For navigating through dataset files
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, BG_ACCENT,
    TEXT_PRIMARY, BUTTON_BG, BUTTON_FG,
    PADDING_NORMAL, PADDING_SMALL
)


class FileSelectorComponent(ttk.LabelFrame):
    """File navigation and selection panel."""
    
    def __init__(self, parent):
        super().__init__(parent, text="File Navigation", padding=PADDING_NORMAL)
        self.pack(fill=tk.X, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.current_file_var = tk.StringVar(value="No file selected")
        self.file_info_var = tk.StringVar(value="0/0")
        
        # Container
        container = ttk.Frame(self)
        container.pack(fill=tk.X)
        
        # File list (combobox)
        list_frame = ttk.Frame(container)
        list_frame.pack(fill=tk.X, pady=(0, PADDING_NORMAL))
        
        list_label = tk.Label(
            list_frame,
            text="File List:",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        list_label.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        self.file_list = ttk.Combobox(
            list_frame,
            state="readonly",
            font=FONT_NORMAL,
            width=60
        )
        self.file_list.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Current file info
        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.X, pady=(0, PADDING_NORMAL))
        
        info_label = tk.Label(
            info_frame,
            text="Current File:",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        info_label.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        self.file_display = tk.Label(
            info_frame,
            textvariable=self.current_file_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            wraplength=800,
            justify=tk.LEFT
        )
        self.file_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Navigation buttons
        nav_frame = ttk.Frame(container)
        nav_frame.pack(fill=tk.X)
        
        # Previous button
        self.prev_btn = tk.Button(
            nav_frame,
            text="◀ Previous",
            font=FONT_NORMAL,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Next button
        self.next_btn = tk.Button(
            nav_frame,
            text="Next ▶",
            font=FONT_NORMAL,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # File counter
        counter_label = tk.Label(
            nav_frame,
            text="Position:",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        counter_label.pack(side=tk.LEFT, padx=(PADDING_NORMAL, 0))
        
        self.counter_display = tk.Label(
            nav_frame,
            textvariable=self.file_info_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            width=10
        )
        self.counter_display.pack(side=tk.LEFT, padx=(PADDING_NORMAL, 0))
    
    
    def populate_files(self, file_list):
        """Populate file list combobox."""
        self.file_list['values'] = file_list
        if file_list:
            self.file_list.current(0)
            self._update_counter(0, len(file_list))
            self.next_btn.config(state=tk.NORMAL if len(file_list) > 1 else tk.DISABLED)
    
    def get_current_file(self):
        """Get currently selected file."""
        return self.file_list.get()
    
    def _update_counter(self, current, total):
        """Update file counter display."""
        self.file_info_var.set(f"{current + 1}/{total}")
        # Update navigation buttons state
        self.prev_btn.config(state=tk.NORMAL if current > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if current < total - 1 else tk.DISABLED)
