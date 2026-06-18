"""
Main GUI Application
PNG Compression Comparison System
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
import customtkinter as ctk

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
from src.compression.comparison_runner import run_comparison
from src.export.exporter import (
    export_metrics_csv,
    export_comparison_csv,
    generate_reduction_chart,
    generate_time_chart,
)
from src.processing.batch_processor import process_dataset
from src.utils.dataset_loader import scan_png_folder, validate_dataset
from src.utils.logger import Logger


ALGORITHM_OUTPUT_DIRS = {
    "deflate": Path("outputs") / "deflate",
    "zopfli": Path("outputs") / "zopfli",
    "oxipng": Path("outputs") / "oxipng",
}


class CompressionApp(ctk.CTk):
    """Main GUI Application for PNG Compression Comparison System."""

    def __init__(self):
        super().__init__()

        # Configure appearance and theme
        ctk.set_appearance_mode("Dark")  # Default to Dark Mode
        ctk.set_default_color_theme("blue")

        # Configure window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Configure background
        self.configure(fg_color=BG_PRIMARY)

        # State tracking
        self.is_compressing = False
        self.is_comparing = False
        self.files_list = []
        self.file_labels = []
        self.current_file_index = 0
        self.cancel_requested = False
        self.worker_thread = None
        self.metrics_data = []
        self.metrics_summary = summarize_metrics([])
        self.selected_algorithm = "deflate"

        # BUG-2 fix: store per-algorithm compressed outputs
        # Structure: {resolved_input_path: {algorithm_key: output_path}}
        self.compressed_outputs = {}

        self.comparison_results = None

        # Build GUI
        self._build_gui()

        # Wire GUI events
        self._bind_events()

        # Log startup
        self.logger = Logger()
        self.logger.app_start()

        # Handle window close gracefully
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _toggle_theme(self):
        """Toggle between Light and Dark appearance modes."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        # Notify components to update standard TK widgets (like Treeviews)
        self.metrics.update_theme_styles()

    def _build_gui(self):
        """Build the main GUI layout using CTKScrollableFrame."""
        # Main scrollable container
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_PRIMARY,
            corner_radius=0
        )
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # ============ LAYOUT STRUCTURE ============

        # 1. Header
        header = HeaderComponent(self.content_frame, toggle_theme_callback=self._toggle_theme)

        # 2. Folder Picker
        self.folder_picker = FolderPickerComponent(self.content_frame)

        # 3. Control Panel
        self.control_panel = ControlPanelComponent(self.content_frame)

        # 4. Main Content Frame (split into left and right)
        main_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left side - Preview & Metrics (stacked)
        left_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Preview
        self.preview = PreviewComponent(left_frame)

        # Metrics table
        self.metrics = MetricsPanelComponent(left_frame)

        # Right side - File Selector
        right_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))

        # File Selector
        self.file_selector = FileSelectorComponent(right_frame)

    def _bind_events(self):
        """Bind GUI events for dataset loading and file navigation."""
        self.folder_picker.browse_btn.configure(command=self._browse_dataset_folder)
        self.control_panel.compress_btn.configure(command=self._start_compression)
        self.control_panel.comparison_btn.configure(command=self._start_comparison)
        self.control_panel.cancel_btn.configure(command=self._cancel_compression)
        self.control_panel.export_btn.configure(command=self._export_results)
        self.file_selector.prev_btn.configure(command=self._select_previous_file)
        self.file_selector.next_btn.configure(command=self._select_next_file)
        self.file_selector.set_change_callback(self._select_file_from_dropdown)
        self.control_panel.set_change_callback(self._on_algorithm_selection_changed)
        self.preview.set_algorithm_change_callback(self._on_preview_algorithm_changed)

    def _on_algorithm_selection_changed(self, algorithm_key):
        """Handle algorithm selection change from control panel to update preview."""
        self.selected_algorithm = algorithm_key
        # Sync preview segmented button
        mapping = {
            "deflate": "Deflate Baseline",
            "zopfli": "Zopfli",
            "oxipng": "OxiPNG"
        }
        self.preview.set_selected_algorithm_label(mapping.get(algorithm_key, "Deflate Baseline"))
        self._update_preview_current_file()

    def _on_preview_algorithm_changed(self, algorithm_key):
        """Handle algorithm selection change from preview card to update control panel and preview."""
        self.selected_algorithm = algorithm_key
        # Sync control panel dropdown
        mapping = {
            "deflate": "Deflate Baseline",
            "zopfli": "Zopfli",
            "oxipng": "OxiPNG"
        }
        self.control_panel.algorithm_var.set(mapping.get(algorithm_key, "Deflate Baseline"))
        self.control_panel._on_algorithm_change() # Update warning label
        self._update_preview_current_file()

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

        self.control_panel.set_status("Memuat dataset...")
        self.folder_picker.set_selected_folder(folder)
        self.files_list = scan_png_folder(folder)

        valid, message = validate_dataset(self.files_list)
        self.logger.dataset_loaded(str(folder), len(self.files_list), valid)
        self.compressed_outputs = {}
        self.metrics_data = []
        self.metrics_summary = summarize_metrics([])
        self.control_panel.disable_export()
        self.file_labels = [
            str(file_path.relative_to(folder)) for file_path in self.files_list
        ]

        self.folder_picker.set_file_count(len(self.files_list))
        self.folder_picker.set_validation_status(message, valid=valid)
        self.file_selector.populate_files(self.file_labels)

        if self.files_list:
            self.current_file_index = 0
            self._update_preview_current_file()
        else:
            self.current_file_index = 0
            self.preview.clear()

        if not valid:
            messagebox.showwarning("Dataset Belum Valid", message)

    # ------------------------------------------------------------------
    # Comparison (M10 + M11 improvements)
    # ------------------------------------------------------------------

    def _start_comparison(self):
        """Start comparison (all 3 algorithms) in a background thread."""
        valid, message = validate_dataset(self.files_list)
        if not valid:
            self.control_panel.set_status(message)
            messagebox.showwarning("Dataset Belum Valid", message)
            return

        # BUG-3 fix: check both compressing and comparing
        if self.is_compressing or self.is_comparing:
            return

        # Show Zopfli warning for comparison too
        messagebox.showinfo(
            "Zopfli Warning",
            "Zopfli bisa sangat lambat untuk dataset besar (60s timeout per file).\n\n"
            "Comparison akan menjalankan semua 3 algoritma secara berurutan."
        )

        self.is_comparing = True
        self.cancel_requested = False
        self.control_panel.set_progress(0)
        self.control_panel.set_status("Memulai comparison (3 algoritma)...")
        self.metrics_data = []
        self.metrics_summary = summarize_metrics([])
        self.compressed_outputs = {}
        self.comparison_results = None
        self.metrics.reset()

        self.control_panel.disable_compress()
        self.control_panel.disable_comparison()
        self.control_panel.disable_algorithm_selector()
        self.control_panel.enable_cancel()
        self.control_panel.disable_export()
        self.folder_picker.browse_btn.configure(state="disabled")

        self.logger.compression_started("comparison", len(self.files_list) * 3)

        self.worker_thread = threading.Thread(
            target=self._run_comparison_background,
            daemon=True
        )
        self.worker_thread.start()

    def _run_comparison_background(self):
        """Run the 3-algorithm comparison outside the Tkinter main loop."""
        try:
            output_dir = Path("outputs") / "comparison"
            comparison_result = run_comparison(
                files=self.files_list,
                output_dir=output_dir,
                progress_callback=self._queue_comparison_progress,
                cancel_check=lambda: self.cancel_requested,
            )
        except Exception as exc:
            self.logger.log_exception(type(exc).__name__, str(exc))
            comparison_result = {
                "per_algorithm": {},
                "all_metrics": [],
                "summary": {"completed": 0, "failed": 0},
                "winners": {
                    "winner_reduction_algorithm": None,
                    "winner_reduction_label": "N/A",
                    "winner_reduction_value": 0,
                    "winner_speed_algorithm": None,
                    "winner_speed_label": "N/A",
                    "winner_speed_value": 0,
                    "winner_balanced_algorithm": None,
                    "winner_balanced_label": "N/A",
                    "winner_balanced_value": 0,
                },
                "cancelled": False,
                "total_time_seconds": 0,
            }
        self.after(0, self._finish_comparison, comparison_result)

    def _queue_comparison_progress(self, progress_percent, status_text, metric=None):
        """Schedule comparison progress updates on the Tkinter main loop."""
        self.after(
            0,
            lambda: self._apply_comparison_progress(progress_percent, status_text, metric)
        )

    def _apply_comparison_progress(self, progress_percent, status_text, metric=None):
        """Apply comparison progress updates to GUI controls."""
        self.control_panel.set_progress(progress_percent)
        self.control_panel.set_status(status_text)
        if metric is not None:
            self.metrics_data.append(metric)
            self.metrics.add_metric(metric)

    def _finish_comparison(self, comparison_result):
        """Restore GUI state and display comparison results."""
        self.is_comparing = False
        self.worker_thread = None
        self.comparison_results = comparison_result

        self.control_panel.enable_compress()
        self.control_panel.enable_comparison()
        self.control_panel.enable_algorithm_selector()
        self.control_panel.disable_cancel()
        self.folder_picker.browse_btn.configure(state="normal")

        winners = comparison_result["winners"]
        per_algorithm = comparison_result["per_algorithm"]
        cancelled = comparison_result["cancelled"]

        # BUG-2 fix: store per-algorithm outputs for preview
        self._register_comparison_outputs(per_algorithm)

        # Update metrics data and summary for the metrics table
        self.metrics_data = comparison_result["all_metrics"]
        completed_count = sum(
            data["summary"]["completed"] for data in per_algorithm.values()
        )
        failed_count = sum(
            data["summary"]["failed"] for data in per_algorithm.values()
        )
        summary = {
            "completed": completed_count,
            "failed": failed_count,
            "cancelled": cancelled,
            "avg_reduction": winners.get("winner_reduction_value", 0),
            "avg_time_ms": winners.get("winner_speed_value", 0),
        }
        self.metrics_summary = summary
        self.metrics.set_summary(summary)

        # Show comparison summary tab
        self.metrics.show_comparison(per_algorithm, winners)

        if cancelled:
            self.control_panel.set_status(
                f"Comparison dibatalkan. {completed_count} selesai, {failed_count} gagal."
            )
        else:
            # Export comparison CSV + charts automatically (BUG-1 fix: timestamped charts)
            self._export_comparison_results(per_algorithm, winners)

            wr_label = winners.get("winner_reduction_label", "N/A")
            ws_label = winners.get("winner_speed_label", "N/A")
            wb_label = winners.get("winner_balanced_label", "N/A")
            self.control_panel.set_status(
                f"Comparison selesai! Best: {wr_label} | Fastest: {ws_label} | Balanced: {wb_label}"
            )

        self.control_panel.set_progress(100)
        self.after_idle(self._update_preview_current_file)

    # BUG-2 fix: store per-algorithm outputs
    def _register_comparison_outputs(self, per_algorithm):
        """Register compressed outputs from all algorithms for preview.

        Stores outputs as {resolved_input_path: {algorithm: output_path}}
        so each algorithm's output can be viewed independently.
        """
        for algo_key, algo_data in per_algorithm.items():
            for result in algo_data.get("results", []):
                if not result.get("success"):
                    continue
                input_path = result.get("input_path")
                output_path = Path(result.get("output_path", ""))
                if input_path and output_path.is_file():
                    resolved = str(Path(input_path).resolve())
                    if resolved not in self.compressed_outputs:
                        self.compressed_outputs[resolved] = {}
                    self.compressed_outputs[resolved][algo_key] = output_path

    def _export_comparison_results(self, per_algorithm, winners):
        """Export comparison CSV and generate charts automatically."""
        output_dir = Path("outputs") / "reports"
        charts_dir = Path("outputs") / "charts"

        # Export CSV
        try:
            csv_path = export_comparison_csv(per_algorithm, winners, output_dir)
            self.logger.export_success(str(csv_path))
        except (OSError, KeyError) as exc:
            self.logger.export_failed(f"comparison CSV: {exc}")

        # BUG-1 fix: generate timestamped charts (no overwrite)
        try:
            reduction_path = generate_reduction_chart(per_algorithm, charts_dir)
            time_path = generate_time_chart(per_algorithm, charts_dir)
            self.logger.info("chart_generated", f"reduction={reduction_path} time={time_path}")
            self.metrics.show_chart(reduction_path, time_path)
        except Exception as exc:
            self.logger.log_exception("chart_error", str(exc))

    # ------------------------------------------------------------------
    # Single-algorithm compression
    # ------------------------------------------------------------------

    def _start_compression(self):
        """Start dataset compression in a background thread."""
        valid, message = validate_dataset(self.files_list)
        if not valid:
            self.control_panel.set_status(message)
            messagebox.showwarning("Dataset Belum Valid", message)
            return

        # BUG-3 fix: check both compressing and comparing
        if self.is_compressing or self.is_comparing:
            return

        self.is_compressing = True
        self.cancel_requested = False
        self.control_panel.set_progress(0)
        self.control_panel.set_status("Memulai batch compression...")
        self.metrics_data = []
        self.metrics_summary = summarize_metrics([])
        self.compressed_outputs = {}
        self.metrics.reset()
        algorithm = self.control_panel.get_algorithm()
        self.selected_algorithm = algorithm

        self.control_panel.disable_compress()
        self.control_panel.disable_comparison()
        self.control_panel.disable_algorithm_selector()
        self.control_panel.enable_cancel()
        self.control_panel.disable_export()
        self.folder_picker.browse_btn.configure(state="disabled")

        self.logger.compression_started(algorithm, len(self.files_list))

        self.worker_thread = threading.Thread(
            target=self._run_batch_compression,
            daemon=True
        )
        self.worker_thread.start()

    def _run_batch_compression(self):
        """Run batch compression outside the Tkinter main loop."""
        algorithm = self.selected_algorithm
        output_dir = ALGORITHM_OUTPUT_DIRS.get(
            algorithm, Path("outputs") / algorithm
        )
        try:
            summary = process_dataset(
                files=self.files_list,
                algorithm=algorithm,
                output_dir=output_dir,
                progress_callback=self._queue_progress_update,
                cancel_check=lambda: self.cancel_requested,
            )
        except Exception as exc:
            # Safety net: unhandled exception in worker thread
            self.logger.log_exception(type(exc).__name__, str(exc))
            summary = {
                "completed": 0,
                "failed": len(self.files_list),
                "cancelled": False,
                "results": [],
                "metrics": [],
                "summary": {
                    "completed": 0,
                    "failed": len(self.files_list),
                    "cancelled": False,
                    "avg_reduction": 0,
                    "avg_time_ms": 0,
                },
            }
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
        if not self.is_compressing and not self.is_comparing:
            return

        self.cancel_requested = True
        self.control_panel.disable_cancel()
        self.control_panel.set_status("Cancel diminta. File aktif akan diselesaikan dulu...")

    def _finish_compression(self, summary):
        """Restore GUI state after batch compression finishes."""
        self.is_compressing = False
        self.worker_thread = None
        algorithm = self.selected_algorithm
        self.control_panel.enable_compress()
        self.control_panel.enable_comparison()
        self.control_panel.enable_algorithm_selector()
        self.control_panel.disable_cancel()
        self.folder_picker.browse_btn.configure(state="normal")
        self._register_compressed_outputs(summary["results"], algorithm)
        self.metrics_summary = summary["summary"]

        if summary["cancelled"]:
            self.logger.compression_cancelled(
                summary["completed"], summary["failed"]
            )
            self.metrics.set_summary(summary["summary"])
            self.after_idle(self._update_preview_current_file)
            self._enable_export_if_ready()
            self.control_panel.set_status(
                f"Partial completion: {summary['completed']} selesai, {summary['failed']} gagal."
            )
            return

        self.logger.compression_finished(
            summary["completed"], summary["failed"],
            summary["summary"]["avg_reduction"],
            summary["summary"]["avg_time_ms"],
        )
        self.logger.write_session_log(
            dataset_path=str(self.folder_picker.get_selected_folder() or ""),
            algorithm=algorithm,
            completed=summary["completed"],
            failed=summary["failed"],
            avg_reduction=summary["summary"]["avg_reduction"],
            avg_time_ms=summary["summary"]["avg_time_ms"],
        )

        self.control_panel.set_progress(100)
        self.metrics.set_summary(summary["summary"])
        self.after_idle(self._update_preview_current_file)
        self._enable_export_if_ready()
        success_count = summary['completed'] - summary['failed']
        self.control_panel.set_status(
            f"Compression selesai ({success_count} success, {summary['failed']} failed)"
        )

    def _enable_export_if_ready(self):
        """Enable export when batch has produced at least one metrics row."""
        if self.metrics_data:
            self.control_panel.enable_export()

    def _export_results(self):
        """Export latest metrics to a timestamped CSV report."""
        if not self.metrics_data:
            self.after(0, lambda: self.control_panel.set_status(
                "Export gagal: belum ada metrics untuk diekspor."
            ))
            return

        try:
            output_path = export_metrics_csv(
                metrics=self.metrics_data,
                summary=self.metrics_summary,
                output_dir=Path("outputs") / "reports",
            )
        except (OSError, KeyError) as exc:
            self.logger.export_failed(str(exc))
            self.logger.log_exception(type(exc).__name__, str(exc))
            self.after(0, lambda: self.control_panel.set_status(
                f"Export gagal: {exc}"
            ))
            return

        self.logger.export_success(str(output_path))
        self.after(0, lambda path=output_path: self.control_panel.set_status(
            f"Export berhasil: {path}"
        ))

    # ------------------------------------------------------------------
    # File navigation & preview
    # ------------------------------------------------------------------

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
        self._update_preview_current_file()

    def _update_preview_current_file(self):
        """Update original and compressed preview for the selected file."""
        if not self.files_list:
            self.preview.clear()
            return

        original_path = self.files_list[self.current_file_index]
        compressed_path = self._get_compressed_output_path(original_path)
        self.preview.display_images(original_path, compressed_path)

    def _get_compressed_output_path(self, original_path):
        """Return the best available compressed output path for a file.

        After single-algorithm compression: returns the stored output.
        After comparison: returns the output of the selected algorithm,
        falling back to the best-reduction algorithm's output.
        """
        resolved = str(Path(original_path).resolve())
        outputs = self.compressed_outputs.get(resolved)

        if not outputs:
            return None

        # outputs is a dict: {algorithm_key: Path}
        # Try the currently selected algorithm first
        if self.selected_algorithm in outputs:
            path = outputs[self.selected_algorithm]
            if path.is_file():
                return path

        # Fall back to the best (smallest) file
        best_path = None
        for algo, path in outputs.items():
            if path.is_file():
                if best_path is None:
                    best_path = path
                else:
                    try:
                        if path.stat().st_size < best_path.stat().st_size:
                            best_path = path
                    except OSError:
                        pass
        return best_path

    def _register_compressed_outputs(self, results, algorithm):
        """Store output paths produced by the latest batch run."""
        for result in results:
            if not result.get("success"):
                continue

            input_path = result.get("input_path")
            output_path = Path(result.get("output_path", ""))
            if input_path and output_path.is_file():
                resolved = str(Path(input_path).resolve())
                if resolved not in self.compressed_outputs:
                    self.compressed_outputs[resolved] = {}
                self.compressed_outputs[resolved][algorithm] = output_path

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

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

    def _on_close(self):
        """Clean shutdown when window is closed."""
        self.cancel_requested = True
        self.logger.info("app_close", "Application closed by user")
        self.destroy()

    def run(self):
        """Start the application."""
        self.mainloop()


def main():
    """Main entry point."""
    app = CompressionApp()
    app.run()


if __name__ == "__main__":
    main()
