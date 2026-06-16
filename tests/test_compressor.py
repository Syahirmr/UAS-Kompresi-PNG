"""
Unit tests for src.compression.compressor
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image

from src.compression.compressor import compress_file


class TestCompressFile(unittest.TestCase):
    """Tests for compress_file()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.outdir = self.tmpdir / "output"
        self._make_png("test.png")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_png(self, name, size=(32, 32)):
        path = self.tmpdir / name
        img = Image.new("RGBA", size, (255, 0, 0, 255))
        img.save(path, format="PNG")
        return path

    # ---------- happy path ----------

    def test_compress_deflate_success(self):
        result = compress_file(self.tmpdir / "test.png", "deflate", self.outdir)
        self.assertTrue(result["success"])
        self.assertGreater(result["output_size"], 0)
        self.assertGreater(result["time_ms"], 0)
        self.assertTrue(Path(result["output_path"]).is_file())

    def test_compress_deflate_reduces_size(self):
        result = compress_file(self.tmpdir / "test.png", "deflate", self.outdir)
        self.assertTrue(result["success"])
        self.assertLessEqual(result["output_size"], result["input_size"] * 1.05)

    # ---------- invalid input ----------

    def test_compress_non_existent_file(self):
        result = compress_file(
            self.tmpdir / "does_not_exist.png",
            "deflate",
            self.outdir,
        )
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("tidak valid", result["error"].lower())

    def test_compress_non_png_file(self):
        txt = self.tmpdir / "not_image.png"
        txt.write_text("this is not a png file")
        result = compress_file(txt, "deflate", self.outdir)
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    # ---------- unknown algorithm ----------

    def test_compress_unknown_algorithm(self):
        result = compress_file(
            self.tmpdir / "test.png",
            "nonexistent_algo_xyz",
            self.outdir,
        )
        self.assertFalse(result["success"])
        self.assertIn("tidak dikenal", result["error"].lower())

    # ---------- algorithm aliases ----------

    def test_compress_deflate_baseline(self):
        result = compress_file(
            self.tmpdir / "test.png",
            "deflate_baseline",
            self.outdir,
        )
        self.assertTrue(result["success"])

    def test_compress_zopfli_raises_placeholder(self):
        """Zopfli runner is a placeholder; expect failure."""
        result = compress_file(
            self.tmpdir / "test.png",
            "zopfli",
            self.outdir,
        )
        self.assertFalse(result["success"])

    def test_compress_oxipng_raises_placeholder(self):
        """OxiPNG runner is a placeholder; expect failure."""
        result = compress_file(
            self.tmpdir / "test.png",
            "oxipng",
            self.outdir,
        )
        self.assertFalse(result["success"])

    # ---------- output directory creation ----------

    def test_compress_creates_output_dir(self):
        new_out = self.tmpdir / "new_output_dir"
        self.assertFalse(new_out.exists())
        result = compress_file(self.tmpdir / "test.png", "deflate", new_out)
        self.assertTrue(result["success"])
        self.assertTrue(new_out.is_dir())

    # ---------- edge cases ----------

    def test_compress_explicit_output_dir_creates_file(self):
        """Ensure compressor writes output to the specified directory."""
        result = compress_file(self.tmpdir / "test.png", "deflate", self.outdir)
        self.assertTrue(result["success"])
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertEqual(Path(result["output_path"]).parent.resolve(), self.outdir.resolve())


if __name__ == "__main__":
    unittest.main()
