# EXPERIMENT PLAN

Project:
PNG Compression Comparison System

Status:
LOCKED

---

# 1. Experiment Objective

Tujuan eksperimen adalah membandingkan efektivitas tiga algoritma kompresi PNG berdasarkan:

* ukuran file hasil
* persentase reduksi ukuran
* waktu kompresi
* konsistensi hasil terhadap berbagai karakteristik gambar

Eksperimen dilakukan menggunakan dataset terkontrol.

---

# 2. Compression Algorithms

## Algorithm A

Deflate Baseline

Kategori:
Baseline Compression

Karakteristik:

* encoder standar
* referensi utama

---

## Algorithm B

Zopfli Deflate

Kategori:
Aggressive Optimization

Karakteristik:

* rasio kompresi lebih tinggi
* waktu proses lebih lama

---

## Algorithm C

OxiPNG

Kategori:
Spatial Optimization

Karakteristik:

* optimasi filter PNG
* keseimbangan ukuran dan performa

---

# 3. Experiment Dataset

Dataset Minimum:

10 file PNG

Jika jumlah lebih besar:
gunakan seluruh dataset.

---

# 4. Dataset Composition

Dataset harus dikontrol.

Distribusi:

Photo:
3 file

Screenshot:
3 file

Illustration:
2 file

Transparency:
2 file

---

# 5. Dataset Rules

Semua file:

* format PNG
* tidak diubah manual
* tidak di-resize
* tidak di-crop
* diproses dari file asli

---

# 6. Execution Method

Mode:

Batch Compression

Urutan:

Untuk setiap file:

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

Progress:

Total Task

Contoh:

10 file × 3 algoritma

=

30 task

---

# 7. Output Directory

outputs/

run_timestamp/

deflate/

zopfli/

oxipng/

reports/

---

# 8. Metrics Collection

Catat untuk setiap hasil:

filename

category

algorithm

resolution

before_size_kb

after_size_kb

reduction_percent

compression_time_ms

status

---

Formula:

Reduction Percent

((before-after)/before)*100

---

# 9. Result Recording

Simpan otomatis:

compression_results.csv

---

Grafik:

size_comparison.png

time_comparison.png

---

# 10. Error Scenario

Jika file gagal:

status:

FAILED

Aturan:

* lanjut file berikutnya
* simpan log
* tampil pada laporan

---

# 11. Cancellation Scenario

Jika Cancel ditekan:

* proses file aktif diselesaikan
* batch berhenti
* hasil parsial tetap disimpan

Status:

PARTIAL_COMPLETED

---

# 12. Analysis Method

Hitung:

rata-rata ukuran akhir

rata-rata reduksi

rata-rata waktu

tingkat keberhasilan

---

Bandingkan berdasarkan:

kategori gambar

algoritma

---

# 13. Interpretation Rules

Evaluasi:

Algoritma terbaik ukuran

↓

Algoritma tercepat

↓

Algoritma paling stabil

↓

Tradeoff akhir

---

# 14. Success Criteria

Eksperimen dianggap valid jika:

≥10 file diproses

semua algoritma berjalan

CSV terbentuk

grafik terbentuk

hasil dapat direproduksi

---

# 15. Expected Findings

Kemungkinan hasil:

Deflate:
cepat

Zopfli:
ukuran terkecil

OxiPNG:
kompromi terbaik

Catatan:

bagian ini adalah hipotesis awal,
bukan hasil penelitian.
