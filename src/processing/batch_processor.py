"""
Batch processor for dataset compression.
"""

from pathlib import Path

from src.compression.compressor import compress_file


def process_dataset(files, algorithm, output_dir, progress_callback, cancel_check):
    """
    Compress all PNG files in a dataset sequentially.

    The active file is always completed before cancellation is applied.
    """
    total_files = len(files)
    results = []

    if total_files == 0:
        progress_callback(0, "Tidak ada file PNG untuk diproses.")
        return {
            "completed": 0,
            "failed": 0,
            "cancelled": False,
            "results": results,
        }

    progress_callback(0, f"Menyiapkan kompresi {total_files} file PNG...")

    cancelled = False
    for index, file_path in enumerate(files, start=1):
        if cancel_check():
            cancelled = True
            break

        input_file = Path(file_path)
        progress_callback(
            ((index - 1) / total_files) * 100,
            f"Memproses {index}/{total_files}: {input_file.name}",
        )

        result = compress_file(input_file, algorithm, output_dir)
        results.append(result)

        progress_callback(
            (index / total_files) * 100,
            _build_status_text(index, total_files, input_file.name, result),
        )

        if cancel_check():
            cancelled = True
            break

    completed = len(results)
    failed = sum(1 for result in results if not result["success"])

    if cancelled:
        progress_callback(
            (completed / total_files) * 100,
            f"Dibatalkan setelah {completed}/{total_files} file selesai.",
        )
    else:
        progress_callback(
            100,
            f"Selesai: {completed}/{total_files} file diproses.",
        )

    return {
        "completed": completed,
        "failed": failed,
        "cancelled": cancelled,
        "results": results,
    }


def _build_status_text(index, total_files, filename, result):
    """Build concise progress status text."""
    if result["success"]:
        return f"Selesai {index}/{total_files}: {filename}"

    return f"Gagal {index}/{total_files}: {filename} - {result['error']}"
