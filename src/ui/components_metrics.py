"""
Metrics Panel Component
Display compression metrics, comparison summary, and charts.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageOps, ImageTk

from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_TITLE, BG_ACCENT, BG_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    PADDING_NORMAL, PADDING_SMALL, BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR
)
from src.export.exporter import compute_ranking_scores


class MetricsPanelComponent(ctk.CTkFrame):
    """Display compression metrics in table format, comparison summary, and charts using CustomTkinter."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)

        # Tabview container
        self.notebook = ctk.CTkTabview(
            self,
            fg_color=BG_ACCENT,
            segmented_button_fg_color=BG_PRIMARY,
            segmented_button_selected_color=BUTTON_BG,
            segmented_button_selected_hover_color=BUTTON_HOVER,
            segmented_button_unselected_hover_color=BUTTON_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=BORDER_RADIUS
        )
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # Add tabs
        self.notebook.add("Metrics Table")
        self.notebook.add("Comparison Summary")
        self.notebook.add("Charts")
        self.notebook.add("Ranking Table")

        # Get frame references for each tab
        self.metrics_tab = self.notebook.tab("Metrics Table")
        self.comparison_tab = self.notebook.tab("Comparison Summary")
        self.charts_tab = self.notebook.tab("Charts")
        self.ranking_tab = self.notebook.tab("Ranking Table")

        # Configure tab frames layout
        self.metrics_tab.grid_columnconfigure(0, weight=1)
        self.metrics_tab.grid_rowconfigure(0, weight=1)
        
        self.ranking_tab.grid_columnconfigure(0, weight=1)
        self.ranking_tab.grid_rowconfigure(0, weight=1)

        # Build tabs content
        self._build_metrics_table()
        self._build_comparison_summary()
        self._build_charts_tab()
        self._build_ranking_table()
        
        # Apply initial Treeview styling based on active theme
        self.update_theme_styles()

    # ------------------------------------------------------------------
    # Treeview Dynamic Styling
    # ------------------------------------------------------------------
    
    def update_theme_styles(self):
        """Dynamically style standard TTK Treeviews to match Light/Dark modes of CTK."""
        style = ttk.Style()
        style.theme_use("clam")
        
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            field_bg = "#2b2b2b"
            header_bg = "#1e1e1e"
            header_fg = "#ffffff"
            selected_bg = "#1f77b4"
        else:
            bg_color = "#ffffff"
            fg_color = "#1e1e1e"
            field_bg = "#ffffff"
            header_bg = "#eaeaea"
            header_fg = "#1e1e1e"
            selected_bg = "#0078d4"

        # Apply Treeview styles
        style.configure(
            "Treeview",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=field_bg,
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=header_bg,
            foreground=header_fg,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", "#ffffff")]
        )
        
        # Redraw charts if loaded
        if self._reduction_chart_path:
            self._toggle_chart_view(only_redraw=True)

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

        tree_frame = ctk.CTkFrame(self.metrics_tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_NORMAL)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            height=8,
            show="headings",
            selectmode=tk.BROWSE
        )

        self.tree.heading("File", text="File")
        self.tree.column("File", width=180, anchor=tk.W)
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

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Summary section below table
        self.summary_var = ctk.StringVar(
            value="Completed: 0 | Failed: 0 | Cancelled: No | Avg Reduction: 0.00% | Avg Time: 0.00 ms"
        )
        summary_label = ctk.CTkLabel(
            self.metrics_tab,
            textvariable=self.summary_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            justify="left"
        )
        summary_label.pack(side="bottom", fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))

    # ------------------------------------------------------------------
    # Tab 2: Comparison Summary
    # ------------------------------------------------------------------

    def _build_comparison_summary(self):
        """Build comparison summary panel with winner display."""
        container = ctk.CTkFrame(self.comparison_tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_NORMAL)

        # Title
        title = ctk.CTkLabel(
            container,
            text="Algorithm Comparison Results",
            font=ctk.CTkFont(family=FONT_TITLE[0], size=FONT_TITLE[1] + 4, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(anchor="w", pady=(0, 15))

        # Per-algorithm summary frame
        self.algo_summary_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.algo_summary_frame.pack(fill="x", pady=(0, 15))

        # Algorithm summary labels (3 columns - one per algo)
        self.algo_frames = {}
        self.algo_summary_labels = {}
        for algo_key, label, color_pair in [
            ("deflate", "Deflate Baseline", ("#0078d4", "#1f77b4")),
            ("zopfli", "Zopfli Deflate", ("#107c10", "#2ea44f")),
            ("oxipng", "OxiPNG", ("#d83b01", "#da3637")),
        ]:
            frame = ctk.CTkFrame(
                self.algo_summary_frame,
                fg_color=BG_PRIMARY,
                corner_radius=BORDER_RADIUS,
                border_width=1,
                border_color=BORDER_COLOR
            )
            frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            self.algo_frames[algo_key] = frame

            algo_title = ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
                text_color=color_pair
            )
            algo_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))

            var = ctk.StringVar(value="No data")
            lbl = ctk.CTkLabel(
                frame,
                textvariable=var,
                font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
                text_color=TEXT_SECONDARY,
                justify="left",
                anchor="w"
            )
            lbl.pack(anchor="w", fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
            self.algo_summary_labels[algo_key] = var

        # Winners section (Sleek cards layout)
        winner_container = ctk.CTkFrame(
            container,
            fg_color=BG_PRIMARY,
            corner_radius=BORDER_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        winner_container.pack(fill="x", pady=(0, 10))

        tk_title = ctk.CTkLabel(
            winner_container,
            text="WINNERS",
            font=ctk.CTkFont(family=FONT_TITLE[0], size=FONT_TITLE[1] + 2, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        tk_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 10))

        # Best compression row
        best_frame = ctk.CTkFrame(winner_container, fg_color="transparent")
        best_frame.pack(fill="x", padx=PADDING_NORMAL, pady=4)
        ctk.CTkLabel(
            best_frame,
            text="Best Compression:",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=("#107c10", "#2ea44f"),
            width=150,
            anchor="w"
        ).pack(side="left")
        self.winner_reduction_var = ctk.StringVar(value="N/A")
        ctk.CTkLabel(
            best_frame,
            textvariable=self.winner_reduction_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        # Fastest row
        fast_frame = ctk.CTkFrame(winner_container, fg_color="transparent")
        fast_frame.pack(fill="x", padx=PADDING_NORMAL, pady=4)
        ctk.CTkLabel(
            fast_frame,
            text="Fastest:",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=("#0078d4", "#1f77b4"),
            width=150,
            anchor="w"
        ).pack(side="left")
        self.winner_speed_var = ctk.StringVar(value="N/A")
        ctk.CTkLabel(
            fast_frame,
            textvariable=self.winner_speed_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        # Balanced row
        balanced_frame = ctk.CTkFrame(winner_container, fg_color="transparent")
        balanced_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(4, PADDING_NORMAL))
        ctk.CTkLabel(
            balanced_frame,
            text="Balanced:",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=("#6b3fa0", "#9b59b6"),
            width=150,
            anchor="w"
        ).pack(side="left")
        self.winner_balanced_var = ctk.StringVar(value="N/A")
        ctk.CTkLabel(
            balanced_frame,
            textvariable=self.winner_balanced_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        # Comparison status
        self.comparison_status_var = ctk.StringVar(value="Belum ada data perbandingan")
        status_lbl = ctk.CTkLabel(
            container,
            textvariable=self.comparison_status_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        status_lbl.pack(anchor="w", fill="x", pady=(10, 0))

    # ------------------------------------------------------------------
    # Tab 3: Charts
    # ------------------------------------------------------------------

    def _build_charts_tab(self):
        """Build chart display tab (shows reduction chart by default)."""
        nav_frame = ctk.CTkFrame(self.charts_tab, fg_color="transparent")
        nav_frame.pack(fill="x", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 0))

        self.chart_switch_var = ctk.StringVar(value="reduction")
        self.chart_switch_btn = ctk.CTkButton(
            nav_frame,
            text="Switch to Time Chart",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            fg_color=BUTTON_BG,
            text_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            corner_radius=CONTROL_RADIUS,
            height=36,
            command=self._toggle_chart_view
        )
        self.chart_switch_btn.pack(side="left")

        # Chart display area
        self.chart_canvas = ctk.CTkLabel(
            self.charts_tab,
            text="[ Chart akan muncul setelah comparison selesai ]",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY,
            fg_color=BG_PRIMARY,
            corner_radius=BORDER_RADIUS,
            height=400
        )
        self.chart_canvas.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_NORMAL)
        self.current_chart_photo = None

        # Store chart paths for toggling
        self._reduction_chart_path = None
        self._time_chart_path = None

    def _toggle_chart_view(self, only_redraw=False):
        """Toggle between reduction chart and time chart."""
        if not only_redraw:
            if self.chart_switch_var.get() == "reduction":
                self.chart_switch_var.set("time")
                self.chart_switch_btn.configure(text="Switch to Reduction Chart")
            else:
                self.chart_switch_var.set("reduction")
                self.chart_switch_btn.configure(text="Switch to Time Chart")

        # Render corresponding chart
        if self.chart_switch_var.get() == "reduction":
            if self._reduction_chart_path:
                self._display_chart_image(self._reduction_chart_path)
        else:
            if self._time_chart_path:
                self._display_chart_image(self._time_chart_path)

    # ------------------------------------------------------------------
    # Tab 4: Ranking Table
    # ------------------------------------------------------------------

    def _build_ranking_table(self):
        """Build ranking table styled for CustomTkinter."""
        columns = (
            "Rank",
            "Algorithm",
            "Avg Reduction %",
            "Avg Time (ms)",
            "Files Success",
            "Score",
        )

        tree_frame = ctk.CTkFrame(self.ranking_tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_NORMAL)

        self.ranking_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            height=6,
            show="headings",
            selectmode=tk.BROWSE,
        )

        self.ranking_tree.heading("Rank", text="Rank")
        self.ranking_tree.column("Rank", width=50, anchor=tk.CENTER)
        self.ranking_tree.heading("Algorithm", text="Algorithm")
        self.ranking_tree.column("Algorithm", width=180, anchor=tk.W)
        self.ranking_tree.heading("Avg Reduction %", text="Avg Reduction %")
        self.ranking_tree.column("Avg Reduction %", width=120, anchor=tk.CENTER)
        self.ranking_tree.heading("Avg Time (ms)", text="Avg Time (ms)")
        self.ranking_tree.column("Avg Time (ms)", width=120, anchor=tk.CENTER)
        self.ranking_tree.heading("Files Success", text="Files Success")
        self.ranking_tree.column("Files Success", width=100, anchor=tk.CENTER)
        self.ranking_tree.heading("Score", text="Score")
        self.ranking_tree.column("Score", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.ranking_tree.yview)
        self.ranking_tree.configure(yscrollcommand=scrollbar.set)

        self.ranking_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Ranking description
        self.ranking_desc_var = ctk.StringVar(
            value="Score: kombinasi 50% reduksi + 50% kecepatan (0-100). Jalankan comparison untuk melihat ranking."
        )
        desc_label = ctk.CTkLabel(
            self.ranking_tab,
            textvariable=self.ranking_desc_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w",
            justify="left"
        )
        desc_label.pack(side="bottom", fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))

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

        # Switch to comparison tab in CTKTabview
        self.notebook.set("Comparison Summary")

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
        self.chart_switch_btn.configure(text="Switch to Time Chart")

        if reduction_path:
            self._display_chart_image(reduction_path)

    def _display_chart_image(self, chart_path):
        """Display a chart image in the charts tab."""
        path = Path(chart_path)
        if not path.is_file():
            self.chart_canvas.configure(
                image=None,
                text="[ Chart image not found ]",
                text_color=TEXT_SECONDARY
            )
            return

        try:
            with Image.open(path) as img:
                img = img.copy()
        except OSError:
            self.chart_canvas.configure(
                image=None,
                text="[ Failed to load chart ]",
                text_color=TEXT_SECONDARY
            )
            return

        # Fit chart to available space
        display_w = 700
        display_h = 400
        img = ImageOps.contain(img, (display_w, display_h), Image.Resampling.LANCZOS)

        # Center on canvas with background color matching active theme
        bg_val = BG_ACCENT
        if isinstance(bg_val, tuple):
            mode = ctk.get_appearance_mode()
            bg_hex = bg_val[1] if mode == "Dark" else bg_val[0]
        else:
            bg_hex = bg_val
            
        canvas = Image.new("RGBA", (display_w, display_h), bg_hex)
        offset_x = (display_w - img.width) // 2
        offset_y = (display_h - img.height) // 2
        canvas.paste(img, (offset_x, offset_y))

        # Build CTK compatible PhotoImage
        self.current_chart_photo = ImageTk.PhotoImage(canvas)
        self.chart_canvas.configure(image=self.current_chart_photo, text="")

    def clear_comparison(self):
        """Reset comparison display."""
        for var in self.algo_summary_labels.values():
            var.set("No data")
        self.winner_reduction_var.set("N/A")
        self.winner_speed_var.set("N/A")
        self.winner_balanced_var.set("N/A")
        self.comparison_status_var.set("Belum ada data perbandingan")
        self.chart_canvas.configure(
            image=None,
            text="[ Chart akan muncul setelah comparison selesai ]",
            text_color=TEXT_SECONDARY
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
