# GUI Architecture Documentation

## Overview

**MILESTONE 1: GUI FOUNDATION** 

Aplikasi menggunakan **Tkinter** untuk GUI desktop. Arsitektur dibangun dengan prinsip modular untuk memudahkan maintenance dan future development.

---

## Architecture Pattern

```
CompressionApp (Main Window)
│
├── HeaderComponent
│   └── Title & Subtitle
│
├── FolderPickerComponent
│   ├── Browse Button
│   ├── Folder Path Display
│   └── File Counter
│
├── ControlPanelComponent
│   ├── Compress Button
│   ├── Cancel Button
│   ├── Export Button
│   ├── Progress Bar
│   └── Status Label
│
├── PreviewComponent (Side-by-side)
│   ├── Original Image Panel
│   └── Compressed Image Panel
│
├── FileSelectorComponent
│   ├── File List (Combobox)
│   ├── Previous Button
│   ├── Next Button
│   └── Position Counter
│
└── MetricsPanelComponent
    └── Treeview Table
        ├── Algorithm
        ├── Original Size
        ├── Compressed Size
        ├── Reduction %
        ├── Time (ms)
        └── Status
```

---

## Component Structure

### 1. HeaderComponent (`components_header.py`)

**Fungsi:**
- Menampilkan judul aplikasi
- Menampilkan subtitle/deskripsi

**Output:**
- Title label
- Subtitle label
- Separator line

**Future Connection:** Tidak ada

---

### 2. FolderPickerComponent (`components_folder_picker.py`)

**Fungsi:**
- Memungkinkan user memilih folder dataset
- Menampilkan path folder yang dipilih
- Menampilkan jumlah file PNG ditemukan

**Buttons:**
- `Browse Folder` - Membuka file dialog

**Future Connection:**
- **MILESTONE 2 (Dataset Loader):** Akan scan folder, validasi file PNG, tampilkan file count
- Method: `populate_files(file_list)` akan dipanggil

---

### 3. ControlPanelComponent (`components_control.py`)

**Fungsi:**
- Tombol kontrol kompresi (Start, Cancel, Export)
- Progress bar untuk monitoring
- Status message display

**Controls:**
- `▶ Start Compression` - Mulai proses kompresi
- `⏹ Cancel` - Batalkan proses
- `📊 Export Results` - Export hasil ke CSV
- Progress Bar (0-100%)
- Status Text

**State Management:**
- Compress: enabled saat ready, disabled saat compressing
- Cancel: disabled saat idle, enabled saat compressing
- Export: disabled saat idle/compressing, enabled saat selesai

**Future Connection:**
- **MILESTONE 3 (Compression):** Akan implement compression logic
  - `_on_compress()` akan trigger batch compression
  - `set_progress(value)` akan update progress bar
  - `set_status(message)` akan update status
- **MILESTONE 4 (Export):** Akan implement export logic
  - `_on_export()` akan generate CSV & charts

---

### 4. PreviewComponent (`components_preview.py`)

**Fungsi:**
- Menampilkan gambar original dan compressed side-by-side
- Fit-window layout (scale otomatis)
- Support preview rotation/selection

**Display:**
- Left panel: Original Image
- Right panel: Compressed Image (algoritma yang dipilih)

**Methods:**
- `display_images(original_path, compressed_path)` - Load dan tampilkan images
- `clear()` - Clear preview
- `set_error(message)` - Display error

**Future Connection:**
- **MILESTONE 2 (Dataset Loader):** File selection akan trigger preview update
- **MILESTONE 3 (Compression):** Compressed image path akan dipass setelah kompresi selesai

---

### 5. FileSelectorComponent (`components_file_selector.py`)

**Fungsi:**
- Navigation through dataset files
- Display current file
- Show position (current/total)

**Controls:**
- File List Combobox - Pilih file dari list
- `◀ Previous` - File sebelumnya
- `Next ▶` - File berikutnya
- Position Counter (1/10, 2/10, etc)

**Methods:**
- `populate_files(file_list)` - Populate combobox dengan file list
- `get_current_file()` - Get selected file
- `_update_counter(current, total)` - Update position display

**Future Connection:**
- **MILESTONE 2 (Dataset Loader):** Akan provide file list setelah folder dipilih
- **MILESTONE 5:** Navigation logic akan implement

---

### 6. MetricsPanelComponent (`components_metrics.py`)

**Fungsi:**
- Tabel hasil kompresi per algoritma
- Display metrics untuk setiap algorithm
- Real-time update selama kompresi

**Columns:**
- Algorithm (Deflate, Zopfli, OxiPNG)
- Original Size (KB)
- Compressed Size (KB)
- Reduction % (percentage)
- Time (ms)
- Status (Waiting/Running/Done/Failed)

**Methods:**
- `update_metrics(algorithm, ...)` - Update metrics untuk satu algorithm
- `reset()` - Reset ke status awal
- `clear_all()` - Hapus semua rows

**Future Connection:**
- **MILESTONE 3 (Compression):** Akan update metrics real-time saat kompresi running
- **MILESTONE 4 (Export):** Data dari metrics akan di-export ke CSV

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER                                                      │
├─────────────────────────────────────────────────────────────┤
│ FOLDER PICKER                                               │
├─────────────────────────────────────────────────────────────┤
│ CONTROL PANEL                                               │
│ [▶ Start] [⏹ Cancel] [📊 Export]  Progress: [████] 50%    │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│ PREVIEW                  │ FILE SELECTOR                   │
│ [Original] [Compressed]  │ [List Dropdown]                │
│                          │ [◀ Prev] [Next ▶]              │
│                          │ Position: 3/10                 │
│                          │                                 │
│ METRICS TABLE            │                                 │
│ ┌──────┬──────┬──────┐   │                                 │
│ │Algo  │Size  │Reduc│   │                                 │
│ ├──────┼──────┼──────┤   │                                 │
│ │Def   │ ...  │  ...│   │                                 │
│ │Zopf  │ ...  │  ...│   │                                 │
│ │Oxi   │ ...  │  ...│   │                                 │
│ └──────┴──────┴──────┘   │                                 │
│                          │                                 │
└──────────────────────────┴──────────────────────────────────┘
```

---

## Data Flow Diagram

```
MILESTONE 2 (Dataset Loader)
        │
        ↓
File List → FileSelectorComponent
        │
        ↓
User selects file
        │
        ├─→ PreviewComponent (load original image)
        │
        └─→ MetricsComponent (reset/prepare)

MILESTONE 3 (Compression)
        │
        ├─→ ControlPanel.set_status()
        ├─→ ControlPanel.set_progress()
        ├─→ MetricsComponent.update_metrics()
        │
        └─→ Hasil kompresi ready

PreviewComponent
        │
        ├─→ Load compressed image
        └─→ Display side-by-side

MILESTONE 4 (Export)
        │
        ├─→ MetricsComponent (read table data)
        └─→ Generate CSV & Charts
```

---

## Responsive Design Features

1. **Canvas with Scrollbar**
   - Support vertical scrolling untuk content panjang
   - Mousewheel support

2. **Flexible Layout**
   - LabelFrame untuk section grouping
   - ttk.Frame untuk layout management
   - Grid-based positioning

3. **Dynamic Button States**
   - Button enable/disable based on state
   - Visual feedback (colors, cursor)

4. **Resizable Components**
   - Preview images scale dengan window size
   - Table columns auto-adjust
   - Text wrapping pada labels

---

## Configuration

**File:** `src/utils/config.py`

Mengatur:
- Window size & title
- Colors (primary, secondary, accent)
- Fonts (title, heading, normal, small, mono)
- Padding & spacing
- Component dimensions

Benefit: Centralized configuration untuk easy theming

---

## Component Integration

Semua komponen terintegrasi di **`CompressionApp`** class:

```python
class CompressionApp(tk.Tk):
    def __init__(self):
        # Build GUI with all components
        self.folder_picker = FolderPickerComponent(content_frame)
        self.control_panel = ControlPanelComponent(content_frame)
        self.preview = PreviewComponent(left_frame)
        self.metrics = MetricsPanelComponent(left_frame)
        self.file_selector = FileSelectorComponent(right_frame)
    
    # Getter methods untuk akses dari main.py
    def get_folder_picker(self):
    def get_control_panel(self):
    def get_preview(self):
    def get_metrics(self):
    def get_file_selector(self):
```

---

## Future Milestone Integration Points

### MILESTONE 2 (Dataset Loader)
```
Location: src/compression/dataset_loader.py

Connect:
- folder_picker.get_selected_folder() → get folder path
- file_selector.populate_files(files) → populate file list
- file_selector.get_current_file() → get selected file
- preview.display_images() → show preview
- metrics.reset() → reset metrics table
```

### MILESTONE 3 (Compression Implementation)
```
Location: src/compression/compressor.py

Connect:
- control_panel.compress_btn → trigger compression
- control_panel.cancel_btn → cancel compression
- control_panel.set_progress() → update progress bar
- control_panel.set_status() → update status text
- metrics.update_metrics() → update metrics per algorithm
- preview.display_images() → show compressed result
```

### MILESTONE 4 (Results Analysis & Export)
```
Location: src/analysis/exporter.py

Connect:
- control_panel.export_btn → trigger export
- metrics.get_data() → read metrics table
- Generate CSV file
- Generate comparison charts
```

### MILESTONE 5 (Testing & Polish)
```
Location: tests/test_gui.py

Connect:
- Unit tests untuk setiap component
- Integration tests untuk data flow
- UI responsiveness testing
```

---

## Files Created

```
src/
├── utils/
│   ├── config.py                    ✅ Configuration constants
│   └── logger.py                    (placeholder)
│
└── ui/
    ├── app.py                       ✅ Main GUI application
    ├── components_header.py         ✅ Header component
    ├── components_folder_picker.py  ✅ Folder picker component
    ├── components_control.py        ✅ Control panel component
    ├── components_preview.py        ✅ Preview component
    ├── components_file_selector.py  ✅ File selector component
    └── components_metrics.py        ✅ Metrics panel component
```

---

## How to Run

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run GUI
python src/main.py
```

---

## Status

✅ **MILESTONE 1: GUI FOUNDATION COMPLETE**

- Main window dengan responsive layout
- Semua components built dan integrated
- Placeholder functionality siap untuk future milestones
- Configuration centralized
- Modular architecture untuk easy expansion

**Next:** MILESTONE 2 — Dataset Loader
