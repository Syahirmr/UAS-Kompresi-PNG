# PNG Compression Comparison System

**Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI**

Aplikasi desktop berbasis Python untuk membandingkan efektivitas tiga algoritma kompresi PNG secara batch. Menyediakan GUI lengkap dengan side-by-side preview, metrics real-time, comparison dashboard, ranking, dan export CSV + charts otomatis.

---

## Features

### 1. Dataset Management
- **Folder picker** — Pilih folder dataset PNG via dialog
- **Auto-scan** — Scan recursive folder, filter hanya file PNG valid
- **Validasi** — Minimum 10 file PNG, abaikan file hidden/corrupted
- **File count** — Tampilkan jumlah dan daftar file

### 2. Compression Algorithms
| Algorithm | Method | Timeout | Karakteristik |
|-----------|--------|---------|---------------|
| **Deflate Baseline** | zlib (stdlib) | Unlimited | Baseline tercepat |
| **Zopfli Deflate** | zopfli Python package (v0.4.3) | 60s per file | Ukuran terkecil, iterasi 15 |
| **OxiPNG** | oxipng.exe (subprocess) | 120s per file | Kompromi terbaik |

### 3. Single Algorithm Compression
- **Sequential processing** — Kompresi semua file dengan satu algoritma
- **Progress bar** — Update real-time 0–100%
- **Cancel** — Batalkan proses; file aktif diselesaikan dulu
- **Partial completion** — Hasil parsial tetap disimpan
- **Export** — CSV report via tombol Export

### 4. Comparison Dashboard (M10)
- **📊 Run Comparison** — Jalankan ketiga algoritma sekaligus
- **Progress per-algoritma** — [Algorithm 2/3] Zopfli | File 4/10 | 40%
- **ETA estimasi** — Rolling window average, format menit:detik
- **Winner display** — Best Compression, Fastest, Balanced Winner (score 0–100)
- **Auto export** — CSV report + charts otomatis setelah comparison selesai

### 5. Preview
- **Side-by-side** — Original vs Compressed
- **Aspect ratio** — ImageOps.contain dengan LANCZOS resampling
- **Navigasi** — Prev/Next/File List dropdown
- **Transparency support** — RGBA alpha compositing
- **Per-algorithm** — Preview berubah sesuai algoritma yang dipilih (BUG-2 fix)

### 6. Metrics & Ranking
- **Table view** — File, Algorithm, Original Size, Compressed Size, Reduction %, Time (ms), Resolution, Status
- **Comparison Summary tab** — Winner cards (Best Compression, Fastest, Balanced)
- **Ranking tab** — Score 0–100 (50% reduction + 50% speed, normalized)
- **Charts tab** — Reduction % bar chart + Time (ms) bar chart
- **Real-time update** — Metrics muncul per-file selama kompresi

### 7. Export
- **Metrics CSV** — `outputs/reports/report_YYYYMMDD_HHMMSS_mmm.csv`
- **Comparison CSV** — `outputs/reports/comparison_report_YYYYMMDD_HHMMSS_mmm.csv` (dengan score + winners)
- **Charts** — `outputs/charts/reduction_chart_TIMESTAMP.png` dan `time_chart_TIMESTAMP.png`
- **No-overwrite** — Timestamp millisecond precision
- **Auto export** — CSV + charts otomatis setelah comparison

### 8. Logging
- **App log** — `logs/app.log` — semua event aplikasi
- **Session log** — `logs/session_YYYYMMDD_HHMMSS.log` — ringkasan per batch
- **Graceful failure** — Logging error tidak crash aplikasi

### 9. Error Handling
- File corrupted → skip, tandai FAILED, lanjut
- File non-PNG → abaikan
- Timeout per-algoritma → tandai FAILED, lanjut algoritma berikutnya
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
│   ├── [▶ Start Compression] [⏹ Cancel] [📊 Run Comparison] [📊 Export]
│   ├── Algorithm Selector (Deflate | Zopfli | OxiPNG)
│   ├── Zopfli Warning Label
│   ├── Progress Bar (0-100%) + ETA
│   └── Status Label
│
├── PreviewComponent (Side-by-side)
│   ├── Original Image Panel
│   └── Compressed Image Panel
│
├── FileSelectorComponent
│   ├── File List (Combobox)
│   ├── [◀ Previous] [Next ▶]
│   └── Position Counter
│
└── MetricsPanelComponent
    ├── Metrics Tab — Treeview Table (File, Algorithm, Size, Reduction, Time, Status)
    ├── Comparison Summary Tab — Winner Cards
    ├── Ranking Tab — Score Table
    └── Charts Tab — Reduction / Time toggle
```

### Module Structure

```
src/
├── main.py                          # Entry point
├── ui/
│   ├── app.py                       # Main GUI (CompressionApp)
│   ├── components_header.py         # Header section
│   ├── components_folder_picker.py  # Folder selection
│   ├── components_control.py        # Buttons, algorithm selector, progress
│   ├── components_preview.py        # Image preview (side-by-side)
│   ├── components_file_selector.py  # File navigation
│   └── components_metrics.py        # Metrics table + comparison dashboard
├── compression/
│   ├── compressor.py                # Compression dispatcher + timeouts
│   ├── comparison_runner.py         # 3-algorithm comparison engine
│   └── algorithms/
│       ├── deflate_runner.py        # Deflate (zlib IDAT re-compression)
│       ├── zopfli_runner.py         # Zopfli (zopfli.zlib package)
│       └── oxipng_runner.py         # OxiPNG (subprocess, tools/ auto-discover)
├── processing/
│   └── batch_processor.py           # Batch compression engine
├── analysis/
│   └── analyzer.py                  # Metrics calculation & summarization
├── export/
│   └── exporter.py                  # CSV export + chart generation + ranking
└── utils/
    ├── config.py                    # GUI constants + algorithm timeouts
    ├── dataset_loader.py            # PNG folder scanner & validator
    └── logger.py                    # Structured logging
```

### Data Flow

```
Folder Dipilih
    ↓
Dataset Loader → scan_png_folder() → validate_dataset()
    ↓
File List → FileSelector + Preview
    ↓
── [Single Algorithm] ──                 ── [Comparison] ──
    ↓                                       ↓
Start Compression                       Run Comparison
    ↓                                       ↓
Batch Processor → loop per file         Comparison Runner
    ↓                                       ↓
Compressor → Deflate/Zopfli/OxiPNG      Algo 1 → Algo 2 → Algo 3
    ↓                                       ↓
Analyzer → build_metric()               Per-algorithm results merged
    ↓                                       ↓
Progress Callback → UI update           Winners + Scores computed
    ↓                                       ↓
Selesai → Metrics + Preview             Charts + CSV auto-export
    ↓
Export → CSV report (manual button)
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **GUI** | Tkinter (ttk.Themed) |
| **Image Processing** | Pillow (PIL) |
| **Deflate** | zlib (stdlib) |
| **Zopfli** | zopfli Python package |
| **OxiPNG** | subprocess (external binary) |
| **Charts** | matplotlib (Agg backend) |
| **CSV** | csv (stdlib) |
| **Logging** | Custom file-based |
| **Threading** | threading (stdlib) |
| **Config** | Python constants module |

---

## Setup

### Prerequisites

- **Python 3.11+** (tested on Python 3.14)
- **pip** (Python package manager)
- Virtual environment (disarankan)

### Install

```bash
# 1. Clone / navigate to project
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
```

### Dependencies

| Package | Version | Fungsi |
|---------|---------|--------|
| Pillow | 12.1.1 | Image processing & preview |
| pandas | 3.0.1 | Data analysis & CSV |
| matplotlib | 3.10.8 | Bar chart generation |
| numpy | 2.4.2 | Numerical computations |
| zopfli | 0.4.3 | Zopfli compression |

### External Tools

**OxiPNG** membutuhkan binary eksternal:
1. Download `oxipng.exe` dari [oxipng releases](https://github.com/shssoichiro/oxipng/releases)
2. Letakkan di `tools/oxipng/oxipng.exe`
   ATAU pastikan tersedia di PATH

### Directory Structure

```
uas-kompresi-png/
├── docs/                  # Dokumentasi proyek
├── src/                   # Source code
├── dataset/
│   └── data1/             # Dataset pengujian (10 PNG, 4 kategori)
├── outputs/
│   ├── deflate/           # Hasil Deflate
│   ├── zopfli/            # Hasil Zopfli
│   ├── oxipng/            # Hasil OxiPNG
│   ├── comparison/        # Hasil per-algoritma dari comparison
│   │   ├── deflate/
│   │   ├── zopfli/
│   │   └── oxipng/
│   ├── charts/            # Chart PNG (timestamped)
│   └── reports/           # CSV reports
├── tools/
│   └── oxipng/            # oxipng.exe (manual download)
├── tests/                 # 128 unit tests
├── logs/                  # Application logs
├── requirements.txt
└── README.md
```

---

## Run

```bash
# Pastikan virtual environment aktif
.venv\Scripts\activate

# Jalankan aplikasi
python -m src.main
```

### Run Tests

```bash
python -m unittest discover -s tests -v
# Expected: 128 tests, 0 failures
```

### Run Comparison (via GUI)

1. Buka aplikasi: `python -m src.main`
2. Klik **Browse Folder** → pilih `dataset/data1`
3. Klik **📊 Run Comparison**
4. Tunggu proses (Deflate → Zopfli → OxiPNG)
5. Lihat hasil di tab **Comparison Summary**, **Ranking**, **Charts**
6. CSV + charts auto-export ke `outputs/reports/` dan `outputs/charts/`

### Export Report

- **Manual:** Setelah single-algorithm compression, klik **📊 Export Results**
- **Otomatis:** Setiap comparison menghasilkan `comparison_report_TIMESTAMP.csv` + charts

---

## Dataset

### Minimum Requirements

- **Minimal 10 file PNG** valid
- Format: **hanya .png** (non-PNG diabaikan)
- File hidden (dot-prefix) diabaikan
- File corrupted otomatis di-skip

### Recommended Composition

| Kategori | Jumlah | File di dataset/data1 |
|----------|--------|----------------------|
| Photo | 3 file | foto1.png, foto2.png, foto3.png |
| Screenshot | 3 file | Screenshot 1.png, Screenshot 2.png, Screenshot 3.png |
| Illustration | 2 file | ilustrasi1.png, ilustrasi2.png |
| Transparency | 2 file | transparan1.png, transparan2.png |

Total: **10 file PNG** dengan variasi karakteristik untuk menghindari bias eksperimen.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No module named 'compression._common'` | Hapus `sys.path.insert(0, ...)` dari `src/main.py` dan `src/ui/app.py` (Python 3.14 stdlib conflict — sudah di-fix) |
| OxiPNG tidak ditemukan | Letakkan `oxipng.exe` di `tools/oxipng/` |
| Zopfli timeout | Batch besar: Zopfli punya timeout 60s per file. Gunakan dataset lebih kecil atau naikkan `ZOPFLI_TIMEOUT` di `src/utils/config.py` |
| GUI tidak muncul | Pastikan display server aktif (Linux: `export DISPLAY=:0`) |
| matplotlib error | Pastikan `matplotlib` terinstal: `pip install matplotlib` |

---

## Testing

### Running Tests

```bash
# Aktifkan virtual environment dulu
.venv\Scripts\activate

# Jalankan semua test
python -m unittest discover -s tests -v
```

### Test Coverage (128 tests)

| Test File | Coverage |
|-----------|----------|
| `test_dataset_loader.py` | scan_png_folder (happy path, empty, hidden, corrupted, non-PNG, non-existent), validate_dataset |
| `test_compressor.py` | compress_file (success, non-existent, non-PNG, unknown algorithm, aliases, output dir creation) |
| `test_batch_processor.py` | process_dataset (3 files, empty, cancel immediate, cancel partial, single file, progress callbacks) |
| `test_metrics.py` | build_metric (success, failed, zero input, unreadable, labels), summarize_metrics (all success, with failed, cancelled, empty, all failed) |
| `test_exporter.py` | export_metrics_csv (creates CSV, header, data, summary, no-overwrite, multiple, empty, output dir, counter fallback), _build_report_path, _format_metric_row, _bytes_to_kb |
| `test_logger.py` | All events no-crash, session log, permission error skip, invalid path |
| `test_oxipng_runner.py` | executable discovery, subprocess, error cases, timeout |
| `test_zopfli_runner.py` | executable discovery, real compression, error cases, timeout |
| `test_comparison.py` | run all algorithms, partial fail, cancel, chart generation, export, winners, ranking scores |
| `test_real_oxipng.py` | Acceptance test with real oxipng binary |
| `test_real_tools.py` | Cross-algorithm real binary acceptance |

---

## Output Structure

```
outputs/
├── deflate/                    # Single Deflate batch
│   └── *.png
├── zopfli/                     # Single Zopfli batch
│   └── *.png
├── oxipng/                     # Single OxiPNG batch
│   └── *.png
├── comparison/                 # Comparison output (3 algoritma)
│   ├── deflate/*.png
│   ├── zopfli/*.png
│   └── oxipng/*.png
├── charts/                     # Chart PNG (timestamped)
│   ├── reduction_chart_20260617_163122_483.png
│   └── time_chart_20260617_163122_483.png
└── reports/                    # CSV reports (timestamped)
    ├── report_20260617_163122_483.csv
    └── comparison_report_20260617_163122_483.csv
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/PRD.md](docs/PRD.md) | Product Requirement Document |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Technical Requirements |
| [docs/EXPERIMENT.md](docs/EXPERIMENT.md) | Experiment Plan |
| [docs/TASKS.md](docs/TASKS.md) | Task Breakdown & Milestones (M0–M11) |
| [docs/GUI_ARCHITECTURE.md](docs/GUI_ARCHITECTURE.md) | GUI Architecture |
| [docs/REPORT_OUTLINE.md](docs/REPORT_OUTLINE.md) | Laporan UAS Outline |

---

## Milestone Status

| Milestone | Status | Description |
|-----------|--------|-------------|
| M0 — Project Setup | ✅ | Structure, venv, dependencies |
| M1 — GUI Foundation | ✅ | Tkinter layout, all components |
| M2 — Dataset Loader | ✅ | PNG scanner, validator |
| M3 — Compression Engine | ✅ | Deflate, Zopfli, OxiPNG runners |
| M4 — Batch Processor | ✅ | Sequential processing, cancel |
| M5 — Metrics Engine | ✅ | Reduction %, time, resolution |
| M6 — Result Viewer | ✅ | Preview, navigation, algorithm switcher |
| M7 — Export System | ✅ | CSV, charts, no-overwrite |
| M8 — Logging & Error | ✅ | Structured logging, error handling |
| M9 — Testing & Polish | ✅ | 128 unit tests, GUI polish |
| M10 — Comparison Dashboard | ✅ | Run all, winners, auto-export |
| M11 — Comparison UX | ✅ | Timeout, ETA, ranking, balanced winner |

---

## Author

UAS — Sistem Multimedia — Semester 6

## License

Proprietary — UAS Assignment
