# FIRELINE Data Science Branch Inventory

Audit date: 2026-09-04

This inventory was prepared before merging any DS branch into `main`. File paths below are the paths on the corresponding branch. Dataset row counts are reported only where the branch documentation or Git file statistics make the count clear; exact post-merge counts will be verified after checkout.

| Branch | Important Files | Dataset(s) | Reports | Scripts | Derived Outputs | Potential Conflict | Notes |
|---|---|---|---|---|---|---|---|
| `main` | `README.md` | None | None | None | None | README is a shared root file | Initial commit only; no DS contribution. |
| `grace` | `notebooks/01_EDA_Pontianak_Weather.ipynb`; `02_EDA_Forest_Fire.ipynb`; `03_EDA_NASA_FIRMS_COMPLETED.ipynb` | `data/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv`; `data/pontianak_weather_daily_2021_2024.csv`; `data/forestfires.csv` | `outputs/FIRELINE_Findings_Report.md`; `.docx` | None | Three analysis-ready CSVs and seven figures under `outputs/` | `.gitignore`; root README; duplicate datasets with other branches under different paths | Best preserved as an independent EDA/output collection because notebooks use `../data` and `../outputs`-style relative paths. |
| `iam/eda-data1-data3-data4` | `notebooks/01_eda.ipynb`; `notebooks/data4/02_preprocessing.ipynb`; `notebooks/scraping_gambut_BIG.ipynb` | NASA hotspot; `complete_data.csv`; provincial population JSON; cleaned school data; peatland CSV/GeoPackage/GeoJSON | `documents/temuan-analisis-data-awal-fireline.md`; two PDFs and seven figures | `scripts/rescoring.py`; `main.py` | `datasets/processed/*`; `datasets/gambut/*` | `.gitignore`; root README; the population JSON has a different version from BMKG branch; derived peatland products overlap conceptually with BMKG outputs | Preserves exposure, peatland, and spatial-work contributions. Notebook paths are relative to the existing `datasets/` layout. |
| `origin/feat/bmkg-and-climate-data-daily-idn` | EDA assets under `EDA/01_*`, `EDA/02_*`, `EDA/03_*` | NASA hotspot; BMKG weather 2024–2026; climate data; soil moisture; peatland GeoJSON; school/population support; Pontianak validation; `forestfires.csv` | EDA summaries and README files in each EDA area; root README | `scripts/01_eda_fireline_hotspots.py`; `02_eda_bmkg_weather.py`; `03_eda_kaggle_climate_baseline.py`; `utils_geo.py` | Cleaned/featured hotspot, weather, and climate CSVs; 24+ hotspot figures, 6 weather figures, 6 climate figures | `.gitignore`; root README; population JSON; derived hotspot/peatland versions; possible generated-feature ambiguity | Most complete weather/climate EDA branch, but it also contains feature-engineered outputs that remain out of scope for a new production dataset. |

## Cross-branch duplicate or version groups

| Logical asset | Locations observed | Initial assessment |
|---|---|---|
| NASA VIIRS hotspot raw extract | `grace:data/...csv`; `iam:datasets/...csv`; `bmkg:datasets/...csv` | Same apparent date scope and columns; Git blobs differ for `grace` versus the other two, so verify bytes/line endings and row-level equality after merge. Keep provenance if differences remain. |
| School/BPS source and cleaned data | `iam:datasets/complete_data.csv`, `datasets/processed/data4_schools_cleaned_*`; `bmkg:datasets/complete_data.csv` | `complete_data.csv` appears to share a blob between `iam` and BMKG; national and Kalimantan cleaned outputs are derived products, not replacements for the source. |
| Provincial population | `iam:datasets/indonesia-province-jml-penduduk.json`; `bmkg:datasets/indonesia-province-jml-penduduk.json` | Different blob sizes; likely different source/processing versions. Preserve both under provenance-specific names if the merge cannot establish equivalence. |
| Peatland spatial data | `iam:datasets/gambut/peta_lahan_gambut_kalimantan.{geojson,gpkg}`; `bmkg:datasets/kalimantan_peatland_spatial.geojson` | Different products and schemas; not safe to choose by filename. Preserve both and document schema/coverage. |
| Peatland-enriched hotspot data | `iam:datasets/gambut/firms_kalimantan_gambut_*.{csv,gpkg}`; `bmkg:datasets/fireline_hotspot_peat_featured_*.csv` | Derived products with different fields and enrichment methods. They must not be treated as raw replacements or as the final integrated dataset. |
| Pontianak weather | `grace:data/...csv`; `bmkg:datasets/...csv` | Same apparent source and scope, but path/blob differs; verify exact equality and retain a canonical copy plus provenance note. |
| Forest Fires / Montesinho | `grace:data/forestfires.csv`; `bmkg:datasets/forestfires.csv` | Reference dataset; same apparent content. It is not Kalimantan production data. |

## Path-risk summary

- `grace` notebooks expect the `data/` and `outputs/` layout.
- `iam` notebooks expect `datasets/` relative to the notebook location.
- BMKG scripts expect to be run from repository root and use `datasets/` and `EDA/` paths.
- A blind move into a new canonical layout would break these references. Existing paths should therefore be preserved during consolidation; any later move requires a separate path update and validation.
- Several generated outputs reference files that are present only on their source branch. Post-merge validation must check those dependencies.
