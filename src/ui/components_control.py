"""
Control Panel Component
Contains compression controls, algorithm selector, and progress monitoring
"""

import customtkinter as ctk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_SMALL, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    PROGRESS_COLOR, PADDING_NORMAL, PADDING_SMALL,
    BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR
)

ALGORITHM_OPTIONS = [
    ("Deflate Baseline", "deflate"),
    ("Zopfli", "zopfli"),
    ("OxiPNG", "oxipng"),
]


class ControlPanelComponent(ctk.CTkFrame):
    """Control panel with algorithm selector, compression buttons, comparison button and progress bar."""
    
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
        
        self.change_callback = None
        
        # ---- Algorithm selector row ----
        algo_frame = ctk.CTkFrame(self, fg_color="transparent")
        algo_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, PADDING_NORMAL))

        algo_label = ctk.CTkLabel(
            algo_frame,
            text="Algorithm:",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        algo_label.pack(side="left", padx=(0, PADDING_NORMAL))

        self.algorithm_var = ctk.StringVar(value="Deflate Baseline")
        
        self.algorithm_combo = ctk.CTkOptionMenu(
            algo_frame,
            variable=self.algorithm_var,
            values=[label for label, _ in ALGORITHM_OPTIONS],
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            dropdown_font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            command=self._on_algorithm_change,
            height=36,
            width=200,
            fg_color=BUTTON_BG,
            button_color=BUTTON_BG,
            button_hover_color=BUTTON_HOVER,
            dropdown_fg_color=BG_ACCENT,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=BUTTON_HOVER,
            text_color=BUTTON_FG,
            corner_radius=CONTROL_RADIUS
        )
        self.algorithm_combo.pack(side="left")

        # Zopfli speed warning label (shown/hidden based on selection)
        self.zopfli_warning_var = ctk.StringVar(
            value="⚠ Zopfli bisa sangat lambat untuk dataset besar (60s timeout per file)."
        )
        self.zopfli_warning_label = ctk.CTkLabel(
            algo_frame,
            textvariable=self.zopfli_warning_var,
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
            text_color=("#d83b01", "#da3637"),
            wraplength=500,
            justify="left"
        )
        self.zopfli_warning_label.pack(side="left", padx=(15, 0))
        # Default: hidden
        self.zopfli_warning_label.pack_forget()

        # ---- Button frame ----
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Compress button
        self.compress_btn = ctk.CTkButton(
            button_frame,
            text="▶ Start Compression",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            fg_color=("#0078d4", "#1f77b4"),
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=40,
            width=180
        )
        self.compress_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="⏹ Cancel",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            fg_color=("#e81123", "#d11a2a"),
            text_color=BUTTON_FG,
            hover_color=("#ff3b30", "#e63946"),
            corner_radius=CONTROL_RADIUS,
            height=40,
            width=140,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Comparison button
        self.comparison_btn = ctk.CTkButton(
            button_frame,
            text="📊 Run Comparison",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            fg_color=("#6b3fa0", "#8e44ad"),
            text_color=BUTTON_FG,
            hover_color=("#7b4fa8", "#9b59b6"),
            corner_radius=CONTROL_RADIUS,
            height=40,
            width=180
        )
        self.comparison_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Export button
        self.export_btn = ctk.CTkButton(
            button_frame,
            text="📤 Export Results",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            fg_color=("#107c10", "#2ea44f"),
            text_color=BUTTON_FG,
            hover_color=("#1f9d1f", "#34d058"),
            corner_radius=CONTROL_RADIUS,
            height=40,
            width=180,
            state="disabled"
        )
        self.export_btn.pack(side="left")
        
        # Progress frame
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Progress label
        progress_label = ctk.CTkLabel(
            progress_frame,
            text="Progress:",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        progress_label.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            orientation="horizontal",
            progress_color=("#0078d4", "#1f77b4"),
            fg_color=("#e5e5e5", "#3a3a3a"),
            height=14,
            corner_radius=7
        )
        self.progress_bar.set(0.0) # ctk progress ranges from 0.0 to 1.0
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, PADDING_NORMAL))
        
        # Progress percentage
        self.progress_text = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY,
            width=40
        )
        self.progress_text.pack(side="left")
        
        # Status frame
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Status label
        status_title = ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        status_title.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Status text
        self.status_var = ctk.StringVar(value="Ready")
        self.status_text = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY,
            justify="left",
            anchor="w"
        )
        self.status_text.pack(side="left", fill="x", expand=True)

    def _on_algorithm_change(self, value=None):
        """Show Zopfli warning when Zopfli is selected."""
        if self.get_algorithm() == "zopfli":
            self.zopfli_warning_label.pack(side="left", padx=(15, 0))
        else:
            self.zopfli_warning_label.pack_forget()

        if self.change_callback:
            self.change_callback(self.get_algorithm())

    def set_change_callback(self, callback):
        """Set callback for algorithm selection change event."""
        self.change_callback = callback

    def set_progress(self, value):
        """Update progress bar (expected value: 0 to 100)."""
        bounded_value = max(0, min(100, value))
        self.progress_bar.set(bounded_value / 100.0)
        self.progress_text.configure(text=f"{int(bounded_value)}%")
    
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
        """Enable algorithm selector."""
        self.algorithm_combo.configure(state="normal")

    def disable_algorithm_selector(self):
        """Disable algorithm selector during compression."""
        self.algorithm_combo.configure(state="disabled")

    def enable_compress(self):
        """Enable compress button."""
        self.compress_btn.configure(state="normal")
    
    def disable_compress(self):
        """Disable compress button."""
        self.compress_btn.configure(state="disabled")

    def enable_comparison(self):
        """Enable comparison button."""
        self.comparison_btn.configure(state="normal")

    def disable_comparison(self):
        """Disable comparison button."""
        self.comparison_btn.configure(state="disabled")
    
    def enable_cancel(self):
        """Enable cancel button."""
        self.cancel_btn.configure(state="normal")
    
    def disable_cancel(self):
        """Disable cancel button."""
        self.cancel_btn.configure(state="disabled")
    
    def enable_export(self):
        """Enable export button."""
        self.export_btn.configure(state="normal")
    
    def disable_export(self):
        """Disable export button."""
        self.export_btn.configure(state="disabled")
