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
            "Algorithm",
            "Original Size",
            "Compressed Size",
            "Reduction %",
            "Time (ms)",
            "Status"
        )
        
        # Configure Treeview
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            height=6,
            show="headings",
            selectmode=tk.BROWSE
        )
        
        # Define column headings and widths
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
        
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert placeholder rows for each algorithm
        algorithms = ["Deflate Baseline", "Zopfli Deflate", "OxiPNG"]
        for algo in algorithms:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    algo,
                    "-",
                    "-",
                    "-",
                    "-",
                    "Waiting"
                )
            )
    
    def reset(self):
        """Reset metrics display to placeholder values."""
        placeholder_values = (
            "-",
            "-",
            "-",
            "-",
            "Waiting"
        )
        for item in self.tree.get_children():
            values = (self.tree.item(item, 'values')[0],) + placeholder_values
            self.tree.item(item, values=values)

    def clear_all(self):
        """Clear all placeholder rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)
