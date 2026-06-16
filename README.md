# PNG Compression Comparison System

Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI

## Deskripsi Proyek

Aplikasi desktop berbasis Python untuk membandingkan efektivitas tiga algoritma kompresi PNG:

1. **Deflate Baseline** - Encoder standar sebagai pembanding utama
2. **Zopfli Deflate** - Optimasi encoding yang lebih agresif
3. **OxiPNG** - Optimasi kompresi melalui filter dan strategi encoding

## Status

**MILESTONE 0: PROJECT SETUP** ✅ COMPLETED

## Struktur Direktori

```
uas-kompresi-png/
├── docs/                  # Dokumentasi proyek
│   ├── PRD.md            # Product Requirement Document
│   ├── REQUIREMENTS.md   # Technical Requirements
│   ├── EXPERIMENT.md     # Experiment Plan
│   ├── TASKS.md          # Task Breakdown
│   └── REPORT_OUTLINE.md # Report Outline
├── src/                  # Source code
│   ├── __init__.py       # Package marker
│   ├── main.py           # Entry point aplikasi
│   ├── ui/               # Tkinter GUI components
│   │   ├── __init__.py
│   │   └── app.py        # Main GUI application
│   ├── compression/      # Compression algorithms
│   │   ├── __init__.py
│   │   └── compressor.py # Compressor classes
│   ├── analysis/         # Results analysis
│   │   ├── __init__.py
│   │   └── analyzer.py   # Data analysis & reporting
│   └── utils/            # Helper utilities
│       ├── __init__.py
│       └── logger.py     # Logging utilities
├── dataset/              # Input PNG files
│   ├── photo/           # Photo category
│   ├── screenshot/       # Screenshot category
│   ├── illustration/     # Illustration category
│   └── transparency/     # Transparent images category
├── outputs/              # Compressed images & reports
│   ├── deflate/         # Deflate results
│   ├── zopfli/          # Zopfli results
│   ├── oxipng/          # OxiPNG results
│   └── reports/         # CSV & charts
├── tools/                # External compression binaries
├── assets/               # Static assets
├── tests/                # Unit tests
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── run.py               # Quick start script
└── README.md            # This file
```

## Kebutuhan Sistem

- Python 3.11 atau lebih tinggi
- pip (Python package manager)
- Virtual environment (disarankan)

## Instalasi

### 1. Clone/Setup Project

```bash
cd uas-kompresi-png
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

### Quick Start

```bash
python run.py
```

### Manual

```bash
python src/main.py
```

## Dependencies

Lihat [requirements.txt](requirements.txt) untuk daftar lengkap dependencies.

### Core Libraries:

- **Pillow** - Image processing
- **pandas** - Data analysis & CSV export
- **matplotlib** - Visualization & chart generation
- **zopfli** - Zopfli compression algorithm
- **numpy** - Numerical computations

### External Tools (Manual Installation Required):

- **oxipng** - PNG optimization tool (install manual ke folder `tools/`)

## Milestone Roadmap

### ✅ MILESTONE 0: PROJECT SETUP (COMPLETED)

- [x] Struktur folder lengkap
- [x] Package modules siap
- [x] Requirements validated
- [x] .gitignore configured
- [x] Project ready for development

**Status:** READY FOR MILESTONE 1

### ⏳ MILESTONE 1: GUI FOUNDATION

Membangun antarmuka aplikasi desktop dengan Tkinter.

### ⏳ MILESTONE 2: DATASET LOADER

Membaca dan memvalidasi file PNG dari folder.

### ⏳ MILESTONE 3: COMPRESSION IMPLEMENTATION

Mengintegrasikan tiga algoritma kompresi.

### ⏳ MILESTONE 4: RESULTS ANALYSIS

Analisis hasil dan pembuatan laporan otomatis.

### ⏳ MILESTONE 5: TESTING & DOCUMENTATION

Testing dan dokumentasi final.

## Dataset Requirements

Dataset harus terdiri dari 4 kategori:

- **Photo** (3 file) - Gambar fotografi
- **Screenshot** (3 file) - Screenshot layar
- **Illustration** (2 file) - Ilustrasi/grafis
- **Transparency** (2 file) - Gambar dengan transparansi

Minimal **10 file PNG** untuk eksperimen valid.

## Output

Aplikasi menghasilkan:

1. **Compressed Images** - Hasil kompresi dalam masing-masing folder algoritma
2. **CSV Report** - `compression_results.csv` dengan metrics lengkap
3. **Charts** - Visualisasi perbandingan dalam format PNG

## Dokumentasi

- [PRD.md](docs/PRD.md) - Product requirements & objectives
- [REQUIREMENTS.md](docs/REQUIREMENTS.md) - Technical specifications
- [EXPERIMENT.md](docs/EXPERIMENT.md) - Experimental methodology
- [TASKS.md](docs/TASKS.md) - Task breakdown & milestones

## Author

UAS - Sistem Multimedia Semester 6

## License

Proprietary - UAS Assignment
