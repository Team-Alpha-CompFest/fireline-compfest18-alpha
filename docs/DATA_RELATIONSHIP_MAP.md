# FIRELINE Data Relationship Map

This is a feasibility map only. It does not create or imply a final integrated analytical dataset.

| Dataset A | Dataset B | Candidate join key | Spatial relationship | Temporal relationship | Expected cardinality | Expected compatibility | Unresolved issue |
|---|---|---|---|---|---|---|---|
| NASA FIRMS raw hotspot | BMKG weather | `acq_date` to weather `date`; nearest station or province | Point to nearest station / province aggregation | Hotspot overpass date to daily weather | Many hotspots to many station-days; one chosen station/aggregate per event would be many-to-one | Moderate for dates; spatially approximate | Need station assignment, UTC/day boundary, and no arbitrary province label. |
| NASA FIRMS raw hotspot | Peatland GeoJSON (either product) | None; point-in-polygon | Hotspot point within peat polygon | Static layer | Many points to zero/one polygon; boundary overlaps possible | Potentially high after CRS/schema checks | Two products have different coverage/schema; choose only after review. |
| NASA FIRMS raw hotspot | Soil moisture | `acq_date` to `date`; nearest station | Point to nearest station or spatial interpolation | Daily | Many hotspots to one station-day or weighted many | Moderate | Stations are sparse relative to points; “peat” applicability needs validation. |
| NASA FIRMS raw hotspot | Kalimantan school export | None; radius/nearest-neighbor/spatial index | Point to facilities within a documented buffer | School layer static; hotspot date is event time | One hotspot to zero/many schools; one school to many hotspots | Potentially high for exposure screening | Buffer distance, valid coordinates, and population semantics are undecided. |
| NASA FIRMS raw hotspot | Administrative boundaries | Point-in-polygon | Point to province/district polygon | Static | One point to zero/one polygon | High if CRS/boundaries align | Boundary version and out-of-scope points must be recorded. |
| NASA FIRMS raw hotspot | Historical Kalimantan climate | date/month + nearest station or province | Point to station/province baseline | 2024–26 event vs 2010–20 historical baseline; no direct date overlap | Many event rows to historical aggregates | Suitable for baseline comparison, not direct same-day join | Baseline statistic and leakage-safe window must be defined later. |
| BMKG weather | Soil moisture | `date`, station/city/province; nearest coordinates | Same station/city or nearest station | Same daily period | Usually one-to-one by city/date where records align | High at observed station level | Source independence, missingness, and soil-layer meaning need review. |
| BMKG weather | Current hotspot daily aggregates | `date` | Province/station aggregate versus hotspot counts | Same 2024–26 dates | One date/province to one aggregate; many hotspots per date | Moderate/high for exploratory correlation | Current EDA aggregates weather over stations and hotspots over all points; ecological/spatial aggregation mismatch. |
| Pontianak weather | Current hotspot | date | Local station/area to all Kalimantan points is not spatially valid | Overlap only 2024 | Many hotspot rows to one local date | Low for regional inference; useful prototype/local validation | Must not be described as Kalimantan-wide weather. |
| Historical climate raw | `province_detail` + `station_detail` | `station_id`, `province_id` | Station metadata supplies coordinates/province | Same historical dates | Many climate rows to one station; station to province many-to-one | High after filtering | Full source table is national; use the cleaned Kalimantan subset for regional claims. |
| Kalimantan school export | Province population JSON | province code/name normalization | School point/province label to province feature | School data and population reference are different vintages | Many schools to one province | Moderate for context only | 2010 population reference conflicts with newer school-associated population fields. |
| Peat-enriched hotspot output | Raw hotspot | stable event key candidate: lat/lon/date/time plus row-level ordering | Same point plus enrichment | Same nominal date range | Expected one-to-one, but featured output has 61,732 versus raw 61,583 rows | Not yet established | Need duplicate/provenance audit before treating it as an enrichment table. |

## Join principles for later phases

1. Preserve raw event rows and source identifiers before any aggregation.
2. Make spatial assignment explicit (CRS, boundary version, nearest-distance rule, and unmatched handling).
3. Keep UTC acquisition time separate from local operational date until the team agrees on the convention.
4. Do not use static exposure or historical climate fields as if they were contemporaneous observations without documenting the temporal relationship.
5. Do not use the Portugal dataset in any Kalimantan empirical join.
