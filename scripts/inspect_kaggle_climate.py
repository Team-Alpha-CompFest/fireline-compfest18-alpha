import pandas as pd

print("Loading climate_data.csv...")
df = pd.read_csv('datasets/climate_data.csv')
print(f"Total rows: {len(df):,}")
print(f"Columns: {list(df.columns)}")

# Convert date
df['date_dt'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
print(f"Date range: {df['date_dt'].min().date()} to {df['date_dt'].max().date()}")
print(f"Unique stations: {df['station_id'].nunique()}")

prov = pd.read_csv('datasets/province_detail.csv')
sta = pd.read_csv('datasets/station_detail.csv').merge(prov, on='province_id', how='left')
kal_ids = sta[sta['province_name'].str.contains('Kalimantan', na=False)]['station_id'].tolist()

df_kal = df[df['station_id'].isin(kal_ids)].merge(
    sta[['station_id', 'station_name', 'province_name', 'latitude', 'longitude']],
    on='station_id', how='left'
)

print(f"\n=== KALIMANTAN SUBSET ===")
print(f"Kalimantan rows: {len(df_kal):,}")
print(f"Kalimantan stations present: {df_kal['station_id'].nunique()} / {len(kal_ids)}")
print(f"Kalimantan date range: {df_kal['date_dt'].min().date()} to {df_kal['date_dt'].max().date()}")
print(f"\nRows per province in Kalimantan:")
print(df_kal['province_name'].value_counts())

print(f"\nMissing values in Kalimantan subset:")
print(df_kal.isnull().sum())

print(f"\nSummary statistics (Kalimantan numeric cols):")
num_cols = ['Tn', 'Tx', 'Tavg', 'RH_avg', 'RR', 'ss', 'ff_x', 'ff_avg']
print(df_kal[num_cols].describe().round(2).to_string())
