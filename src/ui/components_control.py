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
    """Control panel with algorithm selector cards, action controls, and real-time progress details."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        self.change_callback = None
        self.file_count = 0
        
        # State tracking for multi-select algorithms
        # Default: Deflate and OxiPNG selected
        self.selected_algos = {
            "deflate": True,
            "zopfli": False,
            "oxipng": True
        }
        
        # =====================================================================
        # SECTION 2: ALGORITHM SELECTION CARD
        # =====================================================================
        self.selection_card = ctk.CTkFrame(
            self, 
            fg_color=BG_ACCENT, 
            corner_radius=BORDER_RADIUS, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        self.selection_card.pack(fill="x", pady=(0, PADDING_NORMAL))
        
        self.selection_card.grid_columnconfigure(0, weight=3) # Cards column
        self.selection_card.grid_columnconfigure(1, weight=1) # Action column
        
        # Left container: Algorithm Cards
        left_container = ctk.CTkFrame(self.selection_card, fg_color="transparent")
        left_container.grid(row=0, column=0, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
        
        # Title row with badge
        title_row = ctk.CTkFrame(left_container, fg_color="transparent")
        title_row.pack(anchor="w", fill="x", pady=(0, 5))
        
        badge_label = ctk.CTkLabel(
            title_row,
            text="2",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] - 1, weight="bold"),
            text_color="#ffffff",
            fg_color=BUTTON_BG[1],
            width=24,
            height=24,
            corner_radius=12
        )
        badge_label.pack(side="left", padx=(0, 8))
        
        section_title = ctk.CTkLabel(
            title_row,
            text="Pilih Algoritma",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        section_title.pack(side="left")
        
        subtitle_lbl = ctk.CTkLabel(
            left_container,
            text="Pilih satu atau lebih algoritma untuk dibandingkan",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            text_color=TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w", pady=(0, 10))
        
        # Selectable Cards Row
        cards_row = ctk.CTkFrame(left_container, fg_color="transparent")
        cards_row.pack(fill="x", expand=True)
        cards_row.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.cards = {}
        self.card_badges = {}
        
        algo_details = [
            ("deflate", "Deflate (Baseline)", "Seimbang", "Algoritma standar dengan kompatibilitas terbaik.", ("#0078d4", "#1f77b4")),
            ("zopfli", "Zopfli Deflate", "Kompresi Terbaik", "Menghasilkan ukuran file paling kecil.", ("#107c10", "#2ea44f")),
            ("oxipng", "OxiPNG", "Paling Cepat", "Optimasi cepat dengan hasil yang sangat baik.", ("#8B5CF6", "#8B5CF6")),
        ]
        
        for idx, (key, label, badge_text, desc, badge_colors) in enumerate(algo_details):
            card = ctk.CTkFrame(
                cards_row,
                fg_color=("#F8FAFC", "#0B1220"),
                corner_radius=CONTROL_RADIUS,
                border_width=1,
                border_color=BORDER_COLOR
            )
            card.grid(row=0, column=idx, padx=4, pady=5, sticky="nsew")
            self.cards[key] = card
            
            # Click binding to toggle selection
            card.bind("<Button-1>", lambda event, k=key: self._toggle_algorithm(k))
            
            # Header inside card
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 2))
            header.bind("<Button-1>", lambda event, k=key: self._toggle_algorithm(k))
            
            # Text label
            lbl = ctk.CTkLabel(
                header,
                text=label,
                font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
                text_color=TEXT_PRIMARY
            )
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda event, k=key: self._toggle_algorithm(k))
            
            # Badge
            badge = ctk.CTkLabel(
                header,
                text=badge_text,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] - 2, weight="bold"),
                text_color="#ffffff",
                fg_color=badge_colors[1],
                corner_radius=4,
                padx=5,
                pady=1
            )
            badge.pack(side="right")
            badge.bind("<Button-1>", lambda event, k=key: self._toggle_algorithm(k))
            
            # Description
            desc_lbl = ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
                text_color=TEXT_SECONDARY,
                wraplength=200,
                justify="left"
            )
            desc_lbl.pack(anchor="w", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
            desc_lbl.bind("<Button-1>", lambda event, k=key: self._toggle_algorithm(k))
            
        # Right container: Start & Cancel buttons
        right_container = ctk.CTkFrame(self.selection_card, fg_color="transparent")
        right_container.grid(row=0, column=1, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
        right_container.grid_rowconfigure(0, weight=1)
        right_container.grid_columnconfigure(0, weight=1)
        
        action_box = ctk.CTkFrame(right_container, fg_color="transparent")
        action_box.grid(row=0, column=0)
        
        # Start button
        self.compress_btn = ctk.CTkButton(
            action_box,
            text="▶ Mulai Kompresi",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=48,
            width=180
        )
        self.compress_btn.pack(pady=(0, 5))
        
        # Subtext variable showing images selected
        self.btn_subtext_var = ctk.StringVar(value="Pilih folder untuk memulai")
        btn_sub_lbl = ctk.CTkLabel(
            action_box,
            textvariable=self.btn_subtext_var,
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            text_color=TEXT_SECONDARY
        )
        btn_sub_lbl.pack()
        
        # Cancel button (hidden by default)
        self.cancel_btn = ctk.CTkButton(
            action_box,
            text="⏹ Batal",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            fg_color=("#e81123", "#d11a2a"),
            text_color=BUTTON_FG,
            hover_color=("#ff3b30", "#e63946"),
            corner_radius=CONTROL_RADIUS,
            height=36,
            width=180
        )
        # We pack cancel button when compression begins
        
        # Redraw cards initial state
        self._update_cards_ui()

        # =====================================================================
        # SECTION 3: COMPRESSION PROGRESS CARD
        # =====================================================================
        self.progress_card = ctk.CTkFrame(
            self, 
            fg_color=BG_ACCENT, 
            corner_radius=BORDER_RADIUS, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        self.progress_card.pack(fill="x", pady=(0, PADDING_SMALL))
        
        # Title row with badge
        p_title_row = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        p_title_row.pack(anchor="w", fill="x", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        p_badge_label = ctk.CTkLabel(
            p_title_row,
            text="3",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] - 1, weight="bold"),
            text_color="#ffffff",
            fg_color=BUTTON_BG[1],
            width=24,
            height=24,
            corner_radius=12
        )
        p_badge_label.pack(side="left", padx=(0, 8))
        
        p_section_title = ctk.CTkLabel(
            p_title_row,
            text="Progress Kompresi",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        p_section_title.pack(side="left")
        
        # Progress bar container
        progress_bar_row = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        progress_bar_row.pack(fill="x", padx=PADDING_NORMAL, pady=5)
        
        # Current active task label
        self.active_task_var = ctk.StringVar(value="Menunggu proses kompresi dimulai...")
        self.active_task_lbl = ctk.CTkLabel(
            progress_bar_row,
            textvariable=self.active_task_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_PRIMARY,
            justify="left",
            anchor="w"
        )
        self.active_task_lbl.pack(side="left", fill="x", expand=True)
        
        # Progress percentage
        self.progress_pct_var = ctk.StringVar(value="0%")
        self.progress_pct_lbl = ctk.CTkLabel(
            progress_bar_row,
            textvariable=self.progress_pct_var,
            font=ctk.CTkFont(family=FONT_HEADING[0], size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
            width=45,
            anchor="e"
        )
        self.progress_pct_lbl.pack(side="right")
        
        # Progress bar itself
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_card,
            orientation="horizontal",
            progress_color=PROGRESS_COLOR,
            fg_color=("#E5E7EB", "#1F2937"),
            height=10,
            corner_radius=5
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        
        # Detailed stats grid
        self.details_grid = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        self.details_grid.pack(fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        self.details_grid.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # Define detailed metrics labels
        self.detail_vars = {
            "current_file": ctk.StringVar(value="-"),
            "current_algo": ctk.StringVar(value="-"),
            "status": ctk.StringVar(value="Idle"),
            "elapsed": ctk.StringVar(value="00:00:00"),
            "eta": ctk.StringVar(value="--"),
            "remaining": ctk.StringVar(value="-"),
        }
        
        details_labels = [
            ("File Aktif", "current_file", 0),
            ("Algoritma", "current_algo", 1),
            ("Status", "status", 2),
            ("Waktu Berjalan", "elapsed", 3),
            ("ETA", "eta", 4),
            ("Sisa Antrean", "remaining", 5),
        ]
        
        for name, var_key, col in details_labels:
            cell = ctk.CTkFrame(
                self.details_grid,
                fg_color=("#F8FAFC", "#0B1220"),
                corner_radius=6,
                border_width=1,
                border_color=BORDER_COLOR
            )
            cell.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")
            
            lbl_title = ctk.CTkLabel(
                cell,
                text=name,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] - 2),
                text_color=TEXT_SECONDARY
            )
            lbl_title.pack(pady=(4, 1))
            
            lbl_val = ctk.CTkLabel(
                cell,
                textvariable=self.detail_vars[var_key],
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
                text_color=TEXT_PRIMARY,
                wraplength=100
            )
            lbl_val.pack(pady=(0, 4))
            
        # Keep dummies for compatibility with app.py
        self.algorithm_var = ctk.StringVar(value="deflate")
        self.status_var = ctk.StringVar(value="Ready")
        self.comparison_btn = ctk.CTkButton(self, text="", width=0, height=0) # dummy
        self.export_btn = ctk.CTkButton(self, text="", width=0, height=0) # dummy

    def _toggle_algorithm(self, key):
        """Toggle active state of selected card."""
        if not self.compress_btn.cget("state") == "disabled" or self.cancel_btn.winfo_ismapped():
            # Disable selection during running
            if self.cancel_btn.winfo_ismapped():
                return
                
        self.selected_algos[key] = not self.selected_algos[key]
        self._update_cards_ui()
        self._notify_change()
        
    def _update_cards_ui(self):
        """Redraw border colors of cards based on their selection state."""
        for key, card in self.cards.items():
            if self.selected_algos[key]:
                card.configure(
                    border_color=BUTTON_BG[1],
                    border_width=2
                )
            else:
                card.configure(
                    border_color=BORDER_COLOR,
                    border_width=1
                )
                
    def _notify_change(self):
        """Trigger callbacks when algorithms or configuration changes."""
        if self.change_callback:
            # Pass first selected algo as string for backward compat
            algos = self.get_selected_algorithms()
            first_algo = algos[0] if algos else "deflate"
            self.change_callback(first_algo)

    def set_change_callback(self, callback):
        """Set callback for algorithm selection changes."""
        self.change_callback = callback
        
    def set_file_count(self, count):
        """Update file count and button subtexts."""
        self.file_count = count
        if count > 0:
            self.btn_subtext_var.set(f"Akan mengkompresi {count} gambar")
        else:
            self.btn_subtext_var.set("Pilih folder untuk memulai")
            
    def get_selected_algorithms(self):
        """Return list of selected algorithm keys."""
        return [key for key, val in self.selected_algos.items() if val]
        
    def get_algorithm(self):
        """Return primary selected algorithm (first in list) for compatibility."""
        algos = self.get_selected_algorithms()
        return algos[0] if algos else "deflate"
        
    def set_progress(self, value):
        """Update progress bar and status percentage (0 to 100)."""
        bounded_value = max(0, min(100, value))
        self.progress_bar.set(bounded_value / 100.0)
        self.progress_pct_var.set(f"{int(bounded_value)}%")
        
    def set_status(self, message):
        """Update active status messages and grid detail cells."""
        self.status_var.set(message)
        self.active_task_var.set(message)
        
        # Parse details if present in message format
        # Format typical: "[Algorithm 1/3] Deflate | File 4/10 (40%) | ETA: 02s"
        if "File " in message:
            parts = message.split("|")
            for p in parts:
                p = p.strip()
                if "Algorithm" in p or "Deflate" in p or "Zopfli" in p or "OxiPNG" in p:
                    algo_name = p.split("]")[-1].strip() if "]" in p else p
                    self.detail_vars["current_algo"].set(algo_name)
                    self.detail_vars["status"].set("Compressing")
                if "File" in p:
                    # extract filename if trailing, or count
                    f_info = p.split("(")[0].strip()
                    self.detail_vars["current_file"].set(f_info)
                    
                    # calculate remaining
                    try:
                        nums = f_info.replace("File", "").strip().split("/")
                        done, tot = int(nums[0]), int(nums[1])
                        self.detail_vars["remaining"].set(str(tot - done))
                    except Exception:
                        pass
                if "ETA" in p:
                    eta_val = p.replace("ETA:", "").strip()
                    self.detail_vars["eta"].set(eta_val)
                    
    def set_realtime_metrics(self, file_name, algo, elapsed_str, eta_str, remaining_count):
        """Explicitly update real-time progress grid fields."""
        if file_name: self.detail_vars["current_file"].set(file_name)
        if algo: self.detail_vars["current_algo"].set(algo)
        self.detail_vars["elapsed"].set(elapsed_str)
        self.detail_vars["eta"].set(eta_str)
        self.detail_vars["remaining"].set(str(remaining_count))
        self.detail_vars["status"].set("Active" if remaining_count > 0 else "Finished")
        
    def reset_progress(self):
        """Reset progress states."""
        self.set_progress(0)
        self.detail_vars["current_file"].set("-")
        self.detail_vars["current_algo"].set("-")
        self.detail_vars["status"].set("Idle")
        self.detail_vars["elapsed"].set("00:00:00")
        self.detail_vars["eta"].set("--")
        self.detail_vars["remaining"].set("-")
        self.active_task_var.set("Menunggu proses kompresi dimulai...")

    def enable_algorithm_selector(self):
        """Enable card select clicks."""
        # Selection is allowed
        pass

    def disable_algorithm_selector(self):
        """Disable selection inputs."""
        # Blocks click action transitions
        pass

    def enable_compress(self):
        """Enable compress action."""
        self.compress_btn.configure(state="normal")
        
    def disable_compress(self):
        """Disable compress action."""
        self.compress_btn.configure(state="disabled")

    def enable_cancel(self):
        """Enable cancellation action & show button."""
        self.compress_btn.pack_forget()
        self.cancel_btn.pack(pady=(0, 5))
        self.cancel_btn.configure(state="normal")
        
    def disable_cancel(self):
        """Disable cancellation action & hide button."""
        self.cancel_btn.pack_forget()
        self.compress_btn.pack(pady=(0, 5))
        self.cancel_btn.configure(state="disabled")

    # Dummies to avoid crashing legacy callbacks
    def enable_comparison(self): pass
    def disable_comparison(self): pass
    def enable_export(self): pass
    def disable_export(self): pass
    def _on_algorithm_change(self, value=None): pass
