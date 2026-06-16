"""
Logging Utility Module
PNG Compression Comparison System
MILESTONE 8 — Logging & Error Handling

Log format:
YYYY-MM-DD HH:MM:SS | LEVEL | event | details

Events:
app_start, dataset_loaded, compression_started, compression_finished,
compression_cancelled, export_success, export_failed, error, session_log
"""

from datetime import datetime
from pathlib import Path


LOGS_DIR = Path("logs")
APP_LOG = LOGS_DIR / "app.log"


class Logger:
    """Application logger — writes structured events to logs/app.log
    and per-session summary files to logs/session_YYYYMMDD_HHMMSS.log.

    All file operations are wrapped in try/except so that logging
    failures never crash the application.
    """

    def __init__(self):
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
        except (FileNotFoundError, PermissionError, OSError, RuntimeError):
            pass  # Non-critical — app runs without file logging

    # ------------------------------------------------------------------
    # Low-level write
    # ------------------------------------------------------------------

    def _write(self, level: str, event: str, details: str = "") -> None:
        """Append one line to app.log. Silently ignore write failures."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = f"{timestamp} | {level} | {event} | {details}\n"
            with APP_LOG.open("a", encoding="utf-8") as f:
                f.write(line)
        except (FileNotFoundError, PermissionError, OSError, RuntimeError):
            pass  # Non-critical — don't crash the app over a log write

    # ------------------------------------------------------------------
    # Level-based helpers
    # ------------------------------------------------------------------

    def info(self, event: str, details: str = "") -> None:
        """Log an INFO-level event."""
        self._write("INFO", event, details)

    def warn(self, event: str, details: str = "") -> None:
        """Log a WARN-level event."""
        self._write("WARN", event, details)

    def error(self, event: str, details: str = "") -> None:
        """Log an ERROR-level event."""
        self._write("ERROR", event, details)

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------

    def app_start(self) -> None:
        """Log application startup."""
        self.info("app_start", "PNG Compression Comparison System started")

    def dataset_loaded(self, path: str, count: int, valid: bool) -> None:
        """Log dataset folder load."""
        self.info(
            "dataset_loaded",
            f"path={path} count={count} valid={'yes' if valid else 'no'}",
        )

    def compression_started(self, algorithm: str, total_files: int) -> None:
        """Log compression batch start."""
        self.info(
            "compression_started",
            f"algorithm={algorithm} total_files={total_files}",
        )

    def compression_finished(
        self, completed: int, failed: int,
        avg_reduction: float, avg_time_ms: float,
    ) -> None:
        """Log successful batch completion."""
        self.info(
            "compression_finished",
            f"completed={completed} failed={failed} "
            f"avg_reduction={avg_reduction:.2f}% avg_time={avg_time_ms:.2f}ms",
        )

    def compression_cancelled(self, completed: int, failed: int) -> None:
        """Log user-cancelled batch."""
        self.warn(
            "compression_cancelled",
            f"completed={completed} failed={failed}",
        )

    def export_success(self, path: str) -> None:
        """Log successful CSV export."""
        self.info("export_success", f"path={path}")

    def export_failed(self, reason: str) -> None:
        """Log failed CSV export."""
        self.error("export_failed", f"reason={reason}")

    def log_exception(self, exc_type: str, message: str) -> None:
        """Log an unhandled or caught exception."""
        self.error("error", f"type={exc_type} message={message}")

    # ------------------------------------------------------------------
    # Session log
    # ------------------------------------------------------------------

    def write_session_log(
        self,
        dataset_path: str,
        algorithm: str,
        completed: int,
        failed: int,
        avg_reduction: float,
        avg_time_ms: float,
    ) -> None:
        """Write a per-session summary file and log its creation.
        Silently ignore write failures."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_path = LOGS_DIR / f"session_{timestamp}.log"

            with session_path.open("w", encoding="utf-8") as f:
                f.write(f"dataset={dataset_path}\n")
                f.write(f"algorithm={algorithm}\n")
                f.write(f"completed={completed}\n")
                f.write(f"failed={failed}\n")
                f.write(f"avg_reduction={avg_reduction:.4f}\n")
                f.write(f"avg_time_ms={avg_time_ms:.4f}\n")

            self.info("session_log", f"path={session_path}")
        except (FileNotFoundError, PermissionError, OSError, RuntimeError):
            pass  # Non-critical — don't crash the app over a session log
