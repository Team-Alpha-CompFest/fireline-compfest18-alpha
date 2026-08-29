"""
FIRELINE - NASA FIRMS Automated Data Ingestion & Risk Scoring Pipeline
Author: Data Science Team (FIRELINE - COMPFEST 18)
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import json

sys.stdout.reconfigure(encoding='utf-8')

class NasaFirmsPipeline:
    def __init__(self, api_key: str = None, bbox: list = None):
        """
        Inisialisasi pipeline data satelit NASA FIRMS.
        bbox: [min_lon, min_lat, max_lon, max_lat] untuk Kalimantan: [108.5, -4.5, 119.5, 4.5]
        """
        self.api_key = api_key or os.getenv("NASA_FIRMS_MAP_KEY", "DEMO_KEY")
        self.bbox = bbox or [108.5, -4.5, 119.5, 4.5]
        self.source = "VIIRS_NOAA20_NRT"
        
    def fetch_live_firms_data(self, days: int = 1) -> pd.DataFrame:
        """
        Mengambil data hotspot real-time terbaru langsung dari REST API NASA FIRMS.
        """
        bbox_str = ",".join(map(str, self.bbox))
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{self.api_key}/{self.source}/{bbox_str}/{days}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengunduh data satelit NRT dari NASA FIRMS API...")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200 and "latitude" in response.text:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                print(f"[SUCCESS] Berhasil mengambil {len(df)} titik api baru dari satelit!")
                return df
            else:
                print(f"[INFO] API response code {response.status_code}. Beralih ke data buffer lokal.")
                return pd.DataFrame()
        except Exception as e:
            print(f"[ERROR] Gagal terhubung ke NASA FIRMS API: {e}")
            return pd.DataFrame()

    def ingest_local_dataset(self, csv_path: str = "fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv") -> pd.DataFrame:
        """
        Memuat dataset observasi satelit lokal.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Berkas {csv_path} tidak ditemukan!")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Membaca dataset lokal: {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"[SUCCESS] Memuat {len(df):,} baris data titik api.")
        return df

    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Melakukan Feature Engineering otomatis:
        1. Parsing tanggal & waktu deteksi
        2. Perhitungan Fire Severity Index (FSI)
        3. Deteksi Kebakaran Malam (Smoldering Peat Burning Factor)
        4. Klasifikasi Region Kalimantan (Kalbar, Kalteng, Kalsel, Kaltim, Kaltara)
        5. Normalisasi Fire Radiative Power (FRP)
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Menjalankan automated feature engineering...")
        df = df.copy()
        
        # 1. Parsing DateTime
        df['acq_datetime'] = pd.to_datetime(df['acq_date'] + ' ' + df['acq_time'].astype(str).str.zfill(4), format='%Y-%m-%d %H%M', errors='coerce')
        df['month_year'] = df['acq_date'].str.slice(0, 7)
        
        # 2. Fire Severity Index (FSI) Formula Ilmiah
        # Mengkombinasikan suhu kecerahan kanal I-4 dan log-transformed FRP
        df['fire_severity_index'] = (df['brightness'] / 300.0) * np.log1p(df['frp'])
        
        # 3. Peat Smoldering Risk (Night fires indicate subsurface peat combustion)
        df['is_night_smoldering'] = (df['daynight'] == 'N').astype(int)
        
        # 4. Region Tagging Berdasarkan Koordinat Poligon Kalimantan
        def assign_province(lat, lon):
            if lon < 111.0:
                return 'Kalimantan Barat'
            elif lon >= 111.0 and lon < 114.5 and lat < 0.5:
                return 'Kalimantan Tengah'
            elif lon >= 114.5 and lat < -1.0:
                return 'Kalimantan Selatan'
            elif lat >= 1.5 and lon >= 115.0:
                return 'Kalimantan Utara'
            else:
                return 'Kalimantan Timur'
                
        df['province_est'] = [assign_province(lat, lon) for lat, lon in zip(df['latitude'], df['longitude'])]
        
        # 5. Risk Category Ranking
        conditions = [
            (df['frp'] >= 25.0) | (df['brightness'] >= 350.0) | (df['confidence'] == 'h'),
            (df['frp'] >= 8.0) | (df['is_night_smoldering'] == 1),
            (df['frp'] < 8.0)
        ]
        choices = ['CRITICAL (High Hazard)', 'WARNING (Moderate Hazard)', 'MONITOR (Low Hazard)']
        df['hazard_level'] = np.select(conditions, choices, default='MONITOR')
        
        print("[SUCCESS] Feature engineering selesai!")
        return df

    def sync_and_export(self, df: pd.DataFrame, output_json: str = "fireline_data_processed.json"):
        """
        Mengekspor data yang telah diproses untuk dikonsumsi API server dan dashboard.
        """
        summary = {
            "last_synced_utc": datetime.now(timezone.utc).isoformat(),
            "total_hotspots": int(len(df)),
            "critical_hazard_count": int((df['hazard_level'] == 'CRITICAL (High Hazard)').sum()),
            "total_frp_mw": float(round(df['frp'].sum(), 2)),
            "provinces_breakdown": df['province_est'].value_counts().to_dict(),
            "sample_records": df[['latitude', 'longitude', 'brightness', 'frp', 'acq_date', 'confidence', 'hazard_level', 'province_est']].head(100).to_dict(orient='records')
        }
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"[EXPORT] Ringkasan data real-time tersimpan di {output_json}")

if __name__ == "__main__":
    pipeline = NasaFirmsPipeline()
    df_raw = pipeline.ingest_local_dataset()
    df_enriched = pipeline.feature_engineering(df_raw)
    pipeline.sync_and_export(df_enriched)
    print("\n🎉 Pipeline berhasil dijalankan dan siap diintegrasikan secara berkala!")
