# PNG Compression Comparison System

**Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI**

Aplikasi desktop berbasis Python untuk membandingkan efektivitas tiga algoritma kompresi PNG secara batch. Dirancang untuk eksperimen akademik dengan dataset terkontrol, aplikasi ini menyediakan GUI lengkap dengan preview side-by-side, metrics real-time, dan export CSV.

---

## Features

### 1. Dataset Management
- **Folder picker** — Pilih folder dataset PNG via dialog
- **Auto-scan** — Scan recursive folder, filter hanya file PNG valid
- **Validasi** — Minimum 10 file PNG, abaikan file hidden/corrupted
- **File count** — Tampilkan jumlah dan daftar file

### 2. Batch Compression
- **Sequential processing** — Kompresi semua file satu per satu
- **3 algoritma** — Deflate Baseline, Zopfli Deflate, OxiPNG
- **Progress bar** — Update real-time 0–100%
- **Cancel** — Batalkan proses; file aktif diselesaikan dulu
- **Partial completion** — Hasil parsial tetap disimpan

### 3. Preview
- **Side-by-side** — Original vs Compressed
- **Aspect ratio** — Fit with LANCZOS resampling
- **Navigasi** — Prev/Next/File List dropdown
- **Transparency support** — RGBA image handling

### 4. Metrics
- **Table view** — File, Algorithm, Original Size, Compressed Size, Reduction %, Time (ms), Resolution, Status
- **Summary bar** — Completed, Failed, Cancelled, Avg Reduction, Avg Time
- **Real-time update** — Metrics muncul per-file selama kompresi

### 5. Export
- **CSV report** — `outputs/reports/report_YYYYMMDD_HHMMSS.csv`
- **Summary section** — completed, failed, cancelled, avg_reduction, avg_time_ms
- **No-overwrite** — Timestamp + counter otomatis
- **Manual export** — Tombol Export aktif setelah batch selesai

### 6. Logging
- **App log** — `logs/app.log` — semua event aplikasi
- **Session log** — `logs/session_YYYYMMDD_HHMMSS.log` — ringkasan per batch
- **Graceful failure** — Logging error tidak crash aplikasi

### 7. Error Handling
- File corrupted → skip, tandai FAILED, lanjut
- File non-PNG → abaikan
- Export gagal → tampilkan error di status bar
- Kompresi gagal → catat metrics dengan status FAILED

---

## Architecture

### GUI Architecture

```
CompressionApp (Main Window — tk.Tk)
│
├── HeaderComponent
│   └── Title & Subtitle
│
├── FolderPickerComponent
│   ├── Browse Button
│   ├── Folder Path Display
│   └── File Counter + Validation Status
│
├── ControlPanelComponent
│   ├── Start Compression Button
│   ├── Cancel Button
│   ├── Export Results Button
│   ├── Progress Bar (0-100%)
│   └── Status Label
│
├── PreviewComponent (Side-by-side)
│   ├── Original Image Panel
│   └── Compressed Image Panel
│
├── FileSelectorComponent
│   ├── File List (Combobox)
│   ├── Previous / Next Buttons
│   └── Position Counter
│
└── MetricsPanelComponent
    └── Treeview Table
        ├── File, Algorithm, Original Size
        ├── Compressed Size, Reduction %
        ├── Time (ms), Resolution, Status
        └── Summary Bar
```

### Module Structure

```
src/
├── main.py                          # Entry point
├── ui/
│   ├── app.py                       # Main GUI (CompressionApp)
│   ├── components_header.py         # Header section
│   ├── components_folder_picker.py  # Folder selection
│   ├── components_control.py        # Buttons & progress
│   ├── components_preview.py        # Image preview
│   ├── components_file_selector.py  # File navigation
│   └── components_metrics.py        # Metrics table
├── compression/
│   ├── compressor.py                # Compression dispatcher
│   └── algorithms/
│       ├── deflate_runner.py        # Deflate (zlib)
│       ├── zopfli_runner.py         # Zopfli (placeholder)
│       └── oxipng_runner.py         # OxiPNG (placeholder)
├── processing/
│   └── batch_processor.py           # Batch compression engine
├── analysis/
│   └── analyzer.py                  # Metrics calculation
├── export/
│   └── exporter.py                  # CSV export
└── utils/
    ├── config.py                    # GUI constants
    ├── dataset_loader.py            # PNG folder scanner
    └── logger.py                    # Structured logging
```

### Data Flow

```
Folder Dipilih
    ↓
Dataset Loader → scan_png_folder()
    ↓
File List → FileSelector + Preview
    ↓
Start Compression
    ↓
Batch Processor → loop per file
    ├─→ Compressor → Deflate/Zopfli/OxiPNG
    ├─→ Analyzer → build_metric()
    └─→ Progress Callback → UI update
    ↓
Selesai → Metrics + Summary + Preview
    ↓
Export → CSV report (report_YYYYMMDD_HHMMSS.csv)
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **GUI** | Tkinter (ttk.Themed) |
| **Image Processing** | Pillow (PIL) |
| **Deflate** | zlib (stdlib) |
| **CSV** | csv (stdlib) |
| **Logging** | Custom file-based |
| **Threading** | threading (stdlib) |
| **Config** | Python constants module |

---

## How To Run

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- Virtual environment (disarankan)

### Quick Start

```bash
# 1. Clone project
cd uas-kompresi-png

# 2. Create virtual environment
python -m venv .venv

# 3. Activate
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run aplikasi
python src/main.py
```

### Dependencies

See [requirements.txt](requirements.txt) for full list.

| Package | Version | Fungsi |
|---------|---------|--------|
| Pillow | 12.1.1 | Image processing & preview |
| pandas | 3.0.1 | Data analysis & CSV |
| matplotlib | 3.10.8 | Visualization & charts |
| numpy | 2.4.2 | Numerical computations |
| zopfli | 0.4.3 | Zopfli compression |

> **Catatan:** Eksekusi langsung hanya untuk **Deflate Baseline** (zlib). Zopfli dan OxiPNG masih berupa placeholder yang membutuhkan binary eksternal di `tools/`.

### Directory Structure

```
uas-kompresi-png/
├── docs/                  # Dokumentasi proyek
├── src/                   # Source code
├── dataset/               # Input PNG files
├── outputs/               # Hasil kompresi
│   ├── deflate/
│   ├── zopfli/
│   ├── oxipng/
│   └── reports/
├── tools/                 # External binaries (opsional)
├── tests/                 # Unit tests
├── logs/                  # Application logs
├── assets/                # Static assets
├── requirements.txt
└── README.md
```

---

## Dataset Rules

### Minimum Requirements

- **Minimal 10 file PNG** valid
- Format: **hanya .png** (non-PNG diabaikan)
- File hidden (dot-prefix) diabaikan
- File corrupted otomatis di-skip

### Recommended Composition

Agar hasil eksperimen tidak bias, disarankan:

| Kategori | Jumlah | Contoh |
|----------|--------|--------|
| Photo | 3 file | Foto pemandangan, portrait |
| Screenshot | 3 file | Screenshot UI, web, aplikasi |
| Illustration | 2 file | Ilustrasi digital, vector-to-PNG |
| Transparency | 2 file | Gambar dengan alpha channel |

Total: **10+ file PNG** dengan variasi karakteristik.

### Validation Rules

- Aplikasi akan menampilkan **warning** jika < 10 file
- Tombol **Compress** tidak aktif sampai dataset valid
- File tidak diubah, di-resize, atau di-crop selama kompresi

---

## Testing

### Running Tests

```bash
# Aktifkan virtual environment dulu
.venv\Scripts\activate

# Jalankan semua test
python -m unittest discover -s tests -v
```

### Test Coverage

| Test File | Coverage | Test Count |
|-----------|----------|------------|
| `test_dataset_loader.py` | scan_png_folder (happy path, empty, hidden, corrupted, non-PNG, non-existent), validate_dataset | 13 |
| `test_compressor.py` | compress_file (success, non-existent, non-PNG, unknown algorithm, aliases, output dir creation) | 9 |
| `test_batch_processor.py` | process_dataset (3 files, empty, cancel immediate, cancel partial, single file, progress callbacks) | 7 |
| `test_metrics.py` | build_metric (success, failed, zero input, unreadable, labels), summarize_metrics (all success, with failed, cancelled, empty, all failed) | 13 |
| `test_exporter.py` | export_metrics_csv (creates CSV, header, data, summary, no-overwrite, multiple, empty, output dir), _build_report_path, _format_metric_row, _bytes_to_kb | 13 |
| `test_logger.py` | All 8 events no-crash, session log, permission error skip, invalid path | 17 |

**Total: 73 unit tests — all passing.**

### Test Scenarios Covered

- ✅ Happy path — kompresi normal
- ✅ Invalid input — file corrupted, non-PNG, non-existent
- ✅ Empty dataset — folder kosong
- ✅ Cancel flow — cancel immediate, cancel setelah 1 file
- ✅ Export output — CSV format, no-overwrite
- ✅ Metrics calculation — reduction %, average, cancelled flag
- ✅ Logging no-crash — permission error, invalid path
- ✅ Edge cases — zero size, all failed, alias algorithms

---

## Output Example

### CSV Report (`outputs/reports/report_20260616_143022.csv`)

```
file,algorithm,original_size_kb,compressed_size_kb,reduction_percent,time_ms,resolution,status
photo1.png,Deflate Baseline,1024.5000,512.2500,50.0000,150.5000,1920x1080,SUCCESS
screenshot1.png,Deflate Baseline,2048.0000,1024.0000,50.0000,200.7500,2560x1440,SUCCESS

,completed,failed,cancelled,avg_reduction,avg_time_ms
summary
completed,2,,,,
failed,0,,,,
cancelled,False,,,,
avg_reduction,50.0000,,,,
avg_time_ms,175.6250,,,,
```

### Session Log (`logs/session_20260616_143022.log`)

```
dataset=C:\Users\user\dataset-png
algorithm=deflate
completed=10
failed=0
avg_reduction=45.2500
avg_time_ms=180.3000
```

### App Log (`logs/app.log`)

```
2026-06-16 14:30:00 | INFO | app_start | PNG Compression Comparison System started
2026-06-16 14:30:15 | INFO | dataset_loaded | path=C:\Users\user\dataset-png count=10 valid=yes
2026-06-16 14:30:20 | INFO | compression_started | algorithm=deflate total_files=10
2026-06-16 14:32:45 | INFO | compression_finished | completed=10 failed=0 avg_reduction=45.25% avg_time=180.30ms
2026-06-16 14:32:50 | INFO | export_success | path=outputs\reports\report_20260616_143022.csv
```

### GUI Layout

```
┌──────────────────────────────────────────────────────────────┐
│ PNG COMPRESSION COMPARISON SYSTEM                           │
│ Studi Komparasi Tiga Algoritma Kompresi PNG...              │
├──────────────────────────────────────────────────────────────┤
│ DATASET SELECTION                                           │
│ Selected Folder: C:\dataset\  [ Browse Folder ]   Files: 10 │
│ Dataset valid: ditemukan 10 PNG.                            │
├──────────────────────────────────────────────────────────────┤
│ COMPRESSION CONTROL                                         │
│ [▶ Start] [⏹ Cancel] [📊 Export]  ████████░░░  80%        │
│ Status: Selesai 8/10: photo3.png                            │
├─────────────────────────┬────────────────────────────────────┤
│ PREVIEW RESULTS          │ FILE NAVIGATION                  │
│ ┌──────┐ ┌──────┐       │ [photo1.png        ▼]            │
│ │ORIG  │ │COMP  │       │ [◀ Previous] [Next ▶]           │
│ │      │ │      │       │ Position: 3/10                   │
│ └──────┘ └──────┘       │                                    │
│                          │                                    │
│ COMPRESSION METRICS      │                                    │
│ ┌──────┬────┬────┬───┬──┤                                    │
│ │File  │Algo│Orig│Red│% │                                    │
│ ├──────┼────┼────┼───┼──┤                                    │
│ │p1.png│Def │... │...│% │                                    │
│ │ ...  │    │    │   │  │                                    │
│ └──────┴────┴────┴───┴──┘                                    │
│ Completed: 8 | Failed: 0 | Cancelled: No | Avg Red: 45.25%   │
└──────────────────────────────────────────────────────────────┘
```

---

## Known Limitations

### 1. Algorithm Placeholders
- **Zopfli** dan **OxiPNG** masih berupa **placeholder runner** (me-raise `RuntimeError` dengan pesan executable tidak ditemukan).
- Hanya **Deflate Baseline** (zlib) yang berfungsi penuh saat ini.
- Untuk mengaktifkan Zopfli/OxiPNG, binary eksternal harus diletakkan di `tools/` atau tersedia di PATH.

### 2. GUI Threading
- Worker thread menggunakan `daemon=True`. Jika aplikasi ditutup saat kompresi berjalan, thread akan dipotong paksa dan file yang sedang diproses mungkin tidak selesai.
- Belum ada mekanisme `join(timeout)` pada `_on_close`.

### 3. Platform-Specific
- **Windows:** `PermissionError` testing untuk logging tidak optimal (chmod terbatas).
- **Path:** Menggunakan `pathlib.Path` yang cross-platform, namun beberapa test menggunakan absolute path Unix-style.

### 4. Grafik Belum Implementasi
- `size_comparison.png` dan `time_comparison.png` (matplotlib) **belum diimplementasi**.
- Export saat ini hanya CSV.
- Grafik ditandai sebagai `(future)` di TASKS.md.

### 5. Single Algorithm per Run
- Batch compression hanya menjalankan **satu algoritma** per run (default: `deflate`).
- Belum ada fitur "run all algorithms sequentially" dalam satu klik.
- User harus mengganti algoritma dan menjalankan ulang secara manual.

### 6. No GUI Component Tests
- Unit tests hanya mencakup **logic layer** (compression, analysis, export, logging).
- GUI components (button state, event binding, rendering) tidak memiliki automated test.
- Testing GUI membutuhkan framework seperti `pytest-qt` atau manual verification.

### 7. Dataset
- Folder `dataset/` belum terisi (hanya berisi `.gitkeep`).
- User harus menyediakan file PNG sendiri untuk testing.
- Minimal 10 file PNG diperlukan untuk validasi.

### 8. Dependency
- `zopfli` (Python package) dan `oxipng` (binary) tidak terinstal secara default.
- `requirements.txt` menyertakan `zopfli==0.4.3` (Python wrapper), tapi binary eksternal `oxipng` harus diinstal manual.

---

## Status

**MILESTONE 0–9: ✅ COMPLETED**

| Milestone | Status |
|-----------|--------|
| M0 — Project Setup | ✅ |
| M1 — GUI Foundation | ✅ |
| M2 — Dataset Loader | ✅ |
| M3 — Compression Engine | ✅ |
| M4 — Batch Processor | ✅ |
| M5 — Metrics Engine | ✅ |
| M6 — Result Viewer | ✅ |
| M7 — Export System | ✅ |
| M8 — Logging & Error Handling | ✅ |
| M9 — Testing & Polish | ✅ |

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/PRD.md](docs/PRD.md) | Product Requirement Document |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Technical Requirements |
| [docs/EXPERIMENT.md](docs/EXPERIMENT.md) | Experiment Plan |
| [docs/TASKS.md](docs/TASKS.md) | Task Breakdown & Milestones |
| [docs/GUI_ARCHITECTURE.md](docs/GUI_ARCHITECTURE.md) | GUI Architecture |
| [docs/REPORT_OUTLINE.md](docs/REPORT_OUTLINE.md) | Laporan UAS Outline |

---

## Author

UAS — Sistem Multimedia — Semester 6

## License

Proprietary — UAS Assignment
