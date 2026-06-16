"""
Batch processor for dataset compression.
"""

from pathlib import Path

from src.analysis.analyzer import build_metric, summarize_metrics
from src.compression.compressor import compress_file


def process_dataset(files, algorithm, output_dir, progress_callback, cancel_check):
    """
    Compress all PNG files in a dataset sequentially.

    The active file is always completed before cancellation is applied.
    """
    total_files = len(files)
    results = []
    metrics = []

    if total_files == 0:
        progress_callback(0, "Tidak ada file PNG untuk diproses.", None)
        return {
            "completed": 0,
            "failed": 0,
            "cancelled": False,
            "results": results,
            "metrics": metrics,
            "summary": summarize_metrics(metrics),
        }

    progress_callback(0, f"Menyiapkan kompresi {total_files} file PNG...", None)

    cancelled = False
    for index, file_path in enumerate(files, start=1):
        if cancel_check():
            cancelled = True
            break

        input_file = Path(file_path)
        progress_callback(
            ((index - 1) / total_files) * 100,
            f"Memproses {index}/{total_files}: {input_file.name}",
            None,
        )

        result = compress_file(input_file, algorithm, output_dir)
        results.append(result)
        metric = build_metric(input_file, algorithm, result)
        metrics.append(metric)

        progress_callback(
            (index / total_files) * 100,
            _build_status_text(index, total_files, input_file.name, result),
            metric,
        )

        if cancel_check():
            cancelled = True
            break

    completed = len(results)
    failed = sum(1 for result in results if not result["success"])
    summary = summarize_metrics(metrics, cancelled=cancelled)

    if cancelled:
        progress_callback(
            (completed / total_files) * 100,
            f"Dibatalkan setelah {completed}/{total_files} file selesai.",
            None,
        )
    else:
        progress_callback(
            100,
            f"Selesai: {completed}/{total_files} file diproses.",
            None,
        )

    return {
        "completed": completed,
        "failed": failed,
        "cancelled": cancelled,
        "results": results,
        "metrics": metrics,
        "summary": summary,
    }


def _build_status_text(index, total_files, filename, result):
    """Build concise progress status text."""
    if result["success"]:
        return f"Selesai {index}/{total_files}: {filename}"

    return f"Gagal {index}/{total_files}: {filename} - {result['error']}"
