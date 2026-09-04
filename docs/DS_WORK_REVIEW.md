# FIRELINE Data Science Work Review

Review date: 2026-09-04

## `grace`

This branch contains a self-contained EDA package for three datasets:

- NASA FIRMS hotspot observations for the Kalimantan extract.
- Pontianak daily weather for local environmental context.
- The Montesinho/Portugal Forest Fires dataset as a methodology reference.

The meaningful work is in the three notebooks, the Markdown/DOCX findings report, analysis-ready CSVs, and figures. The raw files under `data/` should be preserved. The report explicitly warns that Pontianak is not representative of all Kalimantan and that the Portugal dataset must not be used as Kalimantan evidence.

Important ambiguity: the hotspot and Pontianak files overlap with files on the BMKG branch but are not represented by the same Git blob. The contents must be compared before designating a canonical copy.

## `iam/eda-data1-data3-data4`

This branch contributes exposure-oriented and spatial work:

- school/facility source data and cleaned national/Kalimantan exports;
- provincial population reference data;
- a peatland scraping/processing notebook and peatland spatial outputs in GeoJSON and GeoPackage;
- hotspot preprocessing and peatland-enriched derived files;
- a team findings report focused on NASA, population, and schools.

The school data is not merely temporary: it has a cleaned Kalimantan export and documented coordinate flags. The national cleaned output should be retained as a source/derived artifact but should not be confused with the geographic project scope.

The branch also contains `scripts/rescoring.py`, which is potentially related to later scoring work. It must be preserved but not executed as a new CRPI implementation in this phase.

## `origin/feat/bmkg-and-climate-data-daily-idn`

This branch contributes the broadest repository-level EDA package:

- current BMKG/weather data for 14 stations across five Kalimantan provinces;
- historical climate data and cleaned 2010–2020 Kalimantan subset;
- peat soil moisture and peatland spatial data;
- a large hotspot EDA with preprocessing and feature-engineered exports;
- weather/climate scripts, summaries, and visualizations.

The EDA summaries are useful evidence, but statements based on derived feature outputs, rule-based province labels, or composite hazard scores remain analytical work products. They are not accepted as a final production schema or final CRPI formula in this consolidation phase.

## Duplicate and ambiguous work products

1. Raw hotspot files are nearly identical by header and initial rows but have different Git blob IDs. Treat them as candidate versions until byte/row comparison is complete.
2. The two peatland spatial products have different names, sizes, and schemas. Keep both with source provenance.
3. `fireline_hotspot_clean.csv` appears in multiple locations/branches and has different enrichment levels. A cleaned event table and a peatland-enriched table are different derived products, not interchangeable files.
4. `complete_data.csv` is reused by multiple branches; its downstream cleaned exports have different geographic scopes and must remain separately named.
5. Root `README.md` and `.gitignore` have competing edits. Resolve by retaining the informative project documentation and all relevant ignore rules, then document the resolution.

## Review conclusion

All three branches contain substantive work worth preserving. No branch should be treated as the sole owner of the data foundation, and no filename alone provides enough evidence to discard a competing version.
