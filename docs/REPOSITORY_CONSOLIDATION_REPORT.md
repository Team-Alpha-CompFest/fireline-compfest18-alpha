# FIRELINE Repository Consolidation Report

Audit and consolidation date: 2026-09-04

## Branches merged

| Branch | Result | Merge commit |
|---|---|---|
| `grace` | Merged into `main` with normal non-squashed merge | `4d624b5` |
| `iam/eda-data1-data3-data4` | Merged with `--allow-unrelated-histories`; README and ignore rules resolved; exposure/peatland work preserved | `5d246ba` |
| `origin/feat/bmkg-and-climate-data-daily-idn` | Merged with `--allow-unrelated-histories`; README/ignore rules resolved; both population JSON versions preserved | `07403dc` |

The source branch refs were not deleted. `origin/main` remains the pre-consolidation remote baseline and was not force-pushed.

## Important files preserved

- Grace EDA notebooks, raw/analysis-ready CSVs, findings report, DOCX, and figures.
- IAM school/exposure data, cleaned national/Kalimantan exports, population reference, peatland GeoJSON/GPKG, notebooks, and findings documents.
- BMKG/weather and soil-moisture data, historical climate data, spatial layers, EDA summaries/figures, cleaned/featured outputs, and EDA scripts.
- The two logically equivalent raw hotspot and Pontianak copies remain in their original layouts for provenance; normalized row sets match.
- The two materially different population boundary/data files remain as `datasets/indonesia-province-jml-penduduk.json` and `datasets/indonesia-province-jml-penduduk.iam-branch.json`.

## Conflicts resolved

- `.gitignore`: unioned local-data, Python, virtual-environment, notebook-cache, archive, and IDE rules.
- `README.md`: retained consolidated repository structure/scope and the BMKG project summary.
- Population JSON add/add conflict: no version was discarded; the IAM version was renamed with provenance and the BMKG version retained at the original path.

## Files renamed or moved

- Renamed during conflict resolution: `datasets/indonesia-province-jml-penduduk.json` from the IAM side to `datasets/indonesia-province-jml-penduduk.iam-branch.json`.
- No broad directory moves were performed. Existing layouts were preserved because notebooks and scripts use relative paths.

## Lightweight verification

- `main` working tree is clean except the pre-existing untracked `.DS_Store`.
- All three expected merge commits exist in the history.
- Raw hotspot: 61,583 rows, 15 columns, 2024-08-01 to 2026-05-31, no empty fields observed and no duplicate `(latitude, longitude, acq_date, acq_time)` keys observed.
- BMKG weather: 9,366 rows, 14 cities, 669 dates, five Kalimantan provinces.
- Soil moisture: 9,366 rows, same 14-city/669-date shape as the weather file.
- School cleaned Kalimantan export: 17,548 rows; national export: 215,285 rows.
- Both peatland GeoJSON files and both population JSON files parse as non-empty FeatureCollections.

## Known repository issues

1. There are three established path layouts (`data/`, `datasets/`, and `EDA/`); no canonical physical data directory has been imposed yet.
2. `data/` is ignored by the merged `.gitignore`, although its existing files are tracked. Future new files placed there may be ignored unexpectedly.
3. `scripts/utils_geo.py` references a GeoJSON path under an external dataset layout that is not present in this repository; execution may require configuration.
4. Raw hotspot and Pontianak copies use different line endings but match after line-ending normalization; a canonicalization decision is still pending.
5. The two population JSON versions have identical feature counts but different sizes/content and require a source/schema decision before use.
6. Peatland products have different feature counts and schemas; they are not interchangeable.
7. Some derived outputs contain feature engineering or composite `hazard_score` fields. They are preserved as historical work products, not accepted as a final integrated/modeling dataset.
8. No citizen-report data or schema was found; it remains an external dependency.

## Recommended follow-up

Review `DATA_CATALOG.md`, `DATA_RELATIONSHIP_MAP.md`, and `DATA_ALIGNMENT_ISSUES.md` with the DS team before choosing canonical versions or starting analytical integration.
