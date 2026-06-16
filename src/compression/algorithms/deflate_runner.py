"""
Deflate baseline PNG recompression using Python standard library only.
"""

from pathlib import Path
import binascii
import struct
import zlib


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def run_deflate(input_path, output_dir):
    """Recompress PNG IDAT data with zlib and write output file."""
    input_file = Path(input_path)
    output_folder = Path(output_dir)
    output_file = output_folder / input_file.name

    chunks = _read_png_chunks(input_file)
    idat_data = b"".join(data for chunk_type, data in chunks if chunk_type == b"IDAT")
    if not idat_data:
        raise ValueError("PNG tidak memiliki IDAT chunk.")

    raw_image_data = zlib.decompress(idat_data)
    compressed_data = zlib.compress(raw_image_data, level=9)

    _write_png_chunks(output_file, chunks, compressed_data)
    return output_file


def _read_png_chunks(input_file):
    """Read PNG chunks from a file."""
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
                raise ValueError(f"CRC PNG tidak valid pada chunk {chunk_type.decode('ascii', 'replace')}.")

            chunks.append((chunk_type, data))
            if chunk_type == b"IEND":
                break

    return chunks


def _write_png_chunks(output_file, chunks, compressed_data):
    """Write PNG chunks, replacing all original IDAT chunks with one new IDAT."""
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
    """Write a PNG chunk with a recalculated CRC."""
    target.write(struct.pack(">I", len(data)))
    target.write(chunk_type)
    target.write(data)
    crc = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
    target.write(struct.pack(">I", crc))
