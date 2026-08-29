# Laporan EDA: Titik Panas (Hotspot) Fireline Kalimantan
## Data Kebakaran Aktif Satelit NASA VIIRS NOAA-20 | Agustus 2024 - Mei 2026

Dataset: fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv  
Tanggal Pemrosesan: 29 Agustus 2026  
Konteks: Platform FIRELINE - Studi Kasus COMPFEST 18 (Tim Alpha)  

---

## Ringkasan Dataset

| Atribut | Nilai |
|---|---|
| Total Baris Data | 61.583 deteksi titik panas |
| Rentang Waktu | 01 Agustus 2024 hingga 31 Mei 2026 (22 bulan) |
| Hari Pengamatan Unik | 629 hari |
| Rata-rata Deteksi Harian | 97,9 titik panas per hari |
| Total Energi Radiasi Api | 650,9 GW |
| Cakupan Wilayah | Seluruh Kalimantan (Lintang: -4.17 hingga 4.35, Bujur: 108.68 hingga 119.50) |
| Sensor dan Satelit | NASA VIIRS, Satelit NOAA-20 (N20) |
| Nilai Kosong (Missing Values) | 0 baris |
| Data Duplikat | 0 baris |

Kolom yang dihapus karena bernilai konstan (tanpa variansi informasi): satellite, instrument, type, version.

---

## Temuan Utama (Key Findings)

### Temuan 1: Kalimantan Barat Merupakan Episentrum Utama Karhutla

Provinsi Kalimantan Barat menyumbang 31.764 titik panas (51,6% dari total keseluruhan) serta 367.757 MW total daya radiasi api (FRP). Angka ini mendominasi seluruh wilayah Kalimantan.

| Provinsi | Jumlah Titik Panas | Proporsi | Total FRP (MW) |
|---|---|---|---|
| Kalimantan Barat | 31.764 | 51,6% | 367.757 |
| Kalimantan Tengah | 10.690 | 17,4% | 119.862 |
| Kalimantan Timur | 9.041 | 14,7% | 77.138 |
| Kalimantan Utara | 6.299 | 10,2% | 55.980 |
| Kalimantan Selatan | 3.014 | 4,9% | 25.775 |

Relevansi Dokumen PRD: Menjawab Kesenjangan 3 (Integrasi Data) - Konteks geografis untuk representasi risiko terpadu dan alokasi armada yang proporsional.

---

### Temuan 2: Musim Kemarau Mendorong 83,4% dari Seluruh Aktivitas Kebakaran

Sebanyak 51.375 titik panas (83,4%) terkonsentrasi pada musim kemarau (Juni hingga Oktober), dengan rata-rata FRP sebesar 11,24 MW dibandingkan 7,22 MW pada musim hujan (intensitas 55,6% lebih tinggi pada musim puncak).

- Bulan puncak: September 2024 dengan 16.911 titik panas dalam satu bulan saja
- Bulan terendah: Januari 2025 dengan hanya 124 titik panas (rasio disparitas 136 kali lipat)
- Disparitas musiman 136 kali lipat ini memberikan dasar empiris yang kuat untuk memicu sistem peringatan dini berbasis kalender dan pola cuaca pada FIRELINE

Relevansi Dokumen PRD: Menjawab Kesenjangan 1 (Dari Deteksi Menuju Prioritas) - Konteks temporal memungkinkan respons preventif daripada sekadar reaktif.

---

### Temuan 3: Distribusi FRP Sangat Condong ke Kanan (Right-Skewed)

Distribusi energi kebakaran menunjukkan ketimpangan yang sangat tajam antara api kecil dan kebakaran masif:

| Metrik Statistik | Nilai |
|---|---|
| Median FRP | 6,14 MW (separuh kebakaran berintensitas rendah) |
| Rata-rata FRP | 10,57 MW (tertarik ke atas oleh kejadian ekstrem) |
| Nilai Maksimum FRP | 954,79 MW (kejadian ekstrem tunggal) |
| FRP > 100 MW (Kategori Ekstrem) | 285 kejadian (0,46%) |
| FRP > 500 MW (Kategori Mega-Fire) | 6 kejadian (0,01%) |

Rasio antara median dan nilai maksimum mencapai 1 banding 155. Hal ini membuktikan bahwa sebagian kecil kebakaran melepaskan energi destruktif yang luar biasa besar. Sistem penanganan yang menyamaratakan seluruh titik panas dipastikan akan mengalami salah alokasi armada (misallocation of resources).

Relevansi Dokumen PRD: Menjawab Kesenjangan 2 (Dari Informasi Risiko Menuju Keputusan Operasional).

---

### Temuan 4: Kejadian Kebakaran Masif (Mega-Fire) Bersifat Spesifik Lokasi dan Tanggal

Daftar 5 kejadian kebakaran terbesar (FRP di atas 500 MW):

| Tanggal | Koordinat | FRP (MW) | Provinsi | Tingkat Keyakinan |
|---|---|---|---|---|
| 2025-03-08 | -2.617, 114.710 | 954,79 | Kalimantan Selatan | Low |
| 2025-03-08 | -2.869, 114.798 | 825,59 | Kalimantan Selatan | Low |
| 2026-03-05 | -1.490, 110.142 | 652,45 | Kalimantan Barat | Low |
| 2024-09-17 | -0.007, 116.810 | 550,29 | Kalimantan Timur | Nominal |
| 2024-09-17 | -0.008, 116.805 | 550,29 | Kalimantan Timur | Low |

Catatan penting: 4 dari 5 kejadian kebakaran terbesar membawa label keyakinan (confidence) Low. Hal ini membuktikan bahwa tingkat keyakinan rendah pada sensor satelit tidak selalu berarti api berintensitas rendah, melainkan akibat saturasi sensor atau gangguan asap pekat. Fitur weighted_frp mengoreksi bobot reliabilitas tanpa membuang sinyal bahaya fisik ini.

Relevansi Dokumen PRD: Menjawab Kesenjangan 1 (Penentuan Prioritas) - Kejadian seperti inilah yang wajib dimunculkan FIRELINE sebagai Tanggap Darurat Tier-1.

---

### Temuan 5: Teridentifikasi 224 Zona Kebakaran Kronis (Kerentanan Tinggi)

Sebanyak 224 sel grid (resolusi 0,5 derajat atau sekitar 55 km x 55 km) terdeteksi terbakar berulang kali sebanyak 5 kali atau lebih dalam rentang 22 bulan. Zona kebakaran kronis ini mengindikasikan:

- Pola tata guna lahan yang berulang memicu api (pembukaan lahan pertanian, drainase lahan gambut)
- Kurangnya efektivitas intervensi preventif pada musim sebelumnya
- Kerentanan struktural yang tinggi terlepas dari kondisi cuaca sesaat

Sebanyak 61.549 dari 61.583 titik panas (99,9%) berada di dalam sel grid dengan rekurensi tinggi. Masalah karhutla di Kalimantan secara spasial sangat terkonsentrasi dan memiliki pola historis yang dapat diprediksi.

Relevansi Dokumen PRD: Menjawab Kesenjangan 3 (Dimensi Kerentanan / Vulnerability pada Penilaian Risiko Kontekstual).

---

### Temuan 6: Komposisi Tingkat Keyakinan Deteksi Sensor

| Kategori Keyakinan | Jumlah | Proporsi | Rata-rata FRP (MW) |
|---|---|---|---|
| Nominal (n) | 57.315 | 93,1% | 10,45 |
| Tinggi / High (h) | 2.320 | 3,8% | 15,79 |
| Rendah / Low (l) | 1.948 | 3,2% | 9,23 |

Titik panas dengan keyakinan tinggi rata-rata memiliki FRP 51% lebih besar dibandingkan keyakinan rendah. Fitur bobot keyakinan (confidence_weight: l=0.3, n=0.7, h=1.0) memberikan penyesuaian matematis yang berprinsip bagi mesin penilai risiko tanpa mengabaikan deteksi ekstrem.

Relevansi Dokumen PRD: Memperkuat dimensi BAHAYA (HAZARD) pada kerangka kerja Penilaian Risiko Kontekstual.

---

### Temuan 7: Pemantauan Satelit Siang Hari Menciptakan Titik Buta Sistematis

Sebanyak 54.988 deteksi (89,3%) terjadi pada perlintasan satelit siang hari. Hanya 6.595 deteksi (10,7%) yang tertangkap pada malam hari. Implikasi operasionalnya:

- Kebakaran yang menyala pada malam hari berpotensi tidak terpantau selama lebih dari 12 jam hingga jadwal satelit siang berikutnya
- Hal ini menjelaskan salah satu faktor di balik jeda verifikasi lapangan 12 hingga 24 jam yang disorot dalam dokumen PRD
- Deteksi malam hari memiliki rata-rata FRP sedikit lebih tinggi (10,8 MW vs 10,5 MW siang), mengindikasikan bahwa api yang bertahan menyala pada malam hari cenderung lebih persisten dan besar

Relevansi Dokumen PRD: Menjawab Akar Masalah 3 (Keterlambatan aliran informasi dan respons).

---

### Temuan 8: Intensitas Api dan Selisih Suhu Merupakan Sinyal Independen

Nilai korelasi Pearson antara frp dan temp_delta_K (selisih suhu kecerahan kanal 4 dengan kanal I-5) bernilai moderat (r = 0,52). Ringkasan matriks korelasi:

- brightness vs bright_t31: r = 0,83 (tinggi, keduanya merespons suhu lingkungan)
- frp vs hazard_score: r = 0,82 (skor bahaya didominasi oleh komponen FRP sesuai rancangan)
- frp vs temp_delta_K: r = 0,52 (korelasi moderat, memberikan informasi independen tambahan)

Korelasi moderat ini membuktikan bahwa selisih suhu api terhadap latar belakang tanah (temp_delta_K) memberikan informasi unik di luar metrik FRP mentah.

Relevansi Dokumen PRD: Mendukung penggunaan temp_delta_K sebagai parameter independen penilai bahaya kebakaran.

---

### Temuan 9: Tidak Ditemukan Perbedaan Perilaku Signifikan Hari Kerja vs Akhir Pekan

| Periode | Jumlah Titik Panas | Proporsi | Rata-rata FRP (MW) |
|---|---|---|---|
| Hari Kerja (Senin - Jumat) | 45.217 | 73,4% | 10,70 |
| Akhir Pekan (Sabtu - Minggu) | 16.366 | 26,6% | 10,21 |

Proporsi ini hampir persis mencerminkan rasio kalender (5 dari 7 hari = 71,4% hari kerja). Selisih rata-rata FRP hanya sebesar 4,5% yang secara praktis tidak signifikan. Hal ini menunjukkan bahwa pemicu kebakaran di Kalimantan didominasi oleh faktor musim dan kondisi kekeringan vegetasi daripada jadwal rutinitas mingguan manusia.

---

### Temuan 10: Distribusi Skor Bahaya Memvalidasi Arsitektur Tiga Pilar PRD

Hasil skor bahaya komposit (hazard_score: 40% FRP + 35% selisih suhu + 25% keyakinan deteksi):

| Rentang Skor | Jumlah Kejadian | Interpretasi Operasional |
|---|---|---|
| 0 - 25 (Rendah) | 36.948 (60,0%) | Pemantauan satelit rutin |
| 25 - 50 (Sedang) | 22.327 (36,3%) | Peningkatan patroli lapangan aktif |
| 50 - 75 (Tinggi) | 2.308 (3,7%) | Prioritas tanggap darurat dan pemadaman |
| Di atas 75 (Kritis) | 0 (0,0%) | Membutuhkan integrasi data kerentanan dan paparan |

Tidak ada satu pun titik panas yang melampaui skor 75 hanya dengan mengandalkan data fisik titik api (HAZARD). Hal ini sangat tepat dan selaras dengan rancangan sistem. Untuk mencapai skor tingkat kritis, sistem membutuhkan data PAPARAN (EXPOSURE - jarak ke pemukiman dan sekolah) serta KERENTANAN (VULNERABILITY - tutupan lahan gambut dan histori kejadian). Temuan ini membuktikan secara empiris bahwa platform terpadu FIRELINE mutlak diperlukan.

Relevansi Dokumen PRD: Fondasi empiris bagi mesin pendukung keputusan (Data Science Decision Support System).

---

## Indeks Visualisasi (27 Grafik Analitik)

### Pilar A: Analisis Temporal

| Nama File | Deskripsi Visualisasi |
|---|---|
| 01_daily_trend_with_ma7.png | Tren harian jumlah titik panas dengan garis rata-rata bergerak 7 hari dan anotasi puncak |
| 02_calendar_heatmap_dayofweek_month.png | Peta panas kalender hari dalam seminggu terhadap bulan deteksi |
| 03_monthly_stacked_by_confidence.png | Diagram batang bulanan berdasarkan tingkat keyakinan (Low, Nominal, High) |
| 04_frp_boxplot_per_month.png | Diagram kotak sebaran FRP per bulan dengan penandaan musim kemarau |
| 05_dual_axis_count_vs_total_frp.png | Grafik sumbu ganda: volume titik panas (batang) vs total energi radiasi FRP (garis) |
| 06_year_over_year_2024_vs_2025.png | Perbandingan tahun ke tahun (2024 vs 2025) per bulan kalender |

### Pilar B: Intensitas dan Karakteristik Fisik Api (HAZARD)

| Nama File | Deskripsi Visualisasi |
|---|---|
| 07_frp_distribution_log_scale.png | Histogram distribusi FRP dalam skala logaritmik beserta ambang batas ekstrem |
| 08_brightness_vs_bright_t31_overlay.png | Grafik overlay distribusi suhu kecerahan api vs suhu latar belakang tanah |
| 09_violin_frp_by_confidence.png | Diagram violin sebaran FRP berdasarkan kelas keyakinan deteksi sensor |
| 10_scatter_frp_vs_temp_delta.png | Sebaran FRP terhadap selisih suhu dengan ukuran titik mewakili luas piksel VIIRS |
| 11_day_vs_night_count_and_frp.png | Perbandingan jumlah dan rata-rata FRP antara deteksi siang hari dan malam hari |

### Pilar C: Distribusi Spasial

| Nama File | Deskripsi Visualisasi |
|---|---|
| 12_spatial_scatter_all_hotspots.png | Peta sebaran titik koordinat titik panas di Kalimantan dengan gradasi intensitas |
| 13_hexbin_density_map.png | Peta kepadatan heksagonal (hexbin) wilayah konsentrasi kebakaran |
| 14_kde_spatial_contour.png | Kontur estimasi densitas kernel (KDE) untuk identifikasi zona merah kebakaran |
| 15_bar_hotspots_by_province.png | Diagram batang perbandingan total titik panas dan total energi FRP per provinsi |

### Pilar D: Kejadian Kebakaran Ekstrem

| Nama File | Deskripsi Visualisasi |
|---|---|
| 16_frp_timeline_extreme_events.png | Lini masa nilai FRP seluruh titik panas dengan penandaan kejadian kebakaran masif |
| 17_top20_critical_days_total_frp.png | Peringkat 20 hari paling kritis berdasarkan akumulasi FRP kejadian di atas 50 MW |
| 18_cumulative_total_frp_over_time.png | Grafik akumulasi pelepasan total energi radiasi kebakaran sepanjang periode pengamatan |

### Pilar E: Kerentanan dan Rekurensi Kebakaran

| Nama File | Deskripsi Visualisasi |
|---|---|
| 19_top25_recurrence_chronic_fire_zones.png | Peringkat 25 sel grid dengan tingkat kejadian kebakaran berulang tertinggi |
| 20_heatmap_region_vs_season.png | Matriks risiko jumlah kejadian antara wilayah provinsi dengan musim |
| 21_weekday_vs_weekend_fire_activity.png | Perbandingan pola aktivitas kebakaran antara hari kerja dan akhir pekan |

### Pilar F: Analisis Komposit dan Korelasi

| Nama File | Deskripsi Visualisasi |
|---|---|
| 22_pearson_correlation_matrix.png | Peta panas matriks korelasi linier Pearson antar parameter numerik |
| 23_confidence_donut_and_frp_comparison.png | Diagram donat proporsi tingkat keyakinan dan perbandingan rata-rata vs median FRP |
| 24_intensity_class_composition_by_province.png | Komposisi 100% kelas intensitas kebakaran (Low, Medium, High, Extreme) per provinsi |

### Grafik Tambahan Hasil Rekayasa Fitur (Feature Engineering)

| Nama File | Deskripsi Visualisasi |
|---|---|
| FE01_raw_vs_weighted_frp_monthly.png | Perbandingan total FRP mentah vs FRP terbobot tingkat keyakinan per bulan |
| FE02_hazard_score_by_province.png | Diagram kotak sebaran nilai skor bahaya komposit (hazard_score) per provinsi |
| FE03_chronic_fire_zones_recurrence_map.png | Peta spasial zona kebakaran kronis berdasarkan frekuensi kejadian berulang |

---

## Ringkasan Rekayasa Fitur (Feature Engineering)

Data masukan awal: 11 kolom fungsional (setelah kolom konstan dihapus)  
Data keluaran akhir: 43 kolom (penambahan 32 fitur analitik terstruktur)  

| Kategori Fitur | Daftar Nama Kolom Fitur | Relevansi Sistem FIRELINE |
|---|---|---|
| Temporal (13 fitur) | year, month, month_name, day_of_month, day_name, is_weekend, hour, quarter, year_month, season, days_since_start, is_kemarau, time_period | Analisis deret waktu dan pemicu peringatan dini musiman |
| Karakteristik Bahaya Api / HAZARD (8 fitur) | temp_delta_K, brightness_celsius, bright_t31_celsius, pixel_area_km2, fire_intensity_class, is_extreme_fire, is_mega_fire, frp_log | Kuantifikasi intensitas dan energi destruktif api |
| Tingkat Keyakinan (3 fitur) | confidence_num, confidence_weight, weighted_frp | Penyesuaian reliabilitas sensor satelit pada perhitungan risiko |
| Spasial Regional (4 fitur) | kalimantan_region, lat_zone, coord_grid_1deg, coord_grid_05deg | Agregasi administratif dan pemetaan zona klaster |
| Kerentanan / Vulnerability (3 fitur) | fire_recurrence_count, cumulative_frp_at_grid, is_high_recurrence | Identifikasi zona kebakaran kronis berulang |
| Komposit Bahaya (1 fitur) | hazard_score (skala 0 hingga 100) | Komponen pertama dari Indeks Risiko Kontekstual |

---

## Inventaris Berkas Keluaran

| Berkas | Direktori Penyimpanan | Deskripsi Singkat |
|---|---|---|
| eda_report_summary.md | 01_data_exploration/ | Laporan ringkasan profil statistik data format markdown |
| fireline_hotspot_clean.csv | 03_preprocessing/ | Dataset bersih terstandarisasi (61.583 baris x 16 kolom) |
| feature_engineering_summary.txt | 04_feature_engineering/ | Dokumentasi teknis definisi fitur baru |
| fireline_hotspot_featured.csv | 04_feature_engineering/ | Dataset utama siap analisis dan pemodelan (61.583 baris x 43 kolom) |
| 27 berkas grafik PNG (300 DPI) | 02_visualizations/ | Seluruh visualisasi grafik siap publikasi |

---

## Langkah Analisis Selanjutnya

1. **Integrasi Data Iklim BMKG:** Data cuaca harian (suhu udara, kelembapan relatif, kecepatan angin, curah hujan) pada rentang waktu yang sama akan diintegrasikan untuk melengkapi faktor probabilitas penjalaran api.
2. **Integrasi Data Paparan Fasilitas Publik:** Penggabungan spasial dengan dataset fasilitas pendidikan dan pemukiman (complete_data.csv) untuk menghitung jarak terdekat serta populasi terdampak (dimensi EXPOSURE).
3. **Penyusunan Indeks Risiko Kontekstual Lengkap:** Penggabungan tiga pilar: BAHAYA (Hotspot & Cuaca) + PAPARAN (Pemukiman & Sekolah) + KERENTANAN (Lahan Gambut & Rekurensi) sebagai output inti sistem pendukung keputusan FIRELINE.
