"""
OxiPNG runner placeholder.
"""

from pathlib import Path
import shutil


def run_oxipng(input_path, output_dir):
    """Detect oxipng executable and fail gracefully until wrapper is implemented."""
    executable = shutil.which("oxipng")
    if executable is None:
        raise RuntimeError("Executable oxipng tidak ditemukan di PATH.")

    input_file = Path(input_path)
    Path(output_dir)
    raise RuntimeError(
        f"Wrapper oxipng belum diimplementasikan untuk {input_file.name}; executable terdeteksi: {executable}."
    )
