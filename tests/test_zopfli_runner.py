"""
Unit tests for src.compression.algorithms.zopfli_runner

Tests cover the zopfli.zlib-based PNG recompression logic.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

from src.compression.algorithms.zopfli_runner import run_zopfli


class TestRunZopfli(unittest.TestCase):
    """Tests for run_zopfli() — now uses zopfli.zlib internally."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.outdir = self.tmpdir / "output"
        self.outdir.mkdir(exist_ok=True)
        self.input_png = self.tmpdir / "test.png"
        img = Image.new("RGB", (16, 16), (255, 0, 0))
        img.save(str(self.input_png), format="PNG")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ---------- happy path ----------

    def test_zopfli_returns_dict(self):
        """Always returns a dict."""
        result = run_zopfli(self.input_png, self.outdir)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("output_path", result)

    def test_zopfli_success_produces_png(self):
        """Successful compression produces a real PNG file."""
        result = run_zopfli(self.input_png, self.outdir)
        self.assertTrue(result["success"])
        output = Path(result["output_path"])
        self.assertTrue(output.is_file())
        self.assertGreater(output.stat().st_size, 0)
        # Verify it's a real PNG
        with output.open("rb") as f:
            self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n")

    def test_zopfli_output_is_valid_png(self):
        """Output can be opened by Pillow."""
        result = run_zopfli(self.input_png, self.outdir)
        self.assertTrue(result["success"])
        with Image.open(result["output_path"]) as img:
            img.verify()

    def test_zopfli_preserves_dimensions(self):
        """Output PNG has same dimensions as input."""
        result = run_zopfli(self.input_png, self.outdir)
        self.assertTrue(result["success"])
        with Image.open(result["output_path"]) as img:
            self.assertEqual(img.size, (16, 16))

    def test_zopfli_produces_smaller_or_equal(self):
        """Zopfli recompressed PNG should be comparable in size."""
        result = run_zopfli(self.input_png, self.outdir)
        self.assertTrue(result["success"])
        output_size = Path(result["output_path"]).stat().st_size
        input_size = self.input_png.stat().st_size
        # Zopfli should generally produce smaller or same-size output
        self.assertLessEqual(output_size, input_size * 1.1)

    # ---------- invalid input ----------

    def test_zopfli_non_existent_file(self):
        """Non-existent input returns failure."""
        result = run_zopfli(
            self.tmpdir / "noexist.png", self.outdir
        )
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    def test_zopfli_non_png_file(self):
        """Non-PNG file returns failure."""
        txt = self.tmpdir / "not_png.png"
        txt.write_text("this is not a png")
        result = run_zopfli(txt, self.outdir)
        self.assertFalse(result["success"])
        # Error message should mention invalid PNG
        self.assertTrue(
            "bukan file png" in result["error"].lower()
            or "tidak valid" in result["error"].lower()
            or "gagal" in result["error"].lower()
        )

    # ---------- output path ----------

    def test_zopfli_output_path_is_png(self):
        """Output path should end with .png, not .gz."""
        result = run_zopfli(self.input_png, self.outdir)
        self.assertTrue(result["success"])
        self.assertTrue(result["output_path"].endswith(".png"),
                        f"Expected .png but got: {result['output_path']}")
        self.assertFalse(result["output_path"].endswith(".gz"),
                         "Should NOT be .gz")

    def test_zopfli_error_path_is_png(self):
        """Even on error, output_path points to .png location."""
        result = run_zopfli(self.tmpdir / "noexist.png", self.outdir)
        self.assertFalse(result["success"])
        self.assertTrue(result["output_path"].endswith(".png"))

    # ---------- error: zopfli.zlib.compress fails ----------

    def test_zopfli_zlib_compress_error(self):
        """When zopfli.zlib.compress raises, return failure dict."""
        with patch("zopfli.zlib.compress",
                   side_effect=RuntimeError("Compression failed")):
            result = run_zopfli(self.input_png, self.outdir)
        self.assertFalse(result["success"])
        self.assertIn("Compression failed", result["error"])

    # ---------- error: corrupted IDAT ----------

    def test_zopfli_corrupted_idat(self):
        """Corrupted IDAT data returns failure."""
        # Create a file with valid PNG header but corrupted IDAT
        bad_png = self.tmpdir / "corrupted.png"
        bad_png.write_bytes(
            b"\x89PNG\r\n\x1a\n" +  # signature
            b"\x00\x00\x00\x0d" +    # IHDR length
            b"IHDR" +                # IHDR type
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00" +  # IHDR data
            b"\x90wS\xde" +          # IHDR CRC
            b"\x00\x00\x00\x10" +    # IDAT length (16 bytes)
            b"IDAT" +                # IDAT type
            b"This is corrupted data that won't decompress!!!"  # 16 bytes of bad data
            b"\x00\x00\x00\x00" +    # IEND length
            b"IEND" +                # IEND type
            b"\xaeB`\x82"           # IEND CRC
        )
        result = run_zopfli(bad_png, self.outdir)
        self.assertFalse(result["success"])
        # Should get a decompression error
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
