# Dokumen Arsitektur dan Spesifikasi Visualisasi Dashboard Tableau FIRELINE

**Platform:** FIRELINE (Decision Support System Mitigasi Karhutla Kalimantan)  
**Trek Kompetisi:** Data Science Track - COMPFEST 18  
**Tim:** Alpha  
**Deliverable Checkpoint 2:** Baseline Model Konseptual, CRPI Engine Logic, dan Data Visualization Specs  
**Dokumen Acuan:** SystemData_Checkpoint2_Alpha.pdf

---

## 1. Pendahuluan dan Formasi Tim Analisis

Untuk memenuhi seluruh cakupan tugas Data Scientist / Analyst (DSA) pada Checkpoint 2, rancangan dashboard Tableau FIRELINE dibangun dengan pendekatan multi-tab modular. Sistem ini mengintegrasikan data fisik api, kondisi atmosfer, dan kerentanan manusia ke dalam satu kesatuan sistem pendukung keputusan (Decision Support System).

Struktur tim terdiri dari 3 orang DSA dengan pembagian kepemilikan analitik sebagai berikut:

* **DSA 1 (Lead Spatial & Risk Modeling):**
  - Bertanggung jawab atas Tab 1 (Executive Overview) dan Tab 2 (Hazard Analytics NASA VIIRS).
  - Fokus tugas: Perancangan model komposit Calculated Risk Prioritization Index (CRPI), klasifikasi urgensi insiden (Tier 1-4), analisis Fire Radiative Power (FRP), koreksi bobot keyakinan satelit, dan deteksi 224 grid kebakaran kronis (Chronic Fire Zones).
* **DSA 2 (Lead Meteorological & Climate Analytics):**
  - Bertanggung jawab atas Tab 3 (Meteorology & Climate Vulnerability Engine).
  - Fokus tugas: Integrasi data observasi harian BMKG 2024-2026, pemodelan efek jeda kekeringan (14-day rolling drought lag-effect), Defisit Tekanan Uap (Vapor Pressure Deficit / VPD), dinamika arah angin, serta validasi anomali iklim dekadal Kaggle 2010-2020 (El Nino 2015 dan IOD 2019).
* **DSA 3 (Lead Human Exposure & Dynamic Re-scoring):**
  - Bertanggung jawab atas Tab 4 (Human Exposure & Vital Assets) dan Tab 5 (Dynamic Re-scoring & Verification Workflow).
  - Fokus tugas: Algoritma proksimitas spasial terhadap 17.549 fasilitas pendidikan BPS, penentuan zonasi darurat evakuasi (radius 1 km, 3 km, 5 km), agregasi populasi usia rentan terdampak, dan formulasi logika pembaruan bobot risiko otomatis (Dynamic Re-scoring) berbasis laporan warga terverifikasi.

---

## 2. Matriks Komprehensif Pemetaan Dataset (.CSV)

Tabel berikut merinci peran setiap dataset, variabel kunci yang diekstraksi, relasi penggabungan (join logic), dan penempatannya pada tab dashboard:

| # | Nama File Dataset | Sumber & Karakteristik | Variabel Kunci yang Digunakan | Relasi Penggabungan (Join / Linkage) | Penempatan Tab |
|---|---|---|---|---|---|
| 1 | `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | NASA FIRMS (61.583 baris, VIIRS NOAA-20) | `latitude`, `longitude`, `acq_date`, `acq_time`, `frp`, `brightness`, `bright_t31`, `confidence`, `daynight` | Tabel fakta utama (Spatial coordinates & timestamp) | Tab 1, Tab 2 |
| 2 | `bmkg_kalimantan_weather_2024_2026.csv` | BMKG / ERA5 Reanalysis (9.366 baris, 14 stasiun) | `date`, `city`, `province`, `temp_max`, `humidity_min`, `precipitation_sum`, `windspeed_10m_max`, `vpd_max`, `is_dry_day` | Spatial Nearest Station + Date matching ke Hotspot | Tab 1, Tab 3 |
| 3 | `climate_data.csv` | BMKG Kaggle (87.238 baris Kalimantan, 2010-2020) | `date`, `station_id`, `Tx`, `RH_avg`, `RR`, `ff_avg`, `ss` | Relasi `station_id` ke `station_detail.csv` | Tab 3 |
| 4 | `station_detail.csv` | Direktori Stasiun BMKG (192 baris nasional) | `station_id`, `station_name`, `latitude`, `longitude`, `province_id` | Foreign key relasi ke `climate_data` dan `province_detail` | Tab 3 |
| 5 | `province_detail.csv` | Referensi Wilayah (34 baris) | `province_id`, `province_name` | Lookup nama provinsi untuk stasiun BMKG | Tab 3 |
| 6 | `complete_data.csv` | BPS & Dapodik (17.549 sekolah Kalimantan) | `province_name`, `city_name`, `district_name`, `school_name`, `stage`, `lat`, `long`, `total_education_age_population` | Spatial KD-Tree Join (Jarak minimum ke titik hotspot) | Tab 1, Tab 4 |
| 7 | `pontianak_weather_daily_2021_2024.csv` | Stasiun Supadio Pontianak (1.734 baris) | `date`, `TAVG`, `RH_AVG`, `RR` | Validasi silang tren iklim mikro episentrum Kalbar | Tab 3 |
| 8 | `forestfires.csv` | UCI ML Montesinho (517 baris) | `FFMC`, `DMC`, `DC`, `ISI`, `temp`, `RH`, `wind`, `rain` | Benchmark teoretis FWI pada dokumen laporan teknis (tidak dimuat ke dashboard Tableau agar visualisasi 100% murni fokus Kalimantan) | Laporan Dokumen (Non-Dashboard) |
| 9 | `fireline_citizen_reports_simulation.csv` | Simulasi Log Portal B2C & Verifikasi Lapangan (~2.000 baris) | `report_id`, `hotspot_id`, `report_timestamp`, `citizen_latitude`, `citizen_longitude`, `report_type`, `verification_status`, `verified_by`, `response_time_minutes`, `crpi_initial`, `crpi_updated` | Spatial Buffer Join (0,2 - 3,0 km) & Temporal matching ke hotspot aktif | Tab 5 |
| 10 | `kalimantan_peatland_spatial.geojson` | BBSDLP & SK.129 KLHK (25 Poligon KHG, 4,06 Juta Ha) | `khg_id`, `nama_khg`, `provinsi`, `kabupaten`, `peat_depth`, `depth_cm`, `luas_ha`, `geometry` | Spatial Overlay (Underlay layer visual peta di bawah titik api) | Tab 1, Tab 2 |
| 11 | `kalimantan_peat_soil_moisture_2024_2026.csv` | Open-Meteo ERA5-Land Reanalysis (9.366 baris, 14 stasiun) | `date`, `city`, `soil_moisture_0_to_7cm`, `soil_moisture_7_to_28cm`, `soil_moisture_28_to_100cm`, `soil_temperature_0_to_7cm` | Join tanggal & stasiun BMKG untuk indikator kekeringan gambut | Tab 1, Tab 3 |
| 12 | `fireline_hotspot_peat_featured_2024_2026.csv` | Hasil Integrasi Point-in-Polygon (61.732 baris) | Seluruh variabel hotspot + `is_peatland`, `peat_depth`, `depth_cm`, `soil_moisture_0_to_7cm`, `peat_hazard_multiplier` | Tabel fakta terpadu hasil feature engineering | Tab 1, Tab 2, Tab 4, Tab 5 |

---

## 2.2 Pemetaan Rinci Penggunaan Dataset (.CSV) dan Fitur per Tab Dashboard

Berikut adalah pemetaan operasional rinci untuk setiap tab dashboard, merinci file CSV yang dipanggil, fitur/kolom spesifik yang diekstraksi, tipe data, serta fungsi penggunaannya pada komponen visual:

### A. Tab 1: Executive Command Center & CRPI Prioritization (Overview Operasional Utama)
*Tujuan: Layar kendali tanggap darurat pimpinan satgas untuk penilaian cepat (<1 jam).*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 1 |
|---|---|---|---|
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `latitude`, `longitude` | Float | Menentukan titik koordinat spasial hotspot pada Interactive GIS Map. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `acq_date`, `acq_time` | Date/Time | Filter tanggal harian dan pencatatan jam kejadian pada tabel antrean insiden. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `frp` | Float | Mengatur ukuran titik (*mark size*) lingkaran hotspot pada peta GIS. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `windspeed_10m_max` | Float | Menampilkan metrik kecepatan angin maksimum pada Kartu KPI 4 Command Bar. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `temperature_2m_max`, `relative_humidity_2m_min` | Float | Variabel masukan perhitungan sub-skor Vulnerability per stasiun/wilayah. |
| `complete_data.csv` (17.549 Sekolah) | `min_distance_to_school_km` | Float | Kolom tabel antrean insiden untuk verifikasi jarak ke fasilitas vital terdekat. |
| `complete_data.csv` (17.549 Sekolah) | `schools_within_5km_count` | Int | Menampilkan total sekolah terancam pada Kartu KPI 3 Command Bar. |
| `complete_data.csv` (17.549 Sekolah) | `city_name`, `district_name` | String | Atribut wilayah administrasi pada tabel antrean aksi cepat. |
| *Calculated Field Engine* | `CRPI_Composite_Score` | Float | Menentukan intensitas warna heatmap KDE dan sorting prioritas antrean insiden. |
| *Calculated Field Engine* | `CF_Urgency_Tier` | String | Kategori warna titik peta (Merah/Oranye/Kuning/Hijau) & segmen Donut Chart. |
| *Calculated Field Engine* | `Rekomendasi_Taktis` | String | Kolom instruksi operasional lapangan (Water-bombing, TRC Darat, Patroli). |
| `kalimantan_peatland_spatial.geojson` | `geometry`, `nama_khg`, `peat_depth` | Spatial Poligon | Underlay layer visual batas kubah gambut (warna cokelat transparan 40%) di bawah titik api. |
| `kalimantan_peat_soil_moisture_2024_2026.csv` | `soil_moisture_0_to_7cm` | Float | Indikator kekeringan tanah pada tooltip titik api dan filter kebakaran gambut aktif. |

---

### B. Tab 2: Hazard & Fire Severity Analytics (NASA VIIRS Deep-Dive)
*Tujuan: Membedah karakter fisik termal api dan mengungkap titik buta satelit.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 2 |
|---|---|---|---|
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `brightness` | Float | Suhu kecerahan kanal termal I-4 (4 µm) dalam Kelvin untuk estimasi suhu api. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `bright_t31` | Float | Suhu latar belakang kanal termal I-5 (11 µm) dalam Kelvin. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `brightness - bright_t31` (Temp Delta) | Float | Sumbu X Scatter Plot Termal untuk membedakan anomali api vs panas permukaan. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `frp` | Float | Sumbu Y Scatter Plot Termal (skala logaritmik) pelepasan energi api (MW). |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `confidence` | String | Pewarnaan (*color marks*) Scatter Plot untuk membuktikan anomali saturasi asap. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `daynight`, `acq_time` | String/Int | Sumbu Heatmap Matriks Disparitas Deteksi Siang vs Malam. |
| `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | `latitude`, `longitude` | Float | Agregasi kisi grid spasial 0,05° x 0,05° untuk Peta 224 Zona Kebakaran Kronis. |
| `kalimantan_peatland_spatial.geojson` | `geometry`, `nama_khg`, `depth_cm` | Spatial Poligon | Overlay spasial korelasi 224 Zona Kebakaran Kronis terhadap kubah gambut dalam. |
| `fireline_hotspot_peat_featured_2024_2026.csv` | `is_peatland`, `peat_depth`, `peat_hazard_multiplier` | Mixed | Filter perbandingan termal dan pelepasan energi (FRP) di lahan gambut vs tanah mineral. |

---

### C. Tab 3: Meteorology & Climate Vulnerability Engine (BMKG & Kaggle)
*Tujuan: Memodelkan pemicu atmosferik kekeringan, jeda waktu kemarau, dan anomali iklim.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 3 |
|---|---|---|---|
| `bmkg_kalimantan_weather_2024_2026.csv` | `date` | Date | Sumbu horizontal (X) grafik deret waktu operasional harian. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `temperature_2m_max` | Float | Indikator suhu maksimum pada Bullet Gauge ambang kritis (>33,0 °C). |
| `bmkg_kalimantan_weather_2024_2026.csv` | `relative_humidity_2m_min` | Float | Indikator kelembapan minimum pada Bullet Gauge ambang kritis (<65%). |
| `bmkg_kalimantan_weather_2024_2026.csv` | `precipitation_sum`, `is_dry_day` | Float/Int | Kurva akumulasi hari kering (*14-day rolling drought*) pada grafik sumbu ganda. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `vapor_pressure_deficit_max` | Float | Kurva Defisit Tekanan Uap (VPD) pada grafik deret waktu pemicu kekeringan. |
| `kalimantan_peat_soil_moisture_2024_2026.csv` | `soil_moisture_0_to_7cm`, `soil_moisture_7_to_28cm` | Float | Kurva kadar air lapisan gambut atas dan dalam pada Grafik Deret Waktu Sumbu Ganda. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `windspeed_10m_max`, `windgusts_10m_max` | Float | Visualisasi panjang vektor kecepatan angin pada Peta Mawar Angin (*Wind Rose*). |
| `bmkg_kalimantan_weather_2024_2026.csv` | `city`, `province` | String | Filter pemilihan stasiun BMKG lokal di 5 provinsi Kalimantan. |
| `climate_data.csv` (24 Stasiun Kalimantan) | `date`, `Tx`, `RH_avg`, `RR` | Mixed | Area Chart Anomali Dekadal (2010-2020) mengukur dampak El Nino 2015 & IOD 2019. |
| `station_detail.csv` & `province_detail.csv` | `station_id`, `station_name`, `province_name` | String/Int | Lookup relasi identitas stasiun dan provinsi di Pulau Kalimantan. |
| `pontianak_weather_daily_2021_2024.csv` | `date`, `TAVG`, `RH_AVG`, `RR` | Mixed | Grafik garis validasi silang anomali iklim mikro Kota Pontianak (2021-2024). |

---

### D. Tab 4: Human Exposure & Vital Facility Vulnerability (BPS & Sekolah)
*Tujuan: Memetakan keterancaman fasilitas pendidikan dan melindungi populasi usia rentan.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 4 |
|---|---|---|---|
| `complete_data.csv` (17.549 Sekolah) | `lat`, `long` | Float | Koordinat fisik fasilitas sekolah pada Peta Sebaran Sekolah Kalimantan. |
| `complete_data.csv` (17.549 Sekolah) | `school_name` | String | Nama fasilitas pada tabel pengawasan (*School Safety Watchlist*). |
| `complete_data.csv` (17.549 Sekolah) | `stage` | String | Pewarnaan titik jenjang pendidikan (SD, SMP, SMA, SMK, SLB) & bobot evakuasi. |
| `complete_data.csv` (17.549 Sekolah) | `status` | String | Filter kepemilikan sekolah (Negeri vs Swasta). |
| `complete_data.csv` (17.549 Sekolah) | `city_name` | String | Sumbu X Diagram Batang Agregasi Sekolah Terdampak per Kabupaten. |
| `complete_data.csv` (17.549 Sekolah) | `district_name`, `province_name` | String | Hierarki filter wilayah mikro dan makro. |
| *KD-Tree Join (Hotspot NASA)* | `min_distance_to_school_km` | Float | Filter interaktif proksimitas bahaya (<1 km, 1-3 km, 3-5 km). |
| *KD-Tree Join (Hotspot NASA)* | `schools_within_5km_count` | Int | Sumbu Y Diagram Batang Konsentrasi Sekolah dalam Kepungan Asap. |
| *Calculated Field Engine* | `CF_Exposure_Score` | Float | Pengurutan prioritas perlindungan pada *School Safety Watchlist*. |

---

### E. Tab 5: Dynamic Re-Scoring & Ground-Truth Verification Workflow
*Tujuan: Merealisasikan alur verifikasi laporan warga (B2C Crowdsourcing) dan mendemonstrasikan algoritma pembaruan risiko otomatis (Dynamic Re-scoring) pada dashboard B2G.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 5 |
|---|---|---|---|
| `fireline_citizen_reports_simulation.csv` | `report_id` | String | Identifier unik tiket pengaduan pada tabel antrean verifikasi lapangan. |
| `fireline_citizen_reports_simulation.csv` | `hotspot_id` | String | Foreign key penaut ke titik api satelit NASA di `fireline_hotspot_peat_featured`. |
| `fireline_citizen_reports_simulation.csv` | `report_timestamp` | DateTime | Penanda waktu warga mengirim laporan (sumbu waktu deret antrean). |
| `fireline_citizen_reports_simulation.csv` | `citizen_latitude`, `citizen_longitude` | Float | Koordinat GPS pelapor untuk penanda bendera biru pada Peta Konkordansi Spasial. |
| `fireline_citizen_reports_simulation.csv` | `distance_to_hotspot_km` | Float | Validasi jarak warga terhadap hotspot satelit (radius toleransi 0,2 - 3,0 km). |
| `fireline_citizen_reports_simulation.csv` | `province`, `city_regency`, `district` | String | Atribut wilayah administrasi laporan warga. |
| `fireline_citizen_reports_simulation.csv` | `report_type` | String | Kategori pengaduan (*Smoldering Peat*, *Asap Masuk Sekolah*, *Lahan Terbuka*, *Api Padam*). |
| `fireline_citizen_reports_simulation.csv` | `reporter_role` | String | Tipe pelapor (*Warga Lokal*, *Pihak Sekolah*, *Relawan MPA*, *Petugas Desa*). |
| `fireline_citizen_reports_simulation.csv` | `verification_status` | String | Tahapan alur kerja pada Corong Antrean Verifikasi (*Pipeline Funnel*). |
| `fireline_citizen_reports_simulation.csv` | `verified_by` | String | Identitas regu pemeriksa (*TRC BPBD Regu 1*, *Manggala Agni Daops Ketapang*, dll.). |
| `fireline_citizen_reports_simulation.csv` | `verification_timestamp` | DateTime | Waktu saat petugas lapangan menyelesaikan verifikasi. |
| `fireline_citizen_reports_simulation.csv` | `response_time_minutes` | Float | Metrik efisiensi waktu tanggap pada Kartu KPI SLA Performance (< 1 jam). |
| `fireline_citizen_reports_simulation.csv` | `crpi_initial`, `crpi_updated` | Float | Sumbu Sebelum vs Sesudah pada Simulator Matriks Dynamic Re-scoring. |
| `fireline_citizen_reports_simulation.csv` | `urgency_tier_initial`, `urgency_tier_updated` | String | Visualisasi pergeseran kelas urgensi insiden (misal Tier-3 melonjak jadi Tier-1). |
| `fireline_citizen_reports_simulation.csv` | `tactical_action_dispatched` | String | Kolom instruksi pengerahan armada baru hasil re-scoring (Water-Bombing / Regu Darat). |

> **Notice Arsitektur B2C vs B2G (Pemisahan Tanggung Jawab Input Web):**
> * **Di Sisi Pengguna (Web B2C Public Portal):** Warga **TIDAK** diminta mengisi 21 fitur rumit. Antarmuka web B2C dirancang sangat cepat (*frictionless*) dengan hanya **3 - 4 input sederhana**: (1) Tombol GPS "Gunakan Lokasi Saya", (2) Pilihan cepat kategori kejadian (4 ikon), (3) Unggah foto bukti kamera HP, dan (4) Keterangan singkat 1 kalimat.
> * **Di Sisi Sistem (SEA Backend Auto-Enrichment):** Sistem backend otomatis melakukan *spatial matching* ke hotspot terdekat, menghitung jarak `distance_to_hotspot_km`, mengisi data wilayah, dan mencatat `report_timestamp`.
> * **Di Sisi Operasional Lapangan (Petugas B2G):** Petugas satgas hanya mengklik tombol "Validasi Laporan", memilih kategori temuan lapangan, dan sistem otomatis menghitung `response_time_minutes`.
> * **Di Sisi Engine DSA:** Model analitik secara otomatis menghitung `crpi_updated` dan memperbarui visualisasi Tab 5 di Tableau.

---

## 3. Logika Pemodelan CRPI dan Urgency Engine

Sistem mengadopsi standar kerangka risiko bencana internasional (BNPB dan UNDRR):

$$\text{RISK} = \text{HAZARD} \times \text{VULNERABILITY} \times \text{EXPOSURE}$$

> **Ruang Lingkup Persamaan:** Menjadi fondasi konseptual arsitektur komputasi risiko di seluruh komponen dashboard.

### 3.1 Formulasi Sub-Skor Tiga Pilar (Skala 0 - 100)

#### A. Pilar 1: Hazard Score (Bahaya Fisik Api dan Multiplier Gambut)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 2** (Hazard & Fire Severity Analytics)

Mengukur besaran pelepasan energi termal api dengan koreksi keandalan sensor optik satelit serta penyesuaian risiko api bawah tanah (*sub-surface smoldering*) pada lahan gambut:

$$\text{Hazard\_Score} = \min\Big(100,\; \big(0.40 \times \text{FRP\_Norm} + 0.35 \times \text{Temp\_Delta\_Norm} + 0.25 \times \text{Confidence\_Weight}\big) \times \text{Peat\_Hazard\_Multiplier} \times 100\Big)$$

* `FRP_Norm`: Normalisasi logaritmik $\min(1.0, \frac{\ln(1 + \text{frp})}{\ln(1 + 500)})$.
* `Temp_Delta_Norm`: Normalisasi selisih suhu $\min(1.0, \frac{\text{brightness} - \text{bright\_t31}}{120})$.
* `Confidence_Weight`: Bobot keyakinan satelit (`h` = 1.0, `n` = 0.7, `l` = 0.5 jika FRP > 100 MW untuk mengoreksi saturasi asap tebal).
* `Peat_Hazard_Multiplier`: Pengali bahaya kedalaman gambut berdasarkan poligon Kesatuan Hidrologis Gambut (KHG):
  - Gambut Sangat Dalam (>300 cm): $1.35\times$ (Risiko pembakaran lambat masif, emisi karbon gigaton, dan api sulit dipadamkan).
  - Gambut Dalam (200 - 300 cm): $1.25\times$.
  - Gambut Sedang (100 - 200 cm): $1.15\times$.
  - Gambut Dangkal (50 - 100 cm): $1.05\times$.
  - Tanah Mineral / Non-Gambut: $1.00\times$.

#### B. Pilar 2: Vulnerability Score (Kerentanan Cuaca dan Lahan)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 3** (Meteorology & Climate Vulnerability Engine)

Mengukur potensi percepatan laju rambat api akibat kondisi atmosfer dan histori kekeringan lahan:

$$\text{Vulnerability\_Score} = 0.30 \times \text{VPD\_Norm} + 0.25 \times (1 - \text{RH\_Norm}) + 0.25 \times \text{Wind\_Norm} + 0.20 \times \text{Drought14d\_Norm}$$

* `VPD_Norm`: Defisit tekanan uap $\min(1.0, \frac{\text{vpd\_max}}{3.0})$.
* `RH_Norm`: Kelembapan relatif minimum $\frac{\text{humidity\_min}}{100}$.
* `Wind_Norm`: Kecepatan angin maksimum $\min(1.0, \frac{\text{windspeed\_10m\_max}}{30})$.
* `Drought14d_Norm`: Akumulasi hari kering 14 hari terakhir $\frac{\text{dry\_days\_count}}{14}$.

#### C. Pilar 3: Exposure Score (Paparan Manusia dan Fasilitas Vital)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 4** (Human Exposure & Vital Assets)

Mengukur dampak kerugian terhadap nyawa dan aset pendidikan di Kalimantan melalui komputasi jarak spasial cKDTree terhadap 17.549 sekolah:

$$\text{Exposure\_Score} = 0.60 \times \text{Proximity\_Score} + 0.40 \times \text{Facility\_Density\_5km}$$

* $\text{Proximity\_Score} = \max(0, 1 - \frac{d_{\text{min}}}{10\text{ km}})$. Jika jarak titik api ke sekolah < 1 km, skor kedekatan bernilai 1.0 (maksimum).
* $\text{Facility\_Density\_5km} = \min(1.0, \frac{\text{schools\_within\_5km\_count}}{10})$. Kerapatan jumlah sekolah dalam radius bahaya 5 km.
*(Catatan Metodologi: Menggunakan proksi spasial murni fasilitas sekolah karena 100% berbasis koordinat riil Kalimantan dan independen dari keterbatasan data sensus tingkat kecamatan).*

### 3.2 Formula Penggabungan Komposit (CRPI Composite Score)
> **Diaplikasikan pada:** **Tab 1** (Sorting Antrean Insiden & Heatmap) dan **Tab 5** (Skor Baseline Sebelum Verifikasi)

$$\text{CRPI} = (0.35 \times \text{Hazard\_Score}) + (0.25 \times \text{Vulnerability\_Score}) + (0.40 \times \text{Exposure\_Score})$$

*Bobot Exposure (40%) ditetapkan tertinggi karena keselamatan jiwa manusia dan fasilitas publik merupakan prioritas utama dalam operasi kedaruratan nasional.*

### 3.3 Matriks Klasifikasi Tingkat Urgensi Insiden (Decision Support System)
> **Diaplikasikan pada:** **Tab 1** (Donut Chart & Warna Titik Peta) dan **Tab 5** (Matriks Pergeseran Status Tanggap Darurat)

| Kelas Urgensi | Rentang Nilai CRPI | Karakteristik Insiden | Protokol Rekomendasi Taktis (DSS) |
|---|---|---|---|
| **Tier-1: Critical Risk** | **80 - 100** | Api intensitas tinggi di lahan kering gambut, radius < 3 km dari sekolah atau pemukiman padat. | **Mobilisasi Operasi Udara:** Pengerahan helikopter water-bombing, penerbitan instruksi evakuasi atau peliburan sekolah kepada BPBD dan Dinas Pendidikan dalam < 1 jam. |
| **Tier-2: High Risk** | **60 - 79** | Api skala sedang di lahan rentan, akumulasi kemarau 14 hari, radius 3 - 7 km dari fasilitas publik. | **Pengerahan Regu Darat Cepat:** Pengiriman tim pemadam Manggala Agni dan TRC BPBD dengan target pemadaman di lokasi < 3 jam. |
| **Tier-3: Medium Risk** | **40 - 59** | Titik panas terdeteksi di area perkebunan atau hutan produksi, cuaca kering moderat, jarak > 7 km dari pemukiman. | **Patroli dan Penyekatan:** Pembasahan lahan gambut (rewetting) dan pembuatan parit penyekat api (firebreaks) oleh regu patroli rutin. |
| **Tier-4: Low Risk** | **0 - 39** | Anomali termal kecil terisolasi di pedalaman, kelembapan tinggi atau pasca hujan, jarak ke pemukiman > 15 km. | **Pemantauan Pasif:** Monitoring otomatis deret waktu satelit tanpa kebutuhan dislokasi logistik lapangan. |

### 3.4 Logika Pembaruan Skor Otomatis (Dynamic Re-scoring Logic)
> **Diaplikasikan pada:** **Tab 5** (Dynamic Re-scoring & Ground-Truth Verification Workflow)

Sistem memperbarui skor risiko secara dinamis setelah adanya laporan lapangan terverifikasi dari warga atau tim patroli:

$$\text{CRPI}_{\text{updated}} = \min(100, \text{CRPI}_{\text{initial}} \times (1 + \sum \Delta_{\text{koreksi}}))$$

Aturan penyesuaian bobot ditetapkan sebagai berikut:
1. **Verifikasi Api Gambut Bawah Permukaan (Smoldering Peat Fire):** Ditambahkan koreksi $\Delta = +0.25$ pada komponen Hazard, mengantisipasi keterbatasan sensor optik satelit terhadap api bawah tanah.
2. **Verifikasi Asap Pekat Masuk Pemukiman/Sekolah:** Ditambahkan koreksi $\Delta = +0.20$ pada komponen Exposure, mengeskalasi tingkat peringatan bahaya kesehatan ISPA.
3. **Verifikasi Titik Api Berhasil Dipadamkan:** Skor CRPI langsung diturunkan ke nilai dasar Tier-4 ($\text{CRPI} \le 20$) dan status insiden diubah menjadi terkendali.

---

## 4. Komponen Command Bar Header (Formula Agregasi Harian)
> **Diaplikasikan pada:** **Tab 1** (Sebagai Header Navigasi Eksekutif Utama Dashboard)

Command Bar terletak di bagian paling atas antarmuka dashboard sebagai instrumen navigasi dan pemantauan cepat. Komponen ini memuat 5 metrik agregasi harian yang dihitung secara dinamis:

1. **Total Titik Panas Aktif (Active Hotspots Count):**
   $$\text{Active Hotspots} = \sum_{i \in \text{Hari Terpilih}} \text{Hotspot\_ID}_i$$
2. **Jumlah Insiden Kritis Tier-1 (Critical Tier-1 Count):**
   $$\text{Critical Incidents} = \sum [\text{IF } \text{CRPI} \ge 80 \text{ THEN } 1 \text{ ELSE } 0 \text{ END}]$$
3. **Kecamatan Berstatus Bahaya Tinggi (High Risk Districts Count):**
   $$\text{High Risk Districts} = \text{COUNTD}([\text{Kecamatan}]) \quad \text{WHERE } \max(\text{CRPI}) \ge 60$$
4. **Rata-Rata Indeks Risiko Regional (Kalimantan Mean CRPI):**
   $$\overline{\text{CRPI}} = \frac{1}{N} \sum_{i=1}^{N} \text{CRPI}_i$$
5. **Indikator Status Siaga Darurat Provinsi (Provincial Emergency Status Badge):**
   - **SIAGA 1 (Merah):** Jika terdeteksi $\ge 5$ insiden Tier-1 dalam 24 jam.
   - **SIAGA 2 (Oranye):** Jika terdeteksi insiden Tier-2 tanpa insiden Tier-1.
   - **WASPADA (Kuning):** Jika mayoritas insiden berada pada Tier-3.
   - **AMAN (Hijau):** Seluruh insiden berada pada Tier-4 atau tidak ada hotspot.

---

## 5. Spesifikasi Visualisasi Data Spasial

Visualisasi spasial merupakan komponen sentral sistem informasi geografis FIRELINE:

### 5.1 Layer Heatmap Kerapatan Risiko (Risk Density Heatmap)
* Menggunakan algoritma Kernel Density Estimation (KDE) dua dimensi pada koordinat lintang dan bujur.
* Fungsi pembobotan intensitas: Setiap titik panas diberi bobot proporsional terhadap nilai akhir CRPI.
* Gradasi spektrum warna: Transparan (aman) $\rightarrow$ Kuning (risiko sedang) $\rightarrow$ Oranye (risiko tinggi) $\rightarrow$ Merah tua pekat (episentrum risiko kritis).
* Tujuan: Mengidentifikasi konsentrasi klaster risiko spasial yang melampaui batas administrasi kabupaten.

### 5.2 Batas Zonasi Darurat (Emergency Perimeter Buffering)
Setiap insiden yang terklasifikasi sebagai Tier-1 atau Tier-2 secara otomatis menampilkan 3 cincin batas perimeter darurat:
1. **Cincin Merah (Radius 1 km - Zona Bahaya Langsung):** Zona potensi kontak api langsung dan kebakaran struktural. Protokol: Evakuasi total warga dan penyemprotan sekat basah.
2. **Cincin Oranye (Radius 3 km - Zona Bahaya Asap Tebal):** Zona konsentrasi partikulat asap beracun (PM2.5) ekstrem. Protokol: Penghentian aktivitas sekolah, pembagian masker respiratorik, dan penutupan ruang publik.
3. **Cincin Kuning (Radius 5 km - Zona Siaga dan Penyangga):** Zona pemantauan arah rambatan api berdasarkan vektor angin BMKG.

### 5.3 Layer Spasial Dasar Kubah Gambut (Peatland Underlay & KHG Spatial Boundary)
* **Sumber Data:** `kalimantan_peatland_spatial.geojson` (25 Poligon Kesatuan Hidrologis Gambut utama, total luas 4,06 juta hektar di 5 provinsi Kalimantan).
* **Penempatan Layer:** Berada pada lapisan terbawah peta GIS (*underlay base layer*), tepat di bawah layer batas administrasi kabupaten dan layer titik hotspot.
* **Simbologi & Palet Warna:** Arsiran poligon cokelat-amber semi-transparan (Opacity 35-40%) dengan garis batas tipis (border 0,5 pt, dark brown). Gradasi warna membedakan kelas kedalaman kubah gambut:
  - Sangat Dalam (>300 cm): `#5D4037` (Deep Umber Brown, Opacity 45%)
  - Dalam (200 - 300 cm): `#795548` (Medium Brown, Opacity 40%)
  - Sedang (100 - 200 cm): `#8D6E63` (Light Brown, Opacity 35%)
  - Dangkal (50 - 100 cm): `#A1887F` (Pale Brown, Opacity 30%)
* **Fungsi Analitik:** Memberikan pemahaman situasional seketika (*instant situational awareness*) kepada komandan operasi bahwa hotspot yang jatuh di dalam zona poligon ini memiliki bahaya kebakaran bawah tanah (*smoldering*) yang persisten, sehingga membutuhkan teknik perendaman gambut (*peat rewetting*) dan parit sekat api, bukan sekadar pengeboman air permukaan (*water-bombing* biasa).

---

## 6. Konsep dan Struktur Terperinci 5 Tab Dashboard Tableau

---

### Tab 1: Executive Command Center & CRPI Prioritization (Overview Utama)
* **Penanggung Jawab:** DSA 1 (Lead) didukung DSA 2 dan DSA 3
* **Pengguna Sasaran:** Kepala Pelaksana BPBD, Komandan Lapangan Manggala Agni, Pimpinan Daerah.
* **Tujuan Analitik:** Menyajikan ringkasan situasi darurat operasional dalam satu tampilan layar terintegrasi untuk pengambilan keputusan cepat di bawah 1 jam.

#### Tata Letak Visualisasi:
1. **Bagian Header:** Komponen Command Bar (5 kartu KPI agregasi harian).
2. **Panel Kiri Utama (70% Area):** Peta Spasial Risiko Interaktif (Interactive GIS Map):
   - **Layer Dasar Kubah Gambut (Peatland Underlay Layer):** Menampilkan poligon 25 Kesatuan Hidrologis Gambut (KHG) seluas 4,06 juta hektar dari `kalimantan_peatland_spatial.geojson` dengan arsiran cokelat semi-transparan (35% opacity), memetakan zona rawan api bawah tanah secara visual.
   - **Layer Heatmap Kerapatan Risiko:** Gradasi warna KDE berbasis bobot komposit CRPI.
   - **Layer Simbologi Hotspot Individual:** Ukuran titik proporsional terhadap nilai FRP (MW) dan warna berdasarkan Tier Urgensi (Merah = Tier-1, Oranye = Tier-2, Kuning = Tier-3, Hijau = Tier-4).
   - **Layer Perimeter Kedaruratan:** Lingkaran perimeter zonasi darurat 3 km dan 5 km di sekitar titik Tier-1.
   - **Interactive Rich Tooltip:** Menampilkan nama KHG, status kedalaman gambut, kadar air tanah harian (`soil_moisture_0_to_7cm`), jarak ke sekolah terdekat, dan rekomendasi taktis.
   - **Cross-Filtering Interaktif:** Klik pada hotspot memfilter tabel antrean insiden dan grafik ringkasan secara instan.
3. **Panel Kanan Atas (30% Area):** Donut Chart Distribusi Tingkat Urgensi Insiden:
   - Proporsi persentase insiden aktif dalam kategori Critical, High, Medium, dan Low.
4. **Panel Bawah:** Tabel Antrean Prioritas Aksi (Action Priority Incident Queue):
   - Kolom tabel: ID Hotspot, Waktu Akuisisi, Provinsi, Kabupaten, Status Lahan Gambut / Nama KHG, Nilai FRP (MW), Jarak ke Sekolah Terdekat (km), Kadar Air Tanah (m³/m³), Skor CRPI, Tingkat Urgensi, dan Rekomendasi Taktis (Helikopter Water-Bombing, Regu Darat TRC, atau Patroli Pembasahan Gambut).

---

### Tab 2: Hazard & Fire Severity Analytics (NASA VIIRS Deep-Dive)
* **Penanggung Jawab:** DSA 1
* **Pengguna Sasaran:** Analis Data Penginderaan Jauh, Divisi Pemantauan Satelit.
* **Dataset yang Digunakan:** `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` (61.583 baris titik api Kalimantan), `kalimantan_peatland_spatial.geojson` (25 poligon KHG), `fireline_hotspot_peat_featured_2024_2026.csv` (hasil integrasi Point-in-Polygon). *(Catatan: `forestfires.csv` dialokasikan khusus sebagai benchmark algoritma pada dokumen laporan tertulis)*.
* **Fokus Wilayah:** 100% Pulau Kalimantan (Kalimantan Barat, Kalimantan Tengah, Kalimantan Selatan, Kalimantan Timur, Kalimantan Utara).
* **Tujuan Analitik:** Menganalisis sifat fisik kebakaran, mengidentifikasi titik kebakaran berulang di lahan gambut, mengungkap fenomena api bawah tanah (*smoldering*), dan mengkaji keterbatasan sensor satelit di atas langit Kalimantan.

#### Tata Letak Visualisasi:
1. **Scatter Plot Korelasi Termal (FRP vs Temp Delta vs Confidence):**
   - Sumbu X: Selisih Suhu Api terhadap Latar Belakang (`brightness` - `bright_t31` dalam Kelvin).
   - Sumbu Y: Radiasi Pelepasan Energi Api (`frp` dalam Megawatt, skala logaritmik).
   - Warna Titik: Tingkat Keyakinan Sensor (`confidence`: Low, Nominal, High).
   - Pembuktian Analitik: Menunjukkan bahwa titik api berkekuatan mega-fire (>500 MW) kerap dilabeli *Low Confidence* akibat terhalang kabut asap tebal, memperkuat argumen metodologis perlunya koreksi bobot keyakinan satelit.
2. **Heatmap Matriks Disparitas Deteksi Siang vs Malam:**
   - Matriks kalender bulan vs jam deteksi satelit.
   - Menyoroti temuan empiris bahwa 89,3% deteksi terjadi pada lintasan orbit siang hari, membuktikan keberadaan titik buta (*blind-spot*) pemantauan malam hari yang wajib diisi oleh sistem prakiraan cuaca.
3. **Peta dan Diagram Batang 224 Zona Kebakaran Kronis (Chronic Fire Zones) & Korelasi Gambut:**
   - Analisis spasial pada kisi grid 0,05 derajat (~5,5 km x 5,5 km).
   - Menampilkan 224 petak grid dengan frekuensi kebakaran tertinggi yang menyerap 99,9% aktivitas karhutla Kalimantan.
   - Overlay Spasial Kubah Gambut: Membuktikan bahwa konsentrasi zona kebakaran kronis paling persisten (pesisir Ketapang, Kubu Raya Kalbar, dan Pulang Pisau Kalteng) berhimpitan 100% di dalam batas poligon KHG kubah gambut dalam (>200-300 cm).
4. **Komparasi Dinamika Karakteristik Api Gambut vs Mineral (Peatland vs Mineral Fire Dynamics):**
   - Diagram batang / boxplot perbandingan rata-rata FRP (7,31 MW di gambut vs 10,88 MW di tanah mineral) dan rata-rata kadar air tanah (0,276 m³/m³ di gambut vs 0,307 m³/m³ di mineral).
   - Pembuktian Ilmiah: Membuktikan secara empiris bahwa api gambut menghasilkan FRP radiasi permukaan lebih rendah karena panas terperangkap di bawah permukaan tanah (*sub-surface smoldering*), sehingga sensor optik satelit cenderung meremehkan intensitasnya. Hal ini menjadi landasan ilmiah penetapan `Peat_Hazard_Multiplier` (1.05x - 1.35x).

---

### Tab 3: Meteorology & Climate Vulnerability Engine (BMKG & Kaggle)
* **Penanggung Jawab:** DSA 2
* **Pengguna Sasaran:** Analis Klimatologi BMKG, Tim Perencanaan Operasi Preventif.
* **Dataset yang Digunakan:** `bmkg_kalimantan_weather_2024_2026.csv`, `kalimantan_peat_soil_moisture_2024_2026.csv`, `climate_data.csv`, `station_detail.csv`, `province_detail.csv`, `pontianak_weather_daily_2021_2024.csv`.
* **Tujuan Analitik:** Memodelkan faktor pemicu kekeringan atmosfer, mengukur dinamika desikasi kadar air tanah gambut, membuktikan efek jeda waktu kemarau terhadap ledakan titik api, dan mengkalibrasi risiko berbasis anomali iklim dekadal.

#### Tata Letak Visualisasi:
1. **Grafik Deret Waktu Sumbu Ganda (Dual-Axis Drought, Peat Moisture, vs Hotspot Surge):**
   - Sumbu Garis Kiri 1: Akumulasi hari tanpa hujan berturut-turut (*14-day rolling drought*) dan rata-rata Defisit Tekanan Uap (VPD).
   - Sumbu Garis Kiri 2: Dinamika kadar air tanah gambut harian lapisan 0-7 cm dan 7-28 cm dari `kalimantan_peat_soil_moisture_2024_2026.csv`.
   - Sumbu Batang Kanan: Jumlah kemunculan titik api harian satelit.
   - Pembuktian Analitik: Memperlihatkan secara visual bahwa lonjakan titik api masif selalu didahului oleh periode kemarau kontinu 14 hari sebelumnya DAN penurunan kadar air tanah gambut di bawah ambang batas desikasi kritis (< 0,25 m³/m³), menjadi indikator dini peringatan kebakaran lahan (*peat fuel desiccation early warning*).
2. **Tachometer / Bullet Gauges Ambang Batas Kritis Cuaca dan Kelembapan Lahan:**
   - Menampilkan posisi metrik harian terhadap ambang batas kritis karhutla:
     - Suhu Udara Maksimum (Batas Bahaya: > 33,0 °C)
     - Kelembapan Relatif Minimum (Batas Bahaya: < 65%)
     - Defisit Tekanan Uap VPD (Batas Bahaya: > 1,8 kPa)
     - Kadar Air Tanah Lapisan 0-7 cm (Batas Kritis Gambut Kering: < 0,25 m³/m³)
     - Akumulasi Curah Hujan Harian (Batas Bahaya: < 2,0 mm)
3. **Peta Vektor Mawar Angin (Wind Rose Spread Model):**
   - Pemetaan arah dan kecepatan angin dari 14 stasiun meteorologi BMKG.
   - Berfungsi memproyeksikan lintasan perambatan api dan koridor sebaran kabut asap beracun menuju kawasan pemukiman padat.
4. **Area Chart Anomali Iklim Dekadal (2015 & 2019 vs Baseline 11 Tahun):**
   - Menggunakan 87.238 rekaman data iklim Kaggle (2010-2020).
   - Menampilkan komparasi anomali curah hujan dan suhu pada periode kemarau ekstrem El Nino 2015 dan IOD 2019 terhadap kondisi baseline normal Kalimantan.

---

### Tab 4: Human Exposure & Vital Facility Vulnerability (BPS & Sekolah)
* **Penanggung Jawab:** DSA 3
* **Pengguna Sasaran:** Dinas Pendidikan, Dinas Kesehatan, Bidang Perlindungan Masyarakat BPBD.
* **Dataset yang Digunakan:** `complete_data.csv` (17.549 fasilitas sekolah dan data kependudukan BPS), `indonesia-province-jml-penduduk.json`.
* **Tujuan Analitik:** Mengidentifikasi aset pendidikan yang terancam paparan api dan asap, menetapkan prioritas perlindungan kelompok usia rentan, dan menyusun rekomendasi kebijakan keselamatan publik.

#### Tata Letak Visualisasi:
1. **Peta Sebaran Fasilitas Pendidikan dan Proksimitas Bahaya:**
   - Pemetaan lokasi presisi 17.549 unit sekolah (SD, SMP, SMA, SLB) di seluruh Kalimantan.
   - Filter interaktif jarak proksimitas: Menampilkan sekolah yang berada dalam radius bahaya langsung (< 1 km), bahaya asap pekat (1 - 3 km), dan zona siaga (3 - 5 km) dari titik api aktif.
2. **Diagram Batang Agregasi Populasi Usia Pendidikan Terdampak per Kabupaten:**
   - Sumbu X: Kabupaten/Kota di Kalimantan.
   - Sumbu Y: Estimasi jumlah anak usia sekolah (`total_education_age_population`) yang berada dalam radius bahaya asap aktif.
   - Memberikan dasar keputusan bagi pemerintah daerah untuk mengeluarkan surat edaran peliburan sekolah atau pembelajaran jarak jauh (PJJ).
3. **Tabel Prioritas Evakuasi dan Perlindungan Sekolah (School Safety Watchlist):**
   - Daftar sekolah paling kritis terurut berdasarkan jarak terdekat ke titik api, jenjang pendidikan (Sekolah Dasar dan Sekolah Luar Biasa diprioritaskan karena kerentanan fisiologis dan evakuasi fisik), dan ketersediaan fasilitas kesehatan di kecamatan setempat.

---

### Tab 5: Dynamic Re-Scoring & Ground-Truth Verification Workflow
* **Penanggung Jawab:** DSA 3 (Lead) berkolaborasi dengan DSA 1 dan DSA 2
* **Pengguna Sasaran:** Operator Verifikasi Laporan Command Center, Petugas Lapangan TRC.
* **Dataset yang Digunakan:** `fireline_citizen_reports_simulation.csv` (simulasi ~2.000 log aduan warga B2C) terintegrasi spasial dengan `fireline_hotspot_peat_featured_2024_2026.csv`.
* **Tujuan Analitik:** Merealisasikan alur verifikasi laporan masyarakat dari lapangan (B2C Crowdsourcing) dan mendemonstrasikan algoritma pembaruan bobot risiko secara otomatis (Dynamic Re-scoring) pada command center B2G.

#### Tata Letak Visualisasi:
1. **Corong Antrean Verifikasi Laporan Warga (Verification Pipeline Funnel):**
   - Menampilkan metrik volume laporan pada setiap tahap alur kerja: Laporan Masuk $\rightarrow$ Sedang Diverifikasi Petugas $\rightarrow$ Terverifikasi Valid $\rightarrow$ Laporan Palsu/Ditolak $\rightarrow$ Status Penanganan Selesai.
2. **Simulator Dampak Dynamic Re-scoring (Before vs After Comparison Matrix):**
   - Visualisasi perbandingan skor risiko dan tingkat urgensi insiden sebelum verifikasi lapangan (murni bacaan satelit) vs sesudah verifikasi lapangan.
   - Contoh kasus: Titik api yang awalnya terdeteksi kecil oleh satelit (Tier-3 Skor 48) terbukti sebagai kebakaran gambut bawah tanah tebal yang merambat ke perimeter sekolah, sehingga sistem menaikkan skor secara instan menjadi Tier-1 (Skor 84).
3. **Peta Konkordansi Spasial Satelit vs Laporan Warga:**
   - Menampilkan overlay titik api satelit NASA (simbol lingkaran merah) bersanding dengan koordinat GPS laporan masyarakat (simbol penanda bendera biru).
   - Memvalidasi presisi laporan masyarakat terhadap anomali termal satelit dalam radius toleransi 5 km.
4. **Indikator Efisiensi Waktu Respons (SLA KPI Card):**
   - Menampilkan rata-rata waktu yang dibutuhkan dari penerimaan laporan hingga verifikasi dan pengerahan tim lapangan, membuktikan pencapaian target pemangkasan waktu respons dari 12-24 jam menjadi di bawah 1 jam.

---

## 7. Spesifikasi Interaktivitas Global dan Kontrol Parameter

Untuk menjamin interaktivitas maksimal saat demonstrasi di hadapan dewan juri, dashboard dilengkapi panel kontrol global yang terhubung di seluruh tab:

* **Filter Rentang Waktu (Date Range Slider):** Memungkinkan pemilihan tanggal analisis spesifik (2024-2026) atau peninjauan pergerakan titik api harian secara animasi waktu (*time-lapse playback*).
* **Penyaringan Geografis Berjenjang (Hierarchical Geographical Filter):**
  - Dropdown Provinsi (Kalimantan Barat, Kalimantan Tengah, Kalimantan Selatan, Kalimantan Timur, Kalimantan Utara).
  - Dropdown Kabupaten/Kota (57 entitas).
  - Dropdown Kecamatan (605 entitas).
* **Parameter Analisis Sensitivitas Skenario (What-If Analysis Sliders):**
  - Slider Bobot Hazard ($w_H \in [0.20, 0.50]$, default 0.35).
  - Slider Bobot Vulnerability ($w_V \in [0.15, 0.35]$, default 0.25).
  - Slider Bobot Exposure ($w_E \in [0.30, 0.60]$, default 0.40).
  - *Fungsi:* Mengizinkan pengguna melakukan simulasi pergeseran prioritas operasi, misalnya memberikan bobot penyelamatan populasi lebih tinggi saat kebakaran mendekati kota besar.

---

## 8. Panduan Teknis Implementasi Tableau (Calculated Fields dan LOD Expressions)

Berikut adalah formula teknis yang siap diaplikasikan langsung pada kalkulasi kolom Tableau Desktop:

### 8.1 Calculated Field: Skor Normalisasi Hazard (CF_Hazard_Score)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 2** (Hazard & Fire Severity Analytics)

```tableau
// CF_Hazard_Score: Normalisasi FRP logaritmik, selisih suhu, bobot keyakinan satelit, dan pengali bahaya gambut
MIN(100.0, 
  (
    ( 0.40 * MIN(1.0, LN(1 + [frp]) / LN(1 + 500)) ) +
    ( 0.35 * MIN(1.0, ([brightness] - [bright_t31]) / 120.0) ) +
    ( 0.25 * IF [confidence] = 'h' THEN 1.0 
             ELSEIF [confidence] = 'n' THEN 0.7 
             ELSEIF [confidence] = 'l' AND [frp] > 100 THEN 0.5 
             ELSE 0.3 END )
  ) * 
  (
    IF [peat_depth] = "Sangat Dalam (>300 cm)" THEN 1.35
    ELSEIF [peat_depth] = "Dalam (200-300 cm)" THEN 1.25
    ELSEIF [peat_depth] = "Sedang (100-200 cm)" THEN 1.15
    ELSEIF [peat_depth] = "Dangkal (50-100 cm)" THEN 1.05
    ELSE 1.00 END
  ) * 100.0
)
```

### 8.2 Calculated Field: Pengali Bahaya Kedalaman Gambut (CF_Peat_Hazard_Multiplier)
> **Diaplikasikan pada:** **Tab 1** (Tooltip Rincian Risiko) dan **Tab 2** (Filter Tingkat Kedalaman Gambut)

```tableau
IF ISNULL([is_peatland]) OR [is_peatland] = 0 THEN 1.00
ELSEIF [depth_cm] > 300 THEN 1.35
ELSEIF [depth_cm] > 200 THEN 1.25
ELSEIF [depth_cm] > 100 THEN 1.15
ELSEIF [depth_cm] > 50  THEN 1.05
ELSE 1.00
END
```

### 8.3 Calculated Field: Skor Proksimitas Fasilitas (CF_Exposure_Score)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 4** (Human Exposure & Vital Assets)

```tableau
// CF_Exposure_Score: Proksi Spasial Murni Fasilitas Sekolah (100% Berbasis Koordinat Riil Kalimantan)
( 0.60 * MAX(0.0, 1.0 - ([min_distance_to_school_km] / 10.0)) ) +
( 0.40 * MIN(1.0, [schools_within_5km_count] / 10.0) )
```

> **Catatan Alternatif:** Jika tim memilih opsi pra-pemrosesan Python dengan kolom estimasi disagregasi `[est_district_education_pop]`, formula dapat disesuaikan menjadi:
> `(0.50 * MAX(0.0, 1.0 - ([min_distance_to_school_km] / 10.0))) + (0.30 * MIN(1.0, [schools_within_5km_count] / 15.0)) + (0.20 * MIN(1.0, [est_district_education_pop] / 25000.0))`

### 8.4 Calculated Field: Klasifikasi Tingkat Urgensi (CF_Urgency_Tier)
> **Diaplikasikan pada:** **Tab 1** (Donut Chart & Warna Titik Peta) dan **Tab 5** (Simulator Matriks Re-scoring)

```tableau
IF [CRPI_Composite_Score] >= 80 THEN "Tier-1: Critical Risk"
ELSEIF [CRPI_Composite_Score] >= 60 THEN "Tier-2: High Risk"
ELSEIF [CRPI_Composite_Score] >= 40 THEN "Tier-3: Medium Risk"
ELSE "Tier-4: Low Risk"
END
```

### 8.5 Level of Detail (LOD) Expression: Jumlah Insiden Kritis per Tanggal
> **Diaplikasikan pada:** **Tab 1** (Header Command Bar - Kartu KPI 2: Critical Tier-1 Count)

```tableau
{ FIXED [acq_date] : SUM(IF [CRPI_Composite_Score] >= 80 THEN 1 ELSE 0 END) }
```

### 8.6 Level of Detail (LOD) Expression: Status Siaga Harian Provinsi
> **Diaplikasikan pada:** **Tab 1** (Header Command Bar - Badge Siaga Darurat) dan **Tab 3** (Overview Iklim Regional)

```tableau
IF { FIXED [acq_date], [province] : SUM(IF [CRPI_Composite_Score] >= 80 THEN 1 ELSE 0 END) } >= 5 THEN "SIAGA 1"
ELSEIF { FIXED [acq_date], [province] : SUM(IF [CRPI_Composite_Score] >= 60 THEN 1 ELSE 0 END) } >= 5 THEN "SIAGA 2"
ELSEIF { FIXED [acq_date], [province] : SUM(IF [CRPI_Composite_Score] >= 40 THEN 1 ELSE 0 END) } >= 5 THEN "WASPADA"
ELSE "AMAN"
END
```

### 8.7 Calculated Field: Status Peringatan Desikasi Gambut (CF_Peat_Desiccation_Alert)
> **Diaplikasikan pada:** **Tab 1** (Tooltip & Filter Hotspot Lahan Gambut Kritis) dan **Tab 3** (Status Ambang Batas Kelembapan Tanah)

```tableau
IF [is_peatland] = 1 AND [soil_moisture_0_to_7cm] < 0.25 THEN "DESIKASI KRITIS (BAHAYA API BAWAH TANAH TINGGI)"
ELSEIF [is_peatland] = 1 AND [soil_moisture_0_to_7cm] < 0.35 THEN "DEFISIT AIR MODERAT"
ELSEIF [is_peatland] = 1 THEN "GAMBUT BASAH (NORMAL)"
ELSE "TANAH MINERAL"
END
```
