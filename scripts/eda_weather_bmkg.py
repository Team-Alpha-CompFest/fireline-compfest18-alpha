"""
EDA: BMKG Kalimantan Weather Data 2024-2026
Simple EDA with fire-correlation focus
Output: EDA/02_bmkg_weather_kalimantan/
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PATHS
# ============================================================
WEATHER_PATH = 'datasets/bmkg_kalimantan_weather_2024_2026.csv'
HOTSPOT_PATH = 'EDA/01_fireline_hotspot_kalimantan/04_feature_engineering/fireline_hotspot_featured.csv'
OUT_DIR      = 'EDA/02_bmkg_weather_kalimantan'
VIZ_DIR      = os.path.join(OUT_DIR, 'visualizations')
os.makedirs(VIZ_DIR, exist_ok=True)

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

PROV_PALETTE = {
    'Kalimantan Barat':   '#2980b9',
    'Kalimantan Tengah':  '#e67e22',
    'Kalimantan Timur':   '#27ae60',
    'Kalimantan Selatan': '#c0392b',
    'Kalimantan Utara':   '#8e44ad',
}

def savefig(fig, name):
    path = os.path.join(VIZ_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.25,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'  Saved: {name}')

# ============================================================
# LOAD DATA
# ============================================================
print("Loading weather data...")
df = pd.read_csv(WEATHER_PATH, parse_dates=['date'])
print(f"  Weather rows: {len(df):,} | Date: {df['date'].min().date()} to {df['date'].max().date()}")

print("Loading hotspot data...")
hs = pd.read_csv(HOTSPOT_PATH, parse_dates=['acq_date'])
print(f"  Hotspot rows: {len(hs):,}")

# Daily hotspot count and mean FRP by province and date
hs_daily = hs.groupby(['acq_date', 'kalimantan_region']).agg(
    hotspot_count=('frp', 'count'),
    mean_frp=('frp', 'mean'),
    total_frp=('frp', 'sum'),
    max_frp=('frp', 'max')
).reset_index().rename(columns={'acq_date': 'date', 'kalimantan_region': 'province'})

# Province-level daily weather average (across cities in same province)
df_prov = df.groupby(['date', 'province']).agg(
    temp_max=('temperature_2m_max', 'mean'),
    temp_min=('temperature_2m_min', 'mean'),
    temp_mean=('temperature_2m_mean', 'mean'),
    precip=('precipitation_sum', 'mean'),
    wind_max=('windspeed_10m_max', 'mean'),
    humidity_min=('relative_humidity_2m_min', 'mean'),
    humidity_mean=('relative_humidity_2m_mean', 'mean'),
    vpd_max=('vapor_pressure_deficit_max', 'mean'),
    et0=('et0_fao_evapotranspiration', 'mean'),
    sunshine_h=('sunshine_hours', 'mean'),
    is_dry_day=('is_dry_day', 'mean'),
).reset_index()

# Kalimantan-wide daily average weather
df_kalimantan = df.groupby('date').agg(
    temp_max=('temperature_2m_max', 'mean'),
    temp_mean=('temperature_2m_mean', 'mean'),
    precip=('precipitation_sum', 'mean'),
    wind_max=('windspeed_10m_max', 'mean'),
    humidity_mean=('relative_humidity_2m_mean', 'mean'),
    humidity_min=('relative_humidity_2m_min', 'mean'),
    vpd_max=('vapor_pressure_deficit_max', 'mean'),
    sunshine_h=('sunshine_hours', 'mean'),
).reset_index()

# Kalimantan-wide daily hotspot (all provinces combined)
hs_kal_daily = hs.groupby('acq_date').agg(
    hotspot_count=('frp', 'count'),
    total_frp=('frp', 'sum'),
    mean_frp=('frp', 'mean'),
).reset_index().rename(columns={'acq_date': 'date'})

# Master merged daily dataset (Kalimantan-wide)
merged = pd.merge(df_kalimantan, hs_kal_daily, on='date', how='left')
merged['hotspot_count'] = merged['hotspot_count'].fillna(0)
merged['total_frp']     = merged['total_frp'].fillna(0)
merged['month'] = merged['date'].dt.month
merged['season'] = merged['month'].apply(
    lambda m: 'Dry' if m in {6,7,8,9,10} else 'Wet'
)

print(f"\nMerged daily dataset: {len(merged):,} rows")
print(f"Province-level merged: {len(df_prov):,} rows")

# ============================================================
# CHART 1: Monthly Weather Overview (temp + precip dual-axis)
# ============================================================
print("\n[CHART 1] Monthly weather overview...")
monthly_w = merged.groupby(merged['date'].dt.to_period('M')).agg(
    temp_mean=('temp_mean','mean'),
    temp_max=('temp_max','mean'),
    precip=('precip','sum'),
    humidity_mean=('humidity_mean','mean'),
    wind_max=('wind_max','mean'),
).reset_index()
monthly_w['date_dt'] = monthly_w['date'].dt.to_timestamp()

fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.patch.set_facecolor('#1e2d3d')

# -- Subplot 1: Temperature
ax = axes[0]
ax.set_facecolor('#1e2d3d')
ax.fill_between(monthly_w['date_dt'], monthly_w['temp_mean'],
                alpha=0.3, color='#e74c3c')
ax.plot(monthly_w['date_dt'], monthly_w['temp_mean'], color='#e74c3c',
        lw=2, label='Mean Temp')
ax.plot(monthly_w['date_dt'], monthly_w['temp_max'], color='#f39c12',
        lw=1.5, ls='--', label='Max Temp')
ax.set_ylabel('Temperature (C)', color='white')
ax.legend(loc='upper right', fontsize=9, framealpha=0.4)
ax.set_title('Monthly Temperature Trend -- Kalimantan Average', pad=8)
ax.axvspan(pd.Timestamp('2024-06-01'), pd.Timestamp('2024-11-01'), alpha=0.08, color='#e74c3c')
ax.axvspan(pd.Timestamp('2025-06-01'), pd.Timestamp('2025-11-01'), alpha=0.08, color='#e74c3c')
ax.grid(axis='y', alpha=0.3)

# -- Subplot 2: Precipitation
ax = axes[1]
ax.set_facecolor('#1e2d3d')
bars = ax.bar(monthly_w['date_dt'], monthly_w['precip'],
              width=25, color='#3498db', alpha=0.8, label='Total Precip')
ax.set_ylabel('Monthly Precipitation (mm)', color='white')
ax.legend(loc='upper right', fontsize=9, framealpha=0.4)
ax.set_title('Monthly Precipitation -- Lower = Higher Fire Risk', pad=8)
ax.axvspan(pd.Timestamp('2024-06-01'), pd.Timestamp('2024-11-01'), alpha=0.08, color='#e74c3c', label='Dry Season')
ax.axvspan(pd.Timestamp('2025-06-01'), pd.Timestamp('2025-11-01'), alpha=0.08, color='#e74c3c')
ax.grid(axis='y', alpha=0.3)

# -- Subplot 3: Humidity and Wind
ax = axes[2]
ax.set_facecolor('#1e2d3d')
ax2 = ax.twinx()
ax.plot(monthly_w['date_dt'], monthly_w['humidity_mean'], color='#1abc9c',
        lw=2, label='Humidity (%)')
ax.fill_between(monthly_w['date_dt'], monthly_w['humidity_mean'], alpha=0.2, color='#1abc9c')
ax2.plot(monthly_w['date_dt'], monthly_w['wind_max'], color='#e67e22',
         lw=1.8, ls='-.', label='Max Wind (km/h)')
ax.set_ylabel('Mean Humidity (%)', color='#1abc9c')
ax2.set_ylabel('Max Wind Speed (km/h)', color='#e67e22')
ax2.tick_params(colors='#e67e22')
ax.legend(loc='upper left', fontsize=9, framealpha=0.4)
ax2.legend(loc='upper right', fontsize=9, framealpha=0.4)
ax.set_title('Mean Humidity and Max Wind Speed', pad=8)
ax.grid(axis='y', alpha=0.3)

for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

fig.autofmt_xdate(rotation=35, ha='right')
fig.suptitle('Monthly Weather Overview -- Kalimantan (Aug 2024 to May 2026)',
             fontsize=14, fontweight='bold', color='white', y=1.01)
savefig(fig, 'W01_monthly_weather_overview.png')

# ============================================================
# CHART 2: Weather vs Hotspot Count (dual-axis monthly)
# ============================================================
print("[CHART 2] Weather vs hotspot correlation...")
monthly_hs = merged.groupby(merged['date'].dt.to_period('M')).agg(
    hotspot_count=('hotspot_count','sum'),
    total_frp=('total_frp','sum'),
    temp_max=('temp_max','mean'),
    precip=('precip','sum'),
    humidity_mean=('humidity_mean','mean'),
    vpd_max=('vpd_max','mean'),
).reset_index()
monthly_hs['date_dt'] = monthly_hs['date'].dt.to_timestamp()

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.patch.set_facecolor('#1e2d3d')
subplot_configs = [
    ('temp_max', 'Max Temperature (C)', '#e74c3c', 'positive'),
    ('precip',   'Monthly Precipitation (mm)', '#3498db', 'negative'),
    ('humidity_mean','Mean Humidity (%)', '#1abc9c', 'negative'),
    ('vpd_max',  'Max VPD (kPa)', '#e67e22', 'positive'),
]
for idx, (var, label, color, direction) in enumerate(subplot_configs):
    ax = axes[idx // 2][idx % 2]
    ax.set_facecolor('#1e2d3d')
    ax2 = ax.twinx()

    ax.bar(monthly_hs['date_dt'], monthly_hs['hotspot_count'],
           width=25, alpha=0.55, color='#c0392b', label='Hotspot Count')
    ax2.plot(monthly_hs['date_dt'], monthly_hs[var],
             color=color, lw=2.2, marker='o', ms=5, label=label)

    r, p = pearsonr(
        monthly_hs['hotspot_count'].fillna(0),
        monthly_hs[var].fillna(monthly_hs[var].mean())
    )
    sign = '+' if r > 0 else ''
    ax.set_title(f'Hotspot Count vs {label}\n(Pearson r = {sign}{r:.2f})', fontsize=11)
    ax.set_ylabel('Monthly Hotspot Count', color='#c0392b')
    ax2.set_ylabel(label, color=color)
    ax2.tick_params(colors=color)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.tick_params(axis='x', rotation=30)
    ax.grid(axis='y', alpha=0.2)

fig.suptitle('Monthly Fire Hotspot Count vs Weather Variables -- Kalimantan-wide',
             fontsize=13, fontweight='bold', color='white', y=1.01)
fig.tight_layout()
savefig(fig, 'W02_weather_vs_hotspot_count.png')

# ============================================================
# CHART 3: Correlation heatmap (weather x fire metrics)
# ============================================================
print("[CHART 3] Correlation heatmap...")
avail_cols = [c for c in [
    'temp_max', 'temp_mean', 'precip', 'wind_max',
    'humidity_mean', 'humidity_min', 'vpd_max', 'et0_fao', 'sunshine_h',
    'hotspot_count', 'total_frp', 'mean_frp'
] if c in merged.columns]
corr_df = merged[avail_cols].dropna()

corr_matrix = corr_df.corr()
# Rename for display
rename_map = {
    'temp_max': 'Temp Max', 'temp_mean': 'Temp Mean',
    'precip': 'Precipitation', 'wind_max': 'Wind Max',
    'humidity_mean': 'Humidity Mean', 'humidity_min': 'Humidity Min',
    'vpd_max': 'VPD Max', 'et0_fao': 'Evapotranspiration',
    'sunshine_h': 'Sunshine Hours',
    'hotspot_count': 'Hotspot Count', 'total_frp': 'Total FRP', 'mean_frp': 'Mean FRP'
}
corr_matrix.rename(index=rename_map, columns=rename_map, inplace=True)

fig, ax = plt.subplots(figsize=(13, 10))
fig.patch.set_facecolor('#1e2d3d')
ax.set_facecolor('#1e2d3d')

cmap = LinearSegmentedColormap.from_list('rg_diverge',
    ['#2980b9', '#1a252f', '#c0392b'], N=256)
im = ax.imshow(corr_matrix.values, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
cbar.set_label('Pearson r', color='white', fontsize=10)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

labels = corr_matrix.columns.tolist()
ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(labels, fontsize=9)

for i in range(len(labels)):
    for j in range(len(labels)):
        val = corr_matrix.values[i, j]
        txt_color = 'white' if abs(val) > 0.45 else '#a0aec0'
        ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                fontsize=7.5, color=txt_color, fontweight='bold' if abs(val) > 0.5 else 'normal')

# Highlight fire metric rows/cols
n = len(labels)
fire_idx = [labels.index(x) for x in ['Hotspot Count', 'Total FRP', 'Mean FRP'] if x in labels]
for fi in fire_idx:
    ax.axhline(fi - 0.5, color='#f39c12', lw=1.2, alpha=0.7)
    ax.axhline(fi + 0.5, color='#f39c12', lw=1.2, alpha=0.7)
    ax.axvline(fi - 0.5, color='#f39c12', lw=1.2, alpha=0.7)
    ax.axvline(fi + 0.5, color='#f39c12', lw=1.2, alpha=0.7)

ax.set_title('Pearson Correlation Matrix: Weather Variables vs Fire Metrics\n'
             '(Orange borders highlight fire metric rows/columns)',
             pad=14, color='white')
savefig(fig, 'W03_correlation_heatmap_weather_fire.png')

# ============================================================
# CHART 4: Province-level VPD and Hotspot Comparison (dry season)
# ============================================================
print("[CHART 4] Province VPD vs hotspot (dry season)...")
dry = merged[merged['season'] == 'Dry'].copy()

# Province-level daily weather
prov_dry_w = df_prov[df_prov['date'].dt.month.isin([6,7,8,9,10])].groupby('province').agg(
    temp_max=('temp_max','mean'),
    precip=('precip','mean'),
    vpd_max=('vpd_max','mean'),
    humidity_min=('humidity_min','mean'),
    wind_max=('wind_max','mean'),
).reset_index()

# Province-level daily hotspot during dry season
hs_prov_dry = hs[hs['acq_date'].dt.month.isin([6,7,8,9,10])].groupby('kalimantan_region').agg(
    hotspot_count=('frp','count'),
    total_frp=('frp','sum'),
    mean_frp=('frp','mean'),
).reset_index().rename(columns={'kalimantan_region':'province'})

prov_merged = prov_dry_w.merge(hs_prov_dry, on='province', how='inner')

fig, axes = plt.subplots(1, 3, figsize=(17, 6))
fig.patch.set_facecolor('#1e2d3d')

metrics = [
    ('vpd_max',      'Mean Max VPD (kPa)',    '#e67e22'),
    ('humidity_min', 'Mean Min Humidity (%)', '#1abc9c'),
    ('temp_max',     'Mean Max Temp (C)',      '#e74c3c'),
]

for idx, (var, xlabel, color) in enumerate(metrics):
    ax = axes[idx]
    ax.set_facecolor('#1e2d3d')
    provs = prov_merged['province'].tolist()
    colors = [PROV_PALETTE.get(p, '#7f8c8d') for p in provs]

    sc = ax.scatter(prov_merged[var], prov_merged['hotspot_count'],
                    s=prov_merged['total_frp'] / 1200 + 80,
                    c=colors, zorder=5, edgecolors='white', linewidths=0.8, alpha=0.92)

    for _, row in prov_merged.iterrows():
        short = row['province'].replace('Kalimantan ', 'Kal. ')
        ax.annotate(short, (row[var], row['hotspot_count']),
                    fontsize=8, color='white', ha='center', va='bottom',
                    xytext=(0, 8), textcoords='offset points',
                    path_effects=[__import__('matplotlib.patheffects', fromlist=['withStroke']).withStroke(linewidth=2, foreground='#1e2d3d')])

    if len(prov_merged) > 2:
        r, _ = pearsonr(prov_merged[var], prov_merged['hotspot_count'])
        ax.set_title(f'{xlabel}\nvs Hotspot Count (r = {r:+.2f})', fontsize=11)
    else:
        ax.set_title(f'{xlabel}\nvs Hotspot Count', fontsize=11)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel('Total Hotspot Count (Dry Season)' if idx == 0 else '', fontsize=10)
    ax.grid(alpha=0.2)

fig.suptitle('Province-level: Dry Season Weather vs Fire Activity (Bubble size = Total FRP)',
             fontsize=13, fontweight='bold', color='white', y=1.02)
fig.tight_layout()
savefig(fig, 'W04_province_weather_vs_fire_drySeason.png')

# ============================================================
# CHART 5: Time-series rolling 14-day avg (weather + fire)
# ============================================================
print("[CHART 5] Rolling 14-day weather and fire trend...")
merged_sorted = merged.sort_values('date').copy()
roll = merged_sorted.set_index('date').rolling('14D', min_periods=5)
roll_df = roll.agg({
    'temp_max':       'mean',
    'precip':         'mean',
    'humidity_mean':  'mean',
    'vpd_max':        'mean',
    'hotspot_count':  'mean',
    'total_frp':      'mean',
}).reset_index()

fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
fig.patch.set_facecolor('#1e2d3d')

# Dry season bands
dry_bands = [
    ('2024-06-01', '2024-10-31'),
    ('2025-06-01', '2025-10-31'),
]

for ax in axes:
    ax.set_facecolor('#1e2d3d')
    for s, e in dry_bands:
        ax.axvspan(pd.Timestamp(s), pd.Timestamp(e), alpha=0.10, color='#e74c3c')

# Subplot 1: Fire activity
ax = axes[0]
ax.fill_between(roll_df['date'], roll_df['hotspot_count'], alpha=0.35, color='#c0392b')
ax.plot(roll_df['date'], roll_df['hotspot_count'], color='#c0392b', lw=2, label='Hotspot Count')
ax2 = ax.twinx()
ax2.plot(roll_df['date'], roll_df['total_frp'], color='#e74c3c', lw=1.5, ls='--', label='Total FRP')
ax.set_ylabel('Hotspot Count (14-day avg)', color='#c0392b')
ax2.set_ylabel('Total FRP (14-day avg)', color='#e74c3c')
ax2.tick_params(colors='#e74c3c')
ax.set_title('Fire Activity (14-day rolling average | Orange bands = Dry Season)')

# Subplot 2: Temperature and humidity
ax = axes[1]
ax.plot(roll_df['date'], roll_df['temp_max'], color='#e74c3c', lw=2, label='Max Temp (C)')
ax.plot(roll_df['date'], roll_df['vpd_max'],  color='#e67e22', lw=1.8, ls='-.', label='Max VPD (kPa)')
ax.set_ylabel('Temperature (C) / VPD (kPa)', color='white')
ax.legend(loc='upper right', fontsize=9, framealpha=0.4)
ax.set_title('Temperature and Vapor Pressure Deficit (14-day rolling average)')

# Subplot 3: Precipitation and humidity
ax = axes[2]
ax.plot(roll_df['date'], roll_df['precip'], color='#3498db', lw=2, label='Precipitation (mm)')
ax.fill_between(roll_df['date'], roll_df['precip'], alpha=0.2, color='#3498db')
ax2 = ax.twinx()
ax2.plot(roll_df['date'], roll_df['humidity_mean'], color='#1abc9c', lw=1.8, label='Humidity (%)')
ax.set_ylabel('Precipitation mm (14-day avg)', color='#3498db')
ax2.set_ylabel('Humidity % (14-day avg)', color='#1abc9c')
ax2.tick_params(colors='#1abc9c')
ax.legend(loc='upper left', fontsize=9, framealpha=0.4)
ax2.legend(loc='upper right', fontsize=9, framealpha=0.4)
ax.set_title('Precipitation and Humidity (14-day rolling average)')

axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
fig.autofmt_xdate(rotation=35, ha='right')
fig.suptitle('14-Day Rolling Average: Fire Activity and Weather Conditions -- Kalimantan\n(Aug 2024 to May 2026)',
             fontsize=13, fontweight='bold', color='white', y=1.01)
savefig(fig, 'W05_rolling14d_weather_fire_timeseries.png')

# ============================================================
# CHART 6: Dry vs Wet season weather box comparison
# ============================================================
print("[CHART 6] Dry vs wet season weather distribution...")
df['month'] = df['date'].dt.month
df['season'] = df['month'].apply(lambda m: 'Dry Season (Jun-Oct)' if m in {6,7,8,9,10} else 'Wet Season (Nov-May)')

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.patch.set_facecolor('#1e2d3d')
vars_to_plot = [
    ('temperature_2m_max',       'Max Temperature (C)'),
    ('precipitation_sum',        'Daily Precipitation (mm)'),
    ('windspeed_10m_max',        'Max Wind Speed (km/h)'),
    ('relative_humidity_2m_min', 'Min Humidity (%)'),
    ('vapor_pressure_deficit_max','Max VPD (kPa)'),
    ('et0_fao_evapotranspiration','Evapotranspiration (mm)'),
]
dry_data = df[df['season'] == 'Dry Season (Jun-Oct)']
wet_data = df[df['season'] == 'Wet Season (Nov-May)']

for idx, (var, label) in enumerate(vars_to_plot):
    ax = axes[idx // 3][idx % 3]
    ax.set_facecolor('#1e2d3d')
    d_vals = dry_data[var].dropna()
    w_vals = wet_data[var].dropna()
    bp = ax.boxplot([d_vals, w_vals], patch_artist=True, widths=0.55,
                    medianprops={'color': 'white', 'lw': 2},
                    whiskerprops={'color': '#a0aec0'},
                    capprops={'color': '#a0aec0'},
                    flierprops={'marker': 'o', 'ms': 3, 'alpha': 0.3, 'color': '#7f8c8d'})
    bp['boxes'][0].set_facecolor('#c0392b'); bp['boxes'][0].set_alpha(0.75)
    bp['boxes'][1].set_facecolor('#2980b9'); bp['boxes'][1].set_alpha(0.75)
    ax.set_xticklabels(['Dry Season', 'Wet Season'], fontsize=10)
    ax.set_title(label, fontsize=10)
    ax.grid(axis='y', alpha=0.2)
    # Add mean label
    for pos, vals in enumerate([d_vals, w_vals], 1):
        ax.text(pos, vals.mean(), f'  {vals.mean():.1f}', va='center',
                fontsize=8.5, color='#f0f0f0', fontweight='bold')

fig.suptitle('Weather Variable Distribution: Dry Season vs Wet Season -- Kalimantan\n(Red = Dry Season | Blue = Wet Season)',
             fontsize=13, fontweight='bold', color='white', y=1.01)
fig.tight_layout()
savefig(fig, 'W06_dry_vs_wet_season_weather.png')

# ============================================================
# SAVE SUMMARY REPORT
# ============================================================
print("\nWriting EDA summary...")

# Key correlations with fire
avail_cols2 = [c for c in [
    'temp_max','temp_mean','precip','wind_max','humidity_mean',
    'humidity_min','vpd_max','et0_fao','sunshine_h',
    'hotspot_count','total_frp'
] if c in merged.columns]
fire_weather_corr = merged[avail_cols2].corr()[['hotspot_count','total_frp']].drop(['hotspot_count','total_frp'])

dry_stats = df[df['season']=='Dry Season (Jun-Oct)'][[
    'temperature_2m_max','precipitation_sum','windspeed_10m_max',
    'relative_humidity_2m_min','vapor_pressure_deficit_max'
]].describe().round(2)

wet_stats = df[df['season']=='Wet Season (Nov-May)'][[
    'temperature_2m_max','precipitation_sum','windspeed_10m_max',
    'relative_humidity_2m_min','vapor_pressure_deficit_max'
]].describe().round(2)

summary = f"""WEATHER EDA SUMMARY -- KALIMANTAN 2024-2026
Data source: Open-Meteo Archive API (ERA5 Reanalysis)
Coverage   : 14 stations across 5 Kalimantan provinces
Period     : {df['date'].min().date()} to {df['date'].max().date()}
Total rows : {len(df):,}

STATIONS:
{df.groupby(['province','city']).size().reset_index().rename(columns={0:'days'}).to_string(index=False)}

CORRELATION: Weather Variables vs Fire Metrics (Kalimantan daily aggregates)
{fire_weather_corr.round(3).to_string()}

DRY SEASON WEATHER STATS (Jun-Oct):
{dry_stats.to_string()}

WET SEASON WEATHER STATS (Nov-May):
{wet_stats.to_string()}

CHART INDEX:
W01 - Monthly weather overview (temperature, precipitation, humidity, wind)
W02 - Weather variables vs monthly hotspot count (dual-axis, 4 panels)
W03 - Pearson correlation heatmap (weather x fire metrics)
W04 - Province-level: dry season weather vs hotspot activity (scatter bubble)
W05 - 14-day rolling average: fire activity + weather time-series
W06 - Dry vs wet season weather boxplot comparison (6 variables)
"""

with open(os.path.join(OUT_DIR, 'weather_eda_summary.txt'), 'w', encoding='utf-8') as f:
    f.write(summary)

print(f"\n[ALL 6 CHARTS + SUMMARY SAVED]")
print(f"Output directory: {OUT_DIR}/")
print(f"  visualizations/ -- {len(os.listdir(VIZ_DIR))} files")
