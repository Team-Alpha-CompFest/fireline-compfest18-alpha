# FIRELINE Tableau Data Source Architecture

**Tanggal audit:** 2026-09-06  
**Status:** Proposed handoff architecture — belum disetujui untuk build Tableau  
**Verdict readiness:** `NOT READY` untuk production/live; `READY WITH CONDITIONS` untuk prototype/demo setelah source simulasi dibuat

## 1. Prinsip arsitektur

Tableau tidak boleh menggabungkan seluruh CSV mentah secara bebas. Setiap domain memiliki grain berbeda, sehingga koneksi langsung antar fakta hotspot, weather harian, sekolah, dan poligon gambut dapat menghasilkan penggandaan baris dan KPI yang salah.

Arsitektur yang direkomendasikan:

```text
NASA hotspot observation
        |
        +--> curated analytical fact (one row per detection)
        |       +--> operational weather/soil attributes
        |       +--> peatland attributes
        |       +--> school exposure aggregates
        |       +--> CRPI and urgency outputs
        |
        +--> province-day / grid-month views for aggregate visuals

Operational weather + soil --------> Tab 3 station-day analysis
Historical climate baseline --------> Tab 3 baseline comparison
Pontianak local series --------------> Tab 3 local validation only
School facility points --------------> Tab 4 facility map/detail only
Peatland polygons -------------------> map underlay/spatial context
Citizen reports (dummy -> live) ------> Tab 5
```

## 2. Recommended logical sources

| Logical source | Physical source(s) | Grain | Key | Dashboard use | Current recommendation |
|---|---|---|---|---|---|
| `fireline_observation_fact` | `datasets/fireline_master_analytical_labeled_2024_2026.csv` | 1 row per NASA hotspot observation; 61,583 rows | Source composite `(latitude, longitude, acq_date, acq_time)`; `detection_id` is synthetic | Tabs 1–4; Tab 5 only after report linkage exists | Candidate primary source, **not signed off** until integration blockers are resolved |
| `fireline_raw_reference` | `datasets/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | NASA raw hotspot observation; 61,583 rows | Same source composite | Audit/drill-through and provenance | Keep outside normal dashboard joins |
| `operational_weather_station_day` | `datasets/bmkg_kalimantan_weather_2024_2026.csv` | 1 city-station day; 9,366 rows, 14 cities | `(city, date)` | Tab 3 operational weather | Use as a separate station-day source; do not join raw rows in Tableau without a controlled relationship |
| `operational_soil_station_day` | `datasets/kalimantan_peat_soil_moisture_2024_2026.csv` | 1 city-station day; 9,366 rows | `(city, date)` | Tab 3 soil analysis | Separate source; verify date/station linkage upstream |
| `historical_climate_baseline` | `EDA/03_kaggle_indonesia_climate/03_preprocessing/kalimantan_climate_2010_2020_clean.csv` | 1 historical station day; 87,238 rows, 24 stations | `(station_id, date)` | Tab 3 historical comparison | Separate source; baseline only, not a direct join to core hotspot rows |
| `pontianak_local_validation` | `data/pontianak_weather_daily_2021_2024.csv` | Local daily series; 1,734 source rows / 1,460 unique dates | `date` after deduplication | Tab 3 Pontianak validation | Separate, explicitly labelled local validation; not regional weather |
| `school_facility_points` | `datasets/processed/data4_schools_cleaned_kalimantan.csv` | 1 school/facility row; 17,548 rows, 17,363 valid coordinates | No stable school ID; candidate composite `(school_name, district_name)` | Tab 4 facility map/detail; Tab 1 context | Keep separate from hotspot fact unless a validated aggregate view is produced |
| `peatland_spatial_layer` | `datasets/kalimantan_peatland_spatial.geojson` (25 features) and secondary `datasets/gambut/peta_lahan_gambut_kalimantan.geojson` (146 features) | Polygon | `khg_id`/polygon identifier | Map underlay and Tab 2 spatial context | Keep as spatial layer; primary status remains provisional pending reproducible audit |
| `citizen_report_fact` | Dummy sekarang: `fireline_citizen_reports_simulation.csv`; live nanti: source/API SEA | 1 citizen report | `report_id`; `detection_id`/`event_id` link | Tab 5 | Dummy boleh untuk demo, tetapi harus eksplisit `SIMULATION` dan memakai schema live |

## 3. Source selection by dashboard tab

| Tab | Primary source | Supporting source(s) | Safe relationship |
|---|---|---|---|
| 1. Executive Command Center & CRPI | `fireline_observation_fact` | peatland layer; school aggregate fields already in fact | Filter/aggregate the fact; no raw school or polygon many-to-many join |
| 2. Hazard & Fire Severity | `fireline_observation_fact` | peatland layer; optional validated grid-month view | Use observation grain for points and a separately materialized grid view for recurrence |
| 3. Meteorology & Climate Vulnerability | operational weather/soil station-day plus `fireline_observation_fact` | historical baseline; Pontianak local series | Relate through a certified hotspot-to-station-day bridge, not an unconstrained Tableau join |
| 4. Human Exposure & Vital Facility Vulnerability | `school_facility_points` for facilities; `fireline_observation_fact` for hotspot exposure metrics | province/static reference if required | Keep facility detail and hotspot metrics as separate sheets/sources unless an aggregate bridge is certified |
| 5. Dynamic Re-scoring & Ground-Truth Verification | `citizen_report_fact` (dummy first, then live) | `fireline_observation_fact` | Requires a stable report-to-detection/event key and before/after score fields |

### Two-phase implementation untuk Tab 5

**Phase A — demo/competition:** gunakan dataset dummy yang dibuat khusus untuk menguji visual, filter, dan alur re-scoring. Dummy harus memiliki flag `is_simulated=true`, `source_type='dummy'`, dan label visual `SIMULATION — NOT LIVE DATA`.

**Phase B — live setelah publikasi:** ganti input dengan data/API citizen report tanpa mengubah struktur worksheet Tableau. Data live harus menyimpan report baru, status verifikasi, hasil pencocokan ke `detection_id`/`event_id`, dan audit perubahan skor.

Minimum schema yang sebaiknya sama sejak dummy:

`report_id`, `report_timestamp`, `citizen_latitude`, `citizen_longitude`, `report_type`, `description`, `detection_id`, `event_id`, `matching_method`, `verification_status`, `verified_by`, `verified_at`, `crpi_initial`, `crpi_updated`, `response_time_minutes`, `dispatch_status`, `resolution_status`, `last_updated`, `is_simulated`, `source_type`.

`event_id` boleh null pada fase awal jika keputusan clustering belum disetujui; `detection_id` tetap menjadi link observasi. Dummy tidak boleh dipakai untuk menyimpulkan performa citizen reporting, response time, atau akurasi verifikasi.

## 4. Grain and key controls

The current contract defines the primary grain as `hotspot-observation`, with composite key `(latitude, longitude, acq_date, acq_time)`. It does not yet define an approved `event_id` clustering rule or a physical citizen-report schema.

Required controls before publishing an extract:

1. Preserve `acq_date` (NASA UTC) and `operational_date` (WIB) as separate fields. The current fact has 6,304 shifted dates.
2. Use `COUNTD(detection_id)` for hotspot counts. Do not count rows after adding a one-to-many source.
3. Enforce one row per `(city, date)` for operational weather and soil.
4. Treat school and peatland sources as one-to-many spatial domains. Publish pre-aggregated hotspot metrics or a certified bridge before connecting them.
5. Keep `incident_id`/`event_id` unresolved until the event-grouping decision is approved. `detection_id` is not an incident identifier.
6. Display the coverage and quality flags rather than converting structural non-matches into ordinary zeros.

## 5. Fields suitable for the current fact source

The current master has 50 columns, including raw hotspot fields, operational weather, soil, peatland, nearest-school/5 km/10 km exposure metrics, scores, urgency, and tactical recommendation. It has no `incident_id`, `event_id`, `report_id`, district/city exposure aggregation, verification status, dispatch status, resolution status, or `last_updated`.

Use the existing fields for a provisional observation-level prototype only after the blockers in the readiness report are resolved. Do not recreate upstream CRPI, spatial joins, drought lag features, or report matching as Tableau calculated fields.

## 6. Publication gate

No Tableau workbook should be labelled production-ready until:

- weather distance-threshold handling is corrected and re-audited;
- soil and peat joins are reproducible from declared inputs;
- administrative fallback behaviour is reconciled with the contract;
- dashboard field names and CRPI formula are reconciled with the actual master;
- Tab 5 receives a schema-compatible dummy source for demo and a separately approved live source for publication;
- dummy/live swap is tested without changing worksheet field names;
- DS and SEA approve the source contract and report linkage.
