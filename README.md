# FIRELINE — Final Study Case, Data Science Academy COMPFEST 2026

## Struktur Project

```
.
├── datasets/       # Dataset mentah (lihat bagian "Dataset" di bawah)
├── documents/      # Dokumen pendukung (problem description, temuan analisis)
├── notebooks/      # Notebook eksplorasi, EDA, dan preprocessing
├── main.py
├── pyproject.toml
├── uv.lock
└── .python-version
```

## Prasyarat

- Python (versi mengikuti file `.python-version` di root project)
- [uv](https://docs.astral.sh/uv/) sebagai package & environment manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux
  # atau lihat dokumentasi uv untuk instalasi Windows
  ```

## Setup Lokal

1. **Clone repo**
   ```bash
   git clone <url-repo>
   cd <nama-folder-repo>
   ```

2. **Install dependencies**
   `uv sync` otomatis membuat virtual environment (`.venv`) dan menginstall seluruh dependency sesuai versi yang terkunci di `uv.lock`, memastikan semua anggota tim pakai versi package yang identik.
   ```bash
   uv sync
   ```

3. **Aktifkan virtual environment** (opsional, karena `uv run` di bawah sudah otomatis menggunakan environment yang benar tanpa perlu aktivasi manual)
   ```bash
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows
   ```

4. **Jalankan project**
   ```bash
   uv run jupyter lab        # buka notebook eksplorasi
   # atau
   uv run main.py

## Dokumentasi Tambahan
- `documents/Temuan_Analisis_Data_Awal_(1, 3, 4)_FIRELINE .pdf` - ringkasan temuan analisis data untuk tim non-teknis (PM/UX).