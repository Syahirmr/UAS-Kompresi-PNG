"""
Preview Component
Side-by-side image preview display
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps, ImageTk
from src.utils.config import (
    FONT_NORMAL, BG_ACCENT,
    TEXT_SECONDARY, PADDING_NORMAL,
    PADDING_SMALL, PREVIEW_WIDTH, PREVIEW_HEIGHT
)


class PreviewComponent(ttk.LabelFrame):
    """Side-by-side preview of original and compressed images."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Preview Results", padding=PADDING_NORMAL)
        self.pack(fill=tk.BOTH, expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        self.original_image_path = None
        self.original_photo = None
        
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

        self.original_label.bind("<Configure>", self._on_original_resize)
        
    
    def display_images(self, original_path, compressed_path):
        """
        Display original image only for dataset loading milestone.
        """
        self.display_original(original_path)
        self.compressed_label.config(text="[ COMPRESSED PREVIEW ]")

    def display_original(self, original_path):
        """Load and display the original image fitted to the preview panel."""
        self.original_image_path = original_path
        self._render_original()

    def _on_original_resize(self, event):
        """Re-render preview when the label size changes."""
        if self.original_image_path:
            self._render_original()

    def _render_original(self):
        """Render original image while preserving aspect ratio."""
        try:
            with Image.open(self.original_image_path) as image:
                image = image.copy()
        except OSError:
            self.original_photo = None
            self.original_label.config(
                image="",
                text="[ ORIGINAL PREVIEW FAILED ]",
                fg=TEXT_SECONDARY
            )
            return

        max_width = self.original_label.winfo_width()
        max_height = self.original_label.winfo_height()
        if max_width <= 1 or max_height <= 1:
            max_width = PREVIEW_WIDTH
            max_height = PREVIEW_HEIGHT

        image = ImageOps.contain(
            image,
            (max_width, max_height),
            Image.Resampling.LANCZOS
        )

        preview_canvas = Image.new("RGBA", (max_width, max_height), BG_ACCENT)
        offset_x = (max_width - image.width) // 2
        offset_y = (max_height - image.height) // 2

        if image.mode == "RGBA":
            preview_canvas.paste(image, (offset_x, offset_y), image)
        else:
            preview_canvas.paste(image, (offset_x, offset_y))

        self.original_photo = ImageTk.PhotoImage(preview_canvas)
        self.original_label.config(image=self.original_photo, text="")

    def clear(self):
        """Clear preview placeholders."""
        self.original_image_path = None
        self.original_photo = None
        self.original_label.config(image="", text="[ ORIGINAL PREVIEW ]")
        self.compressed_label.config(text="[ COMPRESSED PREVIEW ]")
