# FIRELINE Shared Data Terminology

These working definitions are intended to keep the three DS contributors consistent. Where the repository does not establish a formal definition, the term is marked as a decision point rather than treated as settled science.

| Term | Shared working definition | Important boundary/ambiguity |
|---|---|---|
| Hotspot | A satellite active-fire detection record in the NASA FIRMS extract. | A hotspot is an observation, not automatically a ground-confirmed fire or incident. |
| Incident | A real-world operational case requiring monitoring, verification, or response. | No incident identifier or ground-truth incident table exists yet. |
| Fire event | A grouped set of hotspot observations believed to represent one spatiotemporal fire occurrence. | Grouping rule is not defined; do not infer one event per row. |
| Observation | One recorded measurement or detection at a specific time and place. | Weather and satellite observations have different measurement processes. |
| Hazard | The physical likelihood/intensity or dangerous condition associated with fire activity. | Must remain distinct from exposure and vulnerability. |
| Vulnerability | Susceptibility of people, ecosystems, or assets to harm once exposed. | Peat recurrence and population attributes are proxies, not complete vulnerability measures. |
| Exposure | People, facilities, or assets located where a hazard could affect them. | School rows are facilities; province population is coarse context, not exact exposed population. |
| Risk | A context-dependent combination of hazard, exposure, and vulnerability. | No final FIRELINE risk formula or CRPI is approved in Phase 1–2. |
| FRP | Fire Radiative Power, reported in the hotspot file in MW; a proxy for radiative fire intensity/energy release. | Not a complete measure of burned area, impact, or response priority. |
| Confidence | NASA detection confidence category (`l`, `n`, `h`) indicating reliability/evidence strength. | It is not fire severity; retain separately from FRP. |
| Peatland | Land associated with peat soils/peatland spatial layers. | Two repository products use different schemas and feature coverage. |
| Soil moisture | Water-content measurements for listed soil-depth layers in the soil-moisture file. | Units/source and representativeness must be confirmed before comparisons or thresholds. |
| Weather observation | A daily station/reanalysis-derived record of meteorological variables. | Current BMKG file has 14 locations, not continuous Kalimantan coverage. |
| Spatial join | Linking a point/feature to another spatial object using containment, nearest distance, buffer, or another explicit geometry rule. | Method and CRS must be recorded; longitude rules are not a substitute for point-in-polygon. |
| Temporal join | Linking records using an agreed date/time window and timezone convention. | NASA `acq_time` is UTC; weather data is daily. |
| Analytical grain | The entity represented by one row in an analysis: e.g., hotspot, hotspot-day-grid, station-day, or province-day. | Different grains cannot be joined without aggregation or duplication assumptions. |
| Derived feature | A value calculated from source data, such as `frp_log`, recurrence, dry-day flags, or a score. | Derived features must retain formula, input version, and leakage review. |

## Terms requiring explicit team decisions later

- Whether “hotspot” or a grouped “fire event” is the primary operational unit.
- How a “critical” observation is defined without conflating FRP and confidence.
- Which peatland product is authoritative for the intended use.
- The acceptable spatial/temporal grain for later integration.
- The definition of vulnerability versus a measurable proxy.
