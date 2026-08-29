"""
BMKG Weather Data Collection via Open-Meteo Archive API
Covers: Kalimantan provinces | Date range: 2024-08-01 to 2026-05-31
Variables: temperature, humidity, precipitation, wind speed (fire-relevant)
Output: datasets/bmkg_kalimantan_weather_2024_2026.csv
"""

import urllib.request
import json
import time
import pandas as pd
from datetime import date

# ============================================================
# KALIMANTAN WEATHER STATIONS (major cities per province)
# ============================================================
STATIONS = [
    # Kalimantan Barat
    {'city': 'Pontianak',    'province': 'Kalimantan Barat',   'lat': -0.0263,  'lon': 109.3425},
    {'city': 'Singkawang',   'province': 'Kalimantan Barat',   'lat':  0.9023,  'lon': 108.9861},
    {'city': 'Ketapang',     'province': 'Kalimantan Barat',   'lat': -1.8432,  'lon': 109.9740},
    {'city': 'Sintang',      'province': 'Kalimantan Barat',   'lat':  0.0639,  'lon': 111.4732},
    # Kalimantan Tengah
    {'city': 'Palangkaraya', 'province': 'Kalimantan Tengah',  'lat': -2.2135,  'lon': 113.9108},
    {'city': 'Sampit',       'province': 'Kalimantan Tengah',  'lat': -2.5350,  'lon': 112.9501},
    {'city': 'Pangkalan Bun','province': 'Kalimantan Tengah',  'lat': -2.6994,  'lon': 111.6238},
    # Kalimantan Timur
    {'city': 'Balikpapan',   'province': 'Kalimantan Timur',   'lat': -1.2379,  'lon': 116.8529},
    {'city': 'Samarinda',    'province': 'Kalimantan Timur',   'lat': -0.4948,  'lon': 117.1436},
    {'city': 'Berau',        'province': 'Kalimantan Timur',   'lat':  2.1668,  'lon': 117.4817},
    # Kalimantan Selatan
    {'city': 'Banjarmasin',  'province': 'Kalimantan Selatan', 'lat': -3.3194,  'lon': 114.5897},
    {'city': 'Banjarbaru',   'province': 'Kalimantan Selatan', 'lat': -3.4478,  'lon': 114.8240},
    # Kalimantan Utara
    {'city': 'Tarakan',      'province': 'Kalimantan Utara',   'lat':  3.3002,  'lon': 117.5765},
    {'city': 'Tanjung Selor','province': 'Kalimantan Utara',   'lat':  2.8380,  'lon': 117.3735},
]

# ============================================================
# API PARAMETERS
# ============================================================
START_DATE = '2024-08-01'
END_DATE   = '2026-05-31'
TIMEZONE   = 'Asia/Jakarta'

DAILY_VARS = [
    'temperature_2m_max',           # Max daily temperature (C) - fire risk indicator
    'temperature_2m_min',           # Min daily temperature (C)
    'temperature_2m_mean',          # Mean daily temperature (C)
    'precipitation_sum',            # Daily total rainfall (mm) - inverse fire risk
    'rain_sum',                     # Daily rain only (excl. snow) (mm)
    'windspeed_10m_max',            # Max wind speed (km/h) - fire spread
    'windgusts_10m_max',            # Max wind gust (km/h) - extreme spread risk
    'relative_humidity_2m_mean',    # Mean daily humidity (%) - low = higher fire risk
    'relative_humidity_2m_max',     # Max humidity
    'relative_humidity_2m_min',     # Min humidity (driest part of day)
    'et0_fao_evapotranspiration',   # Evapotranspiration (mm) - vegetation dryness proxy
    'vapor_pressure_deficit_max',   # VPD max (kPa) - atmospheric dryness, fire danger metric
    'shortwave_radiation_sum',      # Solar radiation (MJ/m2) - drying effect
    'sunshine_duration',            # Sunshine hours (s) - converted to hours
]

BASE_URL = 'https://archive-api.open-meteo.com/v1/archive'

def fetch_station(station):
    params = (
        f"?latitude={station['lat']}"
        f"&longitude={station['lon']}"
        f"&start_date={START_DATE}"
        f"&end_date={END_DATE}"
        f"&daily={','.join(DAILY_VARS)}"
        f"&timezone={TIMEZONE.replace('/', '%2F')}"
    )
    url = BASE_URL + params
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        daily = data['daily']
        n = len(daily['time'])
        rows = []
        for i in range(n):
            row = {
                'date':            daily['time'][i],
                'city':            station['city'],
                'province':        station['province'],
                'latitude':        station['lat'],
                'longitude':       station['lon'],
            }
            for var in DAILY_VARS:
                row[var] = daily.get(var, [None] * n)[i]
            # Derived: sunshine_hours
            if row.get('sunshine_duration') is not None:
                row['sunshine_hours'] = round(row['sunshine_duration'] / 3600, 2)
            else:
                row['sunshine_hours'] = None
            rows.append(row)
        return rows, None
    except Exception as e:
        return [], str(e)

# ============================================================
# SCRAPE ALL STATIONS
# ============================================================
print(f"Scraping {len(STATIONS)} stations | {START_DATE} to {END_DATE}")
print("=" * 60)

all_rows = []
for i, station in enumerate(STATIONS):
    print(f"[{i+1:02d}/{len(STATIONS)}] {station['city']} ({station['province']})...", end=' ', flush=True)
    rows, err = fetch_station(station)
    if err:
        print(f"FAILED: {err}")
    else:
        all_rows.extend(rows)
        print(f"OK ({len(rows)} days)")
    time.sleep(0.4)  # polite rate limiting

print(f"\nTotal rows collected: {len(all_rows):,}")

# ============================================================
# BUILD DATAFRAME & CLEAN
# ============================================================
df = pd.DataFrame(all_rows)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['province', 'city', 'date']).reset_index(drop=True)

# Drop raw sunshine_duration (keep sunshine_hours)
df.drop(columns=['sunshine_duration'], inplace=True, errors='ignore')

# ============================================================
# DERIVED FIRE-RELEVANT FEATURES
# ============================================================
# Drought indicator: dry if precipitation < 2mm
df['is_dry_day'] = (df['precipitation_sum'] < 2.0).astype(int)

# High fire danger: temp > 33 AND humidity < 60 AND wind > 20 km/h
df['high_fire_danger'] = (
    (df['temperature_2m_max'] > 33) &
    (df['relative_humidity_2m_min'] < 60) &
    (df['windspeed_10m_max'] > 20)
).astype(int)

# Season label (matching fireline dataset)
df['month'] = df['date'].dt.month
df['year']  = df['date'].dt.year
df['season'] = df['month'].apply(
    lambda m: 'Dry Season (Jun-Oct)' if m in {6,7,8,9,10} else 'Wet Season (Nov-May)'
)

# ============================================================
# SAVE
# ============================================================
OUT_PATH = 'datasets/bmkg_kalimantan_weather_2024_2026.csv'
df.to_csv(OUT_PATH, index=False)

print(f"\nSaved: {OUT_PATH}")
print(f"Shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nProvince distribution:")
print(df.groupby('province')['city'].nunique().to_string())
print(f"\nDate range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"\nMissing values summary:")
miss = df.isnull().sum()
print(miss[miss > 0].to_string() if miss.any() else "  None")
print("\nSample rows:")
print(df[['date','city','province','temperature_2m_max','precipitation_sum',
          'windspeed_10m_max','relative_humidity_2m_min','vapor_pressure_deficit_max']].head(5).to_string())
