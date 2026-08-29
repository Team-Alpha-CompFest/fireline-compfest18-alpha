"""
Spatial Maps with Kalimantan Province Boundaries
Regenerates charts 12, 13, 14 using GeoJSON province borders
Output: PNG files (no HTML)
"""

import os, json, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
from scipy.stats import gaussian_kde

warnings.filterwarnings('ignore')

FEAT_PATH = 'EDA/01_fireline_hotspot_kalimantan/04_feature_engineering/fireline_hotspot_featured.csv'
GEO_PATH  = 'indonesia_provinces.json'
OUT_VIZ   = 'EDA/01_fireline_hotspot_kalimantan/02_visualizations'

# ============================================================
# STYLE
# ============================================================
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelweight': 'bold',
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.25,
})

C_RED    = '#c0392b'
C_ORANGE = '#e67e22'
C_BLUE   = '#2980b9'
C_NAVY   = '#1a252f'
C_DARK   = '#2c3e50'
C_GRAY   = '#7f8c8d'

PROV_PALETTE = {
    'Kalimantan Barat':   '#2980b9',
    'Kalimantan Tengah':  '#e67e22',
    'Kalimantan Timur':   '#27ae60',
    'Kalimantan Selatan': '#c0392b',
    'Kalimantan Utara':   '#8e44ad',
}
KALIMANTAN_PROVINCES = set(PROV_PALETTE.keys())

# ============================================================
# LOAD DATA
# ============================================================
print("Loading data...")
df = pd.read_csv(FEAT_PATH, parse_dates=['acq_date'])
print(f"  Rows: {len(df):,}")

# ============================================================
# LOAD AND PARSE GEOJSON
# ============================================================
print("Loading GeoJSON...")
with open(GEO_PATH, encoding='utf-8') as f:
    geo = json.load(f)

features = geo['features']
print(f"  Total features: {len(features)}")

# Filter Kalimantan provinces only
kal_features = [ft for ft in features if 'alimantan' in ft['properties'].get('PROVINSI', '')]
print(f"  Kalimantan features: {[ft['properties']['PROVINSI'] for ft in kal_features]}")

def get_prov_color(name):
    for k, v in PROV_PALETTE.items():
        if k.lower() in name.lower():
            return v
    return '#bdc3c7'

# ============================================================
# HELPER: Draw GeoJSON polygons on a matplotlib axis
# ============================================================
def draw_geojson(ax, features, facecolor='#dfe6e9', edgecolor='white',
                 linewidth=0.8, alpha=0.85, use_prov_colors=False,
                 label_provinces=False):
    """
    Draw GeoJSON MultiPolygon/Polygon features onto a matplotlib Axes.
    """
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection

    all_patches = []
    all_colors  = []

    for ft in features:
        geom = ft['geometry']
        geom_type = geom['type']
        prov_name = ft['properties'].get('PROVINSI', '')
        color = get_prov_color(prov_name) if use_prov_colors else facecolor

        if geom_type == 'Polygon':
            rings = [geom['coordinates']]
        elif geom_type == 'MultiPolygon':
            rings = geom['coordinates']
        else:
            continue

        for ring_group in rings:
            coords = np.array(ring_group[0])  # outer ring only
            if len(coords) < 3:
                continue
            patch = Polygon(coords, closed=True)
            all_patches.append(patch)
            all_colors.append(color)

        # Label province centroid
        if label_provinces:
            all_coords = []
            for ring_group in rings:
                all_coords.extend(ring_group[0])
            all_coords = np.array(all_coords)
            cx = all_coords[:, 0].mean()
            cy = all_coords[:, 1].mean()
            short = prov_name.replace('Kalimantan ', 'Kal. ')
            ax.text(cx, cy, short, fontsize=7.5, ha='center', va='center',
                    color='white', fontweight='bold',
                    path_effects=[pe.withStroke(linewidth=2, foreground='#2c3e50')])

    from matplotlib.collections import PatchCollection
    coll = PatchCollection(all_patches, facecolors=all_colors,
                           edgecolors=edgecolor, linewidths=linewidth, alpha=alpha,
                           zorder=1)
    ax.add_collection(coll)

def save_fig(fig, name):
    path = os.path.join(OUT_VIZ, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    print(f"  Saved: {name}")

# Map bounds (Kalimantan)
XMIN, XMAX = 107.8, 120.0
YMIN, YMAX = -4.8, 5.0

# ============================================================
# CHART 12 - Spatial Scatter with Province Map
# ============================================================
print("\nGenerating Chart 12...")
sample_geo = df.sample(min(25000, len(df)), random_state=99)
frp_log = np.log1p(sample_geo['frp'])

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor('#1e2d3d')
fig.patch.set_facecolor('#1e2d3d')

# Draw all Indonesia provinces (non-Kalimantan in muted tone)
all_non_kal = [ft for ft in features if 'alimantan' not in ft['properties'].get('PROVINSI', '')]
draw_geojson(ax, all_non_kal, facecolor='#2d3d4e', edgecolor='#3d5166', linewidth=0.5, alpha=0.6)
# Draw Kalimantan with province colors
draw_geojson(ax, kal_features, use_prov_colors=True, edgecolor='#a0aec0', linewidth=1.2, alpha=0.55, label_provinces=True)

# Hotspot scatter
sizes = np.clip(frp_log * 2.5, 1.5, 45)
norm = Normalize(vmin=frp_log.min(), vmax=frp_log.quantile(0.98))
cmap = plt.cm.YlOrRd
scatter = ax.scatter(
    sample_geo['longitude'], sample_geo['latitude'],
    c=frp_log, cmap=cmap, norm=norm,
    s=sizes, alpha=0.65, linewidths=0, zorder=3
)

# Colorbar
cbar = plt.colorbar(scatter, ax=ax, fraction=0.028, pad=0.02, shrink=0.85)
cbar.set_label('log1p(FRP) -- Fire Intensity', fontsize=9, color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white', fontsize=8)
tick_vals = [0, 1, 2, 3, 4, 5, 6]
cbar.set_ticks(tick_vals)
cbar.set_ticklabels([f'{np.expm1(v):.0f} MW' for v in tick_vals])

# Legend: province colors
legend_patches = [mpatches.Patch(facecolor=c, label=p.replace('Kalimantan ', 'Kal. '))
                  for p, c in PROV_PALETTE.items()]
ax.legend(handles=legend_patches, loc='lower left', fontsize=8.5,
          framealpha=0.85, facecolor='#1e2d3d', edgecolor='#a0aec0',
          labelcolor='white', title='Province', title_fontsize=8.5)

ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)
ax.axhline(0, color='#6c8fa8', lw=0.7, linestyle=':', alpha=0.6)
ax.set_xlabel('Longitude', color='white')
ax.set_ylabel('Latitude', color='white')
ax.tick_params(colors='white', labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor('#3d5166')
ax.set_title(
    f'Spatial Distribution of Fire Hotspots across Kalimantan\n'
    f'(Sample: {len(sample_geo):,} of {len(df):,} detections | Color = Fire Intensity | Size = log(FRP))',
    pad=14, color='white'
)
save_fig(fig, '12_spatial_scatter_all_hotspots.png')

# ============================================================
# CHART 13 - Hexbin Density with Province Borders
# ============================================================
print("Generating Chart 13...")
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor('#0d1117')
fig.patch.set_facecolor('#0d1117')

hb = ax.hexbin(
    df['longitude'], df['latitude'],
    gridsize=65, cmap='inferno', mincnt=1, zorder=2, alpha=0.92
)
# Province borders on top of hexbin
draw_geojson(ax, kal_features, facecolor='none', edgecolor='#ffffff',
             linewidth=1.6, alpha=1.0, label_provinces=True)
draw_geojson(ax, all_non_kal, facecolor='none', edgecolor='#3d5166',
             linewidth=0.5, alpha=0.7)

cbar = plt.colorbar(hb, ax=ax, fraction=0.028, pad=0.02, shrink=0.85)
cbar.set_label('Hotspot Count per Hex Cell', fontsize=9, color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white', fontsize=8)

ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)
ax.axhline(0, color='#6c8fa8', lw=0.7, linestyle=':', alpha=0.6)
ax.set_xlabel('Longitude', color='white')
ax.set_ylabel('Latitude', color='white')
ax.tick_params(colors='white', labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor('#3d5166')
ax.set_title(
    'Hotspot Density Hexbin Map -- Kalimantan Province Boundaries Overlaid\n'
    '(Color = concentration of fire detections per hexagonal cell | All 61,583 records)',
    pad=14, color='white'
)
save_fig(fig, '13_hexbin_density_map.png')

# ============================================================
# CHART 14 - KDE Contour with Province Map
# ============================================================
print("Generating Chart 14...")
sample_kde = df.sample(min(18000, len(df)), random_state=7)
x = sample_kde['longitude'].values
y = sample_kde['latitude'].values

xgrid = np.linspace(XMIN, XMAX, 220)
ygrid = np.linspace(YMIN, YMAX, 200)
Xg, Yg = np.meshgrid(xgrid, ygrid)
positions = np.vstack([Xg.ravel(), Yg.ravel()])
values = np.vstack([x, y])
kernel = gaussian_kde(values, bw_method=0.06)
Z = kernel(positions).reshape(Xg.shape)

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor('#0f1923')
fig.patch.set_facecolor('#0f1923')

contour_f = ax.contourf(Xg, Yg, Z, levels=25, cmap='hot', alpha=0.88, zorder=2)
contour_l = ax.contour(Xg, Yg, Z, levels=10, colors='white', alpha=0.20, linewidths=0.5, zorder=3)

# Province borders on top
draw_geojson(ax, kal_features, facecolor='none', edgecolor='#ffffff',
             linewidth=1.8, alpha=1.0, label_provinces=True)
draw_geojson(ax, all_non_kal, facecolor='none', edgecolor='#2d4a5e',
             linewidth=0.6, alpha=0.8)

cbar = plt.colorbar(contour_f, ax=ax, fraction=0.028, pad=0.02, shrink=0.85)
cbar.set_label('Hotspot Density (KDE)', fontsize=9, color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white', fontsize=8)

ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)
ax.axhline(0, color='#6c8fa8', lw=0.7, linestyle=':', alpha=0.6)
ax.set_xlabel('Longitude', color='white')
ax.set_ylabel('Latitude', color='white')
ax.tick_params(colors='white', labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor('#2d4a5e')
ax.set_title(
    'Kernel Density Estimation (KDE) -- Fire Hotspot Spatial Concentration\n'
    'Province borders shown in white | Brighter areas = highest fire detection density',
    pad=14, color='white'
)
save_fig(fig, '14_kde_spatial_contour.png')

# ============================================================
# BONUS: Chart FE-03 with map (chronic fire zones)
# ============================================================
print("Regenerating FE03 with province map...")
top_grids = df.groupby('coord_grid_05deg').agg(
    count=('frp', 'count'),
    mean_lat=('latitude', 'mean'),
    mean_lon=('longitude', 'mean'),
    mean_frp=('frp', 'mean')
).reset_index()
high_rec = top_grids[top_grids['count'] >= 5]

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor('#1a2733')
fig.patch.set_facecolor('#1a2733')

draw_geojson(ax, all_non_kal, facecolor='#1e2d3d', edgecolor='#2d4050', linewidth=0.5, alpha=0.6)
draw_geojson(ax, kal_features, use_prov_colors=True, edgecolor='#a0aec0',
             linewidth=1.3, alpha=0.35, label_provinces=True)

sc = ax.scatter(
    high_rec['mean_lon'], high_rec['mean_lat'],
    c=high_rec['count'], cmap='YlOrRd',
    s=np.clip(high_rec['count'] * 0.6 + 15, 15, 250),
    alpha=0.90, zorder=5, edgecolors='#2c3e50', linewidths=0.4
)

cbar = plt.colorbar(sc, ax=ax, fraction=0.028, pad=0.02, shrink=0.85)
cbar.set_label('Recurrence Count (total detections per 0.5 deg grid)', fontsize=9, color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white', fontsize=8)

ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)
ax.axhline(0, color='#6c8fa8', lw=0.7, linestyle=':', alpha=0.6)
ax.set_xlabel('Longitude', color='white')
ax.set_ylabel('Latitude', color='white')
ax.tick_params(colors='white', labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor('#2d4050')

legend_patches = [mpatches.Patch(facecolor=c, alpha=0.7, label=p.replace('Kalimantan ', 'Kal. '))
                  for p, c in PROV_PALETTE.items()]
ax.legend(handles=legend_patches, loc='lower left', fontsize=8.5,
          framealpha=0.85, facecolor='#1a2733', edgecolor='#a0aec0',
          labelcolor='white', title='Province', title_fontsize=8.5)

ax.set_title(
    f'Chronic Fire Zones (High Recurrence) in Kalimantan\n'
    f'({len(high_rec):,} grid cells with >= 5 detections in 22 months | Size and color = recurrence count)',
    pad=14, color='white'
)
save_fig(fig, 'FE03_chronic_fire_zones_recurrence_map.png')

print("\n[ALL 4 SPATIAL CHARTS WITH MAP BACKGROUND COMPLETED]")
