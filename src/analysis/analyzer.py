"""
Compression metrics analyzer.
"""

from pathlib import Path

from PIL import Image


def build_metric(file_path, algorithm, compression_result):
    """Build one GUI-ready metrics object for a compressed file."""
    input_file = Path(file_path)
    original_size = compression_result.get("input_size", 0)
    compressed_size = compression_result.get("output_size", 0)
    success = compression_result.get("success", False)

    reduction_percent = 0
    if success and original_size > 0:
        reduction_percent = ((original_size - compressed_size) / original_size) * 100

    return {
        "file": input_file.name,
        "algorithm": _format_algorithm(algorithm),
        "original_size": original_size,
        "compressed_size": compressed_size,
        "reduction_percent": reduction_percent,
        "time_ms": compression_result.get("time_ms", 0),
        "resolution": _read_resolution(input_file),
        "status": "SUCCESS" if success else "FAILED",
    }


def summarize_metrics(metrics, cancelled=False):
    """Compute summary values for a metrics collection."""
    completed = len(metrics)
    failed = sum(1 for metric in metrics if metric["status"] == "FAILED")
    successful_metrics = [
        metric for metric in metrics
        if metric["status"] == "SUCCESS"
    ]

    avg_reduction = _average(
        metric["reduction_percent"] for metric in successful_metrics
    )
    avg_time = _average(metric["time_ms"] for metric in metrics)

    return {
        "completed": completed,
        "failed": failed,
        "cancelled": cancelled,
        "avg_reduction": avg_reduction,
        "avg_time_ms": avg_time,
    }


def _read_resolution(input_file):
    """Read image resolution as WIDTHxHEIGHT."""
    try:
        with Image.open(input_file) as image:
            return f"{image.width}x{image.height}"
    except OSError:
        return "-"


def _average(values):
    """Calculate average from any iterable of numeric values."""
    values = list(values)
    if not values:
        return 0
    return sum(values) / len(values)


def _format_algorithm(algorithm):
    """Format internal algorithm name for display."""
    labels = {
        "deflate": "Deflate Baseline",
        "deflate_baseline": "Deflate Baseline",
        "zopfli": "Zopfli Deflate",
        "zopfli_deflate": "Zopfli Deflate",
        "oxipng": "OxiPNG",
    }
    return labels.get(str(algorithm).lower(), str(algorithm))
