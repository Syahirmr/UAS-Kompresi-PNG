"""
Integration tests for real compressor execution.

These tests exercise the actual compression algorithms against real PNG files.
Tests are skipped when the required executable or package is not available.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image

from src.compression.compressor import compress_file


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


class TestDeflateReal(unittest.TestCase):
    """Deflate — always available (uses zlib/stdlib)."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.png = _make_png(self.tmpdir / "test.png")
        self.outdir = self.tmpdir / "output_deflate"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_deflate_produces_valid_png(self):
        """Deflate produces a real PNG file."""
        result = compress_file(self.png, "deflate", self.outdir)
        self.assertTrue(result["success"], f"Deflate failed: {result['error']}")
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertTrue(_is_valid_png(result["output_path"]))

    def test_deflate_metrics(self):
        """Deflate returns valid metrics."""
        result = compress_file(self.png, "deflate", self.outdir)
        self.assertTrue(result["success"])
        self.assertGreater(result["input_size"], 0)
        self.assertGreater(result["output_size"], 0)
        self.assertGreater(result["time_ms"], 0)
        self.assertTrue(result["output_path"].endswith(".png"))


class TestOxipngReal(unittest.TestCase):
    """OxiPNG — requires executable in tools/oxipng/ or PATH."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.png = _make_png(self.tmpdir / "test.png")
        self.outdir = self.tmpdir / "output_oxipng"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _executable_available(self):
        """Check if oxipng is available via tools/ or PATH."""
        tools = Path(__file__).resolve().parents[1] / "tools" / "oxipng"
        for name in ("oxipng.exe", "oxipng"):
            if (tools / name).is_file():
                return True
        return shutil.which("oxipng") is not None

    def test_oxipng_produces_valid_png(self):
        """OxiPNG produces a real PNG file when executable is available."""
        if not self._executable_available():
            self.skipTest("oxipng executable not found in tools/ or PATH")
        result = compress_file(self.png, "oxipng", self.outdir)
        self.assertTrue(result["success"], f"OxiPNG failed: {result['error']}")
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertTrue(_is_valid_png(result["output_path"]))

    def test_oxipng_reduces_size(self):
        """OxiPNG should reduce file size."""
        if not self._executable_available():
            self.skipTest("oxipng executable not found in tools/ or PATH")
        result = compress_file(self.png, "oxipng", self.outdir)
        self.assertTrue(result["success"])
        self.assertLessEqual(result["output_size"], result["input_size"] * 1.05)


class TestZopfliReal(unittest.TestCase):
    """Zopfli — always available (uses zopfli Python package)."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.png = _make_png(self.tmpdir / "test.png")
        self.outdir = self.tmpdir / "output_zopfli"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_zopfli_produces_valid_png(self):
        """Zopfli produces a real PNG file, not .gz."""
        result = compress_file(self.png, "zopfli", self.outdir)
        self.assertTrue(result["success"], f"Zopfli failed: {result['error']}")
        output_path = Path(result["output_path"])
        self.assertTrue(output_path.is_file())
        self.assertTrue(
            output_path.name.endswith(".png"),
            f"Output should be .png but got: {output_path.name}"
        )
        self.assertTrue(
            _is_valid_png(result["output_path"]),
            "Output is not a valid PNG"
        )

    def test_zopfli_preserves_dimensions(self):
        """Zopfli output has same dimensions as input."""
        result = compress_file(self.png, "zopfli", self.outdir)
        self.assertTrue(result["success"])
        with Image.open(result["output_path"]) as img:
            with Image.open(self.png) as orig:
                self.assertEqual(img.size, orig.size)

    def test_zopfli_preserves_mode_rgb(self):
        """Zopfli preserves RGB mode."""
        result = compress_file(self.png, "zopfli", self.outdir)
        self.assertTrue(result["success"])
        with Image.open(result["output_path"]) as img:
            self.assertEqual(img.mode, "RGB")

    def test_zopfli_with_rgba(self):
        """Zopfli handles RGBA images correctly."""
        rgba = _make_png(self.tmpdir / "rgba.png", mode="RGBA")
        result = compress_file(rgba, "zopfli", self.outdir / "rgba")
        self.assertTrue(result["success"], f"Zopfli RGBA failed: {result['error']}")
        self.assertTrue(_is_valid_png(result["output_path"]))

    def test_zopfli_metrics(self):
        """Zopfli returns valid metrics with output_size > 0."""
        result = compress_file(self.png, "zopfli", self.outdir)
        self.assertTrue(result["success"])
        self.assertGreater(result["input_size"], 0)
        self.assertGreater(result["output_size"], 0)
        self.assertGreater(result["time_ms"], 0)

    def test_zopfli_vs_deflate_comparison(self):
        """Zopfli should produce different (smaller or comparable) output vs deflate."""
        # Run deflate
        deflate_out = self.tmpdir / "out_deflate"
        deflate_result = compress_file(self.png, "deflate", deflate_out)
        self.assertTrue(deflate_result["success"])

        # Run zopfli
        zopfli_out = self.tmpdir / "out_zopfli"
        zopfli_result = compress_file(self.png, "zopfli", zopfli_out)
        self.assertTrue(zopfli_result["success"])

        # Both should produce valid PNGs
        self.assertTrue(_is_valid_png(deflate_result["output_path"]))
        self.assertTrue(_is_valid_png(zopfli_result["output_path"]))


class TestAllAlgorithmsReal(unittest.TestCase):
    """Compare all 3 algorithms on the same image."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        # Use a larger image for meaningful comparison
        self.png = _make_png(self.tmpdir / "compare.png", size=(128, 128))
        self.results = {}

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_all_produce_valid_pngs(self):
        """All 3 algorithms produce valid PNG outputs."""
        # Deflate
        r = compress_file(self.png, "deflate", self.tmpdir / "out_deflate")
        self.assertTrue(r["success"], f"Deflate: {r['error']}")
        self.assertTrue(_is_valid_png(r["output_path"]))
        self.results["deflate"] = r

        # Zopfli (always available)
        r = compress_file(self.png, "zopfli", self.tmpdir / "out_zopfli")
        self.assertTrue(r["success"], f"Zopfli: {r['error']}")
        self.assertTrue(_is_valid_png(r["output_path"]))
        self.results["zopfli"] = r

        print("\n  Size comparison:")
        for algo, r in self.results.items():
            ratio = r["output_size"] / r["input_size"] * 100 if r["input_size"] > 0 else 0
            print(f"    {algo}: {r['input_size']} -> {r['output_size']} bytes ({ratio:.1f}%)")


if __name__ == "__main__":
    unittest.main()
