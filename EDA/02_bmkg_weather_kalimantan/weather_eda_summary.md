# Weather EDA Summary: Kalimantan 2024-2026
**Sumber Data:** Data Terbuka Meteorologi / Reanalisis Global ERA5 ECMWF  
**Cakupan:** 14 stasiun pengamatan di 5 provinsi Kalimantan  
**Periode Pengamatan:** 01 Agustus 2024 hingga 31 Mei 2026 (669 hari)  
**Total Observasi:** 9.366 baris data  

---

## 1. Daftar Stasiun Cuaca per Provinsi

| Provinsi | Kota / Stasiun | Total Hari Pengamatan |
|---|---|---|
| Kalimantan Barat | Ketapang | 669 hari |
| Kalimantan Barat | Pontianak | 669 hari |
| Kalimantan Barat | Singkawang | 669 hari |
| Kalimantan Barat | Sintang | 669 hari |
| Kalimantan Selatan | Banjarbaru | 669 hari |
| Kalimantan Selatan | Banjarmasin | 669 hari |
| Kalimantan Tengah | Palangkaraya | 669 hari |
| Kalimantan Tengah | Pangkalan Bun | 669 hari |
| Kalimantan Tengah | Sampit | 669 hari |
| Kalimantan Timur | Balikpapan | 669 hari |
| Kalimantan Timur | Berau | 669 hari |
| Kalimantan Timur | Samarinda | 669 hari |
| Kalimantan Utara | Tanjung Selor | 669 hari |
| Kalimantan Utara | Tarakan | 669 hari |

---

## 2. Matriks Korelasi Linier (Pearson) vs Indikator Kebakaran

| Variabel Meteorologi | Korelasi vs Jumlah Hotspot (`hotspot_count`) | Korelasi vs Total Energi Api (`total_frp`) |
|---|---|---|
| Kelembapan Relatif Rata-rata (`humidity_mean`) | -0.482 | -0.433 |
| Defisit Tekanan Uap Maksimum (`vpd_max`) | +0.470 | +0.420 |
| Kelembapan Relatif Minimum (`humidity_min`) | -0.460 | -0.410 |
| Suhu Udara Maksimum (`temp_max`) | +0.382 | +0.339 |
| Akumulasi Curah Hujan (`precip`) | -0.361 | -0.323 |
| Suhu Udara Rata-rata (`temp_mean`) | +0.349 | +0.311 |
| Durasi Penyinaran Matahari (`sunshine_h`) | +0.318 | +0.280 |
| Kecepatan Angin Maksimum (`wind_max`) | +0.218 | +0.211 |

---

## 3. Statistik Deskriptif Musim Kemarau (Juni hingga Oktober)

| Metrik | Suhu Maksimum (°C) | Curah Hujan (mm) | Kecepatan Angin (km/jam) | Kelembapan Min (%) | VPD Maksimum (kPa) |
|---|---|---|---|---|---|
| Rata-rata (*mean*) | 30.76 | 7.83 | 11.89 | 65.67 | 1.55 |
| Standar Deviasi | 1.65 | 9.61 | 2.97 | 8.76 | 0.52 |
| Nilai Minimum | 25.00 | 0.00 | 4.00 | 36.00 | 0.18 |
| Kuartil 1 (25%) | 29.80 | 0.80 | 9.80 | 60.00 | 1.18 |
| Median (50%) | 30.90 | 4.30 | 11.50 | 66.00 | 1.53 |
| Kuartil 3 (75%) | 31.90 | 11.60 | 13.60 | 71.00 | 1.89 |
| Nilai Maksimum | 37.00 | 130.80 | 25.00 | 94.00 | 3.84 |

---

## 4. Statistik Deskriptif Musim Hujan (November hingga Mei)

| Metrik | Suhu Maksimum (°C) | Curah Hujan (mm) | Kecepatan Angin (km/jam) | Kelembapan Min (%) | VPD Maksimum (kPa) |
|---|---|---|---|---|---|
| Rata-rata (*mean*) | 30.53 | 10.53 | 12.05 | 67.93 | 1.42 |
| Standar Deviasi | 1.44 | 9.75 | 3.03 | 7.61 | 0.43 |
| Nilai Minimum | 24.90 | 0.00 | 4.90 | 35.00 | 0.15 |
| Kuartil 1 (25%) | 29.70 | 2.70 | 9.90 | 63.00 | 1.14 |
| Median (50%) | 30.60 | 8.30 | 11.70 | 68.00 | 1.40 |
| Kuartil 3 (75%) | 31.50 | 15.60 | 13.80 | 73.00 | 1.69 |
| Nilai Maksimum | 36.20 | 138.60 | 27.80 | 95.00 | 3.89 |

---

## 5. Indeks Berkas Visualisasi

* `W01_monthly_weather_overview.png`: Tinjauan deret waktu bulanan parameter suhu, curah hujan, kelembapan, dan angin.
* `W02_weather_vs_hotspot_count.png`: Analisis korelasi sumbu ganda antara variabel cuaca utama vs volume titik panas.
* `W03_correlation_heatmap_weather_fire.png`: Matriks korelasi Pearson lengkap antara parameter cuaca dan metrik karhutla.
* `W04_province_weather_vs_fire_drySeason.png`: Perbandingan spasial cuaca vs kebakaran di tingkat provinsi selama musim kemarau.
* `W05_rolling14d_weather_fire_timeseries.png`: Analisis tren deret waktu bergerak 14 hari pemicu kebakaran.
* `W06_dry_vs_wet_season_weather.png`: Diagram kotak distribusi parameter cuaca antara musim kemarau dan musim hujan.
