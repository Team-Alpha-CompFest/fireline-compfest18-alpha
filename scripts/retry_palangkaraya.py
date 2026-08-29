"""Retry Palangkaraya and add to CSV"""
import urllib.request, json, time, pandas as pd

station = {'city': 'Palangkaraya', 'province': 'Kalimantan Tengah', 'lat': -2.2135, 'lon': 113.9108}
DAILY_VARS = [
    'temperature_2m_max','temperature_2m_min','temperature_2m_mean',
    'precipitation_sum','rain_sum','windspeed_10m_max','windgusts_10m_max',
    'relative_humidity_2m_mean','relative_humidity_2m_max','relative_humidity_2m_min',
    'et0_fao_evapotranspiration','vapor_pressure_deficit_max',
    'shortwave_radiation_sum','sunshine_duration',
]
url = (f"https://archive-api.open-meteo.com/v1/archive"
       f"?latitude={station['lat']}&longitude={station['lon']}"
       f"&start_date=2024-08-01&end_date=2026-05-31"
       f"&daily={','.join(DAILY_VARS)}&timezone=Asia%2FJakarta")

for attempt in range(3):
    try:
        time.sleep(1)
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        daily = data['daily']
        n = len(daily['time'])
        rows = []
        for i in range(n):
            row = {'date': daily['time'][i], 'city': station['city'],
                   'province': station['province'], 'latitude': station['lat'], 'longitude': station['lon']}
            for var in DAILY_VARS:
                row[var] = daily.get(var, [None]*n)[i]
            sd = row.get('sunshine_duration')
            row['sunshine_hours'] = round(sd/3600, 2) if sd else None
            rows.append(row)
        df_new = pd.DataFrame(rows)
        df_new['date'] = pd.to_datetime(df_new['date'])
        df_new.drop(columns=['sunshine_duration'], inplace=True, errors='ignore')
        df_new['is_dry_day'] = (df_new['precipitation_sum'] < 2.0).astype(int)
        df_new['high_fire_danger'] = (
            (df_new['temperature_2m_max'] > 33) &
            (df_new['relative_humidity_2m_min'] < 60) &
            (df_new['windspeed_10m_max'] > 20)
        ).astype(int)
        df_new['month'] = df_new['date'].dt.month
        df_new['year']  = df_new['date'].dt.year
        df_new['season'] = df_new['month'].apply(
            lambda m: 'Dry Season (Jun-Oct)' if m in {6,7,8,9,10} else 'Wet Season (Nov-May)')

        # Append to CSV
        df_existing = pd.read_csv('datasets/bmkg_kalimantan_weather_2024_2026.csv', parse_dates=['date'])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.sort_values(['province','city','date']).reset_index(drop=True)
        df_combined.to_csv('datasets/bmkg_kalimantan_weather_2024_2026.csv', index=False)
        print(f"OK! Added {len(df_new)} rows. Total now: {len(df_combined):,}")
        print(f"Stations: {df_combined.groupby('province')['city'].nunique().to_dict()}")
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(3)
