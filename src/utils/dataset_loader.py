"""
Dataset loading utilities for PNG input folders.
"""

from pathlib import Path

from PIL import Image, UnidentifiedImageError


MINIMUM_PNG_FILES = 10


def _is_hidden(path):
    """Return True when any path segment is hidden by dot-prefix."""
    return any(part.startswith(".") for part in path.parts)


def _is_valid_png(path):
    """Verify that a PNG file can be opened by Pillow."""
    try:
        with Image.open(path) as image:
            image.verify()
            return image.format == "PNG"
    except (OSError, UnidentifiedImageError):
        return False


def scan_png_folder(path, cancel_check=None):
    """
    Recursively scan a folder for readable PNG files.

    Hidden files/folders, non-PNG files, and corrupted images are ignored.
    """
    folder = Path(path)
    if not folder.is_dir():
        return []

    png_files = []
    for file_path in folder.rglob("*"):
        if cancel_check and cancel_check():
            return None
        if not file_path.is_file():
            continue
        if _is_hidden(file_path.relative_to(folder)):
            continue
        if file_path.suffix.lower() != ".png":
            continue
        if not _is_valid_png(file_path):
            continue
        png_files.append(file_path)

    return sorted(png_files, key=lambda item: str(item).lower())


def validate_dataset(files):
    """Validate that the dataset contains the required minimum PNG files."""
    file_count = len(files)
    if file_count < MINIMUM_PNG_FILES:
        return (
            False,
            f"Dataset belum valid: ditemukan {file_count} PNG, minimal {MINIMUM_PNG_FILES}.",
        )

    return True, f"Dataset valid: ditemukan {file_count} PNG."
