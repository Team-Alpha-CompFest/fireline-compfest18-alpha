# FIRELINE Data Alignment Issues

The issues below are recorded for review. They are not all solved in this phase.

| Issue | Dataset | Why It Matters | Severity | Recommended Resolution |
|---|---|---|---|---|
| Different spatial coverage | Pontianak weather vs Kalimantan hotspot | A single local station cannot represent all Kalimantan conditions. | High | Use only as local validation/prototype; use multi-station weather for regional analysis. |
| Different periods | Current hotspot/weather/soil moisture 2024–26 vs historical climate 2010–20 | Direct joins are impossible; historical values are baselines, not same-day observations. | High | Define baseline windows and keep period labels explicit. |
| Daily vs overpass time | NASA `acq_time` vs daily weather/soil records | A date-only join may assign weather from the wrong local/UTC day. | High | Agree on timezone and date convention; retain UTC acquisition time. |
| Conflicting population versions | Two `indonesia-province-jml-penduduk*.json` files | Province-level exposure/vulnerability numbers may differ materially. | High | Compare source/year/schema with the team; do not select by filename. |
| Conflicting peatland products | 25-feature and 146-feature GeoJSON products | Different spatial coverage and fields can change point-in-polygon results. | High | Profile CRS, coverage, and source; choose or version them explicitly. |
| Derived row-count mismatch | Raw hotspot 61,583 vs BMKG peat-featured 61,732 | Enrichment may duplicate or add rows, breaking one-to-one assumptions. | High | Audit stable keys and duplicate handling before using the featured file. |
| Inconsistent field names | `acq_date`/`date`; `lat`/`latitude`; `long`/`longitude`; `RH_AVG`/`relative_humidity_2m_mean` | Automated joins and schema contracts can fail or silently misalign. | Medium | Create a documented field mapping in a later integration phase. |
| Inconsistent units/semantics | FRP MW, brightness K, precipitation/rain, wind speed, VPD, soil moisture | Thresholds or correlations can be misinterpreted. | High | Preserve units in a data dictionary and confirm source metadata. |
| Missing values | Pontianak `RR` has substantial missingness; BMKG weather has two empty cells observed | Rainfall/dryness features may be biased or silently imputed. | Medium | Quantify by field; retain missingness flags; document any imputation. |
| Duplicate records | Pontianak raw has 1,734 rows but 1,460 unique dates; source contains repeated dates. | Aggregation can overweight duplicated daily observations. | High | Use the cleaned output only with its “first observation” provenance, or define a reproducible dedupe rule. |
| Coordinate validity | School export includes `has_valid_coord`; raw facilities include national rows | Invalid or out-of-scope coordinates can produce false exposure joins. | High | Filter/flag coordinates using explicit geographic and validity checks. |
| Province name normalization | Uppercase school labels, title-case weather labels, metadata names, boundary properties | String joins may miss equivalent provinces or create duplicates. | Medium | Maintain a controlled province lookup with codes and aliases. |
| Administrative labels absent from raw hotspot | NASA raw file has coordinates but no province/district | Dashboard/reporting labels cannot be safely inferred from longitude. | High | Use versioned point-in-polygon boundaries. |
| Potential leakage | Recurrence and `hazard_score` use the full observation period; future modeling could include information after a target time. | Validation metrics can be inflated and operational use invalid. | High | Recompute time-windowed features only after target/grain is approved. |
| Feature/score ambiguity | EDA featured file contains 43 columns and a composite `hazard_score` | Historical EDA output may be mistaken for the final CRPI. | High | Preserve as EDA artifact; do not promote formula or weights without review. |
| Reference geography mismatch | Portugal Forest Fires dataset vs Kalimantan | Its empirical relationships cannot be transferred as production evidence. | High | Keep reference-only; replace with geographically relevant evidence later. |
| Missing citizen feedback | No citizen-report file/schema exists in repository | Intended feedback loop cannot be aligned or validated. | Medium | Obtain schema/data and document consent, privacy, fields, and coverage before use. |
| Broken external path assumption | `scripts/utils_geo.py` points to an external GeoJSON layout not present | Scripts may fail on a clean clone. | Medium | Parameterize boundary path and validate without changing analytical conclusions. |
