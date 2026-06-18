"""
Preview Component
Side-by-side image preview display
"""

import customtkinter as ctk
from PIL import Image, ImageOps
from src.utils.config import (
    FONT_NORMAL, BG_ACCENT, BG_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, PADDING_NORMAL,
    PADDING_SMALL, PREVIEW_WIDTH, PREVIEW_HEIGHT
)


class PreviewComponent(ctk.CTkFrame):
    """Side-by-side preview of original and compressed images styled as modern cards."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.original_image_path = None
        self.original_ctk_image = None
        self.compressed_image_path = None
        self.compressed_ctk_image = None
        
        # Grid layout for side-by-side panels
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Original Image Card
        self.original_card = ctk.CTkFrame(
            self,
            fg_color=BG_ACCENT,
            corner_radius=8,
            border_width=1,
            border_color=("#dddddd", "#3f3f3f")
        )
        self.original_card.grid(row=0, column=0, padx=(0, PADDING_NORMAL), sticky="nsew")
        
        original_title = ctk.CTkLabel(
            self.original_card,
            text="Original Image",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        original_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        # Preview Frame (Canvas area)
        self.original_preview_frame = ctk.CTkFrame(
            self.original_card,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            fg_color=BG_PRIMARY,
            corner_radius=6
        )
        self.original_preview_frame.pack(anchor="center", expand=True, fill="both", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        self.original_preview_frame.pack_propagate(False)
        
        # Label displaying image/text
        self.original_label = ctk.CTkLabel(
            self.original_preview_frame,
            text="[ ORIGINAL PREVIEW ]",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY
        )
        self.original_label.pack(fill="both", expand=True)
        
        # Compressed Image Card
        self.compressed_card = ctk.CTkFrame(
            self,
            fg_color=BG_ACCENT,
            corner_radius=8,
            border_width=1,
            border_color=("#dddddd", "#3f3f3f")
        )
        self.compressed_card.grid(row=0, column=1, padx=(PADDING_NORMAL, 0), sticky="nsew")
        
        compressed_title = ctk.CTkLabel(
            self.compressed_card,
            text="Compressed Image",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        compressed_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        self.compressed_preview_frame = ctk.CTkFrame(
            self.compressed_card,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            fg_color=BG_PRIMARY,
            corner_radius=6
        )
        self.compressed_preview_frame.pack(anchor="center", expand=True, fill="both", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        self.compressed_preview_frame.pack_propagate(False)
        
        self.compressed_label = ctk.CTkLabel(
            self.compressed_preview_frame,
            text="[ COMPRESSED PREVIEW ]",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY
        )
        self.compressed_label.pack(fill="both", expand=True)
        
    def display_images(self, original_path, compressed_path):
        """Display original and compressed images when available."""
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
        ctk_img = self._build_contained_ctk_image(self.original_image_path)
        if ctk_img is None:
            self.original_ctk_image = None
            self.original_label.configure(
                image=None,
                text="[ ORIGINAL PREVIEW FAILED ]",
                text_color=TEXT_SECONDARY
            )
            return

        self.original_ctk_image = ctk_img
        self.original_label.configure(image=self.original_ctk_image, text="")

    def _render_compressed(self):
        """Render compressed image while preserving aspect ratio."""
        ctk_img = self._build_contained_ctk_image(self.compressed_image_path)
        if ctk_img is None:
            self.compressed_ctk_image = None
            self.compressed_label.configure(
                image=None,
                text="[ COMPRESSED PREVIEW ]",
                text_color=TEXT_SECONDARY
            )
            return

        self.compressed_ctk_image = ctk_img
        self.compressed_label.configure(image=self.compressed_ctk_image, text="")

    def _build_contained_ctk_image(self, image_path):
        """Build a centered, contained CTKImage from the source file."""
        if not image_path:
            return None

        try:
            with Image.open(image_path) as image:
                image = image.copy()
        except OSError:
            return None

        # Aspect ratio fitting
        contained = ImageOps.contain(
            image,
            (PREVIEW_WIDTH, PREVIEW_HEIGHT),
            Image.Resampling.LANCZOS
        )

        return ctk.CTkImage(
            light_image=contained,
            dark_image=contained,
            size=(contained.width, contained.height)
        )

    def clear(self):
        """Clear preview placeholders."""
        self.original_image_path = None
        self.original_ctk_image = None
        self.compressed_image_path = None
        self.compressed_ctk_image = None
        self.original_label.configure(image=None, text="[ ORIGINAL PREVIEW ]")
        self.compressed_label.configure(image=None, text="[ COMPRESSED PREVIEW ]")
