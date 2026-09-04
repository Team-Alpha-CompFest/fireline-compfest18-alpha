# FIRELINE Data Alignment Report

Phase 2 status: complete as an inventory/alignment assessment, 2026-09-04.

## 1. What datasets do we actually have?

We have 29 physical data artifacts representing raw, metadata, spatial, cleaned, and EDA-derived products. The core logical groups are NASA hotspot, current weather, peat soil moisture, peatland spatial layers, school/exposure data, historical climate, Pontianak local weather, province/station metadata, population references, and the Portugal Forest Fires reference dataset. No citizen-report data/schema is present.

## 2. Production/core candidates

- NASA FIRMS hotspot detections (Kalimantan extract, 61,583 rows).
- BMKG/current weather file (14 cities, five provinces, 9,366 rows).
- Peat soil moisture file (same 14-city/date frame, 9,366 rows).
- Peatland spatial products (two competing products; no authoritative choice yet).
- Kalimantan cleaned school/exposure export (17,548 rows).

These are candidates, not yet a finalized production data model.

## 3. Supporting/validation datasets

- Cleaned Kalimantan historical climate, 87,238 station-day rows from 2010–2020.
- Pontianak weather, 2021–2024, local validation only.
- Province/station metadata.
- Derived peatland-enriched hotspot outputs.
- National school export and province population reference for context.

## 4. Reference-only datasets

`forestfires.csv` and `outputs/forest_fire_analysis_ready.csv` describe the Montesinho Natural Park, Portugal, 2000–2003. They may inform feature vocabulary, but they are excluded from empirical Kalimantan production/dashboard use.

## 5. Geographic coverage

- NASA hotspot: Kalimantan extract by coordinate bounds, without administrative labels in raw data.
- Current weather and soil moisture: five Kalimantan provinces, 14 cities/stations.
- Historical climate clean: five Kalimantan provinces, 24 stations.
- School exposure clean: five Kalimantan provinces; national companion covers all 34 provinces.
- Pontianak weather: Pontianak only.
- Population references: 32 province features and conflicting versions.
- Forest Fires: Portugal only.

## 6. Temporal coverage

- Core hotspot, current weather, and soil moisture: 2024-08-01 to 2026-05-31.
- Historical climate: 2010-01-01 to 2020-12-31.
- Pontianak local weather: 2021-01-01 to 2024-12-31.
- School/exposure and spatial layers: static/annual snapshots as documented; exact effective dates require source confirmation.
- Forest Fires: 2000–2003.

## 7. What can potentially be joined?

- NASA to current weather/soil moisture by date plus nearest station or documented spatial aggregation.
- NASA to peatland and administrative boundaries by point-in-polygon.
- NASA to schools by radius/nearest-facility spatial relationship.
- Historical climate to station/province metadata by IDs and to current observations as a baseline, not same-day ground truth.
- School rows to province context after name/code normalization.

## 8. What cannot yet be joined safely?

- Pontianak weather to all Kalimantan hotspots as if it were regional weather.
- Either peatland product to production without selecting and validating its coverage/schema.
- The BMKG peat-featured file to raw hotspots as one-to-one without duplicate/key audit.
- Portugal Forest Fires to Kalimantan empirical outcomes.
- Population versions or province labels without a source/year/code decision.
- Any feature set that uses full-period recurrence or composite hazard scores for future validation without leakage controls.

## 9. Important existing EDA findings

- Hotspot activity is strongly seasonal; the Grace report gives 71.9% of detections and 78.7% of total FRP in July–September.
- FRP is highly right-skewed, with reported median 6.14 MW and maximum 954.79 MW.
- Confidence is concentrated in nominal detections and should not be treated as severity.
- Existing weather EDA reports lower humidity and higher VPD associated with higher daily hotspot activity, with spatial/aggregation caveats.
- Historical climate EDA describes 2010–2020 as a baseline and highlights dry-season patterns and 2015/2019 as historical comparison periods.
- School analysis identifies a Kalimantan facility layer with coordinate validity flags and province-level population context.
- Existing spatial work shows two peatland products and derived hotspot enrichments, but no product decision has been made.

## 10. Decisions required before analytical integration

1. Select canonical versions for population, peatland, and any raw/derived duplicate groups, with source and checksum recorded.
2. Approve the analytical grain: hotspot observation, grouped fire event, hotspot-day-grid, or another unit.
3. Approve spatial and temporal join rules, including boundary version, station assignment, buffer distance, and UTC/local date convention.
4. Define data-quality and leakage policies for duplicates, missing weather, full-period recurrence, confidence, and derived scores.
5. Confirm whether/when citizen reports will be obtained and what privacy/validation requirements apply.

## Phase 2 stop condition

Repository consolidation and data alignment are complete. No final integrated analytical dataset, CRPI, feature-engineering expansion, model training, Tableau dashboard, SEA implementation, or API work was performed.
