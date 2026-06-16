"""
Compression dispatcher for single PNG files.
"""

from pathlib import Path
import time

from src.compression.algorithms.deflate_runner import run_deflate
from src.compression.algorithms.oxipng_runner import run_oxipng
from src.compression.algorithms.zopfli_runner import run_zopfli


ALGORITHMS = {
    "deflate": run_deflate,
    "deflate_baseline": run_deflate,
    "zopfli": run_zopfli,
    "zopfli_deflate": run_zopfli,
    "oxipng": run_oxipng,
}


def compress_file(input_path, algorithm, output_dir):
    """
    Compress one PNG file with the selected algorithm.

    Returns a dictionary with success status, sizes, duration, output path,
    and a graceful error message when compression fails.
    """
    started_at = time.perf_counter()
    input_file = Path(input_path)
    output_folder = Path(output_dir)
    output_path = ""
    error = None
    success = False
    output_size = 0

    try:
        input_size = input_file.stat().st_size
    except OSError as exc:
        return _build_result(
            success=False,
            input_size=0,
            output_size=0,
            time_ms=_elapsed_ms(started_at),
            output_path="",
            error=f"Input file tidak valid: {exc}",
        )

    runner = ALGORITHMS.get(str(algorithm).lower())
    if runner is None:
        return _build_result(
            success=False,
            input_size=input_size,
            output_size=0,
            time_ms=_elapsed_ms(started_at),
            output_path="",
            error=f"Algorithm tidak dikenal: {algorithm}",
        )

    try:
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = str(runner(input_file, output_folder))
        output_size = Path(output_path).stat().st_size
        success = True
    except Exception as exc:
        error = str(exc)

    return _build_result(
        success=success,
        input_size=input_size,
        output_size=output_size,
        time_ms=_elapsed_ms(started_at),
        output_path=output_path if success else "",
        error=error,
    )


def _elapsed_ms(started_at):
    """Return elapsed time in milliseconds."""
    return (time.perf_counter() - started_at) * 1000


def _build_result(success, input_size, output_size, time_ms, output_path, error):
    """Build compression result payload."""
    return {
        "success": success,
        "input_size": input_size,
        "output_size": output_size,
        "time_ms": time_ms,
        "output_path": output_path,
        "error": error,
    }
