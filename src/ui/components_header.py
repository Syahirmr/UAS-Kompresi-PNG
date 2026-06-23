"""
Header Component
Displays application title, subtitle, and theme toggle.
"""

import customtkinter as ctk
from src.utils.config import (
    FONT_TITLE, FONT_SMALL, BG_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, PADDING_NORMAL,
    PADDING_LARGE, BUTTON_HOVER
)


class HeaderComponent(ctk.CTkFrame):
    """Header section with application title, subtitle, and a light/dark mode switch."""
    
    def __init__(self, parent, toggle_theme_callback=None):
        super().__init__(parent, fg_color=BG_SECONDARY, corner_radius=0)
        self.pack(fill="x", padx=0, pady=0)
        
        # Setup grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        
        # Text container frame
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w", padx=PADDING_LARGE, pady=PADDING_NORMAL)
        
        # Title
        title_label = ctk.CTkLabel(
            text_frame,
            text="PNG Compression Comparison",
            font=ctk.CTkFont(family=FONT_TITLE[0], size=FONT_TITLE[1] + 6, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(0, 2))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            text_frame,
            text="Bandingkan algoritma kompresi PNG: Deflate (Baseline), Zopfli Deflate, dan OxiPNG",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] + 1),
            text_color=TEXT_SECONDARY
        )
        subtitle_label.pack(anchor="w")
        
        # Theme Switch & Settings Frame
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=0, column=1, padx=PADDING_LARGE, pady=PADDING_NORMAL, sticky="e")
        
        if toggle_theme_callback:
            self.theme_switch = ctk.CTkSwitch(
                controls_frame,
                text="Mode Gelap",
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
                command=toggle_theme_callback,
                progress_color=("#0078d4", "#2563EB")
            )
            self.theme_switch.select()  # default to Dark
            self.theme_switch.pack(side="left", padx=(0, PADDING_NORMAL))
            
        # Settings Gear Button
        self.settings_btn = ctk.CTkButton(
            controls_frame,
            text="⚙",
            font=ctk.CTkFont(size=16),
            width=36,
            height=36,
            fg_color=("#E5E7EB", "#1F2937"),
            text_color=TEXT_PRIMARY,
            hover_color=BUTTON_HOVER,
            corner_radius=8
        )
        self.settings_btn.pack(side="left")
