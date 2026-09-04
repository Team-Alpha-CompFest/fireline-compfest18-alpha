# FIRELINE DS Master Findings

Consolidated from existing notebooks, reports, summaries, and generated outputs. This document preserves reported findings and flags uncertainty; it does not redo the full EDA or approve production features.

## NASA FIRMS

### Key Findings

- The raw Kalimantan extract contains 61,583 hotspot detections from 2024-08-01 to 2026-05-31.
- Existing Grace EDA reports July–September as 71.9% of detections and 78.7% of total FRP; activity is strongly seasonal.
- FRP is strongly right-skewed: reported median 6.14 MW, 99th percentile 70.20 MW, maximum 954.79 MW.
- Existing weather EDA reports Kalimantan Barat as the largest hotspot concentration in the extract and reports negative humidity/hotspot and positive VPD/hotspot associations at aggregated level.
- Confidence counts verified in the raw file are 57,315 nominal, 2,320 high, and 1,948 low. Confidence should represent evidence reliability, not severity.

### Data Quality

- The raw file has 15 columns and no empty fields observed in the current check.
- No duplicate spatial-temporal keys were observed for `(latitude, longitude, acq_date, acq_time)`.
- The `data/` and `datasets/` raw copies have the same normalized row set; their byte difference is line-ending related.
- Administrative labels are absent from the raw table.

### Important Variables

`latitude`, `longitude`, `acq_date`, `acq_time`, `brightness`, `bright_t31`, `frp`, `confidence`, `daynight`, `scan`, and `track` are the primary source fields. Existing derived tables add hour, log FRP, recurrence, grid, province-rule, and thermal fields.

### Known Limitations

- A detection is not a confirmed incident or grouped fire event.
- Satellite overpass time and daily weather dates require an explicit timezone convention.
- Existing reports contain competing thermal/QC interpretations, including brightness-boundary/saturation flags. These must be verified against the product guide before a filter is created.

## BMKG / Weather

### Key Findings

- The current file contains 9,366 rows across 14 cities/stations and five Kalimantan provinces over 669 dates (2024-08-01 to 2026-05-31).
- Existing EDA reports humidity as negatively associated with hotspot counts and VPD as positively associated; reported Pearson values include approximately -0.482 for mean humidity and +0.470 for maximum VPD.
- The existing summary compares June–October and November–May conditions, but these are descriptive associations, not causal estimates.

### Data Quality

- The file has one unique row per city/date in the current duplicate check and two empty cells observed in the current field scan.
- Weather records are station/reanalysis points, not a continuous weather surface.
- Current weather coverage aligns in date range with NASA and soil moisture, but spatial aggregation differs.

### Important Variables

Temperature, precipitation/rain, wind, relative humidity, VPD, sunshine, dry-day, and high-fire-danger flags are available. Units and derived flag definitions must remain attached to the schema.

### Known Limitations

- Station density is limited and not uniform around hotspots.
- Existing weather–fire correlations aggregate weather across stations and hotspots across the region; this ecological aggregation can hide local relationships.
- `high_fire_danger` is an existing derived field, not an approved FIRELINE threshold.

## Peatland

### Key Findings

- Two spatial products are present: a 25-feature GeoJSON with KHG/peat-depth-oriented properties and a 146-feature GeoJSON with landform/peat-type properties.
- Existing IAM work produced point-in-polygon hotspot enrichment and “outside mapped area” statuses.

### Data Quality

- Both GeoJSON files parse as non-empty FeatureCollections but differ in schema and feature count.
- Peat-enriched outputs are derived and cannot replace the raw hotspot table.

### Important Variables

Potentially useful fields include `is_peatland`, peat type/depth, zone/function, polygon area, and source identifiers. Soil moisture fields are present in the BMKG-side enriched output.

### Known Limitations

- No authoritative product has been selected.
- Polygon coverage, CRS, boundary behavior, and missing/outside-area handling need review.
- Peatland status is environmental context, not by itself vulnerability or risk.

## Exposure / School

### Key Findings

- The national cleaned school export contains 215,285 rows; the Kalimantan export contains 17,548 rows across the five Kalimantan provinces.
- Existing findings report that the data includes school stage/status, coordinates, and province-level population/education-age population fields.
- Existing work flags invalid coordinates rather than deleting all associated rows and identifies a need to distinguish facility proximity from population exposure.

### Data Quality

- `has_valid_coord` is available in the cleaned exports.
- The national source and regional export have different geographic scopes and must not be confused.
- The existing report describes a newer population context in school/BPS data, while the separate province population file is described as 2010; these are not interchangeable.

### Important Variables

Province/city/district, school name, stage, status, lat/long, total population, education-age population, and coordinate validity flag.

### Known Limitations

- School facilities are not a complete representation of all settlements, people, or critical infrastructure.
- Province-level population fields cannot answer village-level exposure.
- A distance/buffer rule has not been agreed.

## Pontianak Weather

### Key Findings

- The raw file has 1,734 rows over 2021–2024 and 1,460 unique dates after the existing cleaning approach.
- Existing Grace EDA reports near-complete temperature/humidity fields and substantial rainfall missingness, with rainfall strongly right-skewed.

### Role as Local Validation

Pontianak weather can support a local/prototype check where its dates overlap the NASA period. It must not be described as representative of all Kalimantan.

### Known Limitations

- Duplicate daily observations in the raw file can overweight dates.
- It has no regional station network and cannot support a Kalimantan-wide weather join by itself.

## Citizen Reports

### Available Fields

No citizen-report data or schema was found physically in the consolidated repository. The existing IAM report mentions citizen reports as future work only.

### Intended Role

Potential future validation/feedback layer, subject to data acquisition, privacy, consent, coverage, and incident-matching decisions.

## Contradictory or uncertain findings

1. The BMKG root summary states 17,448 facilities while the checked Kalimantan cleaned file contains 17,548 rows. This is a count discrepancy requiring source/version review.
2. Existing NASA reports use different thermal/QC narratives; saturation/boundary values must be validated from product documentation.
3. The BMKG-side peat-featured file contains 61,732 rows, while raw and other cleaned hotspot tables contain 61,583 rows. The enrichment pipeline may duplicate or add records.
4. Existing EDA reports refer to derived province labels and hazard scores. These are preserved findings/work products, not approved production definitions.
