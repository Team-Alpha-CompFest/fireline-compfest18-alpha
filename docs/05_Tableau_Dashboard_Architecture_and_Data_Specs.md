# Dokumen Arsitektur dan Spesifikasi Visualisasi Dashboard Tableau FIRELINE

**Platform:** FIRELINE (Decision Support System Mitigasi Karhutla Kalimantan)  
**Trek Kompetisi:** Data Science Track - COMPFEST 18  
**Tim:** Alpha  
**Deliverable Checkpoint 2:** Baseline Model Konseptual, CRPI Engine Logic, dan Data Visualization Specs  
**Dokumen Acuan:** `documents/Penyesuaian_Konsep_Dashboard.pdf`

> **Current implementation decision (08 September 2026):** Dashboard prototype menggunakan `datasets/fireline_master_analytical_labeled_2024_2026.csv` sebagai fakta utama. Nama field pada Tableau mengikuti schema master. Dataset pendukung digunakan sebagai source terpisah sesuai grain-nya; raw CSV tidak dijoin bebas di Tableau.

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
  - Fokus tugas: Algoritma proksimitas spasial terhadap 17.548 record sekolah Kalimantan (17.363 koordinat valid), penentuan zonasi darurat (radius 1 km, 3 km, 5 km), agregasi populasi usia rentan bila bridge tervalidasi, dan formulasi logika pembaruan bobot risiko otomatis (Dynamic Re-scoring) berbasis laporan warga terverifikasi.

---

## 2. Matriks Komprehensif Pemetaan Dataset (.CSV)

Tabel berikut merinci peran setiap dataset, variabel kunci yang diekstraksi, relasi penggabungan (join logic), dan penempatannya pada tab dashboard:

| # | Nama File Dataset | Sumber & Karakteristik | Variabel Kunci yang Digunakan | Relasi Penggabungan (Join / Linkage) | Penempatan Tab |
|---|---|---|---|---|---|
| 1 | `fireline_master_analytical_labeled_2024_2026.csv` | Integrated analytical fact (61.583 baris, grain hotspot-observation) | Master schema: hotspot, admin, peatland, weather, soil, school exposure, score, tier | Tabel fakta utama; satu baris per `detection_id` | Tab 1–4; Tab 5 sebagai baseline |
| 2 | `bmkg_kalimantan_weather_2024_2026.csv` | BMKG / ERA5 Reanalysis (9.366 baris, 14 stasiun) | `date`, `city`, `province`, `temperature_2m_max`, `relative_humidity_2m_min`, `precipitation_sum`, `windspeed_10m_max`, `vapor_pressure_deficit_max`, `is_dry_day` | Spatial nearest station + date matching ke hotspot | Tab 1, Tab 3 |
| 3 | `EDA/03_kaggle_indonesia_climate/03_preprocessing/kalimantan_climate_2010_2020_clean.csv` | BMKG Kaggle cleaned (87.238 baris Kalimantan, 2010-2020) | `date`, `station_id`, `Tx`, `RH_avg`, `RR`, `ff_avg`, `ss` | Relasi `station_id` ke station reference | Tab 3 |
| 4 | `datasets/station_detail.csv` | Direktori Stasiun BMKG (192 baris nasional) | `station_id`, `station_name`, `latitude`, `longitude`, `province_id` | Foreign key relasi ke dataset climate cleaned dan `datasets/province_detail.csv` | Tab 3 |
| 5 | `datasets/province_detail.csv` | Referensi Wilayah (34 baris) | `province_id`, `province_name` | Lookup nama provinsi untuk stasiun BMKG | Tab 3 |
| 6 | `datasets/processed/data4_schools_cleaned_kalimantan.csv` | BPS & Dapodik (17.548 record sekolah Kalimantan; 17.363 koordinat valid) | `province_name`, `city_name`, `district_name`, `school_name`, `stage`, `lat`, `long`, `total_education_age_population`, `has_valid_coord` | Spatial cKDTree/radius aggregation ke hotspot; source facility tetap terpisah | Tab 1, Tab 4 |
| 7 | `datasets/pontianak_weather_daily_2021_2024.csv` | Stasiun Supadio Pontianak (1.734 baris) | `date`, `TAVG`, `RH_AVG`, `RR` | Validasi silang tren iklim mikro episentrum Kalbar | Tab 3 |
| 8 | `datasets/forestfires.csv` | UCI ML Montesinho (517 baris) | `FFMC`, `DMC`, `DC`, `ISI`, `temp`, `RH`, `wind`, `rain` | Benchmark teoretis FWI pada dokumen laporan teknis (tidak dimuat ke dashboard Tableau agar visualisasi 100% murni fokus Kalimantan) | Laporan Dokumen (Non-Dashboard) |
| 9 | `datasets/fireline_citizen_reports_simulation.csv` | Dummy Log Portal B2C (20 baris untuk prototype) | `report_id`, `detection_id`, `report_timestamp`, citizen coordinates, `report_type`, `verification_status`, `crpi_initial`, `crpi_updated` | Dummy linkage ke `detection_id` master; kelak diganti input live | Tab 5 |
| 10 | `datasets/kalimantan_peatland_spatial.geojson` | BBSDLP & SK.129 KLHK (25 Poligon KHG, 4,06 Juta Ha) | `khg_id`, `nama_khg`, `provinsi`, `kabupaten`, `peat_depth`, `depth_cm`, `luas_ha`, `geometry` | Spatial Overlay (Underlay layer visual peta di bawah titik api) | Tab 1, Tab 2 |
| 11 | `kalimantan_peat_soil_moisture_2024_2026.csv` | Open-Meteo ERA5-Land Reanalysis (9.366 baris, 14 stasiun) | `date`, `city`, `soil_moisture_0_to_7cm`, `soil_moisture_7_to_28cm`, `soil_moisture_28_to_100cm`, `soil_temperature_0_to_7cm` | Join tanggal & stasiun BMKG untuk indikator kekeringan gambut | Tab 1, Tab 3 |
| 12 | `fireline_hotspot_peat_featured_2024_2026.csv` | Dataset turunan peat/enrichment yang sudah dideduplikasi (61.583 baris) | Hotspot + peatland dan soil fields | Provenance/upstream reference; bukan source utama Tableau | Audit/provenance |

### 2.1 Aturan Kualitas Data dan Batasan Prototype

* **Weather/admin quality:** Master saat ini memiliki `weather_available = True` pada seluruh 61.583 baris, tetapi 2.249 baris (3,65%) memiliki `station_dist_km > 200 km`. Pada prototype, data tetap dapat ditampilkan dari master dengan `station_dist_km` sebagai indikator kualitas dan tooltip peringatan **out-of-range station**. Untuk versi produksi, upstream wajib menetapkan coverage weather berdasarkan ambang 200 km, tidak melakukan imputasi diam-diam, dan menghitung ulang skor/menyimpan quality flag untuk baris yang tidak memenuhi ambang.
* **Administrative quality:** `province_name` dipakai sebagai label dashboard karena selalu terisi. `province_official` dipakai sebagai field validasi dan tidak boleh diisi secara spekulatif; 1.129 baris saat ini tidak memiliki nilai official. `district/kabupaten` dan `kecamatan` tidak boleh ditampilkan sebagai field master sebelum tersedia sumber/bridge yang tervalidasi. `is_in_kalimantan` pada master adalah scope label, bukan pengganti audit polygon produksi.
* **School quality:** File sekolah memiliki 17.548 record; 17.363 memiliki koordinat valid dan hanya record valid yang dipakai untuk hitung jarak/radius. Angka total dan angka valid harus dibedakan pada caption atau tooltip.
* **Grid quality:** Pada resolusi 0,05°, master menghasilkan sekitar 7.514 grid unik. Angka 224 diperlakukan sebagai shortlist priority grid setelah validasi recurrence, bukan jumlah seluruh grid dan bukan klaim cakupan 99,9%.
* **Tab 5:** Dataset `fireline_citizen_reports_simulation.csv` hanya dummy 20 baris untuk demonstrasi alur. Semua baris diberi `is_simulated = true`; metrik SLA dan validasi laporan tidak boleh dipresentasikan sebagai performa operasional nyata.

---

## 2.2 Pemetaan Rinci Penggunaan Dataset (.CSV) dan Fitur per Tab Dashboard

Berikut adalah pemetaan operasional rinci untuk setiap tab dashboard, merinci file CSV yang dipanggil, fitur/kolom spesifik yang diekstraksi, tipe data, serta fungsi penggunaannya pada komponen visual:

### A. Tab 1: Executive Command Center & CRPI Prioritization (Overview Operasional Utama)
*Tujuan: Layar kendali tanggap darurat pimpinan satgas untuk penilaian cepat (<1 jam).*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 1 |
|---|---|---|---|
| `fireline_master_analytical_labeled_2024_2026.csv` | `latitude`, `longitude` | Float | Menentukan titik koordinat spasial hotspot pada Interactive GIS Map. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `acq_date`, `acq_time`, `operational_date` | Date/Time | Traceability NASA UTC dan filter tanggal operasional WIB pada tabel antrean. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `frp` | Float | Mengatur ukuran titik (*mark size*) lingkaran hotspot pada peta GIS. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `windspeed_10m_max` | Float | Menampilkan metrik kecepatan angin maksimum pada Kartu KPI 4 Command Bar. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `temperature_2m_max`, `relative_humidity_2m_min` | Float | Variabel masukan perhitungan sub-skor Vulnerability per stasiun/wilayah. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `nearest_school_distance_km` | Float | Kolom tabel antrean insiden untuk verifikasi jarak ke fasilitas vital terdekat. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `schools_within_5km` | Int | Menampilkan total sekolah terancam pada Kartu KPI Command Bar. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `province_name` | String | Atribut wilayah administrasi; district/kabupaten belum tersedia di master. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `crpi_score` | Float | Menentukan intensitas warna heatmap KDE dan sorting prioritas antrean insiden. |
| *Calculated Field Engine* | `CF_Urgency_Tier` | String | Kategori warna titik peta (Merah/Oranye/Kuning/Hijau) & segmen Donut Chart. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `rekomendasi_taktis` | String | Kolom instruksi operasional lapangan (Water-bombing, TRC Darat, Patroli). |
| `kalimantan_peatland_spatial.geojson` | `geometry`, `nama_khg`, `peat_depth` | Spatial Poligon | Underlay layer visual batas kubah gambut (warna cokelat transparan 40%) di bawah titik api. |
| `kalimantan_peat_soil_moisture_2024_2026.csv` | `soil_moisture_0_to_7cm` | Float | Indikator kekeringan tanah pada tooltip titik api dan filter kebakaran gambut aktif. |

---

### B. Tab 2: Hazard & Fire Severity Analytics (NASA VIIRS Deep-Dive)
*Tujuan: Membedah karakter fisik termal api dan mengungkap titik buta satelit.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 2 |
|---|---|---|---|
| `fireline_master_analytical_labeled_2024_2026.csv` | `brightness` | Float | Suhu kecerahan kanal termal I-4 (4 µm) dalam Kelvin untuk estimasi suhu api. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `bright_t31` | Float | Suhu latar belakang kanal termal I-5 (11 µm) dalam Kelvin. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `temp_delta` | Float | Sumbu X Scatter Plot Termal untuk membedakan anomali api vs panas permukaan. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `frp` | Float | Sumbu Y Scatter Plot Termal (skala logaritmik) pelepasan energi api (MW). |
| `fireline_master_analytical_labeled_2024_2026.csv` | `confidence` | String | Pewarnaan (*color marks*) Scatter Plot untuk membuktikan anomali saturasi asap. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `daynight`, `acq_time` | String/Int | Sumbu Heatmap Matriks Disparitas Deteksi Siang vs Malam. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `latitude`, `longitude` | Float | Agregasi kisi grid spasial 0,05° x 0,05° untuk priority grid; seluruh grid tetap dapat ditampilkan. |
| `kalimantan_peatland_spatial.geojson` | `geometry`, `nama_khg`, `depth_cm` | Spatial Poligon | Overlay spasial korelasi 224 Zona Kebakaran Kronis terhadap kubah gambut dalam. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `is_peatland`, `peat_depth`, `peat_hazard_multiplier` | Mixed | Filter perbandingan termal dan pelepasan energi (FRP) di lahan gambut vs tanah mineral. |

---

### C. Tab 3: Meteorology & Climate Vulnerability Engine (BMKG & Kaggle)
*Tujuan: Memodelkan pemicu atmosferik kekeringan, jeda waktu kemarau, dan anomali iklim.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 3 |
|---|---|---|---|
| `bmkg_kalimantan_weather_2024_2026.csv` | `date` | Date | Sumbu horizontal (X) grafik deret waktu operasional harian. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `temperature_2m_max` | Float | Indikator suhu maksimum pada Bullet Gauge ambang kritis (>33,0 °C). |
| `bmkg_kalimantan_weather_2024_2026.csv` | `relative_humidity_2m_min` | Float | Indikator kelembapan minimum pada Bullet Gauge ambang kritis (<65%). |
| `bmkg_kalimantan_weather_2024_2026.csv` | `precipitation_sum`, `is_dry_day` | Float/Int | Kurva hari kering; fitur akumulasi *14-day rolling drought* masih planned dan tidak dianggap sebagai field aktual master. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `vapor_pressure_deficit_max` | Float | Kurva Defisit Tekanan Uap (VPD) pada grafik deret waktu pemicu kekeringan. |
| `kalimantan_peat_soil_moisture_2024_2026.csv` | `soil_moisture_0_to_7cm`, `soil_moisture_7_to_28cm` | Float | Kurva kadar air lapisan gambut atas dan dalam pada Grafik Deret Waktu Sumbu Ganda. |
| `bmkg_kalimantan_weather_2024_2026.csv` | `windspeed_10m_max`, `windgusts_10m_max` | Float | Visualisasi panjang vektor kecepatan angin pada Peta Mawar Angin (*Wind Rose*). |
| `bmkg_kalimantan_weather_2024_2026.csv` | `city`, `province` | String | Filter pemilihan stasiun BMKG lokal di 5 provinsi Kalimantan. |
| `EDA/03_kaggle_indonesia_climate/03_preprocessing/kalimantan_climate_2010_2020_clean.csv` (24 Stasiun Kalimantan) | `date`, `Tx`, `RH_avg`, `RR` | Mixed | Area Chart Anomali Dekadal (2010-2020) mengukur dampak El Nino 2015 & IOD 2019. |
| `station_detail.csv` & `province_detail.csv` | `station_id`, `station_name`, `province_name` | String/Int | Lookup relasi identitas stasiun dan provinsi di Pulau Kalimantan. |
| `pontianak_weather_daily_2021_2024.csv` | `date`, `TAVG`, `RH_AVG`, `RR` | Mixed | Grafik garis validasi silang anomali iklim mikro Kota Pontianak (2021-2024). |

---

### D. Tab 4: Human Exposure & Vital Facility Vulnerability (BPS & Sekolah)
*Tujuan: Memetakan keterancaman fasilitas pendidikan dan melindungi populasi usia rentan.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 4 |
|---|---|---|---|
| `datasets/processed/data4_schools_cleaned_kalimantan.csv` (17.548 record; 17.363 koordinat valid) | `lat`, `long` | Float | Koordinat fisik fasilitas sekolah pada Peta Sebaran Sekolah Kalimantan. |
| `datasets/processed/data4_schools_cleaned_kalimantan.csv` | `school_name` | String | Nama fasilitas pada tabel pengawasan (*School Safety Watchlist*). |
| `datasets/processed/data4_schools_cleaned_kalimantan.csv` | `stage` | String | Pewarnaan titik jenjang pendidikan (SD, SMP, SMA, SMK, SLB) & bobot evakuasi. |
| `datasets/processed/data4_schools_cleaned_kalimantan.csv` | `status` | String | Filter kepemilikan sekolah (Negeri vs Swasta). |
| `datasets/processed/data4_schools_cleaned_kalimantan.csv` | `city_name` | String | Atribut kota/kabupaten sekolah; agregasi terdampak memerlukan bridge hotspot-sekolah. |
| `datasets/processed/data4_schools_cleaned_kalimantan.csv` | `district_name`, `province_name` | String | Hierarki filter wilayah mikro dan makro pada source fasilitas. |
| *KD-Tree Join (Hotspot NASA)* | `nearest_school_distance_km` | Float | Filter interaktif proksimitas bahaya (<1 km, 1-3 km, 3-5 km). |
| *KD-Tree Join (Hotspot NASA)* | `schools_within_5km` | Int | Sumbu Y Diagram Batang Konsentrasi Sekolah dalam Kepungan Asap. |
| `fireline_master_analytical_labeled_2024_2026.csv` | `exposure_score` | Float | Pengurutan prioritas perlindungan pada *School Safety Watchlist*. |

---

### E. Tab 5: Dynamic Re-Scoring & Ground-Truth Verification Workflow
*Tujuan: Merealisasikan alur verifikasi laporan warga (B2C Crowdsourcing) dan mendemonstrasikan algoritma pembaruan risiko otomatis (Dynamic Re-scoring) pada dashboard B2G.*

| File Sumber (.CSV) | Fitur / Kolom yang Digunakan | Tipe Data | Peran & Penggunaan Visual pada Tab 5 |
|---|---|---|---|
| `datasets/fireline_citizen_reports_simulation.csv` | `report_id` | String | Identifier unik tiket pengaduan pada tabel antrean verifikasi lapangan. |
| `datasets/fireline_citizen_reports_simulation.csv` | `detection_id` | String | Foreign key penaut ke titik api satelit NASA di master. |
| `datasets/fireline_citizen_reports_simulation.csv` | `report_timestamp` | DateTime | Penanda waktu warga mengirim laporan (sumbu waktu deret antrean). |
| `datasets/fireline_citizen_reports_simulation.csv` | `citizen_latitude`, `citizen_longitude` | Float | Koordinat GPS pelapor untuk penanda bendera biru pada Peta Konkordansi Spasial. |
| `datasets/fireline_citizen_reports_simulation.csv` | `distance_to_hotspot_km` | Float | Validasi jarak warga terhadap hotspot satelit (radius toleransi 0,2 - 3,0 km). |
| `datasets/fireline_citizen_reports_simulation.csv` | `province_name` | String | Atribut provinsi laporan warga; field kota/kabupaten/kecamatan belum ada pada dummy. |
| `datasets/fireline_citizen_reports_simulation.csv` | `report_type` | String | Kategori dummy: `smoldering_peat`, `smoke_exposure`, `verified_minor`, `verified_severe`, atau `false_alarm`. |
| `datasets/fireline_citizen_reports_simulation.csv` | `reporter_role` | String | Tipe pelapor (*Warga Lokal*, *Pihak Sekolah*, *Relawan MPA*, *Petugas Desa*). |
| `datasets/fireline_citizen_reports_simulation.csv` | `verification_status` | String | Tahapan alur kerja pada Corong Antrean Verifikasi (*Pipeline Funnel*). |
| `datasets/fireline_citizen_reports_simulation.csv` | `verified_by` | String | Identitas regu pemeriksa; dapat kosong untuk status yang belum diverifikasi. |
| `datasets/fireline_citizen_reports_simulation.csv` | `verification_timestamp` | DateTime | Waktu saat petugas lapangan menyelesaikan verifikasi; dapat kosong pada status pending. |
| `datasets/fireline_citizen_reports_simulation.csv` | `response_time_minutes` | Float | Nilai simulasi untuk kartu SLA; tidak merepresentasikan performa operasional nyata. |
| `datasets/fireline_citizen_reports_simulation.csv` | `crpi_initial`, `crpi_updated` | Float | Sumbu Sebelum vs Sesudah pada Simulator Matriks Dynamic Re-scoring. |
| `datasets/fireline_citizen_reports_simulation.csv` | `urgency_tier_initial`, `urgency_tier_updated` | String | Visualisasi pergeseran kelas urgensi insiden (misal Tier-3 melonjak jadi Tier-1). |
| `datasets/fireline_citizen_reports_simulation.csv` | `dispatch_status`, `resolution_status` | String | Status pengerahan dan penyelesaian laporan pada prototype; instruksi taktis tetap diambil dari `rekomendasi_taktis` master setelah linkage. |
| `datasets/fireline_citizen_reports_simulation.csv` | `last_updated`, `is_simulated`, `source_type` | DateTime/Boolean/String | Audit freshness dan penanda bahwa seluruh record Tab 5 masih dummy. |

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

Mengukur potensi percepatan laju rambat api akibat kondisi atmosfer dan kekeringan lahan:

$$\text{Vulnerability\_Score} = (0.30 \times \text{VPD\_Norm} + 0.25 \times (1 - \text{RH\_Norm}) + 0.25 \times \text{Wind\_Norm} + 0.20 \times \text{Soil\_Deficit\_Norm}) \times 100$$

* `VPD_Norm`: Defisit tekanan uap $\min(1.0, \frac{\text{vapor\_pressure\_deficit\_max}}{3.0})$.
* `RH_Norm`: Kelembapan relatif minimum $\frac{\text{relative\_humidity\_2m\_min}}{100}$.
* `Wind_Norm`: Kecepatan angin maksimum $\min(1.0, \frac{\text{windspeed\_10m\_max}}{30})$.
* `Soil_Deficit_Norm`: Defisit kadar air tanah lapisan 0–7 cm, dihitung dari nilai `soil_moisture_0_to_7cm` pada master. `Drought14d_Norm` tetap menjadi fitur lanjutan yang belum dipakai pada CRPI master saat ini.

#### C. Pilar 3: Exposure Score (Paparan Manusia dan Fasilitas Vital)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 4** (Human Exposure & Vital Assets)

Mengukur dampak kerugian terhadap aset pendidikan di Kalimantan melalui komputasi jarak spasial cKDTree terhadap 17.548 record sekolah Kalimantan (17.363 koordinat valid):

$$\text{Exposure\_Score} = 0.60 \times \text{Proximity\_Score} + 0.40 \times \text{Facility\_Density\_5km}$$

* $\text{Proximity\_Score} = \max(0, 1 - \frac{d_{\text{min}}}{10\text{ km}})$. Jika jarak titik api ke sekolah < 1 km, skor kedekatan bernilai 1.0 (maksimum).
* $\text{Facility\_Density\_5km} = \min(1.0, \frac{\text{schools\_within\_5km}}{10})$. Kerapatan jumlah sekolah dalam radius bahaya 5 km.
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
   $$\text{Active Hotspots} = \text{COUNTD}([\text{detection\_id}]) \quad \text{pada hari terpilih}$$
2. **Jumlah Insiden Kritis Tier-1 (Critical Tier-1 Count):**
   $$\text{Critical Incidents} = \sum [\text{IF } \text{CRPI} \ge 80 \text{ THEN } 1 \text{ ELSE } 0 \text{ END}]$$
3. **Provinsi Berstatus Bahaya Tinggi (High Risk Provinces Count — prototype):**
   $$\text{High Risk Provinces} = \text{COUNTD}([\text{province\_name}]) \quad \text{WHERE } \max([\text{crpi\_score}]) \ge 60$$
   > KPI kabupaten/kecamatan ditunda sampai bridge administrasi tersedia dan tervalidasi.
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
   - **Layer Simbologi Hotspot Individual:** Ukuran titik proporsional terhadap nilai `frp` (MW) dan warna berdasarkan `urgency_tier` (Merah = Tier-1, Oranye = Tier-2, Kuning = Tier-3, Hijau = Tier-4).
   - **Layer Perimeter Kedaruratan:** Lingkaran perimeter zonasi darurat 1 km, 3 km, dan 5 km di sekitar titik Tier-1 dan Tier-2, mengikuti konsep PDF. Cincin ini adalah overlay decision-support, bukan batas evakuasi legal.
   - **Interactive Rich Tooltip:** Menampilkan nama KHG, status kedalaman gambut, kadar air tanah harian (`soil_moisture_0_to_7cm`), jarak ke sekolah terdekat, dan rekomendasi taktis.
   - **Cross-Filtering Interaktif:** Klik pada hotspot memfilter tabel antrean insiden dan grafik ringkasan secara instan.
3. **Panel Kanan Atas (30% Area):** Donut Chart Distribusi Tingkat Urgensi Insiden:
   - Proporsi persentase insiden aktif dalam kategori Critical, High, Medium, dan Low.
4. **Panel Bawah:** Tabel Antrean Prioritas Aksi (Action Priority Incident Queue):
   - Kolom tabel: `detection_id`, Waktu Akuisisi, `province_name`, Status Lahan Gambut / `nama_khg`, Nilai `frp` (MW), `nearest_school_distance_km`, Kadar Air Tanah (m³/m³), `crpi_score`, `urgency_tier`, dan `rekomendasi_taktis`. Kabupaten/kecamatan ditambahkan hanya jika bridge administrasi tervalidasi.

---

### Tab 2: Hazard & Fire Severity Analytics (NASA VIIRS Deep-Dive)
* **Penanggung Jawab:** DSA 1
* **Pengguna Sasaran:** Analis Data Penginderaan Jauh, Divisi Pemantauan Satelit.
* **Dataset yang Digunakan:** `fireline_master_analytical_labeled_2024_2026.csv` (61.583 baris titik api Kalimantan), `kalimantan_peatland_spatial.geojson` (25 poligon KHG). *(Catatan: raw NASA dan `fireline_hotspot_peat_featured_2024_2026.csv` tetap menjadi provenance/upstream; `forestfires.csv` dialokasikan khusus sebagai benchmark algoritma pada dokumen laporan tertulis)*.
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
3. **Peta dan Diagram Batang Priority Grid Kebakaran Kronis (Chronic Fire Zones) & Korelasi Gambut:**
   - Analisis spasial pada kisi grid 0,05 derajat (~5,5 km x 5,5 km).
   - Menampilkan 224 petak prioritas berdasarkan recurrence/frekuensi setelah validasi. Angka 224 adalah shortlist, bukan jumlah seluruh grid, dan klaim cakupan 99,9% tidak digunakan sebelum dibuktikan.
   - Overlay Spasial Kubah Gambut: Menguji apakah konsentrasi priority grid paling persisten (termasuk area Ketapang, Kubu Raya, dan Pulang Pisau) berada di dalam poligon KHG gambut dalam (>200-300 cm). Klaim overlap 100% hanya boleh ditulis setelah analisis spasial mengonfirmasinya.
4. **Komparasi Dinamika Karakteristik Api Gambut vs Mineral (Peatland vs Mineral Fire Dynamics):**
   - Diagram batang / boxplot perbandingan rata-rata FRP (7,31 MW di gambut vs 10,88 MW di tanah mineral) dan rata-rata kadar air tanah (0,276 m³/m³ di gambut vs 0,307 m³/m³ di mineral).
   - Interpretasi Analitik: Perbedaan FRP dan soil moisture menjadi indikasi yang perlu dianalisis terkait *sub-surface smoldering*; visual ini bukan bukti kausal. `Peat_Hazard_Multiplier` tetap diperlakukan sebagai asumsi pemodelan dan perlu validasi sensitivitas.

---

### Tab 3: Meteorology & Climate Vulnerability Engine (BMKG & Kaggle)
* **Penanggung Jawab:** DSA 2
* **Pengguna Sasaran:** Analis Klimatologi BMKG, Tim Perencanaan Operasi Preventif.
* **Dataset yang Digunakan:** `bmkg_kalimantan_weather_2024_2026.csv`, `kalimantan_peat_soil_moisture_2024_2026.csv`, `EDA/03_kaggle_indonesia_climate/03_preprocessing/kalimantan_climate_2010_2020_clean.csv`, `station_detail.csv`, `province_detail.csv`, `pontianak_weather_daily_2021_2024.csv`.
* **Tujuan Analitik:** Memodelkan faktor pemicu kekeringan atmosfer, mengukur dinamika desikasi kadar air tanah gambut, membuktikan efek jeda waktu kemarau terhadap ledakan titik api, dan mengkalibrasi risiko berbasis anomali iklim dekadal.

#### Tata Letak Visualisasi:
1. **Grafik Deret Waktu Sumbu Ganda (Dual-Axis Drought, Peat Moisture, vs Hotspot Surge):**
   - Sumbu Garis Kiri 1: Akumulasi hari tanpa hujan berturut-turut dan rata-rata Defisit Tekanan Uap (VPD). Fitur *14-day rolling drought* berstatus planned karena belum tersedia di master.
   - Sumbu Garis Kiri 2: Dinamika kadar air tanah gambut harian lapisan 0-7 cm dan 7-28 cm dari `kalimantan_peat_soil_moisture_2024_2026.csv`.
   - Sumbu Batang Kanan: Jumlah kemunculan titik api harian satelit.
   - Pembuktian Analitik: Menampilkan hubungan hotspot, cuaca, dan soil moisture. Jangan menyatakan efek jeda 14 hari sebagai hasil aktual sebelum fitur rolling dan validasinya dibuat.
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
* **Dataset yang Digunakan:** `datasets/processed/data4_schools_cleaned_kalimantan.csv` (17.548 fasilitas sekolah; 17.363 koordinat valid), `indonesia-province-jml-penduduk.json` hanya jika bridge agregasi tervalidasi.
* **Tujuan Analitik:** Mengidentifikasi aset pendidikan yang terancam paparan api dan asap, menetapkan prioritas perlindungan kelompok usia rentan, dan menyusun rekomendasi kebijakan keselamatan publik.

#### Tata Letak Visualisasi:
1. **Peta Sebaran Fasilitas Pendidikan dan Proksimitas Bahaya:**
   - Pemetaan lokasi presisi hingga 17.363 unit sekolah berkoordinat valid dari total 17.548 record (SD, SMP, SMA, SLB) di seluruh Kalimantan.
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
* **Dataset yang Digunakan:** `datasets/fireline_citizen_reports_simulation.csv` (20 log dummy untuk prototype) terintegrasi ke `detection_id` pada `fireline_master_analytical_labeled_2024_2026.csv`. Setelah publikasi, source dummy diganti input citizen report live dengan schema yang sama.
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
  - Dropdown kabupaten/kota dan kecamatan hanya diaktifkan setelah field/bridge administrasinya tervalidasi; field tersebut belum ada pada master saat ini.
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
ELSEIF [peat_depth] = "Sangat Dalam (>300 cm)" THEN 1.35
ELSEIF [peat_depth] = "Dalam (200-300 cm)" THEN 1.25
ELSEIF [peat_depth] = "Sedang (100-200 cm)" THEN 1.15
ELSEIF [peat_depth] = "Dangkal (50-100 cm)" THEN 1.05
ELSE 1.00
END
```

### 8.3 Calculated Field: Skor Proksimitas Fasilitas (CF_Exposure_Score)
> **Diaplikasikan pada:** **Tab 1** (Executive Command Center) dan **Tab 4** (Human Exposure & Vital Assets)

```tableau
// CF_Exposure_Score: Proksi Spasial Murni Fasilitas Sekolah (100% Berbasis Koordinat Riil Kalimantan)
( 0.60 * MAX(0.0, 1.0 - ([nearest_school_distance_km] / 10.0)) ) +
( 0.40 * MIN(1.0, [schools_within_5km] / 10.0) )
```

> **Catatan:** Formula prototype hanya menggunakan field sekolah yang benar-benar tersedia di master. Komponen populasi tidak dimasukkan ke CRPI sampai bridge agregasi sekolah/BPS tervalidasi.

### 8.4 Calculated Field: Klasifikasi Tingkat Urgensi (CF_Urgency_Tier)
> **Diaplikasikan pada:** **Tab 1** (Donut Chart & Warna Titik Peta) dan **Tab 5** (Simulator Matriks Re-scoring)

```tableau
IF [crpi_score] >= 80 THEN "Tier 1: Kritis (Critical Risk)"
ELSEIF [crpi_score] >= 60 THEN "Tier 2: Tinggi (High Risk)"
ELSEIF [crpi_score] >= 40 THEN "Tier 3: Sedang (Medium Risk)"
ELSE "Tier 4: Rendah (Low Risk)"
END
```

### 8.5 Level of Detail (LOD) Expression: Jumlah Insiden Kritis per Tanggal
> **Diaplikasikan pada:** **Tab 1** (Header Command Bar - Kartu KPI 2: Critical Tier-1 Count)

```tableau
{ FIXED [operational_date] : COUNTD(IF [crpi_score] >= 80 THEN [detection_id] END) }
```

### 8.6 Level of Detail (LOD) Expression: Status Siaga Harian Provinsi
> **Diaplikasikan pada:** **Tab 1** (Header Command Bar - Badge Siaga Darurat) dan **Tab 3** (Overview Iklim Regional)

```tableau
IF { FIXED [operational_date], [province_name] : COUNTD(IF [crpi_score] >= 80 THEN [detection_id] END) } >= 5 THEN "SIAGA 1"
ELSEIF { FIXED [operational_date], [province_name] : COUNTD(IF [crpi_score] >= 60 THEN [detection_id] END) } >= 5 THEN "SIAGA 2"
ELSEIF { FIXED [operational_date], [province_name] : COUNTD(IF [crpi_score] >= 40 THEN [detection_id] END) } >= 5 THEN "WASPADA"
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
