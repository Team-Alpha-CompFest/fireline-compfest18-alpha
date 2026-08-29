"""
Pipeline Pengolahan Data Resmi Panitia COMPFEST 18
Fokus 100% pada Dataset Asli:
- datasets/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv (61,583 data)
- datasets/complete_data.csv (17,448 fasilitas pendidikan/desa di Kalimantan)
- datasets/province_detail.csv
"""

import os
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import json

def process_official_data():
    print("=" * 60)
    print("[START] MEMPROSES DATASET RESMI PANITIA SECARA KESELURUHAN")
    print("=" * 60)

    # 1. Load Data
    raw_fire_path = 'datasets/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv'
    schools_path = 'datasets/complete_data.csv'

    df_fire = pd.read_csv(raw_fire_path)
    df_schools = pd.read_csv(schools_path)
    print(f"[OK] Loaded Hotspots: {len(df_fire):,} baris")
    print(f"[OK] Loaded Total Schools in Indonesia: {len(df_schools):,} baris")

    # 2. Filter Schools in Kalimantan
    kalimantan_provinces = [p for p in df_schools['province_name'].dropna().unique() if 'KALIMANTAN' in str(p).upper()]
    df_kal_schools = df_schools[df_schools['province_name'].isin(kalimantan_provinces)].dropna(subset=['lat', 'long']).copy()
    df_kal_schools.reset_index(drop=True, inplace=True)
    print(f"[OK] Filtered Kalimantan Schools/Villages: {len(df_kal_schools):,} fasilitas di 5 Provinsi")

    # Save clean Kalimantan schools dataset for reference
    df_kal_schools.to_csv('02_dataset_olahan_master_tableau/kalimantan_schools_and_population.csv', index=False)

    # 3. Spatial Intelligence (BallTree Haversine)
    print("\n[INFO] Membangun Spatial BallTree untuk pencocokan koordinat tercepat...")
    earth_radius_km = 6371.0
    schools_rad = np.radians(df_kal_schools[['lat', 'long']].values)
    tree = BallTree(schools_rad, metric='haversine')

    fire_rad = np.radians(df_fire[['latitude', 'longitude']].values)
    distances, indices = tree.query(fire_rad, k=1)
    dist_km = (distances.flatten() * earth_radius_km).round(2)
    nearest_idx = indices.flatten()

    counts_5km = tree.query_radius(fire_rad, r=5.0 / earth_radius_km, count_only=True)
    counts_10km = tree.query_radius(fire_rad, r=10.0 / earth_radius_km, count_only=True)

    # Map nearest school properties
    nearest_records = df_kal_schools.iloc[nearest_idx].reset_index(drop=True)

    # 4. Feature Engineering
    df_master = df_fire.copy()
    df_master['hotspot_id'] = [f"HS-KLM-{i+1:06d}" for i in range(len(df_master))]

    # Spatial columns
    df_master['nearest_school_name'] = nearest_records['school_name'].values
    df_master['nearest_school_stage'] = nearest_records['stage'].values
    df_master['nearest_school_status'] = nearest_records['status'].values
    df_master['nearest_district'] = nearest_records['district_name'].values
    df_master['nearest_city_regency'] = nearest_records['city_name'].values
    df_master['nearest_province'] = nearest_records['province_name'].values
    df_master['regency_total_population'] = nearest_records['total_population'].values
    df_master['regency_edu_age_population'] = nearest_records['total_education_age_population'].values
    
    df_master['dist_to_school_km'] = dist_km
    df_master['schools_in_radius_5km'] = counts_5km
    df_master['schools_in_radius_10km'] = counts_10km

    # Impact Zone
    conditions_zone = [
        (df_master['dist_to_school_km'] < 3.0),
        (df_master['dist_to_school_km'] >= 3.0) & (df_master['dist_to_school_km'] < 7.0),
        (df_master['dist_to_school_km'] >= 7.0) & (df_master['dist_to_school_km'] < 15.0),
        (df_master['dist_to_school_km'] >= 15.0)
    ]
    zones = [
        'Zona Merah: Bahaya Ekstrem (<3 km)',
        'Zona Oranye: Siaga Tinggi (3-7 km)',
        'Zona Kuning: Waspada Menengah (7-15 km)',
        'Zona Hijau: Area Terpencil (>15 km)'
    ]
    df_master['impact_zone'] = np.select(conditions_zone, zones, default='Zona Hijau: Area Terpencil (>15 km)')

    # Physical Energetics & Temperatures
    df_master['brightness_celsius'] = (df_master['brightness'] - 273.15).round(2)
    df_master['bright_t31_celsius'] = (df_master['bright_t31'] - 273.15).round(2)
    df_master['temp_delta_celsius'] = (df_master['brightness'] - df_master['bright_t31']).round(2)

    # FRP Severity
    conditions_frp = [
        (df_master['frp'] < 5.0),
        (df_master['frp'] >= 5.0) & (df_master['frp'] < 20.0),
        (df_master['frp'] >= 20.0) & (df_master['frp'] < 50.0),
        (df_master['frp'] >= 50.0)
    ]
    frp_labels = [
        'Rendah (<5 MW)',
        'Sedang (5-20 MW)',
        'Tinggi (20-50 MW)',
        'Ekstrem (>50 MW)'
    ]
    df_master['frp_severity_class'] = np.select(conditions_frp, frp_labels, default='Rendah (<5 MW)')

    # Confidence Labels & Numeric Weight
    conf_map_label = {'l': 'Low / Rendah', 'n': 'Nominal / Standar', 'h': 'High / Sangat Yakin'}
    conf_map_weight = {'l': 0.3, 'n': 0.7, 'h': 1.0}
    df_master['confidence_label'] = df_master['confidence'].map(conf_map_label).fillna('Nominal / Standar')
    df_master['confidence_weight'] = df_master['confidence'].map(conf_map_weight).fillna(0.7)

    # Day/Night Label
    daynight_map = {'D': 'Siang Hari (D)', 'N': 'Malam Hari (N)'}
    df_master['daynight_label'] = df_master['daynight'].map(daynight_map).fillna('Siang Hari (D)')

    # Temporal Engineering
    df_master['acq_date'] = pd.to_datetime(df_master['acq_date'])
    df_master['year'] = df_master['acq_date'].dt.year
    df_master['month'] = df_master['acq_date'].dt.month
    df_master['month_name'] = df_master['acq_date'].dt.strftime('%B')
    df_master['day_of_month'] = df_master['acq_date'].dt.day
    df_master['day_name'] = df_master['acq_date'].dt.strftime('%A')
    df_master['is_weekend'] = df_master['acq_date'].dt.dayofweek.isin([5, 6]).astype(int)
    df_master['quarter'] = 'Q' + df_master['acq_date'].dt.quarter.astype(str)
    df_master['year_month'] = df_master['acq_date'].dt.strftime('%Y-%m')

    # Season
    df_master['season'] = np.where(
        df_master['month'].between(6, 10),
        'Musim Kemarau (Puncak Kebakaran)',
        'Musim Hujan'
    )

    # Time of Day
    df_master['hour'] = df_master['acq_time'].astype(str).str.zfill(4).str[:2].astype(int)
    conditions_time = [
        (df_master['hour'] >= 5) & (df_master['hour'] < 11),
        (df_master['hour'] >= 11) & (df_master['hour'] < 15),
        (df_master['hour'] >= 15) & (df_master['hour'] < 18),
    ]
    time_labels = ['Pagi (05-11)', 'Siang (11-15)', 'Sore (15-18)']
    df_master['time_period'] = np.select(conditions_time, time_labels, default='Malam/Dini Hari (18-05)')

    # Composite Multi-Criteria Risk Scoring (0 - 100)
    # FRP Component (30%): Cap at 50 MW
    frp_comp = np.clip(df_master['frp'] / 50.0 * 100, 0, 100) * 0.30

    # Proximity Component (35%): Linear decay from 0 km (100) to 10 km (0)
    prox_comp = np.clip((10.0 - df_master['dist_to_school_km']) / 10.0 * 100, 0, 100) * 0.35

    # Temp Delta Component (20%): Cap at 50°C
    delta_comp = np.clip(df_master['temp_delta_celsius'] / 50.0 * 100, 0, 100) * 0.20

    # Confidence Component (15%)
    conf_comp = (df_master['confidence_weight'] * 100) * 0.15

    df_master['composite_risk_score'] = (frp_comp + prox_comp + delta_comp + conf_comp).round(1)

    # Priority Action Tier
    conditions_tier = [
        (df_master['composite_risk_score'] >= 75.0),
        (df_master['composite_risk_score'] >= 50.0) & (df_master['composite_risk_score'] < 75.0),
        (df_master['composite_risk_score'] >= 25.0) & (df_master['composite_risk_score'] < 50.0)
    ]
    tier_labels = [
        'Tier 1: Pemadaman Darurat & Evakuasi Sekolah Segera',
        'Tier 2: Patroli Lapangan & Water Bombing Siaga',
        'Tier 3: Monitoring Posko & Sosialisasi Warga'
    ]
    df_master['priority_action_tier'] = np.select(conditions_tier, tier_labels, default='Tier 4: Pemantauan Satelit Rutin')

    # 5. Export Processed Master Dataset for Tableau
    output_master_csv = '02_dataset_olahan_master_tableau/fireline_hotspot_kalimantan_processed_master.csv'
    df_master.to_csv(output_master_csv, index=False)
    print(f"\n[OK] SUCCESS! File Master Siap Tableau: {output_master_csv}")
    print(f"     Total Baris: {len(df_master):,}")
    print(f"     Total Kolom: {df_master.shape[1]}")

    # 6. Aggregated Summary for Tableau (Provinsi & Kabupaten)
    summary_kab = df_master.groupby(['nearest_province', 'nearest_city_regency']).agg(
        total_hotspots=('hotspot_id', 'count'),
        total_frp_mw=('frp', 'sum'),
        avg_frp_mw=('frp', 'mean'),
        max_frp_mw=('frp', 'max'),
        avg_risk_score=('composite_risk_score', 'mean'),
        tier1_emergency_count=('priority_action_tier', lambda x: (x == 'Tier 1: Pemadaman Darurat & Evakuasi Sekolah Segera').sum()),
        tier2_patrol_count=('priority_action_tier', lambda x: (x == 'Tier 2: Patroli Lapangan & Water Bombing Siaga').sum()),
        extreme_zone_count=('impact_zone', lambda x: (x == 'Zona Merah: Bahaya Ekstrem (<3 km)').sum()),
        avg_distance_to_school_km=('dist_to_school_km', 'mean'),
        total_population=('regency_total_population', 'first'),
        total_education_population=('regency_edu_age_population', 'first')
    ).reset_index()

    summary_kab.sort_values(by='total_hotspots', ascending=False, inplace=True)
    summary_kab.to_csv('02_dataset_olahan_master_tableau/summary_provinsi_kabupaten_hotspot_analysis.csv', index=False)
    print(f"[OK] SUCCESS! File Agregasi Provinsi/Kabupaten: 02_dataset_olahan_master_tableau/summary_provinsi_kabupaten_hotspot_analysis.csv")

    # 7. Print Insight Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] RINGKASAN HASIL PENGOLAHAN DATA RESMI (61.583 HOTSPOTS)")
    print("=" * 60)
    print(f"Periode Data        : {df_master['acq_date'].min().strftime('%d %b %Y')} s/d {df_master['acq_date'].max().strftime('%d %b %Y')}")
    print("\nDistribusi Per Provinsi:")
    prov_dist = df_master['nearest_province'].value_counts()
    for prov, count in prov_dist.items():
        pct = count / len(df_master) * 100
        print(f"  - {prov:<25}: {count:6,d} ({pct:5.1f}%)")

    print("\nDistribusi Zona Dampak ke Sekolah/Pemukiman:")
    zone_dist = df_master['impact_zone'].value_counts()
    for z, count in zone_dist.items():
        pct = count / len(df_master) * 100
        print(f"  - {z:<40}: {count:6,d} ({pct:5.1f}%)")

    print("\nDistribusi Tingkat Prioritas Tanggap Darurat (Tiers):")
    tier_dist = df_master['priority_action_tier'].value_counts()
    for t, count in tier_dist.items():
        pct = count / len(df_master) * 100
        print(f"  - {t:<50}: {count:6,d} ({pct:5.1f}%)")

    # 8. Update Web Dashboard Data (JSON)
    dash_data = {
        'metadata': {
            'total_hotspots': len(df_master),
            'min_date': df_master['acq_date'].min().strftime('%Y-%m-%d'),
            'max_date': df_master['acq_date'].max().strftime('%Y-%m-%d'),
            'total_schools_covered': len(df_kal_schools),
            'total_frp_mw': float(df_master['frp'].sum()),
            'avg_frp_mw': float(df_master['frp'].mean()),
            'tier1_count': int((df_master['priority_action_tier'] == 'Tier 1: Pemadaman Darurat & Evakuasi Sekolah Segera').sum()),
            'tier2_count': int((df_master['priority_action_tier'] == 'Tier 2: Patroli Lapangan & Water Bombing Siaga').sum()),
            'red_zone_count': int((df_master['impact_zone'] == 'Zona Merah: Bahaya Ekstrem (<3 km)').sum()),
        },
        'province_stats': df_master.groupby('nearest_province').agg(
            hotspots=('hotspot_id', 'count'),
            total_frp=('frp', 'sum'),
            avg_risk=('composite_risk_score', 'mean'),
            tier1=('priority_action_tier', lambda x: int((x == 'Tier 1: Pemadaman Darurat & Evakuasi Sekolah Segera').sum()))
        ).to_dict(orient='index'),
        'monthly_trend': df_master.groupby('year_month').size().to_dict(),
        'top_kabupaten': summary_kab.head(15)[['nearest_city_regency', 'nearest_province', 'total_hotspots', 'total_frp_mw', 'tier1_emergency_count', 'extreme_zone_count']].to_dict(orient='records')
    }

    with open('dashboards_web/fireline_data_processed.json', 'w') as f:
        json.dump(dash_data, f, indent=2)
    print("[OK] SUCCESS! Updated dashboards_web/fireline_data_processed.json")

if __name__ == '__main__':
    process_official_data()
