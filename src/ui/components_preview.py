"""
Preview Component
Dynamic multi-card image preview display with zoom controls
"""

import customtkinter as ctk
from PIL import Image, ImageOps
from pathlib import Path
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_SMALL, BG_ACCENT, BG_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, PADDING_NORMAL,
    PADDING_SMALL, PREVIEW_WIDTH, PREVIEW_HEIGHT,
    BUTTON_BG, BUTTON_HOVER, BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR,
    SUCCESS_COLOR
)


class PreviewComponent(ctk.CTkFrame):
    """Dynamic comparison preview panel supporting Grid/Side-by-side views and zoom."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.original_image_path = None
        self.algo_paths = {}
        self.selected_algos = ["deflate", "oxipng"] # Default selection
        self.winners = None
        self.completed_algos = set()
        
        # State indicators
        self.sync_zoom = True
        
        # =====================================================================
        # TOP CONTROLS BAR
        # =====================================================================
        control_bar = ctk.CTkFrame(self, fg_color=BG_ACCENT, corner_radius=BORDER_RADIUS, border_width=1, border_color=BORDER_COLOR)
        control_bar.pack(fill="x", pady=(0, PADDING_NORMAL))
        
        # Left Section: Title & Subtitle
        title_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        title_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_row.pack(anchor="w")
        
        badge_label = ctk.CTkLabel(
            title_row,
            text="4",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] - 1, weight="bold"),
            text_color="#ffffff",
            fg_color=BUTTON_BG[1],
            width=24,
            height=24,
            corner_radius=12
        )
        badge_label.pack(side="left", padx=(0, 8))
        
        title_lbl = ctk.CTkLabel(
            title_row,
            text="Perbandingan Hasil",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_lbl.pack(side="left")
        
        sub_lbl = ctk.CTkLabel(
            title_frame,
            text="Klik gambar untuk melihat detail",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            text_color=TEXT_SECONDARY
        )
        sub_lbl.pack(anchor="w")
        
        # Right Section: Layout, Zoom, and Sync controls
        controls_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        # View Mode segment buttons
        self.view_mode_var = ctk.StringVar(value="side")
        self.layout_segment = ctk.CTkSegmentedButton(
            controls_frame,
            values=["Side-by-Side View", "Grid View"],
            command=self._on_layout_segment_change,
            fg_color=BG_PRIMARY,
            selected_color=BUTTON_BG,
            selected_hover_color=BUTTON_HOVER,
            text_color=TEXT_PRIMARY,
            height=30,
            corner_radius=CONTROL_RADIUS
        )
        self.layout_segment.set("Side-by-Side View")
        self.layout_segment.pack(side="left", padx=(0, 20))
        
        # Zoom controls
        zoom_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        zoom_frame.pack(side="left", padx=(0, 20))
        
        self.zoom_lbl = ctk.CTkLabel(
            zoom_frame,
            text="Zoom: 100%",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.zoom_lbl.pack(side="left", padx=(0, 5))
        
        self.zoom_slider = ctk.CTkSlider(
            zoom_frame,
            from_=50,
            to=300,
            number_of_steps=10,
            command=self._on_zoom_slider_change,
            height=16,
            width=120
        )
        self.zoom_slider.set(100)
        self.zoom_slider.pack(side="left")
        
        # Sync zoom toggle
        self.sync_zoom_switch = ctk.CTkSwitch(
            controls_frame,
            text="Sinkronkan Zoom",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            command=self._on_sync_zoom_toggle,
            progress_color=BUTTON_BG[1]
        )
        self.sync_zoom_switch.select() # default synced
        self.sync_zoom_switch.pack(side="left")
        
        # =====================================================================
        # MAIN CARDS CONTAINER
        # =====================================================================
        self.cards_container = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True)
        
        # Initialise All 4 Cards: Original, Deflate, Zopfli, OxiPNG
        # 1. Original Card
        self.original_card = self._build_image_card("Original", "Original", None)
        
        # 2. Deflate Card
        self.deflate_card = self._build_image_card("Deflate (Baseline)", "deflate", ("#0078d4", "#1f77b4"))
        
        # 3. Zopfli Card
        self.zopfli_card = self._build_image_card("Zopfli Deflate", "zopfli", ("#107c10", "#2ea44f"))
        
        # 4. OxiPNG Card
        self.oxipng_card = self._build_image_card("OxiPNG", "oxipng", ("#8B5CF6", "#8B5CF6"))
        
        self.algo_cards = {
            "deflate": self.deflate_card,
            "zopfli": self.zopfli_card,
            "oxipng": self.oxipng_card
        }
        
        self.all_cards = {
            "original": self.original_card,
            "deflate": self.deflate_card,
            "zopfli": self.zopfli_card,
            "oxipng": self.oxipng_card
        }
        
        # Render initial empty state
        self._arrange_cards()

    def _build_image_card(self, title, key, accent_color):
        """Construct a standardized image card frame with header details & preview canvas."""
        card = ctk.CTkFrame(
            self.cards_container,
            fg_color=BG_ACCENT,
            corner_radius=BORDER_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        
        # Header area
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        # Title Label
        t_lbl = ctk.CTkLabel(
            hdr,
            text=title,
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=accent_color if accent_color else TEXT_PRIMARY
        )
        t_lbl.pack(side="left")
        
        # Badge Label on Top Left for Winners
        card.winner_badge = ctk.CTkLabel(
            hdr,
            text="",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] - 2, weight="bold"),
            text_color="#ffffff",
            fg_color="transparent",
            corner_radius=4,
            padx=5,
            pady=1
        )
        # We pack winner badge dynamically
        
        # Size Label on Top Right
        card.size_var = ctk.StringVar(value="-")
        size_lbl = ctk.CTkLabel(
            hdr,
            textvariable=card.size_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1] - 1),
            text_color=TEXT_PRIMARY
        )
        size_lbl.pack(side="right")
        
        # Preview Canvas Container
        canvas_frame = ctk.CTkFrame(
            card,
            fg_color=BG_PRIMARY,
            corner_radius=CONTROL_RADIUS,
            height=PREVIEW_HEIGHT
        )
        canvas_frame.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=(0, 5))
        canvas_frame.pack_propagate(False)
        
        # Image Label
        card.img_label = ctk.CTkLabel(
            canvas_frame,
            text="[ PREVIEW ]" if key != "Original" else "[ ORIGINAL PREVIEW ]",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY
        )
        card.img_label.pack(fill="both", expand=True)
        
        # Footer Row (Metrics details)
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        if key == "Original":
            # Original footer displays resolution only
            card.res_var = ctk.StringVar(value="-")
            lbl_res = ctk.CTkLabel(
                footer,
                textvariable=card.res_var,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
                text_color=TEXT_SECONDARY
            )
            lbl_res.pack(side="left")
        else:
            # Result footers display reduction % and time elapsed
            card.reduction_var = ctk.StringVar(value="-")
            card.time_var = ctk.StringVar(value="-")
            
            lbl_red = ctk.CTkLabel(
                footer,
                textvariable=card.reduction_var,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
                text_color=SUCCESS_COLOR
            )
            lbl_red.pack(side="left")
            
            lbl_time = ctk.CTkLabel(
                footer,
                textvariable=card.time_var,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
                text_color=TEXT_SECONDARY
            )
            lbl_time.pack(side="right")
            
        return card

    def _on_layout_segment_change(self, value):
        """Update view layout formatting."""
        mode = "grid" if value == "Grid View" else "side"
        self.view_mode_var.set(mode)
        self._arrange_cards()
        self._render_all_images()
        
    def _on_zoom_slider_change(self, value):
        """Update scale factor labels and apply zoom scale."""
        self.zoom_lbl.configure(text=f"Zoom: {int(value)}%")
        self._render_all_images()
        
    def _on_sync_zoom_toggle(self):
        """Toggle sync zoom parameter."""
        self.sync_zoom = self.sync_zoom_switch.get()
        
    def _arrange_cards(self):
        """Dynamically place visible algorithm cards in grid rows."""
        # Unpack everything
        for card in self.all_cards.values():
            card.grid_forget()
            card.pack_forget()
            
        visible_keys = ["original"]
        for key in ["deflate", "zopfli", "oxipng"]:
            if key in self.selected_algos:
                visible_keys.append(key)
                
        view_mode = self.view_mode_var.get()
        num_cards = len(visible_keys)
        
        # Grid settings reset
        for i in range(4):
            self.cards_container.grid_columnconfigure(i, weight=0)
            self.cards_container.grid_rowconfigure(i, weight=0)
            
        if view_mode == "grid" and num_cards > 2:
            # 2x2 grid layout
            for idx, key in enumerate(visible_keys):
                row = idx // 2
                col = idx % 2
                self.all_cards[key].grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
                self.cards_container.grid_columnconfigure(col, weight=1)
                self.cards_container.grid_rowconfigure(row, weight=1)
        else:
            # Side-by-side single row layout
            for idx, key in enumerate(visible_keys):
                self.all_cards[key].grid(row=0, column=idx, padx=6, pady=6, sticky="nsew")
                self.cards_container.grid_columnconfigure(idx, weight=1)
            self.cards_container.grid_rowconfigure(0, weight=1)

    def display_all_images(self, original_path, compressed_outputs, selected_algos, winners=None, completed_algorithms=None):
        """Set preview files paths & labels details, then render."""
        self.original_image_path = original_path
        self.selected_algos = selected_algos
        self.winners = winners
        if completed_algorithms is not None:
            self.completed_algos = completed_algorithms
        else:
            self.completed_algos = set(compressed_outputs.keys())
        
        # Map algorithm paths
        self.algo_paths = {}
        for algo in ["deflate", "zopfli", "oxipng"]:
            if algo in compressed_outputs and algo in self.completed_algos:
                self.algo_paths[algo] = compressed_outputs[algo]
                
        # Re-arrange dynamic grid columns
        self._arrange_cards()
        
        # Update text labels
        # 1. Original stats
        if original_path:
            p = Path(original_path)
            if p.is_file():
                sz = p.stat().st_size
                self.original_card.size_var.set(self._format_bytes(sz))
                try:
                    with Image.open(p) as img:
                        self.original_card.res_var.set(f"{img.width}x{img.height}")
                except Exception:
                    self.original_card.res_var.set("-")
        else:
            self.original_card.size_var.set("-")
            self.original_card.res_var.set("-")
            
        # 2. Algorithms stats & badges
        for algo in ["deflate", "zopfli", "oxipng"]:
            card = self.algo_cards[algo]
            card.winner_badge.pack_forget()
            
            path = self.algo_paths.get(algo)
            if path and Path(path).is_file():
                # size
                sz = Path(path).stat().st_size
                card.size_var.set(self._format_bytes(sz))
                
                # Calculate reduction percent
                orig_sz = Path(original_path).stat().st_size if original_path else 0
                if orig_sz > 0:
                    pct = ((orig_sz - sz) / orig_sz) * 100
                    card.reduction_var.set(f"{pct:.1f}% lebih kecil")
                else:
                    card.reduction_var.set("-")
                    
                # Time is updated from the results object asynchronously by the app
                # Here we default/read winners badges
                if winners:
                    best_algo = winners.get("winner_reduction_algorithm")
                    fast_algo = winners.get("winner_speed_algorithm")
                    
                    if algo == best_algo:
                        card.winner_badge.configure(text="TERBAIK", fg_color="#107c10")
                        card.winner_badge.pack(side="left", padx=5)
                    elif algo == fast_algo:
                        card.winner_badge.configure(text="TERCEPAT", fg_color="#6b3fa0")
                        card.winner_badge.pack(side="left", padx=5)
            else:
                card.size_var.set("-")
                card.reduction_var.set("-")
                card.time_var.set("-")
                
        self._render_all_images()
        
    def set_algorithm_time(self, algo, time_ms):
        """Set processing time elapsed for a card."""
        if algo in self.algo_cards:
            self.algo_cards[algo].time_var.set(f"{time_ms:.2f} ms")

    def _render_all_images(self):
        """Render all visible images under the current scale factor."""
        zoom = self.zoom_slider.get() / 100.0 if self.sync_zoom else 1.0
        
        # Render original
        self._render_single_image(self.original_card, self.original_image_path, zoom)
        
        # Render algos
        for algo in ["deflate", "zopfli", "oxipng"]:
            if algo in self.selected_algos:
                path = self.algo_paths.get(algo)
                completed = algo in self.completed_algos
                self._render_single_image(self.algo_cards[algo], path, zoom, completed)

    def _render_single_image(self, card, path, zoom, completed=True):
        """Draw image on labels canvas scaled contained with zoom scale."""
        if not completed:
            placeholder_text = "No Result Available\n(Compression Not Executed Yet)"
            card.img_label.configure(image=None, text=placeholder_text)
            return
            
        if not path or not Path(path).is_file():
            card.img_label.configure(image=None, text="[ Belum Diproses ]" if path is None else "[ Gagal ]")
            return
            
        try:
            with Image.open(path) as img:
                img = img.copy()
        except Exception:
            card.img_label.configure(image=None, text="[ Error Load ]")
            return
            
        # Fit image contained
        display_w = int(320 * zoom)
        display_h = int(PREVIEW_HEIGHT * zoom)
        
        contained = ImageOps.contain(img, (display_w, display_h), Image.Resampling.LANCZOS)
        
        ctk_img = ctk.CTkImage(
            light_image=contained,
            dark_image=contained,
            size=(contained.width, contained.height)
        )
        
        card.img_label.configure(image=ctk_img, text="")
        card.img_label.image = ctk_img

    def display_images(self, original_path, compressed_path):
        """Legacy compatibility wrapper."""
        outputs = {}
        if compressed_path:
            # Guess algorithm
            algo = "deflate"
            if "zopfli" in str(compressed_path): algo = "zopfli"
            elif "oxipng" in str(compressed_path): algo = "oxipng"
            outputs[algo] = compressed_path
        self.display_all_images(original_path, outputs, self.selected_algos, self.winners)

    def clear(self):
        """Clear all active images."""
        self.original_image_path = None
        self.algo_paths = {}
        self.winners = None
        self.completed_algos = set()
        for key, card in self.all_cards.items():
            card.img_label.configure(image=None, text="[ PREVIEW ]" if key != "original" else "[ ORIGINAL PREVIEW ]")
            card.size_var.set("-")
            if hasattr(card, "res_var"): card.res_var.set("-")
            if hasattr(card, "reduction_var"): card.reduction_var.set("-")
            if hasattr(card, "time_var"): card.time_var.set("-")
            card.winner_badge.pack_forget()

    def _format_bytes(self, value):
        """Format size labels."""
        if value <= 0: return "-"
        if value < 1024 * 1024:
            return f"{value / 1024:.2f} KB"
        return f"{value / (1024*1024):.2f} MB"

    # Dummies for backward compatibility
    def show_algorithm_selector(self): pass
    def hide_algorithm_selector(self): pass
    def set_algorithm_change_callback(self, callback): pass
    def set_selected_algorithm_label(self, label): pass
