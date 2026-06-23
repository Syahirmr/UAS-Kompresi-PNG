"""
Metrics Panel Component
Displays compression metrics table, comparison summary, charts, ranking, trends, and file details.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageOps, ImageTk
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, FONT_TITLE, FONT_SMALL, BG_ACCENT, BG_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_BG, BUTTON_FG, BUTTON_HOVER,
    PADDING_LARGE, PADDING_NORMAL, PADDING_SMALL, BORDER_RADIUS, CONTROL_RADIUS, BORDER_COLOR,
    SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, PURPLE_COLOR
)
from src.export.exporter import compute_ranking_scores


class MetricsPanelComponent(ctk.CTkFrame):
    """6-tab Analytics Panel for desktop PNG compression details."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)

        # Title row with badge (numbered 5, replacing Point 5 with Point 6 'Tabel Hasil')
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.pack(anchor="w", fill="x", pady=(0, 10))
        
        badge_label = ctk.CTkLabel(
            title_row,
            text="5",
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
            text="Tabel Hasil",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        section_title.pack(side="left")

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

        # Add 6 Tabs
        self.notebook.add("Tabel Hasil")
        self.notebook.add("Ringkasan Metrik")
        self.notebook.add("Visualisasi Chart")
        self.notebook.add("Tabel Peringkat")
        self.notebook.add("Grafik Performa")
        self.notebook.add("Detail Berkas")

        # Tab Frames References
        self.metrics_tab = self.notebook.tab("Tabel Hasil")
        self.summary_tab = self.notebook.tab("Ringkasan Metrik")
        self.charts_tab = self.notebook.tab("Visualisasi Chart")
        self.ranking_tab = self.notebook.tab("Tabel Peringkat")
        self.trends_tab = self.notebook.tab("Grafik Performa")
        self.details_tab = self.notebook.tab("Detail Berkas")

        # Internal state
        self.all_metrics_data = [] # Raw list of dicts
        self.per_algorithm_results = None
        self.winners = None
        self.sort_column = "File"
        self.sort_desc = False
        self.active_file_path = None
        
        # Build contents
        self._build_metrics_table_tab()
        self._build_comparison_summary_tab()
        self._build_charts_tab()
        self._build_ranking_table_tab()
        self._build_trends_tab()
        self._build_details_tab()
        
        # Initialise styling
        self.update_theme_styles()

    # =========================================================================
    # THEME STYLES
    # =========================================================================
    def update_theme_styles(self):
        """Configure standard TTK Treeviews and Matplotlib defaults to match current theme."""
        style = ttk.Style()
        style.theme_use("clam")
        
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            bg_color = "#111827"
            fg_color = "#F9FAFB"
            field_bg = "#111827"
            header_bg = "#1F2937"
            header_fg = "#F9FAFB"
            selected_bg = "#2563EB"
            border_c = "#1F2937"
        else:
            bg_color = "#FFFFFF"
            fg_color = "#111827"
            field_bg = "#FFFFFF"
            header_bg = "#E5E7EB"
            header_fg = "#111827"
            selected_bg = "#2563EB"
            border_c = "#E5E7EB"

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
            borderwidth=1,
            bordercolor=border_c
        )
        style.map(
            "Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", "#ffffff")]
        )
        
        # Re-render Matplotlib charts and trends
        self.after_idle(self._redraw_charts)

    def _redraw_charts(self):
        """Trigger re-drawing of matplotlib canvases when theme changes."""
        if self.per_algorithm_results:
            self._render_matplotlib_charts()
            self._render_trend_charts()

    # =========================================================================
    # TAB 1: METRICS TABLE
    # =========================================================================
    def _build_metrics_table_tab(self):
        """Construct Table View with Search, Sort, Filter, and Export controls."""
        self.metrics_tab.grid_columnconfigure(0, weight=1)
        self.metrics_tab.grid_rowconfigure(1, weight=1)
        
        # Toolbar Frame
        toolbar = ctk.CTkFrame(self.metrics_tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
        
        # Search Box
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._refresh_table())
        search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search files...",
            textvariable=self.search_var,
            width=200,
            height=32,
            corner_radius=CONTROL_RADIUS,
            border_color=BORDER_COLOR
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        # Filter Algorithm Dropdown
        self.filter_algo_var = ctk.StringVar(value="All Algorithms")
        filter_algo = ctk.CTkOptionMenu(
            toolbar,
            variable=self.filter_algo_var,
            values=["All Algorithms", "Deflate Baseline", "Zopfli Deflate", "OxiPNG"],
            command=lambda v: self._refresh_table(),
            width=150,
            height=32,
            fg_color=("#F1F5F9", "#1F2937"),
            button_color=("#E5E7EB", "#1F2937"),
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_ACCENT,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=CONTROL_RADIUS
        )
        filter_algo.pack(side="left", padx=(0, 10))
        
        # Filter Status Dropdown
        self.filter_status_var = ctk.StringVar(value="All Status")
        filter_status = ctk.CTkOptionMenu(
            toolbar,
            variable=self.filter_status_var,
            values=["All Status", "Success", "Failed"],
            command=lambda v: self._refresh_table(),
            width=120,
            height=32,
            fg_color=("#F1F5F9", "#1F2937"),
            button_color=("#E5E7EB", "#1F2937"),
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_ACCENT,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=CONTROL_RADIUS
        )
        filter_status.pack(side="left")
        
        # Export Button (Placed on top right of table toolbar)
        self.export_btn = ctk.CTkButton(
            toolbar,
            text="📤 Export Report",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            fg_color=("#107c10", "#2ea44f"),
            text_color=BUTTON_FG,
            hover_color=("#1f9d1f", "#34d058"),
            corner_radius=CONTROL_RADIUS,
            height=32,
            width=140,
            state="disabled"
        )
        self.export_btn.pack(side="right")
        
        # Table Grid Container
        table_container = ctk.CTkFrame(self.metrics_tab, fg_color="transparent")
        table_container.grid(row=1, column=0, sticky="nsew", padx=PADDING_NORMAL, pady=5)
        
        columns = (
            "File Name",
            "Original Size",
            "Algorithm",
            "Compressed Size",
            "Reduction %",
            "Ratio",
            "Time (ms)",
            "Throughput"
        )
        
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode=tk.BROWSE
        )
        
        col_widths = {
            "File Name": 200,
            "Original Size": 100,
            "Algorithm": 120,
            "Compressed Size": 120,
            "Reduction %": 100,
            "Ratio": 80,
            "Time (ms)": 90,
            "Throughput": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._on_header_click(c))
            self.tree.column(col, width=col_widths[col], anchor=tk.CENTER if col != "File Name" else tk.W)
            
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Selection event binding to update TAB 6 details
        self.tree.bind("<<TreeviewSelect>>", self._on_table_row_selected)
        
        # Summary footer bar
        self.summary_var = ctk.StringVar(
            value="Completed: 0 | Failed: 0 | Avg Reduction: 0.00% | Avg Time: 0.00 ms"
        )
        summary_lbl = ctk.CTkLabel(
            self.metrics_tab,
            textvariable=self.summary_var,
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        summary_lbl.grid(row=2, column=0, sticky="ew", padx=PADDING_NORMAL, pady=(5, PADDING_NORMAL))

    def _on_header_click(self, column):
        """Handle heading click for sorting table rows."""
        if self.sort_column == column:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_column = column
            self.sort_desc = False
            
        self._refresh_table()

    def _on_table_row_selected(self, event):
        """Update file details view when a row is selected."""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        if item_values:
            filename = item_values[0]
            # Find the path matching filename
            for metric in self.all_metrics_data:
                if metric["file"] == filename:
                    # We can use the active path or just display it
                    pass

    def _refresh_table(self):
        """Filter, sort, and rebuild Treeview list items."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_query = self.search_var.get().lower()
        filter_algo = self.filter_algo_var.get()
        filter_status = self.filter_status_var.get()
        
        # Filter
        filtered_metrics = []
        for m in self.all_metrics_data:
            # search name
            if search_query and search_query not in m["file"].lower():
                continue
            # algo
            if filter_algo != "All Algorithms" and m["algorithm"] != filter_algo:
                continue
            # status
            if filter_status != "All Status":
                status_ok = m["status"] == "SUCCESS"
                if filter_status == "Success" and not status_ok: continue
                if filter_status == "Failed" and status_ok: continue
                
            filtered_metrics.append(m)
            
        # Sort
        def get_sort_key(item):
            col_map = {
                "File Name": "file",
                "Original Size": "original_size",
                "Algorithm": "algorithm",
                "Compressed Size": "compressed_size",
                "Reduction %": "reduction_percent",
                "Ratio": "ratio",
                "Time (ms)": "time_ms",
                "Throughput": "throughput_bytes"
            }
            key = col_map.get(self.sort_column, "file")
            val = item.get(key, 0)
            return val if val is not None else 0
            
        filtered_metrics.sort(key=get_sort_key, reverse=self.sort_desc)
        
        # Render
        for m in filtered_metrics:
            orig_sz = m["original_size"]
            comp_sz = m["compressed_size"]
            ratio = orig_sz / comp_sz if comp_sz > 0 else 1.0
            
            # throughput bytes/sec
            time_s = m["time_ms"] / 1000.0
            throughput_val = orig_sz / time_s if time_s > 0 else 0
            
            # Format throughput string
            if throughput_val <= 0:
                tp_str = "-"
            elif throughput_val < 1024 * 1024:
                tp_str = f"{throughput_val / 1024:.1f} KB/s"
            else:
                tp_str = f"{throughput_val / (1024*1024):.1f} MB/s"
                
            self.tree.insert(
                "",
                tk.END,
                values=(
                    m["file"],
                    self._format_bytes(orig_sz),
                    m["algorithm"],
                    self._format_bytes(comp_sz),
                    f"{m['reduction_percent']:.1f}%",
                    f"{ratio:.2f}x",
                    f"{m['time_ms']:.2f}",
                    tp_str
                )
            )

    # =========================================================================
    # TAB 2: Ringkasan Metrik (SUMMARY PANEL)
    # =========================================================================
    def _build_comparison_summary_tab(self):
        """Construct cards layout to display cumulative statistics details."""
        container = ctk.CTkFrame(self.summary_tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        title = ctk.CTkLabel(
            container,
            text="Ringkasan Perbandingan Algoritma",
            font=ctk.CTkFont(family=FONT_TITLE[0], size=FONT_TITLE[1] + 2, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(anchor="w", pady=(0, 15))
        
        # Stat grid container
        stats_grid = ctk.CTkFrame(container, fg_color="transparent")
        stats_grid.pack(fill="both", expand=True)
        stats_grid.grid_columnconfigure((0, 1, 2), weight=1)
        stats_grid.grid_rowconfigure((0, 1), weight=1)
        
        # Variables
        self.avg_reduction_var = ctk.StringVar(value="-")
        self.best_reduction_var = ctk.StringVar(value="-")
        self.fastest_algo_var = ctk.StringVar(value="-")
        self.slowest_algo_var = ctk.StringVar(value="-")
        self.avg_time_var = ctk.StringVar(value="-")
        self.total_processed_var = ctk.StringVar(value="-")
        
        stat_cards_configs = [
            ("Average Reduction", self.avg_reduction_var, 0, 0, SUCCESS_COLOR[1]),
            ("Best Reduction", self.best_reduction_var, 0, 1, SUCCESS_COLOR[1]),
            ("Fastest Algorithm", self.fastest_algo_var, 0, 2, PURPLE_COLOR[1]),
            ("Slowest Algorithm", self.slowest_algo_var, 1, 0, ERROR_COLOR[1]),
            ("Average Processing Time", self.avg_time_var, 1, 1, BUTTON_BG[1]),
            ("Total Files Processed", self.total_processed_var, 1, 2, TEXT_PRIMARY[1]),
        ]
        
        for name, var, row, col, accent_color in stat_cards_configs:
            card = ctk.CTkFrame(
                stats_grid,
                fg_color=BG_PRIMARY,
                corner_radius=BORDER_RADIUS,
                border_width=1,
                border_color=BORDER_COLOR
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            lbl_title = ctk.CTkLabel(
                card,
                text=name,
                font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
                text_color=TEXT_SECONDARY
            )
            lbl_title.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 5))
            
            lbl_val = ctk.CTkLabel(
                card,
                textvariable=var,
                font=ctk.CTkFont(family=FONT_TITLE[0], size=22, weight="bold"),
                text_color=accent_color
            )
            lbl_val.pack(anchor="w", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))

    def _update_comparison_stats(self):
        """Recalculate summary metrics cards from self.all_metrics_data."""
        if not self.all_metrics_data:
            return
            
        success_files = [m for m in self.all_metrics_data if m["status"] == "SUCCESS"]
        if not success_files:
            return
            
        reductions = [m["reduction_percent"] for m in success_files]
        times = [m["time_ms"] for m in self.all_metrics_data]
        
        avg_red = sum(reductions) / len(reductions)
        best_red = max(reductions)
        avg_time = sum(times) / len(times)
        
        self.avg_reduction_var.set(f"{avg_red:.2f}%")
        self.best_reduction_var.set(f"{best_red:.2f}%")
        self.avg_time_var.set(f"{avg_time:.1f} ms")
        self.total_processed_var.set(str(len(self.all_metrics_data)))
        
        # Calculate fastest and slowest algorithm
        algo_times = {}
        for m in self.all_metrics_data:
            if m["status"] == "SUCCESS":
                algo = m["algorithm"]
                if algo not in algo_times:
                    algo_times[algo] = []
                algo_times[algo].append(m["time_ms"])
                
        if algo_times:
            avg_algo_times = {algo: sum(vals)/len(vals) for algo, vals in algo_times.items()}
            fastest = min(avg_algo_times, key=avg_algo_times.get)
            slowest = max(avg_algo_times, key=avg_algo_times.get)
            self.fastest_algo_var.set(fastest)
            self.slowest_algo_var.set(slowest)

    # =========================================================================
    # TAB 3: Visualisasi Chart (COMPRESSION CHARTS)
    # =========================================================================
    def _build_charts_tab(self):
        """Construct Tab 3 holding Matplotlib chart selections."""
        toolbar = ctk.CTkFrame(self.charts_tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=PADDING_NORMAL, pady=PADDING_NORMAL)
        
        self.chart_type_var = ctk.StringVar(value="reduction")
        chart_segment = ctk.CTkSegmentedButton(
            toolbar,
            values=["Reduction Percentage (%)", "Processing Time (ms)", "Compression Ratio"],
            command=self._on_chart_type_changed,
            fg_color=BG_PRIMARY,
            selected_color=BUTTON_BG,
            selected_hover_color=BUTTON_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=CONTROL_RADIUS,
            height=32
        )
        chart_segment.set("Reduction Percentage (%)")
        chart_segment.pack(side="left")
        
        self.chart_canvas = ctk.CTkLabel(
            self.charts_tab,
            text="[ Selesai kompresi untuk melihat visualisasi ]",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY,
            fg_color=BG_PRIMARY,
            corner_radius=BORDER_RADIUS,
            height=420
        )
        self.chart_canvas.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        self.chart_photo = None

    def _on_chart_type_changed(self, value):
        """Toggle chart selected and redraw."""
        mapping = {
            "Reduction Percentage (%)": "reduction",
            "Processing Time (ms)": "time",
            "Compression Ratio": "ratio"
        }
        self.chart_type_var.set(mapping.get(value, "reduction"))
        self._render_matplotlib_charts()

    def _render_matplotlib_charts(self):
        """Render high contrast theme-aware Matplotlib charts to Tkinter Label."""
        if not self.per_algorithm_results:
            return
            
        chart_type = self.chart_type_var.get()
        
        # Configure layout themes
        mode = ctk.get_appearance_mode()
        is_dark = mode == "Dark"
        bg_hex = "#111827" if is_dark else "#FFFFFF"
        text_color = "#F9FAFB" if is_dark else "#111827"
        grid_color = "#1F2937" if is_dark else "#E5E7EB"
        
        # Pull data
        labels = []
        values = []
        colors = []
        
        algo_colors = {
            "deflate": "#0078d4",
            "zopfli": "#107c10",
            "oxipng": "#8B5CF6"
        }
        
        for algo_key in ["deflate", "zopfli", "oxipng"]:
            data = self.per_algorithm_results.get(algo_key)
            if data and data["metrics"]:
                s = data["summary"]
                labels.append(data["label"])
                colors.append(algo_colors[algo_key])
                
                if chart_type == "reduction":
                    values.append(s["avg_reduction"])
                elif chart_type == "time":
                    values.append(s["avg_time_ms"])
                elif chart_type == "ratio":
                    # calculate avg ratio
                    ratios = []
                    for m in data["metrics"]:
                        if m["status"] == "SUCCESS" and m["compressed_size"] > 0:
                            ratios.append(m["original_size"] / m["compressed_size"])
                    values.append(sum(ratios)/len(ratios) if ratios else 1.0)
                    
        if not labels:
            return
            
        fig, ax = plt.subplots(figsize=(6.5, 4.2), facecolor=bg_hex)
        ax.set_facecolor(bg_hex)
        
        bars = ax.bar(labels, values, color=colors, width=0.45)
        
        # Customize ticks & labels colors
        ax.tick_params(colors=text_color)
        ax.spines['bottom'].set_color(grid_color)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_color(grid_color)
        ax.yaxis.grid(True, linestyle="--", alpha=0.5, color=grid_color)
        
        # Titles
        title_map = {
            "reduction": "Average Size Reduction (%)",
            "time": "Average Processing Time (ms)",
            "ratio": "Average Compression Ratio (x)"
        }
        ax.set_title(title_map[chart_type], fontsize=12, fontweight="bold", color=text_color, pad=15)
        
        # Text values on top of bars
        for bar in bars:
            h = bar.get_height()
            txt = f"{h:.2f}%" if chart_type == "reduction" else (f"{h:.2f} ms" if chart_type == "time" else f"{h:.2f}x")
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                h + (max(values)*0.02),
                txt,
                ha="center",
                va="bottom",
                fontsize=9,
                color=text_color,
                fontweight="bold"
            )
            
        plt.tight_layout()
        
        # Save to buffer and display
        chart_dir = Path("outputs") / "charts"
        chart_dir.mkdir(parents=True, exist_ok=True)
        img_path = chart_dir / f"temp_{chart_type}.png"
        fig.savefig(str(img_path), dpi=100, bbox_inches="tight")
        plt.close(fig)
        
        self._display_chart_canvas(self.chart_canvas, img_path)

    def _display_chart_canvas(self, label_widget, img_path):
        """Safely render saved plot image onto targeted CTKLabel widget."""
        if not Path(img_path).is_file():
            return
        try:
            with Image.open(img_path) as img:
                img = img.copy()
            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(img.width, img.height)
            )
            label_widget.configure(image=ctk_img, text="")
            label_widget.image = ctk_img # hold reference
        except Exception:
            pass

    # =========================================================================
    # TAB 4: Tabel Peringkat (RANKING PANEL)
    # =========================================================================
    def _build_ranking_table_tab(self):
        """Construct Table View listing rank score metrics of compressors."""
        tree_frame = ctk.CTkFrame(self.ranking_tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=PADDING_NORMAL)
        
        columns = (
            "Rank",
            "Algorithm",
            "Compression Efficiency",
            "Speed (ms)",
            "Overall Score"
        )
        
        self.ranking_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode=tk.BROWSE
        )
        
        self.ranking_tree.heading("Rank", text="Rank")
        self.ranking_tree.column("Rank", width=60, anchor=tk.CENTER)
        self.ranking_tree.heading("Algorithm", text="Algorithm")
        self.ranking_tree.column("Algorithm", width=180, anchor=tk.W)
        self.ranking_tree.heading("Compression Efficiency", text="Compression Efficiency")
        self.ranking_tree.column("Compression Efficiency", width=160, anchor=tk.CENTER)
        self.ranking_tree.heading("Speed (ms)", text="Speed (ms)")
        self.ranking_tree.column("Speed (ms)", width=120, anchor=tk.CENTER)
        self.ranking_tree.heading("Overall Score", text="Overall Score")
        self.ranking_tree.column("Overall Score", width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.ranking_tree.yview)
        self.ranking_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ranking_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Legend status text below
        lbl_legend = ctk.CTkLabel(
            self.ranking_tab,
            text="Overall Score combines: 50% Size Reduction + 50% Speed Efficiency (Normalized score 0-100)",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        lbl_legend.pack(side="bottom", fill="x", padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))

    def _update_ranking_table(self):
        """Update ranks and overall scores using backend scoring logic."""
        if not self.per_algorithm_results:
            return
            
        for item in self.ranking_tree.get_children():
            self.ranking_tree.delete(item)
            
        scores = compute_ranking_scores(self.per_algorithm_results)
        
        rows = []
        for algo, data in self.per_algorithm_results.items():
            s = data["summary"]
            score = scores.get(algo, 0)
            rows.append((data["label"], s["avg_reduction"], s["avg_time_ms"], score))
            
        rows.sort(key=lambda r: r[3], reverse=True)
        
        for idx, (label, avg_red, avg_time, score) in enumerate(rows, start=1):
            self.ranking_tree.insert(
                "",
                tk.END,
                values=(
                    f"#{idx}",
                    label,
                    f"{avg_red:.2f}% reduction",
                    f"{avg_time:.2f} ms",
                    f"{score:.2f} / 100"
                )
            )

    # =========================================================================
    # TAB 5: Grafik Performa (TREND LINES)
    # =========================================================================
    def _build_trends_tab(self):
        """Construct Tab 5 holding line/area charts selections."""
        toolbar = ctk.CTkFrame(self.trends_tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=PADDING_NORMAL, pady=PADDING_NORMAL)
        
        self.trend_type_var = ctk.StringVar(value="time")
        trend_segment = ctk.CTkSegmentedButton(
            toolbar,
            values=["Time Performance Trend", "Size Reduction Trend", "Ratio Trend"],
            command=self._on_trend_type_changed,
            fg_color=BG_PRIMARY,
            selected_color=BUTTON_BG,
            selected_hover_color=BUTTON_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=CONTROL_RADIUS,
            height=32
        )
        trend_segment.set("Time Performance Trend")
        trend_segment.pack(side="left")
        
        self.trend_canvas = ctk.CTkLabel(
            self.trends_tab,
            text="[ Selesai kompresi untuk melihat tren grafik performa ]",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
            text_color=TEXT_SECONDARY,
            fg_color=BG_PRIMARY,
            corner_radius=BORDER_RADIUS,
            height=420
        )
        self.trend_canvas.pack(fill="both", expand=True, padx=PADDING_NORMAL, pady=(0, PADDING_NORMAL))
        self.trend_photo = None

    def _on_trend_type_changed(self, value):
        """Toggle active trend view selection and render."""
        mapping = {
            "Time Performance Trend": "time",
            "Size Reduction Trend": "reduction",
            "Ratio Trend": "ratio"
        }
        self.trend_type_var.set(mapping.get(value, "time"))
        self._render_trend_charts()

    def _render_trend_charts(self):
        """Render high contrast theme-aware Matplotlib Line/Area charts to Tkinter Label."""
        if not self.per_algorithm_results:
            return
            
        trend_type = self.trend_type_var.get()
        
        # Configure layout themes
        mode = ctk.get_appearance_mode()
        is_dark = mode == "Dark"
        bg_hex = "#111827" if is_dark else "#FFFFFF"
        text_color = "#F9FAFB" if is_dark else "#111827"
        grid_color = "#1F2937" if is_dark else "#E5E7EB"
        
        # Matplotlib plot
        fig, ax = plt.subplots(figsize=(7.0, 4.2), facecolor=bg_hex)
        ax.set_facecolor(bg_hex)
        
        algo_colors = {
            "deflate": "#0078d4",
            "zopfli": "#107c10",
            "oxipng": "#8B5CF6"
        }
        
        lines_drawn = 0
        for algo_key in ["deflate", "zopfli", "oxipng"]:
            data = self.per_algorithm_results.get(algo_key)
            if data and data["metrics"]:
                metrics = data["metrics"]
                x_vals = list(range(1, len(metrics) + 1))
                
                # Fetch metric value
                if trend_type == "time":
                    y_vals = [m["time_ms"] for m in metrics]
                    label = f"{data['label']} Speed"
                elif trend_type == "reduction":
                    y_vals = [m["reduction_percent"] for m in metrics]
                    label = f"{data['label']} Reduction %"
                else: # ratio
                    y_vals = [(m["original_size"] / m["compressed_size"] if m["compressed_size"] > 0 else 1.0) for m in metrics]
                    label = f"{data['label']} Ratio"
                    
                # Plot line & fill area
                color = algo_colors[algo_key]
                ax.plot(x_vals, y_vals, label=label, color=color, linewidth=2, marker="o", markersize=4)
                ax.fill_between(x_vals, y_vals, color=color, alpha=0.1)
                lines_drawn += 1
                
        if lines_drawn == 0:
            plt.close(fig)
            return
            
        # Customize labels & legend
        ax.tick_params(colors=text_color)
        ax.spines['bottom'].set_color(grid_color)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_color(grid_color)
        ax.yaxis.grid(True, linestyle=":", alpha=0.5, color=grid_color)
        ax.xaxis.grid(True, linestyle=":", alpha=0.5, color=grid_color)
        
        ax.set_xlabel("Dataset File Index", color=text_color, fontsize=10)
        
        title_map = {
            "time": "Processing Time Trend (ms)",
            "reduction": "Size Reduction Trend (%)",
            "ratio": "Compression Ratio Trend (x)"
        }
        ax.set_title(title_map[trend_type], fontsize=12, fontweight="bold", color=text_color, pad=15)
        
        legend = ax.legend(facecolor=bg_hex, edgecolor=grid_color, framealpha=0.8)
        if legend:
            for text in legend.get_texts():
                text.set_color(text_color)
                
        plt.tight_layout()
        
        # Save and draw
        chart_dir = Path("outputs") / "charts"
        chart_dir.mkdir(parents=True, exist_ok=True)
        img_path = chart_dir / f"temp_trend_{trend_type}.png"
        fig.savefig(str(img_path), dpi=100, bbox_inches="tight")
        plt.close(fig)
        
        self._display_chart_canvas(self.trend_canvas, img_path)

    # =========================================================================
    # TAB 6: Detail Berkas (FILE METADATA VIEWER)
    # =========================================================================
    def _build_details_tab(self):
        """Construct Tab 6 layout showing file properties and compress comparisons."""
        # Split pane: Left file selector dropdown, right details grid
        self.details_tab.grid_columnconfigure(0, weight=1)
        self.details_tab.grid_columnconfigure(1, weight=2)
        
        # Left Panel (File selector)
        left_side = ctk.CTkFrame(self.details_tab, fg_color="transparent")
        left_side.grid(row=0, column=0, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
        
        lbl_sel = ctk.CTkLabel(
            left_side,
            text="Pilih File Dataset:",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1], weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl_sel.pack(anchor="w", pady=(0, 5))
        
        self.file_details_menu_var = ctk.StringVar(value="None selected")
        self.file_details_menu = ctk.CTkOptionMenu(
            left_side,
            variable=self.file_details_menu_var,
            values=["None selected"],
            command=self._on_details_file_changed,
            height=36,
            fg_color=("#F1F5F9", "#1F2937"),
            button_color=("#E5E7EB", "#1F2937"),
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_ACCENT,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=CONTROL_RADIUS
        )
        self.file_details_menu.pack(fill="x")
        
        # Info Box Original File properties
        self.orig_details_box = ctk.CTkFrame(
            left_side,
            fg_color=BG_PRIMARY,
            corner_radius=CONTROL_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.orig_details_box.pack(fill="both", expand=True, pady=(15, 0))
        
        # Right Panel (Algorithmic outputs details grid)
        self.right_side = ctk.CTkFrame(self.details_tab, fg_color="transparent")
        self.right_side.grid(row=0, column=1, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
        
        self.details_table_container = ctk.CTkFrame(
            self.right_side,
            fg_color=BG_PRIMARY,
            corner_radius=BORDER_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.details_table_container.pack(fill="both", expand=True)
        
        # Populate original details panel
        self._populate_orig_details_card(None)
        
        # Populate right side grid template
        self._populate_comp_details_grid(None)

    def _on_details_file_changed(self, filename):
        """Update properties labels once file is changed in selector dropdown."""
        # Find matching metrics
        metrics = [m for m in self.all_metrics_data if m["file"] == filename]
        
        # Populate
        self._populate_orig_details_card(metrics[0] if metrics else None)
        self._populate_comp_details_grid(metrics)

    def _populate_orig_details_card(self, metric):
        """Clear and rebuild left statistics properties display card."""
        for widget in self.orig_details_box.winfo_children():
            widget.destroy()
            
        t_lbl = ctk.CTkLabel(
            self.orig_details_box,
            text="Original File Info",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        t_lbl.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 10))
        
        if not metric:
            ctk.CTkLabel(
                self.orig_details_box,
                text="No file statistics available.",
                font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
                text_color=TEXT_SECONDARY
            ).pack(anchor="w", padx=PADDING_NORMAL)
            return
            
        # Display rows
        props = [
            ("File Name", metric["file"]),
            ("Dimensions", metric["resolution"]),
            ("File Size", self._format_bytes(metric["original_size"])),
        ]
        
        for k, v in props:
            row = ctk.CTkFrame(self.orig_details_box, fg_color="transparent")
            row.pack(fill="x", padx=PADDING_NORMAL, pady=4)
            
            ctk.CTkLabel(
                row,
                text=f"{k}:",
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"),
                text_color=TEXT_SECONDARY,
                width=100,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=str(v),
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
                text_color=TEXT_PRIMARY
            ).pack(side="left")

    def _populate_comp_details_grid(self, metrics_list):
        """Clear and rebuild right grid panel comparing algorithm compression rows."""
        for widget in self.details_table_container.winfo_children():
            widget.destroy()
            
        t_lbl = ctk.CTkLabel(
            self.details_table_container,
            text="Compression Performance by Algorithm",
            font=ctk.CTkFont(family=FONT_HEADING[0], size=FONT_HEADING[1] + 1, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        t_lbl.pack(anchor="w", padx=PADDING_NORMAL, pady=(PADDING_NORMAL, 10))
        
        if not metrics_list:
            ctk.CTkLabel(
                self.details_table_container,
                text="No compression details run yet.",
                font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
                text_color=TEXT_SECONDARY
            ).pack(anchor="w", padx=PADDING_NORMAL)
            return
            
        # Draw table headers
        hdr = ctk.CTkFrame(self.details_table_container, fg_color="transparent")
        hdr.pack(fill="x", padx=PADDING_NORMAL, pady=2)
        
        headers = [("Algorithm", 140), ("Size", 100), ("Reduction", 100), ("Ratio", 70), ("Time (ms)", 90), ("Status", 80)]
        for label, w in headers:
            ctk.CTkLabel(
                hdr,
                text=label,
                font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] - 1, weight="bold"),
                text_color=TEXT_SECONDARY,
                width=w,
                anchor="w" if label == "Algorithm" else "center"
            ).pack(side="left")
            
        # Draw separators
        sep = ctk.CTkFrame(self.details_table_container, fg_color=BORDER_COLOR[1], height=1)
        sep.pack(fill="x", padx=PADDING_NORMAL, pady=5)
        
        # Populate each algorithm row
        for m in metrics_list:
            row = ctk.CTkFrame(self.details_table_container, fg_color="transparent")
            row.pack(fill="x", padx=PADDING_NORMAL, pady=4)
            
            orig_sz = m["original_size"]
            comp_sz = m["compressed_size"]
            ratio = orig_sz / comp_sz if comp_sz > 0 else 1.0
            
            lbl_algo = ctk.CTkLabel(row, text=m["algorithm"], font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]), text_color=TEXT_PRIMARY, width=140, anchor="w")
            lbl_algo.pack(side="left")
            
            lbl_sz = ctk.CTkLabel(row, text=self._format_bytes(comp_sz), font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]), text_color=TEXT_PRIMARY, width=100)
            lbl_sz.pack(side="left")
            
            lbl_red = ctk.CTkLabel(row, text=f"{m['reduction_percent']:.2f}%", font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1], weight="bold"), text_color=SUCCESS_COLOR, width=100)
            lbl_red.pack(side="left")
            
            lbl_ratio = ctk.CTkLabel(row, text=f"{ratio:.2f}x", font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]), text_color=TEXT_PRIMARY, width=70)
            lbl_ratio.pack(side="left")
            
            lbl_time = ctk.CTkLabel(row, text=f"{m['time_ms']:.2f}", font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]), text_color=TEXT_PRIMARY, width=90)
            lbl_time.pack(side="left")
            
            status_color = SUCCESS_COLOR if m["status"] == "SUCCESS" else ERROR_COLOR
            lbl_status = ctk.CTkLabel(row, text=m["status"], font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1] - 2, weight="bold"), text_color="#ffffff", fg_color=status_color[1], corner_radius=4, width=80)
            lbl_status.pack(side="left")

    def populate_details_menu(self, files_list):
        """Build entries list for details option menu."""
        if not files_list:
            self.file_details_menu.configure(values=["None selected"])
            self.file_details_menu_var.set("None selected")
            return
            
        names = [Path(f).name for f in files_list]
        self.file_details_menu.configure(values=names)
        self.file_details_menu_var.set(names[0])
        self._on_details_file_changed(names[0])

    # =========================================================================
    # CORE INTERACTION OVERLOADS
    # =========================================================================
    def reset(self):
        """Flush table listings and reset stat panel variables."""
        self.all_metrics_data = []
        self.per_algorithm_results = None
        self.winners = None
        self.clear_all()
        self.export_btn.configure(state="disabled")
        
        self.avg_reduction_var.set("-")
        self.best_reduction_var.set("-")
        self.fastest_algo_var.set("-")
        self.slowest_algo_var.set("-")
        self.avg_time_var.set("-")
        self.total_processed_var.set("-")
        
        self.chart_canvas.configure(image=None, text="[ Selesai kompresi untuk melihat visualisasi ]")
        self.trend_canvas.configure(image=None, text="[ Selesai kompresi untuk melihat tren grafik performa ]")
        
        self.file_details_menu.configure(values=["None selected"])
        self.file_details_menu_var.set("None selected")
        self._populate_orig_details_card(None)
        self._populate_comp_details_grid(None)
        
        for item in self.ranking_tree.get_children():
            self.ranking_tree.delete(item)

    def clear_all(self):
        """Purge rows inside metrics treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_metric(self, metric):
        """Insert metric row item, and refresh filter sorted listings."""
        self.all_metrics_data.append(metric)
        self._refresh_table()
        self._update_comparison_stats()
        
        # update details dropdown names
        all_unique_files = list(dict.fromkeys(m["file"] for m in self.all_metrics_data))
        self.file_details_menu.configure(values=all_unique_files)
        # Select active if first item
        if len(all_unique_files) == 1:
            self.file_details_menu_var.set(all_unique_files[0])
            self._on_details_file_changed(all_unique_files[0])

    def set_summary(self, summary):
        """Update summary footer status line."""
        cancelled = "Yes" if summary.get("cancelled", False) else "No"
        self.summary_var.set(
            "Completed: "
            f"{summary.get('completed', 0)} | Failed: {summary.get('failed', 0)} | "
            f"Cancelled: {cancelled} | "
            f"Avg Reduction: {summary.get('avg_reduction', 0):.2f}% | "
            f"Avg Time: {summary.get('avg_time_ms', 0):.2f} ms"
        )

    def show_comparison(self, per_algorithm, winners):
        """Consolidate comparison reports details, redraw tables, charts and render ranks."""
        self.per_algorithm_results = per_algorithm
        self.winners = winners
        
        # Build individual flat metric rows
        self.all_metrics_data = []
        for algo, data in per_algorithm.items():
            for m in data["metrics"]:
                self.all_metrics_data.append(m)
                
        self._refresh_table()
        self._update_comparison_stats()
        self._update_ranking_table()
        
        # Generate and draw charts
        self._render_matplotlib_charts()
        self._render_trend_charts()
        
        # Switch tab view
        self.notebook.set("Ringkasan Metrik")

    def show_chart(self, reduction_path, time_path):
        """Dummies to prevent legacy call errors from app.py."""
        # Charts are drawn dynamically from results dictionaries in memory
        pass

    def clear_comparison(self):
        """Legacy compatibility wrapper."""
        self.reset()

    def _format_bytes(self, value):
        """Format sizes."""
        if value <= 0:
            return "-"
        if value < 1024 * 1024:
            return f"{value / 1024:.2f} KB"
        return f"{value / (1024 * 1024):.2f} MB"
