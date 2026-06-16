"""
Unit tests for src.processing.batch_processor
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image

from src.processing.batch_processor import process_dataset


# Callback helpers — capture calls for assertions
CALLS = []


def _collector(progress, status, metric):
    CALLS.append({"progress": progress, "status": status, "metric": metric})


def _never_cancel():
    return False


def _cancel_after(count):
    """Return a cancel_check that returns True after `count` calls."""
    n = 0

    def _check():
        nonlocal n
        n += 1
        return n > count
    return _check


class TestProcessDataset(unittest.TestCase):
    """Tests for process_dataset()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.outdir = self.tmpdir / "output"
        self.outdir.mkdir(exist_ok=True)
        # Make 3 minimal PNG files
        for i in range(3):
            img = Image.new("RGB", (4, 4), (255, 0, 0))
            img.save(str(self.tmpdir / f"img_{i}.png"), format="PNG")

        self.files = sorted(self.tmpdir.glob("*.png"))
        global CALLS
        CALLS = []

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ---------- happy path ----------

    def test_process_three_files_success(self):
        result = process_dataset(self.files, "deflate", self.outdir,
                                 _collector, _never_cancel)
        self.assertEqual(result["completed"], 3)
        self.assertEqual(result["failed"], 0)
        self.assertFalse(result["cancelled"])
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(len(result["metrics"]), 3)

    def test_process_returns_summary(self):
        result = process_dataset(self.files, "deflate", self.outdir,
                                 _collector, _never_cancel)
        summary = result["summary"]
        self.assertEqual(summary["completed"], 3)
        self.assertEqual(summary["failed"], 0)
        self.assertFalse(summary["cancelled"])
        self.assertGreater(summary["avg_reduction"], 0)
        self.assertGreater(summary["avg_time_ms"], 0)

    # ---------- empty dataset ----------

    def test_process_empty_dataset(self):
        result = process_dataset([], "deflate", self.outdir,
                                 _collector, _never_cancel)
        self.assertEqual(result["completed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertFalse(result["cancelled"])
        self.assertEqual(len(result["results"]), 0)
        self.assertEqual(result["summary"]["avg_reduction"], 0)

    # ---------- cancel flow ----------

    def test_process_cancel_immediately(self):
        """Cancel before any file is processed."""
        result = process_dataset(self.files, "deflate", self.outdir,
                                 _collector, lambda: True)
        self.assertEqual(result["completed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertTrue(result["cancelled"])

    def test_process_cancel_after_one_file(self):
        """Cancel after the first file completes."""
        result = process_dataset(self.files, "deflate", self.outdir,
                                 _collector, _cancel_after(2))
        # 1 file should be completed (cancel_check is called before and after each file)
        self.assertGreaterEqual(result["completed"], 1)
        self.assertTrue(result["cancelled"])

    # ---------- single file ----------

    def test_process_single_file(self):
        files = [self.files[0]]
        result = process_dataset(files, "deflate", self.outdir,
                                 _collector, _never_cancel)
        self.assertEqual(result["completed"], 1)
        self.assertEqual(result["failed"], 0)

    # ---------- progress callbacks ----------

    def test_process_calls_progress(self):
        process_dataset(self.files, "deflate", self.outdir,
                        _collector, _never_cancel)
        self.assertGreater(len(CALLS), 0)
        # Final progress should be 100
        self.assertAlmostEqual(CALLS[-1]["progress"], 100, delta=1)


if __name__ == "__main__":
    unittest.main()
