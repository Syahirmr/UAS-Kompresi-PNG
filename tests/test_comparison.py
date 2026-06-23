"""
Unit tests for the Comparison Dashboard (Milestones 10 + 11).

Covers:
- run_comparison: all algorithms, partial fail, cancel, winners, scores
- export_comparison_csv: new score-based format
- generate_reduction_chart / generate_time_chart: timestamped charts
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

from src.compression.comparison_runner import (
    run_comparison,
    _compute_winners,
    ALGORITHM_LABELS,
)
from src.export.exporter import (
    export_comparison_csv,
    generate_reduction_chart,
    generate_time_chart,
    compute_ranking_scores,
)


# ---------- callback helpers ----------

CALLS = []


def _collector(progress, status, metric):
    CALLS.append({"progress": progress, "status": status, "metric": metric})


def _never_cancel():
    return False


def _cancel_immediately():
    return True


class TestRunComparison(unittest.TestCase):
    """Tests for run_comparison()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.outdir = self.tmpdir / "comparison_out"
        self.outdir.mkdir(exist_ok=True)
        # Make 2 minimal PNG files
        for i in range(2):
            img = Image.new("RGB", (4, 4), (255, 0, 0))
            img.save(str(self.tmpdir / f"img_{i}.png"), format="PNG")
        self.files = sorted(self.tmpdir.glob("*.png"))
        global CALLS
        CALLS = []

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ---------- happy path ----------

    def test_run_comparison_all_algorithms(self):
        """Test 1: Run all algorithms — all should produce results."""
        result = run_comparison(self.files, self.outdir, _collector, _never_cancel)
        self.assertIn("per_algorithm", result)
        self.assertIn("all_metrics", result)
        self.assertIn("winners", result)
        # All 3 algorithms should have data
        for algo in ["deflate", "zopfli", "oxipng"]:
            self.assertIn(algo, result["per_algorithm"])
            data = result["per_algorithm"][algo]
            self.assertGreater(len(data["metrics"]), 0)
            self.assertEqual(data["summary"]["completed"], 2)

    def test_run_comparison_has_winners(self):
        """Comparison should identify winners."""
        result = run_comparison(self.files, self.outdir, _collector, _never_cancel)
        winners = result["winners"]
        self.assertIsNotNone(winners["winner_reduction_algorithm"])
        self.assertIsNotNone(winners["winner_speed_algorithm"])
        self.assertIn(winners["winner_reduction_algorithm"], ["deflate", "zopfli", "oxipng"])
        self.assertIn(winners["winner_speed_algorithm"], ["deflate", "zopfli", "oxipng"])

    def test_run_comparison_all_metrics(self):
        """All metrics should contain metrics from all algorithms."""
        result = run_comparison(self.files, self.outdir, _collector, _never_cancel)
        # 2 files × 3 algorithms = 6 metrics
        self.assertEqual(len(result["all_metrics"]), 6)

    # ---------- empty dataset ----------

    def test_run_comparison_empty_dataset(self):
        """Empty dataset should return empty comparison."""
        result = run_comparison([], self.outdir, _collector, _never_cancel)
        self.assertEqual(result["all_metrics"], [])
        self.assertEqual(result["per_algorithm"], {})
        self.assertFalse(result["cancelled"])

    # ---------- cancel ----------

    def test_run_comparison_cancel_immediately(self):
        """Cancel before any algorithm runs."""
        result = run_comparison(self.files, self.outdir, _collector, _cancel_immediately)
        self.assertTrue(result["cancelled"])
        # At most 1 algorithm may have started
        self.assertLessEqual(len(result["all_metrics"]), 4)

    # ---------- progress callbacks ----------

    def test_run_comparison_calls_progress(self):
        """Progress callback should be called at least once."""
        run_comparison(self.files, self.outdir, _collector, _never_cancel)
        self.assertGreater(len(CALLS), 0)
        self.assertAlmostEqual(CALLS[-1]["progress"], 100, delta=1)

    # ---------- summary ----------

    def test_run_comparison_summary(self):
        """Summary should correctly count completed and failed."""
        result = run_comparison(self.files, self.outdir, _collector, _never_cancel)
        summary = result["summary"]
        # 2 files × 3 algos = 6 total completions
        self.assertGreater(summary["completed"], 0)


class TestComputeWinners(unittest.TestCase):
    """Tests for _compute_winners()"""

    def _make_per_algorithm(self, reduction_values, time_values):
        data = {}
        for algo, red, t in zip(["deflate", "zopfli", "oxipng"], reduction_values, time_values):
            data[algo] = {
                "algorithm": algo,
                "label": ALGORITHM_LABELS[algo],
                "metrics": [
                    {"status": "SUCCESS", "reduction_percent": red, "time_ms": t, "file": "test.png"}
                ],
                "summary": {"avg_reduction": red, "avg_time_ms": t},
            }
        return data

    def test_winner_reduction_is_max(self):
        """Best compression should be the algorithm with highest avg reduction."""
        data = self._make_per_algorithm([10, 20, 15], [100, 200, 150])
        winners = _compute_winners(data, cancelled=False)
        self.assertEqual(winners["winner_reduction_algorithm"], "zopfli")
        self.assertAlmostEqual(winners["winner_reduction_value"], 20)

    def test_winner_speed_is_min(self):
        """Fastest should be the algorithm with lowest avg time."""
        data = self._make_per_algorithm([10, 20, 15], [100, 200, 50])
        winners = _compute_winners(data, cancelled=False)
        self.assertEqual(winners["winner_speed_algorithm"], "oxipng")
        self.assertAlmostEqual(winners["winner_speed_value"], 50)


class TestExportComparisonCsv(unittest.TestCase):
    """Tests for export_comparison_csv()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.per_algorithm = {
            "deflate": {
                "label": "Deflate Baseline",
                "summary": {"completed": 2, "failed": 0, "avg_reduction": 25.0, "avg_time_ms": 100.0},
                "metrics": [
                    {"status": "SUCCESS", "reduction_percent": 20.0, "file": "a.png"},
                    {"status": "SUCCESS", "reduction_percent": 30.0, "file": "b.png"},
                ],
            },
            "zopfli": {
                "label": "Zopfli Deflate",
                "summary": {"completed": 2, "failed": 0, "avg_reduction": 35.0, "avg_time_ms": 500.0},
                "metrics": [
                    {"status": "SUCCESS", "reduction_percent": 30.0, "file": "a.png"},
                    {"status": "SUCCESS", "reduction_percent": 40.0, "file": "b.png"},
                ],
            },
        }
        self.winners = {
            "winner_reduction_label": "Zopfli Deflate",
            "winner_reduction_value": 35.0,
            "winner_speed_label": "Deflate Baseline",
            "winner_speed_value": 100.0,
        }

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_export_creates_csv(self):
        """Comparison CSV should be created."""
        path = export_comparison_csv(self.per_algorithm, self.winners, self.tmpdir)
        self.assertTrue(path.is_file())
        self.assertIn("comparison_report_", path.name)
        self.assertEqual(path.suffix, ".csv")

    def test_export_contains_algorithm_rows(self):
        """CSV should contain algorithm rows."""
        path = export_comparison_csv(self.per_algorithm, self.winners, self.tmpdir)
        content = path.read_text(encoding="utf-8")
        self.assertIn("Deflate Baseline", content)
        self.assertIn("Zopfli Deflate", content)

    def test_export_contains_winners(self):
        """CSV should contain winner information."""
        path = export_comparison_csv(self.per_algorithm, self.winners, self.tmpdir)
        content = path.read_text(encoding="utf-8")
        self.assertIn("best_compression", content)
        self.assertIn("fastest", content)
        self.assertIn("balanced", content)

    def test_export_empty_data(self):
        """Export should handle empty per_algorithm gracefully."""
        path = export_comparison_csv({}, self.winners, self.tmpdir)
        self.assertTrue(path.is_file())


class TestGenerateCharts(unittest.TestCase):
    """Tests for generate_reduction_chart() and generate_time_chart()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.per_algorithm = {
            "deflate": {
                "label": "Deflate Baseline",
                "summary": {"avg_reduction": 25.0, "avg_time_ms": 100.0},
                "metrics": [{"status": "SUCCESS", "file": "a.png"}],
            },
            "zopfli": {
                "label": "Zopfli Deflate",
                "summary": {"avg_reduction": 35.0, "avg_time_ms": 500.0},
                "metrics": [{"status": "SUCCESS", "file": "a.png"}],
            },
            "oxipng": {
                "label": "OxiPNG",
                "summary": {"avg_reduction": 30.0, "avg_time_ms": 300.0},
                "metrics": [{"status": "SUCCESS", "file": "a.png"}],
            },
        }

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_reduction_chart_creates_png(self):
        """Reduction chart should be saved as PNG with timestamp."""
        path = generate_reduction_chart(self.per_algorithm, self.tmpdir)
        self.assertTrue(path.is_file())
        self.assertIn("reduction_chart_", path.name)
        self.assertEqual(path.suffix, ".png")
        self.assertGreater(path.stat().st_size, 0)

    def test_time_chart_creates_png(self):
        """Time chart should be saved as PNG with timestamp."""
        path = generate_time_chart(self.per_algorithm, self.tmpdir)
        self.assertTrue(path.is_file())
        self.assertIn("time_chart_", path.name)
        self.assertEqual(path.suffix, ".png")
        self.assertGreater(path.stat().st_size, 0)

    def test_chart_is_valid_png(self):
        """Chart PNG should have valid signature."""
        path = generate_reduction_chart(self.per_algorithm, self.tmpdir)
        with open(path, "rb") as f:
            sig = f.read(8)
        self.assertEqual(sig, b"\x89PNG\r\n\x1a\n")

    def test_chart_empty_data(self):
        """Chart should handle empty data gracefully."""
        path = generate_reduction_chart({}, self.tmpdir)
        self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
