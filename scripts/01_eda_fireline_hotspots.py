"""
Pipeline 01: Fireline Hotspot Kalimantan EDA, Preprocessing & Feature Engineering
Dataset: NASA VIIRS NOAA-20 (2024-2026) | 61,583 Hotspot Records
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
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, Normalize
from scipy.stats import gaussian_kde

# Import local geospatial utility
sys.path.append(os.path.dirname(__file__))
from utils_geo import ensure_geojson, draw_boundaries, PROV_PALETTE

warnings.filterwarnings('ignore')

# ============================================================
# DIRECTORY & FILE PATHS
# ============================================================
DATA_PATH       = 'datasets/fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv'
OUT_BASE        = 'EDA/01_fireline_hotspot_kalimantan'
OUT_PREPROC     = os.path.join(OUT_BASE, '03_preprocessing')
OUT_FEAT_ENG    = os.path.join(OUT_BASE, '04_feature_engineering')
OUT_VIZ         = os.path.join(OUT_BASE, '02_visualizations')

os.makedirs(OUT_PREPROC, exist_ok=True)
os.makedirs(OUT_FEAT_ENG, exist_ok=True)
os.makedirs(OUT_VIZ, exist_ok=True)

# ============================================================
# MATPLOTLIB STYLE SETTINGS
# ============================================================
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
    path = os.path.join(OUT_VIZ, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.25, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {name}")

# ============================================================
# 1. LOAD, CLEAN & PREPROCESS
# ============================================================
print("\n" + "=" * 70)
print("STAGE 1: LOADING & PREPROCESSING RAW DATASET")
print("=" * 70)

df_raw = pd.read_csv(DATA_PATH)
print(f"Raw dataset shape: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")

# Drop 4 constant columns (zero variance)
drop_cols = ['satellite', 'instrument', 'version', 'type']
df_clean = df_raw.drop(columns=drop_cols, errors='ignore').copy()

# Parse acquisition date
df_clean['acq_date'] = pd.to_datetime(df_clean['acq_date'])

# Save cleaned CSV
clean_file = os.path.join(OUT_PREPROC, 'fireline_hotspot_clean.csv')
df_clean.to_csv(clean_file, index=False)
print(f"Cleaned dataset saved: {clean_file} ({df_clean.shape[0]:,} rows x {df_clean.shape[1]} cols)")

# ============================================================
# 2. FEATURE ENGINEERING (32 NEW FEATURES)
# ============================================================
print("\n" + "=" * 70)
print("STAGE 2: FEATURE ENGINEERING (32 DOMAIN-SPECIFIC FEATURES)")
print("=" * 70)

df = df_clean.copy()

# A. Temporal Features (13)
df['year']             = df['acq_date'].dt.year
df['month']            = df['acq_date'].dt.month
df['month_name']       = df['acq_date'].dt.strftime('%b')
df['day_of_month']     = df['acq_date'].dt.day
df['day_name']         = df['acq_date'].dt.strftime('%A')
df['is_weekend']       = df['acq_date'].dt.dayofweek.isin([5, 6]).astype(int)
df['hour']             = df['acq_time'].astype(str).str.zfill(4).str[:2].astype(int)
df['quarter']          = 'Q' + ((df['month'] - 1) // 3 + 1).astype(str)
df['year_month']       = df['acq_date'].dt.strftime('%Y-%m')
df['season']           = df['month'].apply(lambda m: 'Dry Season (Jun-Oct)' if m in [6,7,8,9,10] else 'Wet Season (Nov-May)')
df['days_since_start'] = (df['acq_date'] - df['acq_date'].min()).dt.days
df['is_kemarau']       = df['month'].isin([6, 7, 8, 9, 10]).astype(int)
df['time_period']      = pd.cut(df['hour'], bins=[-1, 5, 11, 15, 19, 24],
                                labels=['Night (19-05)', 'Morning (05-11)', 'Midday (11-15)', 'Afternoon (15-19)', 'Night (19-05)'],
                                ordered=False)

# B. Fire Hazard & Intensity Features (8)
df['temp_delta_K']          = df['brightness'] - df['bright_t31']
df['brightness_celsius']    = df['brightness'] - 273.15
df['bright_t31_celsius']    = df['bright_t31'] - 273.15
df['pixel_area_km2']        = df['scan'] * df['track'] * 0.140625
df['fire_intensity_class']  = pd.cut(df['frp'], bins=[0, 5, 20, 50, 10000],
                                     labels=['Low (<5 MW)', 'Medium (5-20 MW)', 'High (20-50 MW)', 'Extreme (>50 MW)'])
df['is_extreme_fire']       = (df['frp'] > 100).astype(int)
df['is_mega_fire']          = (df['frp'] > 500).astype(int)
df['frp_log']               = np.log1p(df['frp'])

# C. Sensor Reliability & Confidence Weighting (3)
conf_map = {'l': 0, 'n': 1, 'h': 2}
conf_weight_map = {'l': 0.30, 'n': 0.70, 'h': 1.00}
df['confidence_num']    = df['confidence'].map(conf_map)
df['confidence_weight'] = df['confidence'].map(conf_weight_map)
df['weighted_frp']      = df['frp'] * df['confidence_weight']

# D. Regional & Spatial Features (4)
def assign_kalimantan_province(row):
    lat, lon = row['latitude'], row['longitude']
    if lat >= 1.0 and lon >= 114.5:
        return 'Kalimantan Utara'
    elif lat >= -2.5 and lon >= 114.5:
        return 'Kalimantan Timur'
    elif lat < -1.3 and lon >= 114.0:
        return 'Kalimantan Selatan'
    elif lat <= 0.0 and lon >= 111.0:
        return 'Kalimantan Tengah'
    elif lon < 114.5:
        return 'Kalimantan Barat'
    return 'Other'

df['kalimantan_region'] = df.apply(assign_kalimantan_province, axis=1)
df['lat_zone']          = np.where(df['latitude'] >= 0, 'Utara (North)', 'Selatan (South)')
df['coord_grid_1deg']   = df['latitude'].round().astype(str) + '_' + df['longitude'].round().astype(str)
df['coord_grid_05deg']  = (df['latitude'] * 2).round() / 2
df['coord_grid_05deg']  = df['coord_grid_05deg'].astype(str) + '_' + ((df['longitude'] * 2).round() / 2).astype(str)

# E. Vulnerability & Recurrence Features (3)
grid_counts = df['coord_grid_05deg'].value_counts()
grid_frp    = df.groupby('coord_grid_05deg')['frp'].sum()
df['fire_recurrence_count']  = df['coord_grid_05deg'].map(grid_counts)
df['cumulative_frp_at_grid'] = df['coord_grid_05deg'].map(grid_frp)
df['is_high_recurrence']     = (df['fire_recurrence_count'] >= 5).astype(int)

# F. Composite HAZARD Score (0-100 index)
frp_norm   = np.clip(df['frp'] / df['frp'].quantile(0.99) * 100, 0, 100)
delta_norm = np.clip(df['temp_delta_K'] / df['temp_delta_K'].quantile(0.99) * 100, 0, 100)
conf_norm  = df['confidence_weight'] * 100
df['hazard_score'] = (0.40 * frp_norm + 0.35 * delta_norm + 0.25 * conf_norm).round(2)

# Save featured CSV
featured_file = os.path.join(OUT_FEAT_ENG, 'fireline_hotspot_featured.csv')
df.to_csv(featured_file, index=False)
print(f"Featured dataset saved: {featured_file} ({df.shape[0]:,} rows x {df.shape[1]} cols)")

# ============================================================
# 3. GENERATE VISUALIZATIONS (27 CHARTS)
# ============================================================
print("\n" + "=" * 70)
print("STAGE 3: GENERATING PUBLICATION-GRADE VISUALIZATIONS")
print("=" * 70)

# Load GeoJSON boundary data
geo_data = ensure_geojson()
features = geo_data['features']
kal_features = [ft for ft in features if 'alimantan' in ft['properties'].get('PROVINSI', '')]
non_kal_features = [ft for ft in features if 'alimantan' not in ft['properties'].get('PROVINSI', '')]

# Map bounding box
XMIN, XMAX = 107.8, 120.0
YMIN, YMAX = -4.8, 5.0

# ------------------------------------------------------------
# PILLAR A: TEMPORAL CHARTS (01-06)
# ------------------------------------------------------------
print("[Pillar A] Temporal Analysis Charts...")

# 01. Daily trend with 7-day MA
daily_ts = df.groupby('acq_date').size().reset_index(name='count')
daily_ts['ma7'] = daily_ts['count'].rolling(7, min_periods=1).mean()
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(daily_ts['acq_date'], daily_ts['count'], color='#5c7a99', alpha=0.5, lw=1, label='Daily Detections')
ax.plot(daily_ts['acq_date'], daily_ts['ma7'], color='#e74c3c', lw=2.5, label='7-Day Moving Average')
ax.fill_between(daily_ts['acq_date'], daily_ts['ma7'], color='#e74c3c', alpha=0.15)
ax.axvspan(pd.Timestamp('2024-06-01'), pd.Timestamp('2024-11-01'), alpha=0.1, color='#e67e22', label='Dry Season')
ax.axvspan(pd.Timestamp('2025-06-01'), pd.Timestamp('2025-11-01'), alpha=0.1, color='#e67e22')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_ylabel('Hotspot Count'); ax.set_title('Daily Hotspot Trend across Kalimantan with 7-Day Moving Average')
ax.legend(loc='upper right', framealpha=0.4); ax.grid(alpha=0.2)
fig.autofmt_xdate(rotation=30)
savefig(fig, '01_daily_trend_with_ma7.png')

# 02. Calendar Heatmap (Day of week vs Month)
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
cal_pvt = df.pivot_table(index='day_name', columns='month', values='frp', aggfunc='count').reindex(dow_order)
fig, ax = plt.subplots(figsize=(12, 6))
cmap = LinearSegmentedColormap.from_list('heat', ['#1a252f', '#e67e22', '#c0392b'], N=256)
im = ax.imshow(cal_pvt.values, cmap=cmap, aspect='auto')
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cbar.set_label('Hotspot Count', color='white')
ax.set_xticks(range(12)); ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
ax.set_yticks(range(7)); ax.set_yticklabels(dow_order)
ax.set_title('Calendar Heatmap: Hotspot Count by Day of Week and Month')
savefig(fig, '02_calendar_heatmap_dayofweek_month.png')

# 03. Monthly Stacked by Confidence
monthly_conf = df.groupby(['year_month', 'confidence']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(14, 6))
monthly_conf[['l', 'n', 'h']].plot(kind='bar', stacked=True, color=['#7f8c8d', '#2980b9', '#e74c3c'], ax=ax, alpha=0.85, edgecolor='white', lw=0.3)
ax.set_xlabel('Year-Month'); ax.set_ylabel('Hotspot Count')
ax.set_title('Monthly Hotspot Volume Stacked by Detection Confidence (l, n, h)')
ax.legend(['Low', 'Nominal', 'High'], loc='upper right', framealpha=0.5); ax.tick_params(axis='x', rotation=45)
savefig(fig, '03_monthly_stacked_by_confidence.png')

# 04. FRP Boxplot per Month
months_ordered = sorted(df['month'].unique())
box_data = [df[df['month'] == m]['frp'].dropna().values for m in months_ordered]
fig, ax = plt.subplots(figsize=(13, 6))
bp = ax.boxplot(box_data, patch_artist=True, showfliers=False, widths=0.55,
                medianprops={'color': 'white', 'lw': 2}, boxprops={'facecolor': '#c0392b', 'alpha': 0.75})
ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
ax.set_ylabel('Fire Radiative Power (MW)'); ax.set_title('Monthly Fire Radiative Power (FRP) Distribution (Outliers Clipped for Readability)')
ax.grid(axis='y', alpha=0.2)
savefig(fig, '04_frp_boxplot_per_month.png')

# 05. Dual Axis: Monthly Count vs Total FRP
monthly_agg = df.groupby('year_month').agg(count=('frp', 'count'), total_frp=('frp', 'sum')).reset_index()
fig, ax1 = plt.subplots(figsize=(14, 6))
ax2 = ax1.twinx()
x = np.arange(len(monthly_agg))
ax1.bar(x, monthly_agg['count'], color='#2980b9', alpha=0.7, label='Hotspot Count', width=0.55)
ax2.plot(x, monthly_agg['total_frp'] / 1000, color='#e74c3c', lw=2.5, marker='o', label='Total Energy (GW)')
ax1.set_xticks(x); ax1.set_xticklabels(monthly_agg['year_month'], rotation=45)
ax1.set_ylabel('Hotspot Count', color='#2980b9'); ax2.set_ylabel('Total Energy (GW)', color='#e74c3c')
ax2.tick_params(colors='#e74c3c'); ax1.set_title('Monthly Hotspot Count vs Total Radiative Energy Released')
savefig(fig, '05_dual_axis_count_vs_total_frp.png')

# 06. Year over Year (2024 vs 2025)
yoy = df[df['year'].isin([2024, 2025])].groupby(['month', 'year']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12, 6))
yoy.plot(kind='bar', color=['#3498db', '#e67e22'], ax=ax, alpha=0.85, edgecolor='white', lw=0.4)
ax.set_xticks(range(12)); ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], rotation=0)
ax.set_ylabel('Hotspot Count'); ax.set_title('Year-over-Year Comparison of Fire Activity (2024 vs 2025)')
ax.legend(['Year 2024', 'Year 2025'], framealpha=0.5); ax.grid(axis='y', alpha=0.2)
savefig(fig, '06_year_over_year_2024_vs_2025.png')

# ------------------------------------------------------------
# PILLAR B: HAZARD INTENSITY CHARTS (07-11)
# ------------------------------------------------------------
print("[Pillar B] Fire Hazard & Intensity Charts...")

# 07. FRP Distribution Log Scale
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['frp'], bins=np.logspace(np.log10(0.1), np.log10(1000), 60), color='#c0392b', edgecolor='white', lw=0.3, alpha=0.8)
ax.set_xscale('log')
ax.axvline(df['frp'].median(), color='#f1c40f', lw=2, ls='--', label=f'Median: {df["frp"].median():.2f} MW')
ax.axvline(df['frp'].mean(), color='#e67e22', lw=2, ls='-.', label=f'Mean: {df["frp"].mean():.2f} MW')
ax.axvline(100, color='white', lw=1.5, ls=':', label='Extreme Tier (>100 MW)')
ax.set_xlabel('Fire Radiative Power (MW, Log Scale)'); ax.set_ylabel('Frequency')
ax.set_title('Fire Radiative Power (FRP) Heavy-Tailed Log Distribution'); ax.legend(framealpha=0.4); ax.grid(alpha=0.2)
savefig(fig, '07_frp_distribution_log_scale.png')

# 08. Brightness vs Bright_t31 Overlay
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['brightness_celsius'], bins=50, alpha=0.6, color='#e74c3c', label='Fire Brightness Temp (°C)', edgecolor='white', lw=0.3)
ax.hist(df['bright_t31_celsius'], bins=50, alpha=0.6, color='#2980b9', label='Background Land Temp (°C)', edgecolor='white', lw=0.3)
ax.set_xlabel('Temperature (°C)'); ax.set_ylabel('Frequency')
ax.set_title('Fire Temperature vs Ambient Background Surface Temperature Overlay')
ax.legend(framealpha=0.4); ax.grid(alpha=0.2)
savefig(fig, '08_brightness_vs_bright_t31_overlay.png')

# 09. Violin FRP by Confidence
fig, ax = plt.subplots(figsize=(10, 6))
viol_data = [df[df['confidence'] == c]['frp_log'].dropna().values for c in ['l', 'n', 'h']]
v = ax.violinplot(viol_data, showmedians=True, showextrema=True)
ax.set_xticks([1, 2, 3]); ax.set_xticklabels(['Low (l)', 'Nominal (n)', 'High (h)'])
ax.set_ylabel('log(1 + FRP)'); ax.set_title('Violin Plot: Fire Energy Intensity by Sensor Confidence Level')
ax.grid(axis='y', alpha=0.2)
savefig(fig, '09_violin_frp_by_confidence.png')

# 10. Scatter FRP vs Temp Delta
sample_s = df.sample(min(8000, len(df)), random_state=42)
fig, ax = plt.subplots(figsize=(11, 6))
sc = ax.scatter(sample_s['temp_delta_K'], sample_s['frp'], c=sample_s['hazard_score'], cmap='YlOrRd',
                s=np.clip(sample_s['pixel_area_km2'] * 60, 10, 80), alpha=0.6, edgecolors='none')
cbar = plt.colorbar(sc, ax=ax); cbar.set_label('Hazard Score', color='white')
ax.set_yscale('log'); ax.set_xlabel('Temperature Delta (°K)'); ax.set_ylabel('FRP (MW, Log Scale)')
ax.set_title('Scatter: Fire Radiative Power vs Temperature Delta (Color = Hazard Score)')
ax.grid(alpha=0.2)
savefig(fig, '10_scatter_frp_vs_temp_delta.png')

# 11. Day vs Night Comparison
dn = df.groupby('daynight').agg(count=('frp', 'count'), mean_frp=('frp', 'mean')).reset_index()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.bar(['Daytime (D)', 'Nighttime (N)'], dn['count'], color=['#e67e22', '#2980b9'], alpha=0.85, edgecolor='white', lw=0.4)
ax1.set_ylabel('Hotspot Count'); ax1.set_title('Detection Volume (Day vs Night)'); ax1.grid(axis='y', alpha=0.2)
ax2.bar(['Daytime (D)', 'Nighttime (N)'], dn['mean_frp'], color=['#e67e22', '#2980b9'], alpha=0.85, edgecolor='white', lw=0.4)
ax2.set_ylabel('Mean FRP (MW)'); ax2.set_title('Average Fire Intensity (Day vs Night)'); ax2.grid(axis='y', alpha=0.2)
fig.suptitle('Daytime vs Nighttime Fire Activity Dynamics in Kalimantan', fontsize=13, fontweight='bold', color='white')
savefig(fig, '11_day_vs_night_count_and_frp.png')

# ------------------------------------------------------------
# PILLAR C: SPATIAL MAPS WITH GEOJSON (12-15)
# ------------------------------------------------------------
print("[Pillar C] Spatial Distribution Maps...")

# 12. Spatial Scatter Map
sample_geo = df.sample(min(25000, len(df)), random_state=99)
fig, ax = plt.subplots(figsize=(14, 10))
draw_boundaries(ax, non_kal_features, facecolor='#2d3d4e', edgecolor='#3d5166', linewidth=0.5, alpha=0.6)
draw_boundaries(ax, kal_features, use_prov_colors=True, edgecolor='#a0aec0', linewidth=1.2, alpha=0.55, label_provinces=True)

sc = ax.scatter(sample_geo['longitude'], sample_geo['latitude'], c=np.log1p(sample_geo['frp']),
                cmap='YlOrRd', s=np.clip(np.log1p(sample_geo['frp']) * 2.5, 1.5, 45), alpha=0.65, zorder=3)
cbar = plt.colorbar(sc, ax=ax, fraction=0.028, pad=0.02, shrink=0.85); cbar.set_label('log1p(FRP) -- Intensity', color='white')
ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX)
ax.set_title('Spatial Distribution of Fire Hotspots across Kalimantan\n(Background: Province Boundaries | Size/Color = Fire Intensity)', pad=14)
savefig(fig, '12_spatial_scatter_all_hotspots.png')

# 13. Hexbin Density Map
fig, ax = plt.subplots(figsize=(14, 10))
ax.hexbin(df['longitude'], df['latitude'], gridsize=65, cmap='inferno', mincnt=1, zorder=2, alpha=0.92)
draw_boundaries(ax, kal_features, facecolor='none', edgecolor='#ffffff', linewidth=1.6, alpha=1.0, label_provinces=True)
draw_boundaries(ax, non_kal_features, facecolor='none', edgecolor='#3d5166', linewidth=0.5, alpha=0.7)
ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX)
ax.set_title('Hotspot Density Hexbin Map -- Kalimantan Province Boundaries Overlaid', pad=14)
savefig(fig, '13_hexbin_density_map.png')

# 14. KDE Spatial Contour Map
sample_kde = df.sample(min(18000, len(df)), random_state=7)
xgrid, ygrid = np.linspace(XMIN, XMAX, 220), np.linspace(YMIN, YMAX, 200)
Xg, Yg = np.meshgrid(xgrid, ygrid)
kernel = gaussian_kde(np.vstack([sample_kde['longitude'].values, sample_kde['latitude'].values]), bw_method=0.06)
Z = kernel(np.vstack([Xg.ravel(), Yg.ravel()])).reshape(Xg.shape)

fig, ax = plt.subplots(figsize=(14, 10))
ax.contourf(Xg, Yg, Z, levels=25, cmap='hot', alpha=0.88, zorder=2)
draw_boundaries(ax, kal_features, facecolor='none', edgecolor='#ffffff', linewidth=1.8, alpha=1.0, label_provinces=True)
draw_boundaries(ax, non_kal_features, facecolor='none', edgecolor='#2d4a5e', linewidth=0.6, alpha=0.8)
ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX)
ax.set_title('Kernel Density Estimation (KDE) -- Fire Concentration Epicenters in Kalimantan', pad=14)
savefig(fig, '14_kde_spatial_contour.png')

# 15. Bar Chart: Hotspots by Province
prov_agg = df.groupby('kalimantan_region').agg(count=('frp', 'count'), total_frp=('frp', 'sum')).sort_values('count', ascending=False)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
p_colors = [PROV_PALETTE.get(p, '#7f8c8d') for p in prov_agg.index]
ax1.bar(prov_agg.index, prov_agg['count'], color=p_colors, alpha=0.85, edgecolor='white', lw=0.4)
ax1.set_ylabel('Hotspot Count'); ax1.set_title('Hotspot Count by Province'); ax1.tick_params(axis='x', rotation=30); ax1.grid(axis='y', alpha=0.2)
ax2.bar(prov_agg.index, prov_agg['total_frp'] / 1000, color=p_colors, alpha=0.85, edgecolor='white', lw=0.4)
ax2.set_ylabel('Total Energy (GW)'); ax2.set_title('Total Radiative Energy (GW) by Province'); ax2.tick_params(axis='x', rotation=30); ax2.grid(axis='y', alpha=0.2)
fig.suptitle('Provincial Fire Profile Comparison across Kalimantan', fontsize=13, fontweight='bold', color='white')
savefig(fig, '15_bar_hotspots_by_province.png')

# ------------------------------------------------------------
# PILLAR D: EXTREME EVENTS CHARTS (16-18)
# ------------------------------------------------------------
print("[Pillar D] Extreme Events & Mega-Fires...")

# 16. FRP Timeline of Extreme Events
fig, ax = plt.subplots(figsize=(15, 6))
ax.scatter(df['acq_date'], df['frp'], color='#3498db', alpha=0.3, s=8, label='Normal Detections')
extreme = df[df['frp'] > 100]
ax.scatter(extreme['acq_date'], extreme['frp'], color='#e74c3c', s=45, edgecolors='white', lw=0.6, label=f'Extreme Fires >100 MW (N={len(extreme)})')
ax.axhline(500, color='#f1c40f', ls='--', label='Mega-Fire Threshold (500 MW)')
ax.set_ylabel('FRP (MW)'); ax.set_title('Timeline of Extreme Wildfire Events in Kalimantan (Aug 2024 - May 2026)')
ax.legend(loc='upper right', framealpha=0.5); ax.grid(alpha=0.2)
savefig(fig, '16_frp_timeline_extreme_events.png')

# 17. Top 20 Critical Days
top_days = df.groupby('acq_date')['frp'].sum().nlargest(20).sort_values()
fig, ax = plt.subplots(figsize=(12, 7))
ax.barh(top_days.index.strftime('%Y-%m-%d'), top_days.values / 1000, color='#c0392b', alpha=0.85, edgecolor='white', lw=0.4)
ax.set_xlabel('Total Fire Energy Released (GW)'); ax.set_title('Top 20 Critical Days by Cumulative Fire Energy (GW)')
ax.grid(axis='x', alpha=0.2)
savefig(fig, '17_top20_critical_days_total_frp.png')

# 18. Cumulative FRP over time
cum_df = df.groupby('acq_date')['frp'].sum().cumsum().reset_index()
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(cum_df['acq_date'], cum_df['frp'] / 1000, color='#e74c3c', lw=2.5)
ax.fill_between(cum_df['acq_date'], cum_df['frp'] / 1000, color='#e74c3c', alpha=0.2)
ax.set_ylabel('Cumulative Energy (GW)'); ax.set_title('Cumulative Radiative Fire Energy Growth over Time (GW)')
ax.grid(alpha=0.2)
savefig(fig, '18_cumulative_total_frp_over_time.png')

# ------------------------------------------------------------
# PILLAR E: VULNERABILITY & RECURRENCE (19-21)
# ------------------------------------------------------------
print("[Pillar E] Vulnerability & Recurrence Charts...")

# 19. Top 25 Chronic Fire Grids
top_rec = df.groupby(['coord_grid_05deg', 'kalimantan_region']).size().reset_index(name='count').nlargest(25, 'count').sort_values('count')
fig, ax = plt.subplots(figsize=(12, 8))
colors_bar = [PROV_PALETTE.get(p, '#7f8c8d') for p in top_rec['kalimantan_region']]
ax.barh(top_rec['coord_grid_05deg'] + ' (' + top_rec['kalimantan_region'].str.replace('Kalimantan ', 'Kal. ') + ')',
        top_rec['count'], color=colors_bar, alpha=0.85, edgecolor='white', lw=0.4)
ax.set_xlabel('Total Hotspot Recurrence Count'); ax.set_title('Top 25 Chronic Fire Recurrence Zones (0.5-Degree Grids)')
ax.grid(axis='x', alpha=0.2)
savefig(fig, '19_top25_recurrence_chronic_fire_zones.png')

# 20. Heatmap Region vs Season
pvt_reg_season = df.pivot_table(index='kalimantan_region', columns='season', values='frp', aggfunc='count', fill_value=0)
fig, ax = plt.subplots(figsize=(10, 5))
im = ax.imshow(pvt_reg_season.values, cmap='YlOrRd', aspect='auto')
plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
ax.set_xticks(range(2)); ax.set_xticklabels(pvt_reg_season.columns)
ax.set_yticks(range(len(pvt_reg_season))); ax.set_yticklabels(pvt_reg_season.index)
ax.set_title('Fire Occurrence Risk Matrix: Province vs Season')
savefig(fig, '20_heatmap_region_vs_season.png')

# 21. Weekday vs Weekend
ww = df.groupby('is_weekend').agg(count=('frp', 'count'), mean_frp=('frp', 'mean')).reset_index()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
ax1.bar(['Weekday', 'Weekend'], ww['count'], color=['#3498db', '#e67e22'], alpha=0.85, edgecolor='white', lw=0.4)
ax1.set_ylabel('Hotspot Count'); ax1.set_title('Volume: Weekday vs Weekend'); ax1.grid(axis='y', alpha=0.2)
ax2.bar(['Weekday', 'Weekend'], ww['mean_frp'], color=['#3498db', '#e67e22'], alpha=0.85, edgecolor='white', lw=0.4)
ax2.set_ylabel('Mean FRP (MW)'); ax2.set_title('Intensity: Weekday vs Weekend'); ax2.grid(axis='y', alpha=0.2)
fig.suptitle('Weekday vs Weekend Fire Dynamics', fontsize=12, fontweight='bold', color='white')
savefig(fig, '21_weekday_vs_weekend_fire_activity.png')

# ------------------------------------------------------------
# PILLAR F & BONUS CHARTS (22-24, FE01-FE03)
# ------------------------------------------------------------
print("[Pillar F & Bonus] Composite & Engineered Feature Charts...")

# 22. Pearson Correlation Matrix
corr_cols = ['frp', 'temp_delta_K', 'brightness', 'bright_t31', 'scan', 'track', 'confidence_num', 'hazard_score']
corr_mat = df[corr_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr_mat.values, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
ax.set_xticks(range(len(corr_cols))); ax.set_yticks(range(len(corr_cols)))
ax.set_xticklabels(corr_cols, rotation=35, ha='right'); ax.set_yticklabels(corr_cols)
for i in range(len(corr_cols)):
    for j in range(len(corr_cols)):
        ax.text(j, i, f'{corr_mat.values[i, j]:.2f}', ha='center', va='center', color='white', fontsize=8.5)
ax.set_title('Pearson Correlation Matrix: Hotspot Attributes & Engineered Hazard Score')
savefig(fig, '22_pearson_correlation_matrix.png')

# 23. Confidence Donut & FRP Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
conf_cnt = df['confidence'].value_counts()
ax1.pie(conf_cnt.values, labels=['Nominal (n)', 'High (h)', 'Low (l)'], autopct='%1.1f%%',
        colors=['#2980b9', '#e74c3c', '#7f8c8d'], startangle=140, explode=[0.05, 0.05, 0.05],
        textprops={'color': 'white'})
ax1.set_title('Detection Confidence Proportion')
conf_frp = df.groupby('confidence')['frp'].mean().reindex(['l', 'n', 'h'])
ax2.bar(['Low (l)', 'Nominal (n)', 'High (h)'], conf_frp.values, color=['#7f8c8d', '#2980b9', '#e74c3c'], alpha=0.85, edgecolor='white', lw=0.4)
ax2.set_ylabel('Mean FRP (MW)'); ax2.set_title('Average FRP by Confidence Level'); ax2.grid(axis='y', alpha=0.2)
savefig(fig, '23_confidence_donut_and_frp_comparison.png')

# 24. Intensity Class Composition by Province
int_prov = df.groupby(['kalimantan_region', 'fire_intensity_class']).size().unstack(fill_value=0)
int_prov_pct = int_prov.div(int_prov.sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(13, 6))
int_prov_pct.plot(kind='bar', stacked=True, color=['#27ae60', '#f39c12', '#e67e22', '#c0392b'], ax=ax, alpha=0.85, edgecolor='white', lw=0.3)
ax.set_ylabel('Percentage (%)'); ax.set_title('Fire Intensity Class Composition (100% Stacked) per Province')
ax.tick_params(axis='x', rotation=25); ax.legend(loc='upper right', framealpha=0.5)
savefig(fig, '24_intensity_class_composition_by_province.png')

# FE01. Raw vs Weighted FRP Monthly
fig, ax = plt.subplots(figsize=(14, 5))
mon_rw = df.groupby('year_month').agg(raw=('frp', 'sum'), weighted=('weighted_frp', 'sum')).reset_index()
ax.plot(mon_rw['year_month'], mon_rw['raw'] / 1000, label='Raw Total FRP (GW)', color='#e74c3c', lw=2, marker='o')
ax.plot(mon_rw['year_month'], mon_rw['weighted'] / 1000, label='Confidence-Weighted FRP (GW)', color='#f39c12', lw=2, ls='--', marker='s')
ax.set_ylabel('Energy (GW)'); ax.set_title('Comparison: Raw FRP vs Confidence-Weighted FRP per Month')
ax.legend(framealpha=0.4); ax.tick_params(axis='x', rotation=45); ax.grid(alpha=0.2)
savefig(fig, 'FE01_raw_vs_weighted_frp_monthly.png')

# FE02. Hazard Score Distribution by Province
fig, ax = plt.subplots(figsize=(13, 6))
prov_haz = [df[df['kalimantan_region'] == p]['hazard_score'].dropna().values for p in PROV_PALETTE.keys()]
bp = ax.boxplot(prov_haz, patch_artist=True, widths=0.55, showfliers=False,
                medianprops={'color': 'white', 'lw': 2})
for patch, color in zip(bp['boxes'], PROV_PALETTE.values()):
    patch.set_facecolor(color); patch.set_alpha(0.75)
ax.set_xticklabels([p.replace('Kalimantan ', 'Kal. ') for p in PROV_PALETTE.keys()])
ax.set_ylabel('Hazard Score (0-100)'); ax.set_title('Engineered Composite Hazard Score Distribution by Province')
ax.grid(axis='y', alpha=0.2)
savefig(fig, 'FE02_hazard_score_by_province.png')

# FE03. Chronic Fire Recurrence Map
top_grids = df.groupby('coord_grid_05deg').agg(count=('frp', 'count'), mean_lat=('latitude', 'mean'), mean_lon=('longitude', 'mean')).reset_index()
high_rec = top_grids[top_grids['count'] >= 5]
fig, ax = plt.subplots(figsize=(14, 10))
draw_boundaries(ax, non_kal_features, facecolor='#1e2d3d', edgecolor='#2d4050', linewidth=0.5, alpha=0.6)
draw_boundaries(ax, kal_features, use_prov_colors=True, edgecolor='#a0aec0', linewidth=1.3, alpha=0.35, label_provinces=True)
sc = ax.scatter(high_rec['mean_lon'], high_rec['mean_lat'], c=high_rec['count'], cmap='YlOrRd',
                s=np.clip(high_rec['count'] * 0.6 + 15, 15, 250), alpha=0.90, zorder=5, edgecolors='#2c3e50', linewidths=0.4)
cbar = plt.colorbar(sc, ax=ax, fraction=0.028, pad=0.02, shrink=0.85); cbar.set_label('Recurrence Count', color='white')
ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX)
ax.set_title(f'Chronic Fire Zones in Kalimantan ({len(high_rec):,} Grids with >=5 Recurrences Over 22 Months)', pad=14)
savefig(fig, 'FE03_chronic_fire_zones_recurrence_map.png')

print("\n" + "=" * 70)
print("[PIPELINE 01 COMPLETED SUCCESSFULLY - 27 CHARTS REPRODUCED]")
print("=" * 70)
