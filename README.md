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

# FIRELINE: Spatial Risk Prioritization and Decision Support System
## Platform Mitigasi Bencana Kebakaran Hutan dan Lahan Kalimantan
**COMPFEST 18 Data Science Case Study | Tim Alpha**

---

## Ringkasan Proyek

FIRELINE adalah platform sistem pendukung keputusan (Decision Support System) dan mesin penentu prioritas risiko spasial karhutla berbasis sains data dan penginderaan jauh. 

Sistem ini mengintegrasikan kerangka kerja penilaian risiko kontekstual berbasis tiga pilar:
1. **BAHAYA (HAZARD):** Deteksi aktif titik panas satelit NASA VIIRS NOAA-20 (Agustus 2024 - Mei 2026) dan parameter meteorologi atmosfer BMKG (Suhu Udara, Kelembapan, VPD, Kecepatan Angin, dan Curah Hujan).
2. **PAPARAN (EXPOSURE):** Pemodelan kedekatan spasial titik api terhadap 17.448 fasilitas pendidikan dan pemukiman penduduk di seluruh Kalimantan.
3. **KERENTANAN (VULNERABILITY):** Analisis spasial zona kebakaran berulang (chronic fire zones), tutupan lahan gambut, dan baseline klimatologi historis 11 tahun (2010 - 2020).

---

## Struktur Repositori

```text
fireline-compfest18-alpha/
├── datasets/                              # Direktori dataset utama dan eksternal
│   ├── fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv
│   ├── bmkg_kalimantan_weather_2024_2026.csv
│   ├── complete_data.csv                  # Data spasial sekolah dan pemukiman
│   ├── climate_data.csv                   # Data iklim historis BMKG 2010-2020
│   ├── province_detail.csv
│   └── station_detail.csv
│
├── EDA/                                   # Hasil Exploratory Data Analysis dan Visualisasi
│   ├── 01_fireline_hotspot_kalimantan/    # EDA 61.583 Titik Panas NASA VIIRS (27 Grafik Analitik)
│   ├── 02_bmkg_weather_kalimantan/        # EDA Data Cuaca BMKG 2024-2026 (6 Grafik Analitik)
│   └── 03_kaggle_indonesia_climate/       # EDA Baseline Klimatologi 11 Tahun (6 Grafik Analitik)
│
├── scripts/                               # Pipeline pengolahan data dan kode automasi
├── indonesia_provinces.json               # Data batas administratif GeoJSON Kalimantan
├── .gitignore
└── README.md
```

---

## Ringkasan Temuan Eksplorasi Data (Key Insights)

* **Episentrum Kebakaran:** Kalimantan Barat menyumbang 51,6% titik panas (31.764 deteksi) dan 367.757 MW total daya radiasi api (FRP).
* **Siklus Musiman:** Sebanyak 83,4% kebakaran terkonsentrasi pada musim kemarau (Juni hingga Oktober) dengan disparitas volume hingga 136 kali lipat dibanding musim hujan.
* **Kejadian Ekstrem (Mega-Fires):** Teridentifikasi 6 kejadian kebakaran masif (FRP > 500 MW) dengan puncak energi radiasi mencapai 954,8 MW.
* **Korelasi Meteorologi Kunci:** Kelembapan udara relatif (r = -0,482) dan Defisit Tekanan Uap / VPD (r = +0,470) menjadi pendorong atmosferik utama eskalasi titik api.
* **Validasi Historis 11 Tahun:** Rekam jejak iklim dekadal 2010 - 2020 mengonfirmasi anomali kekeringan El Nino 2015 dan kemarau 2019 sebagai pembanding empiris risiko kebakaran skala besar.
