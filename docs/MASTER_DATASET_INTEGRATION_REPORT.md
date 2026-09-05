# Laporan Integrasi Master Dataset Analitis Berlabel (FIRELINE Master Dataset Report)

**Project:** FIRELINE - AI-Powered Decision Support System (COMPFEST 18 Data Science Track)  
**Author:** Tim Data Science Alpha  
**Tanggal:** 5 September 2026  
**Status:** Verified & Completed (100% 1-to-1 Match)  
**Dataset Output:** [`datasets/fireline_master_analytical_labeled_2024_2026.csv`](../datasets/fireline_master_analytical_labeled_2024_2026.csv)  
**Skrip Pipeline:** [`scripts/06_build_master_integrated_dataset.py`](../scripts/06_build_master_integrated_dataset.py)  

---

## 1. Ringkasan Eksekutif

Proses integrasi analitis (*Master Analytical Integration*) telah berhasil menggabungkan lima domain data spasial dan temporal ke dalam satu tabel master berlabel (*master labeled dataset*). Dataset ini mempertahankan unit observasi primer (**Primary Grain: 1 baris = 1 deteksi titik api satelit NASA VIIRS**) dengan jumlah baris yang **tepat 61.583 baris** tanpa penambahan atau pengurangan baris.

Setiap baris data telah diperkaya dengan parameter atmosferik BMKG, kondisi kelembapan tanah sub-permukaan, karakteristik kedalaman lahan gambut, metrik keterpaparan fasilitas pendidikan BPS via cKDTree, serta perhitungan skor tiga pilar kerangka risiko BNPB/UNDRR (**Calculated Risk Prioritization Index / CRPI**) dan label target kelas urgensi operasional (Tier 1 s.d Tier 4).

### Ringkasan Statistik Kunci:
1. **Total Observasi:** 61.583 baris (100,00% valid, 0 duplikat).
2. **Kesesuaian Waktu (WIB):** Sebanyak 6.304 titik api (10,24%) yang terdeteksi setelah pukul 17:00 UTC berhasil diselaraskan ke tanggal operasional lokal hari berikutnya (`operational_date` = WIB / UTC+7).
3. **Cakupan Cuaca BMKG:** 61.583 baris (100,00%) terhubung dengan stasiun cuaca terdekat dalam radius toleransi representatif.
4. **Proksimitas Sekolah:** Median jarak titik api ke fasilitas sekolah terdekat adalah **2,79 km** (50% kebakaran berada dalam radius <2,8 km dari sekolah).
5. **Rata-Rata Indeks Risiko (CRPI):** 47,55 (Skala 0 - 100), dengan rentang nilai 13,18 s.d 88,18.
6. **Distribusi Kelas Urgensi:**
   - **Tier 1 - Kritis (CRPI $\ge$ 80):** 26 insiden (0,04%)
   - **Tier 2 - Tinggi (60 $\le$ CRPI < 80):** 7.611 insiden (12,36%)
   - **Tier 3 - Sedang (40 $\le$ CRPI < 60):** 39.676 insiden (64,43%)
   - **Tier 4 - Rendah (CRPI < 40):** 14.270 insiden (23,17%)

---

## 2. Struktur Skema Data Master Final (Data Dictionary)

Tabel berikut merinci 41 atribut kolom yang tersusun dalam berkas [`datasets/fireline_master_analytical_labeled_2024_2026.csv`](../datasets/fireline_master_analytical_labeled_2024_2026.csv):

| Kategori Fitur | Nama Kolom | Tipe Data | Deskripsi dan Sumber Data |
| :--- | :--- | :---: | :--- |
| **Identitas & Kunci** | `detection_id` | String | Kunci unik sintetis format `FRL-{YYYYMMDD}-{HHMM}-{Lat}-{Lon}` (Presisi 5 desimal) |
| | `latitude` | Float | Koordinat lintang titik api (NASA VIIRS NOAA-20) |
| | `longitude` | Float | Koordinat bujur titik api (NASA VIIRS NOAA-20) |
| | `acq_date` | Date | Tanggal deteksi satelit berbasis UTC (YYYY-MM-DD) |
| | `acq_time` | Integer | Waktu deteksi satelit berbasis UTC (HHMM) |
| | `operational_date` | Date | Tanggal operasional harian lokal WIB (UTC+7) |
| **Administrasi Spasial** | `province_name` | String | Nama provinsi kanonikal Kalimantan (dengan penanganan garis pantai) |
| | `province_official` | String | Nama provinsi hasil poligon ketat [`indonesia_provinces.json`](../indonesia_provinces.json) |
| | `is_in_kalimantan` | Boolean | Indikator titik api berada di 5 provinsi Kalimantan (100% True) |
| **Fisika Termal Api** | `brightness` | Float | Suhu kecerahan kanal termal I-4 (Kelvin) |
| | `bright_t31` | Float | Suhu latar belakang kanal termal I-5 (Kelvin) |
| | `temp_delta` | Float | Selisih suhu api murni (`brightness - bright_t31`) |
| | `frp` | Float | *Fire Radiative Power* dalam MegaWatt (MW) |
| | `confidence` | String | Tingkat keyakinan sensor satelit (`l`, `n`, `h`) |
| | `daynight` | String | Observasi Siang (`D`) atau Malam (`N`) |
| | `scan` | Float | Resolusi piksel sepanjang pemindaian (*along-scan*) |
| | `track` | Float | Resolusi piksel sepanjang lintasan (*along-track*) |
| **Karakteristik Gambut** | `is_peatland` | Integer | Indikator berada di Kesatuan Hidrologis Gambut (1 = Gambut, 0 = Mineral) |
| | `nama_khg` | String | Nama unit Kesatuan Hidrologis Gambut (SK.129 KLHK) |
| | `khg_id` | String | Kode identitas poligon KHG |
| | `peat_depth` | String | Kelas kedalaman gambut (Sangat Dalam, Dalam, Sedang, Dangkal, Tanah Mineral) |
| | `depth_cm` | Float | Estimasi numerik ketebalan gambut (50 s.d 350 cm) |
| | `fungsi_zona` | String | Fungsi tata ruang gambut (Fungsi Lindung vs Budidaya) |
| | `peat_hazard_multiplier` | Float | Pengali bahaya kebakaran gambut (1,00x s.d 1,35x) |
| **Konteks Cuaca BMKG** | `nearest_station_city` | String | Kota stasiun observasi cuaca BMKG terdekat |
| | `station_dist_km` | Float | Jarak speroid *Haversine* ke stasiun BMKG terdekat (km) |
| | `weather_available` | Boolean | Validitas ketersediaan data cuaca stasiun (100% True) |
| | `temperature_2m_max` | Float | Suhu udara maksimum harian (°C) |
| | `temperature_2m_mean` | Float | Suhu udara rata-rata harian (°C) |
| | `relative_humidity_2m_min` | Float | Kelembapan relatif minimum harian (%) |
| | `relative_humidity_2m_mean` | Float | Kelembapan relatif rata-rata harian (%) |
| | `precipitation_sum` | Float | Akumulasi curah hujan harian (mm) |
| | `windspeed_10m_max` | Float | Kecepatan hembusan angin maksimum pada ketinggian 10 m (km/jam) |
| | `vapor_pressure_deficit_max`| Float | Defisit Tekanan Uap / VPD maksimum (kPa) |
| | `is_dry_day` | Integer | Flag hari tanpa hujan efektif (< 1 mm) |
| **Kekeringan Gambut** | `soil_moisture_0_to_7cm` | Float | Kadar air tanah lapisan atas 0-7 cm ($m^3/m^3$) |
| | `soil_moisture_7_to_28cm` | Float | Kadar air tanah lapisan perakaran 7-28 cm ($m^3/m^3$) |
| | `soil_moisture_28_to_100cm`| Float | Kadar air tanah lapisan dalam 28-100 cm ($m^3/m^3$) |
| | `soil_temperature_0_to_7cm` | Float | Suhu permukaan tanah (°C) |
| **Paparan Sekolah BPS** | `nearest_school_name` | String | Nama fasilitas sekolah terdekat hasil pencarian cKDTree |
| | `nearest_school_stage` | String | Jenjang pendidikan sekolah terdekat (SD, SMP, SMA, SMK, SLB) |
| | `nearest_school_distance_km`| Float | Jarak fisik absolut ke sekolah terdekat (km) |
| | `schools_within_5km` | Integer | Jumlah sekolah dalam radius bahaya langsung 5 km |
| | `schools_within_10km` | Integer | Jumlah sekolah dalam radius sebaran asap 10 km |
| **Skor Risiko & Label** | `hazard_score` | Float | Sub-skor Bahaya Fisik Termal & Multiplier Gambut (Skala 0 - 100) |
| | `vulnerability_score` | Float | Sub-skor Kerentanan Atmosfer & Kekeringan Lahan (Skala 0 - 100) |
| | `exposure_score` | Float | Sub-skor Keterpaparan Manusia & Fasilitas Pendidikan (Skala 0 - 100) |
| | `crpi_score` | Float | **Calculated Risk Prioritization Index** Komposit (Skala 0 - 100) |
| | `urgency_tier` | String | Label Target Klasifikasi Tindakan (Tier 1 s.d Tier 4) |
| | `rekomendasi_taktis` | String | Instruksi operasional tanggap darurat untuk Satgas B2G |

---

## 3. Formulasi Komputasi CRPI dan Pelabelan (Berdasarkan Dokumen 04 & 05)

### A. Pilar 1: Hazard Score (Bobot 35%)
$$\text{Hazard\_Score} = \min\Big(100,\; \big(0.40 \cdot \text{FRP\_Norm} + 0.35 \cdot \text{Temp\_Delta\_Norm} + 0.25 \cdot \text{Confidence\_Weight}\big) \cdot \text{Peat\_Multiplier} \cdot 100\Big)$$
- $\text{FRP\_Norm} = \min(1.0, \frac{\ln(1 + \text{frp})}{\ln(1 + 500)})$
- $\text{Temp\_Delta\_Norm} = \min(1.0, \max(0.0, \frac{\text{brightness} - \text{bright\_t31}}{120}))$
- $\text{Confidence\_Weight}$: `h` = 1.0, `n` = 0.7, `l` = 0.5 (jika FRP > 100 MW) atau 0.3.
- $\text{Peat\_Multiplier}$: Sangat Dalam (1.35x), Dalam (1.25x), Sedang (1.15x), Dangkal (1.05x), Tanah Mineral (1.00x).

### B. Pilar 2: Vulnerability Score (Bobot 25%)
$$\text{Vulnerability\_Score} = \Big(0.30 \cdot \text{VPD\_Norm} + 0.25 \cdot (1 - \text{RH\_Norm}) + 0.25 \cdot \text{Wind\_Norm} + 0.20 \cdot \text{Soil\_Deficit\_Norm}\Big) \cdot 100$$
- $\text{VPD\_Norm} = \min(1.0, \frac{\text{vpd\_max}}{3.0})$
- $\text{RH\_Norm} = \frac{\text{relative\_humidity\_2m\_min}}{100}$
- $\text{Wind\_Norm} = \min(1.0, \frac{\text{windspeed\_10m\_max}}{30.0})$
- $\text{Soil\_Deficit\_Norm} = \max(0.0, 1.0 - \frac{\text{soil\_moisture\_0\_to\_7cm}}{0.40})$

### C. Pilar 3: Exposure Score (Bobot 40%)
$$\text{Exposure\_Score} = \Big(0.60 \cdot \text{Proximity\_Score} + 0.40 \cdot \text{Facility\_Density\_5km}\Big) \cdot 100$$
- $\text{Proximity\_Score} = \max(0.0, 1.0 - \frac{d_{\text{min}}}{10.0\text{ km}})$. Jika jarak $< 1\text{ km}$, skor bernilai 1.0 (maksimum).
- $\text{Facility\_Density\_5km} = \min(1.0, \frac{\text{schools\_within\_5km}}{10.0})$.

### D. Skor Komposit CRPI & Ambang Batas Urgensi:
$$\text{CRPI\_Score} = (0.35 \cdot \text{Hazard\_Score}) + (0.25 \cdot \text{Vulnerability\_Score}) + (0.40 \cdot \text{Exposure\_Score})$$

| Kelas Urgensi | Ambang Skor CRPI | Jumlah Kasus | Persentase | Rekomendasi Tindakan Cepat (DSS) |
| :--- | :---: | :---: | :---: | :--- |
| **Tier 1: Kritis** | $\ge 80,0$ | **26** | **0,04%** | Mobilisasi Operasi Udara: *Water-Bombing* & Evakuasi Sekolah Segera (< 1 Jam) |
| **Tier 2: Tinggi** | $60,0 - 79,9$ | **7.611** | **12,36%** | Pengerahan Regu Darat: Manggala Agni & TRC BPBD (< 3 Jam) |
| **Tier 3: Sedang** | $40,0 - 59,9$ | **39.676** | **64,43%** | Patroli Rutin: Pembuatan Sekat Bakar & *Rewetting* Lahan Gambut |
| **Tier 4: Rendah** | $< 40,0$ | **14.270** | **23,17%** | Pemantauan Satelit: Monitoring Pasif Deret Waktu Tanpa Dislokasi Armada |

---

## 4. Distribusi Spasial per Provinsi

| Provinsi | Total Titik Api | Tier 1 (Kritis) | Tier 2 (Tinggi) | Tier 3 (Sedang) | Tier 4 (Rendah) | Rata-Rata CRPI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kalimantan Barat** | 36.100 | 18 | 4.908 | 23.492 | 7.682 | 48,15 |
| **Kalimantan Timur** | 11.029 | 3 | 1.144 | 7.031 | 2.851 | 46,24 |
| **Kalimantan Tengah** | 8.442 | 4 | 1.059 | 5.253 | 2.126 | 47,40 |
| **Kalimantan Selatan**| 3.597 | 1 | 358 | 2.458 | 780 | 46,92 |
| **Kalimantan Utara** | 2.415 | 0 | 142 | 1.442 | 831 | 44,70 |
| **Total Seluruh Pulau** | **61.583** | **26** | **7.611** | **39.676** | **14.270** | **47,55** |

---

## 5. Validasi Integritas Data

Skrip integrasi telah memverifikasi seluruh syarat kontraktual data:
1. `assert len(df_final) == 61583`: Berhasil terpenuhi tanpa pengecualian.
2. `assert df_final['detection_id'].nunique() == 61583`: Terbukti 100% unik tanpa duplikasi.
3. `assert df_final['weather_available'].all()`: Terbukti 100% observasi memiliki konteks atmosferik.
4. Ukuran Berkas Fisik: **26,74 MB**, sangat ideal untuk diimpor ke dalam Tableau Desktop maupun Public tanpa melampaui limit penyimpanan.
