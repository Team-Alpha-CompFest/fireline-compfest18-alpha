# FIRELINE: Spatial Risk Prioritization & Decision Support System
## Platform Mitigasi Bencana Kebakaran Hutan dan Lahan Kalimantan
**COMPFEST 18 Data Science Case Study | Tim Alpha**

---

## 📌 Ringkasan Proyek

**FIRELINE** adalah platform sistem pendukung keputusan (*Decision Support System*) dan mesin penentu prioritas risiko spasial karhutla berbasis kecerdasan data (*Data Intelligence*). 

Sistem ini mengintegrasikan tiga pilar analisis risiko terpadu:
1. **BAHAYA (HAZARD):** Data deteksi aktif titik panas satelit NASA VIIRS NOAA-20 (2024–2026) dan parameter meteorologi atmosfer BMKG (Suhu, Kelembapan, VPD, Angin, Curah Hujan).
2. **PAPARAN (EXPOSURE):** Pemodelan kedekatan spasial titik api terhadap 17.448 fasilitas pendidikan/sekolah dan pemukiman penduduk di seluruh Kalimantan.
3. **KERENTANAN (VULNERABILITY):** Analisis zona kebakaran kronis (*chronic fire recurrence zones*), tutupan lahan gambut, dan baseline klimatologi historis 11 tahun (2010–2020).

---

## 📁 Struktur Repositori

```text
├── datasets/                              # Dataset utama & eksternal
│   ├── fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv
│   ├── bmkg_kalimantan_weather_2024_2026.csv
│   ├── complete_data.csv                  # Data spasial sekolah & pemukiman
│   ├── climate_data.csv                   # Data iklim BMKG 2010-2020
│   ├── province_detail.csv
│   └── station_detail.csv
│
├── EDA/                                   # Hasil Exploratory Data Analysis & Visualisasi
│   ├── 01_fireline_hotspot_kalimantan/    # EDA 61.583 Titik Panas NASA VIIRS (27 Grafik)
│   ├── 02_bmkg_weather_kalimantan/        # EDA Data Cuaca BMKG 2024-2026 (6 Grafik)
│   └── 03_kaggle_indonesia_climate/       # EDA Baseline Klimatologi 11 Tahun (6 Grafik)
│
├── scripts/                               # Pipeline Python & script automasi
└── indonesia_provinces.json               # Batas administratif GeoJSON 38 provinsi
```

---

## 🔬 Sorotan Temuan Analisis (Key Insights)

* **Episentrum Utama:** Kalimantan Barat menyumbang **51,6% titik panas** dan 367.757 MW total daya radiasi api (FRP).
* **Konsentrasi Musiman:** **83,4% kebakaran** terjadi pada musim kemarau (Juni–Oktober) dengan disparitas 136x lipat dibanding musim hujan.
* **Kejadian Ekstrem (*Mega-Fires*):** Teridentifikasi 6 kejadian kebakaran masif (FRP > 500 MW) dengan puncak energi mencapai 954,8 MW.
* **Pemicu Meteorologi Kunci:** Kelembapan udara relatif (*r = -0,482*) dan *Vapor Pressure Deficit* (*r = +0,470*) merupakan indikator atmosferik paling berkorelasi dengan eskalasi karhutla.
* **Validasi Baseline 11 Tahun:** Rekam jejak iklim historis (2010–2020) mengonfirmasi El Niño 2015 dan kemarau 2019 sebagai pembanding empiris kebakaran skala besar.
