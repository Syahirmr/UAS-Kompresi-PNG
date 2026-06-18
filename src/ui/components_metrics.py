"""
Metrics Panel Component
Display compression metrics, comparison summary, and charts.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from PIL import Image, ImageOps, ImageTk

from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_TITLE, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY,
    PADDING_NORMAL, PADDING_SMALL
)
from src.export.exporter import compute_ranking_scores


class MetricsPanelComponent(ttk.LabelFrame):
    """Display compression metrics in table format, comparison summary, and charts."""

    def __init__(self, parent):
        super().__init__(parent, text="Metrics & Comparison", padding=0)
        self.pack(fill=tk.BOTH, expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)

        # Notebook with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=PADDING_SMALL, pady=PADDING_SMALL)

        # --- Tab 1: Metrics Table ---
        self.metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.metrics_tab, text="Metrics Table")
        self._build_metrics_table()

        # --- Tab 2: Comparison Summary ---
        self.comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_tab, text="Comparison Summary")
        self._build_comparison_summary()

        # --- Tab 3: Charts ---
        self.charts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_tab, text="Charts")
        self._build_charts_tab()

        # --- Tab 4: Ranking Table ---
        self.ranking_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ranking_tab, text="Ranking Table")
        self._build_ranking_table()

    # ------------------------------------------------------------------
    # Tab 1: Metrics Table
    # ------------------------------------------------------------------

    def _build_metrics_table(self):
        """Build the metrics Treeview inside the metrics tab."""
        columns = (
            "File",
            "Algorithm",
            "Original Size",
            "Compressed Size",
            "Reduction %",
            "Time (ms)",
            "Resolution",
            "Status"
        )

        self.tree = ttk.Treeview(
            self.metrics_tab,
            columns=columns,
            height=8,
            show="headings",
            selectmode=tk.BROWSE
        )

        self.tree.heading("File", text="File")
        self.tree.column("File", width=150, anchor=tk.W)
        self.tree.heading("Algorithm", text="Algorithm")
        self.tree.column("Algorithm", width=120, anchor=tk.CENTER)
        self.tree.heading("Original Size", text="Original Size")
        self.tree.column("Original Size", width=100, anchor=tk.CENTER)
        self.tree.heading("Compressed Size", text="Compressed Size")
        self.tree.column("Compressed Size", width=120, anchor=tk.CENTER)
        self.tree.heading("Reduction %", text="Reduction %")
        self.tree.column("Reduction %", width=100, anchor=tk.CENTER)
        self.tree.heading("Time (ms)", text="Time (ms)")
        self.tree.column("Time (ms)", width=90, anchor=tk.CENTER)
        self.tree.heading("Resolution", text="Resolution")
        self.tree.column("Resolution", width=100, anchor=tk.CENTER)
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.metrics_tab, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Summary section below table
        self.summary_var = tk.StringVar(
            value="Completed: 0 | Failed: 0 | Cancelled: No | Avg Reduction: 0.00% | Avg Time: 0.00 ms"
        )
        summary_label = tk.Label(
            self.metrics_tab,
            textvariable=self.summary_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            anchor=tk.W,
            justify=tk.LEFT
        )
        summary_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(PADDING_NORMAL, 0))

    # ------------------------------------------------------------------
    # Tab 2: Comparison Summary
    # ------------------------------------------------------------------

    def _build_comparison_summary(self):
        """Build comparison summary panel with winner display."""
        container = ttk.Frame(self.comparison_tab)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title = tk.Label(
            container,
            text="Algorithm Comparison Results",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        )
        title.pack(anchor=tk.W, pady=(0, 15))

        # Per-algorithm summary frame
        self.algo_summary_frame = ttk.Frame(container)
        self.algo_summary_frame.pack(fill=tk.X, pady=(0, 15))

        # Algorithm summary labels (3 columns - one per algo)
        self.algo_frames = {}
        self.algo_summary_labels = {}
        for algo_key, label, color in [
            ("deflate", "Deflate Baseline", "#0078d4"),
            ("zopfli", "Zopfli Deflate", "#107c10"),
            ("oxipng", "OxiPNG", "#d83b01"),
        ]:
            frame = tk.Frame(
                self.algo_summary_frame,
                bg=BG_ACCENT,
                relief=tk.GROOVE,
                borderwidth=2,
                padx=10,
                pady=10,
            )
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.algo_frames[algo_key] = frame

            algo_title = tk.Label(
                frame,
                text=label,
                font=FONT_HEADING,
                fg=color,
                bg=BG_ACCENT
            )
            algo_title.pack(anchor=tk.W)

            var = tk.StringVar(value="No data")
            lbl = tk.Label(
                frame,
                textvariable=var,
                font=FONT_NORMAL,
                fg=TEXT_SECONDARY,
                bg=BG_ACCENT,
                justify=tk.LEFT
            )
            lbl.pack(anchor=tk.W, fill=tk.X)
            self.algo_summary_labels[algo_key] = var

        # Winners section — now with 3 winners (Best Compression, Fastest, Balanced)
        winner_frame = tk.Frame(
            container,
            bg=BG_ACCENT,
            relief=tk.GROOVE,
            borderwidth=2,
            padx=10,
            pady=10
        )
        winner_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            winner_frame,
            text="WINNERS",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        ).pack(anchor=tk.W, pady=(0, 10))

        # Best compression
        best_frame = ttk.Frame(winner_frame)
        best_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            best_frame,
            text="Best Compression:  ",
            font=FONT_HEADING,
            fg="#107c10",
            bg=BG_ACCENT
        ).pack(side=tk.LEFT)
        self.winner_reduction_var = tk.StringVar(value="N/A")
        tk.Label(
            best_frame,
            textvariable=self.winner_reduction_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        ).pack(side=tk.LEFT)

        # Fastest
        fast_frame = ttk.Frame(winner_frame)
        fast_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            fast_frame,
            text="Fastest:           ",
            font=FONT_HEADING,
            fg="#0078d4",
            bg=BG_ACCENT
        ).pack(side=tk.LEFT)
        self.winner_speed_var = tk.StringVar(value="N/A")
        tk.Label(
            fast_frame,
            textvariable=self.winner_speed_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        ).pack(side=tk.LEFT)

        # Balanced
        balanced_frame = ttk.Frame(winner_frame)
        balanced_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            balanced_frame,
            text="Balanced:           ",
            font=FONT_HEADING,
            fg="#6b3fa0",
            bg=BG_ACCENT
        ).pack(side=tk.LEFT)
        self.winner_balanced_var = tk.StringVar(value="N/A")
        tk.Label(
            balanced_frame,
            textvariable=self.winner_balanced_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT
        ).pack(side=tk.LEFT)

        # Comparison status
        self.comparison_status_var = tk.StringVar(value="Belum ada data perbandingan")
        tk.Label(
            container,
            textvariable=self.comparison_status_var,
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
            anchor=tk.W
        ).pack(anchor=tk.W, fill=tk.X, pady=(10, 0))

    # ------------------------------------------------------------------
    # Tab 3: Charts
    # ------------------------------------------------------------------

    def _build_charts_tab(self):
        """Build chart display tab (shows reduction chart by default)."""
        # Container for chart navigation
        nav_frame = ttk.Frame(self.charts_tab)
        nav_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.chart_switch_var = tk.StringVar(value="reduction")
        self.chart_switch_btn = tk.Button(
            nav_frame,
            text="Switch to Time Chart",
            font=FONT_NORMAL,
            bg="#0078d4",
            fg="#ffffff",
            padx=10,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._toggle_chart_view
        )
        self.chart_switch_btn.pack(side=tk.LEFT)

        # Chart display canvas
        self.chart_canvas = tk.Label(
            self.charts_tab,
            text="[ Chart akan muncul setelah comparison selesai ]",
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
            relief=tk.SUNKEN,
            borderwidth=1,
            justify=tk.CENTER
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.current_chart_photo = None

        # Store chart paths for toggling
        self._reduction_chart_path = None
        self._time_chart_path = None

    def _toggle_chart_view(self):
        """Toggle between reduction chart and time chart."""
        if self.chart_switch_var.get() == "reduction":
            # Show time chart
            self.chart_switch_var.set("time")
            self.chart_switch_btn.config(text="Switch to Reduction Chart")
            if self._time_chart_path:
                self._display_chart_image(self._time_chart_path)
        else:
            # Show reduction chart
            self.chart_switch_var.set("reduction")
            self.chart_switch_btn.config(text="Switch to Time Chart")
            if self._reduction_chart_path:
                self._display_chart_image(self._reduction_chart_path)

    # ------------------------------------------------------------------
    # Tab 4: Ranking Table
    # ------------------------------------------------------------------

    def _build_ranking_table(self):
        """Build ranking table with Algorithm, Avg Reduction %, Avg Time, Files Success, Score."""
        columns = (
            "Rank",
            "Algorithm",
            "Avg Reduction %",
            "Avg Time (ms)",
            "Files Success",
            "Score",
        )

        self.ranking_tree = ttk.Treeview(
            self.ranking_tab,
            columns=columns,
            height=6,
            show="headings",
            selectmode=tk.BROWSE,
        )

        self.ranking_tree.heading("Rank", text="Rank")
        self.ranking_tree.column("Rank", width=50, anchor=tk.CENTER)
        self.ranking_tree.heading("Algorithm", text="Algorithm")
        self.ranking_tree.column("Algorithm", width=150, anchor=tk.W)
        self.ranking_tree.heading("Avg Reduction %", text="Avg Reduction %")
        self.ranking_tree.column("Avg Reduction %", width=120, anchor=tk.CENTER)
        self.ranking_tree.heading("Avg Time (ms)", text="Avg Time (ms)")
        self.ranking_tree.column("Avg Time (ms)", width=120, anchor=tk.CENTER)
        self.ranking_tree.heading("Files Success", text="Files Success")
        self.ranking_tree.column("Files Success", width=100, anchor=tk.CENTER)
        self.ranking_tree.heading("Score", text="Score")
        self.ranking_tree.column("Score", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.ranking_tab, orient=tk.VERTICAL, command=self.ranking_tree.yview)
        self.ranking_tree.configure(yscrollcommand=scrollbar.set)

        self.ranking_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Ranking description
        self.ranking_desc_var = tk.StringVar(
            value="Score: kombinasi 50% reduksi + 50% kecepatan (0-100). Jalankan comparison untuk melihat ranking."
        )
        desc_label = tk.Label(
            self.ranking_tab,
            textvariable=self.ranking_desc_var,
            font=FONT_NORMAL,
            fg=TEXT_SECONDARY,
            bg=BG_ACCENT,
            anchor=tk.W,
            justify=tk.LEFT,
        )
        desc_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(PADDING_NORMAL, 0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self):
        """Reset metrics display to placeholder values."""
        self.clear_all()
        self.set_summary({
            "completed": 0,
            "failed": 0,
            "cancelled": False,
            "avg_reduction": 0,
            "avg_time_ms": 0,
        })
        self.clear_comparison()

    def clear_all(self):
        """Clear all placeholder rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_metric(self, metric):
        """Add one metrics row."""
        self.tree.insert(
            "",
            tk.END,
            values=(
                metric["file"],
                metric["algorithm"],
                self._format_bytes(metric["original_size"]),
                self._format_bytes(metric["compressed_size"]),
                f"{metric['reduction_percent']:.2f}%",
                f"{metric['time_ms']:.2f}",
                metric["resolution"],
                metric["status"],
            )
        )

    def set_summary(self, summary):
        """Update summary section."""
        cancelled = "Yes" if summary["cancelled"] else "No"
        self.summary_var.set(
            "Completed: "
            f"{summary['completed']} | Failed: {summary['failed']} | "
            f"Cancelled: {cancelled} | "
            f"Avg Reduction: {summary['avg_reduction']:.2f}% | "
            f"Avg Time: {summary['avg_time_ms']:.2f} ms"
        )

    # ------------------------------------------------------------------
    # Comparison display
    # ------------------------------------------------------------------

    def show_comparison(self, per_algorithm, winners):
        """Update comparison summary tab with results, rankings, and charts."""
        # Update per-algorithm summaries
        for algo_key, var in self.algo_summary_labels.items():
            data = per_algorithm.get(algo_key)
            if data and data["metrics"]:
                s = data["summary"]
                successful = sum(1 for m in data["metrics"] if m["status"] == "SUCCESS")
                failed_count = sum(1 for m in data["metrics"] if m["status"] == "FAILED")
                var.set(
                    f"Files: {successful} ok, {failed_count} fail\n"
                    f"Avg Reduction: {s['avg_reduction']:.2f}%\n"
                    f"Avg Time: {s['avg_time_ms']:.2f} ms"
                )
            else:
                var.set("No data")

        # Update winners (3 categories)
        wr_label = winners.get("winner_reduction_label", "N/A")
        wr_value = winners.get("winner_reduction_value", 0)
        ws_label = winners.get("winner_speed_label", "N/A")
        ws_value = winners.get("winner_speed_value", 0)
        wb_label = winners.get("winner_balanced_label", "N/A")
        wb_value = winners.get("winner_balanced_value", 0)

        self.winner_reduction_var.set(
            f"{wr_label} (Avg Reduction: {wr_value:.2f}%)"
        )
        self.winner_speed_var.set(
            f"{ws_label} (Avg Time: {ws_value:.2f} ms)"
        )
        self.winner_balanced_var.set(
            f"{wb_label} (Score: {wb_value:.2f})"
        )

        self.comparison_status_var.set(
            "Comparison selesai. Lihat tab Charts untuk visualisasi, Ranking Table untuk peringkat."
        )

        # Update ranking table
        self._update_ranking_table(per_algorithm, winners)

        # Switch to comparison tab
        self.notebook.select(1)

    def _update_ranking_table(self, per_algorithm, winners):
        """Update the ranking table with scores, sorted by rank."""
        # Clear existing rows
        for item in self.ranking_tree.get_children():
            self.ranking_tree.delete(item)

        # Compute scores for each algorithm
        scores = compute_ranking_scores(per_algorithm)

        # Collect rows
        rows = []
        for algo_key, data in per_algorithm.items():
            s = data["summary"]
            successful = sum(1 for m in data["metrics"] if m["status"] == "SUCCESS")
            score = scores.get(algo_key, 0)
            rows.append((data["label"], s["avg_reduction"], s["avg_time_ms"], successful, score))

        # Sort by score descending
        rows.sort(key=lambda r: r[4], reverse=True)

        for rank, (label, avg_red, avg_time, success, score) in enumerate(rows, start=1):
            self.ranking_tree.insert(
                "",
                tk.END,
                values=(
                    f"#{rank}",
                    label,
                    f"{avg_red:.2f}%",
                    f"{avg_time:.2f}",
                    f"{success}",
                    f"{score:.2f}",
                ),
            )

    def show_chart(self, reduction_path, time_path):
        """Store chart paths and display the reduction chart first."""
        self._reduction_chart_path = reduction_path
        self._time_chart_path = time_path
        self.chart_switch_var.set("reduction")
        self.chart_switch_btn.config(text="Switch to Time Chart")

        if reduction_path:
            self._display_chart_image(reduction_path)

    def _display_chart_image(self, chart_path):
        """Display a chart image in the charts tab."""
        path = Path(chart_path)
        if not path.is_file():
            self.chart_canvas.config(
                image="",
                text="[ Chart image not found ]",
                fg=TEXT_SECONDARY
            )
            return

        try:
            with Image.open(path) as img:
                img = img.copy()
        except OSError:
            self.chart_canvas.config(
                image="",
                text="[ Failed to load chart ]",
                fg=TEXT_SECONDARY
            )
            return

        # Fit chart to available space
        display_w = 700
        display_h = 400
        img = ImageOps.contain(img, (display_w, display_h), Image.Resampling.LANCZOS)

        # Center on canvas
        canvas = Image.new("RGBA", (display_w, display_h), BG_ACCENT)
        offset_x = (display_w - img.width) // 2
        offset_y = (display_h - img.height) // 2
        canvas.paste(img, (offset_x, offset_y))

        self.current_chart_photo = ImageTk.PhotoImage(canvas)
        self.chart_canvas.config(image=self.current_chart_photo, text="")

    def clear_comparison(self):
        """Reset comparison display."""
        for var in self.algo_summary_labels.values():
            var.set("No data")
        self.winner_reduction_var.set("N/A")
        self.winner_speed_var.set("N/A")
        self.winner_balanced_var.set("N/A")
        self.comparison_status_var.set("Belum ada data perbandingan")
        self.chart_canvas.config(
            image="",
            text="[ Chart akan muncul setelah comparison selesai ]",
            fg=TEXT_SECONDARY
        )
        self.current_chart_photo = None
        self._reduction_chart_path = None
        self._time_chart_path = None

        # Clear ranking table
        for item in self.ranking_tree.get_children():
            self.ranking_tree.delete(item)

    def _format_bytes(self, value):
        """Format bytes as KB for display."""
        if value <= 0:
            return "-"
        return f"{value / 1024:.2f} KB"
