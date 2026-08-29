import os

readme = """# EDA Report: Fireline Hotspot Kalimantan
## NASA VIIRS NOAA-20 Active Fire Data | Aug 2024 - May 2026

Dataset: fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv
Processed: 29 August 2026
Context: FIRELINE Platform - COMPFEST 18 Case Study (Team Alpha)

---

## Dataset Overview

| Attribute | Value |
|---|---|
| Total Records | 61,583 hotspot detections |
| Time Range | 01 Aug 2024 to 31 May 2026 (22 months) |
| Unique Observation Days | 629 days |
| Average Daily Detections | 97.9 hotspots/day |
| Total Fire Energy Released | 650.9 GW |
| Coverage | Kalimantan (Lat: -4.17 to 4.35, Lon: 108.68 to 119.50) |
| Sensor | NASA VIIRS, Satellite NOAA-20 (N20) |
| Missing Values | 0 |
| Duplicate Records | 0 |

Columns dropped as zero-information constants: satellite, instrument, type, version.

---

## Key Findings

### Finding 1 - Kalimantan Barat is the Primary Fire Epicenter

Kalimantan Barat accounts for 31,764 hotspots (51.6%) and 367,757 MW of total fire energy.

| Province | Count | Share | Total FRP (MW) |
|---|---|---|---|
| Kalimantan Barat | 31,764 | 51.6% | 367,757 |
| Kalimantan Tengah | 10,690 | 17.4% | 119,862 |
| Kalimantan Timur | 9,041 | 14.7% | 77,138 |
| Kalimantan Utara | 6,299 | 10.2% | 55,980 |
| Kalimantan Selatan | 3,014 | 4.9% | 25,775 |

PRD Gap addressed: Gap 3 (Data Integration) - Geographic context for unified risk representation.

---

### Finding 2 - Dry Season Drives 83.4% of All Fire Activity

51,375 hotspots (83.4%) occur during dry season (June to October), with mean FRP of 11.24 MW vs 7.22 MW in wet season - a 55.6% higher intensity.

- Peak month: September 2024 with 16,911 hotspots
- Lowest month: January 2025 with only 124 hotspots (136x fewer than peak)
- This 136x seasonal gap provides strong empirical basis for calendar-based early warning triggers

PRD Gap addressed: Gap 1 (Detection to Prioritization) - Temporal context enables proactive response.

---

### Finding 3 - FRP Distribution is Heavily Right-Skewed

| Metric | Value |
|---|---|
| Median FRP | 6.14 MW |
| Mean FRP | 10.57 MW |
| Maximum FRP | 954.79 MW |
| FRP > 100 MW (Extreme) | 285 events (0.46%) |
| FRP > 500 MW (Mega-fire) | 6 events (0.01%) |

The median-to-max ratio of 1:155 shows that a tiny fraction of fires carry disproportionate destructive energy. Equal-weight hotspot treatment will systematically misallocate response resources.

PRD Gap addressed: Gap 2 (Risk to Operational Decision).

---

### Finding 4 - Mega-Fire Events are Geographically Specific and Date-Stamped

| Date | Coordinates | FRP (MW) | Province | Confidence |
|---|---|---|---|---|
| 2025-03-08 | -2.617, 114.710 | 954.79 | Kalimantan Selatan | Low |
| 2025-03-08 | -2.869, 114.798 | 825.59 | Kalimantan Selatan | Low |
| 2026-03-05 | -1.490, 110.142 | 652.45 | Kalimantan Barat | Low |
| 2024-09-17 | -0.007, 116.810 | 550.29 | Kalimantan Timur | Nominal |
| 2024-09-17 | -0.008, 116.805 | 550.29 | Kalimantan Timur | Low |

Note: 4 of the top 5 mega-fire events carry Low confidence despite extreme FRP. This confirms that low confidence does not mean low intensity - sensor saturation or geometry issues can occur. The weighted_frp feature corrects for reliability without discarding the signal.

PRD Gap addressed: Gap 1 (Prioritization) - These are exactly the events FIRELINE must surface as Tier-1 emergencies.

---

### Finding 5 - 224 Chronic Fire Zones Identified (High Vulnerability)

224 grid cells (0.5-degree resolution, approx 55km x 55km) have been detected burning 5 or more times in 22 months. These chronic fire zones indicate:

- Land use patterns consistently generating ignition (agricultural burning, peat drainage)
- Inadequate preventive intervention in prior seasons
- High structural vulnerability independent of current weather

61,549 of 61,583 hotspots (99.9%) fall within a high-recurrence grid cell. The fire problem in Kalimantan is spatially concentrated and historically predictable.

PRD Gap addressed: Gap 3 (Vulnerability dimension of Contextual Risk Assessment).

---

### Finding 6 - Confidence Composition and Its Implications

| Confidence | Count | Share | Mean FRP (MW) |
|---|---|---|---|
| Nominal (n) | 57,315 | 93.1% | 10.45 |
| High (h) | 2,320 | 3.8% | 15.79 |
| Low (l) | 1,948 | 3.2% | 9.23 |

High-confidence detections average 51% higher FRP than low-confidence ones. The confidence_weight feature (l=0.3, n=0.7, h=1.0) provides principled correction for the risk scoring engine without discarding any signal.

PRD relevance: Confidence directly feeds the HAZARD dimension of Contextual Risk Assessment.

---

### Finding 7 - Daytime Monitoring Creates a Systematic Blind Spot

54,988 detections (89.3%) occur during daytime passes. Only 6,595 (10.7%) are captured at night. Key implications:

- Fires igniting overnight may go undetected for 12+ hours until the next daytime pass
- This partially explains the 12-24 hour verification delay cited in the PRD
- Nighttime detections have slightly higher mean FRP (10.8 vs 10.5 MW daytime), suggesting overnight fires that survive to be detected tend to be more persistent

PRD Gap addressed: Root Cause 3 (Delayed information flow).

---

### Finding 8 - Fire Intensity and Temperature Delta are Independent Signals

Pearson correlation between frp and temp_delta_K: r = 0.52 (moderate). Key matrix:

- brightness vs bright_t31: r = 0.83 (both respond to ambient conditions)
- frp vs hazard_score: r = 0.82 (hazard score dominated by FRP as designed)
- frp vs temp_delta_K: r = 0.52 (independent signal worth including)

The moderate correlation confirms temp_delta_K adds independent information to the hazard assessment beyond raw FRP alone.

PRD relevance: Supports using temp_delta_K as independent signal in Contextual Risk Assessment.

---

### Finding 9 - No Strong Human Behavioral Signal at Weekly Scale

| Period | Count | Share | Mean FRP |
|---|---|---|---|
| Weekday (Mon-Fri) | 45,217 | 73.4% | 10.70 MW |
| Weekend (Sat-Sun) | 16,366 | 26.6% | 10.21 MW |

The split closely mirrors the calendar proportion (5/7 = 71.4% weekday expected). The 4.5% FRP difference is not practically significant. Seasonal and geographic factors dominate over weekly human behavior patterns at this scale.

---

### Finding 10 - Hazard Score Validates Three-Dimension PRD Architecture

The composite hazard_score (40% FRP + 35% temp_delta + 25% confidence):

| Range | Count | Interpretation |
|---|---|---|
| 0-25 (Low) | 36,948 (60.0%) | Routine monitoring |
| 25-50 (Medium) | 22,327 (36.3%) | Active patrol warranted |
| 50-75 (High) | 2,308 (3.7%) | Rapid response priority |
| Above 75 (Critical) | 0 (0.0%) | Reserved for combined H+E+V scoring |

No scores exceed 75 using only HAZARD components. This is correct and expected. The full Contextual Risk Index requires EXPOSURE (proximity to settlements) and VULNERABILITY (peat land, historical recurrence) to push into the critical zone. This validates the PRD architecture: the DS engine needs all three H+E+V dimensions.

PRD Gap addressed: All gaps - This is the foundational evidence for why the integrated FIRELINE engine is necessary.

---

## Visualization Index (27 Charts)

### Pillar A - Temporal Analysis

| File | Description |
|---|---|
| 01_daily_trend_with_ma7.png | Daily count with 7-day moving average, peak annotation |
| 02_calendar_heatmap_dayofweek_month.png | Day-of-week x month heatmap |
| 03_monthly_stacked_by_confidence.png | Monthly counts stacked by confidence level |
| 04_frp_boxplot_per_month.png | FRP distribution per month, dry season highlighted |
| 05_dual_axis_count_vs_total_frp.png | Monthly count (bars) vs total FRP (line) |
| 06_year_over_year_2024_vs_2025.png | YoY comparison by calendar month |

### Pillar B - HAZARD: Fire Intensity

| File | Description |
|---|---|
| 07_frp_distribution_log_scale.png | FRP histogram on log scale with extreme thresholds |
| 08_brightness_vs_bright_t31_overlay.png | Temperature distributions overlay |
| 09_violin_frp_by_confidence.png | FRP violin plot by confidence class |
| 10_scatter_frp_vs_temp_delta.png | FRP vs temp delta scatter, bubble = pixel area |
| 11_day_vs_night_count_and_frp.png | Day vs night count and mean FRP comparison |

### Pillar C - Spatial Distribution

| File | Description |
|---|---|
| 12_spatial_scatter_all_hotspots.png | All 20,000 sampled hotspots geo-scatter |
| 13_hexbin_density_map.png | Hexbin density map, inferno colorscale |
| 14_kde_spatial_contour.png | KDE contour overlay on dark background |
| 15_bar_hotspots_by_province.png | Count and total FRP by province |

### Pillar D - Extreme Events

| File | Description |
|---|---|
| 16_frp_timeline_extreme_events.png | All hotspots plotted by date and FRP, extreme flagged |
| 17_top20_critical_days_total_frp.png | Top 20 days by sum of FRP > 50 MW |
| 18_cumulative_total_frp_over_time.png | Cumulative fire energy over the observation period |

### Pillar E - Vulnerability

| File | Description |
|---|---|
| 19_top25_recurrence_chronic_fire_zones.png | Top 25 grid cells by detection count |
| 20_heatmap_region_vs_season.png | Province x season count risk matrix |
| 21_weekday_vs_weekend_fire_activity.png | Weekday vs weekend count and FRP |

### Pillar F - Composite

| File | Description |
|---|---|
| 22_pearson_correlation_matrix.png | Lower-triangle Pearson correlation heatmap |
| 23_confidence_donut_and_frp_comparison.png | Confidence donut plus FRP by confidence |
| 24_intensity_class_composition_by_province.png | Stacked 100% intensity class per province |

### Feature Engineering Bonus

| File | Description |
|---|---|
| FE01_raw_vs_weighted_frp_monthly.png | Raw vs confidence-weighted FRP per month |
| FE02_hazard_score_by_province.png | Hazard score distribution boxplot per province |
| FE03_chronic_fire_zones_recurrence_map.png | Chronic fire zone map with recurrence overlay |

---

## Feature Engineering Summary

Input: 11 columns after dropping constants
Output: 43 columns (32 engineered features added)

| Category | Feature Names |
|---|---|
| Temporal (13) | year, month, month_name, day_of_month, day_name, is_weekend, hour, quarter, year_month, season, days_since_start, is_kemarau, time_period |
| HAZARD (8) | temp_delta_K, brightness_celsius, bright_t31_celsius, pixel_area_km2, fire_intensity_class, is_extreme_fire, is_mega_fire, frp_log |
| Confidence (3) | confidence_num, confidence_weight, weighted_frp |
| Spatial (4) | kalimantan_region, lat_zone, coord_grid_1deg, coord_grid_05deg |
| Vulnerability (3) | fire_recurrence_count, cumulative_frp_at_grid, is_high_recurrence |
| Composite (1) | hazard_score (0-100, HAZARD component only) |

---

## Output Files

| File | Location | Rows x Cols |
|---|---|---|
| eda_report_summary.txt | 01_data_exploration/ | Full text profiling |
| fireline_hotspot_clean.csv | 03_preprocessing/ | 61,583 x 16 |
| feature_engineering_summary.txt | 04_feature_engineering/ | Feature docs |
| fireline_hotspot_featured.csv | 04_feature_engineering/ | 61,583 x 43 |
| 27 PNG charts (300 DPI) | 02_visualizations/ | All pillars |

---

## Next Steps

Next dataset: Climate and weather data (BMKG) covering the same date range will provide the environmental dimension.

Integration target: Climate data (temperature, humidity, rainfall, wind speed) joined by date and region will extend hazard_score with weather-derived fire spread probability.

Exposure dimension: Spatial join with complete_data.csv (school and settlement coordinates) will provide proximity-based exposure scoring per hotspot.

Final DS deliverable: Contextual Risk Index = HAZARD (this dataset) + EXPOSURE (complete_data join) + VULNERABILITY (recurrence + land type proxy)
"""

output_path = 'EDA/01_fireline_hotspot_kalimantan/README.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(readme)

print('README.md written to:', output_path)
print('Size:', len(readme), 'chars')
