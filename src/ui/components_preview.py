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
        self.compressed_image_path = None
        self.compressed_photo = None
        
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

        self.original_preview_frame = tk.Frame(
            original_panel,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            bg=BG_ACCENT
        )
        self.original_preview_frame.pack(anchor=tk.CENTER, expand=True)
        self.original_preview_frame.pack_propagate(False)
        self.original_preview_frame.grid_propagate(False)
        
        # Original image placeholder
        self.original_label = tk.Label(
            self.original_preview_frame,
            text="[ ORIGINAL PREVIEW ]",
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
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

        self.compressed_preview_frame = tk.Frame(
            compressed_panel,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            bg=BG_ACCENT
        )
        self.compressed_preview_frame.pack(anchor=tk.CENTER, expand=True)
        self.compressed_preview_frame.pack_propagate(False)
        self.compressed_preview_frame.grid_propagate(False)
        
        # Compressed preview placeholder
        self.compressed_label = tk.Label(
            self.compressed_preview_frame,
            text="[ COMPRESSED PREVIEW ]",
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
            relief=tk.SUNKEN,
            borderwidth=1,
            justify=tk.CENTER
        )
        self.compressed_label.pack(fill=tk.BOTH, expand=True)
        
    
    def display_images(self, original_path, compressed_path):
        """
        Display original and compressed images when available.
        """
        self.display_original(original_path)
        self.display_compressed(compressed_path)

    def display_original(self, original_path):
        """Load and display the original image fitted to the preview panel."""
        self.original_image_path = original_path
        self._render_original()

    def display_compressed(self, compressed_path):
        """Load and display the compressed image when output exists."""
        self.compressed_image_path = compressed_path
        self._render_compressed()

    def _render_original(self):
        """Render original image while preserving aspect ratio."""
        photo = self._build_contained_photo(
            self.original_image_path
        )
        if photo is None:
            self.original_photo = None
            self.original_label.config(
                image="",
                text="[ ORIGINAL PREVIEW FAILED ]",
                fg=TEXT_SECONDARY
            )
            return

        self.original_photo = photo
        self.original_label.config(image=self.original_photo, text="")

    def _render_compressed(self):
        """Render compressed image while preserving aspect ratio."""
        photo = self._build_contained_photo(
            self.compressed_image_path
        )
        if photo is None:
            self.compressed_photo = None
            self.compressed_label.config(
                image="",
                text="[ COMPRESSED PREVIEW ]",
                fg=TEXT_SECONDARY
            )
            return

        self.compressed_photo = photo
        self.compressed_label.config(image=self.compressed_photo, text="")

    def _build_contained_photo(self, image_path):
        """Build a centered, contained PhotoImage from the source file."""
        if not image_path:
            return None

        try:
            with Image.open(image_path) as image:
                image = image.copy()
        except OSError:
            return None

        image = ImageOps.contain(
            image,
            (PREVIEW_WIDTH, PREVIEW_HEIGHT),
            Image.Resampling.LANCZOS
        )

        preview_canvas = Image.new("RGBA", (PREVIEW_WIDTH, PREVIEW_HEIGHT), BG_ACCENT)
        offset_x = (PREVIEW_WIDTH - image.width) // 2
        offset_y = (PREVIEW_HEIGHT - image.height) // 2

        if image.mode == "RGBA":
            preview_canvas.paste(image, (offset_x, offset_y), image)
        else:
            preview_canvas.paste(image, (offset_x, offset_y))

        return ImageTk.PhotoImage(preview_canvas)

    def clear(self):
        """Clear preview placeholders."""
        self.original_image_path = None
        self.original_photo = None
        self.compressed_image_path = None
        self.compressed_photo = None
        self.original_label.config(image="", text="[ ORIGINAL PREVIEW ]")
        self.compressed_label.config(image="", text="[ COMPRESSED PREVIEW ]")
