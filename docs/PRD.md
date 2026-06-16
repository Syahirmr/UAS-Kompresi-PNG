# Product Requirement Document (PRD)

## Project Title

Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI

---

# 1. Background

Ukuran file gambar yang besar dapat mempengaruhi kebutuhan penyimpanan dan efisiensi distribusi data pada sistem digital.

Format PNG merupakan format gambar yang mendukung kompresi tanpa kehilangan kualitas (lossless compression), sehingga cocok digunakan untuk penelitian komparatif terhadap metode optimasi kompresi.

Proyek ini bertujuan membangun aplikasi desktop berbasis Python untuk melakukan kompresi gambar PNG menggunakan tiga algoritma berbeda dan membandingkan hasilnya berdasarkan ukuran file dan waktu kompresi.

---

# 2. Objective

Membangun aplikasi yang dapat:

* melakukan kompresi gambar PNG secara batch
* membandingkan tiga algoritma kompresi
* menampilkan hasil kompresi secara visual
* menghitung efektivitas kompresi
* menghasilkan data pengujian yang dapat dianalisis

---

# 3. Scope

## Included

### Input

* folder berisi file PNG
* minimal 10 gambar

### Processing

* menjalankan seluruh algoritma terhadap semua file

### Output

* file hasil kompresi
* preview visual
* tabel hasil
* file CSV
* grafik otomatis

---

## Excluded

* format selain PNG
* upload satuan per file
* kompresi video
* resize gambar
* pengubahan resolusi
* cloud upload
* database

---

# 4. Compression Algorithms

## Algorithm 1

Deflate Baseline

Deskripsi:
menggunakan implementasi standar encoder berbasis zlib sebagai baseline.

Tujuan:
menjadi pembanding utama.

---

## Algorithm 2

Zopfli Deflate

Deskripsi:
menggunakan pendekatan optimasi encoding yang lebih agresif dibanding Deflate standar.

Tujuan:
menghasilkan ukuran file lebih kecil.

---

## Algorithm 3

OxiPNG

Deskripsi:
optimasi kompresi PNG melalui pemilihan filter dan strategi encoding.

Tujuan:
mencari rasio kompresi terbaik.

---

# 5. User Flow

1. User membuka aplikasi
2. User memilih folder dataset
3. Sistem melakukan validasi file PNG
4. Sistem menampilkan jumlah file
5. User menjalankan proses kompresi
6. Sistem menampilkan progress
7. Sistem menyimpan seluruh hasil
8. User melihat preview
9. User mengekspor hasil

---

# 6. Functional Requirements

## Folder Selection

User dapat memilih folder dataset.

---

## Batch Compression

Sistem menjalankan seluruh algoritma terhadap semua file.

---

## Preview Result

Menampilkan:

* gambar asli
* gambar hasil algoritma aktif

Navigasi:

* previous
* next
* daftar file

---

## Metrics

Untuk setiap hasil tampilkan:

* ukuran awal
* ukuran akhir
* persentase reduksi
* waktu kompresi
* resolusi

---

## Export

Generate:

* compression_results.csv
* comparison_chart.png

---

## Progress Monitoring

Menampilkan:

* progress bar
* jumlah file selesai
* tombol cancel

Jika cancel:

* file aktif diselesaikan
* proses berhenti setelahnya

---

## Error Handling

Jika file gagal:

* tandai FAILED
* lanjut file berikutnya
* catat pada laporan

---

# 7. Non Functional Requirements

* Python Desktop Application
* berjalan secara lokal
* GUI responsif
* mendukung dataset >10 file
* hasil dapat direproduksi
* struktur kode modular

---

# 8. Dataset Requirements

Dataset harus terdiri dari beberapa karakteristik:

* foto
* screenshot
* ilustrasi
* gambar transparan

Tujuan:
menghindari bias pengujian.

---

# 9. Output Structure

outputs/

├── deflate/
│
├── zopfli/
│
├── oxipng/
│
└── reports/

---

# 10. Success Criteria

Aplikasi dianggap berhasil apabila:

* seluruh algoritma dapat berjalan
* hasil kompresi tersimpan
* GUI dapat menampilkan preview
* CSV berhasil dibuat
* grafik berhasil dibuat
* pengujian minimal 10 gambar selesai

---

# 11. Deliverables

1. Source Code
2. Dataset Pengujian
3. Hasil Kompresi
4. CSV Analisis
5. Grafik Perbandingan
6. Dokumentasi
7. Laporan UAS
