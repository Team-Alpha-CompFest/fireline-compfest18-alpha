# FIRELINE — Data Exploration & Findings Report

## Scope
This report consolidates the Data Exploration work for the three datasets currently used by the Data Science team:

1. **NASA FIRMS Active Fire — Kalimantan, NOAA-20 VIIRS** (main event/hotspot dataset)
2. **Pontianak Weather Daily 2021–2024** (environmental context)
3. **Forest Fires / Montesinho** (historical fire-methodology reference)

The report is written for FIRELINE's intended use as a **Decision Support System (DSS)** for BPBD, Manggala Agni, and local-government Command Centers. The objective at this checkpoint is not to finalize an AI risk model, but to identify trustworthy patterns, data limitations, feature candidates, and the next integration steps.

---

## 1. Executive Summary

### 1.1 NASA FIRMS
- The supplied NASA dataset contains **61,583 hotspot detections** from **1 August 2024 to 31 May 2026** across the supplied Kalimantan bounding area.
- All 15 raw columns are complete; there are **0 exact duplicate rows** and **0 spatial-temporal duplicates** under `(latitude, longitude, acq_date, acq_time)`.
- Fire activity is highly concentrated in time. **July–September represents 71.9% of all hotspot detections and 78.7% of total FRP** in this extract.
- FRP is highly right-skewed: the **median is 6.14 MW**, while the **99th percentile is 70.20 MW** and the maximum is **954.79 MW**.
- Detection confidence is dominated by the nominal class (`n`, 93.1%), with high (`h`, 3.8%) and low (`l`, 3.2%) observations. Confidence should be treated as **reliability**, not severity.
- Spatial concentration is clearly visible, but the current dataset lacks administrative boundary identifiers; grid cells are therefore appropriate for screening, while province/district labels should come from an explicit spatial join.

### 1.2 Pontianak Weather
- The raw weather file contains **1,734 rows**, which reduce to **1,460 unique dates** after removing duplicate dates while preserving the first observation.
- `TAVG` and `RH_AVG` are nearly complete, while `RR` (rainfall) has **459 missing values (26.2%)**.
- Rainfall is strongly right-skewed: median **5.5 mm**, 99th percentile **101.6 mm**, maximum **197 mm**.
- Temperature and humidity show a strong inverse association in the available daily station data (Pearson approximately **-0.816**), so these variables should not be interpreted as independent signals without checking multicollinearity.
- Because the dataset is station-based and limited to Pontianak, it cannot be treated as spatially representative of all Kalimantan without interpolation or a broader station/network dataset.

### 1.3 Forest Fire Dataset
- The dataset has **517 observations and 13 columns** with no missing values and 4 exact duplicate rows.
- It is the well-known **Montesinho Natural Park, Portugal** forest-fire dataset, covering **2000–2003**, with `area` as burned area in hectares and FWI variables (`FFMC`, `DMC`, `DC`, `ISI`).
- This dataset is valuable for understanding **feature concepts and fire-weather relationships**, but it should **not be merged as empirical historical Kalimantan fire data**. Its geography and time period are different.
- The burned-area target is extremely skewed and contains 47.8% zero-area observations under the dataset's definition.

---

## 2. NASA FIRMS Variable Reference

| Variable | Meaning | Unit / code | FIRELINE role | Caution |
|---|---|---|---|---|
| `latitude` | Hotspot latitude | degrees | Spatial join / mapping | Needs boundary join for admin names |
| `longitude` | Hotspot longitude | degrees | Spatial join / mapping | Same as above |
| `acq_date` | Satellite acquisition date | YYYY-MM-DD | Temporal analysis / joins | Observation date, not necessarily ignition time |
| `acq_time` | Satellite acquisition time | HHMM UTC | Sub-daily pattern | UTC must be handled consistently |
| `brightness` | Fire-pixel brightness temperature | K | Thermal signal | Nonlinear relation with FRP; saturation/geometry effects matter |
| `bright_t31` | Thermal/background reference field in the FIRMS export | K | Thermal context | Keep provenance; verify exact field semantics against product version |
| `frp` | Fire Radiative Power | MW | **Primary intensity/urgency candidate** | Proxy, not a complete risk measure |
| `confidence` | Detection confidence class | `l/n/h` | Reliability / verification | Not a severity score |
| `daynight` | Day/night observation | `D/N` | Observation context | Do not equate night with “always more accurate” |
| `scan` | Across-scan pixel resolution indicator | pixels / product-specific metric | Geometry/QC | Can affect comparison of FRP across swath |
| `track` | Along-track pixel resolution indicator | pixels / product-specific metric | Geometry/QC | Same |
| `type` | Detection type code | categorical | Product context | Constant `0` in supplied extract |
| `version` | Product/algorithm version | version | Reproducibility | Not a substantive risk predictor |

NASA's VIIRS documentation identifies fire brightness temperatures, background thermal quantities, FRP, confidence classes, day/night flags, and scan/track as core attributes of the active-fire product. FRP is commonly used as a proxy for fire radiative intensity, while confidence is intended to help gauge detection reliability.

---

## 3. NASA FIRMS Detailed Findings

### Finding 1 — Fire activity has a strong seasonal concentration
**Evidence.** July–September accounts for **71.9%** of hotspot detections and **78.7%** of total FRP. September is the strongest hotspot month in several observed periods, but 2024 and 2026 are partial years.

**Interpretation.** FIRELINE should expect operational load to be highly seasonal. This does not prove that season alone causes fires; it establishes a repeatable concentration pattern in the supplied observations.

**FIRELINE implication.** The DSS should support seasonal baselines and rolling activity indicators instead of relying only on a fixed threshold.

**Next action.** Build `daily_hotspot_count`, `daily_total_frp`, 7-day rolling activity, and historical seasonal baselines.

### Finding 2 — FRP is a useful urgency signal, but raw FRP is highly skewed
**Evidence.** Median FRP is **6.14 MW**, the 90th percentile is **22.11 MW**, and the 99th percentile is **70.20 MW**; the maximum is **954.79 MW**.

**Interpretation.** A small number of extreme detections can dominate summary statistics. Therefore, an AI/analytics engine should not treat raw FRP as a normally distributed variable.

**FIRELINE implication.** FRP is appropriate for ranking hotspot intensity, but it should be combined with exposure and environmental context.

**Next action.** Consider percentile rank, `log1p(FRP)`, and rolling/local aggregates as model features.

### Finding 3 — Detection confidence and fire intensity are distinct dimensions
**Evidence.** The dataset is 93.1% nominal, 3.8% high confidence, and 3.2% low confidence. High-FRP observations are not exclusive to high-confidence records; the supplied extract contains high-FRP low-confidence observations.

**Interpretation.** A low-confidence detection should not automatically be discarded when operational false negatives are costly. It should be treated as lower-confidence evidence and potentially routed to verification.

**FIRELINE implication.** The future priority engine should represent **severity** and **evidence reliability** separately.

**Next action.** Keep confidence as a categorical or calibrated reliability feature and define a verification rule for low-confidence high-FRP hotspots.

### Finding 4 — Spatial hotspots are concentrated, but administrative risk is not yet identifiable from the raw file alone
**Evidence.** A 0.25-degree grid yields 695 occupied cells with clear differences in hotspot count and total FRP.

**Interpretation.** Spatial concentration exists, but assigning a cell to “West Kalimantan” or another province based only on longitude is too coarse.

**FIRELINE implication.** Dashboard labels and operational dispatch need explicit spatial joins to province/district boundaries, land cover, settlements, facilities, and road/access layers.

**Next action.** Perform point-in-polygon spatial joins and create district-level aggregates.

### Finding 5 — Thermal anomaly flags should be preserved, not silently removed
**Evidence.** There are 57 rows with brightness exactly at 207.93 K and 166 rows with `brightness - bright_t31 < 0`, including several high-FRP observations.

**Interpretation.** These cases require product-level QA. They may reflect retrieval/saturation/field-specific encoding or other product behavior; they are not safe to label as ordinary fires or errors without validation.

**Next action.** Add QC flags, preserve the raw rows, and verify against the product guide/source export before any filtering rule is introduced.

---

## 4. Pontianak Weather Findings

| Variable | Observed summary | Potential wildfire relevance | Main limitation |
|---|---|---|---|
| `TAVG` | Mean 27.68°C; range 24–31°C | Higher temperature can reflect drier/hotter conditions and may interact with humidity | Station-specific |
| `RH_AVG` | Mean 82.64%; range 65–96% | Lower RH generally indicates drier air; candidate environmental context | Station-specific |
| `RR` | Mean 12.83 mm among valid records; median 5.5 mm; 26.2% missing | Recent rainfall can reduce fuel dryness; rainfall accumulation/deficit is potentially useful | High missingness |
| `date` | 2021–2024 daily coverage | Required for temporal joins | Must align with FIRMS dates |

The strongest immediate DS action is **not** to impute all missing rainfall values automatically. Because 26.2% of `RR` is missing, rainfall-derived features should carry a missingness indicator or be computed only where valid, and a more spatially representative weather source should be considered for Kalimantan-wide modeling.

---

## 5. Forest Fire Dataset Findings

The Forest Fire dataset is from **Montesinho Natural Park in northeastern Portugal**, not Kalimantan, and contains 517 records from 2000–2003. Its variables are useful as a **feature vocabulary** but not as direct historical evidence for the FIRELINE geography.

| Variable | Meaning | How it can inform FIRELINE |
|---|---|---|
| `X`, `Y` | Grid coordinates in Montesinho | Demonstrates spatial fire context; not reusable as Kalimantan coordinates |
| `month`, `day` | Calendar context | Supports temporal feature ideas |
| `FFMC` | Fine Fuel Moisture Code | Conceptually represents moisture of fine fuels |
| `DMC` | Duff Moisture Code | Represents moisture/drying in surface organic material |
| `DC` | Drought Code | Captures longer-term drying/drought effect |
| `ISI` | Initial Spread Index | Represents initial fire spread potential |
| `temp` | Temperature | Environmental candidate |
| `RH` | Relative humidity | Environmental candidate |
| `wind` | Wind speed | Potential spread/context feature |
| `rain` | Rainfall | Moisture/wetness context |
| `area` | Burned area (ha) | Historical outcome variable in Portugal; not a Kalimantan target |

The main methodological value is that these variables suggest a future FIRELINE feature family: **recent rainfall + humidity + temperature + wind + longer-term dryness indicators**. The actual coefficients/relationships must be recalibrated using geographically relevant Kalimantan data.

---

## 6. Integration Blueprint for FIRELINE

### Proposed analytical unit
Use a **hotspot-event / hotspot-day** representation anchored on NASA FIRMS. Then enrich each event or spatial-temporal aggregate with context.

### Suggested integration flow

`NASA FIRMS hotspot`
→ spatial join to administrative/land layers
→ temporal + spatial association with weather
→ exposure join to population/schools
→ historical recurrence features
→ risk/context features
→ priority ranking

### Data integration readiness

| Dataset | Spatial compatibility | Temporal compatibility | Recommended treatment |
|---|---|---|---|
| NASA FIRMS | Native lat/long | Main current period | Core event table |
| Pontianak Weather | Single-station | Overlap with FIRMS only in 2024 | Use as local reference / integration prototype, not full-Kalimantan weather |
| Forest Fire | Local 9x9 grid in Portugal | 2000–2003 | Method/reference only; replace with Kalimantan historical data for empirical modeling |
| Population/School | Requires spatial join | Usually annual/static | Exposure layer |
| Peatland/Land cover | Requires spatial join | Static or periodically updated | Hazard/vulnerability context |

---

## 7. Feature Engineering Recommendations

### High priority
1. **FRP percentile / log(FRP)** — stabilizes the long tail and supports relative urgency.
2. **Daily hotspot count** — captures operational load.
3. **Daily total FRP** — captures aggregate fire energy.
4. **7-day rolling hotspot count / FRP** — captures persistence.
5. **Historical hotspot frequency by spatial cell** — captures recurrence.
6. **Confidence reliability feature** — separate from intensity.
7. **Population exposure count within a buffer** — connects hazard to impact.
8. **Distance to schools / critical facilities** — operationally interpretable exposure feature.
9. **Rainfall accumulation / dry-day sequence** — once an appropriate weather layer is available.

### Do not implement yet
- A hard “critical FRP” rule presented as universally dangerous.
- A province label inferred only from longitude.
- Direct model training on the Portugal Forest Fire dataset and presentation of its results as Kalimantan risk evidence.
- Global deletion of low-confidence detections.

---

## 8. Immediate Next Steps for the Three-Person DS Team

### Step 1 — Standardize the NASA event table
Create stable fields for `date`, `hour_utc`, `frp_log`, `confidence_level`, spatial grid, and QC flags.

### Step 2 — Build the weather join prototype
Use date + nearest weather station / spatial rule. Start with Pontianak as a **prototype region**, not as a universal Kalimantan weather representation.

### Step 3 — Replace the Portugal history for production modeling
Search for geographically relevant Kalimantan/Indonesia historical fire data. The Forest Fire dataset can remain in the project as a methodological reference for FWI-style variables.

### Step 4 — Add exposure
Point-in-polygon / radius-based joins for population and schools. This is the point where FIRELINE can move from “fire severity” to **response priority**.

### Step 5 — Only then test risk models
Begin with an interpretable baseline (weighted scoring / calibrated risk index) before moving to ML. The final model should explain why a hotspot moved up or down the dispatch queue.

---

## 9. Final Finding: What We Know Now

The data exploration changes the FIRELINE design in an important way:

> **FIRELINE should not be framed as a hotspot detector. It should be framed as a context-enrichment and prioritization system.**

NASA FIRMS already gives the system a strong current fire-signal backbone. The analytical opportunity lies in adding context around each hotspot: **environmental conditions, historical recurrence, human exposure, critical facilities, and later operational accessibility**.

The most important technical warning is that the supplied Forest Fire dataset is geographically unrelated to Kalimantan. Its FWI/weather variables can inspire features, but its empirical relationships should not be transferred directly to FIRELINE without geographically relevant validation.

---

## References / Method Notes

[1] NASA Earthdata, *Collection 2 Visible Infrared Imaging Radiometer Suite (VIIRS) 375 m Active Fire User Guide* — product fields for fire brightness temperature, background temperatures, FRP, confidence, and day/night.

[2] NASA Earthdata FIRMS FAQ / Forum — notes on VIIRS confidence classes, FRP as a fire-intensity proxy, and scan/track geometry.

[3] UCI Machine Learning Repository, *Forest Fires* dataset — Montesinho Natural Park, Portugal; 517 instances; variables and burned-area target.
