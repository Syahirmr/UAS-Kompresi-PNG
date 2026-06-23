"""
Integration tests for real OxiPNG executable execution.

Tests exercise the actual oxipng.exe binary placed in tools/oxipng/.
Skipped when executable is not found.

Includes an automated acceptance test that prints a summary.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image

from src.compression.compressor import compress_file
from src.compression.algorithms.oxipng_runner import _find_executable


def _make_png(path, size=(32, 32), mode="RGB"):
    """Create a minimal but real PNG for testing."""
    img = Image.new(mode, size, (128, 64, 32))
    img.save(str(path), format="PNG")
    return path


def _is_valid_png(path):
    """Check if a file is a valid PNG using Pillow."""
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def _executable_available():
    """Check if oxipng is available via tools/ or PATH."""
    result, source = _find_executable()
    return result is not None


class TestOxipngExecutableDiscovery(unittest.TestCase):
    """Test 1: executable ditemukan."""

    def test_executable_found(self):
        """oxipng executable ditemukan di tools/oxipng/ atau PATH."""
        executable, source = _find_executable()
        self.assertIsNotNone(
            executable,
            "oxipng executable tidak ditemukan. "
            "Letakkan oxipng.exe di tools/oxipng/",
        )
        self.assertIsNotNone(source)
        # Should find from tools/ priority
        self.assertIn("tools/oxipng", source)


class TestOxipngRealCompression(unittest.TestCase):
    """Tests 2-6: compress success, output exists, PNG valid, size reduction."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.png = _make_png(self.tmpdir / "test.png")
        self.outdir = self.tmpdir / "output_oxipng"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_oxipng_compress_success(self):
        """Test 2: compress_file() return success=True."""
        if not _executable_available():
            self.skipTest("oxipng executable not found")
        result = compress_file(self.png, "oxipng", self.outdir)
        self.assertTrue(result["success"], f"OxiPNG failed: {result['error']}")

    def test_oxipng_output_file_exists(self):
        """Test 3: output file exist."""
        if not _executable_available():
            self.skipTest("oxipng executable not found")
        result = compress_file(self.png, "oxipng", self.outdir)
        self.assertTrue(result["success"])
        output_path = Path(result["output_path"])
        self.assertTrue(output_path.is_file(), "Output file tidak ditemukan")
        self.assertGreater(output_path.stat().st_size, 0, "Output file kosong")

    def test_oxipng_output_valid_png(self):
        """Test 4: output PNG valid (PIL.verify)."""
        if not _executable_available():
            self.skipTest("oxipng executable not found")
        result = compress_file(self.png, "oxipng", self.outdir)
        self.assertTrue(result["success"])
        self.assertTrue(
            _is_valid_png(result["output_path"]),
            "Output bukan PNG valid",
        )

    def test_oxipng_size_reduction(self):
        """Test 5: output_size <= input_size * 1.05 (allow slight overhead)."""
        if not _executable_available():
            self.skipTest("oxipng executable not found")
        result = compress_file(self.png, "oxipng", self.outdir)
        self.assertTrue(result["success"])
        self.assertLessEqual(
            result["output_size"],
            result["input_size"] * 1.05,
            "Output size terlalu besar dari input",
        )


class TestOxipngAcceptance(unittest.TestCase):
    """Test E: Acceptance test otomatis — prints summary."""

    def test_acceptance_summary(self):
        """Print structured acceptance test report."""
        if not _executable_available():
            print("=== OXIPNG ACCEPTANCE ===")
            print("Executable: NOT FOUND")
            print("Status: SKIPPED")
            self.skipTest("oxipng executable not found")

        tmpdir = Path(tempfile.mkdtemp())
        try:
            png = _make_png(tmpdir / "accept.png", size=(64, 64))
            input_size = png.stat().st_size
            outdir = tmpdir / "out"

            result = compress_file(png, "oxipng", outdir)
            output_path = Path(result["output_path"])
            output_size = output_path.stat().st_size if output_path.is_file() else 0
            reduction = (
                (1 - output_size / input_size) * 100
                if input_size > 0 and output_size > 0
                else 0
            )
            png_valid = _is_valid_png(result["output_path"]) if result["success"] else False

            executable, source = _find_executable()

            print()
            print("=== OXIPNG ACCEPTANCE ===")
            print(f"Executable:  {executable}")
            print(f"Source:      {source}")
            print(f"Status:      {'PASS' if result['success'] else 'FAIL'}")
            print(f"Input Size:  {input_size} bytes")
            print(f"Output Size: {output_size} bytes")
            print(f"Reduction:   {reduction:.2f}%")
            print(f"PNG Valid:   {'YES' if png_valid else 'NO'}")
            print(f"Error:       {result.get('error', 'None')}")
            print()

            self.assertTrue(result["success"], f"Acceptance FAILED: {result.get('error')}")
            self.assertTrue(png_valid, "Output PNG tidak valid")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
