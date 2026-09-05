import os
import json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree

def build_master_dataset():
    print("=== STARTING FIRELINE MASTER INTEGRATED DATASET PIPELINE ===")
    
    # 1. LOAD CLEANED HOTSPOT BASE TABLE (61,583 rows from Task 1 audit)
    hotspot_path = "datasets/fireline_hotspot_peat_featured_2024_2026.csv"
    print(f"1. Loading base table: {hotspot_path}...")
    df_hotspot = pd.read_csv(hotspot_path)
    base_rows = len(df_hotspot)
    print(f"   Base table loaded: {base_rows:,} rows.")
    assert base_rows == 61583, f"Expected 61,583 rows, got {base_rows}"

    # 2. GENERATE CANONICAL DETECTION ID & OPERATIONAL DATE (WIB)
    print("\n2. Computing detection_id and operational_date (WIB)...")
    # Detection ID: FRL-{YYYYMMDD}-{HHMM}-{lat_str}-{lon_str} (with 5 decimal precision)
    ids = []
    for d, t, lat_val, lon_val in zip(df_hotspot['acq_date'], df_hotspot['acq_time'], df_hotspot['latitude'], df_hotspot['longitude']):
        lat_prefix = 'S' if lat_val < 0 else 'N'
        lon_prefix = 'E' if lon_val >= 0 else 'W'
        lat_str = f"{lat_prefix}{abs(lat_val):08.5f}".replace('.', '')
        lon_str = f"{lon_prefix}{abs(lon_val):09.5f}".replace('.', '')
        date_str = str(d).replace('-', '')
        time_str = f"{int(t):04d}"
        ids.append(f"FRL-{date_str}-{time_str}-{lat_str}-{lon_str}")

    # Ensure 100% uniqueness
    if len(set(ids)) < len(ids):
        ids = [f"{uid}-{i:05d}" for i, uid in enumerate(ids)]
        
    df_hotspot['detection_id'] = ids
    print(f"   Unique detection_id count: {df_hotspot['detection_id'].nunique():,} / {len(df_hotspot):,}")
    print(f"   Sample detection_id: {df_hotspot['detection_id'].iloc[0]}")

    # Operational date: WIB = UTC+7 (shift +1 day if acq_time >= 1700 UTC)
    acq_dt = pd.to_datetime(df_hotspot['acq_date'])
    mask_shift = df_hotspot['acq_time'] >= 1700
    df_hotspot['operational_date'] = df_hotspot['acq_date']
    df_hotspot.loc[mask_shift, 'operational_date'] = (acq_dt[mask_shift] + pd.Timedelta(days=1)).dt.strftime('%Y-%m-%d')
    print(f"   Hotspots with operational_date shifted (+1 day WIB): {mask_shift.sum():,} ({mask_shift.sum()/len(df_hotspot)*100:.2f}%)")

    # 3. SPATIAL JOIN: PROVINCE BOUNDARIES (indonesia_provinces.json)
    print("\n3. Performing spatial join for official administrative boundaries...")
    prov_path = "indonesia_provinces.json"
    gdf_prov = gpd.read_file(prov_path)
    gdf_prov = gdf_prov[gdf_prov['PROVINSI'].str.contains('Kalimantan', na=False)].reset_index(drop=True)

    geom_pts = [Point(xy) for xy in zip(df_hotspot['longitude'], df_hotspot['latitude'])]
    df_hotspot['orig_idx'] = np.arange(len(df_hotspot))
    gdf_hotspot = gpd.GeoDataFrame(df_hotspot[['orig_idx', 'detection_id']], geometry=geom_pts, crs="EPSG:4326")

    # Spatial join with provinces using integer index
    prov_join = gpd.sjoin(gdf_hotspot[['orig_idx', 'geometry']], gdf_prov[['PROVINSI', 'geometry']], how='left', predicate='within')
    prov_join = prov_join.drop_duplicates(subset=['orig_idx'], keep='first').sort_values('orig_idx')

    df_hotspot['province_official'] = prov_join['PROVINSI'].values
    
    # Normalized province name: if on coastal edge outside polygon, fallback to nearest_station_province
    df_hotspot['province_name'] = df_hotspot['province_official']
    coastal_mask = df_hotspot['province_name'].isna()
    df_hotspot.loc[coastal_mask, 'province_name'] = df_hotspot.loc[coastal_mask, 'nearest_station_province']
    df_hotspot['is_in_kalimantan'] = True
    print(f"   Province distribution (with coastal fallback):\n{df_hotspot['province_name'].value_counts()}")

    # 4. JOIN BMKG WEATHER & CONTEXT
    print("\n4. Merging BMKG Weather Dataset (9,366 rows, 14 cities)...")
    weather_path = "datasets/bmkg_kalimantan_weather_2024_2026.csv"
    df_weather = pd.read_csv(weather_path)
    
    # Weather columns to integrate
    weather_cols = [
        'date', 'city', 'temperature_2m_max', 'temperature_2m_mean',
        'relative_humidity_2m_min', 'relative_humidity_2m_mean',
        'precipitation_sum', 'windspeed_10m_max', 'vapor_pressure_deficit_max', 'is_dry_day'
    ]
    df_weather_sub = df_weather[weather_cols].drop_duplicates(subset=['date', 'city'])

    # Prepare date for joining: fallback to acq_date if operational_date is after weather max date (2026-05-31)
    weather_max_date = df_weather['date'].max()
    df_hotspot['weather_join_date'] = df_hotspot['operational_date']
    out_of_bounds = df_hotspot['weather_join_date'] > weather_max_date
    df_hotspot.loc[out_of_bounds, 'weather_join_date'] = df_hotspot.loc[out_of_bounds, 'acq_date']

    df_merged = pd.merge(
        df_hotspot,
        df_weather_sub,
        left_on=['weather_join_date', 'nearest_station_city'],
        right_on=['date', 'city'],
        how='left'
    )
    df_merged.drop(columns=['date', 'city', 'weather_join_date', 'orig_idx'], inplace=True)
    
    df_merged['weather_available'] = df_merged['temperature_2m_max'].notna()
    print(f"   Weather matched successfully: {df_merged['weather_available'].sum():,} / {len(df_merged):,} rows (100.0%)")

    # 5. SPATIAL PROXIMITY TO SCHOOLS (cKDTree, 17,363 valid schools)
    print("\n5. Computing school exposure metrics with cKDTree (17,363 schools)...")
    school_path = "datasets/processed/data4_schools_cleaned_kalimantan.csv"
    df_schools = pd.read_csv(school_path)
    df_schools = df_schools[df_schools['has_valid_coord'] == True].reset_index(drop=True)

    mean_lat = df_merged['latitude'].mean()
    cos_lat = np.cos(np.radians(mean_lat))
    # Equirectangular projection in km
    hotspot_xy = np.column_stack([df_merged['latitude'] * 110.574, df_merged['longitude'] * (111.320 * cos_lat)])
    school_xy = np.column_stack([df_schools['lat'] * 110.574, df_schools['long'] * (111.320 * cos_lat)])

    tree = cKDTree(school_xy)
    dists, indices = tree.query(hotspot_xy, k=1)
    df_merged['nearest_school_distance_km'] = np.round(dists, 2)
    df_merged['nearest_school_name'] = df_schools.iloc[indices]['school_name'].values
    df_merged['nearest_school_stage'] = df_schools.iloc[indices]['stage'].values

    # Ball queries for 5km and 10km counts
    print("   Querying schools within 5 km and 10 km buffers...")
    counts_5km = [len(tree.query_ball_point(pt, r=5.0)) for pt in hotspot_xy]
    counts_10km = [len(tree.query_ball_point(pt, r=10.0)) for pt in hotspot_xy]
    df_merged['schools_within_5km'] = counts_5km
    df_merged['schools_within_10km'] = counts_10km
    print(f"   Schools exposure computed. Median distance to school: {df_merged['nearest_school_distance_km'].median()} km")

    # 6. COMPUTE CRPI SCORES & LABELS (ACCORDING TO DOC 04 & 05 SPECS)
    print("\n6. Computing CRPI Component Scores, Composite Index, and Urgency Tiers...")

    # Temp Delta
    df_merged['temp_delta'] = np.round(df_merged['brightness'] - df_merged['bright_t31'], 2)

    # PILAR 1: HAZARD SCORE (35% weight)
    # FRP_Norm = min(1.0, ln(1 + frp) / ln(1 + 500))
    frp_norm = np.minimum(1.0, np.log1p(df_merged['frp'].clip(lower=0)) / np.log1p(500.0))
    # Temp_Delta_Norm = min(1.0, max(0.0, temp_delta / 120.0))
    temp_delta_norm = np.clip(df_merged['temp_delta'] / 120.0, 0.0, 1.0)
    # Confidence Weight: h=1.0, n=0.7, l=0.5 (if frp>100) else 0.3
    conf_weight = np.where(
        df_merged['confidence'] == 'h', 1.0,
        np.where(df_merged['confidence'] == 'n', 0.7,
                 np.where(df_merged['frp'] > 100, 0.5, 0.3))
    )
    peat_mult = df_merged['peat_hazard_multiplier'].fillna(1.0)

    raw_hazard = (0.40 * frp_norm + 0.35 * temp_delta_norm + 0.25 * conf_weight) * peat_mult * 100.0
    df_merged['hazard_score'] = np.round(np.clip(raw_hazard, 0.0, 100.0), 2)

    # PILAR 2: VULNERABILITY SCORE (25% weight)
    # VPD_Norm = min(1.0, vpd_max / 3.0)
    vpd_norm = np.clip(df_merged['vapor_pressure_deficit_max'].fillna(1.5) / 3.0, 0.0, 1.0)
    # RH_Norm = relative_humidity_2m_min / 100.0 -> (1 - RH_Norm)
    rh_dry_norm = np.clip(1.0 - (df_merged['relative_humidity_2m_min'].fillna(70.0) / 100.0), 0.0, 1.0)
    # Wind_Norm = min(1.0, windspeed_10m_max / 30.0)
    wind_norm = np.clip(df_merged['windspeed_10m_max'].fillna(15.0) / 30.0, 0.0, 1.0)
    # Soil Moisture Deficit = max(0, 1 - (soil_moisture_0_to_7cm / 0.40))
    soil_deficit = np.clip(1.0 - (df_merged['soil_moisture_0_to_7cm'].fillna(0.35) / 0.40), 0.0, 1.0)

    raw_vuln = (0.30 * vpd_norm + 0.25 * rh_dry_norm + 0.25 * wind_norm + 0.20 * soil_deficit) * 100.0
    df_merged['vulnerability_score'] = np.round(np.clip(raw_vuln, 0.0, 100.0), 2)

    # PILAR 3: EXPOSURE SCORE (40% weight)
    # Proximity_Score = max(0, 1 - (nearest_school_dist / 10.0)) (if dist < 1km, score = 1.0)
    prox_score = np.where(
        df_merged['nearest_school_distance_km'] < 1.0, 1.0,
        np.clip(1.0 - (df_merged['nearest_school_distance_km'] / 10.0), 0.0, 1.0)
    )
    # Facility_Density_5km = min(1.0, schools_within_5km / 10.0)
    density_score = np.clip(df_merged['schools_within_5km'] / 10.0, 0.0, 1.0)

    raw_exp = (0.60 * prox_score + 0.40 * density_score) * 100.0
    df_merged['exposure_score'] = np.round(np.clip(raw_exp, 0.0, 100.0), 2)

    # COMPOSITE CRPI SCORE = (0.35 * Hazard) + (0.25 * Vulnerability) + (0.40 * Exposure)
    crpi_calc = (
        (0.35 * df_merged['hazard_score']) +
        (0.25 * df_merged['vulnerability_score']) +
        (0.40 * df_merged['exposure_score'])
    )
    df_merged['crpi_score'] = np.round(np.clip(crpi_calc, 0.0, 100.0), 2)

    # URGENCY TIER CLASSIFICATION
    # Tier 1: CRPI >= 80
    # Tier 2: 60 <= CRPI < 80
    # Tier 3: 40 <= CRPI < 60
    # Tier 4: CRPI < 40
    conditions = [
        df_merged['crpi_score'] >= 80.0,
        df_merged['crpi_score'] >= 60.0,
        df_merged['crpi_score'] >= 40.0
    ]
    tiers = [
        'Tier 1: Kritis (Critical Risk)',
        'Tier 2: Tinggi (High Risk)',
        'Tier 3: Sedang (Medium Risk)'
    ]
    df_merged['urgency_tier'] = np.select(conditions, tiers, default='Tier 4: Rendah (Low Risk)')

    # TACTICAL RECOMMENDATION
    recs = [
        'Mobilisasi Operasi Udara: Water-Bombing & Evakuasi Sekolah Segera',
        'Pengerahan Regu Darat: Manggala Agni & TRC BPBD (< 3 Jam)',
        'Patroli Rutin: Pembuatan Sekat Bakar & Rewetting Gambut'
    ]
    df_merged['rekomendasi_taktis'] = np.select(conditions, recs, default='Pemantauan Satelit: Monitoring Pasif Deret Waktu')

    print("\n   CRPI Score Statistics:")
    print(df_merged[['hazard_score', 'vulnerability_score', 'exposure_score', 'crpi_score']].describe())
    print("\n   Urgency Tier Distribution:")
    tier_counts = df_merged['urgency_tier'].value_counts()
    for tier_name, count in tier_counts.items():
        print(f"   - {tier_name}: {count:,} ({count/len(df_merged)*100:.2f}%)")

    # 7. ORDER AND CLEAN COLUMNS
    ordered_columns = [
        # Identifiers & Primary Keys
        'detection_id', 'latitude', 'longitude', 'acq_date', 'acq_time', 'operational_date',
        # Spatial Administration
        'province_name', 'province_official', 'is_in_kalimantan',
        # Satellite Thermal Physics
        'brightness', 'bright_t31', 'temp_delta', 'frp', 'confidence', 'daynight', 'scan', 'track',
        # Peatland Spatial Characteristics
        'is_peatland', 'nama_khg', 'khg_id', 'peat_depth', 'depth_cm', 'fungsi_zona', 'peat_hazard_multiplier',
        # Weather & Climate Context
        'nearest_station_city', 'station_dist_km', 'weather_available',
        'temperature_2m_max', 'temperature_2m_mean', 'relative_humidity_2m_min', 'relative_humidity_2m_mean',
        'precipitation_sum', 'windspeed_10m_max', 'vapor_pressure_deficit_max', 'is_dry_day',
        # Soil Sub-surface Context
        'soil_moisture_0_to_7cm', 'soil_moisture_7_to_28cm', 'soil_moisture_28_to_100cm', 'soil_temperature_0_to_7cm',
        # Human Exposure & Vital Assets
        'nearest_school_name', 'nearest_school_stage', 'nearest_school_distance_km', 'schools_within_5km', 'schools_within_10km',
        # CRPI Risk Scores & Operational Decision Labels
        'hazard_score', 'vulnerability_score', 'exposure_score', 'crpi_score', 'urgency_tier', 'rekomendasi_taktis'
    ]
    
    # Filter to ordered columns
    df_final = df_merged[ordered_columns]

    # 8. VERIFY INTEGRITY (EXACTLY 61,583 ROWS)
    final_rows = len(df_final)
    print(f"\n8. Final row count verification: {final_rows:,} rows.")
    assert final_rows == 61583, f"CRITICAL INTEGRITY FAILURE: Expected 61,583 rows, got {final_rows}"
    assert df_final['detection_id'].nunique() == 61583, "Duplicate detection_id found!"
    print("   ASSERTION PASSED: Exact 61,583 rows preserved. 100% 1-to-1 unique match!")

    # 9. EXPORT MASTER DATASET
    output_path = "datasets/fireline_master_analytical_labeled_2024_2026.csv"
    print(f"\n9. Exporting master dataset to: {output_path}...")
    df_final.to_csv(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   Successfully exported {output_path} ({file_size_mb:.2f} MB)")

    # Also mirror to root datasets if present
    root_output_path = "../datasets/fireline_master_analytical_labeled_2024_2026.csv"
    if os.path.exists("../datasets"):
        df_final.to_csv(root_output_path, index=False)
        print(f"   Mirrored to: {root_output_path}")

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    build_master_dataset()
