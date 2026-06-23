"""
OxiPNG runner — real subprocess execution.

Executable discovery priority:
1. tools/oxipng/oxipng.exe
2. PATH environment (shutil.which)

Always returns a result dict — never raises.
"""

from pathlib import Path
import shutil
import subprocess

from src.utils.logger import Logger
from src.utils.config import OXIPNG_TIMEOUT


PROJECT_TOOLS = Path(__file__).resolve().parents[3] / "tools" / "oxipng"
EXECUTABLE_CANDIDATES = []

# Windows
for name in ("oxipng.exe", "oxipng"):
    candidate = PROJECT_TOOLS / name
    if candidate.is_file():
        EXECUTABLE_CANDIDATES.append(str(candidate))

_logger = Logger()


def _find_executable():
    """Locate oxipng executable with priority: tools/ > PATH.

    Returns (path | None, source_label).
    """
    # Priority 1 — tools/oxipng/
    for candidate in EXECUTABLE_CANDIDATES:
        path = Path(candidate)
        if path.is_file():
            return str(path), f"tools/oxipng/{path.name}"

    # Priority 2 — PATH
    which = shutil.which("oxipng")
    if which:
        return which, "PATH"

    return None, None


def run_oxipng(input_path, output_dir, timeout=OXIPNG_TIMEOUT):
    """Re-compress one PNG with oxipng via subprocess.

    Args:
        input_path: Path to input PNG.
        output_dir: Directory for output PNG.
        timeout: Subprocess timeout in seconds (default from config).

    Returns a dict with keys: success, output_path, error.
    """
    input_file = Path(input_path)
    output_folder = Path(output_dir)
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / input_file.name

    executable, source = _find_executable()
    if executable is None:
        _logger.warn("tool_not_found", "oxipng not found in tools/ or PATH")
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "Executable oxipng tidak ditemukan. "
                     "Letakkan oxipng.exe di tools/oxipng/ atau pastikan tersedia di PATH.",
        }

    _logger.info("tool_detected",
                 f"oxipng source={source} path={executable}")

    cmd = [executable, "-o", "4", "--out", str(output_file), str(input_file)]
    _logger.info("oxipng_command", f"cmd={' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Log full details for debugging
        _logger.info("oxipng_result",
                     f"cmd={' '.join(cmd)} "
                     f"returncode={result.returncode} "
                     f"stdout={result.stdout.strip()} "
                     f"stderr={result.stderr.strip()} "
                     f"output_exists={output_file.is_file()}")

        if result.returncode != 0:
            error_msg = result.stderr.strip() or f"oxipng exit code {result.returncode}"
            return {
                "success": False,
                "output_path": str(output_file),
                "error": error_msg,
            }

        if not output_file.is_file():
            return {
                "success": False,
                "output_path": str(output_file),
                "error": "oxipng selesai tetapi file output tidak ditemukan.",
            }

        # Verify output is a valid PNG
        try:
            with open(output_file, "rb") as f:
                sig = f.read(len(b"\x89PNG\r\n\x1a\n"))
            if sig != b"\x89PNG\r\n\x1a\n":
                return {
                    "success": False,
                    "output_path": str(output_file),
                    "error": "oxipng output bukan PNG valid.",
                }
        except OSError as exc:
            return {
                "success": False,
                "output_path": str(output_file),
                "error": f"Gagal verifikasi output: {exc}",
            }

        return {
            "success": True,
            "output_path": str(output_file),
            "error": None,
        }

    except FileNotFoundError:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "oxipng executable tidak ditemukan saat menjalankan subprocess.",
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "oxipng timeout setelah 120 detik.",
        }
    except PermissionError:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": "oxipng: Permission denied.",
        }
    except OSError as exc:
        return {
            "success": False,
            "output_path": str(output_file),
            "error": f"oxipng: {exc}",
        }
