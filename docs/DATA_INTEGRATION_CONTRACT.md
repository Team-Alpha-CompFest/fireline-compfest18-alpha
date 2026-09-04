# FIRELINE Data Integration Contract

**Version:** 1.0  
**Author:** Rizki Ilham Putra Pratama  
**Date:** 2026-09-04  
**Status:** DRAFT - Requires DS team review and SE alignment  

---

## 1. Purpose

Dokumen ini menetapkan aturan integrasi data resmi yang harus dipatuhi seluruh anggota tim DS dan SE saat membangun integrated analytical dataset, dashboard, API, maupun model CRPI. Tujuannya memastikan semua join, agregasi, dan transformasi menggunakan konvensi yang sama sehingga output konsisten dan reproducible.

---

## 2. Analytical Grain (Unit Observasi Analitik)

### Primary Grain: `hotspot-observation`

Satu baris dalam integrated analytical dataset = **satu deteksi satelit NASA FIRMS**.

| Property | Value |
|---|---|
| Composite Key | `(latitude, longitude, acq_date, acq_time)` |
| Row count (raw) | 61,583 |
| Uniqueness | Verified — no duplicate keys in raw extract |
| Rationale | Ini unit terkecil yang tersedia; aggregation ke fire event, grid, atau province-day dilakukan di layer analitik/dashboard, bukan di base table |

### Derived Grains (untuk dashboard/analisis)

| Grain | Use Case | Aggregation Rule |
|---|---|---|
| `station-day` | Weather & soil moisture analysis | 1 row per `(city, date)` — native grain of BMKG/soil files |
| `province-day` | Dashboard KPI, time-series | Aggregate hotspot counts, sum/mean FRP, mean weather per province per date |
| `grid-month` | Recurrence & chronic zone analysis | Count distinct dates with detections per 0.5° grid cell per month |
| `province-static` | Exposure summary | School count, population by province |

> **Aturan:** Semua derived grains merujuk ke tabel primary grain. Tidak boleh membuat derived grain yang menghilangkan traceability ke raw `hotspot-observation`.

---

## 3. Incident Identifier

### Current State: Tidak ada `incident_id` formal.

NASA FIRMS tidak menyediakan incident grouping. Saat ini setiap deteksi berdiri sendiri.

### Proposed Convention

| Field | Type | Format | Description |
|---|---|---|---|
| `detection_id` | `string` | `FRL-{acq_date}-{acq_time}-{lat6}-{lon6}` | Synthetic unique ID per detection. `lat6`/`lon6` = latitude/longitude rounded to 6 decimal places, tanpa tanda minus (gunakan N/S prefix). |
| `event_id` | `string` | TBD (Phase 3) | Grouped fire event ID; requires spatiotemporal clustering rule belum disetujui. |

**Contoh `detection_id`:** `FRL-20240801-0545-S206932-E1109148`

> **Decision needed (Phase 3):** Apakah event grouping menggunakan DBSCAN spatial + temporal window, atau clustering manual? Sampai disetujui, semua analisis menggunakan `detection_id` pada hotspot-observation grain.

---

## 4. Temporal Convention

### 4.1 Timezone

| Rule | Specification |
|---|---|
| **Raw acquisition time** | UTC (field `acq_time` = HHMM UTC dari NASA) |
| **Operational date** | WIB (UTC+7) — `operational_date = acq_date` jika `acq_time >= 1700 UTC` (= 00:00 WIB next day), shift date accordingly |
| **Weather/soil date** | Assumed local date (daily aggregate, no intra-day timestamp) |
| **Conversion formula** | `operational_date = acq_date + 1 day` jika `acq_time_utc >= 1700`, else `operational_date = acq_date` |
| **Retained fields** | Simpan KEDUA `acq_date` (UTC original) dan `operational_date` (WIB derived) |

### 4.2 Date Format

| All dates | `YYYY-MM-DD` (ISO 8601) |
|---|---|
| Historical climate `date` | Convert dari `DD-MM-YYYY` ke `YYYY-MM-DD` saat preprocessing |

### 4.3 Temporal Coverage

| Dataset | Period | Overlap Window |
|---|---|---|
| NASA FIRMS hotspot | 2024-08-01 to 2026-05-31 | **Core period** |
| BMKG weather | 2024-08-01 to 2026-05-31 | Same as core |
| Peat soil moisture | 2024-08-01 to 2026-05-31 | Same as core |
| School/exposure | Static (2022 vintage) | N/A — joined as static layer |
| Peatland spatial | Static snapshot | N/A — joined as static layer |
| Historical climate | 2010-01-01 to 2020-12-31 | **Baseline only** — no direct date join to core |
| Pontianak weather | 2021-01-01 to 2024-12-31 | Partial overlap; local validation only |

### 4.4 Season Definition

| Season | Months | Label |
|---|---|---|
| Kemarau (dry) | June – October | `dry` |
| Hujan (wet) | November – May | `wet` |

---

## 5. Spatial Convention

### 5.1 Coordinate Reference System (CRS)

| Rule | Value |
|---|---|
| **Standard CRS** | EPSG:4326 (WGS 84, geographic lat/lon) |
| **All spatial joins** | Reproject to EPSG:4326 before join |
| **Precision** | Retain 6 decimal places for point coordinates |

### 5.2 Administrative Boundary

| Rule | Specification |
|---|---|
| **Boundary source** | `indonesia_provinces.json` (38 features, EPSG:4326) |
| **Join method** | Point-in-polygon spatial join |
| **Province field output** | `province_name` (title-case, normalized) |
| **Unmatched handling** | Hotspots outside all polygons get `province_name = NULL`, flagged `is_in_kalimantan = FALSE` |
| **Kalimantan filter** | Retain only 5 provinces: Kalimantan Barat, Kalimantan Tengah, Kalimantan Timur, Kalimantan Selatan, Kalimantan Utara |

### 5.3 Province Name Normalization Lookup

| Canonical Name | Aliases Accepted |
|---|---|
| Kalimantan Barat | KALIMANTAN BARAT, Kalimantan Barat, kalimantan barat |
| Kalimantan Tengah | KALIMANTAN TENGAH, Kalimantan Tengah |
| Kalimantan Timur | KALIMANTAN TIMUR, Kalimantan Timur |
| Kalimantan Selatan | KALIMANTAN SELATAN, Kalimantan Selatan |
| Kalimantan Utara | KALIMANTAN UTARA, Kalimantan Utara |

> **Rule:** Semua pipeline normalize ke title-case canonical name. Jangan gunakan province code tanpa lookup karena code systems berbeda antar dataset.

### 5.4 Station Assignment (Hotspot → Weather/Soil)

| Rule | Specification |
|---|---|
| **Method** | Nearest station by haversine distance |
| **Output fields** | `nearest_station_city`, `nearest_station_province`, `station_distance_km` |
| **Max distance threshold** | 200 km — hotspots beyond this get `weather_available = FALSE` |
| **Rationale** | 14 stations across ~540,000 km²; average Voronoi cell ~38,500 km² |

### 5.5 Peatland Spatial Join

| Rule | Specification |
|---|---|
| **Authoritative product** | `datasets/kalimantan_peatland_spatial.geojson` (25 features, KHG-oriented) — **PROVISIONAL** pending Habib's audit |
| **Secondary product** | `datasets/gambut/peta_lahan_gambut_kalimantan.geojson` (146 features, landform-oriented) — retained for comparison |
| **Join method** | Point-in-polygon (hotspot point within peat polygon) |
| **Output fields** | `is_peatland` (boolean), `peat_depth`, `depth_cm`, `khg_id` |
| **Unmatched handling** | `is_peatland = FALSE`, depth fields = NULL |
| **CRS check** | Verify both products are EPSG:4326 before join |

### 5.6 School Exposure (Hotspot → Schools)

| Rule | Specification |
|---|---|
| **Method** | Radius buffer dari hotspot point |
| **Buffer distances** | 5 km (immediate), 10 km (near), 25 km (extended) |
| **Output fields** | `schools_within_5km`, `schools_within_10km`, `schools_within_25km`, `nearest_school_distance_km`, `nearest_school_name` |
| **Coordinate filter** | Only schools with `has_valid_coord = True` |
| **Static nature** | School layer is 2022 vintage; document this temporal gap |

---

## 6. Source of Truth

### 6.1 Canonical Raw Files

| Domain | Canonical File | Path |
|---|---|---|
| Hotspot | fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv | `datasets/` |
| Weather | bmkg_kalimantan_weather_2024_2026.csv | `datasets/` |
| Soil Moisture | kalimantan_peat_soil_moisture_2024_2026.csv | `datasets/` |
| Peatland (primary) | kalimantan_peatland_spatial.geojson | `datasets/` |
| Peatland (secondary) | peta_lahan_gambut_kalimantan.geojson | `datasets/gambut/` |
| School (Kalimantan) | data4_schools_cleaned_kalimantan.csv | `datasets/processed/` |
| Admin boundary | indonesia_provinces.json | root |
| Historical climate | kalimantan_climate_2010_2020_clean.csv | `EDA/03_kaggle_indonesia_climate/03_preprocessing/` |

### 6.2 Files NOT Source of Truth (derived/reference only)

| File | Reason |
|---|---|
| `fireline_hotspot_peat_featured_2024_2026.csv` | Derived enrichment, 61,732 rows ≠ raw 61,583 — row count mismatch needs audit |
| `fireline_hotspot_featured.csv` | EDA feature engineering output with composite `hazard_score`; not approved production schema |
| `fireline_hotspot_clean.csv` | Intermediate preprocessing; use raw + fresh pipeline instead |
| `forestfires.csv` | Portugal reference only — excluded from production |
| `pontianak_weather_daily_2021_2024.csv` | Local single-station — not regional weather |
| `indonesia-province-jml-penduduk*.json` | 2010 census data, conflicting versions — superseded by 2022 BPS in school dataset |
| `complete_data.csv` | National scope — use Kalimantan cleaned export instead |

---

## 7. Join Strategy Summary

### 7.1 Join Map

```
NASA FIRMS (hotspot-observation)
├── × Admin Boundary ──── [point-in-polygon] → province_name
├── × BMKG Weather ─────── [operational_date = weather.date, nearest_station] → weather fields  
├── × Soil Moisture ────── [operational_date = soil.date, nearest_station] → soil fields
├── × Peatland Spatial ─── [point-in-polygon] → peatland fields
├── × School Export ────── [radius buffer 5/10/25 km] → exposure counts
└── × Historical Climate ── [NO DIRECT JOIN; baseline comparison by province+month]
```

### 7.2 Join Rules Detail

| Join | Left Table | Right Table | Key | Type | Expected Cardinality | Null Handling |
|---|---|---|---|---|---|---|
| Hotspot → Admin | hotspot | admin polygon | spatial PiP | left outer | many:0-1 | NULL province = outside boundary |
| Hotspot → Weather | hotspot | weather | `(operational_date, nearest_station_city)` | left outer | many:1 | NULL weather = no station within threshold |
| Hotspot → Soil | hotspot | soil moisture | `(operational_date, nearest_station_city)` | left outer | many:1 | NULL soil = same as weather |
| Hotspot → Peatland | hotspot | peatland polygon | spatial PiP | left outer | many:0-1 | `is_peatland = FALSE` |
| Hotspot → Schools | hotspot | school points | spatial radius | left outer | many:many (aggregated to counts) | 0 schools = no facilities in radius |
| Weather → Soil | weather | soil moisture | `(date, city)` | inner | 1:1 | Drop unmatched (same frame expected) |

### 7.3 Join Integrity Checks

Setelah setiap join, verifikasi:

1. **Row count preservation:** Left outer join tidak boleh menambah/mengurangi row count dari left table
2. **Key uniqueness:** Right table key harus unique (1 weather row per city-date)
3. **Coverage rate:** Hitung `% NOT NULL` untuk setiap joined field
4. **Spatial sanity:** Sample 100 matched pairs, verify distance/containment makes sense visually

---

## 8. Data Quality & Leakage Policies

### 8.1 Duplicate Handling

| Dataset | Duplicate Rule |
|---|---|
| NASA hotspot | Key `(lat, lon, acq_date, acq_time)` — currently 0 duplicates; if found, keep first occurrence |
| BMKG weather | Key `(city, date)` — currently 0 duplicates |
| Soil moisture | Key `(city, date)` — currently 0 duplicates |
| Schools | Key `(school_name, district_name)` — flag and review |

### 8.2 Missing Value Policy

| Field | Policy |
|---|---|
| Weather fields (temp, humidity, etc.) | Retain NULL; do NOT impute. Flag `weather_available = FALSE` |
| Soil moisture | Retain NULL; flag `soil_data_available = FALSE` |
| FRP | No missing values observed; if missing, exclude from FRP-based calculations |
| School coordinates | Use only `has_valid_coord = True` for spatial joins |
| Peatland attributes | NULL = outside mapped peatland area; treat as `is_peatland = FALSE` |

### 8.3 Leakage Prevention

| Risk | Mitigation |
|---|---|
| Full-period recurrence counts | **Do not use** `fire_recurrence_count` from EDA featured file. Recompute using only data before target date with rolling window |
| Composite `hazard_score` | **Do not use** existing EDA formula. Define and version new formula through team review |
| Future weather in historical features | Ensure all weather features use only `operational_date` or earlier |
| Static exposure as temporal | Document that school/population data is 2022 vintage; do not imply contemporaneous observation |

---

## 9. Output Schema — Integrated Analytical Dataset

### Required Fields (minimal viable)

| Column | Type | Source | Description |
|---|---|---|---|
| `detection_id` | string | Derived | Synthetic unique ID |
| `latitude` | float | NASA raw | Detection latitude |
| `longitude` | float | NASA raw | Detection longitude |
| `acq_date` | date | NASA raw | UTC acquisition date |
| `acq_time` | int | NASA raw | UTC acquisition time (HHMM) |
| `operational_date` | date | Derived | WIB operational date |
| `brightness` | float | NASA raw | Brightness temperature K |
| `bright_t31` | float | NASA raw | Channel 31 brightness K |
| `frp` | float | NASA raw | Fire Radiative Power MW |
| `confidence` | string | NASA raw | Detection confidence (l/n/h) |
| `daynight` | string | NASA raw | D or N |
| `scan` | float | NASA raw | Along-scan pixel size |
| `track` | float | NASA raw | Along-track pixel size |
| `province_name` | string | Admin join | Normalized province name |
| `is_in_kalimantan` | boolean | Admin join | Within 5 Kalimantan provinces |
| `nearest_station_city` | string | Station assignment | Nearest weather station city |
| `station_distance_km` | float | Station assignment | Distance to nearest station |
| `weather_available` | boolean | Derived | Station within threshold |
| `temperature_2m_max` | float | Weather join | Daily max temp °C |
| `temperature_2m_mean` | float | Weather join | Daily mean temp °C |
| `precipitation_sum` | float | Weather join | Daily precipitation mm |
| `relative_humidity_2m_mean` | float | Weather join | Daily mean RH % |
| `vapor_pressure_deficit_max` | float | Weather join | Daily max VPD kPa |
| `windspeed_10m_max` | float | Weather join | Daily max wind km/h |
| `sunshine_hours` | float | Weather join | Daily sunshine hours |
| `soil_moisture_0_to_7cm` | float | Soil join | Topsoil moisture |
| `soil_moisture_7_to_28cm` | float | Soil join | Subsoil moisture |
| `is_peatland` | boolean | Peatland join | Within peatland polygon |
| `peat_depth` | string | Peatland join | Peat depth class |
| `depth_cm` | float | Peatland join | Peat depth numeric cm |
| `schools_within_5km` | int | School buffer | Count schools 5km radius |
| `schools_within_10km` | int | School buffer | Count schools 10km radius |
| `nearest_school_distance_km` | float | School buffer | Distance to closest school |

### Extension Fields (Phase 3, setelah validasi)

| Column | Type | Source | Notes |
|---|---|---|---|
| `event_id` | string | Clustering | Requires approved grouping algorithm |
| `risk_score` | float | CRPI model | Requires approved formula |
| `urgency_tier` | int | CRPI model | 1-4 tier mapping dari risk_score |
| `historical_baseline_temp` | float | Historical climate | Province-month baseline comparison |

---

## 10. Versioning & Update Protocol

| Rule | Specification |
|---|---|
| **Contract version** | Semver (major.minor); increment major jika grain/key/join berubah |
| **Integrated dataset filename** | `fireline_integrated_v{VERSION}_{YYYYMMDD}.csv` |
| **Change log** | Setiap perubahan join rule/schema harus didokumentasikan di file ini |
| **Refresh trigger** | Re-run pipeline jika raw data diperbarui atau join rule berubah |

---

## 11. Decisions Pending (Untuk Diskusi Tim)

| # | Decision | Owner | Deadline | Impact |
|---|---|---|---|---|
| 1 | Select authoritative peatland product (25-feature vs 146-feature) | Habib | 2026-09-05 | Peatland join fields |
| 2 | Approve event grouping algorithm for `event_id` | All DS | Phase 3 | Grain extension |
| 3 | Approve CRPI formula (Hazard × Exposure × Vulnerability weights) | All DS | Phase 3 | `risk_score`, `urgency_tier` |
| 4 | Confirm school exposure buffer distances (5/10/25 km) with UXA/SE | All + SE | 2026-09-05 | Dashboard & API |
| 5 | Citizen report schema & integration point | All + SE | Phase 3 | Feedback loop |
| 6 | Max station distance threshold (currently 200 km) | DS | 2026-09-05 | Weather coverage |
| 7 | Dashboard refresh frequency & staleness indicator | DS + SE | 2026-09-05 | `last_updated` behavior |

---

## 12. Glossary Reference

Lihat [DATA_TERMINOLOGY.md](DATA_TERMINOLOGY.md) untuk definisi istilah bersama.

---

*Document ini bersifat living document. Setiap perubahan harus di-review oleh minimal 2 anggota DS sebelum diterapkan ke pipeline.*
