# FIRELINE Dashboard Readiness Report

**Tanggal audit:** 2026-09-06  
**Scope:** repository `main`, source datasets, integration scripts, DS×SEA contract, dan dashboard specification  
**Verdict:** `NOT READY`

## 1. Executive verdict

FIRELINE belum siap masuk ke tahap build Tableau production. Tab 1–4 memiliki sebagian besar bahan analitik pada tingkat observasi hotspot, tetapi belum semuanya memenuhi kontrak integrasi atau spesifikasi field dashboard. Tab 5 tidak dapat dibangun secara valid karena dataset citizen report/verification dan kontrak SEA belum ada secara fisik.

Dataset master saat ini berisi 61.583 baris dan 50 kolom, dengan periode NASA `2024-08-01` sampai `2026-05-31`. Master ini berguna sebagai kandidat sumber observasi, tetapi statusnya belum boleh diperlakukan sebagai signed-off source of truth.

## 2. Current-state inventory

| Domain | Bukti aktual | Grain/coverage | Status |
|---|---|---|---|
| NASA hotspot | `datasets/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv` | 61.583 observation; source key unik | Available |
| Integrated master | `datasets/fireline_master_analytical_labeled_2024_2026.csv` | 61.583 rows; 50 columns | Candidate; integration sign-off pending |
| Operational weather | `datasets/bmkg_kalimantan_weather_2024_2026.csv` | 9.366 city-days; 14 cities; 2024-08-01–2026-05-31 | Available, linkage conditionally valid |
| Soil moisture | `datasets/kalimantan_peat_soil_moisture_2024_2026.csv` | 9.366 city-days; same station/date frame | Available, master join not independently executed |
| Peatland | KHG GeoJSON 25 features; BIG GeoJSON 146 features | Static polygon layers | Available, audit reproducibility pending |
| Schools | `datasets/processed/data4_schools_cleaned_kalimantan.csv` | 17.548 rows; 17.363 valid coordinates | Available as separate facility source |
| Historical climate | cleaned EDA file, 87.238 rows, 24 stations, 2010–2020 | Station-day baseline | Available for comparison only |
| Pontianak local | `data/pontianak_weather_daily_2021_2024.csv` | 1.734 source rows; 1.460 unique dates | Local validation only |
| Citizen reports/SEA | Expected `fireline_citizen_reports_simulation.csv` is absent | No report grain/schema/link | Blocking |

## 3. Data Alignment audit

| Dataset/domain | Geography | Time | Grain | Source of truth / derived | Finding |
|---|---|---|---|---|---|
| NASA hotspot | Kalimantan scope | 2024-08-01–2026-05-31; acquisition time UTC | hotspot-observation | Raw NASA file | Aligned and unique on declared composite key |
| Operational weather | 14 nearest-station cities across 5 provinces | 2024-08-01–2026-05-31; daily local date | station-day | BMKG/Open-Meteo curated file | Key lookup coverage is 100%, but 2.249 hotspots are >200 km from station and still marked available in master |
| Soil moisture | Same station frame as operational weather | 2024-08-01–2026-05-31 | station-day | Soil curated file | Values are complete in master, but builder inherits them from a pre-enriched file rather than executing/auditing the declared join |
| Peatland | KHG primary plus BIG secondary | Static snapshot | polygon | KHG GeoJSON provisional canonical | Existing report documents 5.414 matches and 149 boundary duplicates; current environment cannot independently rerun GeoPandas/Shapely validation |
| Schools | Kalimantan | Static 2022 vintage | facility point | Cleaned school export | 17.363 valid coordinates; master stores nearest/count aggregates, not a school-level bridge |
| Historical climate | 5 Kalimantan provinces / 24 stations | 2010–2020 | station-day | Cleaned EDA baseline | Correctly treated as baseline; not a direct same-day join |
| Pontianak | One local station | 2021–2024 | local day | Local source | Suitable only for local validation narrative |

## 4. Join audit

The table below uses the requested format. “Match rate” is defined against the left input unless noted otherwise. A structural non-match (for example, a hotspot outside peatland or with no school inside 5 km) is not automatically a data error.

| Join | Method | Input Rows | Output Rows | Match Rate | Duplicate Risk | Unmatched Reason | Status |
|---|---|---:|---:|---:|---|---|---|
| Hotspot → admin province | Point-in-polygon in builder; fallback to nearest station province | 61.583 | 61.583 | 98,17% strict `province_official`; 100% after fallback | Low row-expansion risk; semantic misclassification risk from fallback | 1.129 strict polygon non-matches | **BLOCKED / contract mismatch**: contract requires NULL and `is_in_kalimantan=False`; builder hardcodes `is_in_kalimantan=True` and fills fallback |
| Hotspot → weather | Lookup by `(operational_date, nearest_station_city)` with acquisition-date fallback | 61.583 | 61.583 | 100% lookup; 96,35% within the 200 km contract threshold | Right key unique; no expansion observed | 2.249 beyond 200 km threshold | **BLOCKED**: all rows are marked `weather_available=True`, including beyond threshold |
| Hotspot → soil | Intended `(operational_date, nearest_station_city)` station-day join; current master inherits soil columns from peat-featured input | 61.583 | 61.583 | 100% non-null in inherited output | Unknown from current builder because no explicit join is run there | Independent join/match evidence absent | **CONDITIONAL**: rerun from declared source and publish match/duplicate audit |
| Hotspot → peatland KHG | Point-in-polygon; deterministic depth-max dedup reported | 61.583 | 61.583 | 5.414 / 61.583 = 8,79% peat match | 149 boundary duplicates reported and removed; current output key is unique | 56.169 structural non-peat rows | **CONDITIONAL**: documented, but geospatial rerun and provisional canonical approval remain pending |
| Hotspot → schools | Equirectangular projected cKDTree nearest-neighbour plus radius counts | 61.583 | 61.583 | 100% nearest metric; 79,06% have ≥1 school within 5 km | Aggregated counts avoid row expansion; raw point join would be many-to-many | 12.897 have zero school within 5 km; 17.363 school points have valid coordinates | **CONDITIONAL**: no 25 km output; no certified school bridge or stable school ID |
| Raw hotspot → master | Numeric-normalized comparison of `(lat, lon, date, time)` | 61.583 | 61.583 | 100% semantic key parity | No duplicate source keys observed | Exact CSV strings differ in formatting for a small number of numeric values | **PASS for traceability**, not a substitute for integration sign-off |

## 5. Analytical integration findings

### Blocking findings

1. **Weather threshold is not implemented.** The contract says a station farther than 200 km must result in `weather_available=False`. The current master contains 2.249 rows beyond that threshold while all 61.583 rows are marked available.
2. **The master builder does not perform all declared joins.** It loads the peat-featured dataset and inherits peat and soil fields. This makes the output complete-looking but prevents an auditable, reproducible soil/peat integration step in the master build.
3. **Administrative semantics differ from the contract.** `province_official` is null for 1.129 points; `province_name` is filled using nearest-station fallback, and `is_in_kalimantan` is hardcoded true. This must be resolved before province-level decision KPIs are published.
4. **CRPI specification and implementation differ.** The dashboard spec names `Drought14d_Norm`, while the master formula uses soil-moisture deficit and has no `Drought14d_Norm`. The spec and master also use different field names and expect fields absent from the master, including district/kabupaten, population exposure, sunshine/wind gusts in the fact, and 25 km school counts.
5. **The integration contract is still DRAFT.** DS×SEA approval, an event-grouping rule, and a downstream report schema are not complete.

### Non-blocking or conditional findings

- The master’s 50 columns differ from the integration report’s stated 41 attributes; the report should be corrected for traceability.
- `acq_date` and `operational_date` differ for 6.304 records. Both must remain visible and the dashboard must label which one drives filters.
- `khg_id` and `fungsi_zona` are null for non-peatland rows; this is structural missingness, not automatically an error.
- Exact string comparison of raw/master composite keys can fail because values such as `114` and `114.0` are formatted differently; numeric-normalized comparison is required.
- Geospatial revalidation cannot currently be reproduced in this environment because GeoPandas/Shapely tooling is unavailable.

## 6. DS×SEA contract audit

| Requirement | Actual repository state | Readiness |
|---|---|---|
| Shared primary grain | `hotspot-observation` is documented | Defined |
| Stable detection key | `detection_id` exists in master and is synthetic | Usable for observation traceability |
| Stable incident/event key | No physical `incident_id`/`event_id`; grouping rule TBD | Blocking for incident workflow |
| Report key and report schema | No `report_id`; planned citizen CSV absent | Blocking |
| Verification status/timestamp | Not present | Blocking |
| CRPI before/after report | Not present | Blocking |
| Dispatch/resolution lifecycle | Not present | Blocking |
| SEA downstream schema/API contract | No formal physical schema in repository | Blocking |
| Ownership and SLA | Not evidenced in current contract | Blocking for operational handoff |

## 7. Readiness by dashboard tab

| Tab | What is backed today | Missing / mismatch | Verdict |
|---|---|---|---|
| 1. Executive Command Center & CRPI | Coordinates, dates, FRP, confidence, peat flags, weather/soil fields, school proximity aggregates, CRPI, urgency, recommendation exist in master | No approved district/kabupaten/population linkage; CRPI formula/spec mismatch; admin fallback issue | **Not ready for production** |
| 2. Hazard & Fire Severity | NASA thermal fields and peat attributes exist | No certified chronic-fire grid table matching the stated 224 zones / 0.05° spec; peat canonical still provisional | **Conditional prototype only** |
| 3. Meteorology & Climate Vulnerability | Operational weather/soil, historical cleaned climate, and Pontianak source exist | Weather threshold issue; no `Drought14d_Norm` in master; sources have different coverage/grain; sunshine/wind gusts are not in master | **Conditional after contract reconciliation** |
| 4. Human Exposure & Vital Facility Vulnerability | Nearest school and 5/10 km counts exist; separate school facility source exists | No 25 km count; no validated hotspot→school bridge; district/status/population KPI can cause many-to-many duplication | **Conditional aggregate-only prototype** |
| 5. Dynamic Re-Scoring & Ground-Truth Verification | Only conceptual `rescoring.py` logic exists | No citizen report file, report key, verification fields, timestamps, before/after CRPI, dispatch/resolution status | **Blocked** |

## 8. Recommended Tableau calculations

### Safe UI-level calculations after upstream sign-off

- `COUNTD([detection_id])` for hotspot count.
- Tier display label/color based on existing `urgency_tier`.
- Display bands for `confidence`, `frp`, `station_dist_km`, and `nearest_school_distance_km`.
- Explicit date selector using either `acq_date` or `operational_date`, with the chosen convention labelled on the dashboard.
- Aggregate-only KPIs from the certified fact: count distinct detections, mean/sum FRP, mean CRPI, and tier distribution.

### Calculations that must remain upstream

- CRPI and all sub-score formulas.
- Drought lag features and weather station assignment.
- Peatland point-in-polygon and boundary deduplication.
- School nearest/radius calculations.
- Incident/event clustering and citizen-report matching.
- Before/after re-scoring and response-time logic.

## 9. Recommended filters and tooltips

Recommended filters for the provisional observation fact:

- `operational_date` and optionally `acq_date` as separate, clearly labelled controls;
- `province_name` only after the admin fallback decision is approved;
- `is_peatland`, `peat_depth`, `confidence`, `daynight`, `urgency_tier`;
- FRP and station/school distance bands;
- `nearest_station_city` and `weather_available` after threshold correction.

Validated tooltip candidates: `detection_id`, latitude/longitude, acquisition and operational date/time, FRP, brightness, `bright_t31`, `temp_delta`, confidence, day/night, peat status/depth, station city/distance, weather values, soil values, nearest school name/stage/distance, school counts, hazard/vulnerability/exposure/CRPI scores, urgency tier, and tactical recommendation.

Do not expose district, population, verification status, dispatch status, resolution status, or report status until those fields have a physical, validated source.

## 10. Required actions before Tableau build

1. DS and SEA approve the integration contract, primary date convention, province fallback policy, CRPI formula/field names, and event/report identifiers.
2. Rebuild and re-audit weather with the 200 km threshold; publish `weather_available=False` for out-of-threshold observations or document an approved exception.
3. Rebuild soil and peat joins from their declared source files in an auditable pipeline; rerun duplicate, match-rate, and CRS/geometry checks.
4. Decide whether the dashboard uses a certified aggregate exposure view or a separate facility source; add/approve 25 km counts if required by the spec.
5. Reconcile the dashboard specification with actual schema: `Drought14d_Norm`, district/population fields, field names, chronic grid definition, and weather variables.
6. Produce the citizen-report/SEA schema and sample data, including report-to-detection/event linkage, verification lifecycle, and before/after CRPI.
7. Only after steps 1–6 pass, create Tableau extracts and validate KPI totals against the certified source.

