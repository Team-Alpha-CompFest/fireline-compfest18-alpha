# FIRELINE Data Science Merge Plan

Prepared: 2026-09-04, before branch merges.

## Proposed merge order

1. Merge `grace` into `main` to preserve the first complete EDA/output package and its existing `data/`/`outputs/` path layout.
2. Merge local `iam/eda-data1-data3-data4` to add exposure, population, peatland, and preprocessing work.
3. Merge `origin/feat/bmkg-and-climate-data-daily-idn` to add weather, historical climate, soil moisture, spatial EDA, and scripts.

Each merge will use a normal non-squashed merge. After each merge: inspect `git status`, inspect the diff/stat, check for deletions/overwrites, check dataset sizes, and run lightweight path/file validation.

## Expected conflicts and handling

| Area | Expected risk | Safe handling |
|---|---|---|
| Root `README.md` | Each branch has different project documentation. | Retain a consolidated informative README, with scope and paths from all contributions. Do not silently prefer the shortest file. |
| `.gitignore` | Ignore rules differ. | Union relevant rules; do not add rules that hide tracked analytical files. |
| Provincial population JSON | Branch versions have different blob sizes. | Keep both temporarily with provenance-specific names if Git reports add/add conflict; compare schemas before any later decision. |
| Raw hotspot extract | Same logical filename exists under different directory layouts and branch blobs differ. | Preserve both paths initially; compare after merge. Do not overwrite either raw file. |
| Pontianak weather | Same logical dataset exists under different paths/blobs. | Preserve both until exact comparison; mark it as local validation data. |
| Peatland spatial outputs | Different products and schemas. | Preserve both GeoJSON/GPKG products and document their field/coverage differences. |
| Derived hotspot files | Clean, featured, peat-enriched, and rescored outputs have different semantics. | Keep all named products; do not collapse them into an integrated modeling table. |
| Notebook paths | Relative paths depend on the original branch layout. | Do not move files during merge. Search path references and report unresolved ones. |

## Files to preserve

- Raw/source CSV, JSON, GeoJSON, and GeoPackage files from all branches.
- All EDA notebooks, scripts, Markdown/PDF/DOCX reports, and visual outputs.
- Cleaned and derived exports, with their original names and paths where possible.
- Git history through ordinary merges.

## Files not to create or commit in this phase

- A final integrated analytical/modeling dataset.
- New CRPI calculations or a finalized risk formula.
- Tableau/dashboard artifacts, APIs, SEA architecture changes, or model-training outputs.
- Obvious local environment/cache files such as `.venv`, `__pycache__`, and `.DS_Store` when untracked.

The existing untracked `.DS_Store` is outside this consolidation and will not be deleted automatically.

## Standardization policy

The repository currently contains three established layouts (`data/` + `outputs/`, `datasets/` + `documents/`, and `EDA/` + `datasets/`). Because notebooks and scripts use relative paths, no blind mass move is planned. Safe documentation directories (`docs/` and `reports/findings/`) may be added. A later structural migration should be a separate change with path updates and notebook execution checks.

## Stop/escalation rule

If a merge conflict involves two materially different dataset versions and evidence cannot establish equivalence, stop at that conflict, preserve both versions, document the conflict, and ask the DS team to decide. Do not resolve by filename, timestamp, or branch order.
