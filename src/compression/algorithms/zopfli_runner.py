"""
Zopfli runner placeholder.
"""

from pathlib import Path
import shutil


def run_zopfli(input_path, output_dir):
    """Detect zopfli executable and fail gracefully until wrapper is implemented."""
    executable = shutil.which("zopfli")
    if executable is None:
        raise RuntimeError("Executable zopfli tidak ditemukan di PATH.")

    input_file = Path(input_path)
    Path(output_dir)
    raise RuntimeError(
        f"Wrapper zopfli belum diimplementasikan untuk {input_file.name}; executable terdeteksi: {executable}."
    )
