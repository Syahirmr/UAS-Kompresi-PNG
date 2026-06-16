"""
Main GUI Application
PNG Compression Comparison System
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import threading
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
from src.analysis.analyzer import summarize_metrics
from src.processing.batch_processor import process_dataset
from src.utils.dataset_loader import scan_png_folder, validate_dataset


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
        self.file_labels = []
        self.current_file_index = 0
        self.cancel_requested = False
        self.worker_thread = None
        self.metrics_data = []

        # Wire GUI events
        self._bind_events()
    
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

    def _bind_events(self):
        """Bind GUI events for dataset loading and file navigation."""
        self.folder_picker.browse_btn.config(command=self._browse_dataset_folder)
        self.control_panel.compress_btn.config(command=self._start_compression)
        self.control_panel.cancel_btn.config(command=self._cancel_compression)
        self.file_selector.prev_btn.config(command=self._select_previous_file)
        self.file_selector.next_btn.config(command=self._select_next_file)
        self.file_selector.file_list.bind(
            "<<ComboboxSelected>>",
            self._select_file_from_dropdown
        )

    def _browse_dataset_folder(self):
        """Open a folder dialog and load PNG dataset files."""
        folder_path = filedialog.askdirectory(
            title="Pilih Folder Dataset PNG",
            mustexist=True
        )
        if not folder_path:
            return

        folder = Path(folder_path)
        if not folder.is_dir():
            message = "Folder tidak valid."
            self.folder_picker.set_validation_status(message, valid=False)
            messagebox.showerror("Folder Invalid", message)
            return

        self.folder_picker.set_selected_folder(folder)
        self.files_list = scan_png_folder(folder)
        self.file_labels = [
            str(file_path.relative_to(folder)) for file_path in self.files_list
        ]

        valid, message = validate_dataset(self.files_list)
        self.folder_picker.set_file_count(len(self.files_list))
        self.folder_picker.set_validation_status(message, valid=valid)
        self.file_selector.populate_files(self.file_labels)

        if self.files_list:
            self.current_file_index = 0
            self.preview.display_original(self.files_list[0])
        else:
            self.current_file_index = 0
            self.preview.clear()

        if not valid:
            messagebox.showwarning("Dataset Belum Valid", message)

    def _start_compression(self):
        """Start dataset compression in a background thread."""
        valid, message = validate_dataset(self.files_list)
        if not valid:
            self.control_panel.set_status(message)
            messagebox.showwarning("Dataset Belum Valid", message)
            return

        if self.is_compressing:
            return

        self.is_compressing = True
        self.cancel_requested = False
        self.control_panel.set_progress(0)
        self.control_panel.set_status("Memulai batch compression...")
        self.metrics_data = []
        self.metrics.reset()
        self.control_panel.disable_compress()
        self.control_panel.enable_cancel()
        self.control_panel.disable_export()

        self.worker_thread = threading.Thread(
            target=self._run_batch_compression,
            daemon=True
        )
        self.worker_thread.start()

    def _run_batch_compression(self):
        """Run batch compression outside the Tkinter main loop."""
        summary = process_dataset(
            files=self.files_list,
            algorithm="deflate",
            output_dir=Path("outputs") / "deflate",
            progress_callback=self._queue_progress_update,
            cancel_check=lambda: self.cancel_requested,
        )
        self.after(0, self._finish_compression, summary)

    def _queue_progress_update(self, progress_percent, status_text, metric=None):
        """Schedule progress updates on the Tkinter main loop."""
        self.after(
            0,
            lambda: self._apply_progress_update(progress_percent, status_text, metric)
        )

    def _apply_progress_update(self, progress_percent, status_text, metric=None):
        """Apply progress updates to GUI controls."""
        self.control_panel.set_progress(progress_percent)
        self.control_panel.set_status(status_text)
        if metric is not None:
            self.metrics_data.append(metric)
            self.metrics.add_metric(metric)
            self.metrics.set_summary(
                summarize_metrics(self.metrics_data, cancelled=self.cancel_requested)
            )

    def _cancel_compression(self):
        """Request graceful cancellation after the active file finishes."""
        if not self.is_compressing:
            return

        self.cancel_requested = True
        self.control_panel.disable_cancel()
        self.control_panel.set_status("Cancel diminta. File aktif akan diselesaikan dulu...")

    def _finish_compression(self, summary):
        """Restore GUI state after batch compression finishes."""
        self.is_compressing = False
        self.worker_thread = None
        self.control_panel.enable_compress()
        self.control_panel.disable_cancel()

        if summary["cancelled"]:
            self.metrics.set_summary(summary["summary"])
            self.control_panel.set_status(
                f"Partial completion: {summary['completed']} selesai, {summary['failed']} gagal."
            )
            return

        self.control_panel.set_progress(100)
        self.metrics.set_summary(summary["summary"])
        self.control_panel.set_status(
            f"Batch selesai: {summary['completed']} file diproses, {summary['failed']} gagal."
        )

    def _select_previous_file(self):
        """Select previous file in the dataset."""
        self._select_file_by_index(self.current_file_index - 1)

    def _select_next_file(self):
        """Select next file in the dataset."""
        self._select_file_by_index(self.current_file_index + 1)

    def _select_file_from_dropdown(self, event=None):
        """Select file from dropdown change."""
        self._select_file_by_index(self.file_selector.get_current_index())

    def _select_file_by_index(self, index):
        """Select file and update original preview."""
        if not self.files_list or index < 0 or index >= len(self.files_list):
            return

        self.current_file_index = index
        self.file_selector.select_index(index)
        self.preview.display_original(self.files_list[index])
    
    
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
