"""
Zopfli runner — real PNG recompression using zopfli Python package.

Produces real PNG output (not .gz) by reading the input PNG's IDAT data,
decompressing it, and re-compressing with the zopfli algorithm via the
zopfli.zlib Python module.

Always returns a result dict — never raises.
"""

from pathlib import Path
import binascii
import struct
import zlib
import signal

from src.utils.config import ZOPFLI_TIMEOUT, ZOPFLI_MAX_ITERATIONS


# ---------------------------------------------------------------------------
# Timeout helper via signal (Unix) or simple fallback
# ---------------------------------------------------------------------------

class _TimeoutError(Exception):
    pass


def _apply_timeout(func, args, timeout):
    """Run a function with a timeout in seconds.

    On Unix uses signal.SIGALRM. On Windows signal.alarm is not available
    so the operation runs without a hard timeout; the comparison runner's
    overall progress tracking will surface excessive delays.

    When timeout is None or <= 0, runs without any timeout.
    """
    if not timeout or timeout <= 0:
        return func(*args)

    if hasattr(signal, "SIGALRM"):
        # Unix: use SIGALRM
        timeout_int = int(timeout)

        def _handler(signum, frame):
            raise _TimeoutError(f"Zopfli timeout after {timeout_int}s")

        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(timeout_int)
        try:
            result = func(*args)
            signal.alarm(0)
            return result
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
    else:
        # Windows: no SIGALRM — run normally
        return func(*args)


def run_zopfli(input_path, output_dir, timeout=ZOPFLI_TIMEOUT, max_iterations=ZOPFLI_MAX_ITERATIONS):
    """Re-compress one PNG's IDAT with zopfli and write a real PNG output.

    Reads PNG chunks, decompresses IDAT with zlib, re-compresses the raw
    image data with zopfli.zlib.compress(), and writes a new PNG file.

    Args:
        input_path: Path to input PNG.
        output_dir: Directory for output PNG.
        timeout: Per-file timeout in seconds (default from config).
        max_iterations: Zopfli iteration count (default from config).

    Returns a dict with keys: success, output_path, error.
    """
    input_file = Path(input_path)
    output_folder = Path(output_dir)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / input_file.name

    if not input_file.is_file():
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"Input file tidak ditemukan: {input_file}",
        }

    try:
        chunks = _read_png_chunks(input_file)
    except (ValueError, OSError) as exc:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"Gagal membaca PNG: {exc}",
        }

    idat_data = b"".join(
        data for chunk_type, data in chunks if chunk_type == b"IDAT"
    )
    if not idat_data:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "PNG tidak memiliki IDAT chunk.",
        }

    try:
        raw_image_data = zlib.decompress(idat_data)
    except zlib.error as exc:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"Gagal decompress IDAT: {exc}",
        }

    try:
        import zopfli.zlib
        compressed_data = _apply_timeout(
            lambda: zopfli.zlib.compress(raw_image_data, numiterations=max_iterations),
            (),
            timeout,
        )
    except ImportError:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "zopfli Python package tidak terinstal. Jalankan: pip install zopfli",
        }
    except _TimeoutError:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"Zopfli timeout setelah {timeout} detik.",
        }
    except Exception as exc:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"Gagal compress dengan zopfli: {exc}",
        }

    try:
        _write_png_chunks(output_file, chunks, compressed_data)
    except OSError as exc:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"Gagal menulis output PNG: {exc}",
        }

    if not output_file.is_file() or output_file.stat().st_size == 0:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "Output PNG gagal dibuat atau kosong.",
        }

    return {
        "success": True,
        "output_path": str(output_file),
        "error": None,
    }


# ---------------------------------------------------------------------------
# PNG chunk I/O  (shared pattern with deflate_runner.py)
# ---------------------------------------------------------------------------

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _read_png_chunks(input_file):
    """Read all PNG chunks from a file, return list of (type, data)."""
    with input_file.open("rb") as source:
        signature = source.read(len(PNG_SIGNATURE))
        if signature != PNG_SIGNATURE:
            raise ValueError("Input bukan file PNG valid.")

        chunks = []
        while True:
            length_bytes = source.read(4)
            if not length_bytes:
                break
            if len(length_bytes) != 4:
                raise ValueError("PNG chunk length rusak.")

            length = struct.unpack(">I", length_bytes)[0]
            chunk_type = source.read(4)
            data = source.read(length)
            crc = source.read(4)

            if len(chunk_type) != 4 or len(data) != length or len(crc) != 4:
                raise ValueError("PNG chunk rusak atau tidak lengkap.")

            expected_crc = struct.unpack(">I", crc)[0]
            actual_crc = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
            if expected_crc != actual_crc:
                raise ValueError(
                    f"CRC tidak valid pada chunk "
                    f"{chunk_type.decode('ascii', 'replace')}."
                )

            chunks.append((chunk_type, data))
            if chunk_type == b"IEND":
                break

    return chunks


def _write_png_chunks(output_file, chunks, compressed_data):
    """Write PNG chunks, replacing IDAT with the new compressed data."""
    wrote_idat = False
    with output_file.open("wb") as target:
        target.write(PNG_SIGNATURE)
        for chunk_type, data in chunks:
            if chunk_type == b"IDAT":
                if not wrote_idat:
                    _write_chunk(target, b"IDAT", compressed_data)
                    wrote_idat = True
                continue
            _write_chunk(target, chunk_type, data)


def _write_chunk(target, chunk_type, data):
    """Write one PNG chunk with recalculated CRC."""
    target.write(struct.pack(">I", len(data)))
    target.write(chunk_type)
    target.write(data)
    crc = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
    target.write(struct.pack(">I", crc))
