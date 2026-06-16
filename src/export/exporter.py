"""
CSV export utilities for compression metrics.
"""

import csv
from datetime import datetime
from pathlib import Path


CSV_COLUMNS = [
    "file",
    "algorithm",
    "original_size_kb",
    "compressed_size_kb",
    "reduction_percent",
    "time_ms",
    "resolution",
    "status",
]


def export_metrics_csv(metrics, summary, output_dir):
    """Export metrics and summary to a timestamped CSV file."""
    reports_dir = Path(output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    output_path = _build_report_path(reports_dir)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for metric in metrics:
            writer.writerow(_format_metric_row(metric))

        writer.writerow({})
        writer.writerow({"file": "summary"})
        writer.writerow({"file": "completed", "algorithm": str(summary["completed"])})
        writer.writerow({"file": "failed", "algorithm": str(summary["failed"])})
        writer.writerow({"file": "cancelled", "algorithm": str(summary["cancelled"])})
        writer.writerow({"file": "avg_reduction", "algorithm": f"{summary['avg_reduction']:.4f}"})
        writer.writerow({"file": "avg_time_ms", "algorithm": f"{summary['avg_time_ms']:.4f}"})

    return output_path


def _build_report_path(reports_dir):
    """Build a timestamped report path without overwriting an existing file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = reports_dir / f"report_{timestamp}.csv"
    if not output_path.exists():
        return output_path

    counter = 1
    while True:
        candidate = reports_dir / f"report_{timestamp}_{counter}.csv"
        if not candidate.exists():
            return candidate
        counter += 1


def _format_metric_row(metric):
    """Convert one metrics object to a CSV row."""
    return {
        "file": metric["file"],
        "algorithm": metric["algorithm"],
        "original_size_kb": _bytes_to_kb(metric["original_size"]),
        "compressed_size_kb": _bytes_to_kb(metric["compressed_size"]),
        "reduction_percent": f"{metric['reduction_percent']:.4f}",
        "time_ms": f"{metric['time_ms']:.4f}",
        "resolution": metric["resolution"],
        "status": metric["status"],
    }


def _bytes_to_kb(value):
    """Convert bytes to kilobytes."""
    if value <= 0:
        return "0.0000"
    return f"{value / 1024:.4f}"
