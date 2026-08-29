# Fireline Hotspot Kalimantan - EDA Profiling Report
**Dataset:** `fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv`  
**Observation Period:** 01 August 2024 to 31 May 2026  
**Platform Reference:** FIRELINE Decision Support System - COMPFEST 18  

---

## 1. Basic Profile

| Metric | Value |
|---|---|
| Total Records | 61,583 rows |
| Total Columns | 15 columns |
| Memory Usage | 20.26 MB |
| Duplicate Rows | 0 rows |

---

## 2. Column Data Types and Completeness

| Column Name | Data Type | Missing Count | Missing Percentage | Information Status |
|---|---|---|---|---|
| `latitude` | float64 | 0 | 0.00% | Active (Spatial coordinate) |
| `longitude` | float64 | 0 | 0.00% | Active (Spatial coordinate) |
| `brightness` | float64 | 0 | 0.00% | Active (Channel 4 brightness temp, Kelvin) |
| `scan` | float64 | 0 | 0.00% | Active (Spatial scan resolution) |
| `track` | float64 | 0 | 0.00% | Active (Spatial track resolution) |
| `acq_date` | object | 0 | 0.00% | Active (Date string YYYY-MM-DD) |
| `acq_time` | int64 | 0 | 0.00% | Active (Time integer HHMM) |
| `satellite` | object | 0 | 0.00% | Constant (`N20`) -> Dropped in preprocessing |
| `instrument` | object | 0 | 0.00% | Constant (`VIIRS`) -> Dropped in preprocessing |
| `confidence` | object | 0 | 0.00% | Active (Categorical: l, n, h) |
| `version` | int64 | 0 | 0.00% | Constant (`2`) -> Dropped in preprocessing |
| `bright_t31` | float64 | 0 | 0.00% | Active (Channel I-5 brightness temp, Kelvin) |
| `frp` | float64 | 0 | 0.00% | Active (Fire Radiative Power, MW) |
| `daynight` | object | 0 | 0.00% | Active (D = Day, N = Night) |
| `type` | int64 | 0 | 0.00% | Constant (`0`) -> Dropped in preprocessing |

---

## 3. Constant and Zero-Variance Columns

The following columns exhibit zero variance across all 61,583 records and provide no discriminatory value for modeling or prioritization:

* `satellite`: 100.0% populated with `N20` (NOAA-20)
* `instrument`: 100.0% populated with `VIIRS`
* `version`: 100.0% populated with `2`
* `type`: 100.0% populated with `0` (Presumed vegetation fire)

**Decision:** Dropped during preprocessing to streamline dataset memory and eliminate redundant schema.

---

## 4. Categorical Distribution

### 4.1 Confidence Level
* `Nominal (n)`: 57,315 records (93.1%)
* `High (h)`: 2,320 records (3.8%)
* `Low (l)`: 1,948 records (3.2%)

### 4.2 Detection Time Period
* `Daytime (D)`: 54,988 records (89.3%)
* `Nighttime (N)`: 6,595 records (10.7%)

---

## 5. Numeric Distribution Summary

| Column | Min | 25% (Q1) | Median | Mean | 75% (Q3) | Max | Std Dev | IQR |
|---|---|---|---|---|---|---|---|---|
| `latitude` | -4.1735 | -1.0529 | -0.0168 | -0.1711 | 0.6964 | 4.3510 | 1.4369 | 1.7493 |
| `longitude` | 108.6836 | 110.4147 | 111.5694 | 112.6655 | 115.2384 | 119.4994 | 2.8446 | 4.8237 |
| `brightness` (K) | 207.9300 | 331.2900 | 335.8600 | 335.8698 | 342.2200 | 367.0000 | 13.6766 | 10.9300 |
| `bright_t31` (K) | 241.4800 | 289.3900 | 292.9900 | 292.1313 | 296.2700 | 361.8100 | 6.5165 | 6.8800 |
| `frp` (MW) | 0.0900 | 3.5800 | 6.1400 | 10.5699 | 11.4300 | 954.7900 | 17.4237 | 7.8500 |
| `scan` | 0.3200 | 0.3900 | 0.4400 | 0.4598 | 0.5100 | 0.8000 | 0.0872 | 0.1200 |
| `track` | 0.3600 | 0.3900 | 0.4600 | 0.4837 | 0.5600 | 0.7800 | 0.1091 | 0.1700 |
| `acq_time` | 0434 | 0538 | 0605 | 0703 | 0630 | 1901 | 370.17 | 92.00 |

---

## 6. Temporal and Geographic Coverage

### 6.1 Temporal Bounds
* **Start Date:** 01 August 2024
* **End Date:** 31 May 2026
* **Total Duration:** 668 calendar days
* **Active Fire Dates:** 629 days with detected hotspots
* **Daily Average:** 97.9 hotspots per active day

### 6.2 Spatial Bounds (Kalimantan Bounding Box)
* **Latitude Range:** -4.1735 to 4.3510 degrees
* **Longitude Range:** 108.6836 to 119.4994 degrees

---

## 7. FRP Outlier and Extreme Event Analysis

* **IQR Upper Fence (Q3 + 1.5 * IQR):** 23.20 MW
* **Total Statistical Outliers:** 5,691 records (9.2%)
* **FRP > 50 MW (Severe):** 1,344 records (2.18%)
* **FRP > 100 MW (Extreme Tier 1):** 285 records (0.46%)
* **FRP > 200 MW (High Magnitude):** 66 records (0.11%)
* **FRP > 500 MW (Mega-Fire):** 6 records (0.01%)
* **Maximum Observed FRP:** 954.79 MW

### Top 10 Extreme FRP Events

| Date | Latitude | Longitude | FRP (MW) | Confidence | Region Context |
|---|---|---|---|---|---|
| 2025-03-08 | -2.6167 | 114.7098 | 954.79 | Low | Kalimantan Selatan |
| 2025-03-08 | -2.8690 | 114.7976 | 825.56 | Low | Kalimantan Selatan |
| 2026-03-05 | -1.4904 | 110.1422 | 652.45 | Low | Kalimantan Barat |
| 2024-09-17 | -0.0069 | 116.8098 | 550.26 | Nominal | Kalimantan Timur |
| 2024-09-17 | -0.0076 | 116.8051 | 550.26 | Low | Kalimantan Timur |
| 2024-09-17 | -0.0030 | 116.8045 | 550.26 | Low | Kalimantan Timur |
| 2025-03-08 | -2.8696 | 114.7938 | 470.10 | Low | Kalimantan Selatan |
| 2025-03-08 | -2.8702 | 114.7901 | 470.10 | Low | Kalimantan Selatan |
| 2025-10-02 | -1.1307 | 113.8820 | 459.70 | Low | Kalimantan Tengah |
| 2025-03-08 | -2.9850 | 114.8184 | 445.57 | Low | Kalimantan Selatan |

---

## 8. Monthly Seasonality Distribution

* **Peak Month:** September 2024 with 16,911 hotspots
* **Trough Month:** January 2025 with 124 hotspots
* **Seasonality Ratio:** 136.4x disparity between peak dry season and peak wet season

---

## 9. Linear Correlation Matrix (Pearson)

| Metric | brightness | bright_t31 | frp | scan | track |
|---|---|---|---|---|---|
| `brightness` | 1.000 | 0.249 | 0.132 | -0.048 | 0.186 |
| `bright_t31` | 0.249 | 1.000 | 0.193 | -0.148 | -0.339 |
| `frp` | 0.132 | 0.193 | 1.000 | 0.065 | 0.005 |
| `scan` | -0.048 | -0.148 | 0.065 | 1.000 | 0.418 |
| `track` | 0.186 | -0.339 | 0.005 | 0.418 | 1.000 |

---

## 10. Key Insights for FIRELINE Platform

1. **Data Completeness:** Zero missing values across 61,583 rows. No spatial or temporal imputation required.
2. **Schema Optimization:** Four constant columns (`satellite`, `instrument`, `version`, `type`) dropped with zero loss of information.
3. **Severe Distribution Asymmetry:** Median FRP is 6.14 MW while max reaches 954.79 MW. Standard means are biased by extremes; log-transformed values (`frp_log`) and threshold categorization are necessary for balanced risk modeling.
4. **Sensor Confidence Dynamics:** 93.1% of detections are classified as nominal confidence. However, extreme mega-fire events (FRP > 500 MW) frequently carry low sensor confidence flags due to smoke occlusion or saturation, confirming that confidence must be weighted rather than used as a hard filter.
5. **Monitoring Window Bias:** 89.3% of satellite detections occur during daytime overpasses. Nighttime fire progression represents an operational blind spot requiring predictive extrapolation.
6. **Critical Response Tiering:** 285 events with FRP exceeding 100 MW constitute priority Tier 1 emergency suppression targets.
7. **Predictable Seasonality:** Fire incidence is concentrated between June and October (83.4% of volume), providing clear operational schedules for resource pre-positioning.
8. **Spatial Recurrence as Vulnerability:** Chronic fire zones with repeated ignitions on identical 0.5-degree grid cells indicate recurring human or ecological triggers.
9. **Temperature Differential Signal:** `temp_delta_K` (brightness minus bright_t31) provides an independent measure of fire intensity relative to background ambient ground heat.
10. **Sensor Geometry Invariance:** Scan and track dimensions show minimal correlation with FRP, confirming that reported fire radiative power is an environmental signal rather than an optical artifact.
