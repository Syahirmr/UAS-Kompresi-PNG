"""
Folder Picker Component
For selecting dataset directory
"""

import customtkinter as ctk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_SMALL, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    SUCCESS_COLOR, ERROR_COLOR, PADDING_NORMAL, PADDING_SMALL,
    BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR
)


class FolderPickerComponent(ctk.CTkFrame):
    """Folder picker and dataset validation panel styled as a modern card."""
    
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
        
        # Grid layout to place Picker on the left, Stats on the right
        self.grid_columnconfigure(0, weight=3) # Picker controls
        self.grid_columnconfigure(1, weight=4) # Stats panel
        
        # LEFT AREA: Folder Picker Controls
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
        
        # Title row with badge
        title_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_row.pack(anchor="w", fill="x", pady=(0, 5))
        
        # Badge Label (Circle "1")
        badge_label = ctk.CTkLabel(
            title_row,
            text="1",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] - 1, weight="bold"),
            text_color="#ffffff",
            fg_color=BUTTON_BG[1],
            width=24,
            height=24,
            corner_radius=12
        )
        badge_label.pack(side="left", padx=(0, 8))
        
        # Section Title
        folder_title = ctk.CTkLabel(
            title_row,
            text="Pilih Folder Gambar",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        folder_title.pack(side="left")
        
        # Subtitle description
        folder_sub = ctk.CTkLabel(
            left_frame,
            text="Pilih folder yang berisi gambar PNG untuk dikompresi (min. 10 file)",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            text_color=TEXT_SECONDARY
        )
        folder_sub.pack(anchor="w", pady=(0, 10))
        
        # Input Controls Row
        input_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        input_row.pack(anchor="w", fill="x")
        
        # Browse Button
        self.browse_btn = ctk.CTkButton(
            input_row,
            text="📁 Pilih Folder",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=36,
            width=130
        )
        self.browse_btn.pack(side="left", padx=(0, PADDING_NORMAL))
        
        # Folder path display text box
        self.selected_folder = ctk.StringVar(value="Belum memilih folder")
        self.path_entry = ctk.CTkEntry(
            input_row,
            textvariable=self.selected_folder,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1] - 1),
            text_color=TEXT_PRIMARY,
            fg_color=("#F1F5F9", "#0B1220"),
            border_color=BORDER_COLOR,
            corner_radius=CONTROL_RADIUS,
            height=36,
            state="readonly"
        )
        self.path_entry.pack(side="left", fill="x", expand=True)

        # Validation status label below path display
        self.validation_status = ctk.StringVar(value="Dataset belum dipilih")
        self.status_label = ctk.CTkLabel(
            left_frame,
            textvariable=self.validation_status,
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
            text_color=ERROR_COLOR,
            justify="left"
        )
        self.status_label.pack(anchor="w", pady=(5, 0))

        # RIGHT AREA: Dashboard Statistics Grid
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
        right_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        
        # Stats variables
        self.total_images_var = ctk.StringVar(value="-")
        self.total_size_var = ctk.StringVar(value="-")
        self.format_var = ctk.StringVar(value="-")
        self.avg_resolution_var = ctk.StringVar(value="-")
        
        # Cards definitions
        stats_configs = [
            ("Total Gambar", self.total_images_var, 0),
            ("Total Ukuran", self.total_size_var, 1),
            ("Format", self.format_var, 2),
            ("Resolusi Rata-rata", self.avg_resolution_var, 3),
        ]
        
        self.stat_cards = []
        for label_text, var, col in stats_configs:
            card = ctk.CTkFrame(
                right_frame, 
                fg_color=("#F8FAFC", "#0B1220"), 
                corner_radius=CONTROL_RADIUS, 
                border_width=1, 
                border_color=BORDER_COLOR
            )
            card.grid(row=0, column=col, padx=4, pady=5, sticky="nsew")
            self.stat_cards.append(card)
            
            # Value display (Large)
            val_lbl = ctk.CTkLabel(
                card,
                textvariable=var,
                font=ctk.CTkFont(family=FONT_HEADING[0], size=16, weight="bold"),
                text_color=TEXT_PRIMARY
            )
            val_lbl.pack(pady=(PADDING_NORMAL, 2), expand=True)
            
            # Label display (Small description)
            title_lbl = ctk.CTkLabel(
                card,
                text=label_text,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] - 1),
                text_color=TEXT_SECONDARY
            )
            title_lbl.pack(pady=(0, PADDING_NORMAL), expand=True)
            
    def get_selected_folder(self):
        """Return selected folder path."""
        return self.selected_folder.get()
    
    def set_file_count(self, count):
        """Update file count display."""
        self.total_images_var.set(str(count))

    def set_selected_folder(self, folder_path):
        """Update selected folder display."""
        self.selected_folder.set(str(folder_path))

    def set_validation_status(self, message, valid=False):
        """Update dataset validation status."""
        self.validation_status.set(message)
        self.status_label.configure(text_color=SUCCESS_COLOR if valid else ERROR_COLOR)
        
    def set_dataset_stats(self, count, total_size, format_str, avg_resolution):
        """Set all stats variables at once."""
        self.total_images_var.set(str(count) if count > 0 else "-")
        self.total_size_var.set(total_size)
        self.format_var.set(format_str)
        self.avg_resolution_var.set(avg_resolution)
