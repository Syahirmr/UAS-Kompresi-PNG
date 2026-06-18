"""
CSV export utilities for compression metrics and comparison reports.
"""

import csv
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend to avoid GUI freezes
import matplotlib.pyplot as plt


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

COMPARISON_CSV_COLUMNS = [
    "algorithm",
    "files_processed",
    "avg_reduction",
    "avg_time_ms",
    "success",
    "failed",
    "score",
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


def _timestamp_ms():
    """Return a millisecond-precision timestamp string: YYYYMMDD_HHMMSS_mmm."""
    now = datetime.now()
    return f"{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond // 1000:03d}"


def _build_report_path(reports_dir):
    """Build a timestamped report path with millisecond precision."""
    timestamp = _timestamp_ms()
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


# -------------------------------------------------------------------------
# Comparison report export
# -------------------------------------------------------------------------


def export_comparison_csv(per_algorithm, winners, output_dir):
    """Export comparison results to a timestamped CSV file with scoring."""
    reports_dir = Path(output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    output_path = reports_dir / f"comparison_report_{_timestamp_ms()}.csv"

    # Compute scores for each algorithm
    scores = compute_ranking_scores(per_algorithm)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        # Header
        writer.writerow(COMPARISON_CSV_COLUMNS)

        # Per-algorithm rows (sorted by score descending)
        sorted_algos = sorted(
            per_algorithm.items(),
            key=lambda item: scores.get(item[0], 0),
            reverse=True,
        )
        for algo_key, data in sorted_algos:
            s = data["summary"]
            successful = sum(1 for m in data["metrics"] if m["status"] == "SUCCESS")
            failed_count = sum(1 for m in data["metrics"] if m["status"] == "FAILED")
            writer.writerow([
                data["label"],
                s["completed"],
                f"{s['avg_reduction']:.4f}",
                f"{s['avg_time_ms']:.4f}",
                successful,
                failed_count,
                f"{scores.get(algo_key, 0):.2f}",
            ])

        # Winners section
        writer.writerow([])
        writer.writerow(["=== WINNERS ==="])
        writer.writerow(["best_compression", winners.get("winner_reduction_label", "N/A")])
        writer.writerow(["best_compression_value", f"{winners.get('winner_reduction_value', 0):.4f}"])
        writer.writerow(["fastest", winners.get("winner_speed_label", "N/A")])
        writer.writerow(["fastest_value", f"{winners.get('winner_speed_value', 0):.4f}"])
        writer.writerow(["balanced", winners.get("winner_balanced_label", "N/A")])
        writer.writerow(["balanced_score", f"{winners.get('winner_balanced_value', 0):.2f}"])

    return output_path


def compute_ranking_scores(per_algorithm):
    """Compute a balanced ranking score (0-100) for each algorithm.

    Higher score = better overall performance.
    Formula: 50% reduction + 50% speed (normalized).
    """
    scores = {}
    reduction_values = {}
    time_values = {}

    for algo_key, data in per_algorithm.items():
        s = data["summary"]
        successful = [m for m in data["metrics"] if m["status"] == "SUCCESS"]
        if successful:
            reduction_values[algo_key] = s["avg_reduction"]
            time_values[algo_key] = s["avg_time_ms"]

    if not reduction_values:
        return scores

    max_reduction = max(reduction_values.values()) if reduction_values else 1
    min_time = min(time_values.values()) if time_values else 1

    for algo_key in reduction_values:
        red = reduction_values[algo_key]
        t = max(time_values[algo_key], 0.001)

        reduction_score = (red / max_reduction) * 50 if max_reduction > 0 else 0
        speed_score = (min_time / t) * 50 if min_time > 0 else 0
        scores[algo_key] = min(reduction_score + speed_score, 100)

    return scores


# -------------------------------------------------------------------------
# Comparison charts — timestamped, no overwrite (BUG-1 fix)
# -------------------------------------------------------------------------


def generate_reduction_chart(per_algorithm, output_dir):
    """Generate a bar chart for average reduction (%) with timestamp.

    Returns the path to the saved PNG file.
    """
    charts_dir = Path(output_dir)
    charts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = _timestamp_ms()
    output_path = charts_dir / f"reduction_chart_{timestamp}.png"

    labels = []
    values = []
    for algo_key in ["deflate", "zopfli", "oxipng"]:
        data = per_algorithm.get(algo_key)
        if data and data["metrics"]:
            s = data["summary"]
            labels.append(data["label"])
            values.append(s["avg_reduction"])

    fig, ax = plt.subplots(figsize=(7, 5))
    if not labels:
        ax.text(0.5, 0.5, "No comparison data available",
                ha="center", va="center", fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    else:
        colors = ["#0078d4", "#107c10", "#d83b01"]
        bars = ax.bar(labels, values, color=colors[:len(labels)], width=0.5)
        ax.set_title("Average Reduction (%)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Reduction (%)")
        ax.tick_params(axis="x", rotation=15)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    fig.savefig(str(output_path), dpi=100, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_time_chart(per_algorithm, output_dir):
    """Generate a bar chart for average time (ms) with timestamp.

    Returns the path to the saved PNG file.
    """
    charts_dir = Path(output_dir)
    charts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = _timestamp_ms()
    output_path = charts_dir / f"time_chart_{timestamp}.png"

    labels = []
    values = []
    for algo_key in ["deflate", "zopfli", "oxipng"]:
        data = per_algorithm.get(algo_key)
        if data and data["metrics"]:
            s = data["summary"]
            labels.append(data["label"])
            values.append(s["avg_time_ms"])

    fig, ax = plt.subplots(figsize=(7, 5))
    if not labels:
        ax.text(0.5, 0.5, "No comparison data available",
                ha="center", va="center", fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    else:
        colors = ["#0078d4", "#107c10", "#d83b01"]
        bars = ax.bar(labels, values, color=colors[:len(labels)], width=0.5)
        ax.set_title("Average Time (ms)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Time (ms)")
        ax.tick_params(axis="x", rotation=15)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    fig.savefig(str(output_path), dpi=100, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _find_best_worst(metrics):
    """Find the best and worst file from a metrics list."""
    successful = [m for m in metrics if m["status"] == "SUCCESS"]
    if not successful:
        return "-", "-"

    best = max(successful, key=lambda m: m["reduction_percent"])
    worst = min(successful, key=lambda m: m["reduction_percent"])
    return best["file"], worst["file"]
