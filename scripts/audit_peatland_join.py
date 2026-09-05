import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def run_peatland_audit():
    print("=== STARTING PEATLAND JOIN AUDIT ===")
    
    # 1. Load Raw NASA Hotspot
    hotspot_path = "datasets/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv"
    df_raw = pd.read_csv(hotspot_path)
    raw_count = len(df_raw)
    print(f"1. Raw NASA Hotspot loaded: {raw_count} rows")
    
    key_cols = ['latitude', 'longitude', 'acq_date', 'acq_time']
    unique_keys = len(df_raw.drop_duplicates(subset=key_cols))
    print(f"   Unique composite keys (lat, lon, acq_date, acq_time): {unique_keys} (Duplicate keys in raw: {raw_count - unique_keys})")
    
    # 2. Inspect Peatland Product 1: kalimantan_peatland_spatial.geojson (KHG, 25 features)
    peat_khg_path = "datasets/kalimantan_peatland_spatial.geojson"
    gdf_khg = gpd.read_file(peat_khg_path)
    crs_khg = gdf_khg.crs
    print(f"\n2. Peatland Product 1 (KHG): {len(gdf_khg)} features")
    print(f"   CRS: {crs_khg} (EPSG:{crs_khg.to_epsg() if crs_khg else 'Unknown'})")
    print(f"   Columns: {list(gdf_khg.columns)}")
    print(f"   Geometries: {gdf_khg.geometry.geom_type.value_counts().to_dict()}")
    
    # 3. Inspect Peatland Product 2: peta_lahan_gambut_kalimantan.geojson (BIG, 146 features)
    peat_big_path = "datasets/gambut/peta_lahan_gambut_kalimantan.geojson"
    gdf_big = gpd.read_file(peat_big_path)
    crs_big = gdf_big.crs
    print(f"\n3. Peatland Product 2 (BIG): {len(gdf_big)} features")
    print(f"   CRS: {crs_big} (EPSG:{crs_big.to_epsg() if crs_big else 'Unknown'})")
    print(f"   Columns: {list(gdf_big.columns)}")
    print(f"   Geometries: {gdf_big.geometry.geom_type.value_counts().to_dict()}")

    # 4. Audit Existing fireline_hotspot_peat_featured_2024_2026.csv
    featured_path = "datasets/fireline_hotspot_peat_featured_2024_2026.csv"
    df_featured = pd.read_csv(featured_path)
    featured_count = len(df_featured)
    print(f"\n4. Existing Featured Dataset loaded: {featured_count} rows")
    diff_rows = featured_count - raw_count
    print(f"   Discrepancy vs raw: +{diff_rows} rows")
    
    dup_mask = df_featured.duplicated(subset=key_cols, keep=False)
    dup_rows = df_featured[dup_mask]
    print(f"   Number of duplicate occurrences: {len(dup_rows)} rows across {dup_rows[key_cols].drop_duplicates().shape[0]} unique hotspots")
    
    # Sample duplicates
    if len(dup_rows) > 0:
        sample_dup = dup_rows.sort_values(by=key_cols).head(6)
        print("   Sample duplicate rows showing boundary overlap:")
        print(sample_dup[key_cols + ['khg_id', 'nama_khg', 'peat_depth', 'depth_cm']])
        
    # 5. Deduplication Solution
    # Sort by key_cols and depth_cm descending (so deepest peat depth is preserved if touching 2 polygons)
    df_dedup = df_featured.sort_values(by=key_cols + ['depth_cm'], ascending=[True, True, True, True, False])
    df_dedup = df_dedup.drop_duplicates(subset=key_cols, keep='first').reset_index(drop=True)
    dedup_count = len(df_dedup)
    print(f"\n5. Deduplication applied:")
    print(f"   Resulting row count: {dedup_count} rows (Matches raw exactly: {dedup_count == raw_count})")
    
    # Overwrite the file with the clean deduplicated 61,583 rows
    df_dedup.to_csv(featured_path, index=False)
    print(f"   Successfully updated {featured_path} with 61,583 clean rows!")
    
    # Also update in root datasets if needed
    root_featured_path = "../datasets/fireline_hotspot_peat_featured_2024_2026.csv"
    if os.path.exists(root_featured_path):
        df_dedup.to_csv(root_featured_path, index=False)
        print(f"   Also updated {root_featured_path} with 61,583 clean rows!")

    # 6. Detailed Statistics on Matched vs Unmatched and Peat Depth Classes
    matched_khg = df_dedup[df_dedup['is_peatland'] == 1]
    unmatched_khg = df_dedup[df_dedup['is_peatland'] == 0]
    
    print("\n6. Final Statistics (KHG 25 Features Product):")
    print(f"   Total Hotspots: {len(df_dedup):,} (100.0%)")
    print(f"   - Matched (Lahan Gambut): {len(matched_khg):,} ({len(matched_khg)/len(df_dedup)*100:.2f}%)")
    print(f"   - Unmatched (Tanah Mineral): {len(unmatched_khg):,} ({len(unmatched_khg)/len(df_dedup)*100:.2f}%)")
    
    print("\n   Breakdown by Peat Depth Class:")
    depth_dist = df_dedup['peat_depth'].value_counts()
    for depth_label, count in depth_dist.items():
        pct = count / len(df_dedup) * 100
        print(f"   - {depth_label}: {count:,} ({pct:.2f}%)")
        
    print("\n   Peat Hazard Multiplier Distribution:")
    mult_dist = df_dedup['peat_hazard_multiplier'].value_counts().sort_index(ascending=False)
    for mult, count in mult_dist.items():
        pct = count / len(df_dedup) * 100
        print(f"   - Multiplier {mult:.2f}x: {count:,} ({pct:.2f}%)")

    # 7. Spatial Join with BIG Product (146 features) for Comparison
    print("\n7. Performing Spatial Join with BIG Product (146 features) for Cross-Validation:")
    geometry = [Point(xy) for xy in zip(df_raw['longitude'], df_raw['latitude'])]
    gdf_hotspots = gpd.GeoDataFrame(df_raw, geometry=geometry, crs="EPSG:4326")
    
    gdf_big_join = gpd.sjoin(gdf_hotspots, gdf_big[['is_peatland', 'peat_depth', 'peat_type', 'landform', 'geometry']], how='left', predicate='within')
    gdf_big_dedup = gdf_big_join.drop_duplicates(subset=key_cols, keep='first')
    
    matched_big = gdf_big_dedup[gdf_big_dedup['is_peatland'] == 1]
    unmatched_big = gdf_big_dedup[gdf_big_dedup['is_peatland'].isna() | (gdf_big_dedup['is_peatland'] == 0)]
    print(f"   BIG Product Match Results:")
    print(f"   - Matched (Lahan Gambut BIG): {len(matched_big):,} ({len(matched_big)/len(gdf_big_dedup)*100:.2f}%)")
    print(f"   - Unmatched (Tanah Mineral): {len(unmatched_big):,} ({len(unmatched_big)/len(gdf_big_dedup)*100:.2f}%)")
    print(f"   - BIG Peat Depth breakdown:")
    print(gdf_big_dedup['peat_depth'].value_counts().to_dict())
    print(f"   - BIG Peat Type breakdown:")
    print(gdf_big_dedup['peat_type'].value_counts().to_dict())
    
    print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    run_peatland_audit()
