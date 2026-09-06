# FIRELINE Dashboard Handoff Checklist

**Tanggal:** 2026-09-06  
**Current status:** `NOT READY` untuk production/live; `READY WITH CONDITIONS` untuk prototype/demo.

## A. Data Alignment

- [ ] Dataset inventory, source-of-truth, geography, time coverage, and grain signed off by DS.
- [ ] `acq_date` (UTC) versus `operational_date` (WIB) convention signed off and labelled in dashboard.
- [ ] Administrative province rule signed off; strict spatial non-match versus station fallback is explicitly decided.
- [ ] Weather/soil operational period and historical baseline period are clearly separated.
- [ ] Structural nulls for non-peatland rows are documented and not confused with data failure.

## B. Analytical Integration

- [ ] NASA source key `(latitude, longitude, acq_date, acq_time)` is unique and traceable to `detection_id`.
- [ ] Every left join preserves 61.583 master rows and publishes input/output/match-rate evidence.
- [ ] Weather station key `(city, date)` is unique and the 200 km threshold is enforced.
- [ ] Soil join is executed from the declared soil source and independently audited.
- [ ] Peatland CRS, containment, boundary duplicates, canonical layer, and unmatched handling are signed off.
- [ ] School exposure uses valid coordinates only and publishes a certified aggregate or bridge without many-to-many KPI inflation.
- [ ] No unresolved duplicate expansion exists in any Tableau source.

## C. CRPI and operational labels

- [ ] CRPI formula, component weights, normalization, and field names are approved by DS/SEA.
- [ ] Dashboard specification is reconciled with implementation, including `Drought14d_Norm` versus soil-moisture features.
- [ ] `hazard_score`, `vulnerability_score`, `exposure_score`, and `crpi_score` are traceable to approved upstream inputs.
- [ ] `urgency_tier` thresholds and `rekomendasi_taktis` mapping are approved.
- [ ] Dashboard does not recompute production CRPI or spatial joins in Tableau.

## D. DS×SEA and Tab 5

- [ ] Dummy citizen-report source exists for demo, with the same schema planned for live input.
- [ ] Dummy records carry `is_simulated=true` / `source_type='dummy'` and a visible `SIMULATION — NOT LIVE DATA` label.
- [ ] Physical live citizen-report dataset/API and schema exists before public release.
- [ ] `report_id` and `detection_id`/`event_id` linkage rule is approved.
- [ ] `incident_id`/`event_id` definition and clustering window are approved, or the dashboard is explicitly observation-only.
- [ ] Verification status, verifier, verification timestamp, and evidence fields exist.
- [ ] CRPI before/after fields and re-scoring audit trail exist.
- [ ] Dispatch, response-time, resolution, and last-updated fields exist.
- [ ] SEA owner, API/table contract, refresh cadence, and SLA are documented.

## E. Five-tab visual coverage

- [ ] Tab 1 queue is traceable to `detection_id` and does not imply unvalidated incident grouping.
- [ ] Tab 2 chronic-fire grid definition and source are certified.
- [ ] Tab 3 weather distance coverage, drought feature, and baseline comparability are documented.
- [ ] Tab 4 school/facility population metrics have a validated grain and no row multiplication.
- [ ] Demo Tab 5 uses dummy report/verification data and can show before/after re-scoring without implying real performance.
- [ ] Live Tab 5 is tested with real report/verification data after publication.
- [ ] Every KPI, mark, tooltip, and filter is backed by a validated field.

## F. Tableau release gate

- [ ] `docs/TABLEAU_DATA_SOURCE_ARCHITECTURE.md` approved.
- [ ] `reports/dashboard/DASHBOARD_READINESS_REPORT.md` verdict changed from `NOT READY`.
- [ ] Certified extracts are generated from approved sources.
- [ ] Row counts, distinct detection counts, null rates, and key KPI totals are reconciled against the audit report.
- [ ] Workbook performance and filter behaviour are tested on the intended Tableau environment.
- [ ] Final DS/SEA sign-off is recorded with date, owner, and source version/hash.

## Current blockers to close

1. Missing live citizen-report source and SEA contract for Tab 5; dummy data is acceptable only for the explicitly labelled demo phase.
2. Weather >200 km threshold violation affecting 2.249 observations.
3. Soil/peat fields inherited from a derived file instead of independently rebuilt/audited in the master builder.
4. Province fallback and hardcoded `is_in_kalimantan` differ from the integration contract.
5. Dashboard specification and master schema/CRPI formula are not reconciled.
