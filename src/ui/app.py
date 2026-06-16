"""
Main GUI Application
PNG Compression Comparison System
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import (
    WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    WINDOW_GEOMETRY, BG_PRIMARY, BG_SECONDARY
)
from src.ui.components_header import HeaderComponent
from src.ui.components_folder_picker import FolderPickerComponent
from src.ui.components_control import ControlPanelComponent
from src.ui.components_preview import PreviewComponent
from src.ui.components_file_selector import FileSelectorComponent
from src.ui.components_metrics import MetricsPanelComponent


class CompressionApp(tk.Tk):
    """Main GUI Application for PNG Compression Comparison System."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Configure style
        self._configure_styles()
        
        # Configure background
        self.configure(bg=BG_PRIMARY)
        
        # Build GUI
        self._build_gui()
        
        # State tracking
        self.is_compressing = False
        self.files_list = []
        self.current_file_index = 0
    
    def _configure_styles(self):
        """Configure custom Tkinter styles."""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Configure custom frames
        style.configure('Header.TFrame', background=BG_SECONDARY)
        style.configure('TLabelframe', background=BG_PRIMARY, foreground="#333333")
        style.configure('TLabelframe.Label', background=BG_PRIMARY, foreground="#333333")
        style.configure('TFrame', background=BG_PRIMARY)
        style.configure('TLabel', background=BG_PRIMARY, foreground="#333333")
    
    def _build_gui(self):
        """Build the main GUI layout."""
        
        # Main container with scrolling
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling support
        canvas = tk.Canvas(
            main_frame,
            bg=BG_PRIMARY,
            highlightthickness=0
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame inside canvas for content
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # ============ LAYOUT STRUCTURE ============
        
        # 1. Header
        header = HeaderComponent(content_frame)
        
        # 2. Folder Picker
        self.folder_picker = FolderPickerComponent(content_frame)
        
        # 3. Control Panel
        self.control_panel = ControlPanelComponent(content_frame)
        
        # 4. Main Content Frame (split into left and right)
        main_content = ttk.Frame(content_frame)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left side - Preview & Metrics (stacked)
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Preview
        self.preview = PreviewComponent(left_frame)
        
        # Metrics table
        self.metrics = MetricsPanelComponent(left_frame)
        
        # Right side - File Selector
        right_frame = ttk.Frame(main_content)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))
        
        # File Selector
        self.file_selector = FileSelectorComponent(right_frame)
        
        # Update scroll region
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Scrolling and resize behavior may be added in future milestones
    
    
    def get_folder_picker(self):
        """Get folder picker component."""
        return self.folder_picker
    
    def get_control_panel(self):
        """Get control panel component."""
        return self.control_panel
    
    def get_preview(self):
        """Get preview component."""
        return self.preview
    
    def get_metrics(self):
        """Get metrics component."""
        return self.metrics
    
    def get_file_selector(self):
        """Get file selector component."""
        return self.file_selector
    
    def run(self):
        """Start the application."""
        self.mainloop()


def main():
    """Main entry point."""
    app = CompressionApp()
    app.run()


if __name__ == "__main__":
    main()
