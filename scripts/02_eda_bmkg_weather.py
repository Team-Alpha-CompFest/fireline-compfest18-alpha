"""
Pipeline 02: BMKG Kalimantan Weather Data Collection & Fire-Correlation EDA (2024-2026)
Source: Open-Meteo Archive API / ERA5 Reanalysis (14 BMKG Stations x 5 Kalimantan Provinces)
Context: FIRELINE Platform - COMPFEST 18 Case Study (Team Alpha)
"""

import os
import sys
import json
import time
import urllib.request
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import pearsonr

# Import local geospatial utility
sys.path.append(os.path.dirname(__file__))
from utils_geo import PROV_PALETTE

warnings.filterwarnings('ignore')

# ============================================================
# PATH CONFIGURATION
# ============================================================
WEATHER_CSV  = 'datasets/bmkg_kalimantan_weather_2024_2026.csv'
HOTSPOT_CSV  = 'EDA/01_fireline_hotspot_kalimantan/04_feature_engineering/fireline_hotspot_featured.csv'
OUT_BASE     = 'EDA/02_bmkg_weather_kalimantan'
VIZ_DIR      = os.path.join(OUT_BASE, 'visualizations')
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
# 1. LOAD DATASETS
# ============================================================
print("\n" + "=" * 70)
print("STAGE 1: LOADING WEATHER & HOTSPOT DATASETS")
print("=" * 70)

df_weather = pd.read_csv(WEATHER_CSV, parse_dates=['date'])
print(f"Weather records: {len(df_weather):,} rows across {df_weather['city'].nunique()} stations")

df_hotspot = pd.read_csv(HOTSPOT_CSV, parse_dates=['acq_date'])
print(f"Hotspot records: {len(df_hotspot):,} rows")

# Daily aggregate summaries
df_prov = df_weather.groupby(['date', 'province']).agg(
    temp_max=('temperature_2m_max', 'mean'),
    temp_mean=('temperature_2m_mean', 'mean'),
    precip=('precipitation_sum', 'mean'),
    wind_max=('windspeed_10m_max', 'mean'),
    humidity_min=('relative_humidity_2m_min', 'mean'),
    humidity_mean=('relative_humidity_2m_mean', 'mean'),
    vpd_max=('vapor_pressure_deficit_max', 'mean'),
    et0_fao=('et0_fao_evapotranspiration', 'mean'),
    sunshine_h=('sunshine_hours', 'mean'),
    is_dry_day=('is_dry_day', 'mean'),
).reset_index()

df_kalimantan = df_weather.groupby('date').agg(
    temp_max=('temperature_2m_max', 'mean'),
    temp_mean=('temperature_2m_mean', 'mean'),
    precip=('precipitation_sum', 'mean'),
    wind_max=('windspeed_10m_max', 'mean'),
    humidity_mean=('relative_humidity_2m_mean', 'mean'),
    humidity_min=('relative_humidity_2m_min', 'mean'),
    vpd_max=('vapor_pressure_deficit_max', 'mean'),
    et0_fao=('et0_fao_evapotranspiration', 'mean'),
    sunshine_h=('sunshine_hours', 'mean'),
).reset_index()

hs_kal_daily = df_hotspot.groupby('acq_date').agg(
    hotspot_count=('frp', 'count'),
    total_frp=('frp', 'sum'),
    mean_frp=('frp', 'mean'),
).reset_index().rename(columns={'acq_date': 'date'})

merged = pd.merge(df_kalimantan, hs_kal_daily, on='date', how='left')
merged['hotspot_count'] = merged['hotspot_count'].fillna(0)
merged['total_frp']     = merged['total_frp'].fillna(0)
merged['month']         = merged['date'].dt.month
merged['season']        = merged['month'].apply(lambda m: 'Dry' if m in [6,7,8,9,10] else 'Wet')

# ============================================================
# 2. GENERATE 6 WEATHER EDA CHARTS
# ============================================================
print("\n" + "=" * 70)
print("STAGE 2: GENERATING WEATHER-FIRE CORRELATION VISUALIZATIONS")
print("=" * 70)

# W01. Monthly Weather Overview
monthly_w = merged.groupby(merged['date'].dt.to_period('M')).agg(
    temp_mean=('temp_mean', 'mean'), temp_max=('temp_max', 'mean'),
    precip=('precip', 'sum'), humidity_mean=('humidity_mean', 'mean'),
    wind_max=('wind_max', 'mean')
).reset_index()
monthly_w['date_dt'] = monthly_w['date'].dt.to_timestamp()

fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
axes[0].plot(monthly_w['date_dt'], monthly_w['temp_mean'], color='#e74c3c', lw=2, label='Mean Temp (°C)')
axes[0].plot(monthly_w['date_dt'], monthly_w['temp_max'], color='#f39c12', lw=1.5, ls='--', label='Max Temp (°C)')
axes[0].set_ylabel('Temperature (°C)'); axes[0].legend(loc='upper right', framealpha=0.4); axes[0].grid(axis='y', alpha=0.3)
axes[0].set_title('Monthly Temperature Trend across Kalimantan')

axes[1].bar(monthly_w['date_dt'], monthly_w['precip'], width=25, color='#3498db', alpha=0.8, label='Precipitation (mm)')
axes[1].set_ylabel('Total Precip (mm)'); axes[1].legend(loc='upper right', framealpha=0.4); axes[1].grid(axis='y', alpha=0.3)
axes[1].set_title('Monthly Cumulative Precipitation (mm)')

ax2 = axes[2].twinx()
axes[2].plot(monthly_w['date_dt'], monthly_w['humidity_mean'], color='#1abc9c', lw=2, label='Humidity (%)')
ax2.plot(monthly_w['date_dt'], monthly_w['wind_max'], color='#e67e22', lw=1.8, ls='-.', label='Max Wind (km/h)')
axes[2].set_ylabel('Humidity (%)', color='#1abc9c'); ax2.set_ylabel('Wind Speed (km/h)', color='#e67e22')
axes[2].legend(loc='upper left', framealpha=0.4); ax2.legend(loc='upper right', framealpha=0.4); axes[2].grid(axis='y', alpha=0.3)
axes[2].set_title('Mean Relative Humidity and Maximum Wind Speed')

for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.autofmt_xdate(rotation=30)
fig.suptitle('Monthly Meteorological Overview of Kalimantan (2024-2026)', fontsize=14, fontweight='bold', color='white', y=1.01)
savefig(fig, 'W01_monthly_weather_overview.png')

# W02. Weather vs Hotspot Count (4 Panels)
monthly_hs = merged.groupby(merged['date'].dt.to_period('M')).agg(
    hotspot_count=('hotspot_count', 'sum'), temp_max=('temp_max', 'mean'),
    precip=('precip', 'sum'), humidity_mean=('humidity_mean', 'mean'),
    vpd_max=('vpd_max', 'mean')
).reset_index()
monthly_hs['date_dt'] = monthly_hs['date'].dt.to_timestamp()

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
configs = [
    ('temp_max', 'Max Temperature (°C)', '#e74c3c'),
    ('precip', 'Monthly Precipitation (mm)', '#3498db'),
    ('humidity_mean', 'Mean Humidity (%)', '#1abc9c'),
    ('vpd_max', 'Max VPD (kPa)', '#e67e22'),
]

for idx, (var, label, col) in enumerate(configs):
    ax = axes[idx // 2, idx % 2]
    ax2 = ax.twinx()
    ax.bar(monthly_hs['date_dt'], monthly_hs['hotspot_count'], width=25, alpha=0.55, color='#c0392b')
    ax2.plot(monthly_hs['date_dt'], monthly_hs[var], color=col, lw=2.2, marker='o', ms=5)
    r, _ = pearsonr(monthly_hs['hotspot_count'].fillna(0), monthly_hs[var].fillna(0))
    ax.set_title(f'Hotspot Count vs {label}\n(Pearson r = {r:+.2f})', fontsize=11)
    ax.set_ylabel('Hotspot Count', color='#c0392b'); ax2.set_ylabel(label, color=col)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y')); ax.grid(axis='y', alpha=0.2)

fig.suptitle('Monthly Fire Hotspot Count vs Weather Variables across Kalimantan', fontsize=13, fontweight='bold', color='white', y=1.01)
fig.tight_layout()
savefig(fig, 'W02_weather_vs_hotspot_count.png')

# W03. Correlation Heatmap
corr_vars = ['temp_max', 'temp_mean', 'precip', 'wind_max', 'humidity_mean', 'humidity_min', 'vpd_max', 'et0_fao', 'sunshine_h', 'hotspot_count', 'total_frp']
corr_data = merged[[c for c in corr_vars if c in merged.columns]].dropna().corr()
rename_map = {
    'temp_max': 'Temp Max', 'temp_mean': 'Temp Mean', 'precip': 'Precipitation',
    'wind_max': 'Wind Max', 'humidity_mean': 'Humidity Mean', 'humidity_min': 'Humidity Min',
    'vpd_max': 'VPD Max', 'et0_fao': 'Evapotranspiration', 'sunshine_h': 'Sunshine Hours',
    'hotspot_count': 'Hotspot Count', 'total_frp': 'Total FRP'
}
corr_data.rename(index=rename_map, columns=rename_map, inplace=True)

fig, ax = plt.subplots(figsize=(12, 9))
cmap = LinearSegmentedColormap.from_list('div', ['#2980b9', '#1a252f', '#c0392b'], N=256)
im = ax.imshow(corr_data.values, cmap=cmap, vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
ax.set_xticks(range(len(corr_data))); ax.set_yticks(range(len(corr_data)))
ax.set_xticklabels(corr_data.columns, rotation=45, ha='right'); ax.set_yticklabels(corr_data.index)
for i in range(len(corr_data)):
    for j in range(len(corr_data)):
        val = corr_data.values[i, j]
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', color='white' if abs(val) > 0.4 else '#a0aec0', fontsize=8)
ax.set_title('Pearson Correlation Matrix: Meteorological Variables vs Fire Indicators', pad=14)
savefig(fig, 'W03_correlation_heatmap_weather_fire.png')

# W04. Province Dry Season Scatter
prov_dry_w = df_prov[df_prov['date'].dt.month.isin([6,7,8,9,10])].groupby('province').agg(
    temp_max=('temp_max', 'mean'), vpd_max=('vpd_max', 'mean'), humidity_min=('humidity_min', 'mean')
).reset_index()
hs_prov_dry = df_hotspot[df_hotspot['acq_date'].dt.month.isin([6,7,8,9,10])].groupby('kalimantan_region').agg(
    hotspot_count=('frp', 'count'), total_frp=('frp', 'sum')
).reset_index().rename(columns={'kalimantan_region': 'province'})
prov_merged = prov_dry_w.merge(hs_prov_dry, on='province', how='inner')

fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
metrics = [('vpd_max', 'Mean Max VPD (kPa)'), ('humidity_min', 'Mean Min Humidity (%)'), ('temp_max', 'Mean Max Temp (°C)')]
for idx, (var, label) in enumerate(metrics):
    ax = axes[idx]
    colors = [PROV_PALETTE.get(p, '#7f8c8d') for p in prov_merged['province']]
    ax.scatter(prov_merged[var], prov_merged['hotspot_count'], s=prov_merged['total_frp'] / 1200 + 80,
               c=colors, zorder=5, edgecolors='white', lw=0.8, alpha=0.9)
    for _, row in prov_merged.iterrows():
        ax.annotate(row['province'].replace('Kalimantan ', 'Kal. '), (row[var], row['hotspot_count']),
                    fontsize=8.5, color='white', ha='center', xytext=(0, 8), textcoords='offset points')
    ax.set_xlabel(label); ax.set_ylabel('Total Hotspot Count' if idx == 0 else ''); ax.grid(alpha=0.2)
    ax.set_title(f'{label} vs Fire Activity', fontsize=10.5)

fig.suptitle('Provincial Dry Season Weather vs Fire Activity (Bubble Size = Total FRP)', fontsize=13, fontweight='bold', color='white', y=1.02)
fig.tight_layout()
savefig(fig, 'W04_province_weather_vs_fire_drySeason.png')

# W05. Rolling 14-Day Timeseries
roll_df = merged.sort_values('date').set_index('date').rolling('14D', min_periods=5).mean().reset_index()
fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
for ax in axes:
    ax.axvspan(pd.Timestamp('2024-06-01'), pd.Timestamp('2024-10-31'), alpha=0.10, color='#e74c3c')
    ax.axvspan(pd.Timestamp('2025-06-01'), pd.Timestamp('2025-10-31'), alpha=0.10, color='#e74c3c')

axes[0].plot(roll_df['date'], roll_df['hotspot_count'], color='#c0392b', lw=2)
axes[0].set_ylabel('Hotspot Count (14-day MA)', color='#c0392b'); axes[0].set_title('Fire Hotspot Activity (14-Day Rolling Average)')

axes[1].plot(roll_df['date'], roll_df['temp_max'], color='#e74c3c', lw=2, label='Max Temp (°C)')
axes[1].plot(roll_df['date'], roll_df['vpd_max'], color='#e67e22', lw=1.8, ls='-.', label='Max VPD (kPa)')
axes[1].set_ylabel('Temp / VPD'); axes[1].legend(loc='upper right', framealpha=0.4); axes[1].set_title('Atmospheric Thermal & Dryness Trend')

axes[2].plot(roll_df['date'], roll_df['precip'], color='#3498db', lw=2, label='Precipitation (mm)')
ax_hum = axes[2].twinx()
ax_hum.plot(roll_df['date'], roll_df['humidity_mean'], color='#1abc9c', lw=1.8, label='Humidity (%)')
axes[2].set_ylabel('Precipitation mm', color='#3498db'); ax_hum.set_ylabel('Humidity %', color='#1abc9c')
axes[2].legend(loc='upper left', framealpha=0.4); ax_hum.legend(loc='upper right', framealpha=0.4); axes[2].set_title('Hydrological Dynamics')

axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.autofmt_xdate(rotation=30)
fig.suptitle('14-Day Rolling Average: Atmospheric Fire Weather Conditions vs Fire Activity', fontsize=13, fontweight='bold', color='white', y=1.01)
savefig(fig, 'W05_rolling14d_weather_fire_timeseries.png')

# W06. Dry vs Wet Season Boxplot
df_weather['season'] = df_weather['month'].apply(lambda m: 'Dry Season (Jun-Oct)' if m in [6,7,8,9,10] else 'Wet Season (Nov-May)')
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
plot_vars = [
    ('temperature_2m_max', 'Max Temperature (°C)'), ('precipitation_sum', 'Daily Rainfall (mm)'),
    ('windspeed_10m_max', 'Max Wind Speed (km/h)'), ('relative_humidity_2m_min', 'Min Humidity (%)'),
    ('vapor_pressure_deficit_max', 'Max VPD (kPa)'), ('et0_fao_evapotranspiration', 'Evapotranspiration (mm)')
]
for idx, (var, label) in enumerate(plot_vars):
    ax = axes[idx // 3, idx % 3]
    d_v = df_weather[df_weather['season'] == 'Dry Season (Jun-Oct)'][var].dropna()
    w_v = df_weather[df_weather['season'] == 'Wet Season (Nov-May)'][var].dropna()
    bp = ax.boxplot([d_v, w_v], patch_artist=True, widths=0.55, showfliers=False, medianprops={'color': 'white', 'lw': 2})
    bp['boxes'][0].set_facecolor('#c0392b'); bp['boxes'][0].set_alpha(0.75)
    bp['boxes'][1].set_facecolor('#2980b9'); bp['boxes'][1].set_alpha(0.75)
    ax.set_xticklabels(['Dry Season', 'Wet Season']); ax.set_title(label); ax.grid(axis='y', alpha=0.2)

fig.suptitle('Meteorological Distribution Comparison: Dry Season vs Wet Season across Kalimantan', fontsize=13, fontweight='bold', color='white', y=1.01)
fig.tight_layout()
savefig(fig, 'W06_dry_vs_wet_season_weather.png')

print("\n" + "=" * 70)
print("[PIPELINE 02 COMPLETED SUCCESSFULLY - 6 CHARTS REPRODUCED]")
print("=" * 70)
