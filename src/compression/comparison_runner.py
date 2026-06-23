"""
Comparison runner — runs all 3 compression algorithms on a dataset.

Returns combined metrics, per-algorithm summaries, and winner analysis.
"""

from pathlib import Path
import time

from src.analysis.analyzer import build_metric, summarize_metrics
from src.compression.compressor import compress_file
from src.utils.config import COMPARISON_ETA_WINDOW

ALGORITHMS = ["deflate", "zopfli", "oxipng"]

ALGORITHM_LABELS = {
    "deflate": "Deflate Baseline",
    "zopfli": "Zopfli Deflate",
    "oxipng": "OxiPNG",
}

# Per-algorithm timeouts (seconds) — used by comparison runner
ALGORITHM_TIMEOUTS = {
    "deflate": None,    # unlimited
    "zopfli": 60,       # 60s per file
    "oxipng": 120,      # 120s per file
}


def _format_eta(seconds):
    """Format seconds as a human-readable ETA string."""
    if seconds is None or seconds < 0:
        return "--"
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}m {secs:02d}s"


def run_comparison(files, output_dir, progress_callback, cancel_check):
    """Run all 3 algorithms on the dataset sequentially.

    Progress reports total work as len(files) × 3 steps.
    Returns a dict with keys: per_algorithm, all_metrics, summary, winners.
    """
    total_files = len(files)
    num_algos = len(ALGORITHMS)
    total_steps = total_files * num_algos
    steps_done = 0
    all_metrics = []
    per_algorithm_results = {}
    cancelled = False

    # For ETA calculation
    file_times = []   # rolling window of per-file times
    started_at = time.time()

    if total_files == 0:
        progress_callback(0, "Tidak ada file PNG untuk diproses.", None)
        return _empty_comparison()

    progress_callback(
        0,
        f"Comparison: {total_files} file × {num_algos} algoritma = {total_steps} task",
        None,
    )

    for algo_idx, algo in enumerate(ALGORITHMS):
        if cancel_check():
            cancelled = True
            break

        algo_output_dir = output_dir / algo
        algo_metrics = []
        algo_results = []

        for idx, file_path in enumerate(files, start=1):
            if cancel_check():
                cancelled = True
                break

            input_file = Path(file_path)
            step = steps_done + idx
            pct = min((step / total_steps) * 100, 99)

            # Build progress text with algorithm count, file position, and optional ETA
            algo_pct = ((idx - 1) / total_files) * 100 if total_files > 0 else 0
            progress_text = (
                f"[Algorithm {algo_idx + 1}/{num_algos}] "
                f"{ALGORITHM_LABELS[algo]} | "
                f"File {idx}/{total_files} ({algo_pct:.0f}%)"
            )

            # Compute ETA from rolling average
            if file_times:
                avg_time = sum(file_times) / len(file_times)
                remaining_steps = total_steps - step
                eta_seconds = remaining_steps * avg_time
                progress_text += f" | ETA: {_format_eta(eta_seconds)}"

            progress_callback(pct, progress_text, None)

            file_start = time.time()
            result = compress_file(input_file, algo, algo_output_dir)
            elapsed = time.time() - file_start

            # Track per-file time for ETA (rolling window)
            file_times.append(elapsed)
            if len(file_times) > COMPARISON_ETA_WINDOW:
                file_times.pop(0)

            result["input_path"] = str(input_file)
            algo_results.append(result)
            metric = build_metric(input_file, algo, result)
            algo_metrics.append(metric)
            all_metrics.append(metric)

            # Send progress update with metric after compression finishes
            pct_after = min(((steps_done + idx) / total_steps) * 100, 100)
            progress_callback(pct_after, progress_text, metric)

        steps_done += len(files)

        if algo_metrics:
            summary = summarize_metrics(algo_metrics, cancelled=cancelled)
        else:
            summary = {"completed": 0, "failed": len(files), "cancelled": cancelled,
                       "avg_reduction": 0, "avg_time_ms": 0}

        per_algorithm_results[algo] = {
            "algorithm": algo,
            "label": ALGORITHM_LABELS[algo],
            "results": algo_results,
            "metrics": algo_metrics,
            "summary": summary,
        }

        if cancelled:
            break

    # Compute winners across successfully completed algorithms
    winners = _compute_winners(per_algorithm_results, cancelled)

    overall_summary = _compute_overall_summary(per_algorithm_results)

    progress_callback(
        100,
        _build_comparison_done_text(per_algorithm_results, cancelled),
        None,
    )

    return {
        "per_algorithm": per_algorithm_results,
        "all_metrics": all_metrics,
        "summary": overall_summary,
        "winners": winners,
        "cancelled": cancelled,
        "total_time_seconds": time.time() - started_at,
    }


def _compute_score(reduction, time_ms, max_reduction, min_time):
    """Compute a balanced score (0-100) for ranking.

    Combines reduction and speed:
    - reduction_score: normalized 0-50 (higher reduction = better)
    - speed_score: normalized 0-50 (lower time = better)
    """
    if max_reduction <= 0:
        reduction_score = 0
    else:
        reduction_score = (reduction / max_reduction) * 50

    if min_time <= 0 or time_ms <= 0:
        speed_score = 25  # neutral score when no data
    else:
        # Invert: lower time = higher score (capped at 50)
        speed_score = (min_time / max(time_ms, 0.001)) * 50

    return min(reduction_score + speed_score, 100)


def _compute_winners(per_algorithm_results, cancelled):
    """Determine best compression, fastest, and balanced algorithms."""
    reduction_scores = {}
    speed_scores = {}
    algo_summaries = {}

    for algo, data in per_algorithm_results.items():
        s = data["summary"]
        # Only consider algorithms with at least 1 successful metric
        successful = [m for m in data["metrics"] if m["status"] == "SUCCESS"]
        if successful:
            reduction_scores[algo] = s["avg_reduction"]
            speed_scores[algo] = s["avg_time_ms"]
            algo_summaries[algo] = s

    winner_reduction = max(reduction_scores, key=reduction_scores.get) if reduction_scores else None
    winner_speed = min(speed_scores, key=speed_scores.get) if speed_scores else None

    # Determine balanced winner (best average of reduction + speed scores)
    balanced_winner = None
    balanced_score = -1
    if algo_summaries:
        max_reduction = max(reduction_scores.values()) if reduction_scores else 1
        min_time = min(speed_scores.values()) if speed_scores else 1
        for algo_key, summary in algo_summaries.items():
            score = _compute_score(
                summary["avg_reduction"],
                summary["avg_time_ms"],
                max_reduction,
                min_time,
            )
            if score > balanced_score:
                balanced_score = score
                balanced_winner = algo_key

    return {
        "winner_reduction_algorithm": winner_reduction,
        "winner_reduction_label": ALGORITHM_LABELS.get(winner_reduction, "N/A") if winner_reduction else "N/A",
        "winner_reduction_value": reduction_scores.get(winner_reduction, 0),
        "winner_speed_algorithm": winner_speed,
        "winner_speed_label": ALGORITHM_LABELS.get(winner_speed, "N/A") if winner_speed else "N/A",
        "winner_speed_value": speed_scores.get(winner_speed, 0),
        "winner_balanced_algorithm": balanced_winner,
        "winner_balanced_label": ALGORITHM_LABELS.get(balanced_winner, "N/A") if balanced_winner else "N/A",
        "winner_balanced_value": balanced_score,
    }


def _compute_overall_summary(per_algorithm_results):
    """Build summary dict for all algorithms combined."""
    total_completed = 0
    total_failed = 0
    for data in per_algorithm_results.values():
        total_completed += data["summary"]["completed"]
        total_failed += data["summary"]["failed"]

    return {
        "completed": total_completed,
        "failed": total_failed,
    }


def _build_comparison_done_text(per_algorithm_results, cancelled):
    """Build status text for completion."""
    parts = []
    for algo, data in per_algorithm_results.items():
        s = data["summary"]
        parts.append(f"{ALGORITHM_LABELS[algo]}: {s['completed']} ok, {s['failed']} fail")
    text = " | ".join(parts)
    if cancelled:
        return f"Comparison cancelled. {text}"
    return f"Comparison complete. {text}"


def _empty_comparison():
    """Return empty comparison result."""
    return {
        "per_algorithm": {},
        "all_metrics": [],
        "summary": {"completed": 0, "failed": 0},
        "winners": {
            "winner_reduction_algorithm": None,
            "winner_reduction_label": "N/A",
            "winner_reduction_value": 0,
            "winner_speed_algorithm": None,
            "winner_speed_label": "N/A",
            "winner_speed_value": 0,
            "winner_balanced_algorithm": None,
            "winner_balanced_label": "N/A",
            "winner_balanced_value": 0,
        },
        "cancelled": False,
        "total_time_seconds": 0,
    }
