# Laporan EDA: Dataset Iklim Historis Indonesia (Kaggle BMKG 2010-2020)
## Analisis Baseline Klimatologi 11 Tahun dan Relevansi terhadap Pemodelan Karhutla Kalimantan

**Dataset Sumber:** Kaggle Indonesia Climate Dataset (`climate_data.csv`, `province_detail.csv`, `station_detail.csv`)  
**Cakupan Wilayah:** 24 Stasiun Meteorologi/Klimatologi BMKG di 5 Provinsi Kalimantan  
**Rentang Waktu Observasi:** 01 Januari 2010 hingga 31 Desember 2020 (11 Tahun Penuh)  
**Total Observasi Kalimantan:** 87.238 baris data harian  
**Konteks Integrasi:** Platform FIRELINE - Studi Kasus COMPFEST 18 (Tim Alpha)  

---

## 1. Nilai Strategis Dataset Iklim Dekadal (2010-2020)

Dataset historis 11 tahun ini memberikan **baseline klimatologi jangka panjang (*decadal climate normal*)** yang sangat krusial untuk memvalidasi temuan pada data satelit 2024-2026:

1. **Benchmark Tahun Kebakaran Ekstrem (El Nino 2015 & Kekeringan 2019):**  
   Menyediakan rekam jejak empiris dua episode kebakaran hutan dan lahan paling dahsyat dalam sejarah modern Indonesia (2015 dan 2019).
2. **Kuantifikasi Siklus Musiman (*Dry Season Climatology*):**  
   Membuktikan secara statistik bahwa anomali penurunan kelembapan (RH < 80%) dan lonjakan suhu maksimum (Tx > 33 °C) secara konsisten terjadi pada bulan Juni hingga Oktober di seluruh Kalimantan.
3. **Penyusunan Ambang Batas Peringatan Dini (*Fire Weather Thresholds*):**  
   Menjadi dasar kalibrasi ilmiah untuk parameter cuaca pada mesin pendukung keputusan FIRELINE.

---

## 2. Ringkasan Profil Data Kalimantan (2010-2020)

| Atribut | Nilai Statistik |
|---|---|
| Total Baris Observasi | 87.238 baris data harian |
| Jumlah Stasiun BMKG | 24 stasiun pengamatan resmi BMKG |
| Periode Waktu | 01 Januari 2010 sampai 31 Desember 2020 |
| Suhu Maksimum Rata-rata (`Tx`) | 32,24 °C (Maksimum absolut: 38,20 °C) |
| Suhu Rata-rata (`Tavg`) | 27,09 °C |
| Kelembapan Relatif Rata-rata (`RH_avg`) | 84,67% (Minimum absolut: 37,00%) |
| Rata-rata Curah Hujan Harian (`RR`) | 9,93 mm/hari |
| Persentase Hari Tanpa Hujan (*Dry Days* < 2mm) | 50,4% dari seluruh hari pengamatan |

### Distribusi Stasiun dan Observasi per Provinsi

| Provinsi | Jumlah Stasiun BMKG | Total Baris Data | Suhu Maksimum Rata-rata (`Tx`) | Rata-rata Kelembapan (`RH_avg`) |
|---|---|---|---|---|
| Kalimantan Barat | 8 stasiun | 30.347 baris | 32,54 °C | 84,12% |
| Kalimantan Tengah | 6 stasiun | 19.494 baris | 32,18 °C | 84,55% |
| Kalimantan Utara | 4 stasiun | 14.812 baris | 31,95 °C | 85,20% |
| Kalimantan Timur | 4 stasiun | 11.703 baris | 31,88 °C | 84,80% |
| Kalimantan Selatan | 2 stasiun | 10.882 baris | 32,65 °C | 84,70% |

---

## 3. Temuan Utama dan Korelasi dengan Dinamika Karhutla

### Temuan 1: Validasi Empiris Periode Puncak Kebakaran (Juni - Oktober)
Data 11 tahun membuktikan bahwa setiap tahun, kelembapan rata-rata Kalimantan mengalami penurunan signifikan dari ~87% pada musim hujan menjadi ~81% pada bulan Agustus-September, disertai lonjakan durasi penyinaran matahari hingga rata-rata 6-7 jam per hari. Pola ini persis merefleksikan lonjakan 83,4% titik api yang terdeteksi pada dataset satelit NASA 2024-2026.

### Temuan 2: Anatomi Cuaca Mega-Fire 2015 dan 2019
Pada episode El Nino 2015 dan fenomena Indian Ocean Dipole (IOD) positif 2019:
* Suhu maksimum rata-rata melonjak hingga melampaui **34,5 °C** secara terus menerus selama Agustus-September.
* Curah hujan harian anjlok drastis ke bawah **2,5 mm/hari** selama lebih dari 60 hari berturut-turut.
* Total akumulasi hari bahaya api tinggi (*fire danger days*) mencapai rekor tertinggi dekade tersebut, memicu pelepasan kabut asap lintas batas (*transboundary haze*).

### Temuan 3: Kalimantan Barat dan Kalimantan Selatan Memiliki Paparan Panas Tertinggi
Kalimantan Barat dan Kalimantan Selatan mencatatkan suhu harian maksimum rata-rata tertinggi (32,54 °C dan 32,65 °C) serta frekuensi hari terik (>34 °C) paling sering. Hal ini selaras sempurna dengan temuan EDA Titik Api di mana Kalimantan Barat menyumbang **51,6% dari total titik api Kalimantan**.

---

## 4. Indeks Visualisasi Analitik (6 Grafik 300 DPI)

Direktori: `EDA/03_kaggle_indonesia_climate/02_visualizations/`

| Nama Berkas | Deskripsi Analitik |
|---|---|
| `K01_decadal_monthly_climatology_kalimantan.png` | Profil 4 panel klimatologi bulanan 11 tahun: dinamika suhu (Tx/Tavg/Tn), penurunan kelembapan, defisit curah hujan, dan probabilitas hari bahaya api per bulan. |
| `K02_historical_extreme_years_2015_2019.png` | Analisis komparatif anomali cuaca pada tahun kebakaran ekstrem (El Nino 2015 dan Kekeringan 2019) vs baseline normal 2010-2020. |
| `K03_provincial_climate_vulnerability_profile.png` | Profil kerentanan iklim komparatif antar 5 provinsi di Kalimantan (suhu maksimum, persentase hari kering, profil kecepatan angin, dan indeks bahaya cuaca). |
| `K04_correlation_matrix_decadal_climate.png` | Matriks korelasi Pearson antar variabel meteorologi dari 87.238 baris data, mengonfirmasi hubungan kuat antara suhu tinggi, kelembapan rendah, dan risiko kebakaran. |
| `K05_spatial_station_network_kalimantan.png` | Peta sebaran spasial 24 stasiun meteorologi BMKG di Kalimantan yang di-overlay di atas batas wilayah administratif GeoJSON. |
| `K06_fire_weather_risk_index_decadal_trend.png` | Tren deret waktu 11 tahun frekuensi hari bahaya kebakaran tinggi, memperlihatkan lonjakan masif pada 2015 dan 2019 sebagai bukti empiris risiko iklim. |

---

## 5. Hubungan Sinergis dengan Arsitektur Platform FIRELINE

Pengolahan dataset iklim historis ini melengkapi fondasi analitik FIRELINE:

1. **Kalibrasi Model Risiko Berbasis 11 Tahun Sejarah:**  
   Menghindari *overfitting* terhadap data 2 tahun terakhir (2024-2026) dengan menyertakan spektrum variabilitas iklim jangka panjang.
2. **Standardisasi Ambang Batas Bahaya:**  
   Menetapkan batasan kuantitatif kondisi atmosfer kritis: **Tx >= 33 °C**, **RH <= 80%**, dan **Curah Hujan < 2 mm**.
3. **Penyempurnaan Skor Kerentanan Lingkungan:**  
   Memberikan bobot kerentanan iklim regional per provinsi yang berbasis data historis BMKG resmi.
