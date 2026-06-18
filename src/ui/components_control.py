"""
Control Panel Component
Contains compression controls, algorithm selector, and progress monitoring
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_SMALL, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG,
    PROGRESS_COLOR, PADDING_NORMAL, PADDING_SMALL
)


ALGORITHM_OPTIONS = [
    ("Deflate Baseline", "deflate"),
    ("Zopfli", "zopfli"),
    ("OxiPNG", "oxipng"),
]


class ControlPanelComponent(ttk.LabelFrame):
    """Control panel with algorithm selector, compression buttons, comparison button and progress bar."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Compression Control", padding=PADDING_NORMAL)
        self.pack(fill=tk.X, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        # ---- Algorithm selector row ----
        algo_frame = ttk.Frame(self)
        algo_frame.pack(fill=tk.X, pady=(0, PADDING_NORMAL))

        algo_label = tk.Label(
            algo_frame,
            text="Algorithm:",
            font=FONT_HEADING,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        algo_label.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))

        self.algorithm_var = tk.StringVar(value="deflate")
        self.algorithm_combo = ttk.Combobox(
            algo_frame,
            textvariable=self.algorithm_var,
            values=[label for label, _ in ALGORITHM_OPTIONS],
            state="readonly",
            font=FONT_NORMAL,
            width=25,
        )
        self.algorithm_combo.current(0)
        self.algorithm_combo.pack(side=tk.LEFT)

        # Zopfli speed warning label (shown/hidden based on selection)
        self.zopfli_warning_var = tk.StringVar(
            value="⚠ Zopfli bisa sangat lambat untuk dataset besar (60s timeout per file)."
        )
        self.zopfli_warning_label = tk.Label(
            algo_frame,
            textvariable=self.zopfli_warning_var,
            font=FONT_SMALL,
            fg="#d83b01",
            bg=BG_ACCENT,
            wraplength=500,
            justify=tk.LEFT
        )
        self.zopfli_warning_label.pack(side=tk.LEFT, padx=(10, 0))
        # Default: hidden
        self.zopfli_warning_label.pack_forget()

        # Bind algorithm combo selection to show/hide warning
        self.algorithm_combo.bind("<<ComboboxSelected>>", self._on_algorithm_change)

        # ---- Button frame ----
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(0, PADDING_NORMAL))
        
        # Compress button
        self.compress_btn = tk.Button(
            button_frame,
            text="▶ Start Compression",
            font=FONT_HEADING,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.NORMAL
        )
        self.compress_btn.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Cancel button
        self.cancel_btn = tk.Button(
            button_frame,
            text="⏹ Cancel",
            font=FONT_HEADING,
            bg="#e81123",
            fg=BUTTON_FG,
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Comparison button
        self.comparison_btn = tk.Button(
            button_frame,
            text="📊 Run Comparison",
            font=FONT_HEADING,
            bg="#6b3fa0",
            fg=BUTTON_FG,
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.NORMAL
        )
        self.comparison_btn.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Export button
        self.export_btn = tk.Button(
            button_frame,
            text="📊 Export Results",
            font=FONT_HEADING,
            bg="#107c10",
            fg=BUTTON_FG,
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=(PADDING_NORMAL, 0))
        
        # Progress label
        progress_label = tk.Label(
            progress_frame,
            text="Progress:",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        progress_label.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, PADDING_NORMAL))
        
        # Progress percentage
        self.progress_text = tk.Label(
            progress_frame,
            text="0%",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            width=5
        )
        self.progress_text.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=(PADDING_NORMAL, 0))
        
        # Status label
        status_title = tk.Label(
            status_frame,
            text="Status:",
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        status_title.pack(side=tk.LEFT, padx=(0, PADDING_NORMAL))
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_text = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            width=80,
            justify=tk.LEFT
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.X, expand=True)


    def _on_algorithm_change(self, event=None):
        """Show Zopfli warning when Zopfli is selected."""
        if self.get_algorithm() == "zopfli":
            self.zopfli_warning_label.pack(side=tk.LEFT, padx=(10, 0))
        else:
            self.zopfli_warning_label.pack_forget()


    def set_progress(self, value):
        """Update progress bar."""
        bounded_value = max(0, min(100, value))
        self.progress_var.set(bounded_value)
        self.progress_text.config(text=f"{int(bounded_value)}%")
    
    def set_status(self, message):
        """Update status message."""
        self.status_var.set(message)
    
    def get_algorithm(self):
        """Return internal algorithm key based on current selection."""
        selected_label = self.algorithm_var.get()
        for label, key in ALGORITHM_OPTIONS:
            if label == selected_label:
                return key
        return "deflate"  # fallback

    def enable_algorithm_selector(self):
        """Enable algorithm combobox."""
        self.algorithm_combo.config(state="readonly")

    def disable_algorithm_selector(self):
        """Disable algorithm combobox during compression."""
        self.algorithm_combo.config(state=tk.DISABLED)

    def enable_compress(self):
        """Enable compress button."""
        self.compress_btn.config(state=tk.NORMAL)
    
    def disable_compress(self):
        """Disable compress button."""
        self.compress_btn.config(state=tk.DISABLED)

    def enable_comparison(self):
        """Enable comparison button."""
        self.comparison_btn.config(state=tk.NORMAL)

    def disable_comparison(self):
        """Disable comparison button."""
        self.comparison_btn.config(state=tk.DISABLED)
    
    def enable_cancel(self):
        """Enable cancel button."""
        self.cancel_btn.config(state=tk.NORMAL)
    
    def disable_cancel(self):
        """Disable cancel button."""
        self.cancel_btn.config(state=tk.DISABLED)
    
    def enable_export(self):
        """Enable export button."""
        self.export_btn.config(state=tk.NORMAL)
    
    def disable_export(self):
        """Disable export button."""
        self.export_btn.config(state=tk.DISABLED)
