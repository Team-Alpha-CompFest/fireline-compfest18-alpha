"""
Generate High-Quality Analytical Visualizations for COMPFEST Case Study
Based 100% on Official Panitia Dataset (61,583 Hotspots)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set modern aesthetic
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

os.makedirs('visualizations', exist_ok=True)

print("[1/3] Loading Master Processed Data...")
df = pd.read_csv('02_dataset_olahan_master_tableau/fireline_hotspot_kalimantan_processed_master.csv')
df['acq_date'] = pd.to_datetime(df['acq_date'])

# 1. TEMPORAL & SEASONALITY CHART
print("[2/3] Generating Temporal Trend Chart...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=False)

# Monthly Trend with Season Highlight
monthly_counts = df.groupby('year_month').size()
monthly_frp = df.groupby('year_month')['frp'].sum()

ax1.plot(monthly_counts.index, monthly_counts.values, marker='o', color='#e63946', linewidth=2.5, label='Jumlah Hotspot')
ax1.fill_between(monthly_counts.index, monthly_counts.values, color='#e63946', alpha=0.15)
ax1.set_title('Tren Temporal Titik Api (Hotspot) Bulanan di Kalimantan (Ags 2024 - Mei 2026)', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylabel('Total Titik Api Terdeteksi', fontsize=11, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, linestyle='--', alpha=0.6)

# Annotate Peak
peak_idx = monthly_counts.idxmax()
peak_val = monthly_counts.max()
ax1.annotate(f'Puncak Karhutla: {peak_idx}\n({peak_val:,} Hotspot)', 
             xy=(peak_idx, peak_val), xytext=(30, 20), textcoords='offset points',
             arrowprops=dict(arrowstyle="->", color='black', lw=1.5),
             bbox=dict(boxstyle="round,pad=0.3", fc="#ffdddd", ec="#e63946", lw=1.5),
             fontweight='bold')

# Province Stacked Bar Chart
prov_monthly = df.groupby(['year_month', 'nearest_province']).size().unstack().fillna(0)
prov_colors = ['#1d3557', '#457b9d', '#e63946', '#f4a261', '#2a9d8f']
prov_monthly.plot(kind='bar', stacked=True, ax=ax2, color=prov_colors, width=0.75)
ax2.set_title('Komposisi Titik Api per Provinsi Kalimantan per Bulan', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Bulan Deteksi', fontsize=11, fontweight='bold')
ax2.set_ylabel('Jumlah Titik Api', fontsize=11, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)
ax2.legend(title='Provinsi', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('visualizations/01_temporal_monthly_trend_official.png', dpi=300, bbox_inches='tight')
plt.close()
print("   [OK] Saved visualizations/01_temporal_monthly_trend_official.png")

# 2. IMPACT ZONE & RISK DISTRIBUTION
print("[3/3] Generating Spatial Impact & Risk Distribution Chart...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Impact Zone Donut Chart
zone_counts = df['impact_zone'].value_counts()
zone_colors = ['#d62828', '#f77f00', '#fcbf49', '#2a9d8f']
wedges, texts, autotexts = ax1.pie(zone_counts.values, labels=[z.split(':')[0] for z in zone_counts.index], 
                                  autopct='%1.1f%%', startangle=140, colors=zone_colors, 
                                  textprops=dict(color="black", fontweight='bold'),
                                  wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
ax1.set_title('Distribusi Titik Api Berdasarkan Zona Kedekatan Fasilitas Edukasi/Pemukiman', fontsize=12, fontweight='bold')

# Action Tier Bar Chart
tier_counts = df['priority_action_tier'].value_counts()
tier_colors = ['#f77f00', '#fcbf49', '#d62828', '#2a9d8f']
ax2.barh([t.split(':')[0] for t in tier_counts.index], tier_counts.values, color=tier_colors, edgecolor='black', alpha=0.85)
ax2.set_title('Distribusi Tingkat Prioritas Tindakan (CF-Action Tiers)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Jumlah Titik Api', fontsize=11, fontweight='bold')
for i, v in enumerate(tier_counts.values):
    ax2.text(v + 500, i, f"{v:,} ({v/len(df)*100:.1f}%)", va='center', fontweight='bold')

# Top 10 High Risk Regencies
top_kab = df.groupby('nearest_city_regency').agg(
    hotspots=('hotspot_id', 'count'),
    tier1_emergency=('priority_action_tier', lambda x: (x.str.startswith('Tier 1')).sum())
).sort_values(by='hotspots', ascending=False).head(10)

top_kab['hotspots'].plot(kind='barh', ax=ax3, color='#e76f51', edgecolor='black', alpha=0.85)
ax3.invert_yaxis()
ax3.set_title('Top 10 Kabupaten/Kota dengan Akumulasi Hotspot Tertinggi', fontsize=12, fontweight='bold')
ax3.set_xlabel('Jumlah Hotspot', fontsize=11, fontweight='bold')
for i, v in enumerate(top_kab['hotspots']):
    ax3.text(v + 100, i, f"{v:,}", va='center', fontweight='bold')

# Risk Score Distribution
sns.histplot(df['composite_risk_score'], bins=40, kde=True, ax=ax4, color='#1d3557', edgecolor='black')
ax4.set_title('Distribusi Skor Risiko Komposit (CF-Risk Score: 0-100)', fontsize=12, fontweight='bold')
ax4.set_xlabel('Skor Risiko (0 - 100)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Frekuensi Kejadian', fontsize=11, fontweight='bold')
ax4.axvline(75, color='#d62828', linestyle='--', linewidth=2, label='Ambang Batas Tier 1 (>=75)')
ax4.axvline(50, color='#f77f00', linestyle='--', linewidth=2, label='Ambang Batas Tier 2 (>=50)')
ax4.legend(loc='upper right')

plt.tight_layout()
plt.savefig('visualizations/02_risk_and_impact_analytics_official.png', dpi=300, bbox_inches='tight')
plt.close()
print("   [OK] Saved visualizations/02_risk_and_impact_analytics_official.png")

print("\n[ALL VISUALIZATIONS GENERATED SUCCESSFULLY]")
