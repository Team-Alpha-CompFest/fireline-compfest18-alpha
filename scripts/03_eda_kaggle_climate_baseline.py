"""
Pipeline 03: Kaggle Indonesia Climate Dataset (2010-2020) Decadal Climatology EDA
Source: 24 BMKG Stations in Kalimantan (87,238 Daily Observations)
Context: FIRELINE Platform - COMPFEST 18 Case Study (Team Alpha)
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import pearsonr

# Import local geospatial utility
sys.path.append(os.path.dirname(__file__))
from utils_geo import ensure_geojson, draw_boundaries, PROV_PALETTE

warnings.filterwarnings('ignore')

# ============================================================
# PATH CONFIGURATION
# ============================================================
CLIMATE_CSV  = 'datasets/climate_data.csv'
PROV_CSV     = 'datasets/province_detail.csv'
STA_CSV      = 'datasets/station_detail.csv'
OUT_BASE     = 'EDA/03_kaggle_indonesia_climate'
DATA_DIR     = os.path.join(OUT_BASE, '03_preprocessing')
VIZ_DIR      = os.path.join(OUT_BASE, '02_visualizations')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

# Style settings
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelweight': 'bold',
    'axes.facecolor': '#1e2d3d',
    'figure.facecolor': '#1e2d3d',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'axes.edgecolor': '#3d5166',
    'grid.color': '#2d4050',
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.25,
})

def savefig(fig, name):
    path = os.path.join(VIZ_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.25, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {name}")

# ============================================================
# 1. LOAD & PREPROCESS KALIMANTAN SUBSET
# ============================================================
print("\n" + "=" * 70)
print("STAGE 1: LOADING & FILTERING KALIMANTAN 11-YEAR CLIMATE DATA")
print("=" * 70)

prov_df = pd.read_csv(PROV_CSV)
sta_df  = pd.read_csv(STA_CSV).merge(prov_df, on='province_id', how='left')

kal_sta = sta_df[sta_df['province_name'].str.contains('Kalimantan', na=False)].copy()
kal_ids = kal_sta['station_id'].tolist()
print(f"BMKG Kalimantan stations: {len(kal_sta)}")

climate_df = pd.read_csv(CLIMATE_CSV)
df_kal = climate_df[climate_df['station_id'].isin(kal_ids)].merge(
    kal_sta[['station_id', 'station_name', 'region_name', 'province_name', 'latitude', 'longitude']],
    on='station_id', how='left'
)

# Parse dates & features
df_kal['date']       = pd.to_datetime(df_kal['date'], format='%d-%m-%Y', errors='coerce')
df_kal['year']       = df_kal['date'].dt.year
df_kal['month']      = df_kal['date'].dt.month
df_kal['month_name'] = df_kal['date'].dt.strftime('%b')
df_kal['year_month'] = df_kal['date'].dt.strftime('%Y-%m')
df_kal['season']     = df_kal['month'].apply(lambda m: 'Dry Season (Jun-Oct)' if m in [6,7,8,9,10] else 'Wet Season (Nov-May)')

# Fire weather indicators
df_kal['is_dry_day']      = (df_kal['RR'] < 2.0).astype(int)
df_kal['is_extreme_heat'] = (df_kal['Tx'] >= 34.0).astype(int)
df_kal['fire_danger_day'] = ((df_kal['Tx'] >= 33.0) & (df_kal['RH_avg'] <= 80.0) & (df_kal['RR'] < 2.0)).astype(int)

# Save cleaned subset
clean_csv = os.path.join(DATA_DIR, 'kalimantan_climate_2010_2020_clean.csv')
df_kal.to_csv(clean_csv, index=False)
print(f"Cleaned 11-year dataset saved: {clean_csv} ({len(df_kal):,} rows)")

# ============================================================
# 2. GENERATE 6 DECADAL CLIMATE CHARTS
# ============================================================
print("\n" + "=" * 70)
print("STAGE 2: GENERATING DECADAL CLIMATOLOGY & RISK VISUALIZATIONS")
print("=" * 70)

month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
months_x = np.arange(1, 13)

# K01. Decadal Monthly Climatology
monthly_clim = df_kal.groupby('month').agg(
    Tx_mean=('Tx', 'mean'), Tn_mean=('Tn', 'mean'), Tavg_mean=('Tavg', 'mean'),
    RH_mean=('RH_avg', 'mean'), RR_sum_mean=('RR', lambda x: x.sum() / 11 / df_kal['station_id'].nunique()),
    ss_mean=('ss', 'mean'), fire_danger_prob=('fire_danger_day', 'mean'),
).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(15, 11))
axes[0, 0].plot(months_x, monthly_clim['Tx_mean'], color='#e74c3c', lw=2.5, marker='o', label='Max Temp (Tx)')
axes[0, 0].plot(months_x, monthly_clim['Tavg_mean'], color='#f39c12', lw=2, marker='s', label='Avg Temp (Tavg)')
axes[0, 0].plot(months_x, monthly_clim['Tn_mean'], color='#3498db', lw=2, marker='^', label='Min Temp (Tn)')
axes[0, 0].axvspan(6, 10, color='#e74c3c', alpha=0.15, label='Dry Season Window')
axes[0, 0].set_xticks(months_x); axes[0, 0].set_xticklabels(month_labels); axes[0, 0].set_ylabel('Temperature (°C)'); axes[0, 0].set_title('Decadal Monthly Temperature (°C)')
axes[0, 0].legend(loc='lower right', fontsize=8.5, framealpha=0.4); axes[0, 0].grid(alpha=0.2)

axes[0, 1].plot(months_x, monthly_clim['RH_mean'], color='#1abc9c', lw=2.5, marker='o')
axes[0, 1].fill_between(months_x, monthly_clim['RH_mean'], 80, color='#1abc9c', alpha=0.25)
axes[0, 1].axvspan(6, 10, color='#e74c3c', alpha=0.15)
axes[0, 1].set_xticks(months_x); axes[0, 1].set_xticklabels(month_labels); axes[0, 1].set_ylabel('Relative Humidity (%)'); axes[0, 1].set_title('Decadal Monthly Relative Humidity (%)')
axes[0, 1].grid(alpha=0.2)

ax2 = axes[1, 0].twinx()
axes[1, 0].bar(months_x - 0.15, monthly_clim['RR_sum_mean'], width=0.4, color='#2980b9', alpha=0.8, label='Monthly Rainfall')
ax2.plot(months_x + 0.15, monthly_clim['ss_mean'], color='#f1c40f', lw=2.5, marker='D', label='Sunshine Hours')
axes[1, 0].axvspan(6, 10, color='#e74c3c', alpha=0.15)
axes[1, 0].set_xticks(months_x); axes[1, 0].set_xticklabels(month_labels)
axes[1, 0].set_ylabel('Monthly Rainfall (mm)', color='#2980b9'); ax2.set_ylabel('Daily Sunshine Duration (hours)', color='#f1c40f')
axes[1, 0].set_title('Decadal Rainfall Deficit vs Sunshine Duration'); axes[1, 0].grid(alpha=0.2)

probs = monthly_clim['fire_danger_prob'] * 100
colors = ['#c0392b' if m in [6,7,8,9,10] else '#2980b9' for m in months_x]
axes[1, 1].bar(months_x, probs, color=colors, alpha=0.85, edgecolor='white', lw=0.5)
axes[1, 1].set_xticks(months_x); axes[1, 1].set_xticklabels(month_labels)
axes[1, 1].set_ylabel('Probability (%)'); axes[1, 1].set_title('Probability of High Fire Danger Days (%)')
axes[1, 1].grid(axis='y', alpha=0.2)

fig.suptitle('Decadal Climatology of Kalimantan (2010-2020 BMKG Baseline)', fontsize=14, fontweight='bold', color='white', y=1.02)
fig.tight_layout()
savefig(fig, 'K01_decadal_monthly_climatology_kalimantan.png')

# K02. Extreme Years Comparison (2015 El Nino & 2019 vs Normal)
df_kal['year_cat'] = df_kal['year'].apply(
    lambda y: '2015 (Extreme El Nino)' if y == 2015 else ('2019 (Severe Drought)' if y == 2019 else 'Normal Baseline (2010-2020)')
)
yearly_monthly = df_kal.groupby(['year_cat', 'month']).agg(Tx=('Tx', 'mean'), RH=('RH_avg', 'mean'), RR=('RR', 'mean')).reset_index()

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
palette_cat = {'Normal Baseline (2010-2020)': '#3498db', '2019 (Severe Drought)': '#e67e22', '2015 (Extreme El Nino)': '#e74c3c'}
for cat in palette_cat.keys():
    sub = yearly_monthly[yearly_monthly['year_cat'] == cat]
    axes[0].plot(sub['month'], sub['Tx'], label=cat, color=palette_cat[cat], lw=2.5, marker='o')
    axes[1].plot(sub['month'], sub['RH'], label=cat, color=palette_cat[cat], lw=2.5, marker='s')
    axes[2].plot(sub['month'], sub['RR'], label=cat, color=palette_cat[cat], lw=2.5, marker='^')

for ax, ylabel, title in zip(axes, ['Max Temp (°C)', 'Relative Humidity (%)', 'Rainfall (mm/day)'],
                             ['Max Temperature in Extreme Years', 'Humidity Anomaly in Extreme Years', 'Rainfall Deficit in Extreme Years']):
    ax.axvspan(6, 10, color='#e74c3c', alpha=0.12)
    ax.set_xticks(months_x); ax.set_xticklabels(month_labels); ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(alpha=0.2)
axes[0].legend(loc='lower center', fontsize=8.5, framealpha=0.5)

fig.suptitle('Impact of Climate Anomalies on Fire Weather in Kalimantan (2015 & 2019 vs Baseline)', fontsize=13, fontweight='bold', color='white', y=1.02)
fig.tight_layout()
savefig(fig, 'K02_historical_extreme_years_2015_2019.png')

# K03. Provincial Vulnerability Profile
prov_clim = df_kal.groupby('province_name').agg(
    Tx_mean=('Tx', 'mean'), dry_days_pct=('is_dry_day', lambda x: x.mean() * 100),
    wind_max_mean=('ff_x', 'mean'), fire_danger_days=('fire_danger_day', 'sum'), total_obs=('station_id', 'count')
).reset_index()
prov_clim['fire_danger_pct'] = (prov_clim['fire_danger_days'] / prov_clim['total_obs']) * 100

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
prov_names = prov_clim['province_name'].tolist()
prov_short = [p.replace('Kalimantan ', 'Kal. ') for p in prov_names]
bar_colors = [PROV_PALETTE.get(p, '#7f8c8d') for p in prov_names]

axes[0, 0].bar(prov_short, prov_clim['Tx_mean'], color=bar_colors, alpha=0.85, edgecolor='white', lw=0.6)
axes[0, 0].set_ylabel('Mean Max Temp (°C)'); axes[0, 0].set_title('Mean Maximum Temperature (2010-2020)'); axes[0, 0].set_ylim(30, 34); axes[0, 0].grid(axis='y', alpha=0.2)

axes[0, 1].bar(prov_short, prov_clim['dry_days_pct'], color=bar_colors, alpha=0.85, edgecolor='white', lw=0.6)
axes[0, 1].set_ylabel('Dry Days (%)'); axes[0, 1].set_title('Frequency of Dry Days (Rainfall < 2mm)'); axes[0, 1].set_ylim(40, 65); axes[0, 1].grid(axis='y', alpha=0.2)

axes[1, 0].bar(prov_short, prov_clim['wind_max_mean'], color=bar_colors, alpha=0.85, edgecolor='white', lw=0.6)
axes[1, 0].set_ylabel('Max Wind Speed (m/s)'); axes[1, 0].set_title('Wind Hazard Profile (Max Wind Speed m/s)'); axes[1, 0].set_ylim(0, 6); axes[1, 0].grid(axis='y', alpha=0.2)

axes[1, 1].bar(prov_short, prov_clim['fire_danger_pct'], color=bar_colors, alpha=0.85, edgecolor='white', lw=0.6)
axes[1, 1].set_ylabel('Fire Danger Days (%)'); axes[1, 1].set_title('Climatological Fire Weather Vulnerability Index (%)'); axes[1, 1].grid(axis='y', alpha=0.2)

fig.suptitle('Provincial Climatological Fire Vulnerability Baseline across Kalimantan (2010-2020)', fontsize=14, fontweight='bold', color='white', y=1.02)
fig.tight_layout()
savefig(fig, 'K03_provincial_climate_vulnerability_profile.png')

# K04. Correlation Matrix
corr_vars = ['Tx', 'Tn', 'Tavg', 'RH_avg', 'RR', 'ss', 'ff_x', 'ff_avg', 'fire_danger_day']
corr_data = df_kal[corr_vars].dropna().corr()
rename_corr = {'Tx': 'Max Temp (Tx)', 'Tn': 'Min Temp (Tn)', 'Tavg': 'Avg Temp (Tavg)', 'RH_avg': 'Humidity (RH)', 'RR': 'Rainfall (RR)', 'ss': 'Sunshine (ss)', 'ff_x': 'Max Wind (ff_x)', 'ff_avg': 'Avg Wind (ff_avg)', 'fire_danger_day': 'Fire Danger Flag'}
corr_data.rename(index=rename_corr, columns=rename_corr, inplace=True)

fig, ax = plt.subplots(figsize=(11, 9))
cmap = LinearSegmentedColormap.from_list('rg_div', ['#2980b9', '#1a252f', '#c0392b'], N=256)
im = ax.imshow(corr_data.values, cmap=cmap, vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
ax.set_xticks(range(len(corr_data))); ax.set_yticks(range(len(corr_data)))
ax.set_xticklabels(corr_data.columns, rotation=40, ha='right'); ax.set_yticklabels(corr_data.index)
for i in range(len(corr_data)):
    for j in range(len(corr_data)):
        val = corr_data.values[i, j]
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', color='white' if abs(val) > 0.4 else '#a0aec0', fontsize=8)
ax.set_title('Pearson Correlation Matrix: Decadal Climate Variables (87,238 Records)', pad=14)
savefig(fig, 'K04_correlation_matrix_decadal_climate.png')

# K05. Spatial Map of 24 BMKG Stations
geo_data = ensure_geojson()
kal_features = [ft for ft in geo_data['features'] if 'alimantan' in ft['properties'].get('PROVINSI', '')]
non_kal_features = [ft for ft in geo_data['features'] if 'alimantan' not in ft['properties'].get('PROVINSI', '')]

fig, ax = plt.subplots(figsize=(14, 10))
draw_boundaries(ax, non_kal_features, facecolor='#2d3d4e', edgecolor='#3d5166', linewidth=0.5, alpha=0.5)
draw_boundaries(ax, kal_features, use_prov_colors=True, edgecolor='#ffffff', linewidth=1.2, alpha=0.45)

for _, st in kal_sta.iterrows():
    ax.scatter(st['longitude'], st['latitude'], s=140, color='#f1c40f', edgecolors='#1e2d3d', lw=1.5, zorder=5)
    short_name = st['station_name'].replace('Stasiun Meteorologi ', 'Stamet ').replace('Stasiun Klimatologi ', 'Staklim ').replace('Stasiun Geofisika ', 'Stageof ')
    ax.text(st['longitude'], st['latitude'] + 0.15, short_name, fontsize=7.5, color='white', ha='center', va='bottom',
            fontweight='bold', zorder=6, path_effects=[pe.withStroke(linewidth=2, foreground='#1e2d3d')])

ax.set_xlim(107.8, 120.0); ax.set_ylim(-4.8, 5.0)
ax.set_title('Network of 24 BMKG Weather Stations across Kalimantan (2010-2020 Decadal Dataset)', pad=14)
savefig(fig, 'K05_spatial_station_network_kalimantan.png')

# K06. 11-Year Decadal Trend of Fire Danger Days
yearly_danger = df_kal.groupby(['year', 'province_name'])['fire_danger_day'].sum().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(14, 6.5))
years = yearly_danger.index
bottom = np.zeros(len(years))
for prov in yearly_danger.columns:
    vals = yearly_danger[prov].values
    ax.bar(years, vals, bottom=bottom, label=prov.replace('Kalimantan ', 'Kal. '), color=PROV_PALETTE.get(prov, '#7f8c8d'), alpha=0.85, edgecolor='white', lw=0.4)
    bottom += vals

ax.set_xticks(years); ax.set_ylabel('Total High Fire Danger Days'); ax.set_title('11-Year Trend of High Fire Danger Days in Kalimantan (2010-2020)')
ax.legend(loc='upper left', fontsize=9, framealpha=0.5); ax.grid(axis='y', alpha=0.2)
savefig(fig, 'K06_fire_weather_risk_index_decadal_trend.png')

print("\n" + "=" * 70)
print("[PIPELINE 03 COMPLETED SUCCESSFULLY - 6 CHARTS REPRODUCED]")
print("=" * 70)
