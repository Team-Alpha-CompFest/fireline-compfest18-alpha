"""
EDA Phase 2: Visualizations - 24 Professional Charts
Dataset: fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv
FIRELINE - COMPFEST 18 Case Study
Style: Professional, no emojis, no em-dashes
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

warnings.filterwarnings('ignore')

OUT_VIZ = 'EDA/01_fireline_hotspot_kalimantan/02_visualizations'
FEAT_PATH = 'EDA/01_fireline_hotspot_kalimantan/04_feature_engineering/fireline_hotspot_featured.csv'

# ============================================================
# STYLE SETUP
# ============================================================
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelweight': 'bold',
    'axes.grid': True,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'grid.alpha': 0.35,
    'grid.linestyle': '--',
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.25,
    'legend.frameon': True,
    'legend.framealpha': 0.9,
})

# Color Palette
C_RED      = '#c0392b'
C_ORANGE   = '#e67e22'
C_YELLOW   = '#f39c12'
C_GREEN    = '#27ae60'
C_BLUE     = '#2980b9'
C_NAVY     = '#1a252f'
C_DARK     = '#2c3e50'
C_GRAY     = '#7f8c8d'
C_LIGHT    = '#ecf0f1'

PROV_COLORS = {
    'Kalimantan Barat':   '#2980b9',
    'Kalimantan Tengah':  '#e67e22',
    'Kalimantan Timur':   '#27ae60',
    'Kalimantan Selatan': '#c0392b',
    'Kalimantan Utara':   '#8e44ad',
    'Other':              '#7f8c8d',
}

CONF_COLORS = {'l': C_GREEN, 'n': C_BLUE, 'h': C_RED}
INTENSITY_COLORS = {
    'Low (<5 MW)':      C_GREEN,
    'Medium (5-20 MW)': C_YELLOW,
    'High (20-50 MW)':  C_ORANGE,
    'Extreme (>50 MW)': C_RED,
}

def save_fig(fig, name):
    path = os.path.join(OUT_VIZ, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    print(f"  Saved: {name}")

# ============================================================
# LOAD DATA
# ============================================================
print("Loading featured data...")
df = pd.read_csv(FEAT_PATH, parse_dates=['acq_date'])
print(f"  Rows: {len(df):,}  Cols: {df.shape[1]}")

# ============================================================
# PILLAR A - TEMPORAL (Charts 01-06)
# ============================================================
print("\n[PILLAR A] Temporal Charts...")

# 01 - Daily trend + 7-day MA
daily = df.groupby('acq_date').size().reset_index(name='count')
daily['ma7'] = daily['count'].rolling(7, center=True).mean()
fig, ax = plt.subplots(figsize=(16, 5))
ax.fill_between(daily['acq_date'], daily['count'], alpha=0.15, color=C_BLUE)
ax.plot(daily['acq_date'], daily['count'], color=C_BLUE, lw=0.8, alpha=0.6, label='Daily Count')
ax.plot(daily['acq_date'], daily['ma7'], color=C_RED, lw=2.2, label='7-Day Moving Average')
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
ax.set_title('Daily Hotspot Count with 7-Day Moving Average\nKalimantan Fire Hotspots (Aug 2024 - May 2026)', pad=15)
ax.set_ylabel('Number of Hotspots Detected')
ax.set_xlabel('Date')
ax.legend(loc='upper left')
# Annotate peak
peak_day = daily.loc[daily['count'].idxmax()]
ax.annotate(f"Peak: {peak_day['count']:,}\n{peak_day['acq_date'].strftime('%d %b %Y')}",
            xy=(peak_day['acq_date'], peak_day['count']),
            xytext=(40, 20), textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color=C_DARK, lw=1.5),
            bbox=dict(boxstyle='round,pad=0.4', fc='#ffeaa7', ec=C_ORANGE, lw=1.5),
            fontsize=9, fontweight='bold')
save_fig(fig, '01_daily_trend_with_ma7.png')

# 02 - Calendar Heatmap
df['week_of_year'] = df['acq_date'].dt.isocalendar().week.astype(int)
df['weekday'] = df['acq_date'].dt.weekday
heatmap_data = df.pivot_table(index='weekday', columns='year_month', values='frp', aggfunc='count', fill_value=0)
fig, ax = plt.subplots(figsize=(20, 4))
sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax, linewidths=0.2,
            cbar_kws={'label': 'Hotspot Count', 'shrink': 0.8})
ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)
ax.set_xlabel('Month (Year-Month)')
ax.set_ylabel('Day of Week')
ax.set_title('Hotspot Activity Heatmap: Day of Week vs Month\n(Color Intensity = Number of Hotspot Detections)', pad=15)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
save_fig(fig, '02_calendar_heatmap_dayofweek_month.png')

# 03 - Stacked bar: monthly hotspot by confidence
monthly_conf = df.groupby(['year_month', 'confidence']).size().unstack(fill_value=0)
monthly_conf = monthly_conf.reindex(columns=['l', 'n', 'h'], fill_value=0)
fig, ax = plt.subplots(figsize=(16, 5))
bottom = np.zeros(len(monthly_conf))
colors_conf = [C_GREEN, C_BLUE, C_RED]
labels_conf = ['Low Confidence', 'Nominal Confidence', 'High Confidence']
for col, color, label in zip(['l', 'n', 'h'], colors_conf, labels_conf):
    ax.bar(range(len(monthly_conf)), monthly_conf[col], bottom=bottom, color=color,
           label=label, edgecolor='white', linewidth=0.4, width=0.8)
    bottom += monthly_conf[col].values
ax.set_xticks(range(len(monthly_conf)))
ax.set_xticklabels(monthly_conf.index, rotation=45, ha='right', fontsize=8)
ax.set_title('Monthly Hotspot Count by Detection Confidence Level\n(Low / Nominal / High Confidence)', pad=15)
ax.set_ylabel('Number of Hotspots')
ax.set_xlabel('Month')
ax.legend(loc='upper right')
save_fig(fig, '03_monthly_stacked_by_confidence.png')

# 04 - Box plot: FRP per month
months_order = sorted(df['year_month'].unique())
frp_capped = np.clip(df['frp'], 0, 100)
df['frp_capped'] = frp_capped
monthly_frp = [df[df['year_month'] == m]['frp_capped'].values for m in months_order]
fig, ax = plt.subplots(figsize=(18, 5))
bp = ax.boxplot(monthly_frp, patch_artist=True, showfliers=False, widths=0.6,
                medianprops=dict(color='white', linewidth=2))
kemarau_months = [m for m in months_order if int(m.split('-')[1]) in [6,7,8,9,10]]
for i, (patch, m) in enumerate(zip(bp['boxes'], months_order)):
    if m in kemarau_months:
        patch.set_facecolor(C_RED)
        patch.set_alpha(0.75)
    else:
        patch.set_facecolor(C_BLUE)
        patch.set_alpha(0.55)
ax.set_xticks(range(1, len(months_order)+1))
ax.set_xticklabels(months_order, rotation=45, ha='right', fontsize=8)
ax.set_title('FRP Distribution per Month (Capped at 100 MW)\nRed = Dry Season (Jun-Oct) | Blue = Wet Season', pad=15)
ax.set_ylabel('Fire Radiative Power - FRP (MW)')
ax.set_xlabel('Month')
red_patch = mpatches.Patch(color=C_RED, alpha=0.75, label='Dry Season (Jun-Oct)')
blue_patch = mpatches.Patch(color=C_BLUE, alpha=0.55, label='Wet Season (Nov-May)')
ax.legend(handles=[red_patch, blue_patch], loc='upper right')
save_fig(fig, '04_frp_boxplot_per_month.png')

# 05 - Dual axis: hotspot count vs total FRP per month
monthly_agg = df.groupby('year_month').agg(count=('frp', 'count'), total_frp=('frp', 'sum')).reset_index()
fig, ax1 = plt.subplots(figsize=(16, 5))
ax2 = ax1.twinx()
ax1.bar(range(len(monthly_agg)), monthly_agg['count'], color=C_BLUE, alpha=0.55, label='Hotspot Count', width=0.7)
ax2.plot(range(len(monthly_agg)), monthly_agg['total_frp'] / 1000, color=C_RED, lw=2.5,
         marker='o', markersize=5, label='Total FRP (GW)')
ax1.set_xticks(range(len(monthly_agg)))
ax1.set_xticklabels(monthly_agg['year_month'], rotation=45, ha='right', fontsize=8)
ax1.set_ylabel('Number of Hotspots', color=C_BLUE)
ax2.set_ylabel('Total Fire Energy Released (GW)', color=C_RED)
ax1.set_title('Monthly Hotspot Volume vs Total Fire Energy Released\n(Count = bars, Total FRP = line)', pad=15)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
ax1.tick_params(axis='y', labelcolor=C_BLUE)
ax2.tick_params(axis='y', labelcolor=C_RED)
save_fig(fig, '05_dual_axis_count_vs_total_frp.png')

# 06 - Year-over-Year comparison
yoy = df[df['year'].isin([2024, 2025])].groupby(['year', 'month']).size().unstack(level=0)
fig, ax = plt.subplots(figsize=(12, 5))
month_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
for yr, color, marker in [(2024, C_BLUE, 'o'), (2025, C_RED, 's')]:
    if yr in yoy.columns:
        ax.plot(yoy.index, yoy[yr], color=color, lw=2.2, marker=marker, markersize=7, label=str(yr))
        ax.fill_between(yoy.index, yoy[yr], alpha=0.10, color=color)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(month_labels)
ax.set_title('Year-over-Year Hotspot Count Comparison: 2024 vs 2025\n(Same months aligned - detecting worsening or improvement)', pad=15)
ax.set_ylabel('Number of Hotspots')
ax.set_xlabel('Month')
ax.legend()
ax.axvspan(6, 10, alpha=0.06, color=C_RED, label='Dry Season Zone')
save_fig(fig, '06_year_over_year_2024_vs_2025.png')

# ============================================================
# PILLAR B - HAZARD: Fire Intensity (Charts 07-11)
# ============================================================
print("[PILLAR B] HAZARD Fire Intensity Charts...")

# 07 - FRP distribution (log scale)
fig, ax = plt.subplots(figsize=(12, 5))
ax.hist(np.log1p(df['frp']), bins=60, color=C_BLUE, alpha=0.75, edgecolor='white', lw=0.4)
ax.axvline(np.log1p(100), color=C_RED, lw=2, linestyle='--', label='FRP = 100 MW (Extreme threshold)')
ax.axvline(np.log1p(500), color='#8e44ad', lw=2, linestyle='--', label='FRP = 500 MW (Mega-fire threshold)')
ax.set_title('Distribution of Fire Radiative Power - FRP (Log Scale)\nlog1p(FRP) transformation applied to reveal distribution shape', pad=15)
ax.set_xlabel('log1p(FRP) - log-transformed Fire Radiative Power (MW)')
ax.set_ylabel('Frequency')
ax.legend()
# Secondary x-axis labels
from matplotlib.ticker import FuncFormatter
def log_to_mw(x, pos):
    return f'{np.expm1(x):.0f}'
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ticks = [0, 1, 2, 3, 4, 5, 6, 7]
ax2.set_xticks(ticks)
ax2.set_xticklabels([f'{np.expm1(t):.0f} MW' for t in ticks], fontsize=9)
ax2.set_xlabel('Actual FRP Value (MW)', labelpad=8)
save_fig(fig, '07_frp_distribution_log_scale.png')

# 08 - Brightness and bright_t31 overlay
fig, ax = plt.subplots(figsize=(12, 5))
ax.hist(df['brightness'], bins=80, color=C_RED, alpha=0.6, label='Brightness (Fire Surface)', edgecolor='white', lw=0.3, density=True)
ax.hist(df['bright_t31'], bins=80, color=C_BLUE, alpha=0.6, label='Bright T31 (Background Temp)', edgecolor='white', lw=0.3, density=True)
ax.set_title('Temperature Distribution: Fire Surface (Brightness) vs Background (Bright T31)\nUnit: Kelvin (K) - Overlap reveals temperature gap between fire and land', pad=15)
ax.set_xlabel('Temperature (Kelvin)')
ax.set_ylabel('Density')
ax.legend()
save_fig(fig, '08_brightness_vs_bright_t31_overlay.png')

# 09 - Violin: FRP by confidence
fig, ax = plt.subplots(figsize=(10, 6))
data_violin = [np.clip(df[df['confidence'] == c]['frp'].values, 0, 100) for c in ['l', 'n', 'h']]
parts = ax.violinplot(data_violin, positions=[1, 2, 3], showmedians=True, showextrema=True)
for i, (pc, color) in enumerate(zip(parts['bodies'], [C_GREEN, C_BLUE, C_RED])):
    pc.set_facecolor(color)
    pc.set_alpha(0.65)
for part in ['cmedians', 'cmaxes', 'cmins', 'cbars']:
    parts[part].set_color(C_DARK)
    parts[part].set_linewidth(1.5)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['Low Confidence\n(l = 3.2%)', 'Nominal Confidence\n(n = 93.1%)', 'High Confidence\n(h = 3.8%)'])
ax.set_title('FRP Distribution by Detection Confidence Class (Capped at 100 MW)\nHigh confidence detections tend to have higher fire intensity', pad=15)
ax.set_ylabel('Fire Radiative Power - FRP (MW)')
save_fig(fig, '09_violin_frp_by_confidence.png')

# 10 - Scatter: FRP vs temp_delta
sample = df.sample(min(10000, len(df)), random_state=42)
fig, ax = plt.subplots(figsize=(10, 7))
for conf, color, label in [('l', C_GREEN, 'Low'), ('n', C_BLUE, 'Nominal'), ('h', C_RED, 'High')]:
    s = sample[sample['confidence'] == conf]
    size = s['pixel_area_km2'] * 80
    ax.scatter(s['temp_delta_K'], np.log1p(s['frp']), c=color, s=size, alpha=0.45,
               label=f'Confidence: {label} (n={len(s):,})', edgecolors='none')
ax.set_title('Fire Intensity (FRP) vs Temperature Delta: Fire vs Background\n(Bubble size = pixel area in km2)', pad=15)
ax.set_xlabel('Temperature Delta: Brightness minus Bright T31 (Kelvin)')
ax.set_ylabel('log1p(FRP) - Fire Radiative Power')
ax.legend(loc='upper left')
save_fig(fig, '10_scatter_frp_vs_temp_delta.png')

# 11 - Day vs Night comparison
dn = df.groupby('daynight').agg(count=('frp', 'count'), mean_frp=('frp', 'mean')).reset_index()
labels_dn = ['Daytime (D)', 'Nighttime (N)']
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
colors_dn = [C_ORANGE, C_NAVY]
bars1 = ax1.bar(labels_dn, dn['count'], color=colors_dn, edgecolor='white', lw=0.5)
for bar, val in zip(bars1, dn['count']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300,
             f'{val:,}\n({val/len(df)*100:.1f}%)', ha='center', fontweight='bold', fontsize=10)
ax1.set_title('Hotspot Count by Detection Period', pad=12)
ax1.set_ylabel('Number of Hotspots')
bars2 = ax2.bar(labels_dn, dn['mean_frp'], color=colors_dn, edgecolor='white', lw=0.5)
for bar, val in zip(bars2, dn['mean_frp']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{val:.2f} MW', ha='center', fontweight='bold', fontsize=10)
ax2.set_title('Mean FRP by Detection Period', pad=12)
ax2.set_ylabel('Mean Fire Radiative Power (MW)')
fig.suptitle('Daytime vs Nighttime Fire Detection Analysis\n(89.3% Daytime | 10.7% Nighttime)', fontsize=14, fontweight='bold', y=1.02)
save_fig(fig, '11_day_vs_night_count_and_frp.png')

# ============================================================
# PILLAR C - SPATIAL (Charts 12-15)
# ============================================================
print("[PILLAR C] Spatial Charts...")

# 12 - Scatter geo: all hotspots
sample_geo = df.sample(min(20000, len(df)), random_state=99)
fig, ax = plt.subplots(figsize=(12, 10))
sizes = np.clip(np.log1p(sample_geo['frp']) * 3, 2, 50)
scatter = ax.scatter(sample_geo['longitude'], sample_geo['latitude'],
                     c=sample_geo['frp_log'], cmap='YlOrRd',
                     s=sizes, alpha=0.45, linewidths=0)
cbar = plt.colorbar(scatter, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label('log1p(FRP) - Fire Intensity', fontsize=10)
cbar.set_ticks([0, 1, 2, 3, 4, 5, 6, 7])
cbar.set_ticklabels(['0', '1 MW', '6 MW', '19 MW', '53 MW', '147 MW', '402 MW', '1096 MW'])
ax.set_title(f'Spatial Distribution of Fire Hotspots in Kalimantan\n(Sample: {len(sample_geo):,} of {len(df):,} total hotspots | Color and size = Fire intensity)', pad=15)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_facecolor('#dfe6e9')
ax.set_xlim(107.5, 120.5)
ax.set_ylim(-5.0, 5.0)
ax.axhline(0, color='white', lw=0.8, linestyle=':', alpha=0.7)
save_fig(fig, '12_spatial_scatter_all_hotspots.png')

# 13 - Hexbin density
fig, ax = plt.subplots(figsize=(12, 9))
hb = ax.hexbin(df['longitude'], df['latitude'], gridsize=60, cmap='inferno', mincnt=1)
cbar = plt.colorbar(hb, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label('Hotspot Count per Hex Cell', fontsize=10)
ax.set_title('Hotspot Density Hexbin Map - Kalimantan\n(Darker/brighter = higher concentration of fire detections)', pad=15)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_facecolor('#1a1a2e')
ax.set_xlim(107.5, 120.5)
ax.set_ylim(-5.0, 5.0)
save_fig(fig, '13_hexbin_density_map.png')

# 14 - KDE spatial contour
from scipy.stats import gaussian_kde
sample_kde = df.sample(min(15000, len(df)), random_state=7)
x = sample_kde['longitude'].values
y = sample_kde['latitude'].values
xgrid = np.linspace(108, 119.5, 200)
ygrid = np.linspace(-4.5, 4.5, 200)
Xg, Yg = np.meshgrid(xgrid, ygrid)
positions = np.vstack([Xg.ravel(), Yg.ravel()])
values = np.vstack([x, y])
kernel = gaussian_kde(values, bw_method=0.05)
Z = kernel(positions).reshape(Xg.shape)
fig, ax = plt.subplots(figsize=(12, 9))
ax.set_facecolor('#1e3a5f')
contour_f = ax.contourf(Xg, Yg, Z, levels=20, cmap='hot')
contour_l = ax.contour(Xg, Yg, Z, levels=10, colors='white', alpha=0.25, linewidths=0.5)
cbar = plt.colorbar(contour_f, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label('Hotspot Density (KDE)', fontsize=10)
ax.set_title('Kernel Density Estimation (KDE) of Hotspot Spatial Concentration\n(Hottest areas = highest density of fire detections)', pad=15)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.axhline(0, color='white', lw=0.8, linestyle=':', alpha=0.5)
save_fig(fig, '14_kde_spatial_contour.png')

# 15 - Bar: per province
prov_agg = df.groupby('kalimantan_region').agg(
    count=('frp', 'count'),
    total_frp=('frp', 'sum'),
    mean_frp=('frp', 'mean')
).reset_index().sort_values('count', ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
colors_prov = [PROV_COLORS.get(p, C_GRAY) for p in prov_agg['kalimantan_region']]
bars = ax1.barh(prov_agg['kalimantan_region'], prov_agg['count'], color=colors_prov, edgecolor='white', lw=0.5)
for bar, val in zip(bars, prov_agg['count']):
    pct = val / len(df) * 100
    ax1.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
             f'{val:,} ({pct:.1f}%)', va='center', fontweight='bold', fontsize=10)
ax1.set_title('Total Hotspot Count by Province', pad=12)
ax1.set_xlabel('Number of Hotspots')
ax1.invert_yaxis()
bars2 = ax2.barh(prov_agg['kalimantan_region'], prov_agg['total_frp']/1000, color=colors_prov, edgecolor='white', lw=0.5)
for bar, val in zip(bars2, prov_agg['total_frp']/1000):
    ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             f'{val:,.0f} GW', va='center', fontweight='bold', fontsize=10)
ax2.set_title('Total Fire Energy Released by Province (GW)', pad=12)
ax2.set_xlabel('Total FRP (GW)')
ax2.invert_yaxis()
fig.suptitle('Hotspot Distribution by Kalimantan Province\n(Kalimantan Barat is the primary epicenter)', fontsize=14, fontweight='bold', y=1.02)
save_fig(fig, '15_bar_hotspots_by_province.png')

# ============================================================
# PILLAR D - EXTREME EVENTS (Charts 16-18)
# ============================================================
print("[PILLAR D] Extreme Events Charts...")

# 16 - Scatter timeline: FRP over time
fig, ax = plt.subplots(figsize=(16, 6))
normal = df[df['frp'] <= 50]
extreme = df[(df['frp'] > 50) & (df['frp'] <= 100)]
mega = df[df['frp'] > 100]
ax.scatter(normal['acq_date'], normal['frp'], c=C_BLUE, s=3, alpha=0.25, label='Normal (<= 50 MW)')
ax.scatter(extreme['acq_date'], extreme['frp'], c=C_ORANGE, s=15, alpha=0.7, label='Extreme (50-100 MW)')
ax.scatter(mega['acq_date'], mega['frp'], c=C_RED, s=40, alpha=0.9, marker='^', label=f'Mega Fire (>100 MW, n={len(mega):,})')
ax.set_title('Fire Intensity (FRP) Timeline: Identifying Extreme Fire Events\n(All 61,583 hotspots plotted by detection date)', pad=15)
ax.set_ylabel('Fire Radiative Power (MW)')
ax.set_xlabel('Detection Date')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
ax.legend(loc='upper right')
ax.set_ylim(-20, 1000)
save_fig(fig, '16_frp_timeline_extreme_events.png')

# 17 - Top extreme event dates
df['date_only'] = df['acq_date'].dt.date
top_dates = df[df['frp'] > 50].groupby('date_only').agg(
    total_frp=('frp', 'sum'),
    max_frp=('frp', 'max'),
    count=('frp', 'count')
).sort_values('total_frp', ascending=False).head(20)
fig, ax = plt.subplots(figsize=(14, 7))
colors_bar = [C_RED if v > 500 else C_ORANGE for v in top_dates['total_frp']]
bars = ax.barh([str(d) for d in top_dates.index], top_dates['total_frp'],
               color=colors_bar, edgecolor='white', lw=0.4)
for bar, (_, row) in zip(bars, top_dates.iterrows()):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            f'{row["total_frp"]:.0f} MW ({row["count"]} events, max {row["max_frp"]:.0f} MW)',
            va='center', fontsize=8.5)
ax.set_title('Top 20 Critical Days by Total Fire Energy Released\n(Sum of FRP > 50 MW events per day)', pad=15)
ax.set_xlabel('Total FRP Released (MW)')
ax.invert_yaxis()
save_fig(fig, '17_top20_critical_days_total_frp.png')

# 18 - Monthly total FRP cumulative
monthly_frp = df.groupby('year_month').agg(total_frp=('frp', 'sum'), count=('frp', 'count')).reset_index()
monthly_frp['cumulative_frp'] = monthly_frp['total_frp'].cumsum()
fig, ax = plt.subplots(figsize=(16, 5))
ax.fill_between(range(len(monthly_frp)), monthly_frp['cumulative_frp'] / 1e6, alpha=0.20, color=C_RED)
ax.plot(range(len(monthly_frp)), monthly_frp['cumulative_frp'] / 1e6, color=C_RED, lw=2.5, marker='o', markersize=4)
ax.set_xticks(range(len(monthly_frp)))
ax.set_xticklabels(monthly_frp['year_month'], rotation=45, ha='right', fontsize=8)
ax.set_title('Cumulative Total Fire Energy Released Over Time\n(Kalimantan: Aug 2024 - May 2026, in Terawatt-minutes)', pad=15)
ax.set_ylabel('Cumulative Total FRP (TW-min x 10^6)')
ax.set_xlabel('Month')
save_fig(fig, '18_cumulative_total_frp_over_time.png')

# ============================================================
# PILLAR E - VULNERABILITY (Charts 19-21)
# ============================================================
print("[PILLAR E] Vulnerability Charts...")

# 19 - Top recurrence grid cells
top_recurrence = df.groupby('coord_grid_05deg').agg(
    count=('frp', 'count'),
    total_frp=('frp', 'sum'),
    mean_lat=('latitude', 'mean'),
    mean_lon=('longitude', 'mean'),
    province=('kalimantan_region', lambda x: x.mode()[0])
).sort_values('count', ascending=False).head(25).reset_index()
fig, ax = plt.subplots(figsize=(14, 8))
colors_rec = [PROV_COLORS.get(p, C_GRAY) for p in top_recurrence['province']]
bars = ax.barh([f"{r['mean_lat']:.1f}N, {r['mean_lon']:.1f}E ({r['province'].split()[1]})"
                for _, r in top_recurrence.iterrows()],
               top_recurrence['count'], color=colors_rec, edgecolor='white', lw=0.3)
for bar, val in zip(bars, top_recurrence['count']):
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontweight='bold', fontsize=9)
ax.set_title('Top 25 High-Recurrence Locations (0.5 deg Grid Cells)\n(Chronic fire zones = high vulnerability per PRD)', pad=15)
ax.set_xlabel('Total Hotspot Detections (Aug 2024 - May 2026)')
ax.invert_yaxis()
ax.set_yticklabels(ax.get_yticklabels(), fontsize=8.5)
legend_patches = [mpatches.Patch(color=c, label=p.split()[1] if ' ' in p else p)
                  for p, c in PROV_COLORS.items() if p != 'Other']
ax.legend(handles=legend_patches, loc='lower right', fontsize=9)
save_fig(fig, '19_top25_recurrence_chronic_fire_zones.png')

# 20 - Heatmap: Region x Season
season_region = df.groupby(['kalimantan_region', 'season']).size().unstack(fill_value=0)
if season_region.index.isin(['Other']).any():
    season_region = season_region[season_region.index != 'Other']
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(season_region, cmap='YlOrRd', annot=True, fmt=',d', ax=ax,
            linewidths=0.5, annot_kws={'size': 11, 'weight': 'bold'},
            cbar_kws={'label': 'Hotspot Count'})
ax.set_title('Hotspot Count: Kalimantan Region vs Season\n(Risk Matrix: where + when = highest fire pressure)', pad=15)
ax.set_xlabel('Season')
ax.set_ylabel('Province')
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha='right')
save_fig(fig, '20_heatmap_region_vs_season.png')

# 21 - Weekday vs Weekend FRP
wd = df.groupby('is_weekend').agg(
    count=('frp', 'count'),
    mean_frp=('frp', 'mean'),
    median_frp=('frp', 'median')
).reset_index()
wd_labels = ['Weekday (Mon-Fri)', 'Weekend (Sat-Sun)']
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.bar(wd_labels, wd['count'], color=[C_BLUE, C_ORANGE], edgecolor='white')
for i, (val, label) in enumerate(zip(wd['count'], wd_labels)):
    pct = val / len(df) * 100
    ax1.text(i, val + 200, f'{val:,}\n({pct:.1f}%)', ha='center', fontweight='bold')
ax1.set_title('Hotspot Count: Weekday vs Weekend', pad=12)
ax1.set_ylabel('Number of Hotspots')
ax2.bar(wd_labels, wd['mean_frp'], color=[C_BLUE, C_ORANGE], edgecolor='white')
for i, val in enumerate(wd['mean_frp']):
    ax2.text(i, val + 0.1, f'{val:.2f} MW', ha='center', fontweight='bold')
ax2.set_title('Mean FRP: Weekday vs Weekend', pad=12)
ax2.set_ylabel('Mean Fire Radiative Power (MW)')
fig.suptitle('Weekday vs Weekend Fire Activity Pattern\n(Signal for human-caused vs natural ignition)', fontsize=14, fontweight='bold', y=1.02)
save_fig(fig, '21_weekday_vs_weekend_fire_activity.png')

# ============================================================
# PILLAR F - COMPOSITE (Charts 22-24)
# ============================================================
print("[PILLAR F] Composite Charts...")

# 22 - Correlation heatmap
num_cols = ['latitude', 'longitude', 'brightness', 'bright_t31', 'frp', 'frp_log',
            'scan', 'track', 'temp_delta_K', 'pixel_area_km2', 'confidence_num',
            'hazard_score', 'fire_recurrence_count']
corr_matrix = df[num_cols].corr().round(2)
fig, ax = plt.subplots(figsize=(14, 11))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, cmap='RdBu_r', center=0, annot=True,
            fmt='.2f', ax=ax, square=True, linewidths=0.5,
            annot_kws={'size': 8}, vmin=-1, vmax=1,
            cbar_kws={'label': 'Pearson Correlation Coefficient', 'shrink': 0.8})
ax.set_title('Pearson Correlation Matrix - All Numeric Features\n(Lower triangle | Red = Positive, Blue = Negative)', pad=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
save_fig(fig, '22_pearson_correlation_matrix.png')

# 23 - Confidence breakdown donut
conf_counts = df['confidence'].value_counts()
conf_labels = {
    'l': f"Low (l)\n{conf_counts.get('l', 0):,} ({conf_counts.get('l', 0)/len(df)*100:.1f}%)",
    'n': f"Nominal (n)\n{conf_counts.get('n', 0):,} ({conf_counts.get('n', 0)/len(df)*100:.1f}%)",
    'h': f"High (h)\n{conf_counts.get('h', 0):,} ({conf_counts.get('h', 0)/len(df)*100:.1f}%)"
}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
sizes = [conf_counts.get('l', 0), conf_counts.get('n', 0), conf_counts.get('h', 0)]
labels_c = [conf_labels['l'], conf_labels['n'], conf_labels['h']]
colors_c = [C_GREEN, C_BLUE, C_RED]
wedges, texts = ax1.pie(sizes, colors=colors_c, startangle=90,
                         wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2))
ax1.legend(wedges, labels_c, loc='center', bbox_to_anchor=(0.5, -0.08), fontsize=10)
ax1.set_title('Detection Confidence Distribution\n(Donut Chart)', pad=12)
conf_frp = df.groupby('confidence').agg(mean_frp=('frp', 'mean'), median_frp=('frp', 'median')).reset_index()
x_pos = np.arange(3)
width = 0.35
ax2.bar(x_pos - width/2, conf_frp['mean_frp'], width, label='Mean FRP', color=[C_GREEN, C_BLUE, C_RED], alpha=0.75)
ax2.bar(x_pos + width/2, conf_frp['median_frp'], width, label='Median FRP',
        color=[C_GREEN, C_BLUE, C_RED], alpha=0.45, hatch='//')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(['Low (l)', 'Nominal (n)', 'High (h)'])
ax2.set_title('Mean vs Median FRP by Confidence\n(High confidence = higher fire intensity)', pad=12)
ax2.set_ylabel('Fire Radiative Power (MW)')
ax2.legend()
fig.suptitle('Detection Confidence Analysis: Distribution and Fire Intensity by Confidence Level',
             fontsize=13, fontweight='bold', y=1.02)
save_fig(fig, '23_confidence_donut_and_frp_comparison.png')

# 24 - Fire intensity class distribution per province
intensity_order = ['Low (<5 MW)', 'Medium (5-20 MW)', 'High (20-50 MW)', 'Extreme (>50 MW)']
prov_intensity = df[df['kalimantan_region'] != 'Other'].groupby(
    ['kalimantan_region', 'fire_intensity_class']).size().unstack(fill_value=0)
prov_intensity = prov_intensity.reindex(columns=intensity_order, fill_value=0)
prov_intensity_pct = prov_intensity.div(prov_intensity.sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(14, 6))
bottom = np.zeros(len(prov_intensity_pct))
int_colors = [C_GREEN, C_YELLOW, C_ORANGE, C_RED]
for col, color in zip(intensity_order, int_colors):
    ax.bar(prov_intensity_pct.index, prov_intensity_pct[col], bottom=bottom,
           color=color, label=col, edgecolor='white', lw=0.4, width=0.65)
    bottom += prov_intensity_pct[col].values
ax.set_title('Fire Intensity Class Composition by Province\n(Stacked 100% - Proportion of Low/Medium/High/Extreme per province)', pad=15)
ax.set_ylabel('Percentage of Hotspots (%)')
ax.set_xlabel('Province')
ax.set_xticklabels(prov_intensity_pct.index, rotation=15, ha='right')
ax.legend(loc='upper right', fontsize=9)
ax.set_ylim(0, 110)
save_fig(fig, '24_intensity_class_composition_by_province.png')

# ============================================================
# BONUS - FE Insight Charts
# ============================================================
print("[BONUS] Feature Engineering Insight Charts...")

# FE-01: Weighted FRP per month
monthly_wfrp = df.groupby('year_month').agg(
    raw_frp=('frp', 'sum'),
    weighted=('weighted_frp', 'sum')
).reset_index()
fig, ax = plt.subplots(figsize=(16, 5))
x = range(len(monthly_wfrp))
ax.bar(x, monthly_wfrp['raw_frp']/1000, width=0.4, align='edge', label='Raw Total FRP (GW)', color=C_BLUE, alpha=0.7)
ax.bar([i - 0.4 for i in x], monthly_wfrp['weighted']/1000, width=0.4, align='edge',
       label='Confidence-Weighted FRP (GW)', color=C_RED, alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels(monthly_wfrp['year_month'], rotation=45, ha='right', fontsize=8)
ax.set_title('Raw FRP vs Confidence-Weighted FRP per Month (GW)\n(Weighted FRP = FRP corrected for sensor reliability)', pad=15)
ax.set_ylabel('Total FRP (GW)')
ax.legend()
save_fig(fig, 'FE01_raw_vs_weighted_frp_monthly.png')

# FE-02: Hazard score distribution per province
fig, ax = plt.subplots(figsize=(12, 6))
prov_list = [p for p in prov_intensity.index if p != 'Other']
data_haz = [df[df['kalimantan_region'] == p]['hazard_score'].values for p in prov_list]
bp = ax.boxplot(data_haz, patch_artist=True, showfliers=False, widths=0.6,
                medianprops=dict(color='white', linewidth=2))
for patch, prov in zip(bp['boxes'], prov_list):
    patch.set_facecolor(PROV_COLORS.get(prov, C_GRAY))
    patch.set_alpha(0.75)
ax.set_xticklabels(prov_list, rotation=20, ha='right')
ax.set_title('Hazard Score Distribution by Kalimantan Province\n(Composite HAZARD index: 40% FRP + 35% Temp Delta + 25% Confidence)', pad=15)
ax.set_ylabel('Hazard Score (0-100)')
save_fig(fig, 'FE02_hazard_score_by_province.png')

# FE-03: Recurrence scatter map
top_grids = df.groupby('coord_grid_05deg').agg(
    count=('frp', 'count'),
    mean_lat=('latitude', 'mean'),
    mean_lon=('longitude', 'mean'),
    mean_frp=('frp', 'mean')
).reset_index()
high_rec = top_grids[top_grids['count'] >= 5]
fig, ax = plt.subplots(figsize=(12, 9))
ax.set_facecolor('#dfe6e9')
ax.scatter(df.sample(5000)['longitude'], df.sample(5000)['latitude'],
           c=C_GRAY, s=2, alpha=0.2, label='All hotspots (sample)')
sc = ax.scatter(high_rec['mean_lon'], high_rec['mean_lat'],
                c=high_rec['count'], cmap='hot', s=high_rec['count'] * 0.5 + 20,
                alpha=0.85, zorder=5, edgecolors=C_DARK, linewidths=0.4)
cbar = plt.colorbar(sc, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label('Recurrence Count (total hotspot detections)', fontsize=9)
ax.set_title(f'Chronic Fire Zones (High Recurrence Areas) in Kalimantan\n({len(high_rec):,} grid cells with >= 5 detections in 22 months)', pad=15)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_xlim(107.5, 120.5)
ax.set_ylim(-5.0, 5.0)
save_fig(fig, 'FE03_chronic_fire_zones_recurrence_map.png')

print("\n[ALL 27 CHARTS SAVED SUCCESSFULLY]")
