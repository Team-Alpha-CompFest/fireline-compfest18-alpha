# Laporan EDA: Data Cuaca dan Iklim Kalimantan (BMKG / ERA5)
## Analisis Parameter Meteorologi dan Korelasi dengan Kebakaran Hutan | Agustus 2024 - Mei 2026

Dataset: bmkg_kalimantan_weather_2024_2026.csv  
Tanggal Pemrosesan: 29 Agustus 2026  
Konteks: Platform FIRELINE - Studi Kasus COMPFEST 18 (Tim Alpha)  

---

## Ringkasan Dataset

| Atribut | Nilai |
|---|---|
| Total Baris Data | 9.366 observasi harian |
| Jumlah Stasiun Pengamatan | 14 stasiun cuaca (mencakup 5 provinsi di Kalimantan) |
| Rentang Waktu | 01 Agustus 2024 hingga 31 Mei 2026 (669 hari kalender) |
| Sumber Data | Data Terbuka Meteorologi / Reanalisis Global ERA5 ECMWF |
| Nilai Kosong (Missing Values) | 0 baris (100% lengkap) |
| Parameter Kunci | Suhu, Curah Hujan, Kelembapan, Angin, VPD, Evapotranspirasi, Radiasi Matahari |

---

## Distribusi Stasiun Pengamatan Cuaca

Sebanyak 14 stasiun cuaca dipilih secara strategis di kota-kota utama dan zona rawan karhutla di 5 provinsi Kalimantan:

| Provinsi | Kota / Stasiun | Lintang (Lat) | Bujur (Lon) | Hari Pengamatan |
|---|---|---|---|---|
| Kalimantan Barat | Pontianak | -0.0263 | 109.3425 | 669 hari |
| Kalimantan Barat | Singkawang | 0.9023 | 108.9861 | 669 hari |
| Kalimantan Barat | Ketapang | -1.8432 | 109.9740 | 669 hari |
| Kalimantan Barat | Sintang | 0.0639 | 111.4732 | 669 hari |
| Kalimantan Tengah | Palangkaraya | -2.2135 | 113.9108 | 669 hari |
| Kalimantan Tengah | Sampit | -2.5350 | 112.9501 | 669 hari |
| Kalimantan Tengah | Pangkalan Bun | -2.6994 | 111.6238 | 669 hari |
| Kalimantan Timur | Balikpapan | -1.2379 | 116.8529 | 669 hari |
| Kalimantan Timur | Samarinda | -0.4948 | 117.1436 | 669 hari |
| Kalimantan Timur | Berau | 2.1668 | 117.4817 | 669 hari |
| Kalimantan Selatan | Banjarmasin | -3.3194 | 114.5897 | 669 hari |
| Kalimantan Selatan | Banjarbaru | -3.4478 | 114.8240 | 669 hari |
| Kalimantan Utara | Tarakan | 3.3002 | 117.5765 | 669 hari |
| Kalimantan Utara | Tanjung Selor | 2.8380 | 117.3735 | 669 hari |

---

## Temuan Utama Korelasi Cuaca vs Titik Panas (Hotspot)

Berdasarkan penggabungan data agregat harian cuaca dan deteksi titik panas satelit NASA VIIRS:

| Variabel Meteorologi | Korelasi Pearson vs Jumlah Titik Panas | Korelasi Pearson vs Total Energi Api (FRP) | Dampak Fisik terhadap Karhutla |
|---|---|---|---|
| Kelembapan Relatif Rata-rata (`humidity_mean`) | -0,482 | -0,433 | Udara kering memicu pengeringan cepat biomassa daun dan serasah gambut. |
| Defisit Tekanan Uap Maksimum (`vpd_max`) | +0,470 | +0,420 | Daya hisap kekeringan atmosfer; makin tinggi VPD, makin mudah api menyala. |
| Suhu Udara Maksimum (`temp_max`) | +0,382 | +0,339 | Suhu tinggi memanaskan bahan bakar vegetasi hingga mendekati titik sulut api. |
| Akumulasi Curah Hujan (`precip`) | -0,361 | -0,323 | Hujan berfungsi sebagai agen pemadam alami dan pembasah permukaan gambut. |
| Durasi Penyinaran Matahari (`sunshine_h`) | +0,318 | +0,280 | Paparan surya mempercepat proses evapotranspirasi air dari lapisan tanah atas. |
| Kecepatan Angin Maksimum (`wind_max`) | +0,218 | +0,211 | Suplai oksigen konstan dan pendorong laju penjalaran api (fire spread rate). |

---

### Analisis Mendalam Temuan Kunci

#### 1. Kelembapan Udara dan VPD Merupakan Indikator Paling Kritis
Variabel kelembapan udara (`humidity_mean` r = -0,482) dan defisit tekanan uap (`vpd_max` r = +0,470) memiliki korelasi linear paling kuat terhadap lonjakan kebakaran. Ketika kelembapan udara harian anjlok di bawah 65% dan VPD melampaui 1,8 kPa, risiko kemunculan titik api meningkat drastis.

#### 2. Dinamika Musim Kemarau (Juni hingga Oktober)
* Pada musim kemarau, rata-rata curah hujan harian turun menjadi 7,83 mm (dibandingkan 10,53 mm pada musim hujan).
* Suhu maksimum mencapai puncaknya di 37,0 °C dengan nilai VPD maksimum mencapai 3,84 kPa.
* Kondisi ini menjelaskan mengapa 83,4% titik api karhutla Kalimantan terkonsentrasi pada periode musim kemarau.

#### 3. Kecepatan Angin Memperparah Pelepasan Energi Destruktif Api
Meskipun korelasi kecepatan angin terhadap frekuensi titik api adalah moderat (+0,218), korelasi terhadap intensitas pelepasan daya api (`total_frp` r = +0,211) menegaskan bahwa angin kencang (di atas 20 km/jam) mengubah titik api kecil menjadi kebakaran hebat (*high-intensity crown fires*).

---

## Indeks Visualisasi Cuaca (6 Grafik Analitik)

Direktori: `EDA/02_bmkg_weather_kalimantan/visualizations/`

| Nama Berkas | Deskripsi Analitik |
|---|---|
| `W01_monthly_weather_overview.png` | Gambaran umum deret waktu bulanan untuk suhu udara (rata-rata dan maksimum), akumulasi curah hujan, serta kelembapan dan kecepatan angin dengan penandaan jendela musim kemarau. |
| `W02_weather_vs_hotspot_count.png` | Grafik sumbu ganda 4 panel yang mengkorelasikan volume titik panas bulanan dengan suhu maksimum, curah hujan, kelembapan, dan VPD. |
| `W03_correlation_heatmap_weather_fire.png` | Peta panas matriks korelasi Pearson lengkap antara 9 variabel cuaca terhadap metrik kebakaran (jumlah hotspot, total FRP, dan rata-rata FRP). |
| `W04_province_weather_vs_fire_drySeason.png` | Diagram sebaran gelembung tingkat provinsi selama musim kemarau: hubungan antara parameter kekeringan udara vs volume kebakaran (ukuran gelembung mewakili total FRP). |
| `W05_rolling14d_weather_fire_timeseries.png` | Analisis tren deret waktu bergerak 14 hari (*14-day rolling average*) yang memperlihatkan bagaimana penurunan kelembapan dan curah hujan mendahului lonjakan masif titik api. |
| `W06_dry_vs_wet_season_weather.png` | Diagram kotak (*boxplot*) perbandingan distribusi 6 variabel meteorologi utama antara musim kemarau dan musim hujan. |

---

## Integrasi dengan Platform FIRELINE

Hasil analisis data cuaca ini akan diintegrasikan ke dalam arsitektur sistem pendukung keputusan FIRELINE:

1. **Fire Weather Danger Index (FWDI):**  
   Penggabungan parameter cuaca harian (`temp_max`, `humidity_min`, `vpd_max`, `wind_max`, `precip`) untuk membentuk skor probabilitas penjalaran api.
2. **Penyempurnaan Dimensi Bahaya (HAZARD):**  
   Skor bahaya fisik api satelit (`hazard_score`) akan dikalikan dengan faktor lingkungan cuaca, menghasilkan prediksi bahaya real-time yang adaptif terhadap dinamika atmosfer.
3. **Pemicu Sistem Peringatan Dini Proaktif:**  
   Ketika tren moving average 14 hari mendeteksi akumulasi defisit curah hujan dan kenaikan VPD, sistem FIRELINE secara otomatis menaikkan status siaga wilayah sebelum titik api pertama terdeteksi oleh satelit.
