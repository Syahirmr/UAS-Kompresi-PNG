# PNG Compression Comparison System

**Studi Komparasi Tiga Algoritma Kompresi PNG Menggunakan Python Berbasis GUI Modern**

Aplikasi desktop berbasis Python untuk membandingkan efektivitas tiga algoritma kompresi gambar berformat PNG secara otomatis (batch). Aplikasi ini dirancang sebagai tugas akhir (UAS) Sistem Multimedia yang menitikberatkan pada perbandingan performa rasio kompresi dan waktu eksekusi.

---

## Latar Belakang & Landasan Teori

Tujuan utama dari proyek ini adalah menemukan algoritma kompresi *lossless* terbaik untuk gambar berformat PNG dengan menyeimbangkan dua variabel utama: **Rasio Kompresi** (ukuran file sekecil mungkin) dan **Kecepatan Waktu Eksekusi** (waktu pemrosesan secepat mungkin).

### 1. Kenapa Memilih 3 Algoritma Ini?

Kami menguji tiga algoritma yang masing-masing mewakili pendekatan teknis yang berbeda di industri kompresi:

*   **Deflate Baseline (zlib):**
    Merupakan algoritma bawaan (*standard library*) dari Python yang digunakan hampir di seluruh sistem komputasi di dunia.
    *   **Kelebihan:** Sangat cepat karena sudah dioptimasi di level C, cocok sebagai *baseline* (nilai rujukan awal).
    *   **Kekurangan:** Rasio kompresi standar dan kurang maksimal jika dibandingkan dengan algoritma pencarian mendalam (*exhaustive*).

*   **Zopfli (Google Zopfli):**
    Algoritma buatan Google yang melakukan pencarian ruang kompresi secara mendalam (*exhaustive search*) hingga 15 iterasi untuk memadatkan data semaksimal mungkin dengan format Deflate standar.
    *   **Kelebihan:** Menghasilkan ukuran file yang sangat kecil (3-8% lebih kecil dibanding zlib), sangat ideal untuk keperluan web (seperti CDN) di mana file dikompres sekali namun diunduh jutaan kali.
    *   **Kekurangan:** Waktu pemrosesan (CPU time) sangat lambat, bahkan bisa 100x lebih lama dibanding zlib.

*   **OxiPNG (Rust-based Optimizer):**
    Algoritma kompresi ulang *lossless* yang ditulis dalam bahasa Rust, merupakan evolusi mutakhir dari OptiPNG. OxiPNG membuang meta-data yang tidak diperlukan dan menerapkan pencarian *heuristic* tingkat lanjut.
    *   **Kelebihan:** Mampu berjalan secara *multithreaded*, sehingga dapat memproses *chunk* gambar secara paralel. Memberikan rasio kompresi yang hampir menyaingi Zopfli namun dengan waktu eksekusi yang jauh lebih cepat.
    *   **Kekurangan:** Memerlukan *binary file* (`.exe`) eksternal tambahan.

### 2. Keputusan Arsitektur UI: Kenapa CustomTkinter?

Dalam pengembangan antarmuka (GUI), kami memilih menggunakan **Tkinter** yang dipadukan dengan **CustomTkinter** karena alasan teknis berikut:
*   **Lightweight & Native:** Tidak seperti framework Electron (Node.js) atau Qt yang sangat berat dan memakan banyak RAM, Tkinter adalah pustaka GUI bawaan Python yang sangat ringan.
*   **Estetika Modern:** Kombinasi `CustomTkinter` mengatasi kelemahan klasik Tkinter dengan menyediakan elemen UI modern (sudut melengkung, efek *hover*) serta transisi *Dark/Light Mode* layaknya aplikasi *native* modern tanpa mengorbankan performa.
*   **Integrasi Multithreading:** Aplikasi ini merender antarmuka di *Main Thread*, sedangkan proses pemindaian folder (ratusan file) dan kompresi mesin dijalankan di *Background Worker Thread* terpisah. Hal ini memastikan UI tidak macet (*hang/freeze*) selama eksperimen berlangsung.

---

## Sorotan Fitur (Features Overview)

### 1. Performa Pemindaian *Background* (Baru)
Proses memuat dataset tidak lagi membuat UI macet berkat implementasi sistem *background thread* untuk proses pembacaan file. Pemindaian (*scanning*) yang panjang bisa di-*cancel* kapan saja oleh pengguna.

### 2. Comparison Dashboard 📊
Menjalankan ketiga algoritma (Deflate, Zopfli, OxiPNG) sekaligus secara berurutan. Di akhir proses, sistem otomatis menentukan pemenang berdasarkan 3 metrik:
- **Best Compression:** Algoritma dengan pengurangan ukuran (*reduction*) terbesar.
- **Fastest:** Algoritma dengan waktu tercepat.
- **Balanced Winner:** Algoritma dengan skor terbaik (Kalkulasi 50% ukuran file + 50% kecepatan).

### 3. Visualisasi & Eksport Data Otomatis
Setiap kali *comparison* selesai dijalankan, data metrik diekspor secara otomatis agar tidak hilang.
- **Laporan CSV:** Rekapitulasi detil (`comparison_report_YYYYMMDD.csv`).
- **Diagram Grafik:** Aplikasi otomatis men- *generate* grafik batang perbandingan performa di direktori `outputs/charts/`.

---

## Visualisasi Fitur

Berikut adalah gambaran hasil akhir (*output*) berupa diagram komparasi yang dihasilkan oleh aplikasi:

| Grafik Reduksi Ukuran File | Grafik Kecepatan Kompresi |
|:---:|:---:|
| ![Reduction Chart](outputs/charts/reduction_chart_20260618_171138_821.png) | ![Time Chart](outputs/charts/time_chart_20260618_171138_924.png) |
*(Diagram yang dihasilkan secara otomatis usai proses uji coba untuk analisis laporan)*

---

## Setup & Instalasi

### Prasyarat
- **Python 3.11+**
- Virtual Environment (Opsional namun disarankan)

### Cara Menginstal

```bash
# 1. Clone & Navigasi
cd uas-kompresi-png

# 2. Buat & Aktifkan Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # Untuk Windows

# 3. Instal semua dependensi
pip install -r requirements.txt
```

### Eksternal Binary (OxiPNG)
Aplikasi membutuhkan `oxipng.exe` yang diletakkan di direktori berikut:
`tools/oxipng/oxipng.exe`

---

## Struktur Proyek Utama

```text
uas-kompresi-png/
├── src/
│   ├── ui/app.py                    # Main GUI & CustomTkinter UI
│   ├── compression/algorithms/      # Modul zlib, zopfli, dan oxipng runner
│   ├── analysis/analyzer.py         # Penghitung matriks skor
│   ├── export/exporter.py           # Ekspor ke CSV, Excel, dan pembuat Chart
│   └── utils/dataset_loader.py      # Background scanner
├── dataset/                         # Folder sample input PNG
├── outputs/
│   ├── comparison/                  # Hasil kompresi per algoritma
│   ├── charts/                      # Output visual diagram
│   └── reports/                     # Output hasil eksperimen CSV/Excel
├── tests/                           # +128 Unit Testing
└── tools/oxipng/                    # Lokasi binary OxiPNG
```

---

## Cara Menjalankan Aplikasi

```bash
# Pastikan virtual env aktif
.venv\Scripts\activate

# Mulai GUI
python -m src.main
```

**Panduan Pengujian:**
1. Klik **Browse Folder** dan pilih direktori dataset (misal: `dataset/data1`).
2. Proses pemindaian berjalan di *background*, tunggu hingga jumlah file terdeteksi.
3. Klik tombol biru **Run Comparison** untuk menjalankan eksperimen pada ketiga algoritma.
4. Cek visual komparasi di layar, dan lihat hasil laporan lengkapnya di tab **Comparison Summary** atau di folder `outputs/reports`.

---

## Testing & Kualitas Kode

Aplikasi ini dilindungi oleh lebih dari 128 *Unit Tests* yang mencakup modul-modul kritis:
```bash
# Untuk menjalankan test
python -m unittest discover -s tests -v
```

---

*Laporan ini dibuat sebagai bagian dari Tugas Akhir Sistem Multimedia Semester 6.*
