# FIRELINE Master EDA Findings Review

**Author:** Rizki Ilham Putra Pratama  
**Date:** 2026-09-04  
**Purpose:** Konsolidasi dan review seluruh temuan EDA dari 3 anggota DS. Dokumen ini membedakan **Finding** (fakta dari data), **Hypothesis** (interpretasi yang perlu validasi), **Limitation** (batasan data/metode), dan **Actionable Insight** (rekomendasi konkret).

---

## Table of Contents

1. [NASA FIRMS Hotspot](#1-nasa-firms-hotspot)
2. [BMKG Weather / Current Climate](#2-bmkg-weather--current-climate)
3. [Historical Climate Baseline (2010–2020)](#3-historical-climate-baseline-20102020)
4. [Peatland & Soil Moisture](#4-peatland--soil-moisture)
5. [School & Population Exposure](#5-school--population-exposure)
6. [Pontianak Weather (Local)](#6-pontianak-weather-local)
7. [Cross-Dataset Findings](#7-cross-dataset-findings)
8. [Contradictions & Discrepancies](#8-contradictions--discrepancies)
9. [Summary: Dashboard & CRPI Implications](#9-summary-dashboard--crpi-implications)

---

## 1. NASA FIRMS Hotspot

**Sources:** EDA/01 README, Grace report, DS_MASTER_FINDINGS, temuan-analisis-data-awal

### Findings (Fakta Empiris)

| # | Finding | Evidence | Confidence |
|---|---|---|---|
| F1.1 | **61,583 hotspot detections** dalam 22 bulan (Aug 2024 – May 2026) di Kalimantan | Raw file row count, verified no duplicates on `(lat, lon, acq_date, acq_time)` | High |
| F1.2 | **Kalimantan Barat mendominasi** dengan 51.6% total hotspot (31,764 detections) dan total FRP tertinggi (367,757 MW) | Province aggregation dari EDA hotspot | High |
| F1.3 | **Musim kemarau (Jun–Oct) = 83.4%** dari seluruh deteksi, intensitas rata-rata 55.6% lebih tinggi vs musim hujan | Monthly breakdown, FRP comparison | High |
| F1.4 | **FRP sangat right-skewed**: median 6.14 MW, mean 10.57 MW, max 954.79 MW; ratio median:max = 1:155 | Statistical summary dari 61,583 rows | High |
| F1.5 | **Disparitas musiman 136x**: Sep 2024 = 16,911 deteksi vs Jan 2025 = 124 deteksi | Monthly count comparison | High |
| F1.6 | **Confidence distribution**: 93.1% Nominal, 3.8% High, 3.2% Low | Direct count from raw data | High |
| F1.7 | **89.3% deteksi terjadi siang hari** (daytime overpass); hanya 10.7% malam | `daynight` field distribution | High |
| F1.8 | **4 dari 5 mega-fire events (FRP > 500 MW) berlabel confidence Low** | Top-5 FRP events crossreferenced with confidence | High |
| F1.9 | **~4% deteksi menyentuh batas saturasi sensor** (brightness = 367K) | Brightness distribution analysis, confirmed by NASA VIIRS documentation | High |
| F1.10 | **Tidak ada perbedaan signifikan hari kerja vs akhir pekan** (proporsi ~71.4% vs 28.6% sesuai rasio kalender) | Day-of-week breakdown | High |
| F1.11 | **99.9% hotspot berada dalam grid cells dengan rekurensi tinggi** (224 cells terbakar ≥5x dalam 22 bulan) | Grid recurrence analysis resolusi 0.5° | Medium — grid resolution mempengaruhi angka |
| F1.12 | **Korelasi FRP vs temp_delta_K = 0.52** (moderat) — sinyal independen | Pearson correlation matrix | High |

### Hypotheses (Perlu Validasi)

| # | Hypothesis | Basis | Validation Needed |
|---|---|---|---|
| H1.1 | Grid recurrence mengindikasikan pola pembukaan lahan berulang atau drainase gambut | Spatial concentration pattern | Ground-truth land use verification |
| H1.2 | Deteksi malam hari yang lebih sedikit menciptakan blind spot > 12 jam untuk kebakaran nokturnal | Overpass timing pattern | Cross-reference dengan sensor lain (MODIS, geostationary) |
| H1.3 | Confidence Low pada mega-fire disebabkan saturasi sensor atau gangguan asap, bukan api kecil | Mega-fire event analysis | Verify dengan NASA product guide, Schroeder et al. 2014 |
| H1.4 | Pola musiman sepenuhnya driven by kekeringan vegetasi, bukan aktivitas manusia mingguan | Weekday/weekend non-difference | Perlu spatial correlation dengan land use data |

### Limitations

| # | Limitation | Impact |
|---|---|---|
| L1.1 | **Deteksi ≠ kejadian/insiden di lapangan**. Satu deteksi bisa jadi bagian dari kebakaran yang sama | Overcount events jika digunakan tanpa grouping |
| L1.2 | **Tidak ada label administratif** di raw data. Province assignment via EDA menggunakan rule-based longitude boundaries, bukan point-in-polygon resmi | Province counts bisa salah di perbatasan |
| L1.3 | **Saturasi sensor** pada brightness 367K berarti intensitas sebenarnya bisa lebih tinggi dari tercatat | Underestimate severity pada kasus terpanas |
| L1.4 | **Temporal scope parsial** — hanya 22 bulan, bukan multi-year cycle lengkap | Seasonal patterns belum cover inter-annual variability (El Niño, IOD) |
| L1.5 | **Grid recurrence dihitung full-period** — berpotensi leakage jika digunakan untuk prediction | Harus recompute dengan rolling window |

---

## 2. BMKG Weather / Current Climate

**Sources:** EDA/02 README, weather_eda_summary, DS_MASTER_FINDINGS

### Findings

| # | Finding | Evidence | Confidence |
|---|---|---|---|
| F2.1 | **9,366 observasi** dari 14 stasiun di 5 provinsi, 669 hari (Aug 2024 – May 2026) | File inspection, 0 missing values | High |
| F2.2 | **Kelembapan rata-rata berkorelasi negatif terkuat** dengan hotspot count (r = -0.482) | Pearson correlation at aggregated daily level | Medium — ecological aggregation |
| F2.3 | **VPD max berkorelasi positif** (r = +0.470) dengan hotspot count | Same aggregated analysis | Medium |
| F2.4 | **Curah hujan harian turun 26%** di musim kemarau (7.83 mm vs 10.53 mm musim hujan) | Seasonal descriptive statistics | High |
| F2.5 | **VPD max mencapai 3.84 kPa** di musim kemarau (vs max 3.89 kPa musim hujan — surprisingly close) | Descriptive statistics | High |
| F2.6 | **Kecepatan angin berkorelasi moderat** (r = +0.218) dengan hotspot count, namun memperparah intensitas | Correlation analysis | Medium |

### Hypotheses

| # | Hypothesis | Basis | Validation Needed |
|---|---|---|---|
| H2.1 | Penurunan kelembapan dan curah hujan **mendahului** lonjakan hotspot dengan lag 1–2 minggu | 14-day rolling average visual trend | Formal Granger causality test atau lag correlation analysis |
| H2.2 | Threshold RH < 65% dan VPD > 1.8 kPa bisa menjadi early warning trigger | Visual threshold analysis | Statistical breakpoint analysis dengan confidence intervals |
| H2.3 | Kecepatan angin > 20 km/jam mengubah fire behavior dari surface ke crown fire | Physical reasoning + moderate correlation | Requires fire behavior modeling, bukan hanya correlation |

### Limitations

| # | Limitation | Impact |
|---|---|---|
| L2.1 | **Hanya 14 stasiun** untuk ~540,000 km² — 1 stasiun per ~38,500 km² | Weather assignment ke hotspot jauh dari stasiun sangat approximate |
| L2.2 | **Korelasi dihitung pada aggregated daily level** (sum hotspot vs mean weather) — ecological fallacy risk | Individual hotspot-level weather relationship bisa berbeda |
| L2.3 | **Source data = ERA5 reanalysis**, bukan murni observasi stasiun BMKG | "BMKG weather" misnomer; accuracy depends on reanalysis resolution |
| L2.4 | `high_fire_danger` dan `is_dry_day` adalah **derived flags dari EDA**, bukan standard meteorologi resmi | Jangan gunakan sebagai threshold resmi tanpa validasi |

---

## 3. Historical Climate Baseline (2010–2020)

**Sources:** EDA/03 README, DS_MASTER_FINDINGS

### Findings

| # | Finding | Evidence | Confidence |
|---|---|---|---|
| F3.1 | **87,238 observasi harian** dari 24 stasiun BMKG di Kalimantan, 11 tahun penuh | Cleaned dataset | High |
| F3.2 | **50.4% hari tanpa hujan** (< 2mm) sepanjang dekade | Descriptive statistics | High |
| F3.3 | **2015 dan 2019** merupakan tahun kebakaran ekstrem: suhu max > 34.5°C terus-menerus, curah hujan < 2.5mm/hari selama > 60 hari berturut | Year-specific analysis | High |
| F3.4 | **Pola musiman konsisten** sepanjang 11 tahun: RH turun dari ~87% (wet) ke ~81% (Aug–Sep) | Monthly climatology | High |
| F3.5 | **Kalimantan Barat dan Selatan** memiliki suhu harian max rata-rata tertinggi (32.54°C dan 32.65°C) | Provincial comparison | High |

### Hypotheses

| # | Hypothesis | Basis | Validation Needed |
|---|---|---|---|
| H3.1 | Threshold Tx ≥ 33°C, RH ≤ 80%, curah hujan < 2mm bisa menjadi fire-weather threshold berbasis dekade | Percentile-based analysis dari 11 tahun | Backtest against known fire events (2015, 2019) |
| H3.2 | 2024 fire season intensity (puncak Sep 2024) sebanding dengan 2015/2019 | Year-over-year comparison | Requires overlapping satellite data di 2015/2019 (different sensor) |

### Limitations

| # | Limitation | Impact |
|---|---|---|
| L3.1 | **Tidak ada overlap temporal** dengan data hotspot (2010–2020 vs 2024–2026) | Direct date join impossible; baseline comparison only |
| L3.2 | **Date format DD-MM-YYYY** di source — perlu konversi | Pipeline risk jika tidak dihandle |
| L3.3 | **24 stasiun vs 14 stasiun** — network tidak identik dengan current weather | Station-level comparison memerlukan spatial matching |
| L3.4 | **Fire danger days** adalah rule-based output EDA, bukan validated index | Jangan treat sebagai ground truth fire occurrence |

---

## 4. Peatland & Soil Moisture

**Sources:** DATA_CATALOG, DS_MASTER_FINDINGS, GeoJSON schema inspection

### Findings

| # | Finding | Evidence | Confidence |
|---|---|---|---|
| F4.1 | **Dua produk peatland** dengan schema berbeda: 25-feature KHG-oriented vs 146-feature landform-oriented | GeoJSON inspection | High |
| F4.2 | **Soil moisture tersedia** pada 3 kedalaman (0–7cm, 7–28cm, 28–100cm) untuk 14 stasiun × 669 hari | CSV schema inspection | High |
| F4.3 | **Peat-enriched hotspot output** memiliki 61,732 rows vs raw 61,583 — **149 rows discrepancy** | Row count comparison | High — requires audit |
| F4.4 | IAM spatial join menghasilkan kategori **"outside mapped area"** untuk sebagian hotspot | Derived file inspection | High |
| F4.5 | `peat_hazard_multiplier` field exists di featured file tapi **formula/derivation undocumented** | Schema review | High |

### Hypotheses

| # | Hypothesis | Basis | Validation Needed |
|---|---|---|---|
| H4.1 | Peatland hotspots lebih likely menjadi persistent/underground fires | Domain knowledge | Cross-reference FRP duration dan recurrence di peatland vs non-peatland zones |
| H4.2 | Soil moisture di kedalaman 0–7cm paling predictive untuk ignition | Physical reasoning | Correlation analysis hotspot occurrence vs soil moisture layers |

### Limitations

| # | Limitation | Impact |
|---|---|---|
| L4.1 | **Belum ada keputusan produk peatland mana yang authoritative** | Spatial join results bisa berbeda signifikan |
| L4.2 | **Soil moisture source/provenance tidak sepenuhnya documented** | Representativeness untuk peatland areas unclear |
| L4.3 | **Row count mismatch 61,732 vs 61,583** — enrichment pipeline mungkin duplicate atau add rows | Featured file tidak reliable sebagai source of truth |
| L4.4 | **"Peat" representativeness** dari 14 stasiun point measurements ke seluruh lahan gambut questionable | Spatial interpolation error |

---

## 5. School & Population Exposure

**Sources:** temuan-analisis-data-awal, DS_MASTER_FINDINGS, DATA_CATALOG

### Findings

| # | Finding | Evidence | Confidence |
|---|---|---|---|
| F5.1 | **17,548 sekolah di Kalimantan** setelah filtering dan cleaning (dari 215,285 nasional) | Cleaned export row count | High |
| F5.2 | **~99% sekolah memiliki koordinat valid** | `has_valid_coord` field distribution | High |
| F5.3 | **SD mendominasi** jumlah fasilitas (140,000+ nasional) — kelompok usia paling rentan terhadap ISPA | Stage distribution analysis | High |
| F5.4 | **Data populasi 2022** (dari BPS di school dataset) lebih baru dari populasi provinsi 2010 | Source year comparison | High |
| F5.5 | **SLB (sekolah berkebutuhan khusus) jumlahnya sangat kecil** tapi memerlukan evakuasi lebih kompleks | Count by stage | High |
| F5.6 | **Populasi tersedia di level provinsi**, bukan kecamatan/desa | Field granularity check | High |

### Hypotheses

| # | Hypothesis | Basis | Validation Needed |
|---|---|---|---|
| H5.1 | Hotspot dekat sekolah (< 5km) merupakan prioritas dispatch paling tinggi | Problem description alignment | User research dengan BPBD/Manggala Agni |
| H5.2 | Jumlah sekolah dalam radius bisa menjadi proxy exposure yang workable meski bukan sempurna | Geographic proximity assumption | Validate apakah sekolah = proxy populasi terdampak di konteks rural Kalimantan |

### Limitations

| # | Limitation | Impact |
|---|---|---|
| L5.1 | **Sekolah ≠ semua permukiman** — fasilitas kesehatan, desa, infrastruktur vital tidak tercakup | Exposure metric undercount |
| L5.2 | **Populasi hanya level provinsi** — tidak bisa menjawab "desa mana paling berisiko" | Granularity terlalu kasar untuk precision dispatch |
| L5.3 | **Data vintage 2022** — sekolah bisa tutup/buka, populasi berubah | Temporal mismatch dengan hotspot 2024–2026 |
| L5.4 | **Buffer distance belum disetujui** (5/10/25 km proposal) | Hasil exposure count sangat sensitif terhadap threshold |

---

## 6. Pontianak Weather (Local)

**Sources:** DS_MASTER_FINDINGS, DATA_CATALOG

### Findings

| # | Finding | Evidence | Confidence |
|---|---|---|---|
| F6.1 | **1,460 unique days** setelah cleaning (1,734 raw rows, 274 duplicates) | Cleaning pipeline output | High |
| F6.2 | **Rainfall (RR) substantial missingness** | Field completeness check | High |
| F6.3 | Periode 2021–2024, hanya overlap 5 bulan dengan hotspot data (Aug–Dec 2024) | Date range comparison | High |

### Limitations

| # | Limitation | Impact |
|---|---|---|
| L6.1 | **Single station** — tidak representatif untuk seluruh Kalimantan | Tidak boleh digunakan sebagai regional weather |
| L6.2 | **Duplicate handling** menggunakan "first observation" tanpa clear provenance | Reproducibility concern |

### Actionable Decision

> **Role:** Pontianak weather = **local validation / prototype only**. Tidak dimasukkan dalam integrated analytical dataset. Didokumentasikan sebagai referensi.

---

## 7. Cross-Dataset Findings

### 7.1 Convergent Patterns (Dikonfirmasi oleh Multiple Sources)

| Pattern | Supporting Evidence | Strength |
|---|---|---|
| **Musim kemarau (Jun–Oct) = peak fire period** | Hotspot 83.4%, weather seasonality, historical 11-year baseline, semua konsisten | Very Strong |
| **Kalimantan Barat = highest fire concentration** | Hotspot 51.6% count, weather highest temp exposure, historical climate alignment | Strong |
| **Humidity & VPD = strongest weather predictors** | Current weather r = ±0.47–0.48, historical baseline seasonal dip consistent | Moderate-Strong |
| **Skewed FRP distribution** | Multiple EDA analyses report same pattern; median:max ratio 1:155 | Strong |

### 7.2 Divergent or Unresolved Patterns

| Issue | Datasets Involved | Resolution Needed |
|---|---|---|
| **Row count mismatch** 61,583 vs 61,732 | Raw hotspot vs peat-featured derived | Audit enrichment pipeline for duplication |
| **Province label method** | Rule-based (longitude) vs point-in-polygon (admin boundary) | Use point-in-polygon with versioned boundary |
| **Two competing peatland products** | 25-feature vs 146-feature GeoJSON | Select authoritative product or document when each applies |
| **Population source conflict** | 2010 province census vs 2022 BPS school data | Use 2022 BPS; archive 2010 as historical reference |
| **Station count gap** | Current weather = 14 stations, historical = 24 stations | Different network; spatial comparison requires matching |
| **Facility count minor discrepancy** | BMKG summary says 17,448 vs cleaned file 17,548 | Source/version audit needed |

---

## 8. Contradictions & Discrepancies

| # | Discrepancy | Detail | Severity | Recommendation |
|---|---|---|---|---|
| D1 | **Hotspot row count mismatch** | `fireline_hotspot_peat_featured` has 61,732 rows, all other hotspot tables have 61,583 | High | Do not use featured file as base table. Audit for duplicate/added rows |
| D2 | **Competing thermal narratives** | Different EDA reports use different brightness thresholds and saturation interpretations | Medium | Standardize based on NASA VIIRS Collection 2 product guide |
| D3 | **Population vintages** | 2010 census file exists alongside 2022 BPS data in school dataset | High | Resolved: use 2022 BPS. Archive 2010 |
| D4 | **Hazard score formula** | EDA featured file has `hazard_score` with 40% FRP + 35% temp_delta + 25% confidence weights — **not approved for production** | High | Treat as EDA experiment. New CRPI formula requires team approval |
| D5 | **Province assignment methods** | Grace EDA uses rule-based (Kalbar = 109–111.5°E), BMKG branch uses coordinate metadata | Medium | Replace both with point-in-polygon spatial join per Integration Contract |
| D6 | **Peatland spatial products** | Different provenance, schema, feature counts (25 vs 146) | High | Habib auditing; decision pending |
| D7 | **Weather source label** | Data labeled "BMKG" but actually ERA5 reanalysis from Open-Meteo | Medium | Correct labeling in documentation; acknowledge reanalysis nature |
| D8 | **Facility count** | 17,448 in BMKG summary vs 17,548 in cleaned file | Low | Verify which is correct, likely minor version difference |

---

## 9. Summary: Dashboard & CRPI Implications

### 9.1 What We Can Confidently Show in Dashboard

| Dashboard Element | Data Support | Caveats |
|---|---|---|
| **Hotspot map** (location, FRP, confidence) | Strong — 61,583 verified detections | Detection ≠ incident; needs disclaimer |
| **Temporal trend** (daily/monthly hotspot count & FRP) | Strong — 22 months daily data | Only 2 fire seasons |
| **Province breakdown** (count, FRP by province) | Moderate — requires proper PiP admin join | Don't use longitude-based rule |
| **Weather correlation** (humidity, VPD, temp vs hotspot) | Moderate — at aggregated level | Ecological aggregation caveat |
| **Seasonal pattern** | Very Strong — confirmed by 11-year baseline | Definition (Jun–Oct) is convention |
| **School exposure count** (per province or per hotspot radius) | Moderate — 17,548 schools with coords | Static 2022 vintage, buffer distance TBD |
| **Peatland overlay** | Low-Moderate — pending product selection | Two competing sources |

### 9.2 What We Cannot Yet Show

| Element | Blocker |
|---|---|
| **CRPI / risk score** | Formula not approved; existing `hazard_score` is EDA experiment |
| **Urgency tier** | Depends on CRPI |
| **Citizen reports** | No data/schema exists |
| **Event-level view** (grouped fire events) | Event grouping algorithm not defined |
| **Village/district-level exposure** | Population only at province level |
| **Real-time operational status** | No dispatch/verification data |
| **Predictive fire forecast** | No model trained yet |

### 9.3 Top 5 Actionable Insights for SE Team

| # | Insight | Action | Priority |
|---|---|---|---|
| 1 | **Hotspot data sudah siap untuk visualisasi** — 61,583 rows, clean, no duplicates, no missing values | SE bisa mulai build map layer dan temporal charts dengan data existing | High |
| 2 | **Weather join menggunakan nearest-station** approach — hasilnya approximate, bukan precise per-hotspot | Dashboard harus menampilkan `station_distance_km` dan disclaimer cakupan | High |
| 3 | **Musim kemarau = core operational window** — 83.4% aktivitas Jun–Oct | Dashboard default filter bisa set ke current dry season; alert escalation logic berbasis kalender | Medium |
| 4 | **FRP right-skewed** — median 6.14 MW, max 954.79 MW | Visualisasi harus menggunakan log scale atau percentile-based coloring, bukan linear scale | Medium |
| 5 | **Tidak ada citizen report data** — feedback loop yang ada di PRD belum bisa diimplementasikan secara data-driven | SE perlu define schema citizen report bersama DS dan UXA sebelum build fitur pelaporan | High |

---

## Appendix A: File Reference Map

| EDA Source | Key Report File | Dataset Used |
|---|---|---|
| Grace (NASA, Pontianak, Portugal) | `documents/temuan-analisis-data-awal-fireline.md` | Data 1, 3, 4 |
| BMKG branch (Hotspot EDA) | `EDA/01_fireline_hotspot_kalimantan/README.md` | Data 1 |
| BMKG branch (Weather) | `EDA/02_bmkg_weather_kalimantan/README.md` | Data 2 |
| BMKG branch (Historical) | `EDA/03_kaggle_indonesia_climate/README.md` | Data 5 |
| IAM branch (Peatland, School) | `notebooks/scraping_gambut_BIG.ipynb`, `notebooks/data4/` | Data 4, 6 |
| Consolidated | `reports/findings/DS_MASTER_FINDINGS.md` | All |
| Alignment | `docs/DATA_ALIGNMENT_REPORT.md`, `docs/DATA_ALIGNMENT_ISSUES.md` | All |

## Appendix B: Key Numeric Reference

| Metric | Value | Source |
|---|---|---|
| Total hotspot detections | 61,583 | Raw NASA file |
| Days with observations | 629 unique dates | Raw NASA file |
| Average daily detections | 97.9 | 61,583 / 629 |
| Peak month (Sep 2024) | 16,911 detections | Monthly breakdown |
| Total FRP | 650.9 GW | Sum across all detections |
| FRP median / mean / max | 6.14 / 10.57 / 954.79 MW | Statistical summary |
| Weather stations | 14 cities, 5 provinces | Current weather file |
| Historical stations | 24 stations, 5 provinces | 2010–2020 cleaned file |
| School facilities (Kalimantan) | 17,548 | Cleaned export |
| Peatland features (Product 1/2) | 25 / 146 | GeoJSON files |
| Soil moisture observations | 9,366 | CSV file |

---

*Review ini berdasarkan semua EDA report, notebook output, dan documentation yang tersedia di repository per 4 September 2026. Findings akan di-update seiring analytical integration (Habib) dan dashboard build phase.*
