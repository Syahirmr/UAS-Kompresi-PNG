"""
Metrics Panel Component
Display compression metrics for algorithms
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import (
    FONT_NORMAL, FONT_HEADING, BG_ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY,
    PADDING_NORMAL, PADDING_SMALL
)


class MetricsPanelComponent(ttk.LabelFrame):
    """Display compression metrics in table format."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Compression Metrics", padding=PADDING_NORMAL)
        self.pack(fill=tk.BOTH, expand=True, padx=PADDING_NORMAL, pady=PADDING_SMALL)
        
        # Create Treeview for metrics table
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
        
        # Configure Treeview
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            height=8,
            show="headings",
            selectmode=tk.BROWSE
        )
        
        # Define column headings and widths
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
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and scrollbar
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Summary section
        self.summary_var = tk.StringVar(
            value="Completed: 0 | Failed: 0 | Cancelled: No | Avg Reduction: 0.00% | Avg Time: 0.00 ms"
        )
        summary_label = tk.Label(
            self,
            textvariable=self.summary_var,
            font=FONT_NORMAL,
            fg=TEXT_PRIMARY,
            bg=BG_ACCENT,
            anchor=tk.W,
            justify=tk.LEFT
        )
        summary_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(PADDING_NORMAL, 0))
    
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

    def _format_bytes(self, value):
        """Format bytes as KB for display."""
        if value <= 0:
            return "-"
        return f"{value / 1024:.2f} KB"
