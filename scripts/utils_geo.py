"""
Geospatial Utilities Module for FIRELINE Project
Handles GeoJSON downloading, verification, and boundary plotting.
"""

import os
import json
import urllib.request
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe

GEOJSON_URL = (
    "https://raw.githubusercontent.com/denyherianto/"
    "indonesia-geojson-topojson-maps-with-38-provinces/main/GeoJSON/indonesia-38-provinces.geojson"
)
LOCAL_GEOJSON_PATH = "indonesia_provinces.json"

PROV_PALETTE = {
    'Kalimantan Barat':   '#2980b9',
    'Kalimantan Tengah':  '#e67e22',
    'Kalimantan Timur':   '#27ae60',
    'Kalimantan Selatan': '#c0392b',
    'Kalimantan Utara':   '#8e44ad',
}

def ensure_geojson(target_path=LOCAL_GEOJSON_PATH):
    """Ensure the Indonesia GeoJSON file is downloaded and valid."""
    if not os.path.exists(target_path):
        print(f"Downloading Indonesia GeoJSON to {target_path}...")
        urllib.request.urlretrieve(GEOJSON_URL, target_path)
    
    with open(target_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    features = data.get('features', [])
    kal_count = sum(1 for ft in features if 'alimantan' in ft['properties'].get('PROVINSI', ''))
    print(f"GeoJSON loaded: {len(features)} total provinces, {kal_count} Kalimantan provinces.")
    return data

def draw_boundaries(ax, features, facecolor='#dfe6e9', edgecolor='white',
                    linewidth=0.8, alpha=0.85, use_prov_colors=False,
                    label_provinces=False):
    """Draw GeoJSON MultiPolygon/Polygon boundaries on a matplotlib axis."""
    patches, colors = [], []

    for ft in features:
        geom = ft['geometry']
        geom_type = geom['type']
        prov_name = ft['properties'].get('PROVINSI', '')
        color = PROV_PALETTE.get(prov_name, '#bdc3c7') if use_prov_colors else facecolor

        rings = [geom['coordinates']] if geom_type == 'Polygon' else geom['coordinates']

        for ring_group in rings:
            coords = np.array(ring_group[0])
            if len(coords) < 3:
                continue
            patches.append(Polygon(coords, closed=True))
            colors.append(color)

        if label_provinces:
            all_coords = []
            for ring_group in rings:
                all_coords.extend(ring_group[0])
            all_coords = np.array(all_coords)
            cx, cy = all_coords[:, 0].mean(), all_coords[:, 1].mean()
            short = prov_name.replace('Kalimantan ', 'Kal. ')
            ax.text(cx, cy, short, fontsize=7.5, ha='center', va='center',
                    color='white', fontweight='bold',
                    path_effects=[pe.withStroke(linewidth=2, foreground='#2c3e50')])

    coll = PatchCollection(patches, facecolors=colors, edgecolors=edgecolor,
                           linewidths=linewidth, alpha=alpha, zorder=1)
    ax.add_collection(coll)

if __name__ == '__main__':
    ensure_geojson()
