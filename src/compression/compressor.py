"""
Compression dispatcher for single PNG files.
"""

from pathlib import Path
import time

from src.compression.algorithms.deflate_runner import run_deflate
from src.compression.algorithms.oxipng_runner import run_oxipng
from src.compression.algorithms.zopfli_runner import run_zopfli
from src.utils.config import DEFLATE_TIMEOUT, OXIPNG_TIMEOUT, ZOPFLI_TIMEOUT, ZOPFLI_MAX_ITERATIONS


ALGORITHM_TIMEOUTS = {
    "deflate": DEFLATE_TIMEOUT,       # None = unlimited
    "deflate_baseline": DEFLATE_TIMEOUT,
    "zopfli": ZOPFLI_TIMEOUT,         # 60s from config
    "zopfli_deflate": ZOPFLI_TIMEOUT,
    "oxipng": OXIPNG_TIMEOUT,         # 120s from config
}

ALGORITHMS = {
    "deflate": run_deflate,
    "deflate_baseline": run_deflate,
    "zopfli": run_zopfli,
    "zopfli_deflate": run_zopfli,
    "oxipng": run_oxipng,
}


def compress_file(input_path, algorithm, output_dir, timeout=None, max_iterations=None):
    """
    Compress one PNG file with the selected algorithm.

    Args:
        input_path: Path to input PNG.
        algorithm: Algorithm key (e.g. "deflate", "zopfli", "oxipng").
        output_dir: Directory for output.
        timeout: Optional per-file timeout in seconds. Falls back to config default.
        max_iterations: Max iterations for Zopfli. Falls back to config default.

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

    algo_key = str(algorithm).lower()
    runner = ALGORITHMS.get(algo_key)
    if runner is None:
        return _build_result(
            success=False,
            input_size=input_size,
            output_size=0,
            time_ms=_elapsed_ms(started_at),
            output_path="",
            error=f"Algorithm tidak dikenal: {algorithm}",
        )

    # Resolve timeout: explicit > config default
    if timeout is None:
        timeout = ALGORITHM_TIMEOUTS.get(algo_key)
    if max_iterations is None:
        max_iterations = ZOPFLI_MAX_ITERATIONS

    kwargs = {}
    if algo_key in ("oxipng",):
        kwargs["timeout"] = timeout
    elif algo_key in ("zopfli", "zopfli_deflate"):
        kwargs["timeout"] = timeout
        kwargs["max_iterations"] = max_iterations

    try:
        output_folder.mkdir(parents=True, exist_ok=True)
        runner_result = runner(input_file, output_folder, **kwargs)

        # Runner may return:
        #   - Path (legacy success, e.g. deflate_runner)
        #   - dict with success=True|False (oxipng, zopfli)
        if isinstance(runner_result, dict):
            output_path = str(runner_result.get("output_path", ""))
            if runner_result.get("success"):
                output_size = Path(output_path).stat().st_size
                success = True
            else:
                error = runner_result.get("error", "Unknown error")
        else:
            output_path = str(runner_result)
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
