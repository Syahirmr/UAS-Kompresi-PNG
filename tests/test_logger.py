"""
Unit tests for src.utils.logger
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.utils.logger import Logger, LOGS_DIR


class TestLogger(unittest.TestCase):
    """Tests for Logger class — verifies logging does not crash."""

    def setUp(self):
        # Use a temporary directory to isolate logs
        self._orig_logs_dir = LOGS_DIR
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_logger(self):
        """Create a logger whose LOGS_DIR points at the temporary directory."""
        logger = Logger()
        # Override with tmpdir so test runs are isolated
        import src.utils.logger as logger_mod
        logger_mod.LOGS_DIR = self.tmpdir
        logger_mod.APP_LOG = self.tmpdir / "app.log"
        return Logger()

    # ---------- all events no-crash ----------

    def test_app_start(self):
        logger = self._make_logger()
        logger.app_start()  # should not raise

    def test_dataset_loaded(self):
        logger = self._make_logger()
        logger.dataset_loaded("/test/path", 10, True)

    def test_compression_started(self):
        logger = self._make_logger()
        logger.compression_started("deflate", 10)

    def test_compression_finished(self):
        logger = self._make_logger()
        logger.compression_finished(10, 0, 45.5, 120.3)

    def test_compression_cancelled(self):
        logger = self._make_logger()
        logger.compression_cancelled(5, 1)

    def test_export_success(self):
        logger = self._make_logger()
        logger.export_success("/path/to/report.csv")

    def test_export_failed(self):
        logger = self._make_logger()
        logger.export_failed("disk full")

    def test_log_exception(self):
        logger = self._make_logger()
        logger.log_exception("ValueError", "bad value")

    def test_info_level(self):
        logger = self._make_logger()
        logger.info("test_event", "some details")

    def test_warn_level(self):
        logger = self._make_logger()
        logger.warn("test_warn", "warning details")

    def test_error_level(self):
        logger = self._make_logger()
        logger.error("test_error", "error details")

    # ---------- session log ----------

    def test_write_session_log(self):
        logger = self._make_logger()
        logger.write_session_log(
            dataset_path="/test/data",
            algorithm="deflate",
            completed=10,
            failed=1,
            avg_reduction=45.5,
            avg_time_ms=120.3,
        )
        # Verify session file was created
        session_files = list(self.tmpdir.glob("session_*.log"))
        self.assertGreaterEqual(len(session_files), 1)

    def test_session_log_contains_fields(self):
        logger = self._make_logger()
        logger.write_session_log(
            dataset_path="/test/data",
            algorithm="zopfli",
            completed=5,
            failed=0,
            avg_reduction=60.0,
            avg_time_ms=500.0,
        )
        session_files = sorted(self.tmpdir.glob("session_*.log"))
        content = session_files[-1].read_text(encoding="utf-8")
        self.assertIn("dataset=/test/data", content)
        self.assertIn("algorithm=zopfli", content)
        self.assertIn("completed=5", content)

    # ---------- no-crash under error conditions ----------

    def test_logger_no_crash_on_permission_error(self):
        """Logger should not crash even when writing is impossible."""
        # Point to a read-only directory (make it not writable after creation)
        restricted = self.tmpdir / "restricted"
        restricted.mkdir(exist_ok=True)
        try:
            restricted.chmod(0o444)  # read-only
        except PermissionError:
            self.skipTest("Cannot set read-only on this platform")

        import src.utils.logger as logger_mod
        original = logger_mod.LOGS_DIR, logger_mod.APP_LOG
        logger_mod.LOGS_DIR = restricted
        logger_mod.APP_LOG = restricted / "app.log"

        try:
            logger = Logger()
            logger.app_start()  # should not crash despite permission error
        except Exception as exc:
            self.fail(f"Logger crashed on permission error: {exc}")
        finally:
            logger_mod.LOGS_DIR, logger_mod.APP_LOG = original
            try:
                restricted.chmod(0o755)
            except PermissionError:
                pass

    def test_logger_no_crash_on_invalid_path(self):
        """Logger should not crash when path is invalid."""
        import src.utils.logger as logger_mod
        original = logger_mod.LOGS_DIR, logger_mod.APP_LOG
        logger_mod.LOGS_DIR = Path("")
        logger_mod.APP_LOG = Path("") / "app.log"

        try:
            logger = Logger()
            logger.info("test", "should not crash")
        except Exception as exc:
            self.fail(f"Logger crashed on invalid path: {exc}")
        finally:
            logger_mod.LOGS_DIR, logger_mod.APP_LOG = original


if __name__ == "__main__":
    unittest.main()
