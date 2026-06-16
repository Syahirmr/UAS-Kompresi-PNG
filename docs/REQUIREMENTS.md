# Technical Requirements

## Project Name

PNG Compression Comparison System

Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI

---

# 1. Technology Stack

## Programming Language

Python 3.11+

---

## GUI Framework

Tkinter

Alasan:

* stabil
* dependency ringan
* kompatibel dengan Python standar

---

## Core Libraries

Pillow

Fungsi:

* membaca gambar
* membuat preview
* resize preview

---

pandas

Fungsi:

* export CSV
* manipulasi hasil eksperimen

---

matplotlib

Fungsi:

* generate grafik PNG otomatis

---

pathlib

Fungsi:

* manajemen path

---

subprocess

Fungsi:

* menjalankan tool eksternal

---

threading

Fungsi:

* batch process tanpa freeze GUI

---

time

Fungsi:

* menghitung waktu kompresi

---

csv

Fungsi:

* export hasil

---

# 2. External Compression Tools

Semua algoritma dijalankan menggunakan CLI/Binary.

Folder:

tools/

---

## Algorithm 1

Deflate Baseline

Implementasi:

zlib / pngcrush equivalent

Output Folder:

outputs/deflate/

---

## Algorithm 2

Zopfli

Implementasi:

zopfli executable

Output Folder:

outputs/zopfli/

---

## Algorithm 3

OxiPNG

Implementasi:

oxipng executable

Output Folder:

outputs/oxipng/

---

# 3. Directory Structure

project/

docs/

src/

dataset/

outputs/

tools/

assets/

tests/

---

# 4. Source Structure

src/

main.py

ui/

compression/

analysis/

utils/

---

# 5. GUI Specification

Window:

Desktop

Resizable:
True

---

Sections

HEADER

Folder Picker

Compression Panel

Progress Panel

Preview Panel

Export Panel

---

# 6. Input Rules

Input Type:

Folder

Accepted:

.png

Validation:

* ignore non png
* minimum 10 PNG

Jika kurang:

tampilkan warning

---

# 7. Processing Rules

Semua algoritma dijalankan otomatis.

Urutan:

File

↓

Deflate

↓

Zopfli

↓

OxiPNG

↓

Record Metrics

↓

Next File

---

Batch:

Sequential

---

Cancel:

selesaikan file aktif

stop setelahnya

---

# 8. Preview Rules

Preview Mode:

Side-by-side

Tampilan:

Original

Compressed

Image Scale:

Fit Window

Navigasi:

Prev

Next

File Selector

---

# 9. Metrics

Simpan:

filename

algorithm

before_size_kb

after_size_kb

reduction_percent

compression_time_ms

resolution

status

---

Formula

Reduction:

((before-after)/before)*100

---

# 10. Export

CSV

compression_results.csv

---

Charts

size_comparison.png

time_comparison.png

---

# 11. Error Handling

Jika gagal:

status=FAILED

lanjut file berikut

catat ke CSV

---

# 12. Logging

Buat file:

logs/app.log

Catat:

timestamp

filename

algorithm

result

duration

---

# 13. Performance Target

Dataset:

10–50 file

Target:

GUI tetap responsif

Target waktu:

< 5 menit untuk 10 file

---

# 14. Dependency Installation

requirements.txt

Minimal:

Pillow

pandas

matplotlib

zopfli

---

CLI tool manual:

tools/

oxipng

---

# 15. Deliverables

Executable Python App

CSV

Charts

Compressed Images

Logs
