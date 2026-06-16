"""
Unit tests for src.analysis.analyzer
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image

from src.analysis.analyzer import build_metric, summarize_metrics


class TestBuildMetric(unittest.TestCase):
    """Tests for build_metric()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_png(self, name, size=(16, 16)):
        path = self.tmpdir / name
        img = Image.new("RGBA", size, (0, 128, 255, 255))
        img.save(path, format="PNG")
        return path

    def _compression_result(self, success=True, input_size=1024, output_size=512,
                            time_ms=100.5):
        return {
            "success": success,
            "input_size": input_size,
            "output_size": output_size,
            "time_ms": time_ms,
        }

    # ---------- happy path ----------

    def test_build_metric_success(self):
        png = self._make_png("photo.png")
        cr = self._compression_result(input_size=20480, output_size=10240, time_ms=150.0)
        metric = build_metric(png, "deflate", cr)

        self.assertEqual(metric["file"], "photo.png")
        self.assertEqual(metric["algorithm"], "Deflate Baseline")
        self.assertEqual(metric["original_size"], 20480)
        self.assertEqual(metric["compressed_size"], 10240)
        self.assertAlmostEqual(metric["reduction_percent"], 50.0, places=2)
        self.assertEqual(metric["time_ms"], 150.0)
        self.assertEqual(metric["resolution"], "16x16")
        self.assertEqual(metric["status"], "SUCCESS")

    def test_build_metric_with_zopfli_label(self):
        png = self._make_png("z.png")
        cr = self._compression_result()
        metric = build_metric(png, "zopfli", cr)
        self.assertEqual(metric["algorithm"], "Zopfli Deflate")

    def test_build_metric_with_oxipng_label(self):
        png = self._make_png("o.png")
        cr = self._compression_result()
        metric = build_metric(png, "oxipng", cr)
        self.assertEqual(metric["algorithm"], "OxiPNG")

    # ---------- failed compression ----------

    def test_build_metric_failed(self):
        png = self._make_png("fail.png")
        cr = self._compression_result(success=False, input_size=100, output_size=0)
        metric = build_metric(png, "deflate", cr)
        self.assertEqual(metric["status"], "FAILED")
        self.assertEqual(metric["reduction_percent"], 0)
        self.assertGreater(metric["resolution"], "0x0")

    # ---------- edge cases ----------

    def test_build_metric_zero_input_size(self):
        png = self._make_png("zero.png")
        cr = self._compression_result(success=True, input_size=0, output_size=0)
        metric = build_metric(png, "deflate", cr)
        self.assertEqual(metric["reduction_percent"], 0)

    def test_build_metric_non_existent_file_resolution(self):
        png = Path(self.tmpdir / "noexist.png")
        cr = self._compression_result(success=True, input_size=100, output_size=50)
        metric = build_metric(png, "deflate", cr)
        # Resolution should be "-" for unreadable files
        self.assertEqual(metric["resolution"], "-")


class TestSummarizeMetrics(unittest.TestCase):
    """Tests for summarize_metrics()"""

    def setUp(self):
        self.success_metric = {
            "file": "a.png", "algorithm": "Deflate",
            "original_size": 200, "compressed_size": 100,
            "reduction_percent": 50.0, "time_ms": 100.0,
            "resolution": "10x10", "status": "SUCCESS",
        }
        self.failed_metric = {
            "file": "b.png", "algorithm": "Deflate",
            "original_size": 200, "compressed_size": 0,
            "reduction_percent": 0.0, "time_ms": 50.0,
            "resolution": "10x10", "status": "FAILED",
        }

    # ---------- happy path ----------

    def test_summarize_all_success(self):
        metrics = [self.success_metric, self.success_metric]
        s = summarize_metrics(metrics)

        self.assertEqual(s["completed"], 2)
        self.assertEqual(s["failed"], 0)
        self.assertAlmostEqual(s["avg_reduction"], 50.0, places=2)
        self.assertAlmostEqual(s["avg_time_ms"], 100.0, places=2)

    def test_summarize_with_failed(self):
        metrics = [self.success_metric, self.failed_metric]
        s = summarize_metrics(metrics)

        self.assertEqual(s["completed"], 2)
        self.assertEqual(s["failed"], 1)
        self.assertAlmostEqual(s["avg_reduction"], 50.0, places=2)
        self.assertAlmostEqual(s["avg_time_ms"], 75.0, places=2)

    def test_summarize_cancelled(self):
        metrics = [self.success_metric]
        s = summarize_metrics(metrics, cancelled=True)

        self.assertTrue(s["cancelled"])

    def test_summarize_not_cancelled(self):
        s = summarize_metrics([self.success_metric], cancelled=False)
        self.assertFalse(s["cancelled"])

    def test_summarize_default_cancelled(self):
        s = summarize_metrics([self.success_metric])
        self.assertFalse(s["cancelled"])

    # ---------- empty ----------

    def test_summarize_empty_metrics(self):
        s = summarize_metrics([])
        self.assertEqual(s["completed"], 0)
        self.assertEqual(s["failed"], 0)
        self.assertFalse(s["cancelled"])
        self.assertEqual(s["avg_reduction"], 0)
        self.assertEqual(s["avg_time_ms"], 0)

    def test_summarize_all_failed(self):
        metrics = [self.failed_metric, self.failed_metric]
        s = summarize_metrics(metrics)

        self.assertEqual(s["completed"], 2)
        self.assertEqual(s["failed"], 2)
        # avg_reduction = avg of empty list = 0
        self.assertEqual(s["avg_reduction"], 0)
        self.assertAlmostEqual(s["avg_time_ms"], 50.0, places=2)


if __name__ == "__main__":
    unittest.main()
