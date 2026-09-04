# FIRELINE — Final Study Case, Data Science Academy COMPFEST 2026

Repository konsolidasi sementara untuk kontribusi Data Science FIRELINE.

## Struktur kontribusi

```text
├── data/           # Dataset dan output EDA dari branch grace
├── datasets/       # Dataset, processed data, dan spatial data
├── documents/      # Dokumen pendukung dan findings
├── notebooks/      # Notebook EDA dan preprocessing
├── outputs/        # Derived EDA outputs dan figures
├── docs/           # Audit dan alignment documentation
├── EDA/            # EDA package dari branch BMKG
├── scripts/        # Script EDA/utilitas
├── main.py
└── README.md
```

Path existing dipertahankan karena notebook dan script memakai relative path. Jangan memindahkan dataset atau notebook tanpa memperbarui referensinya.

## Prasyarat dan setup

- Python (versi mengikuti `.python-version`)
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
uv run jupyter lab
uv run main.py
```

## Scope saat ini

Phase 1–2 hanya mencakup repository consolidation dan data alignment. Final integrated dataset, CRPI, model training, Tableau, API, dan SEA tetap di luar scope sampai review tim selesai.

Dokumentasi audit tersedia di `docs/`.
