# TASK BREAKDOWN

Project:
PNG Compression Comparison System

Status:
PLANNING

---

# MILESTONE 0 — PROJECT SETUP

Tujuan:
menyiapkan struktur proyek agar siap dikembangkan.

Checklist:

[x] Buat struktur folder project

[x] Buat virtual environment

[x] Install dependency

[x] Generate requirements.txt

[x] Setup gitignore

[x] Verifikasi aplikasi dapat dijalankan

Output:

* project siap dijalankan
* dependency terinstal

Dependency:
none

Priority:
HIGH

Estimated:
30–60 menit

---

# MILESTONE 1 — GUI FOUNDATION

Tujuan:
membangun tampilan aplikasi desktop.

Checklist:

[x] Buat main window

[x] Buat layout responsive

[x] Tambahkan Folder Picker

[x] Tambahkan tombol Compress

[x] Tambahkan tombol Cancel

[x] Tambahkan tombol Export

[x] Tambahkan area Preview

[x] Tambahkan Progress Bar

[x] Tambahkan panel Metrics

[x] Tambahkan File Selector

Output:

* GUI dapat dibuka
* semua komponen tampil

Dependency:

MILESTONE 0

Priority:
HIGH

Estimated:
2–4 jam

---

# MILESTONE 2 — DATASET LOADER

Tujuan:
membaca dan memvalidasi dataset PNG.

Checklist:

[x] Scan folder

[x] Cari file PNG

[x] Abaikan file non PNG

[x] Hitung jumlah file

[x] Validasi minimum 10 file

[x] Tampilkan warning jika kurang

[x] Tampilkan daftar file

Output:

* dataset berhasil dimuat

Dependency:

MILESTONE 1

Priority:
HIGH

Estimated:
1–2 jam

---

# MILESTONE 3 — COMPRESSION ENGINE

Tujuan:
membuat sistem kompresi.

Checklist:

[x] Implement Deflate Runner

[x] Implement Zopfli Runner

[x] Implement OxiPNG Runner

[x] Setup subprocess executor

[x] Setup output folder

[x] Simpan hasil

[x] Tangani error

Output:

outputs/

deflate/

zopfli/

oxipng/

Dependency:

MILESTONE 2

Priority:
CRITICAL

Estimated:
3–5 jam

---

# MILESTONE 4 — BATCH PROCESSOR

Tujuan:
menjalankan kompresi seluruh dataset.

Checklist:

[x] Loop seluruh file

[x] Jalankan algoritma terpilih

[x] Simpan hasil

[x] Update progress

[x] Implement cancel

[x] Tangani partial completion

Output:

batch compression selesai

Dependency:

MILESTONE 3

Priority:
CRITICAL

Estimated:
2–3 jam

---

# MILESTONE 5 — METRICS ENGINE

Tujuan:
menghasilkan data komparasi.

Checklist:

[x] Hitung ukuran awal

[x] Hitung ukuran akhir

[x] Hitung persentase reduksi

[x] Hitung waktu kompresi

[x] Ambil resolusi

[x] Simpan status

Output:

metrics dataset

Dependency:

MILESTONE 4

Priority:
HIGH

Estimated:
2 jam

---

# MILESTONE 6 — RESULT VIEWER

Tujuan:
menampilkan hasil ke GUI.

Checklist:

[x] Preview original

[x] Preview compressed

[x] Fit image

[x] Navigasi Prev

[x] Navigasi Next

[x] File Selector

[ ] Ganti algoritma aktif

[ ] Update metrics panel

Output:

preview interaktif

Dependency:

MILESTONE 5

Priority:
HIGH

Estimated:
2–3 jam

---

# MILESTONE 7 — EXPORT SYSTEM

Tujuan:
mengekspor hasil.

Checklist:

[x] Generate CSV

[ ] Generate grafik ukuran

[ ] Generate grafik waktu

[x] Export manual via tombol Export

[x] Implement re-export tanpa overwrite

Output:

outputs/reports/

report_YYYYMMDD_HHMMSS.csv

size_comparison.png (future)

time_comparison.png (future)

Dependency:

MILESTONE 6

Priority:
HIGH

Estimated:
2 jam

---

# MILESTONE 8 — LOGGING & ERROR

Tujuan:
memastikan aplikasi stabil.

Checklist:

[ ] Logging aplikasi

[ ] Logging kompresi

[ ] Logging error

[ ] Logging cancel

[ ] Logging export

Output:

logs/app.log

Dependency:

MILESTONE 7

Priority:
MEDIUM

Estimated:
1–2 jam

---

# MILESTONE 9 — TESTING

Tujuan:
validasi aplikasi.

Checklist:

[ ] Uji dataset ≥10

[ ] Uji cancel

[ ] Uji export

[ ] Uji preview

[ ] Uji gagal kompresi

[ ] Uji performa

Output:

aplikasi siap demo

Dependency:

MILESTONE 8

Priority:
CRITICAL

Estimated:
2–4 jam

---

# FINAL DELIVERY

Checklist:

[ ] Source Code

[ ] Dataset

[ ] Hasil Kompresi

[ ] CSV

[ ] Grafik

[ ] Screenshot

[ ] Dokumentasi

[ ] Laporan

Status:

READY FOR SUBMISSION
