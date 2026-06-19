"""
Unit tests for src.utils.dataset_loader
"""

import unittest
import tempfile
from pathlib import Path
from PIL import Image

from src.utils.dataset_loader import scan_png_folder, validate_dataset


class TestScanPngFolder(unittest.TestCase):
    """Tests for scan_png_folder()"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_png(self, name, size=(4, 4)):
        """Create a minimal valid PNG in tmpdir."""
        path = self.tmpdir / name
        img = Image.new("RGB", size, (255, 0, 0))
        img.save(path, format="PNG")
        return path

    # ---------- happy path ----------

    def test_scan_finds_png_files(self):
        self._make_png("a.png")
        self._make_png("b.png")
        result = scan_png_folder(self.tmpdir)
        self.assertEqual(len(result), 2)

    def test_scan_returns_sorted(self):
        self._make_png("z.png")
        self._make_png("a.png")
        result = scan_png_folder(self.tmpdir)
        names = [p.name for p in result]
        self.assertEqual(names, sorted(names))

    # ---------- invalid input ----------

    def test_scan_non_existent_folder(self):
        result = scan_png_folder("/path/that/does/not/exist")
        self.assertEqual(result, [])

    def test_scan_file_path_instead_of_folder(self):
        png = self._make_png("test.png")
        result = scan_png_folder(png)
        self.assertEqual(result, [])

    def test_scan_ignores_non_png(self):
        self._make_png("good.png")
        (self.tmpdir / "not_image.txt").write_text("hello")
        result = scan_png_folder(self.tmpdir)
        self.assertEqual(len(result), 1)

    def test_scan_ignores_hidden_dotfile(self):
        self._make_png("visible.png")
        self._make_png(".hidden.png")
        result = scan_png_folder(self.tmpdir)
        self.assertEqual(len(result), 1)

    def test_scan_ignores_hidden_dotfolder(self):
        hidden = self.tmpdir / ".secret"
        hidden.mkdir()
        img = Image.new("RGB", (2, 2), (0, 255, 0))
        img.save(str(hidden / "inner.png"), format="PNG")
        self._make_png("visible.png")
        result = scan_png_folder(self.tmpdir)
        self.assertEqual(len(result), 1)

    def test_scan_corrupted_png_ignored(self):
        self._make_png("good.png")
        bad = self.tmpdir / "bad.png"
        bad.write_bytes(b"\x89PNG\x0d\x0a\x1a\x0a" + b"\x00" * 20)
        result = scan_png_folder(self.tmpdir)
        self.assertEqual(len(result), 1)

    # ---------- empty dataset ----------

    def test_scan_empty_folder(self):
        result = scan_png_folder(self.tmpdir)
        self.assertEqual(result, [])

    # ---------- cancellation ----------

    def test_scan_cancellation(self):
        self._make_png("a.png")
        self._make_png("b.png")
        result = scan_png_folder(self.tmpdir, cancel_check=lambda: True)
        self.assertIsNone(result)


class TestValidateDataset(unittest.TestCase):
    """Tests for validate_dataset()"""

    def test_valid_with_10_files(self):
        files = [Path(f"file{i}.png") for i in range(10)]
        valid, msg = validate_dataset(files)
        self.assertTrue(valid)
        self.assertIn("Dataset valid", msg)

    def test_valid_with_more_than_10(self):
        files = [Path(f"file{i}.png") for i in range(15)]
        valid, msg = validate_dataset(files)
        self.assertTrue(valid)
        self.assertIn("Dataset valid", msg)

    def test_invalid_empty(self):
        valid, msg = validate_dataset([])
        self.assertFalse(valid)
        self.assertIn("belum valid", msg)

    def test_invalid_less_than_10(self):
        files = [Path(f"file{i}.png") for i in range(5)]
        valid, msg = validate_dataset(files)
        self.assertFalse(valid)
        self.assertIn("minimal", msg)


if __name__ == "__main__":
    unittest.main()
