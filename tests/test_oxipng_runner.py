"""
Unit tests for src.compression.algorithms.oxipng_runner
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

from src.compression.algorithms.oxipng_runner import (
    run_oxipng,
    _find_executable,
    EXECUTABLE_CANDIDATES,
)


class TestFindExecutable(unittest.TestCase):
    """Tests for _find_executable()"""

    def test_returns_none_when_not_found(self):
        """No oxipng in tools/ or PATH."""
        with patch("src.compression.algorithms.oxipng_runner.EXECUTABLE_CANDIDATES", []):
            with patch("src.compression.algorithms.oxipng_runner.shutil.which",
                       return_value=None):
                result, source = _find_executable()
                self.assertIsNone(result)
                self.assertIsNone(source)

    def test_returns_path_from_tools(self):
        """oxipng found in tools/oxipng/."""
        fake_path = str(Path("/fake/tools/oxipng/oxipng.exe"))
        with patch("src.compression.algorithms.oxipng_runner.EXECUTABLE_CANDIDATES",
                   [fake_path]):
            with patch("pathlib.Path.is_file", return_value=True):
                result, source = _find_executable()
                self.assertTrue(result.endswith("oxipng.exe"))
                self.assertIn("tools/oxipng", source)

    def test_returns_path_from_path(self):
        """oxipng found via shutil.which."""
        with patch("src.compression.algorithms.oxipng_runner.EXECUTABLE_CANDIDATES", []):
            with patch("src.compression.algorithms.oxipng_runner.shutil.which",
                       return_value="/usr/bin/oxipng"):
                result, source = _find_executable()
                self.assertEqual(result, "/usr/bin/oxipng")
                self.assertEqual(source, "PATH")


class TestRunOxipng(unittest.TestCase):
    """Tests for run_oxipng()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.outdir = self.tmpdir / "output"
        self.outdir.mkdir(exist_ok=True)
        # Create a tiny PNG
        self.input_png = self.tmpdir / "test.png"
        img = Image.new("RGB", (4, 4), (255, 0, 0))
        img.save(str(self.input_png), format="PNG")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ---------- executable not found ----------

    def test_no_executable_returns_failure(self):
        """When oxipng is not found, return graceful error dict."""
        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=(None, None)):
            result = run_oxipng(self.input_png, self.outdir)

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("tidak ditemukan", result["error"])

    # ---------- subprocess failure ----------

    def test_subprocess_nonzero_exit(self):
        """oxipng exits with non-zero code."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error: invalid file"

        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=("/fake/oxipng", "PATH")):
            with patch("src.compression.algorithms.oxipng_runner.subprocess.run",
                       return_value=mock_result):
                result = run_oxipng(self.input_png, self.outdir)

        self.assertFalse(result["success"])
        self.assertIn("invalid file", result["error"])

    def test_subprocess_timeout(self):
        """oxipng times out."""
        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=("/fake/oxipng", "PATH")):
            with patch("src.compression.algorithms.oxipng_runner.subprocess.run",
                       side_effect=__import__("subprocess").TimeoutExpired(
                           "oxipng", 120)):
                result = run_oxipng(self.input_png, self.outdir)

        self.assertFalse(result["success"])
        self.assertIn("timeout", result["error"].lower())

    def test_subprocess_permission_error(self):
        """oxipng raises PermissionError."""
        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=("/fake/oxipng", "PATH")):
            with patch("src.compression.algorithms.oxipng_runner.subprocess.run",
                       side_effect=PermissionError("Access denied")):
                result = run_oxipng(self.input_png, self.outdir)

        self.assertFalse(result["success"])
        self.assertIn("permission", result["error"].lower())

    def test_subprocess_os_error(self):
        """oxipng raises OSError."""
        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=("/fake/oxipng", "PATH")):
            with patch("src.compression.algorithms.oxipng_runner.subprocess.run",
                       side_effect=OSError("Out of memory")):
                result = run_oxipng(self.input_png, self.outdir)

        self.assertFalse(result["success"])
        self.assertIn("Out of memory", result["error"])

    # ---------- output file not created ----------

    def test_output_file_missing_returns_failure(self):
        """oxipng exits 0 but file is not created."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""

        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=("/fake/oxipng", "PATH")):
            with patch("src.compression.algorithms.oxipng_runner.subprocess.run",
                       return_value=mock_result):
                result = run_oxipng(self.input_png, self.outdir)

        self.assertFalse(result["success"])
        self.assertIn("tidak ditemukan", result["error"])

    # ---------- output path always set ----------

    def test_output_path_always_returned(self):
        """Even on failure, output_path points to where the file should be."""
        with patch("src.compression.algorithms.oxipng_runner._find_executable",
                   return_value=(None, None)):
            result = run_oxipng(self.input_png, self.outdir)

        self.assertIn("test.png", result["output_path"])
        self.assertTrue(result["output_path"].endswith(".png"))


if __name__ == "__main__":
    unittest.main()
